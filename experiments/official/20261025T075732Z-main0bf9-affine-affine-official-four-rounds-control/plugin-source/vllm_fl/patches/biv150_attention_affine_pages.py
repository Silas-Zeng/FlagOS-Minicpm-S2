"""BI-V150 MiniCPM 连续页寻址；保持当前 Attention 数学与 Q-fragment。"""
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


# 以下只把已测组件接到本步 metadata；原 runner/C2/C3/Q-fragment 源码不改。
import functools
import inspect
import json
import os
import weakref
from types import MethodType, SimpleNamespace

_BINDING = "_biv150_affine_pages_binding"
_STATE = "_biv150_affine_pages_state"
_ROUTER = None
_SOURCE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


class _Binding:
    def __init__(self, state, epoch, metadata, descriptor, facts, producer):
        self.state, self.epoch = state, epoch
        self.table = weakref.ref(metadata.block_table)
        self.cu = weakref.ref(metadata.query_start_loc)
        self.lens = weakref.ref(metadata.seq_lens)
        self.descriptor, self.facts, self.producer = descriptor, facts, producer
        self.streams, self.observed = set(), False

    def matches(self, values):
        return (self.state.epoch == self.epoch
                and self.table() is values.get("block_tables_ptr")
                and self.cu() is values.get("query_start_len_ptr")
                and self.lens() is values.get("seq_lens_ptr")
                and values.get("num_seqs") == self.facts["rows"]
                and values["query_ptr"].shape[0] == self.facts["query_tokens"]
                and self.facts["max_page"] < values["key_cache_ptr"].shape[0])

    def prepare(self, torch):
        stream = torch.cuda.current_stream(device=self.descriptor.device)
        if stream != self.producer and stream not in self.streams:
            stream.wait_stream(self.producer)
            self.descriptor.record_stream(stream)
            self.streams.add(stream)


class _Router:
    def __init__(self, baseline, candidate, qmod):
        self.original, self.candidate, self.qmod = baseline, candidate, qmod

    def __getattr__(self, name):
        # C2 的 normalized kernel 身份仍解析到原 .fn，不能替换其源码形态。
        return getattr(self.original, name)

    def __getitem__(self, grid):
        original = self.original[grid]
        candidate = self.candidate.wrapper[grid]

        def invoke(*args, **kwargs):
            binding = None
            try:
                table = kwargs.get("block_tables_ptr")
                item = getattr(table, _BINDING, None)
                if (not args and item is not None and item.matches(kwargs)
                        and self.qmod._eligible(kwargs)):
                    from vllm.forward_context import get_forward_context
                    mode = get_forward_context().cudagraph_runtime_mode
                    torch = self.candidate.attention.torch
                    if mode.name == "NONE" and not torch.cuda.is_current_stream_capturing():
                        binding = item
            except (AttributeError, KeyError, TypeError, RuntimeError):
                binding = None
            if binding is None:
                return original(*args, **kwargs)
            binding.prepare(torch)
            compiled = candidate(**dict(kwargs, affine_pages_ptr=binding.descriptor))
            # 已提交后不重试原路；诊断也不能再次启动 kernel。
            if not binding.observed and binding.state.reported < 4:
                binding.observed = True
                binding.state.reported += 1
                print("BIV150_AFFINE_PAGES_SELECTED " + json.dumps(dict(
                    binding.facts, epoch=binding.epoch, actual_requests=True,
                    q_hoisted=compiled is not None and compiled.hash in self.candidate.optimized,
                    graph_mode="NONE", runtime_source_sha256=_SOURCE_SHA)), flush=True)
            return compiled
        return invoke


def _install_kernel():
    global _ROUTER
    if _ROUTER is not None:
        return _ROUTER
    import importlib
    qmod = importlib.import_module("vllm_fl.patches.biv150_q_fragment_service")
    baseline = qmod._MANAGER
    if baseline is None or not baseline.active:
        raise ValueError("当前 Q-fragment 未自然安装")
    if baseline.holder[baseline.kernel_key] is not baseline.wrapper:
        raise ValueError("当前 normalized kernel 存在未知包装")
    _, source = sources(baseline.attention.__file__)
    raw = instantiate(baseline.attention, source)
    jit = importlib.import_module("triton.runtime.jit")
    cloned = jit.JITFunction(raw.fn, version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug, noinline=raw.noinline, repr=raw._repr,
        launch_metadata=raw.launch_metadata)
    holder = {"kernel": raw}
    candidate = qmod.Manager(baseline.attention, baseline.backend,
                             holder, "kernel", raw, cloned).install()
    router = _Router(baseline.wrapper, candidate, qmod)
    baseline.holder[baseline.kernel_key] = router
    _ROUTER = router
    return router


