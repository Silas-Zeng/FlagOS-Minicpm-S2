"""CPU-only proof of index identity, alias lifetime, scope and source surgery."""

import ast
from copy import deepcopy
import hashlib
import importlib.util
from itertools import product
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import torch


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "hidden_view_transform", ROOT / "patches/framework/biv150_decode_hidden_view.py")
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)


def make_runner():
    def compute_logits(self, value):
        # Deterministic read-only stand-in; installed implementation is a
        # separate source/GPU gate, not proved by this CPU method.
        return value[:, :17].clone()
    compute_logits.__module__ = "vllm.model_executor.models.llama"
    model_cls = type("LlamaForCausalLM", (), {
        "__module__": "vllm.model_executor.models.llama",
        "compute_logits": compute_logits,
    })
    processor_cls = type("LogitsProcessor", (), {
        "__module__": "vllm.model_executor.layers.logits_processor",
        "logits_as_input": False,
    })
    quant_cls = type("UnquantizedEmbeddingMethod", (), {
        "__module__": "vllm.model_executor.layers.vocab_parallel_embedding",
    })
    loaded = model_cls()
    loaded.logits_processor = processor_cls()
    loaded.lm_head = NS(quant_method=quant_cls())
    return NS(
        model=loaded, device=torch.device("cpu"),
        model_config=NS(model="/workspace/MiniCPM5-2B", dtype=torch.bfloat16,
            runner_type="generate", quantization=None, is_encoder_decoder=False,
            hf_text_config=NS(model_type="llama", hidden_size=2048,
                num_hidden_layers=42, num_attention_heads=16,
                num_key_value_heads=2, intermediate_size=6144, vocab_size=130560)),
        parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
            decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False),
        speculative_config=None, lora_config=None,
        vllm_config=NS(quant_config=None, kv_transfer_config=None, ec_transfer_config=None),
        cache_config=NS(kv_sharing_fast_prefill=False),
        kv_sharing_fast_prefill_eligible_layers=set(), use_aux_hidden_state_outputs=False,
        is_pooling_model=False, broadcast_pp_output=False, enable_prompt_embeds=False,
        supports_mm_inputs=False, num_prompt_logprobs={},
    )


def eligible(runner, hidden, indices, n, **changes):
    args = dict(max_num_scheduled_tokens=1, num_tokens_unpadded=n, num_reqs=n,
        spec_decode_metadata=None, aux_hidden_states=None, should_ubatch=False,
        ubatch_slices=None, ubatch_slices_padded=None, torch_module=torch)
    args.update(changes)
    return candidate._biv150_decode_hidden_view_eligible(runner, hidden, indices, **args)


