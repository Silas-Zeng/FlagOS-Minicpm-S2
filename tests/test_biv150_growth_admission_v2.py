"""One CPU contract for actual V2 placeholder methods and narrow scope."""

import ast
import hashlib
import importlib.util
from pathlib import Path
import unittest

from tests import test_biv150_growth_admission as fixtures


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "analysis/source/growth-admission"
sp = importlib.util.spec_from_file_location("growth_v2", ROOT / "patches/framework/biv150_growth_admission_v2.py")
growth = importlib.util.module_from_spec(sp)
sp.loader.exec_module(growth)


def actual_placeholder_classes():
    nodes = []
    for filename, name in (("scheduler.py", "Scheduler"), ("async_scheduler.py", "AsyncScheduler")):
        cls = next(n for n in ast.parse((SOURCE / filename).read_text(encoding="utf-8")).body
                   if isinstance(n, ast.ClassDef) and n.name == name)
        cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_update_after_schedule"]
        if name == "Scheduler":
            cls.bases = []
        nodes.append(cls)
    module = ast.Module(body=[ast.ImportFrom(module="__future__",
        names=[ast.alias(name="annotations")], level=0), *nodes], type_ignores=[])
    namespace = {}
    exec(compile(ast.fix_missing_locations(module), "actual-v2-placeholder-contract", "exec"), namespace)
    return namespace["Scheduler"], namespace["AsyncScheduler"]


class V2Contract(unittest.TestCase):
    def test_actual_v2_placeholders_budget_and_source_scope(self):
        for name, expected in growth.EXPECTED_SOURCES.items():
            self.assertEqual(hashlib.sha256((SOURCE / (name.rsplit(".", 1)[-1] + ".py")).read_bytes()).hexdigest(), expected)
        Base, Async = actual_placeholder_classes()
        template, candidate, kwargs, _ = fixtures.fixture()
        scheduler = Async()
        scheduler.__dict__.update(vars(template))
        scheduler.use_v2_model_runner = True
        scheduler.defer_block_free = False
        scheduler.current_step, scheduler.pp_size = 1, 1
        scheduler.num_sampled_tokens_per_step = 1
        scheduler.enable_return_routed_experts = False
        scheduler._inflight_prefills, scheduler.finished_req_ids = set(), set()
        request = type("HashableRequest", (), {})()
        request.__dict__.update(vars(scheduler.running[0]))
        request.num_computed_tokens, request.num_output_placeholders = 63, 0
        request.next_decode_eligible_step = 0
        scheduler.running, scheduler.requests = [request], {request.request_id: request}
        output = fixtures.N(num_scheduled_tokens={request.request_id: 1},
            has_structured_output_requests=False, scheduled_spec_decode_tokens={},
            num_spec_tokens_to_schedule=0, pending_structured_output_tokens=False)
        for step in (1, 2):
            scheduler.current_step = step
            self.assertGreaterEqual(step, request.next_decode_eligible_step)
            scheduler._update_after_schedule(output)  # exact actual base + Async bodies
            self.assertEqual(request.num_output_placeholders, step)
            self.assertEqual(request.num_computed_tokens, 63 + step)
            self.assertEqual(request.next_decode_eligible_step, step + 1)
            self.assertEqual(request.spec_token_ids, [])
            self.assertEqual(growth._future_tokens(request, 131072), 96)
        classes = (fixtures.FullSpec, fixtures.Coordinator, fixtures.FullManager, (Base, Async))
        self.assertTrue(growth._eligible(scheduler, *classes))
        self.assertEqual(growth._growth_demand(scheduler, candidate, kwargs, "RUNNING"), (9, 8))
        scheduler.defer_block_free = True
        self.assertFalse(growth._eligible(scheduler, *classes))
        scheduler.defer_block_free = False
        scheduler.__class__ = type("UnauditedAsync", (Async,), {})
        self.assertFalse(growth._eligible(scheduler, *classes))
        self.assertFalse(growth.install()["installed"])


if __name__ == "__main__":
    unittest.main()
