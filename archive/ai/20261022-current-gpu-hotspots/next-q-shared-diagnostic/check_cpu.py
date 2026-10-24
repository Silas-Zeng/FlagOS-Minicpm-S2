"""一次必要静态检查；不导入 Torch/Triton/vLLM，不执行设备代码。"""
import ast
import contextlib
import hashlib
import io
import json
from pathlib import Path
import runpy
import sys
import time

start = time.perf_counter()
here = Path(__file__).resolve().parent
root = here.parents[1]
old = root / "tmp/next-prefill-v-late/validate_prefill_v_late.py"
saved = root / "experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/source"
checks = {}
texts = {name: (here / name).read_text(encoding="utf-8") for name in ("worker.py", "fixture.py", "diagnose_q_shared.py")}
trees = {name: ast.parse(text) for name, text in texts.items()}
checks["syntax"] = True
get_fn = lambda tree, name: next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name)
dump = lambda node: ast.dump(node, include_attributes=False)
old_tree = ast.parse(old.read_text())
new_main = get_fn(trees["diagnose_q_shared.py"], "main")
old_main = get_fn(old_tree, "main")
old_try = next(node for node in old_main.body if isinstance(node, ast.Try))
new_try = next(node for node in new_main.body if isinstance(node, ast.Try))
checks["owner_finally_ast_identical"] = [dump(node) for node in old_try.finalbody] == [dump(node) for node in new_try.finalbody]
checks["old_timeout_300_preserved"] = 'status = child.wait(timeout=300)' in texts["diagnose_q_shared.py"]
checks["old_group_owner_preserved"] = 'start_new_session=True' in texts["diagnose_q_shared.py"] and 'fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)' in texts["diagnose_q_shared.py"]
checks["fixture_make_data_ast_identical"] = dump(get_fn(trees["fixture.py"], "make_data")) == dump(get_fn(ast.parse((saved / "validate_mixed_decode.py").read_text()), "make_data"))
checks["fixture_pages_ast_identical"] = dump(get_fn(trees["fixture.py"], "prepare_pages")) == dump(get_fn(old_tree, "prepare_pages"))
checks["no_candidate_import_or_install"] = all(word not in texts["worker.py"] for word in ("policy.py", "manager.", "cache_experiment", "generated_attention"))
checks["one_KV_write_before_profile"] = texts["worker.py"].count("impl.do_kv_cache_update(") == 1 and texts["worker.py"].index("impl.do_kv_cache_update(") < texts["worker.py"].index("torch.cuda.profiler.start()")
start_at = texts["worker.py"].index("torch.cuda.profiler.start()")
stop_at = texts["worker.py"].index("torch.cuda.profiler.stop()")
window = texts["worker.py"][start_at:stop_at]
checks["window_only_forward_and_end_sync"] = 'for _ in range(LOOPS):\n            impl.forward(layer, q, k, v, cache, metadata, output)\n        torch.cuda.synchronize()' in window and "do_kv_cache_update" not in window
checks["fixed_ixsys_metrics_command"] = all(part in texts["diagnose_q_shared.py"] for part in ('/usr/local/corex-4.5.0/bin/ixsys', '"--profile-from-start", "off"', '"--gpu-metrics-device", "0"', '"--gpu-metrics-set", "3"', '"--gpu-metrics-frequency", "500"'))
pins = json.loads((here / "asset-pins.json").read_text())
checks["worker_fixture_pins"] = all(hashlib.sha256((here / name).read_bytes()).hexdigest() == value for name, value in pins.items())
sys.path.insert(0, str(saved))
original_argv = sys.argv[:]
for name in ("worker.py", "diagnose_q_shared.py"):
    sys.argv = [str(here / name), "--help"]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            runpy.run_path(str(here / name), run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
sys.argv = original_argv
checks["help_no_accelerator_import"] = not any(name in sys.modules for name in ("torch", "triton", "vllm"))
receipt = {"checks": checks, "passed": all(checks.values()), "elapsed_seconds": time.perf_counter() - start,
           "sha256": {name: hashlib.sha256((here / name).read_bytes()).hexdigest() for name in texts},
           "scope": "CPU static checks only; no candidate/math comparison, no GPU or network"}
(here / "cpu-check.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
print(json.dumps(receipt))
assert receipt["passed"]