class HiddenViewCPUProof(unittest.TestCase):
    def test_counts_prove_exact_identity_including_zero_rows(self):
        for n in range(1, 7):
            for lengths in product(range(4), repeat=n):
                pure = max(lengths) == 1 and sum(lengths) == n
                self.assertEqual(pure, all(value == 1 for value in lengths))
                if pure:
                    ends, total = [], 0
                    for value in lengths:
                        total += value
                        ends.append(total - 1)
                    self.assertEqual(ends, list(range(n)))

    def test_dynamic_active_sizes_preserve_values_layout_logits_and_rng(self):
        runner = make_runner()
        for n in (1, 7, 29, 60, 61, 62, 64, 65):
            padded = ((n + 7) // 8) * 8
            hidden = (torch.arange(padded * 2048).reshape(padded, 2048) % 97).to(torch.bfloat16)
            before = hidden.clone()
            for dtype in (torch.int32, torch.int64):
                indices = torch.arange(n, dtype=dtype)
                self.assertTrue(eligible(runner, hidden, indices, n))
                rng_before = torch.get_rng_state().clone()
                view, gathered = hidden[:n], hidden[indices]
                self.assertTrue(torch.equal(torch.get_rng_state(), rng_before))
                self.assertTrue(torch.equal(view, gathered))
                self.assertEqual(view.shape, gathered.shape)
                self.assertEqual(view.stride(), gathered.stride())
                self.assertEqual(view.untyped_storage().data_ptr(), hidden.untyped_storage().data_ptr())
                self.assertNotEqual(gathered.untyped_storage().data_ptr(), hidden.untyped_storage().data_ptr())
                a, b = runner.model.compute_logits(view), runner.model.compute_logits(gathered)
                self.assertTrue(torch.equal(a, b))
                self.assertTrue(torch.equal(hidden, before))
                g1, g2 = torch.Generator().manual_seed(79), torch.Generator().manual_seed(79)
                s1 = torch.multinomial(a.float().softmax(-1), 1, generator=g1)
                s2 = torch.multinomial(b.float().softmax(-1), 1, generator=g2)
                self.assertTrue(torch.equal(s1, s2))
                self.assertTrue(torch.equal(g1.get_state(), g2.get_state()))

    def test_view_owns_storage_but_is_not_a_snapshot(self):
        hidden = torch.arange(4 * 2048).reshape(4, 2048).to(torch.bfloat16)
        view, copied = hidden[:3], hidden[torch.arange(3)]
        hidden[0, 0] = -7
        self.assertEqual(view[0, 0].item(), -7)
        self.assertNotEqual(copied[0, 0].item(), -7)
        del hidden
        self.assertEqual(view[0, 0].item(), -7)
        # This explicit hazard is why read-only logits and no overlapping
        # producer overwrite are required; owning storage alone is not enough.

    def test_unsupported_configuration_falls_back(self):
        hidden = torch.zeros((8, 2048), dtype=torch.bfloat16)
        indices = torch.arange(7)
        exclusions = [
            ("model_config.model", "other-model"), ("model_config.dtype", torch.float16),
            ("model_config.runner_type", "pooling"), ("model_config.quantization", "x"),
            ("model_config.is_encoder_decoder", True),
            ("model_config.hf_text_config.num_hidden_layers", 41),
            ("parallel_config.tensor_parallel_size", 2),
            ("parallel_config.pipeline_parallel_size", 2),
            ("parallel_config.decode_context_parallel_size", 2),
            ("parallel_config.data_parallel_size", 2),
            ("parallel_config.use_ubatching", True), ("speculative_config", object()),
            ("lora_config", object()), ("vllm_config.quant_config", object()),
            ("vllm_config.kv_transfer_config", object()),
            ("vllm_config.ec_transfer_config", object()),
            ("cache_config.kv_sharing_fast_prefill", True),
            ("kv_sharing_fast_prefill_eligible_layers", {"x"}),
            ("use_aux_hidden_state_outputs", True), ("is_pooling_model", True),
            ("broadcast_pp_output", True), ("enable_prompt_embeds", True),
            ("supports_mm_inputs", True), ("num_prompt_logprobs", {"x": 1}),
            ("model.logits_processor.logits_as_input", True),
        ]
        for path, value in exclusions:
            runner = make_runner()
            target = runner
            fields = path.split(".")
            for field in fields[:-1]:
                target = getattr(target, field)
            setattr(target, fields[-1], value)
            self.assertFalse(eligible(runner, hidden, indices, 7), path)
        runner = make_runner()
        del runner.parallel_config.use_ubatching
        self.assertFalse(eligible(runner, hidden, indices, 7))

    def test_unsupported_dynamic_metadata_falls_back(self):
        runner = make_runner()
        hidden, indices = torch.zeros((8, 2048), dtype=torch.bfloat16), torch.arange(7)
        for changes in [dict(max_num_scheduled_tokens=2), dict(num_tokens_unpadded=8),
                dict(num_reqs=0), dict(max_num_scheduled_tokens=True),
                dict(spec_decode_metadata=object()), dict(aux_hidden_states=[]),
                dict(should_ubatch=True), dict(ubatch_slices=[]), dict(ubatch_slices_padded=[])]:
            self.assertFalse(eligible(runner, hidden, indices, 7, **changes))
        for bad in [hidden.float(), hidden[:, ::2], hidden[1:], hidden[:6], hidden.unsqueeze(0)]:
            self.assertFalse(eligible(runner, bad, indices, 7))
        for bad in [indices.float(), indices[:6], indices.unsqueeze(0)]:
            self.assertFalse(eligible(runner, hidden, bad, 7))

    def test_transform_rejects_drift_and_non_bytes(self):
        with self.assertRaises(TypeError):
            candidate.transform_source("source")
        with self.assertRaisesRegex(RuntimeError, "unaudited runner source"):
            candidate.transform_source(b"source")

    def test_actual_retained_transform_only_changes_common_selection(self):
        path = ROOT / "tmp/remote-source/model_runner.py"
        if not path.is_file():
            self.skipTest("exact retained runner is a local audit input, not a test fixture")
        original = path.read_bytes()
        changed = candidate.transform_source(original)
        compile(changed, "hidden-view-candidate", "exec")
        self.assertEqual(changed.count(candidate.MARKER.encode()), 1)
        self.assertIn(candidate._BROADCAST.encode(), changed)
        before, after = ast.parse(original), ast.parse(changed)
        after.body = [node for node in after.body if not (
            isinstance(node, ast.FunctionDef) and node.name == "_biv150_decode_hidden_view_eligible")]
        replacements = 0
        class Restore(ast.NodeTransformer):
            def visit_If(self, node):
                nonlocal replacements
                if (isinstance(node.test, ast.Call) and isinstance(node.test.func, ast.Name)
                        and node.test.func.id == "_biv150_decode_hidden_view_eligible"):
                    replacements += 1
                    return node.orelse[0]
                return self.generic_visit(node)
        after = Restore().visit(after)
        self.assertEqual(replacements, 1)
        self.assertEqual(ast.dump(before), ast.dump(after))
        with self.assertRaisesRegex(RuntimeError, "unaudited runner source"):
            candidate.transform_source(changed)


if __name__ == "__main__":
    unittest.main()
