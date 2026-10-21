"""Opt-in mapped mixed Attention; external request/token/sampling rows stay fixed.

Only the exact SQL+C3 runner footer enables this. No operator/accelerator is
imported by merely importing this module. Unknown features use the original
C3 forward; after a selected forward starts, errors propagate without retry.
"""
from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import wraps
import hashlib
import importlib
import importlib.util
import inspect
from pathlib import Path
import sys


EXPECTED_DERIVED = "72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1"
EXPECTED = {
    "vllm.v1.attention.backend": "c524988a2223ec556bdb128a31c255075f0d07e7643e803b447975cd9c30a6b8",
    "vllm.v1.attention.backends.triton_attn": "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605",
    "vllm.v1.attention.ops.triton_unified_attention": "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f",
    "vllm.v1.attention.ops.triton_attention_helpers": "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1",
    "vllm_fl.patches.biv150_decode_launch_runtime": "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f",
    "vllm_fl.patches.biv150_mixed_decode": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
}
_PLAN = "_biv150_mapped_decode_plan"
_MARKER = "_biv150_mapped_decode_v1"
_CONTEXT = ContextVar("biv150_mapped_decode_call", default=None)
_REAL = ContextVar("biv150_mapped_decode_real_execute", default=False)
_COUNTS = dict.fromkeys(("plans", "forward_selected", "real_forward_selected", "forward_fallback",
                         "skip_2d_dispatches", "mapped_3d_dispatches", "capture_fallback"), 0)


def snapshot_stats():
    return dict(_COUNTS)


def _require(module, expected):
    if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
        raise RuntimeError("unaudited mapped-decode source: " + module.__name__)


def _dependencies():
    modules = {name: importlib.import_module(name) for name in EXPECTED}
    for name, expected in EXPECTED.items():
        _require(modules[name], expected)
    c3 = modules["vllm_fl.patches.biv150_mixed_decode"]
    attention = modules["vllm.v1.attention.ops.triton_unified_attention"]
    c3._require_fast_runtime(attention)
    return modules


def load_derived(path=None):
    path = Path(path) if path is not None else Path(__file__).with_name("biv150_mapped_attention.py")
    if hashlib.sha256(path.read_bytes()).hexdigest() != EXPECTED_DERIVED:
        raise RuntimeError("unaudited derived mapped Attention")
    name = "vllm_fl.patches._biv150_mapped_attention_impl"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _indices(common, metadata):
    cpu = common.query_start_loc_cpu
    count, total = common.num_reqs, metadata.num_actual_tokens
    if (cpu.device.type != "cpu" or cpu.ndim != 1 or cpu.shape[0] != count + 1
            or metadata.query_start_loc.shape != cpu.shape
            or metadata.seq_lens.shape[0] != count or metadata.block_table.shape[0] != count
            or metadata.slot_mapping.shape[0] < total):
        return None
    offsets = cpu.tolist()
    lengths = [right - left for left, right in zip(offsets, offsets[1:])]
    if (not lengths or offsets[0] != 0 or offsets[-1] != total
            or min(lengths) <= 0 or max(lengths) != metadata.max_query_len):
        return None
    indices = [row for row, length in enumerate(lengths) if length == 1]
    prefix = next((row for row, length in enumerate(lengths) if length != 1), count)
    if not indices or len(indices) == count or len(indices) == prefix or len(indices) > metadata.seq_threshold_3D:
        return None
    return indices


@dataclass
class _MappedPlan:
    cpu_indices: object
    gpu_indices: object
    num_reqs: int
    num_tokens: int
    producer_stream: object
    consumers: set = field(default_factory=set)

    def prepare_consumer(self, torch):
        stream = torch.cuda.current_stream(device=self.gpu_indices.device)
        if stream != self.producer_stream and stream not in self.consumers:
            stream.wait_stream(self.producer_stream)
            self.gpu_indices.record_stream(stream)
            self.consumers.add(stream)


def _extra_builder_scope(builder):
    config, model = builder.vllm_config, builder.vllm_config.model_config
    return (getattr(model, "quantization", "unknown") is None
            and getattr(model, "is_encoder_decoder", None) is False
            and getattr(config, "kv_transfer_config", None) is None
            and getattr(config, "ec_transfer_config", None) is None)


