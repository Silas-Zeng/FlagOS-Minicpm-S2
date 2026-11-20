"""CPU 可构造的组件原型；只改页号寻址，尚无服务注册或设备启动器。"""
from __future__ import annotations

import ast
from dataclasses import dataclass
import hashlib
import linecache
from pathlib import Path

ATTENTION_SHA = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
PAGE = 16
PAGES_PER_TILE = 4
OLD_LOOKUP = """        physical_block_idx = tl.load(
            block_tables_ptr + block_table_offset + seq_offset // BLOCK_SIZE
        ).to(tl.int64)
"""
NEW_LOOKUP = """        first_page = j * (TILE_SIZE // BLOCK_SIZE)
        if (first_page >= affine_lo) & (
            first_page + TILE_SIZE // BLOCK_SIZE <= affine_hi
        ):
            physical_block_idx = (
                affine_base.to(tl.int64)
                + seq_offset // BLOCK_SIZE
                - affine_lo.to(tl.int64)
            )
        else:
            physical_block_idx = tl.load(
                block_tables_ptr + block_table_offset + seq_offset // BLOCK_SIZE
            ).to(tl.int64)
"""
DESCRIPTOR_LOAD = """    # 每个 CTA 读一次，只消费本批次当前页表的描述符。
    tl.static_assert(not IS_3D and BLOCK_SIZE == 16 and TILE_SIZE == 64)
    tl.static_assert(not USE_TD and not USE_TD_QO and KV_QUANT_MODE == 0)
    affine_lo = tl.load(affine_pages_ptr + seq_idx * 3)
    affine_hi = tl.load(affine_pages_ptr + seq_idx * 3 + 1)
    affine_base = tl.load(affine_pages_ptr + seq_idx * 3 + 2)
"""


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("源码锚点不唯一：" + old[:60])
    return text.replace(old, new, 1)


def sources(attention_path):
    """基准复用 main0bf9 的 L=0，Q-hoist 由当前 main 的 IR 变换另行应用。"""
    raw = Path(attention_path).read_bytes()
    if hashlib.sha256(raw).hexdigest() != ATTENTION_SHA:
        raise ValueError("Attention 源码版本不匹配")
    text = raw.decode("utf-8")
    fn = next(n for n in ast.parse(text).body
              if isinstance(n, ast.FunctionDef) and n.name == "kernel_unified_attention")
    start = min([fn.lineno] + [n.lineno for n in fn.decorator_list])
    baseline = "\n".join(text.splitlines()[start - 1:fn.end_lineno]) + "\n"
    baseline = once(baseline, "L = tl.full([BLOCK_M], 1.0, dtype=tl.float32)",
                    "L = tl.zeros([BLOCK_M], dtype=tl.float32)")
    candidate = once(baseline, "    block_tables_ptr,\n",
                     "    block_tables_ptr,\n    affine_pages_ptr,\n")
    anchor = "    block_table_offset = seq_idx * block_table_stride\n"
    candidate = once(candidate, anchor, anchor + DESCRIPTOR_LOAD)
    candidate = once(candidate, OLD_LOOKUP, NEW_LOOKUP)
    # 精确逆回保证 dot、softmax、mask、writer、loop 边界没有附带变化。
    restored = once(candidate, NEW_LOOKUP, OLD_LOOKUP)
    restored = once(restored, DESCRIPTOR_LOAD, "")
    restored = once(restored, "    block_tables_ptr,\n    affine_pages_ptr,\n",
                    "    block_tables_ptr,\n")
    if restored != baseline:
        raise AssertionError("不能精确恢复基准数学")
    ast.parse(baseline)
    ast.parse(candidate)
    return baseline, candidate


def instantiate(attention, source):
    """未来组件使用受控原模块的 helper；不替换任何已安装模块或全局绑定。"""
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = "<affine-pages-component-" + digest + ".py>"
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
    namespace = dict(vars(attention))
    exec(compile(source, filename, "exec"), namespace)
    return namespace["kernel_unified_attention"]


def snapshot(request_ids, query_lengths, seq_lens, page_rows, batch_epoch):
    """调用者提供当前 CPU 页表镜像；不从 GPU 读回，不按容量/旧快照猜映射。"""
    if not (len(request_ids) == len(query_lengths) == len(seq_lens) == len(page_rows)):
        raise ValueError("请求顺序、P、KV 长度和页表行数不一致")
    if len(set(request_ids)) != len(request_ids):
        raise ValueError("请求 ID 重复")
    rows = []
    for req, p, length, row in zip(request_ids, query_lengths, seq_lens, page_rows):
        if type(p) is not int or type(length) is not int or not (0 < p <= length):
            raise ValueError("本组件仅接受有效的当前 P/序列长度")
        count = (length + PAGE - 1) // PAGE
        if count > len(row):
            raise ValueError("当前页表未覆盖完整 KV 长度")
        live = tuple(row[:count])
        if any(type(x) is not int or not (0 <= x < 2 ** 31) for x in live):
            raise ValueError("当前物理页号不是非负 int32")
        rows.append((req, p, length, live))
    return (batch_epoch, tuple(rows))


def longest(live):
    best_lo, best_hi, start = 0, 0, 0
    for end in range(1, len(live) + 1):
        if end == len(live) or live[end] != live[end - 1] + 1:
            if end - start > best_hi - best_lo:
                best_lo, best_hi = start, end
            start = end
    if best_hi - best_lo < PAGES_PER_TILE:
        return (0, 0, 0)
    return (best_lo, best_hi, live[best_lo])


@dataclass(frozen=True)
class BoundPlan:
    binding: tuple
    descriptors: tuple

    def matches(self, request_ids, query_lengths, seq_lens, page_rows, batch_epoch):
        return self.binding == snapshot(request_ids, query_lengths, seq_lens,
                                        page_rows, batch_epoch)


def plan(request_ids, query_lengths, seq_lens, page_rows, batch_epoch):
    bound = snapshot(request_ids, query_lengths, seq_lens, page_rows, batch_epoch)
    descriptors = tuple(longest(live) if p > 1 else (0, 0, 0)
                        for _, p, _, live in bound[1])
    return BoundPlan(bound, descriptors)
