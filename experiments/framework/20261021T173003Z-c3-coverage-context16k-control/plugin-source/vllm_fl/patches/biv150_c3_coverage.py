"""Opt-in CPU-only observations of the exact SQL+C3 runner.

No metadata, request ordering, tensor, sampler or forward is changed. A plan
counter records creation only: Impl.forward has additional guards. Snapshots
are cumulative over observed execute calls, not proof of workload completion.
Import and byte transformation use only the standard library.
"""
from __future__ import annotations

import atexit
from contextvars import ContextVar
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import weakref


EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_SOURCES = {
    "vllm.v1.attention.backend": "c524988a2223ec556bdb128a31c255075f0d07e7643e803b447975cd9c30a6b8",
    "vllm.v1.attention.backends.utils": "f1375ec8e3a2d5c77ab15773eef2c00a4117826a3c238ceb5bcd4efe9fa55381",
    "vllm.v1.worker.gpu_input_batch": "de1ea4fc9d43fc6079dd375e407c2b6d93f5e1a11f49732d13654c41eaf30a65",
    "vllm.v1.attention.backends.triton_attn": "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605",
    "vllm_fl.patches.biv150_mixed_decode": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
}
FOOTER = b"\n# _biv150_c3_coverage_v1\nfrom vllm_fl.patches.biv150_c3_coverage import install as _install_c3_coverage\n_install_c3_coverage(ModelRunnerFL, enabled=True)\n"
_ACTIVE = ContextVar("biv150_c3_coverage", default=None)
_STATES: list[weakref.ReferenceType] = []
_MARKER = "_biv150_c3_coverage_v1"
_STATE = "_biv150_c3_coverage_state"


def transform_source(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_RUNNER:
        raise RuntimeError("C3 coverage requires the exact unmodified SQL+C3 runner")
    return source + FOOTER


def _emit(state, reason):
    try:
        payload = {"pid": os.getpid(), "reason": reason,
                   "workload_complete": False, "plan_is_forward_execution": False,
                   **state["counts"]}
        print("BIV150_C3_COVERAGE " + json.dumps(payload, sort_keys=True), flush=True)
    except Exception:
        # Observation I/O must never replace an original result/exception.
        pass


def _at_exit():
    for reference in _STATES:
        runner = reference()
        if runner is not None:
            _emit(getattr(runner, _STATE), "process_exit")


def _state(runner):
    state = getattr(runner, _STATE, None)
    if state is None:
        names = ("execute_calls", "execute_errors", "metadata_steps", "metadata_build_calls",
                 "multiple_metadata_steps", "observation_errors", "mixed_steps",
                 "pure_single_query_steps", "pure_multi_query_steps", "requests", "tokens",
                 "mixed_single_query_requests", "mixed_prefix_requests", "mixed_planned_requests",
                 "mixed_decode_requests", "mixed_decode_in_prefix", "mixed_decode_planned",
                 "mixed_single_query_outside_prefix", "mixed_without_prefix",
                 "mixed_prefix_without_plan", "padding_or_unsupported_steps")
        state = {"counts": dict.fromkeys(names, 0)}
        setattr(runner, _STATE, state)
        _STATES.append(weakref.ref(runner))
    return state


def _scope(runner):
    try:
        config = runner.vllm_config
        model, parallel = config.model_config, config.parallel_config
        text = model.hf_text_config
        return (Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
                and str(model.dtype) == "torch.bfloat16"
                and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
                     text.num_key_value_heads) == (2048, 42, 16, 2)
                and all(getattr(parallel, key, None) == 1 for key in (
                    "tensor_parallel_size", "pipeline_parallel_size",
                    "decode_context_parallel_size", "data_parallel_size"))
                and parallel.use_ubatching is False
                and config.speculative_config is None and config.lora_config is None
                and runner.use_async_spec_decode is False
                and runner.is_pooling_model is False
                and runner.supports_mm_inputs is False)
    except Exception:
        return False


