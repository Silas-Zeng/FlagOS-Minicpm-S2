"""CPU list/address/branch proofs; no torch, Triton, CUDA or vLLM imports.

The recorder executes the intended integer copy formula, not GPU code.
Actual compiler, stream and correctness gates remain required.
"""

import ast
import importlib.util
from numbers import Integral
from pathlib import Path
from types import SimpleNamespace as NS
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "patches/framework/biv150_async_token_update.py"
TRANSFORM = ROOT / "patches/framework/biv150_async_token_update_source.py"
SPEC = importlib.util.spec_from_file_location("async_token_transform", TRANSFORM)
transform = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(transform)


class Tensor:
    next_pointer = 1000

    def __init__(self, values, shape, dtype="int32", stride=1, storage=None):
        self.values, self.shape, self.dtype = list(values), shape, dtype
        self.ndim, self.device, self.step = len(shape), "cuda", stride
        self.device = NS(type="cuda")
        self.records = []
        Tensor.next_pointer += 1024
        self.pointer = storage if storage is not None else Tensor.next_pointer

    def stride(self, dim):
        return self.step

    def untyped_storage(self):
        return NS(data_ptr=lambda: self.pointer)

    def record_stream(self, stream):
        self.records.append(stream)


class KernelRecorder:
    def __init__(self):
        self.calls = []

    def __getitem__(self, grid):
        def launch(src, dst, prev, target, n, src_rows, dst_rows, src_stride, dst_stride, **meta):
            self.calls.append((grid, n, src_rows, dst_rows, src_stride, dst_stride, meta))
            # Snapshot equals the original gather's read-before-scatter behavior.
            snapshot = list(src.values)
            for i in range(n):
                old, new = prev.values[i], target.values[i]
                if 0 <= old < src_rows and 0 <= new < dst_rows:
                    dst.values[new * dst_stride] = snapshot[old * src_stride]
        return launch


def load_runtime_functions():
    stream = object()
    cuda = NS(is_current_stream_capturing=lambda: False, current_stream=lambda device=None: stream)
    api = NS(Tensor=Tensor, int32="int32", int64="int64", bfloat16="bfloat16", cuda=cuda)
    kernel = KernelRecorder()
    ns = dict(Integral=Integral, Path=Path, torch=api,
              current_platform=NS(vendor_name="iluvatar"),
              triton=NS(cdiv=lambda a, b: (a + b - 1) // b),
              _gather_scatter_i32=kernel, selected_launches=1)
    tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name != "_gather_scatter_i32":
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(RUNTIME), "exec"), ns)
    config = NS(model_config=NS(model="/workspace/MiniCPM5-2B", dtype="bfloat16",
                               hf_text_config=NS(hidden_size=2048, num_hidden_layers=42,
                                                 num_attention_heads=16, num_key_value_heads=2),
                               is_encoder_decoder=False),
                parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
                                   decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False),
                speculative_config=None, lora_config=None)
    runner = NS(vllm_config=config, use_async_scheduling=True, use_async_spec_decode=False,
                num_spec_tokens=0, prev_num_spec_tokens=0, enable_prompt_embeds=False,
                use_aux_hidden_state_outputs=False, _draft_token_ids=None, uses_mrope=False, uses_xdrope_dim=0)
    return ns, runner, kernel, stream


