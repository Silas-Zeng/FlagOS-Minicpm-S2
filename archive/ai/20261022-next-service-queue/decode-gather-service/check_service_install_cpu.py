"""唯一新增接线合同；不重测1a9/原方法门，不导入设备框架。"""
import ast
from contextlib import redirect_stdout
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
import textwrap
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    prepare = load("prepare_decode_gather_service", HERE / "prepare_decode_gather_service.py")
    validator = load("check_decode_gather_selection", HERE / "check_actual_selection.py")
    source = ROOT / "experiments/framework/20261022T070452Z-cpu-combination-combined-decode4k-control/plugin-source"
    raw = (source / prepare.RUNNER).read_bytes()
    original_helper = (ROOT / "tmp/next-decode-gather/biv150_decode_cpu_gather.py").read_bytes()
    helper = (HERE / "biv150_decode_cpu_gather.py").read_bytes()
    assert helper == original_helper and sha(helper) == prepare.RUNTIME_SHA
    footer = (HERE / "service_append.py").read_bytes()
    changed = prepare.transform(raw)
    runtime = prepare.load_runtime()
    assert changed.endswith(footer) and runtime.reverse(changed[:-len(footer)]) == raw
    for bad in (changed, raw + b"\n"):
        try:
            prepare.transform(bad)
        except RuntimeError:
            pass
        else:
            raise AssertionError("允许重复或不明基点")
    namespace = {}
    tree = ast.parse(textwrap.dedent(footer.decode("utf-8")))
    factory = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[factory], type_ignores=[])),
                 "actual:service-observer-footer", "exec"), namespace)
    sentinel = object()
    original_error = ValueError("原execute异常")

    class Runner:
        def __init__(self):
            self._biv150_decode_cpu_gather = {"selected": 40, "fallback": 0}
            self.input_batch = NS(num_reqs=62)
            self.original_calls = 0

        def execute_model(self, output, *args, **kwargs):
            self.original_calls += 1
            if output.fail:
                raise original_error
            self._biv150_decode_cpu_gather["selected"] += output.delta
            return sentinel

    original = Runner.execute_model
    namespace[factory.name](Runner)
    wrapped = Runner.execute_model
    runner = Runner()
    runner._biv150_decode_cpu_gather["selected"] += 80  # dummy历史，不能冒称真实命中。
    capture = io.StringIO()
    with redirect_stdout(capture):
        assert runner.execute_model(NS(delta=0, fail=False, total_num_scheduled_tokens=62)) is sentinel
        assert not capture.getvalue()
        try:
            runner.execute_model(NS(delta=0, fail=True, total_num_scheduled_tokens=62))
        except ValueError as error:
            assert error is original_error and error.__context__ is None
        else:
            raise AssertionError("原异常丢失")
        assert not capture.getvalue()
        runner.input_batch.num_reqs = 1
        assert runner.execute_model(NS(delta=1, fail=False, total_num_scheduled_tokens=1)) is sentinel
        assert not capture.getvalue(), "单请求smoke不是多请求screen命中"
        runner.input_batch.num_reqs = 62
        assert runner.execute_model(NS(delta=1, fail=False, total_num_scheduled_tokens=62)) is sentinel
        first = capture.getvalue()
        assert first.count(validator.MARKER) == 1 and Runner.execute_model is original
        assert wrapped(runner, NS(delta=1, fail=False, total_num_scheduled_tokens=62)) is sentinel
        assert capture.getvalue() == first and runner.original_calls == 5
    records = validator.review("(EngineCore_DP0 pid=%d) ready\n" % os.getpid() + first)
    assert records[0]["selected_prepare_inputs_calls_in_execute"] == 1
    for invalid in (first, first.replace('"num_requests": 62', '"num_requests": 1')):
        try:
            validator.review(invalid)
        except RuntimeError:
            pass
        else:
            raise AssertionError("缺Engine PID或单请求记录未拒绝")
    namespace[factory.name](Runner)
    emit_failure = Runner()
    with patch("builtins.print", side_effect=OSError("诊断写入失败")):
        assert emit_failure.execute_model(NS(delta=1, fail=False, total_num_scheduled_tokens=62)) is sentinel
    assert Runner.execute_model is original and emit_failure.original_calls == 1

    class BadObservation(dict):
        def get(self, *args):
            raise ValueError("观察元信息失败")

    namespace[factory.name](Runner)
    read_failure = Runner()
    read_failure._biv150_decode_cpu_gather = BadObservation(selected=40, fallback=0)
    try:
        read_failure.execute_model(NS(delta=0, fail=True, total_num_scheduled_tokens=62))
    except ValueError as error:
        assert error is original_error and error.__context__ is None
    else:
        raise AssertionError("观察失败吞掉原异常")
    assert Runner.execute_model is original and read_failure.original_calls == 1
    baseline = prepare.source_map(source)
    assert baseline[prepare.RUNNER] == prepare.BASE_SHA and prepare.HELPER not in baseline
    expected = {**baseline, prepare.RUNNER: sha(changed), prepare.HELPER: sha(helper)}
    delta = sorted(k for k in set(expected) | set(baseline) if expected.get(k) != baseline.get(k))
    assert delta == sorted([prepare.RUNNER, prepare.HELPER])
    launcher = (HERE / "launch_decode_gather_service.sh").read_text(encoding="utf-8")
    reference = (ROOT / "tmp/c3views-service/launch_c3views_service.sh").read_text(encoding="utf-8")
    command = next(line for line in launcher.splitlines() if line.startswith("command=("))
    assert command == next(line for line in reference.splitlines() if line.startswith("command=("))
    for block in re.findall(r"<<'PY'\n(.*?)\nPY\n", launcher, re.S):
        compile(block, "launcher:stdlib-heredoc", "exec")
    for filename in ("prepare_decode_gather_service.py", "check_actual_selection.py", "biv150_decode_cpu_gather.py"):
        compile((HERE / filename).read_bytes(), filename, "exec")
    assert not any(name in sys.modules for name in ("torch", "triton", "vllm"))
    result = {"passed": True, "kind": "one CPU observer/transform contract; no runtime or GPU retest",
              "base_runner_sha256": sha(raw), "candidate_runner_sha256": sha(changed),
              "runtime_sha256": sha(helper), "observer_footer_sha256": sha(footer),
              "base_files": len(baseline), "candidate_files": len(expected), "changed_paths": delta,
              "full_copy_executed": False, "original_driver_command_line_unchanged": True,
              "checks": ["exact helper unchanged", "6f transform inverse exact", "no dummy history marker",
                         "no single-request smoke marker", "original execute once/result/exception unchanged",
                         "first same-Engine multi-request selected delta", "observer removed after first hit",
                         "cached wrapper no repeated marker", "emit failure preserves successful result",
                         "observation read failure preserves original exception context",
                         "two source paths only", "no device imports"]}
    (HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