def _extra_layout(torch, query, cache, output, metadata, plan):
    return (query.stride(1) == output.stride(1) == 128
            and query.stride(2) == output.stride(2) == 1
            and query.stride(0) >= 2048 and output.stride(0) >= 2048
            and tuple(cache.stride()[2:]) == (256, 128, 1) and cache.stride(0) >= 8192
            and metadata.block_table.dtype == torch.int32
            and metadata.block_table.stride(1) == 1
            and metadata.block_table.stride(0) >= metadata.block_table.shape[1]
            and metadata.query_start_loc.dtype == torch.int32
            and metadata.query_start_loc.stride(0) == metadata.seq_lens.stride(0) == 1
            and metadata.seq_lens.dtype == torch.int32
            and metadata.seq_lens.device == metadata.block_table.device == plan.gpu_indices.device == query.device
            and len({value.untyped_storage().data_ptr() for value in (query, cache, output)}) == 3
            and metadata.num_actual_tokens == plan.num_tokens
            and metadata.seq_lens.shape[0] == plan.num_reqs)


class _Unified:
    def __init__(self, original, derived):
        self.original, self.derived = original, derived

    def __call__(self, *args, **kwargs):
        plan = _CONTEXT.get()
        if plan is None:
            return self.original(*args, **kwargs)
        # Neither call reorders Q/output or updates KV. The two write sets
        # are disjoint. The mapped function itself selects explicit C2 w2/s1.
        self.derived.unified_attention(*args, **kwargs, biv150_skip_single_query=True)
        _COUNTS["skip_2d_dispatches"] += 1
        result = self.derived.unified_attention(*args, **kwargs, biv150_decode_req_indices=plan.gpu_indices)
        _COUNTS["mapped_3d_dispatches"] += 1
        return result


def _wrap_backend(backend, derived, torch, c3):
    """Private real-backend gate seam; production install validates sources."""
    builder_cls, impl_cls = backend.TritonAttentionMetadataBuilder, backend.TritonAttentionImpl
    original_build, original_forward = builder_cls.build, impl_cls.forward
    c3_marker = "_biv150_natural_prefix_wrapper"
    if (not getattr(original_build, c3_marker, False)
            or not getattr(original_forward, c3_marker, False)
            or not hasattr(original_forward, "__wrapped__")
            or Path(original_build.__code__.co_filename).resolve() != Path(c3.__file__).resolve()
            or Path(original_forward.__code__.co_filename).resolve() != Path(c3.__file__).resolve()
            or Path(inspect.unwrap(original_build).__code__.co_filename).resolve() != Path(backend.__file__).resolve()):
        raise RuntimeError("mapped decode requires the original installed C3 wrappers")
    if isinstance(backend.unified_attention, _Unified):
        raise RuntimeError("mapped decode already wraps this backend")
    base_forward = original_forward.__wrapped__
    if (inspect.unwrap(base_forward) is not base_forward
            or Path(base_forward.__code__.co_filename).resolve() != Path(backend.__file__).resolve()):
        raise RuntimeError("unexpected C3 base forward")
    if derived.unified_attention.__globals__ is not vars(derived):
        raise RuntimeError("derived Attention global binding mismatch")
    unified = _Unified(backend.unified_attention, derived)

    @wraps(original_build)
    def build(self, common_prefix_len, common_attn_metadata, fast_build=False):
        metadata = original_build(self, common_prefix_len, common_attn_metadata, fast_build=fast_build)
        if (metadata.max_query_len <= 1 or common_prefix_len != 0 or fast_build
                or not c3._builder_eligible(self, backend, torch)
                or not c3._metadata_eligible(metadata) or not _extra_builder_scope(self)
                or metadata.seq_threshold_3D != 64):
            return metadata
        indices = _indices(common_attn_metadata, metadata)
        if indices is None or not c3._cuda_tensors(metadata.query_start_loc, metadata.seq_lens,
                                                  metadata.block_table, metadata.slot_mapping):
            return metadata
        if (metadata.num_par_softmax_segments != 16
                or any(value is None or value.shape[0] < len(indices) for value in (
                    metadata.softmax_segm_output, metadata.softmax_segm_max, metadata.softmax_segm_expsum))):
            return metadata
        if torch.cuda.is_current_stream_capturing():
            _COUNTS["capture_fallback"] += 1
            return metadata
        cpu_indices = torch.tensor(indices, dtype=torch.int32, pin_memory=True)
        gpu_indices = cpu_indices.to(metadata.query_start_loc.device, non_blocking=True)
        setattr(metadata, _PLAN, _MappedPlan(cpu_indices, gpu_indices, common_attn_metadata.num_reqs,
                metadata.num_actual_tokens, torch.cuda.current_stream(device=gpu_indices.device)))
        _COUNTS["plans"] += 1
        return metadata

    @wraps(original_forward)
    def forward(self, layer, query, key, value, kv_cache, attn_metadata, output,
                output_scale=None, output_block_scale=None):
        plan = getattr(attn_metadata, _PLAN, None)
        if (plan is None
                or not c3._impl_eligible(self, backend, torch, query, key, value, kv_cache,
                                         attn_metadata, output, output_scale, output_block_scale)
                or not _extra_layout(torch, query, kv_cache, output, attn_metadata, plan)):
            _COUNTS["forward_fallback"] += 1
            return original_forward(self, layer, query, key, value, kv_cache, attn_metadata, output,
                                    output_scale=output_scale, output_block_scale=output_block_scale)
        if torch.cuda.is_current_stream_capturing():
            _COUNTS["capture_fallback"] += 1
            return original_forward(self, layer, query, key, value, kv_cache, attn_metadata, output,
                                    output_scale=output_scale, output_block_scale=output_block_scale)
        plan.prepare_consumer(torch)
        token = _CONTEXT.set(plan)
        try:
            result = base_forward(self, layer, query, key, value, kv_cache, attn_metadata, output,
                                  output_scale=output_scale, output_block_scale=output_block_scale)
        finally:
            _CONTEXT.reset(token)
        _COUNTS["forward_selected"] += 1
        if _REAL.get():
            _COUNTS["real_forward_selected"] += 1
        if _COUNTS["forward_selected"] == 1 or (_REAL.get() and _COUNTS["real_forward_selected"] == 1):
            print("BIV150_MAPPED_DECODE_FIRST_SELECTED real_execute=" + str(int(_REAL.get()))
                  + " decode_requests=" + str(len(plan.gpu_indices))
                  + " forward_selected=" + str(_COUNTS["forward_selected"]), flush=True)
        return result

    setattr(build, _MARKER, True)
    setattr(forward, _MARKER, True)
    builder_cls.build, impl_cls.forward = build, forward
    backend.unified_attention = unified
    return {"original_build": original_build, "original_forward": original_forward,
            "original_unified": unified.original, "proxy": unified}


