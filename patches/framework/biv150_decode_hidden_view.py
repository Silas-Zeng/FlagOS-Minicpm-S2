"""Unintegrated runner-source candidate: prefix view for audited one-token rows.

Pure Python transformation; importing this module does not import torch/vLLM,
write files, install a patch, or touch a device. Apply only to a fresh copy of
the exact retained runner, before appending any other candidate footer.
"""

from __future__ import annotations

import hashlib
import inspect


EXPECTED_RUNNER_SHA256 = "446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64"
MARKER = "# _biv150_decode_hidden_view_candidate_v1"
_ASSIGNMENT = "                sample_hidden_states = hidden_states[logits_indices]\n"
_COMMON = _ASSIGNMENT + "                logits = self.model.compute_logits(sample_hidden_states)\n"
_BROADCAST = "                # Rare case.\n                assert not self.is_pooling_model\n\n" + _ASSIGNMENT
_CLASS = "class ModelRunnerFL(\n"


def _biv150_decode_hidden_view_eligible(
    runner, hidden_states, logits_indices,
    max_num_scheduled_tokens, num_tokens_unpadded, num_reqs,
    spec_decode_metadata, aux_hidden_states,
    should_ubatch, ubatch_slices, ubatch_slices_padded, torch_module,
):
    """Metadata-only predicate; never read device tensor contents or allocate.

    The exact source hash supplies the index provenance. For nonnegative q_i,
    max(q_i)=1 and sum(q_i)=N imply all N q_i=1. The retained _prepare_inputs
    then gives logits_indices = cumsum(q_i)-1 = [0, ..., N-1].
    """
    if (
        any(type(value) is not int for value in (
            max_num_scheduled_tokens, num_tokens_unpadded, num_reqs))
        or num_reqs <= 0
        or max_num_scheduled_tokens != 1
        or num_tokens_unpadded != num_reqs
        or spec_decode_metadata is not None
        or aux_hidden_states is not None
        or should_ubatch is not False
        or ubatch_slices is not None
        or ubatch_slices_padded is not None
    ):
        return False
    try:
        model = runner.model_config
        parallel = runner.parallel_config
        text = model.hf_text_config
        loaded = runner.model
        processor = loaded.logits_processor
        quant_method = loaded.lm_head.quant_method
        compute = loaded.compute_logits
        return (
            str(model.model).replace("\\", "/").rstrip("/").rsplit("/", 1)[-1] == "MiniCPM5-2B"
            and model.dtype == torch_module.bfloat16
            and model.runner_type == "generate"
            and model.quantization is None
            and model.is_encoder_decoder is False
            and (text.model_type, text.hidden_size, text.num_hidden_layers,
                 text.num_attention_heads, text.num_key_value_heads,
                 text.intermediate_size, text.vocab_size)
                == ("llama", 2048, 42, 16, 2, 6144, 130560)
            and all(getattr(parallel, name) == 1 for name in (
                "tensor_parallel_size", "pipeline_parallel_size",
                "decode_context_parallel_size", "data_parallel_size"))
            and parallel.use_ubatching is False
            and runner.speculative_config is None
            and runner.lora_config is None
            and runner.vllm_config.quant_config is None
            and runner.vllm_config.kv_transfer_config is None
            and runner.vllm_config.ec_transfer_config is None
            and runner.cache_config.kv_sharing_fast_prefill is False
            and not runner.kv_sharing_fast_prefill_eligible_layers
            and runner.use_aux_hidden_state_outputs is False
            and runner.is_pooling_model is False
            and runner.broadcast_pp_output is False
            and runner.enable_prompt_embeds is False
            and runner.supports_mm_inputs is False
            and not runner.num_prompt_logprobs
            and type(loaded).__module__ == "vllm.model_executor.models.llama"
            and type(loaded).__name__ == "LlamaForCausalLM"
            and getattr(compute, "__func__", None) is type(loaded).compute_logits
            and compute.__func__.__module__ == "vllm.model_executor.models.llama"
            and type(processor).__module__ == "vllm.model_executor.layers.logits_processor"
            and type(processor).__name__ == "LogitsProcessor"
            and processor.logits_as_input is False
            and type(quant_method).__module__ == "vllm.model_executor.layers.vocab_parallel_embedding"
            and type(quant_method).__name__ == "UnquantizedEmbeddingMethod"
            and isinstance(hidden_states, torch_module.Tensor)
            and hidden_states.dtype == torch_module.bfloat16
            and hidden_states.device == runner.device
            and hidden_states.ndim == 2
            and hidden_states.shape[0] >= num_reqs
            and hidden_states.shape[1] == 2048
            and hidden_states.is_contiguous()
            and hidden_states.storage_offset() == 0
            and isinstance(logits_indices, torch_module.Tensor)
            and logits_indices.device == hidden_states.device
            and logits_indices.ndim == 1
            and logits_indices.shape[0] == num_reqs
            and logits_indices.dtype in (torch_module.int32, torch_module.int64)
        )
    except (AttributeError, TypeError, ValueError, RuntimeError):
        # Unknown configuration/layout keeps the exact retained gather.
        return False


def transform_source(runner_source: bytes) -> bytes:
    """Change only the ordinary branch; broadcast/PP remains byte-for-byte.

    This changes ownership (copy -> view), so profiling and installed logits
    implementation/lifetime validation remain required before integration.
    """
    if not isinstance(runner_source, bytes):
        raise TypeError("runner source must be bytes")
    actual = hashlib.sha256(runner_source).hexdigest()
    if actual != EXPECTED_RUNNER_SHA256:
        raise RuntimeError(f"unaudited runner source: expected {EXPECTED_RUNNER_SHA256}, got {actual}")
    source = runner_source.decode("utf-8")
    if (MARKER in source or "_biv150_decode_hidden_view_eligible" in source
            or source.count(_ASSIGNMENT) != 2 or source.count(_COMMON) != 1
            or source.count(_BROADCAST) != 1 or source.count(_CLASS) != 1):
        raise RuntimeError("unexpected retained runner hidden-state anchors")
    replacement = '''                if _biv150_decode_hidden_view_eligible(
                    self, hidden_states, logits_indices,
                    max_num_scheduled_tokens, num_tokens_unpadded, num_reqs,
                    spec_decode_metadata, aux_hidden_states,
                    should_ubatch, ubatch_slices, ubatch_slices_padded, torch,
                ):
                    sample_hidden_states = hidden_states[:num_reqs]
                else:
                    sample_hidden_states = hidden_states[logits_indices]
                logits = self.model.compute_logits(sample_hidden_states)
'''
    source = source.replace(_COMMON, replacement, 1)
    helper = MARKER + "\n" + inspect.getsource(_biv150_decode_hidden_view_eligible) + "\n\n"
    return source.replace(_CLASS, helper + _CLASS, 1).encode("utf-8")


transform = transform_source
