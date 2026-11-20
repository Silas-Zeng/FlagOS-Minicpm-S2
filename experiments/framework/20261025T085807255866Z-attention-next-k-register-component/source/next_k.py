"""独立组件：当前 affine 寻址上，只跨一轮保留下一 K 的寄存器载荷。"""
from __future__ import annotations

import ast
import hashlib
import re


LOOP = "    # iterate through tiles (now limited to the sliding window range)\n"
K_LOAD = """            K_load = tl.load(
                key_cache_ptr + k_offset,
                mask=dim_mask[:, None] & tile_mask[None, :],
                other=0.0,
            )
"""
CURRENT_K = """            if next_k_valid:
                K_load = next_k_value
            else:
                K_load = tl.load(
                    key_cache_ptr + k_offset,
                    mask=dim_mask[:, None] & tile_mask[None, :],
                    other=0.0,
                )
"""
INITIAL = """    # 第一轮仍使用本轮 K 原始加载；空循环不读取 K。
    next_k_valid = tl.full((), False, tl.int1)
    next_k_value = tl.zeros((HEAD_SIZE_PADDED, TILE_SIZE), dtype=Q.dtype)

"""
ANCHOR = "        acc = acc * alpha[:, None]\n"
PREFETCH = """
        # 仅预取下一轮确实访问且完整位于当前已验证连续段的 TILE64。
        # V 保持原时序；没有新 shared buffer，不 carry 物理页向量。
        next_first_page = (j + 1) * (TILE_SIZE // BLOCK_SIZE)
        next_k_valid = ((j + 1 < loop_hi)
                        & (next_first_page >= affine_lo)
                        & (next_first_page + TILE_SIZE // BLOCK_SIZE <= affine_hi))
        if next_k_valid:
            next_seq = (j + 1) * TILE_SIZE + offs_t
            next_physical = (affine_base.to(tl.int64)
                             + next_seq // BLOCK_SIZE - affine_lo.to(tl.int64))
            next_offset = (
                next_physical[None, :] * stride_k_cache_0
                + kv_head_idx * stride_k_cache_2
                + offs_d[:, None] * stride_k_cache_3
                + (next_seq % BLOCK_SIZE)[None, :] * stride_k_cache_1
            )
            next_k_value = tl.load(
                key_cache_ptr + next_offset,
                mask=dim_mask[:, None] & (next_seq < max_seq_prefix_len)[None, :],
                other=0.0,
            )
        else:
            next_k_value = tl.zeros((HEAD_SIZE_PADDED, TILE_SIZE), dtype=Q.dtype)
"""


def transform(source):
    """仅三处机械变换，精确逆回 affine 基准；不插入/重排浮点运算。"""
    replacements = [(LOOP, INITIAL + LOOP), (K_LOAD, CURRENT_K),
                    (ANCHOR, ANCHOR + PREFETCH)]
    changed = source
    for old, new in replacements:
        if changed.count(old) != 1:
            raise ValueError("next-K 锚点变化：" + old[:60])
        changed = changed.replace(old, new, 1)
    restored = changed
    for old, new in reversed(replacements):
        if restored.count(new) != 1:
            raise ValueError("next-K 逆变换锚点变化")
        restored = restored.replace(new, old, 1)
    if restored != source:
        raise ValueError("next-K 未精确逆回原浮点与掩码源码")
    ast.parse(changed)
    return changed


def resource_fields(compiled):
    asm = compiled.asm.get("asm", "")
    fields = {}
    for name in ("sgpr_count", "sgpr_spill_count", "vgpr_count", "vgpr_spill_count",
                 "private_segment_fixed_size"):
        matches = re.findall(r"\." + name + r":\s*(\d+)", asm)
        if len(matches) != 1:
            raise ValueError("唯一实际 ASM 资源缺失：" + name)
        fields[name] = int(matches[0])
    meta = compiled.metadata
    fields["shared"] = meta.get("shared") if isinstance(meta, dict) else meta.shared
    fields["raw_four_cta_register_bound"] = fields["vgpr_count"] <= 128
    fields["actual_occupancy_proven"] = False
    return fields


