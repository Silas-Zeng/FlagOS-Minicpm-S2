"""Small CPU-only metadata, fallback and alias gates; no vLLM/GPU imports.

The tiny dataclass/call recorder models the wrapper interface, not Attention
arithmetic or CUDA ordering. Real H2D/kernel/accuracy gates remain necessary.
"""

from dataclasses import dataclass
import gc
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace as NS
import unittest
from unittest import mock
import weakref

import torch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "mixed_decode_candidate", ROOT / "patches/framework/biv150_mixed_decode.py")
candidate = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = candidate
SPEC.loader.exec_module(candidate)


class Stream:
    def __init__(self):
        self.waits = []

    def wait_stream(self, other):
        self.waits.append(other)


class FakeCuda:
    def __init__(self):
        self.stream = Stream()
        self.capturing = False

    def current_stream(self, device=None):
        return self.stream

    def is_current_stream_capturing(self):
        return self.capturing


@dataclass
class Metadata:
    num_actual_tokens: int
    max_query_len: int
    query_start_loc: object
    max_seq_len: int
    seq_lens: object
    block_table: object
    slot_mapping: object
    seq_threshold_3D: int = 64
    num_par_softmax_segments: int = 16
    softmax_segm_output: object = None
    softmax_segm_max: object = None
    softmax_segm_expsum: object = None
    causal: object = True
    use_cascade: bool = False
    common_prefix_len: int = 0
    mm_prefix_range: object = None
    mm_prefix_range_tensor: object = None
    scheduler_metadata: object = None
    prefix_scheduler_metadata: object = None


def common(lengths):
    offsets = [0]
    for length in lengths:
        offsets.append(offsets[-1] + length)
    return NS(num_reqs=len(lengths), num_actual_tokens=sum(lengths),
              max_query_len=max(lengths), max_seq_len=501,
              query_start_loc_cpu=torch.tensor(offsets, dtype=torch.int32),
              query_start_loc=torch.tensor(offsets, dtype=torch.int32),
              seq_lens=torch.arange(len(lengths), dtype=torch.int32) + 20,
              block_table_tensor=torch.arange(len(lengths) * 4).reshape(len(lengths), 4),
              slot_mapping=torch.arange(sum(lengths)), causal=True)


def backend_and_config():
    config = NS(
        model_config=NS(model="/workspace/MiniCPM5-2B", dtype=torch.bfloat16,
                        hf_text_config=NS(hidden_size=2048, num_hidden_layers=42,
                                          num_attention_heads=16, num_key_value_heads=2)),
        parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
                           decode_context_parallel_size=1, data_parallel_size=1,
                           use_ubatching=False), speculative_config=None, lora_config=None,
        cache_config=NS(kv_sharing_fast_prefill=False),
        compilation_config=NS(cudagraph_mode="FULL_DECODE_ONLY"))

    class Builder:
        num_heads_q, num_heads_kv, headdim, block_size = 16, 2, 128, 16

        def __init__(self):
            self.vllm_config, self.calls = config, []

        def build(self, common_prefix_len, common_attn_metadata, fast_build=False):
            self.calls.append((common_prefix_len, common_attn_metadata, fast_build))
            cm = common_attn_metadata
            return Metadata(cm.num_actual_tokens, cm.max_query_len, cm.query_start_loc,
                            cm.max_seq_len, cm.seq_lens, cm.block_table_tensor,
                            cm.slot_mapping, causal=cm.causal,
                            softmax_segm_output=torch.empty(64, 1),
                            softmax_segm_max=torch.empty(64, 1),
                            softmax_segm_expsum=torch.empty(64, 1),
                            common_prefix_len=common_prefix_len,
                            use_cascade=common_prefix_len > 0)

    class Impl:
        attn_type = "DECODER"
        num_heads, num_kv_heads, head_size = 16, 2, 128
        _kv_quant_mode, kv_cache_dtype, _is_per_token_head_quant = 0, "auto", False
        kv_sharing_target_layer_name = None
        alibi_slopes = sinks = None
        use_alibi_sqrt = use_td = False
        sliding_window, logits_soft_cap, chunk_lookback = (-1, -1), 0, -1

        def __init__(self):
            self.calls = []

        def forward(self, layer, query, key, value, kv_cache, attn_metadata, output,
                    output_scale=None, output_block_scale=None):
            self.calls.append(dict(layer=layer, query=query, key=key, value=value,
                                   kv_cache=kv_cache, attn_metadata=attn_metadata,
                                   output=output, output_scale=output_scale,
                                   output_block_scale=output_block_scale))
            # Token ownership depends on correctly normalized child offsets.
            cu = attn_metadata.query_start_loc.tolist()
            for row, (start, end) in enumerate(zip(cu, cu[1:])):
                output[start:end].copy_(query[start:end] + attn_metadata.seq_lens[row])
            return output

    return NS(TritonAttentionMetadataBuilder=Builder, TritonAttentionImpl=Impl,
              CUDAGraphMode=NS(FULL_DECODE_ONLY="FULL_DECODE_ONLY"),
              AttentionType=NS(DECODER="DECODER"), KVQuantMode=NS(NONE=0),
              envs=NS(VLLM_BATCH_INVARIANT=False)), config


