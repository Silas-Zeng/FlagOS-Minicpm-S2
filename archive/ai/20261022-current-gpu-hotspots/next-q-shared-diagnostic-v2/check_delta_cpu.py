"""仅本次顺序/退出聚合差分；不重跑 v1 合同或导入设备运行时。"""
import ast
import copy
import hashlib
import json
from pathlib import Path
import time

start = time.perf_counter()
here = Path(__file__).resolve().parent
old = here.parent / "next-q-shared-diagnostic"
worker = (here / "worker.py").read_text(encoding="utf-8")
controller = (here / "diagnose_q_shared.py").read_text(encoding="utf-8")
tree = ast.parse(controller)
worker_tree = ast.parse(worker)
fn = lambda tree, name: next(node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name == name)
dump = lambda node: ast.dump(node, include_attributes=False)
old_worker = ast.parse((old / "worker.py").read_text(encoding="utf-8"))
old_controller = ast.parse((old / "diagnose_q_shared.py").read_text(encoding="utf-8"))
checks = {"config_before_backend_import_and_install": worker.index("config = EngineArgs(") < worker.index("modules = {}") < worker.index('result["c2_install"]'),
          "actual_binding_guards": "backend.unified_attention is not attention.unified_attention" in worker and "attention.unified_attention.__globals__ is not vars(attention)" in worker and "impl.forward.__func__ is baseline[3]" in worker,
          "empty_capture_still_rejected": 'selected != [True, False] or len(observers[1].observed) != 1' in worker,
          "capture_unchanged": dump(fn(worker_tree, "Capture")) == dump(fn(old_worker, "Capture"))}
window = lambda text: text[text.index('        observers = '):text.index('\n\ndef main():')]
checks["observer_profile_and_restore_bytes_unchanged"] = window(worker) == window((old / "worker.py").read_text(encoding="utf-8"))
old_try = next(node for node in fn(old_controller, "main").body if isinstance(node, ast.Try))
new_try = next(node for node in fn(tree, "main").body if isinstance(node, ast.Try))
checks["owner_cleanup_ast_unchanged"] = [dump(n) for n in old_try.finalbody] == [dump(n) for n in new_try.finalbody]
checks["missing_result_fails_closed"] = controller.index('status = ixsys_status if ixsys_status != 0 else 1') < controller.index('worker_result = json.loads(')
namespace = {}
exec(compile(ast.Module(body=[fn(tree, "completion_status")], type_ignores=[]), "<completion-only>", "exec"), namespace)
complete = namespace["completion_status"]
good = {"status": "diagnostic_complete_no_performance_verdict", "profile": {"start_returned": True, "stop_returned": True, "completed_calls": 128},
        "checks": dict.fromkeys(("entire_kv_bits_unchanged", "rng_unchanged", "valid_output_finite", "padding_untouched", "same_q_repeat_output_bits"), True),
        "device_settled": True, "entry_bindings_restored": True}
cases = [("complete", 0, good, 0), ("ixsys_failed", 7, good, 7), ("empty", 0, {}, 1), ("nonobject", 0, [], 1)]
for name, group, key, value in (("worker_failed", None, "status", "failed"), ("no_start", "profile", "start_returned", False),
                              ("no_stop", "profile", "stop_returned", False), ("partial", "profile", "completed_calls", 127),
                              ("bool_calls", "profile", "completed_calls", True), ("kv_changed", "checks", "entire_kv_bits_unchanged", False),
                              ("unsettled", None, "device_settled", False), ("unrestored", None, "entry_bindings_restored", False)):
    value_case = copy.deepcopy(good)
    (value_case if group is None else value_case[group])[key] = value
    cases.append((name, 0, value_case, 1))
missing = copy.deepcopy(good)
missing["checks"].pop("rng_unchanged")
cases.append(("missing_check", 0, missing, 1))
checks["completion_status_13_cases"] = all(complete(code, value)[0] == expected for _, code, value, expected in cases)
pins = json.loads((here / "asset-pins.json").read_text())
checks["new_pins"] = all(hashlib.sha256((here / name).read_bytes()).hexdigest() == value for name, value in pins.items())
result = {"passed": all(checks.values()), "checks": checks, "exit_cases": [name for name, *_ in cases],
          "elapsed_seconds": time.perf_counter() - start,
          "sha256": {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in ("worker.py", "diagnose_q_shared.py", "asset-pins.json")}}
(here / "cpu-check.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result))
assert result["passed"]
