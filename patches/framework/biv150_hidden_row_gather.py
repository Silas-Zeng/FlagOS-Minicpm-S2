"""Opt-in exact BF16 final-hidden row copy for the audited runner seam.

The transformer is the only supported caller.  It supplies the real CPU query
lengths used to create non-speculative logits_indices in the exact runner.
Unsupported contracts return None and preserve the original indexing path.
No generated source per M, autotuning, float arithmetic, padding, or RNG work.
"""

from pathlib import Path

import numpy as np
import torch
import triton
import triton.language as tl
from vllm.platforms import current_platform


selected_launches = 0


@triton.jit(do_not_specialize=["rows", "count"])
def _copy_hidden_rows(src, indices, out, rows, count, WIDTH: tl.constexpr):
    row = tl.program_id(0)
    col = tl.arange(0, WIDTH)
    active = row < count
    raw = tl.load(indices + row, mask=active, other=0).to(tl.int64)
    source_row = tl.where(raw < 0, raw + rows, raw)
    valid = active & (source_row >= 0) & (source_row < rows)
    # A load/store only: BF16 payloads, signed zero and NaN bits stay intact.
    value = tl.load(src + source_row * WIDTH + col, mask=valid, other=0)
    tl.store(out + row * WIDTH + col, value, mask=valid)


def _runner_contract(runner):
    config = getattr(runner, "vllm_config", None)
    if config is None:
        return False
    model, parallel = config.model_config, config.parallel_config
    text = model.hf_text_config
    return (
        current_platform.vendor_name == "iluvatar"
        and Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
        and model.dtype == torch.bfloat16 and model.quantization is None
        and text.architectures == ["LlamaForCausalLM"]
        and (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
             text.num_attention_heads, text.num_key_value_heads) == (2048, 6144, 42, 16, 2)
        and not model.is_encoder_decoder
        and not runner.is_pooling_model and not runner.supports_mm_inputs
        and not runner.enable_prompt_embeds and not runner.use_aux_hidden_state_outputs
        and not runner.broadcast_pp_output
        and not runner.uses_mrope and runner.uses_xdrope_dim == 0
        and config.speculative_config is None and config.lora_config is None
        and runner.num_spec_tokens == 0 and not runner.use_async_spec_decode
        and runner._draft_token_ids is None
        and not config.cache_config.kv_sharing_fast_prefill
        and all(getattr(parallel, name, None) == 1 for name in (
            "tensor_parallel_size", "pipeline_parallel_size",
            "data_parallel_size", "decode_context_parallel_size"))
        and not parallel.use_ubatching
        and not config.compilation_config.pass_config.enable_sp
    )


def _tensor_contract(runner, hidden, indices):
    if not isinstance(hidden, torch.Tensor) or not isinstance(indices, torch.Tensor):
        return False
    return (
        hidden.device.type == "cuda" and hidden.device == indices.device == runner.device
        and hidden.dtype == torch.bfloat16 and indices.dtype in (torch.int32, torch.int64)
        and hidden.ndim == 2 and hidden.shape[1] == 2048
        and 0 < hidden.shape[0] <= runner.max_num_tokens
        and hidden.is_contiguous() and hidden.stride() == (2048, 1)
        and indices.ndim == 1 and 0 < indices.shape[0] == runner.input_batch.num_reqs
        and indices.stride(0) == 1
        and hidden.data_ptr() % 128 == 0 and indices.data_ptr() % 4 == 0
        and hidden.untyped_storage().data_ptr() != indices.untyped_storage().data_ptr()
    )


def _query_end_contract(runner, lengths, count, rows):
    """Prove bounds from the existing CPU source of logits_indices; no D2H.

    The pinned _prepare_inputs creates logits_indices=query_start_loc[1:]-1.
    This is a seam-specific proof, not a validator for arbitrary GPU indices.
    """
    if (not isinstance(lengths, np.ndarray) or lengths.dtype != np.int32
            or lengths.ndim != 1 or lengths.shape[0] != count
            or not np.all(lengths > 0)):
        return False
    ends = np.cumsum(lengths, dtype=np.int64)
    query_cpu = runner.query_start_loc.np
    return (
        isinstance(query_cpu, np.ndarray) and query_cpu.ndim == 1
        and query_cpu.dtype == np.int32 and query_cpu.shape[0] >= count + 1
        and query_cpu[0] == 0 and int(ends[-1]) <= rows
        and np.array_equal(query_cpu[1:count + 1], ends)
    )


def try_gather_hidden_rows(runner, hidden, indices, lengths):
    """Return a fresh N x 2048 tensor, or None before any candidate launch.

    Only the exact transformed non-speculative runner owns the valid-index
    construction contract.  Negative/reordered arbitrary indices are not a
    public scope even though the private copy kernel supports their valid values.
    """
    global selected_launches
    if (not _runner_contract(runner) or not _tensor_contract(runner, hidden, indices)
            or not _query_end_contract(runner, lengths, indices.shape[0], hidden.shape[0])
            or torch.cuda.is_current_stream_capturing()):
        return None
    out = torch.empty((indices.shape[0], 2048), dtype=hidden.dtype, device=hidden.device)
    _copy_hidden_rows[(indices.shape[0],)](
        hidden, indices, out, hidden.shape[0], indices.shape[0],
        WIDTH=2048, num_warps=2, num_stages=1)
    # Original stream readiness is unchanged; record allocator use on that stream.
    stream = torch.cuda.current_stream(device=hidden.device)
    for value in (hidden, indices, out):
        value.record_stream(stream)
    if selected_launches == 0:
        print("BIV150_HIDDEN_ROW_GATHER_FIRST_SELECTED bf16_copy=1", flush=True)
    selected_launches += 1
    return out
