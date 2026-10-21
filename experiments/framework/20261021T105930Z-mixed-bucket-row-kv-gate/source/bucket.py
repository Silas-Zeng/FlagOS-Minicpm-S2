"""Opt-in prefill/mixed NONE row buckets; real Attention/sampling stay unpadded.

Install only on a new copy of the frozen SQL+C2+mixed source.  This module is
not imported by the current candidate or the submission patch.  It changes
physical model rows, so its accuracy and performance are still unverified.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass, replace
import functools
import hashlib
import importlib
from pathlib import Path
import sys


EXPECTED_RUNNER_SHA256 = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_BACKEND_SHA256 = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_KV_WRITER_SHA256 = "f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb"
FOOTER_BOUNDARY = b"\n# BIV150_MIXED_TOKEN_BUCKET_OPT_IN_V1\n"
EXPECTED_FOOTER_SHA256 = "21074c950f7ebfec73215f8db746f13b6980779277b084cec6c79e27b706e620"
_MARKER = "_biv150_mixed_token_bucket"
_EXECUTION = ContextVar("biv150_mixed_token_bucket_execution", default=None)


@dataclass
class _Execution:
    runner: object
    scheduler_output: object
    actual: int = 0
    padded: int = 0


def _require_source(module, expected):
    actual = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
    if expected is None or actual != expected:
        raise RuntimeError(f"unaudited token-bucket dependency: {module.__name__}: {actual}")


def _require_runner_source(runner_class):
    module = sys.modules[runner_class.__module__]
    raw = Path(module.__file__).read_bytes()
    count = raw.count(FOOTER_BOUNDARY)
    if count > 1:
        raise RuntimeError("duplicate token-bucket footer")
    original = raw.split(FOOTER_BOUNDARY, 1)[0]
    if count and hashlib.sha256(raw[len(original):]).hexdigest() != EXPECTED_FOOTER_SHA256:
        raise RuntimeError("unaudited token-bucket installation footer")
    if hashlib.sha256(original).hexdigest() != EXPECTED_RUNNER_SHA256:
        raise RuntimeError("token buckets require the exact frozen SQL+C2+mixed runner prefix")
    if module.ModelRunnerFL is not runner_class:
        raise RuntimeError("unexpected ModelRunnerFL binding")
    return module


def _eligible(runner, module, backend, torch):
    config = runner.vllm_config
    model, parallel = config.model_config, config.parallel_config
    text = model.hf_text_config
    groups = runner.attn_groups
    return (
        Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
        and model.dtype == torch.bfloat16
        and model.quantization is None
        and (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
             text.num_attention_heads, text.num_key_value_heads) == (2048, 6144, 42, 16, 2)
        and text.architectures == ["LlamaForCausalLM"]
        and text.hidden_act == "silu"
        and not model.is_encoder_decoder
        and not runner.is_pooling_model and not runner.supports_mm_inputs
        and not runner.enable_prompt_embeds and not runner.uses_mrope
        and runner.uses_xdrope_dim == 0
        and not runner.use_aux_hidden_state_outputs and not runner.broadcast_pp_output
        and runner.uniform_decode_query_len == 1
        and config.speculative_config is None and config.lora_config is None
        and not config.cache_config.kv_sharing_fast_prefill
        and config.cache_config.cache_dtype in ("auto", "bfloat16")
        and not runner.calculate_kv_scales
        and all(getattr(parallel, name, None) == 1 for name in (
            "tensor_parallel_size", "pipeline_parallel_size",
            "data_parallel_size", "decode_context_parallel_size"))
        and not parallel.use_ubatching
        and not config.compilation_config.pass_config.enable_sp
        and config.compilation_config.cudagraph_mode == module.CUDAGraphMode.FULL_DECODE_ONLY
        and not module.envs.VLLM_BATCH_INVARIANT
        and not module.has_kv_transfer_group() and not module.has_ec_transfer()
        and runner.cross_layers_kv_cache is None
        and runner.cross_layers_attn_backend is None
        and not runner.shared_kv_cache_layers
        and runner.device.type == "cuda"
        and runner.input_ids.gpu.device == runner.device
        and runner.positions.device == runner.device
        and runner.input_ids.gpu.ndim == runner.positions.ndim == 1
        and len(groups) == 1 and len(groups[0]) > 0
        and all(group.backend is backend.TritonAttentionBackend for group in groups[0])
        and not torch.cuda.is_current_stream_capturing()
    )


def _wrap_runner(runner_class, module, backend, torch):
    """Small internal seam for CPU contract checks; install owns exact guards."""
    original_execute = runner_class.execute_model
    original_determine = runner_class._determine_batch_execution_and_padding
    original_preprocess = runner_class._preprocess
    wrapped = [getattr(method, _MARKER, False) for method in (
        original_execute, original_determine, original_preprocess)]
    if any(wrapped):
        if not all(wrapped):
            raise RuntimeError("partially installed token-bucket wrappers")
        return

    @functools.wraps(original_execute)
    def execute(self, scheduler_output, intermediate_tensors=None):
        # Only real execution can authorize a bucket.  Profile/dummy/capture
        # callers of determine never receive this per-call plan.
        token = _EXECUTION.set(_Execution(self, scheduler_output))
        try:
            return original_execute(self, scheduler_output, intermediate_tensors)
        finally:
            _EXECUTION.reset(token)

    @functools.wraps(original_determine)
    def determine(self, num_tokens, num_reqs, num_scheduled_tokens_np,
                  max_num_scheduled_tokens, use_cascade_attn,
                  allow_microbatching=True, force_eager=False,
                  force_uniform_decode=None, force_has_lora=None,
                  force_num_active_loras=None, num_encoder_reqs=0):
        result = original_determine(
            self, num_tokens, num_reqs, num_scheduled_tokens_np,
            max_num_scheduled_tokens, use_cascade_attn,
            allow_microbatching=allow_microbatching, force_eager=force_eager,
            force_uniform_decode=force_uniform_decode,
            force_has_lora=force_has_lora,
            force_num_active_loras=force_num_active_loras,
            num_encoder_reqs=num_encoder_reqs)
        context = _EXECUTION.get()
        mode, descriptor, ubatch, across_dp, stats = result
        if (context is None or context.runner is not self
                or force_eager or force_uniform_decode is not None
                or force_has_lora is not None or force_num_active_loras is not None
                or use_cascade_attn or num_encoder_reqs or ubatch or across_dp is not None
                or mode != module.CUDAGraphMode.NONE or descriptor.uniform
                or num_tokens < 256 or max_num_scheduled_tokens <= 1
                or descriptor.num_tokens != num_tokens
                or num_tokens != context.scheduler_output.total_num_scheduled_tokens
                or context.scheduler_output.scheduled_encoder_inputs
                or context.scheduler_output.scheduled_spec_decode_tokens
                or not _eligible(self, module, backend, torch)):
            return result
        padded = ((num_tokens + 127) // 128) * 128
        capacity = min(self.max_num_tokens, self.input_ids.gpu.shape[0],
                       self.positions.shape[0])
        if padded == num_tokens or padded > capacity:
            return result
        # BatchDescriptor.num_reqs/uniform and all real scheduler metadata stay
        # unchanged.  Only the backbone's physical first dimension grows.
        descriptor = replace(descriptor, num_tokens=padded)
        if stats is not None:
            stats = module.CUDAGraphStat(
                num_unpadded_tokens=num_tokens, num_padded_tokens=padded,
                num_paddings=padded - num_tokens, runtime_mode=str(mode))
        context.actual, context.padded = num_tokens, padded
        if not getattr(self, "_biv150_bucket_first_selected", False):
            print(f"BIV150_MIXED_TOKEN_BUCKET_FIRST_SELECTED actual={num_tokens} padded={padded}",
                  flush=True)
            self._biv150_bucket_first_selected = True
        return mode, descriptor, ubatch, across_dp, stats

    @functools.wraps(original_preprocess)
    def preprocess(self, scheduler_output, num_input_tokens, intermediate_tensors=None):
        result = original_preprocess(self, scheduler_output, num_input_tokens,
                                     intermediate_tensors)
        context = _EXECUTION.get()
        if (context is None or context.runner is not self
                or context.scheduler_output is not scheduler_output or not context.padded):
            return result
        if (num_input_tokens != context.padded
                or scheduler_output.total_num_scheduled_tokens != context.actual
                or result[0] is None or result[1] is not None
                or result[0].shape[0] != context.padded
                or result[2].shape[0] != context.padded):
            raise RuntimeError("bucket preprocess contract changed before model execution")
        # The original preprocess already zeros positions[M:B]; the original
        # slot-mapping builder already fills slot_mapping[M:B] with -1.  This
        # one additional same-stream operation makes embedding tail IDs legal.
        result[0][context.actual:context.padded].zero_()
        return result

    for method in (execute, determine, preprocess):
        setattr(method, _MARKER, True)
    runner_class.execute_model = execute
    runner_class._determine_batch_execution_and_padding = determine
    runner_class._preprocess = preprocess


def install(runner_class):
    """Explicit footer entry; no file mutation or environment-triggered enable."""
    module = _require_runner_source(runner_class)
    backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
    writer = importlib.import_module("vllm.v1.attention.ops.triton_reshape_and_cache_flash")
    _require_source(backend, EXPECTED_BACKEND_SHA256)
    _require_source(writer, EXPECTED_KV_WRITER_SHA256)
    if (module.current_platform.vendor_name != "iluvatar"
            or backend.current_platform.vendor_name != "iluvatar"
            or backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash
            or backend.TritonAttentionBackend.forward_includes_kv_cache_update is not False):
        raise RuntimeError("unsupported token-bucket backend or KV writer binding")
    torch = importlib.import_module("torch")
    _wrap_runner(runner_class, module, backend, torch)
    return {"installed": True, "bucket": 128, "minimum_tokens": 256,
            "scope": "real BF16 MiniCPM nonuniform prefill/mixed NONE backbone rows only",
            "accuracy": "unverified", "performance": "unverified"}