class AsyncTokenUpdateTests(unittest.TestCase):
    def setUp(self):
        self.ns, self.runner, self.kernel, self.stream = load_runtime_functions()

    def invoke(self, previous, destinations, src_values=None, total=8, src_stride=1, dst_stride=1):
        source_values = list(src_values if src_values is not None else [100, 101, 102, 103])
        src = Tensor(source_values, (len(source_values) // src_stride, 1), stride=src_stride)
        dst = Tensor([-99] * (total * dst_stride), (total,), stride=dst_stride)
        prev, target = Tensor(previous, (len(previous),), "int64"), Tensor(destinations, (len(destinations),), "int64")
        # All four actual CUDA tensors are on the same device.
        for value in (dst, prev, target):
            value.device = src.device
        selected = self.ns["fused_sampled_token_update"](self.runner, src, dst, prev, target,
                                                       previous, destinations, total)
        return selected, src, dst, prev, target

    def test_reorder_removal_new_prefill_holes_and_duplicate_reads(self):
        for previous, destinations in (([2, 0, 3], [0, 1, 2]), ([0, 3], [0, 1]),
                                       ([3, 1], [2, 7]), ([1, 1, 2], [0, 2, 5])):
            with self.subTest(previous=previous, destinations=destinations):
                selected, src, dst, prev, target = self.invoke(previous, destinations)
                self.assertTrue(selected)
                expected = [-99] * 8
                for old, new in zip(previous, destinations):
                    expected[new] = src.values[old]
                self.assertEqual(dst.values, expected)
                for value in (src, dst, prev, target):
                    self.assertEqual(value.records, [self.stream])

    def test_runtime_strides_and_integer_extremes(self):
        values = [-(2**31), 999, 2**31 - 1, 999]
        selected, _, dst, _, _ = self.invoke([1, 0], [0, 2], values, src_stride=2, dst_stride=2)
        self.assertTrue(selected)
        self.assertEqual(dst.values[0], 2**31 - 1)
        self.assertEqual(dst.values[4], -(2**31))
        self.assertTrue(all(x == -99 for i, x in enumerate(dst.values) if i not in (0, 4)))

    def test_bounds_empty_and_duplicate_destinations_fall_back(self):
        for previous, destinations in (([], []), ([-1], [0]), ([4], [0]),
                                       ([0], [-1]), ([0], [8]), ([0, 1], [2, 2]), ([0], [1, 2])):
            with self.subTest(previous=previous, destinations=destinations):
                self.assertFalse(self.invoke(previous, destinations)[0])
        self.assertEqual(self.kernel.calls, [])

    def test_dtype_device_alias_and_configuration_fall_back(self):
        selected, src, dst, prev, target = self.invoke([0], [0])
        check = self.ns["_tensor_contract"]
        src.dtype = "int64"
        self.assertFalse(check(src, dst, prev, target, 1, 8))
        src.dtype = "int32"
        dst.pointer = src.pointer
        self.assertFalse(check(src, dst, prev, target, 1, 8))
        self.runner.enable_prompt_embeds = True
        self.assertFalse(self.invoke([0], [0])[0])
        self.runner.enable_prompt_embeds = False
        self.runner.vllm_config.speculative_config = object()
        self.assertFalse(self.invoke([0], [0])[0])

    def test_kernel_active_dimensions_are_not_constexpr(self):
        tree = ast.parse(RUNTIME.read_text(encoding="utf-8"))
        kernel = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_gather_scatter_i32")
        decorator = kernel.decorator_list[0]
        dns = ast.literal_eval(next(k.value for k in decorator.keywords if k.arg == "do_not_specialize"))
        self.assertEqual(set(dns), {"n", "src_rows", "dst_rows", "src_stride", "dst_stride"})
        self.assertEqual([a.arg for a in kernel.args.args if a.annotation], ["BLOCK"])

    def test_transform_changes_only_import_and_terminal_pair(self):
        source = (ROOT / "tmp/remote-source/model_runner.py").read_bytes()
        changed = transform.transform_source(source)
        ast.parse(changed)
        restored = changed.replace(transform.REPLACEMENT, transform.ORIGINAL, 1).replace(
            b"from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n", b"", 1)
        self.assertEqual(source, restored)
        for bad in (source + b"\n", changed):
            with self.assertRaises(RuntimeError):
                transform.transform_source(bad)
        # Existing no-common/unchanged early returns and both original H2Ds
        # are byte-identical and precede the sole newly inserted conditional.
        before, _ = source.split(transform.ORIGINAL)
        new_before, _ = changed.split(transform.REPLACEMENT)
        self.assertEqual(before, new_before.replace(
            b"from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n", b"", 1))


if __name__ == "__main__":
    unittest.main()
