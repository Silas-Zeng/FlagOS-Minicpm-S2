"""仅修初始化顺序和 ixsys/worker 退出聚合，原 v1 资产保持不变。"""
import ast
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
old = here.parent / "next-q-shared-diagnostic"
sha = lambda raw: hashlib.sha256(raw).hexdigest()
worker_raw = (old / "worker.py").read_bytes()
controller_raw = (old / "diagnose_q_shared.py").read_bytes()
assert sha(worker_raw) == "f12c1a6c3aaf2f8c90aaf37d5eb533b9da97cb02faf4094ab23389428cd5370c"
assert sha(controller_raw) == "57dc327b64f04d6b1ebe384d4c7f118e355730eef4291cb4c9a650b54e61efe5"
worker = worker_raw.decode()
config = '''        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
                            max_model_len=131072, compilation_config=CompilationConfig(
                                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
'''
assert worker.count(config) == 1
worker = worker.replace(config, "", 1)
worker = worker.replace('        modules = {}\n', config + '        modules = {}\n', 1)
anchor = '        preinstall = (attention.kernel_unified_attention, attention.reduce_segments,\n'
identity = '''        if (backend.unified_attention is not attention.unified_attention
                or attention.unified_attention.__globals__ is not vars(attention)):
            raise RuntimeError("backend unified_attention/global identity changed after plugin configuration")
'''
assert worker.count(anchor) == 1
worker = worker.replace(anchor, identity + anchor, 1)
anchor = '        observers = (Capture(baseline[0], "attention"), Capture(baseline[1], "reducer"))\n'
identity2 = '''        result["binding_identity_before_observer"] = (
            backend.unified_attention is attention.unified_attention
            and attention.unified_attention.__globals__ is vars(attention)
            and attention.kernel_unified_attention is baseline[0]
            and attention.reduce_segments is baseline[1]
            and type(impl) is backend.TritonAttentionImpl
            and impl.forward.__func__ is baseline[3])
        if not result["binding_identity_before_observer"]:
            raise RuntimeError("baseline observer would not intercept the actual backend path")
'''
assert worker.count(anchor) == 1
worker = worker.replace(anchor, identity2 + anchor, 1)
(here / "worker.py").write_text(worker, encoding="utf-8", newline="\n")
for name in ("fixture.py", "runtime.py", "mixed.py"):
    (here / name).write_bytes((old / name).read_bytes())
pins = {name: sha((here / name).read_bytes()) for name in ("worker.py", "fixture.py")}
(here / "asset-pins.json").write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
controller = controller_raw.decode()
old_pins = json.loads((old / "asset-pins.json").read_text())
assert controller.count("ASSET_PINS = " + repr(old_pins)) == 1
controller = controller.replace("ASSET_PINS = " + repr(old_pins), "ASSET_PINS = " + repr(pins), 1)
helper = '''def completion_status(ixsys_status, result):
    """ixsys exit 0 不能替代 worker 完整完成；缺失或不完整都 fail closed。"""
    if not isinstance(result, dict):
        return 1, {"complete": False, "reason": "worker result is not an object"}
    profile, checks = result.get("profile"), result.get("checks")
    expected_checks = {"entire_kv_bits_unchanged", "rng_unchanged", "valid_output_finite",
                       "padding_untouched", "same_q_repeat_output_bits"}
    complete = (result.get("status") == "diagnostic_complete_no_performance_verdict"
        and isinstance(profile, dict)
        and profile.get("start_returned") is True and profile.get("stop_returned") is True
        and type(profile.get("completed_calls")) is int and profile["completed_calls"] == 128
        and isinstance(checks, dict) and expected_checks <= checks.keys()
        and all(value is True for value in checks.values())
        and result.get("device_settled") is True and result.get("entry_bindings_restored") is True)
    status = 0 if ixsys_status == 0 and complete else (ixsys_status if ixsys_status != 0 else 1)
    return status, {"complete": complete, "worker_status": result.get("status"),
                    "profile": profile, "checks": checks}


'''
controller = controller.replace('def main():\n', helper + 'def main():\n', 1)
old_wait = '            status = child.wait(timeout=300)\n'
new_wait = '''            ixsys_status = child.wait(timeout=300)
            manifest["ixsys_exit_code"] = ixsys_status
            status = ixsys_status if ixsys_status != 0 else 1
            worker_result = json.loads((run / "results.json").read_text(encoding="utf-8"))
            status, manifest["worker_completion"] = completion_status(ixsys_status, worker_result)
'''
assert controller.count(old_wait) == 1
controller = controller.replace(old_wait, new_wait, 1)
controller = controller.replace('    except BaseException:\n        manifest["controller_error"]',
                                '    except BaseException:\n        status = 1\n        manifest["controller_error"]', 1)
(here / "diagnose_q_shared.py").write_text(controller, encoding="utf-8", newline="\n")
ast.parse(worker)
ast.parse(controller)
print(json.dumps({**pins, "diagnose_q_shared.py": sha(controller.encode())}))