def _observe(runner, frame, values, result):
    counts = frame["state"]["counts"]
    if values.get("for_cudagraph_capture", False):
        return
    counts["metadata_build_calls"] += 1
    if frame["seen"]:
        counts["multiple_metadata_steps"] += int(frame["seen"] == 1)
        frame["seen"] += 1
        return
    frame["seen"] = 1
    tokens, number = values["num_tokens"], values["num_reqs"]
    per_layer, _ = result
    if not isinstance(per_layer, dict) or not per_layer:
        counts["padding_or_unsupported_steps"] += 1
        return
    backend = sys.modules["vllm.v1.attention.backends.triton_attn"]
    unique = {id(value): value for value in per_layer.values()}
    candidates = [value for value in unique.values()
                  if type(value) is backend.TritonAttentionMetadata]
    if (len(candidates) != 1 or len(unique) != 1
            or values.get("use_spec_decode", False)
            or values.get("ubatch_slices") is not None):
        counts["padding_or_unsupported_steps"] += 1
        return
    metadata = candidates[0]
    cpu = runner.query_start_loc.cpu
    if (cpu.device.type != "cpu" or number != runner.input_batch.num_reqs
            or metadata.num_actual_tokens != tokens or metadata.seq_lens.shape[0] != number
            or metadata.query_start_loc.shape[0] != number + 1):
        counts["padding_or_unsupported_steps"] += 1
        return
    offsets = cpu[:number + 1].tolist()
    lengths = [right - left for left, right in zip(offsets, offsets[1:])]
    if (not lengths or offsets[0] != 0 or offsets[-1] != tokens
            or min(lengths) <= 0 or max(lengths) != metadata.max_query_len):
        raise RuntimeError("unexpected real CPU query offsets")
    single = [length == 1 for length in lengths]
    prefix = next((index for index, value in enumerate(single) if not value), number)
    plan = getattr(metadata, "_biv150_natural_prefix_plan", None)
    planned = 0 if plan is None else plan.prefix_tokens
    if not isinstance(planned, int) or not 0 <= planned <= prefix:
        raise RuntimeError("unexpected original C3 plan")
    computed = runner.input_batch.num_computed_tokens_cpu[:number]
    prompts = runner.input_batch.num_prompt_tokens[:number]
    decode = [one and int(done) > 0 and int(done) >= int(prompt)
              for one, done, prompt in zip(single, computed, prompts)]
    counts["metadata_steps"] += 1
    counts["requests"] += number
    counts["tokens"] += tokens
    if max(lengths) == 1:
        counts["pure_single_query_steps"] += 1
    elif not any(single):
        counts["pure_multi_query_steps"] += 1
    else:
        counts["mixed_steps"] += 1
        counts["mixed_single_query_requests"] += sum(single)
        counts["mixed_prefix_requests"] += prefix
        counts["mixed_planned_requests"] += planned
        counts["mixed_decode_requests"] += sum(decode)
        counts["mixed_decode_in_prefix"] += sum(decode[:prefix])
        counts["mixed_decode_planned"] += sum(decode[:planned])
        counts["mixed_single_query_outside_prefix"] += sum(single) - prefix
        counts["mixed_without_prefix"] += int(prefix == 0)
        counts["mixed_prefix_without_plan"] += int(prefix > 0 and planned == 0)


def install(runner_cls, *, enabled=False):
    if enabled is not True:
        return False
    if getattr(runner_cls, _MARKER, False):
        return False
    module = sys.modules[runner_cls.__module__]
    source = Path(module.__file__).read_bytes()
    if (not source.endswith(FOOTER)
            or hashlib.sha256(source[:-len(FOOTER)]).hexdigest() != EXPECTED_RUNNER):
        raise RuntimeError("unaudited coverage runner/source footer")
    for name, expected in EXPECTED_SOURCES.items():
        dependency = sys.modules.get(name)
        if dependency is None or hashlib.sha256(Path(dependency.__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("unaudited coverage dependency: " + name)
    original_execute = runner_cls.execute_model
    original_metadata = runner_cls._build_attention_metadata
    for function in (original_execute, original_metadata):
        original = inspect.unwrap(function)
        if (original.__module__ != module.__name__
                or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise RuntimeError("unexpected pre-existing runner wrapper")
    signature = inspect.signature(original_metadata)

    @wraps(original_execute)
    def execute(self, *args, **kwargs):
        if _ACTIVE.get() is not None or not _scope(self):
            return original_execute(self, *args, **kwargs)
        state = _state(self)
        state["counts"]["execute_calls"] += 1
        frame = {"runner": self, "state": state, "seen": 0}
        token = _ACTIVE.set(frame)
        try:
            return original_execute(self, *args, **kwargs)
        except BaseException:
            state["counts"]["execute_errors"] += 1
            raise
        finally:
            _ACTIVE.reset(token)
            if state["counts"]["execute_calls"] == 1 or state["counts"]["execute_calls"] % 64 == 0:
                _emit(state, "periodic")

    @wraps(original_metadata)
    def metadata(self, *args, **kwargs):
        result = original_metadata(self, *args, **kwargs)
        frame = _ACTIVE.get()
        if frame is not None and frame["runner"] is self:
            try:
                values = signature.bind(self, *args, **kwargs).arguments
                _observe(self, frame, values, result)
            except Exception:
                frame["state"]["counts"]["observation_errors"] += 1
        return result

    runner_cls.execute_model = execute
    runner_cls._build_attention_metadata = metadata
    setattr(runner_cls, _MARKER, True)
    atexit.register(_at_exit)
    print("BIV150_C3_COVERAGE_INSTALLED cpu_offsets_only=1 plan_is_forward_execution=0", flush=True)
    return True
