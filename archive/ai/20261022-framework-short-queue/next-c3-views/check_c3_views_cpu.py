"""唯一CPU合同：真实两层forward的参数、scale和异常；不模拟Attention数值。"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


policy = load("c3_views_cpu_policy", HERE / "biv150_c3_view_reuse.py")
c3 = load("c3_views_cpu_original", ROOT / "patches/framework/biv150_mixed_decode.py")
backend_path = ROOT / "tmp/remote-source/triton_attn.py"
source = policy._source(backend_path, policy.EXPECTED_BACKEND)
policy._source(c3.__file__, policy.EXPECTED_C3)
trace, calls = [], []
device = NS(type="cuda", index=0)


class Tensor:
    def __init__(self, name, shape, offset=0, dtype="bf16", scalar=None, strides=None):
        self.name, self.shape, self.offset = name, tuple(shape), offset
        self.dtype, self.device, self.scalar = dtype, device, scalar
        if strides is None:
            strides, size = [], 1
            for dim in reversed(self.shape):
                strides.insert(0, size)
                size *= dim
        self.strides = tuple(strides)

    @property
    def ndim(self):
        return len(self.shape)

    def __getitem__(self, sl):
        assert isinstance(sl, slice)
        start, stop, step = sl.indices(self.shape[0])
        assert step == 1
        trace.append(("slice", self.name, start, stop))
        return Tensor(self.name, (stop - start,) + self.shape[1:],
                      self.offset + start * self.strides[0], self.dtype, self.scalar, self.strides)

    def unbind(self, dim):
        assert dim == 1 and self.shape[dim] == 2
        trace.append(("unbind", self.name))
        shape = self.shape[:dim] + self.shape[dim + 1:]
        strides = self.strides[:dim] + self.strides[dim + 1:]
        return tuple(Tensor(self.name, shape, self.offset + i * self.strides[dim],
                            self.dtype, strides=strides) for i in range(2))

    def expand(self, shape):
        trace.append(("expand", self.name, tuple(shape), self.scalar))
        return Tensor(self.name, shape, self.offset, self.dtype, self.scalar, (0,) * len(shape))

    def record_stream(self, stream):
        trace.append(("record_stream", self.name))


class Stream:
    def wait_stream(self, other):
        trace.append(("wait_stream",))


stream = Stream()
torch = NS(Tensor=Tensor, bfloat16="bf16", cuda=NS(
    current_stream=lambda device=None: stream, is_current_stream_capturing=lambda: False))
enums = NS(DECODER="decoder", ENCODER="encoder", ENCODER_ONLY="encoder_only")
quant = NS(NONE=0, FP8_PER_TENSOR=1)
fault = NS(error=None)


def describe(value):
    if isinstance(value, Tensor):
        return (value.name, value.shape, value.offset, value.strides, value.dtype, value.scalar)
    return value


def capture(**kwargs):
    calls.append({key: describe(value) for key, value in kwargs.items()})
    if fault.error is not None:
        raise fault.error


ns = {"__name__": "c3_cpu_backend", "torch": torch, "AttentionType": enums,
      "KVQuantMode": quant, "is_quantized_kv_cache": lambda _: False, "unified_attention": capture}
cls, = [n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == "TritonAttentionImpl"]
forward, = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "forward"]
exec(compile(ast.fix_missing_locations(ast.Module(body=[forward], type_ignores=[])),
             str(backend_path), "exec"), ns)


class Impl:
    forward = ns["forward"]
    attn_type = enums.DECODER
    num_heads, num_kv_heads, head_size = 16, 2, 128
    _kv_quant_mode, kv_cache_dtype, _is_per_token_head_quant = quant.NONE, "auto", False
    kv_sharing_target_layer_name = None
    alibi_slopes = sinks = None
    use_alibi_sqrt = use_td = False
    sliding_window, logits_soft_cap, chunk_lookback = (-1, -1), 0, -1
    scale = 128 ** -0.5


class Builder:
    def build(self, *args, **kwargs):
        raise AssertionError("本合同不执行builder或GPU元数据生成")


backend = NS(TritonAttentionImpl=Impl, TritonAttentionMetadataBuilder=Builder,
             torch=torch, AttentionType=enums, KVQuantMode=quant)
c3._wrap_backend(backend, torch)
manager = policy.Manager.__new__(policy.Manager)
manager.backend, manager.c3, manager.torch = backend, c3, torch
manager.original_forward = Impl.forward
manager.fast_forward = policy._compile_backend(source, ns, str(backend_path))
manager.active = False
manager.counts = {"selected_calls": 0, "fallback_calls": 0}
manager.wrapper = manager._make_wrapper()


def metadata(tokens, requests, maxq, label):
    return NS(num_actual_tokens=tokens, max_query_len=maxq, max_seq_len=16384,
              query_start_loc=Tensor(label + ".cu", (requests + 1,), dtype="i32"),
              seq_lens=Tensor(label + ".seq", (requests,), dtype="i32"),
              block_table=Tensor(label + ".table", (requests, 1024), dtype="i32"),
              seq_threshold_3D=64, num_par_softmax_segments=16,
              softmax_segm_output=Tensor("scratch.out", (64, 16, 16, 128), dtype="fp32"),
              softmax_segm_max=Tensor("scratch.max", (64, 16, 16), dtype="fp32"),
              softmax_segm_expsum=Tensor("scratch.sum", (64, 16, 16), dtype="fp32"),
              causal=True, use_cascade=False, common_prefix_len=0, mm_prefix_range=None,
              mm_prefix_range_tensor=None, scheduler_metadata=None, prefix_scheduler_metadata=None)


parent = metadata(2048, 30, 2019, "parent")
plan = c3._SplitPlan(29, 2048, metadata(29, 29, 1, "decode"),
                     metadata(2019, 1, 2019, "prefill"), stream)
setattr(parent, c3._PLAN, plan)
data = dict(layer=NS(_q_scale=Tensor("qs", (), dtype="fp32", scalar=0.75),
                    _k_scale=Tensor("ks", (), dtype="fp32", scalar=1.25),
                    _v_scale=Tensor("vs", (), dtype="fp32", scalar=0.5)),
            query=Tensor("Q", (2051, 16, 128)), key=Tensor("K", (2051, 2, 128)),
            value=Tensor("V", (2051, 2, 128)), kv_cache=Tensor("cache", (30720, 2, 16, 2, 128)),
            attn_metadata=parent, output=Tensor("O", (2051, 16, 128)))
impl = Impl()
assert manager.original_forward(impl, **data) is data["output"]
old_calls, old_trace = list(calls), list(trace)
calls.clear(); trace.clear()
manager.install()
assert impl.forward(**data) is data["output"]
new_calls, new_trace = list(calls), list(trace)
assert new_calls == old_calls and len(new_calls) == 2
assert [row["max_seqlen_q"] for row in new_calls] == [1, 2019]
assert [row["k_descale"][-1] for row in new_calls] == [1.25, 1.25]
assert [row["v_descale"][-1] for row in new_calls] == [0.5, 0.5]
assert sum(x[0] == "unbind" for x in old_trace) == 2
assert sum(x[0] == "unbind" for x in new_trace) == 1
assert sum(x[0] == "slice" for x in old_trace) == 12
assert sum(x[0] == "slice" for x in new_trace) == 4
assert manager.snapshot() == {"selected_calls": 1, "fallback_calls": 0}

# 原output scale错误必须原路抛出，不能候选偷偷丢参或执行Attention。
calls.clear()
for candidate in (False, True):
    manager.install() if candidate else manager.restore()
    try:
        impl.forward(**data, output_scale=object(), output_block_scale=object())
    except NotImplementedError as exc:
        assert exc.__context__ is None
    else:
        raise AssertionError("原output_block_scale错误丢失")
assert not calls and manager.snapshot()["fallback_calls"] == 1

# 选中后的真实helper异常不能重试或继续prefill。
calls.clear()
sentinel = RuntimeError("原 unified launch 错误")
fault.error = sentinel
try:
    impl.forward(**data)
except RuntimeError as exc:
    assert exc is sentinel and exc.__context__ is None
else:
    raise AssertionError("原异常被吞掉")
assert len(calls) == 1
manager.restore()
assert Impl.forward is manager.original_forward and not manager.active
assert not any(name in sys.modules for name in ("torch", "triton", "vllm"))

receipt = {
    "status": "one_CPU_forward_contract_passed_not_device_validation",
    "runtime_sha256": hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest(),
    "check_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    "backend_sha256": policy.EXPECTED_BACKEND, "c3_sha256": policy.EXPECTED_C3,
    "checks": ["exact_backend_AST_reverse", "original_C3_forward_and_backend_forward",
               "two_unified_calls_all_kwargs_alias_offsets_equal", "nonunit_scale_shape_stride_source_equal",
               "slices_12_to_4_unbind_2_to_1", "output_scale_error_fallback", "same_launch_error_no_retry",
               "original_forward_restored", "no_framework_import"],
    "limitations": ["CPU descriptor/call stubs, not Attention math, factory live-source identity, GPU bytes, stream readiness or performance."]}
(HERE / "cpu-check.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt, ensure_ascii=False))