def _step_cpu(runner, kwargs):
    """只消费 prepare_inputs 已完成的真实顺序；C2 staging 已经 P，不能再 P。"""
    import numpy as np
    n = int(kwargs["num_reqs"])
    if n <= 0 or n != runner.input_batch.num_reqs:
        return None
    scheduled = kwargs.get("num_scheduled_tokens")
    if not isinstance(scheduled, dict) or len(scheduled) != n:
        return None  # 原 dummy/capture 调用没有实际 scheduler 请求字典。
    if (kwargs.get("for_cudagraph_capture", False) or kwargs.get("use_spec_decode", False)
            or kwargs.get("ubatch_slices") is not None
            or kwargs.get("num_reqs_padded") not in (None, n)
            or kwargs.get("num_tokens_padded") not in (None, kwargs["num_tokens"])
            or kwargs["max_query_len"] <= 1):
        return None
    order = kwargs.get("compute_order")
    permutation = tuple(range(n)) if order is None else tuple(map(int, order.permutation))
    if sorted(permutation) != list(range(n)):
        raise ValueError("C2 permutation 不是本步请求排列")
    ids = tuple(runner.input_batch.req_ids[i] for i in permutation)
    cu = runner.query_start_loc.cpu[:n + 1].numpy()
    qs = tuple(map(int, np.diff(cu)))
    if int(cu[0]) != 0 or sum(qs) != kwargs["num_tokens"] or min(qs) <= 0:
        raise ValueError("当前 query_start_loc 与请求/token 数不一致")
    if qs != tuple(scheduled.get(req, -1) for req in ids):
        raise ValueError("实际请求顺序/P 与 scheduler 字典不一致")
    if order is None:
        lengths = tuple(map(int, runner.optimistic_seq_lens_cpu[:n].tolist()))
        table = runner.input_batch.block_table[0].block_table.np
    else:
        if qs != tuple(map(int, order.scheduled)):
            raise ValueError("C2 scheduled 与实际 query_start_loc 不一致")
        lengths = tuple(map(int, order.state["seq_np"][:n]))
        table = order.state["table_np"]  # copy_block_table 已按 P 写好。
    if table.dtype != np.int32 or table.shape[1] != 8192 or table.strides[1] != 4:
        raise ValueError("不是当前 page16/stride8192 CPU 页表")
    descriptors, pages = [], []
    for q, length, row in zip(qs, lengths, table[:n]):
        if not 0 < q <= length <= 131072:
            raise ValueError("本步 P/KV 长度不符")
        live = tuple(map(int, row[:(length + 15) // 16])) if q > 1 else ()
        if any(x < 0 or x >= 2 ** 31 for x in live):
            raise ValueError("当前物理页号越界")
        desc = longest(live) if live else (0, 0, 0)
        lo, hi, base = desc
        if hi and any(live[j] != base + j - lo for j in range(lo, hi)):
            raise ValueError("descriptor 不等于当前页表")
        descriptors.append(desc)
        pages.append(live)
    covered = [max(0, hi // 4 - (lo + 3) // 4) for lo, hi, _ in descriptors]
    if not any(covered):
        return None
    return dict(ids=ids, qs=qs, lengths=lengths, descriptors=tuple(descriptors),
                pages=tuple(pages), permutation=permutation, covered=covered,
                c2_reordered=order is not None)


def _attach(runner, kwargs, result, state):
    import torch
    if torch.cuda.is_current_stream_capturing():
        return
    metadata_by_layer = result[0]
    if not isinstance(metadata_by_layer, dict) or len(metadata_by_layer) != 42:
        return
    metadata = next(iter(metadata_by_layer.values()))
    if any(value is not metadata for value in metadata_by_layer.values()):
        return
    try:
        cpu = _step_cpu(runner, kwargs)
    except (ValueError, KeyError, AttributeError, TypeError) as error:
        if not state.rejected:
            state.rejected = True
            print("BIV150_AFFINE_PAGES_FALLBACK " + str(error), flush=True)
        return
    if cpu is None:
        return
    n = len(cpu["ids"])
    split = getattr(metadata, "_biv150_natural_prefix_plan", None)
    prefix = 0 if split is None else split.prefix_tokens
    if prefix and (cpu["qs"][:prefix] != (1,) * prefix
                   or split.total_tokens != sum(cpu["qs"])):
        return
    if (metadata.block_table.shape != (n, 8192) or metadata.seq_lens.shape != (n,)
            or metadata.query_start_loc.shape != (n + 1,)
            or metadata.num_actual_tokens != sum(cpu["qs"])):
        return
    _install_kernel()
    if state.host is None:
        state.host = torch.empty((runner.max_num_reqs, 3), dtype=torch.int32, pin_memory=True)
    # _build_attention_metadata 处于原 synchronize_input_prep 域，保护 host 重用。
    state.host.numpy()[:n] = cpu["descriptors"]
    device = torch.empty((n, 3), dtype=torch.int32, device=runner.device)
    device.copy_(state.host[:n], non_blocking=True)
    producer = torch.cuda.current_stream(device=runner.device)
    verified = False
    evidence = os.environ.get("BIV150_AFFINE_EVIDENCE_DIR")
    if evidence and state.evidence_count < 4:
        if not torch.equal(device.cpu(), state.host[:n]):
            raise RuntimeError("descriptor H2D 字节不一致")
        for i, live in enumerate(cpu["pages"]):
            if live and tuple(metadata.block_table[i, :len(live)].cpu().tolist()) != live:
                raise RuntimeError("GPU 当前页表与 CPU 计划不一致")
        verified = True
        folder = Path(evidence)
        folder.mkdir(parents=True, exist_ok=True)
        payload = dict(cpu, ids=[hashlib.sha256(str(x).encode()).hexdigest() for x in cpu["ids"]],
                       epoch=state.epoch, c3_prefix=prefix, runtime_source_sha256=_SOURCE_SHA)
        (folder / ("epoch-%d.json" % state.epoch)).write_text(
            json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        state.evidence_count += 1
    variants = [(metadata, 0)] if split is None else [(split.prefill, prefix)]
    # C3 仅候选其 prefill 分支；decode 继续已有 GQA 路径。
    for md, start in variants:
        facts = dict(rows=n - start, query_tokens=sum(cpu["qs"][start:]),
            cpu_descriptor_verified=True, device_binding_verified=verified,
            c2_reordered=cpu["c2_reordered"], c3_prefix=prefix,
            query_lengths=cpu["qs"][start:], seq_lens=cpu["lengths"][start:],
            descriptors=cpu["descriptors"][start:],
            affine_tiles=sum(cpu["covered"][start:]),
            max_page=max((max(row) for row in cpu["pages"][start:] if row), default=0),
            descriptor_h2d_per_step=1, shared_layers=42)
        binding = _Binding(state, state.epoch, md, device[start:n], facts, producer)
        setattr(md.block_table, _BINDING, binding)


def install_runner(runner):
    """唯一 worker 构造后安装；原 runner 文件、C2/C3 闭包及原参数不变。"""
    if hasattr(runner, _STATE):
        return
    import torch
    from vllm.platforms import current_platform
    from vllm_fl.compile_semantics import native_model_matches
    config = runner.vllm_config
    if (current_platform.vendor_name != "iluvatar"
            or not native_model_matches(config.model_config.hf_text_config)
            or config.model_config.dtype != torch.bfloat16
            or config.parallel_config.tensor_parallel_size != 1
            or config.parallel_config.pipeline_parallel_size != 1
            or config.parallel_config.enable_dbo
            or config.speculative_config is not None
            or config.kv_transfer_config is not None
            or config.ec_transfer_config is not None
            or not runner.use_async_scheduling
            or runner.prepare_inputs_event is None
            or config.compilation_config.cudagraph_mode.name != "FULL_DECODE_ONLY"):
        return
    if "BI-V150" not in torch.cuda.get_device_properties(runner.device).name:
        return
    original = runner._build_attention_metadata
    if "_build_attention_metadata" in runner.__dict__:
        raise ValueError("已有未知实例 metadata wrapper")
    state = SimpleNamespace(epoch=0, host=None, reported=0, evidence_count=0, rejected=False)
    signature = inspect.signature(original)

    @functools.wraps(original)
    def build(self, *args, **kwargs):
        state.epoch += 1  # 每次 build 都失效旧计划，包含 graph/dummy/fallback。
        result = original(*args, **kwargs)
        values = kwargs if not args else signature.bind(*args, **kwargs).arguments
        _attach(self, values, result, state)
        return result

    runner._build_attention_metadata = MethodType(build, runner)
    setattr(runner, _STATE, state)
    print("BIV150_AFFINE_PAGES_INSTALLED " + json.dumps(dict(
        runtime_source_sha256=_SOURCE_SHA, runner_source_unchanged=True,
        scope="MiniCPM BF16 TP1 page16 2D eager metadata")), flush=True)
