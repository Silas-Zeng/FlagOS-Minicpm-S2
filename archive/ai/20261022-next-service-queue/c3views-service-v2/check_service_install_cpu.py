"""只核新增服务接线/首次 execute 证据；不重跑原 policy 合同，不导入 Torch。"""
import ast
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    core = (ROOT / "tmp/small-input-gates/biv150_c3_view_reuse.py").read_bytes()
    suffix = (HERE / "service_append.py").read_bytes()
    assert sha(core) == "ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4"
    combined = core + suffix
    (HERE / "biv150_c3_view_reuse.py").write_bytes(combined)
    prepare = load("prepare_c3views", HERE / "prepare_c3views_service.py")
    runtime = load("runtime_c3views", HERE / "biv150_c3_view_reuse.py")
    validator = load("validator_c3views", HERE / "check_actual_selection.py")
    source = ROOT / "experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/plugin-source"
    runner = (source / prepare.RUNNER).read_bytes()
    changed = prepare.transform(runner)
    assert changed[:len(runner)] == runner and changed[len(runner):] == prepare.ADDITION
    original_ast = ast.parse(runner)
    assert any(isinstance(n, ast.ClassDef) and n.name == "ModelRunnerFL" for n in original_ast.body)
    install_call = ast.parse(prepare.ADDITION.decode().lstrip().replace('\n    ', '\n')).body[-1]
    assert "ModelRunnerFL" in ast.unparse(install_call)
    assert combined[:len(core)] == core
    for name in ("service_append.py", "prepare_c3views_service.py", "biv150_c3_view_reuse.py", "check_actual_selection.py"):
        compile((HERE / name).read_bytes(), name, "exec")

    manager = SimpleNamespace(counts={"selected_calls": 100})
    sentinel = object()
    class Runner:
        def execute_model(self, scheduled, *args, **kwargs):
            if scheduled.mode == "raise":
                raise ValueError("original execute failure")
            manager.counts["selected_calls"] += scheduled.delta
            return sentinel
    original = Runner.execute_model
    observation = runtime._bind_first_actual_execute(Runner, manager)
    wrapped = Runner.execute_model
    manager.counts["selected_calls"] += 42  # dummy warmup 在 execute 外命中，不能成证据。
    capture = io.StringIO()
    with redirect_stdout(capture):
        assert Runner().execute_model(SimpleNamespace(mode="ok", delta=0, total_num_scheduled_tokens=128)) is sentinel
        assert not capture.getvalue()
        try:
            Runner().execute_model(SimpleNamespace(mode="raise", delta=0, total_num_scheduled_tokens=128))
        except ValueError as error:
            assert str(error) == "original execute failure"
        else:
            raise AssertionError("原执行异常被吞")
        assert not capture.getvalue()
        assert Runner().execute_model(SimpleNamespace(mode="ok", delta=42, total_num_scheduled_tokens=157)) is sentinel
        first = capture.getvalue()
        assert Runner.execute_model is original and observation["reported"]
        # 即使框架已缓存旧 bound 方法，后续不再打印。
        assert wrapped(Runner(), SimpleNamespace(mode="ok", delta=42, total_num_scheduled_tokens=157)) is sentinel
        assert capture.getvalue() == first
    import os
    records = validator.review("(EngineCore_DP0 pid=%d) ready\n" % os.getpid() + first)
    assert records[0]["selected_forward_calls_in_execute"] == 42
    for invalid in ("BIV150_C3_VIEWS_INSTALLED True\n", first.replace(str(os.getpid()), "999999999")):
        try:
            validator.review(invalid)
        except RuntimeError:
            pass
        else:
            raise AssertionError("安装或非 Engine PID 被当成真实命中")

    actions = []
    fake_manager = SimpleNamespace(counts={"selected_calls": 0},
        install=lambda: actions.append("install"), restore=lambda: actions.append("restore"))
    runtime.create = lambda *args: fake_manager
    with patch("importlib.import_module", return_value=object()):
        class MissingExecute:
            pass
        try:
            runtime.install_service(MissingExecute)
        except AttributeError:
            pass
        else:
            raise AssertionError("缺失执行挂点没有失败")
        assert actions == ["install", "restore"]
        assert runtime._SERVICE is None
        runtime.install_service(Runner)
        installed = Runner.execute_model
        runtime.install_service(Runner)
        assert Runner.execute_model is installed and actions == ["install", "restore", "install"]

    preparations = []
    for variant in ("baseline", "candidate"):
        output = HERE / ("prepared-" + variant)
        command = [sys.executable, str(HERE / "prepare_c3views_service.py"),
                   "--base-dir", str(source), "--output-dir", str(output), "--variant", variant]
        done = subprocess.run(command, check=True, text=True, encoding="utf-8", capture_output=True)
        preparations.append({"command": command, "stdout": done.stdout.strip()})
    baseline = json.loads((HERE / "prepared-baseline-preparation.json").read_text(encoding="utf-8"))
    candidate = json.loads((HERE / "prepared-candidate-preparation.json").read_text(encoding="utf-8"))
    assert baseline["source_sha256"] == candidate["base_source_sha256"]
    delta = sorted(k for k in set(baseline["source_sha256"]) | set(candidate["source_sha256"])
                   if baseline["source_sha256"].get(k) != candidate["source_sha256"].get(k))
    assert delta == sorted([prepare.RUNNER, prepare.HELPER])
    result = {"passed": True, "kind": "CPU only; new install/probe risk, no GPU or previous policy retest",
              "base_runner_sha256": sha(runner), "candidate_runner_sha256": sha(changed),
              "policy_core_sha256": sha(core), "service_policy_sha256": sha(combined),
              "changed_paths": delta, "baseline_file_count": len(baseline["source_sha256"]),
              "candidate_file_count": len(candidate["source_sha256"]), "preparations": preparations,
              "checks": ["exact base prefix plus C3-after install", "actual ModelRunnerFL class",
                         "core policy byte identical", "dummy/no-hit/exception do not report",
                         "first successful execute increment only", "one marker and probe restores original",
                         "cached wrapper no repeated marker", "Engine PID required",
                         "install rollback and idempotence", "full isolated copies differ only declared two paths"]}
    (HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "preparations"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
