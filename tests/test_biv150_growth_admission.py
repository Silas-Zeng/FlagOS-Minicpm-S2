"""Small CPU contracts using the actual downloaded allocation predictors.

No torch/vLLM import, device, new scheduler simulator or rewritten predictor.
"""

import ast
from collections import defaultdict
import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace as N
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/source/growth-admission"
spec = importlib.util.spec_from_file_location(
    "growth_candidate", ROOT / "patches/framework/biv150_growth_admission.py")
growth = importlib.util.module_from_spec(spec)
spec.loader.exec_module(growth)


def actual_methods(filename, cls_name, names, globals_):
    tree = ast.parse((SOURCE / filename).read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls_name)
    cls.bases, cls.keywords, cls.decorator_list = [], [], []
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    module = ast.Module(body=[ast.ImportFrom(
        module="__future__", names=[ast.alias(name="annotations")], level=0), cls],
        type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(SOURCE / filename), "exec"), globals_)
    return globals_[cls_name]


ActualSizing = actual_methods("single_type_kv_cache_manager.py", "SingleTypeKVCacheManager",
    {"get_num_blocks_to_allocate", "_get_num_evictable_blocks"},
    {"cdiv": lambda a, b: (a + b - 1) // b})
ActualCoord = actual_methods("kv_cache_coordinator.py", "KVCacheCoordinator",
    {"get_num_blocks_to_allocate"}, {"CrossAttentionManager": type("Cross", (), {})})


class FullManager(ActualSizing):
    def get_num_skipped_tokens(self, total):
        return 0


class Coordinator(ActualCoord):
    pass


class FullSpec:
    pass


def request(name, status="RUNNING", *, maximum=32):
    return N(request_id=name, status=status, num_prompt_tokens=64, max_tokens=maximum,
             num_tokens=64, num_computed_tokens=64 if status == "RUNNING" else 0,
             num_output_placeholders=0, resumable=False, use_structured_output=False,
             has_encoder_inputs=False, mm_features=[], pooling_params=None)


def fixture():
    manager = N(watermark_blocks=0, max_model_len=131072,
                empty_kv_cache_blocks=N(blocks=((),)))
    sizing = FullManager()
    sizing.block_size, sizing._max_admission_blocks_per_request = 16, None
    sizing.req_to_blocks = defaultdict(list)
    sizing.num_cached_block = {}
    a, b, c = request("a"), request("b"), request("c", "WAITING")
    for active in (a, b):
        sizing.req_to_blocks[active.request_id] = [N(ref_cnt=1, is_null=False) for _ in range(4)]
        sizing.num_cached_block[active.request_id] = 0
    coordinator = Coordinator()
    coordinator.single_type_managers = (sizing,)
    manager.coordinator = coordinator
    pool = N(num_gpu_blocks=18, free=9)
    pool.get_num_free_blocks = lambda: pool.free
    manager.block_pool = pool
    full = FullSpec()
    for key, value in dict(block_size=16, num_kv_heads=2, head_size=128, head_size_v=128,
                           dtype="torch.bfloat16", sliding_window=None,
                           attention_chunk_size=None, non_causal=False).items():
        setattr(full, key, value)
    manager.kv_cache_config = N(kv_cache_groups=[N(kv_cache_spec=full, layer_names=list(range(42)))])
    config = N(model_config=N(model="/workspace/MiniCPM5-2B", dtype="torch.bfloat16",
        hf_text_config=N(hidden_size=2048, num_hidden_layers=42,
                         num_attention_heads=16, num_key_value_heads=2)),
        parallel_config=N(tensor_parallel_size=1, pipeline_parallel_size=1,
            data_parallel_size=1, decode_context_parallel_size=1,
            prefill_context_parallel_size=1, use_ubatching=False),
        speculative_config=None, lora_config=None, cache_config=N(kv_sharing_fast_prefill=False))
    scheduler = N(kv_cache_manager=manager, running=[a, b], max_model_len=131072,
        block_size=16, vllm_config=config, is_encoder_decoder=False, has_mamba_layers=False,
        use_v2_model_runner=False, connector=None, ec_connector=None,
        scheduler_reserve_full_isl=True, num_lookahead_tokens=0, policy=N(value="fcfs"))
    kwargs = dict(full_sequence_must_fit=True, num_new_computed_tokens=0,
                  new_computed_blocks=None, has_scheduled_reqs=True)
    return scheduler, c, kwargs, sizing


class GrowthContracts(unittest.TestCase):
    def test_exact_general_hook_and_repeated_install(self):
        hook_spec = importlib.util.spec_from_file_location("growth_source_transformer",
            ROOT / "patches/framework/biv150_growth_admission_source.py")
        hook = importlib.util.module_from_spec(hook_spec)
        hook_spec.loader.exec_module(hook)
        original = (ROOT / "experiments/accuracy/20261021T090505Z-sql-mixed-level3"
                    "/source/plugin/vllm_fl/__init__.py").read_bytes()
        changed = hook.transform_source(original)
        self.assertTrue(changed.startswith(original))
        compile(changed, "isolated_candidate/__init__.py", "exec")
        register = next(n for n in ast.parse(changed).body
                        if isinstance(n, ast.FunctionDef) and n.name == "register_model")
        self.assertIsInstance(register.body[-1], ast.Expr)
        self.assertEqual(register.body[-1].value.func.id, "_install_growth_admission")
        with self.assertRaisesRegex(RuntimeError, "unaudited"):
            hook.transform_source(changed)

        modules = {name: N(__name__=name, __file__=str(SOURCE / (name.rsplit('.', 1)[-1] + '.py')))
                   for name in growth.EXPECTED_SOURCES}
        manager_name = "vllm.v1.core.kv_cache_manager"
        scheduler_name = "vllm.v1.core.sched.scheduler"
        manager_cls = actual_methods("kv_cache_manager.py", "KVCacheManager",
            {"allocate_slots"}, {"__name__": manager_name})
        scheduler_cls = actual_methods("scheduler.py", "Scheduler", {"schedule"},
            {"__name__": scheduler_name, "KVCacheManager": manager_cls})
        modules[manager_name].KVCacheManager = manager_cls
        modules[scheduler_name].Scheduler = scheduler_cls
        modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator = Coordinator
        modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager = FullManager
        modules.update({"vllm.platforms": N(current_platform=N(vendor_name="iluvatar")),
                        "vllm.v1.request": N(RequestStatus=N(
                            WAITING="WAITING", PREEMPTED="PREEMPTED", RUNNING="RUNNING")),
                        "vllm.v1.kv_cache_interface": N(FullAttentionSpec=FullSpec)})
        with patch.object(growth.importlib, "import_module", side_effect=modules.__getitem__):
            self.assertTrue(growth.install(enabled=True)["installed"])
            first = scheduler_cls.schedule
            self.assertTrue(growth.install(enabled=True)["already_installed"])
            self.assertIs(scheduler_cls.schedule, first)

    def test_source_identity_and_default_off(self):
        for name, expected in growth.EXPECTED_SOURCES.items():
            filename = name.rsplit(".", 1)[-1] + ".py"
            self.assertEqual(hashlib.sha256((SOURCE / filename).read_bytes()).hexdigest(), expected)
        self.assertEqual(growth.install(), {"installed": False, "reason": "disabled by default"})

    def test_exact_boundary_includes_future_outputs_and_existing_pages(self):
        scheduler, candidate, kwargs, sizing = fixture()
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"), (9, 10))
        calls = []
        wrapped = growth._wrap_allocate(lambda *a, **k: calls.append((a, k)) or "original",
                                         ("WAITING", "PREEMPTED"), "RUNNING")
        token = growth._SCHEDULER.set(scheduler)
        try:
            self.assertIsNone(wrapped(scheduler.kv_cache_manager, candidate, 16, **kwargs))
            self.assertEqual(calls, [])
            scheduler.kv_cache_manager.block_pool.free = 10
            scheduler.kv_cache_manager.block_pool.num_gpu_blocks = 19
            self.assertEqual(wrapped(scheduler.kv_cache_manager, candidate, 16, **kwargs), "original")
        finally:
            growth._SCHEDULER.reset(token)
        self.assertEqual(len(sizing.req_to_blocks), 2)  # read-only predictor did not add c
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], kwargs)

    def test_free_prefix_touch_and_live_shared_prefix(self):
        scheduler, candidate, kwargs, sizing = fixture()
        scheduler.running = scheduler.running[:1]
        sizing.req_to_blocks["a"] += [N(ref_cnt=1, is_null=False) for _ in range(2)]
        prefix = [N(ref_cnt=0, is_null=False) for _ in range(4)]
        kwargs.update(new_computed_blocks=N(blocks=(prefix,)), num_new_computed_tokens=64)
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING")[1], 6)
        self.assertTrue(all(x.ref_cnt == 0 for x in prefix))  # no touch/mutation in gate
        for block in prefix:
            block.ref_cnt = 1
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING")[1], 2)

    def test_finish_cancel_id_reuse_and_preallocated_pages(self):
        scheduler, candidate, kwargs, sizing = fixture()
        scheduler.running.pop()
        scheduler.kv_cache_manager.block_pool.free += 4
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"), (13, 8))
        candidate.request_id = "b"  # same ID as removed request, only live actual pages matter
        sizing.req_to_blocks.pop("b")
        sizing.num_cached_block.pop("b")
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"), (13, 8))
        sizing.req_to_blocks["b"] = [N(ref_cnt=1, is_null=False) for _ in range(4)]
        sizing.num_cached_block["b"] = 0
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING")[1], 4)

    def test_unsupported_empty_oversized_and_running_pass_through(self):
        scheduler, candidate, kwargs, _ = fixture()
        self.assertTrue(growth._eligible(scheduler, FullSpec, Coordinator, FullManager))
        candidate.resumable = True
        self.assertIsNone(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"))
        candidate.resumable = False
        candidate.max_tokens = 32768
        self.assertIsNone(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"))
        scheduler.running.clear()
        self.assertIsNone(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"))
        scheduler.connector = object()
        self.assertFalse(growth._eligible(scheduler, FullSpec, Coordinator, FullManager))
        wrapped = growth._wrap_allocate(lambda *a, **k: "original", ("WAITING",), "RUNNING")
        token = growth._SCHEDULER.set(scheduler)
        try:
            candidate.status = "RUNNING"
            self.assertEqual(wrapped(scheduler.kv_cache_manager, candidate, 1, **kwargs), "original")
        finally:
            growth._SCHEDULER.reset(token)

    def test_async_extent_model_cap_and_scope_finally(self):
        scheduler, candidate, _, _ = fixture()
        candidate.num_computed_tokens = 98
        candidate.num_output_placeholders = 35
        self.assertEqual(growth._future_tokens(candidate, scheduler.max_model_len), 99)
        self.assertEqual(growth._future_tokens(candidate, 98), 98)
        def fail(scheduler):
            self.assertIs(growth._SCHEDULER.get(), scheduler)
            raise RuntimeError("deliberate original failure")
        wrapped = growth._wrap_schedule(fail, FullSpec, Coordinator, FullManager)
        with self.assertRaisesRegex(RuntimeError, "deliberate original failure"):
            wrapped(scheduler)
        self.assertIsNone(growth._SCHEDULER.get())


if __name__ == "__main__":
    unittest.main()
