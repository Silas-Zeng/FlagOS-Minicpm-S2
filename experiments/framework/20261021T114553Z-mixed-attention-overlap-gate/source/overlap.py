"""Explicit single-layer prototype: overlap the exact existing C3 split.

This object does not install a serving patch. Its caller must eventually wait
for completion and collect pending frames. Full-model retention/memory and
accuracy are unverified; the sole immediate consumer is the short GPU gate.
"""
from collections import deque
from dataclasses import dataclass
import hashlib
from pathlib import Path


EXPECTED_MIXED = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"


def _require_file(module, expected):
    if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
        raise RuntimeError("unaudited overlap dependency: " + module.__name__)


@dataclass
class _Pending:
    ready: object
    done: object
    references: tuple


class MixedAttentionOverlap:
    """No class/file mutation; call forward explicitly instead of serving install."""
    def __init__(self, backend, mixed, torch, device):
        _require_file(mixed, EXPECTED_MIXED)
        _require_file(backend, mixed.EXPECTED_BACKEND_SHA256)
        import importlib
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        _require_file(attention, mixed.EXPECTED_ATTENTION_SHA256)
        _require_file(helpers, mixed.EXPECTED_HELPERS_SHA256)
        mixed._require_fast_runtime(attention)
        serial = backend.TritonAttentionImpl.forward
        base = getattr(serial, "__wrapped__", None)
        if (attention.current_platform.vendor_name != "iluvatar"
                or backend.unified_attention is not attention.unified_attention
                or not getattr(serial, mixed._MARKER, False)
                or base is None
                or Path(serial.__code__.co_filename).resolve() != Path(mixed.__file__).resolve()
                or Path(base.__code__.co_filename).resolve() != Path(backend.__file__).resolve()
                or base.__globals__ is not vars(backend)):
            raise RuntimeError("overlap requires the exact installed C3/base forward binding")
        if torch.cuda.is_current_stream_capturing():
            raise RuntimeError("overlap prototype cannot be created during capture")
        self.backend, self.mixed, self.torch = backend, mixed, torch
        self.serial, self.base = serial, base
        self.device = torch.device(device)
        self.side = torch.cuda.Stream(device=self.device)
        self.pending = deque()
        self.selected_calls, self.fallback_calls, self.peak_pending = 0, 0, 0

    def collect_completed(self):
        """Release strong references only after the actual side done event completes."""
        removed = 0
        while self.pending and self.pending[0].done.query():
            self.pending.popleft()
            removed += 1
        return removed

    def _references(self, layer, query, key, value, cache, metadata, output, plan):
        torch = self.torch
        objects = [layer, query, key, value, cache, metadata, output, plan, plan.decode, plan.prefill]
        for md in (metadata, plan.decode, plan.prefill):
            for name in ("query_start_loc", "seq_lens", "block_table", "slot_mapping",
                         "softmax_segm_output", "softmax_segm_max", "softmax_segm_expsum"):
                objects.append(getattr(md, name, None))
        for name in ("_q_scale", "_k_scale", "_v_scale"):
            objects.append(getattr(layer, name, None))
        tensors, seen = [], set()
        for value in objects:
            if isinstance(value, torch.Tensor):
                if value.device != self.device:
                    return None, None
                storage = value.untyped_storage().data_ptr()
                if storage not in seen:
                    seen.add(storage)
                    tensors.append(value)
        return tuple(objects), tuple(tensors)

    def forward(self, impl, layer, query, key, value, cache, metadata, output,
                output_scale=None, output_block_scale=None):
        torch, mixed = self.torch, self.mixed
        plan = getattr(metadata, mixed._PLAN, None)
        capture = torch.cuda.is_current_stream_capturing()
        eligible = (not capture and plan is not None
                    and mixed._impl_eligible(impl, self.backend, torch, query, key, value,
                                            cache, metadata, output, output_scale, output_block_scale)
                    and query.device == self.device
                    and 0 < plan.prefix_tokens < plan.total_tokens
                    and plan.decode.max_query_len == 1 and plan.prefill.max_query_len > 1
                    and plan.decode.num_actual_tokens == plan.prefix_tokens
                    and plan.prefill.num_actual_tokens == plan.total_tokens - plan.prefix_tokens
                    and output.stride() == (2048, 128, 1))
        if eligible:
            writable = {output.untyped_storage().data_ptr()}
            scratch = (plan.decode.softmax_segm_output, plan.decode.softmax_segm_max,
                       plan.decode.softmax_segm_expsum)
            read_storages = {x.untyped_storage().data_ptr() for x in (query, key, value, cache)}
            scratch_storages = {x.untyped_storage().data_ptr() for x in scratch}
            eligible = (not writable.intersection(read_storages | scratch_storages)
                        and len(scratch_storages) == 3
                        and not scratch_storages.intersection(read_storages))
        if not eligible:
            self.fallback_calls += 1
            return self.serial(impl, layer, query, key, value, cache, metadata, output,
                               output_scale=output_scale, output_block_scale=output_block_scale)
        self.collect_completed()
        plan.prepare_consumer(torch)
        current = torch.cuda.current_stream(device=self.device)
        if current == self.side:
            self.fallback_calls += 1
            return self.serial(impl, layer, query, key, value, cache, metadata, output,
                               output_scale=output_scale, output_block_scale=output_block_scale)
        references, tensors = self._references(layer, query, key, value, cache, metadata, output, plan)
        if references is None:
            self.fallback_calls += 1
            return self.serial(impl, layer, query, key, value, cache, metadata, output,
                               output_scale=output_scale, output_block_scale=output_block_scale)
        ready = torch.cuda.Event(enable_timing=False)
        done = torch.cuda.Event(enable_timing=False)
        frame = _Pending(ready, done, references)
        # Retain before enqueue. Any later exception is an experiment failure;
        # never fall back after partially launching the split.
        self.pending.append(frame)
        self.peak_pending = max(self.peak_pending, len(self.pending))
        for tensor in tensors:
            tensor.record_stream(self.side)
        # The actual caller already enqueued KV update on current. This record
        # is after that update and Q/metadata producers; no host synchronization.
        ready.record(current)
        self.side.wait_event(ready)
        boundary, total = plan.prefix_tokens, plan.total_tokens
        with torch.cuda.stream(self.side):
            self.base(impl, layer, query[:boundary], key[:boundary], value[:boundary],
                      cache, plan.decode, output[:boundary],
                      output_scale=output_scale, output_block_scale=output_block_scale)
            done.record(self.side)  # Includes the 3D reducer, not just partials.
        self.base(impl, layer, query[boundary:total], key[boundary:total], value[boundary:total],
                  cache, plan.prefill, output[boundary:total],
                  output_scale=output_scale, output_block_scale=output_block_scale)
        current.wait_event(done)  # Original O/MLP may be queued only after this.
        self.selected_calls += 1
        return output