def mechanism(ttgir, assembly, source):
    """保守的真实 ASM 结构门：预取 load 后各路径先到 PV，不能提前等待。

    只识别实际 BI sl_jump/sl_cbr 及 .loc；未知 CFG 拒绝计时，保存原件供人审。
    不把此结构门解释为硬件 stall 时长或 occupancy 证明。
    """
    src = source.splitlines()
    load_line = next(i + 1 for i, x in enumerate(src) if "next_k_value = tl.load(" in x)
    pv_line = next(i + 1 for i, x in enumerate(src) if "acc += tl.dot(P.to(V.dtype), V)" in x)
    loops = [x for x in ttgir.splitlines() if "= scf.for " in x]
    if len(loops) != 1 or "tensor<128x64xbf16" not in loops[0]:
        raise ValueError("实际 TTGIR 未保留唯一循环中的下一 K 载荷 carry")
    lines = assembly.splitlines()
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = "<affine-pages-component-" + digest + ".py>"
    files = [m[1] for x in lines if (m := re.match(r'\s*\.file\s+(\d+)\s+"([^"]+)"', x))
             and m[2] == filename]
    if len(files) != 1:
        raise ValueError("实际 ASM 缺唯一当前源码 .file，不能借 helper 同行号定位")
    source_file = int(files[0])
    labels = {m[1]: i for i, x in enumerate(lines)
              if (m := re.match(r"^(BB\d+_\d+):", x))}
    current_line, loads, pv = None, [], set()
    for i, line in enumerate(lines):
        loc = re.match(r"\s*\.loc\s+(\d+)\s+(\d+)\s+\d+", line)
        if loc:
            current_line = int(loc[2]) if int(loc[1]) == source_file else None
        if current_line == load_line and re.search(r"ml_lsa_(?:blkload|load)_", line):
            loads.append(i)
        if current_line == pv_line and "ml_matrix_mad_" in line:
            pv.add(i)
    if not loads or len(pv) != 32:
        raise ValueError("实际 ASM 缺可定位 next-K load 或32条原 PV MAD")

    def until_pv(start):
        # 三色DFS：仅至少一条到达PV不够，未到PV先回环的路径也必须拒绝。
        todo, active, completed, reached = [(start, False)], set(), set(), set()
        while todo:
            i, leaving = todo.pop()
            if leaving:
                active.remove(i)
                completed.add(i)
                continue
            if i in completed:
                continue
            if i in active:
                raise ValueError("next-K 在 PV 前出现回环")
            if i in pv:
                reached.add(i)
                completed.add(i)
                continue
            if not (0 <= i < len(lines)) or len(completed) + len(active) > 4000:
                raise ValueError("next-K 到 PV 的路径越界/过长")
            line = lines[i]
            if ("sl_wait" in line and "vmcnt" in line) or "sl_barrier" in line:
                raise ValueError("next-K 在 PV 前被等待/barrier 截断：" + str(i + 1))
            jump = re.search(r"\b(sl_jump|sl_cbr_\w+)\s+(BB\d+_\d+)", line)
            if jump:
                if jump[2] not in labels:
                    raise ValueError("未知跳转目标")
                successors = [labels[jump[2]]]
                if jump[1] != "sl_jump":
                    successors.append(i + 1)
            elif "sl_exit" in line or "s_endpgm" in line:
                raise ValueError("next-K 未消费 PV 即退出")
            else:
                successors = [i + 1]
            active.add(i)
            todo.append((i, True))
            todo.extend((successor, False) for successor in successors)
        if not reached:
            raise ValueError("next-K 后没有到达 PV")
        return sorted(x + 1 for x in reached)

    reached = [until_pv(i + 1) for i in loads]
    return dict(pass_=True, next_k_source_line=load_line, pv_source_line=pv_line,
                next_k_asm_lines=[x + 1 for x in loads], pv_asm_lines=sorted(x + 1 for x in pv),
                first_pv_per_load=reached, source_sha256=digest,
                limits="结构门不是 stall/occupancy 证明；另审原 ASM 和真实资源")