def install(runner_cls, *, enabled=False):
    if enabled is not True:
        return False
    if getattr(runner_cls, _MARKER, False):
        return False
    from .biv150_mapped_decode_source import EXPECTED_RUNNER, RUNNER_FOOTER
    module = sys.modules[runner_cls.__module__]
    source = Path(module.__file__).read_bytes()
    if (not source.endswith(RUNNER_FOOTER)
            or hashlib.sha256(source[:-len(RUNNER_FOOTER)]).hexdigest() != EXPECTED_RUNNER):
        raise RuntimeError("unaudited mapped runner/source footer")
    modules = _dependencies()
    backend = modules["vllm.v1.attention.backends.triton_attn"]
    attention = modules["vllm.v1.attention.ops.triton_unified_attention"]
    if backend.unified_attention is not attention.unified_attention:
        raise RuntimeError("unknown pre-existing backend Attention replacement")
    original_execute = runner_cls.execute_model
    if (runner_cls.__name__ != "ModelRunnerFL"
            or inspect.unwrap(original_execute).__qualname__ != "ModelRunnerFL.execute_model"
            or Path(inspect.unwrap(original_execute).__code__.co_filename).resolve()
            != Path(module.__file__).resolve()):
        raise RuntimeError("unknown execute_model identity")
    import torch
    _wrap_backend(backend, load_derived(), torch, modules["vllm_fl.patches.biv150_mixed_decode"])

    @wraps(original_execute)
    def execute(self, *args, **kwargs):
        token = _REAL.set(True)
        try:
            return original_execute(self, *args, **kwargs)
        finally:
            _REAL.reset(token)
    runner_cls.execute_model = execute
    setattr(runner_cls, _MARKER, True)
    print("BIV150_MAPPED_DECODE_INSTALLED request_and_sampling_rows_unchanged=1", flush=True)
    return True