class MixedDecodeTests(unittest.TestCase):
    def setUp(self):
        self.backend, self.config = backend_and_config()
        self.original_forward = self.backend.TritonAttentionImpl.forward
        self.cuda = FakeCuda()
        self.api = NS(bfloat16=torch.bfloat16, cuda=self.cuda)
        # The production helper strictly rejects CPU tensors. Tests override
        # just this descriptor predicate, with all arithmetic still on CPU.
        self.device_patch = mock.patch.object(candidate, "_cuda_tensors", return_value=True)
        self.device_patch.start()
        self.addCleanup(self.device_patch.stop)
        candidate._wrap_backend(self.backend, self.api)
        self.builder = self.backend.TritonAttentionMetadataBuilder()
        self.impl = self.backend.TritonAttentionImpl()

    def inputs(self, cm, padding=3):
        n = cm.num_actual_tokens + padding
        return dict(layer=object(), query=torch.randn(n, 16, 128, dtype=torch.bfloat16),
                    key=torch.randn(n, 2, 128, dtype=torch.bfloat16),
                    value=torch.randn(n, 2, 128, dtype=torch.bfloat16),
                    kv_cache=torch.empty(2, 2, 16, 2, 128, dtype=torch.bfloat16),
                    output=torch.full((n, 16, 128), -999, dtype=torch.bfloat16))

    def test_once_built_plan_normalizes_multi_request_suffix(self):
        cm = common([1, 1, 7, 9])
        metadata = self.builder.build(0, cm)
        plan = getattr(metadata, candidate._PLAN)
        self.assertEqual(len(self.builder.calls), 1)
        self.assertIs(self.builder.calls[0][1], cm)
        self.assertEqual(plan.decode.query_start_loc.tolist(), [0, 1, 2])
        self.assertEqual(plan.prefill.query_start_loc.tolist(), [0, 7, 16])
        self.assertEqual(plan.prefill.max_query_len, 9)
        self.assertEqual(plan.decode.max_seq_len, cm.max_seq_len)
        self.assertEqual(cm.query_start_loc.tolist(), [0, 1, 2, 9, 18])
        self.assertEqual(plan.prefill.block_table.stride(), cm.block_table_tensor.stride())
        self.assertEqual(plan.prefill.block_table.data_ptr(), cm.block_table_tensor[2:].data_ptr())
        self.assertIs(plan.decode.softmax_segm_output, metadata.softmax_segm_output)

    def test_zero_nonprefix_all_decode_and_capacity_fallback(self):
        for lengths in ([7, 1, 9], [7, 9], [1, 1], [1, 0, 7], [0, 1, 7], [1] * 65 + [7]):
            with self.subTest(lengths=lengths):
                metadata = self.builder.build(0, common(lengths))
                self.assertFalse(hasattr(metadata, candidate._PLAN))
        cm = common([1, 7])
        cm.num_actual_tokens += 1
        self.assertFalse(hasattr(self.builder.build(0, cm), candidate._PLAN))

    def test_config_and_metadata_guards(self):
        targets = [(self.config, "speculative_config", object()),
                   (self.config, "lora_config", object()),
                   (self.config.parallel_config, "use_ubatching", True),
                   (self.config.parallel_config, "tensor_parallel_size", 2),
                   (self.config.cache_config, "kv_sharing_fast_prefill", True),
                   (self.config.model_config, "model", "/workspace/OtherModel"),
                   (self.config.compilation_config, "cudagraph_mode", "FULL"),
                   (self.backend.envs, "VLLM_BATCH_INVARIANT", True)]
        for target, name, value in targets:
            with self.subTest(name=name), mock.patch.object(target, name, value):
                self.assertFalse(hasattr(self.builder.build(0, common([1, 7])), candidate._PLAN))
        cm = common([1, 7])
        cm.causal = torch.tensor(True)
        self.assertFalse(hasattr(self.builder.build(0, cm), candidate._PLAN))
        self.assertFalse(hasattr(self.builder.build(1, common([1, 7])), candidate._PLAN))

    def test_split_kwargs_output_alias_and_padding_sentinel(self):
        cm = common([1, 1, 7, 9])
        metadata = self.builder.build(0, cm)
        data = self.inputs(cm)
        expected = data["output"].clone()
        reference = self.backend.TritonAttentionImpl()
        self.original_forward(reference, **{**data, "output": expected}, attn_metadata=metadata)
        returned = self.impl.forward(**data, attn_metadata=metadata)
        self.assertIs(returned, data["output"])
        self.assertTrue(torch.equal(returned, expected))
        self.assertEqual(len(self.impl.calls), 2)
        self.assertEqual(self.impl.calls[0]["query"].shape[0], 2)
        self.assertEqual(self.impl.calls[1]["query"].shape[0], 16)
        self.assertEqual(self.impl.calls[1]["output"].data_ptr(), data["output"][2:].data_ptr())
        self.assertIs(self.impl.calls[1]["kv_cache"], data["kv_cache"])
        self.assertIs(self.impl.calls[0]["layer"], data["layer"])
        self.assertTrue((returned[18:] == -999).all())

    def test_forward_fallback_preserves_all_parameter_objects(self):
        cm = common([1, 7])
        metadata = self.builder.build(0, cm)
        data = self.inputs(cm)
        scale, block_scale = object(), object()
        self.impl.forward(**data, attn_metadata=metadata,
                          output_scale=scale, output_block_scale=block_scale)
        self.assertEqual(len(self.impl.calls), 1)
        call = self.impl.calls[0]
        for name, value in data.items():
            self.assertIs(call[name], value)
        self.assertIs(call["attn_metadata"], metadata)
        self.assertIs(call["output_scale"], scale)
        self.assertIs(call["output_block_scale"], block_scale)
        for name, value in (("alibi_slopes", object()), ("sinks", object()),
                            ("sliding_window", (15, 0)), ("use_td", True),
                            ("kv_sharing_target_layer_name", "other_layer"),
                            ("_kv_quant_mode", 1), ("attn_type", "ENCODER")):
            with self.subTest(name=name), mock.patch.object(self.impl, name, value):
                self.impl.calls.clear()
                self.impl.forward(**data, attn_metadata=metadata)
                self.assertEqual(len(self.impl.calls), 1)
                self.assertIs(self.impl.calls[0]["query"], data["query"])

    def test_captured_and_pure_decode_paths_never_split(self):
        cm = common([1, 7])
        self.cuda.capturing = True
        self.assertFalse(hasattr(self.builder.build(0, cm), candidate._PLAN))
        self.cuda.capturing = False
        metadata = self.builder.build(0, cm)
        self.cuda.capturing = True
        self.impl.forward(**self.inputs(cm), attn_metadata=metadata)
        self.assertEqual(len(self.impl.calls), 1)
        pure = common([1, 1])
        self.cuda.capturing = False
        metadata = self.builder.build(0, pure)
        self.impl.calls.clear()
        self.impl.forward(**self.inputs(pure), attn_metadata=metadata)
        self.assertEqual(len(self.impl.calls), 1)

    def test_shared_plan_holds_suffix_and_records_each_consumer_once(self):
        cm = common([1, 7])
        metadata = self.builder.build(0, cm)
        plan = getattr(metadata, candidate._PLAN)
        suffix_ref = weakref.ref(plan.prefill.query_start_loc)
        producer, consumer = self.cuda.stream, Stream()
        self.cuda.stream = consumer
        recorded = []
        data = self.inputs(cm)
        with mock.patch.object(torch.Tensor, "record_stream", lambda tensor, stream: recorded.append((tensor, stream))):
            for _ in range(42):
                self.impl.forward(**data, attn_metadata=metadata)
            self.assertEqual(consumer.waits, [producer])
            self.assertEqual(len(recorded), 1)
            self.assertIs(recorded[0][0], suffix_ref())
            self.assertIs(recorded[0][1], consumer)
            self.assertEqual(len(self.builder.calls), 1)
            second = Stream()
            self.cuda.stream = second
            self.impl.forward(**data, attn_metadata=metadata)
            self.assertEqual(second.waits, [producer])
            self.assertEqual(len(recorded), 2)
        del plan
        gc.collect()
        self.assertIsNotNone(suffix_ref())
        self.assertIs(suffix_ref(), getattr(metadata, candidate._PLAN).prefill.query_start_loc)

    def test_fast_build_and_installer_idempotence(self):
        cm = common([1, 7])
        metadata = self.builder.build(0, cm, fast_build=True)
        self.assertFalse(hasattr(metadata, candidate._PLAN))
        self.assertEqual(self.builder.calls[0], (0, cm, True))
        build, forward = self.backend.TritonAttentionMetadataBuilder.build, self.backend.TritonAttentionImpl.forward
        candidate._wrap_backend(self.backend, self.api)
        self.assertIs(build, self.backend.TritonAttentionMetadataBuilder.build)
        self.assertIs(forward, self.backend.TritonAttentionImpl.forward)

    def test_uninstalled_runtime_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "installed audited w2s1"):
            candidate._require_fast_runtime(NS(kernel_unified_attention=object()))

    def test_source_drift_rejected_before_either_method_mutates(self):
        backend, _ = backend_and_config()
        backend.__file__ = __file__
        before = (backend.TritonAttentionMetadataBuilder.build, backend.TritonAttentionImpl.forward)
        with mock.patch.object(candidate.importlib, "import_module", return_value=backend):
            with self.assertRaisesRegex(RuntimeError, "unaudited mixed-decode dependency"):
                candidate.install()
        self.assertEqual(before, (backend.TritonAttentionMetadataBuilder.build,
                                  backend.TritonAttentionImpl.forward))


if __name__ == "__main__":
    unittest.main()
