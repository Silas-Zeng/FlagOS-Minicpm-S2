"""只执行 v2 新增的观察失败隔离合同；不重跑原 policy/旧接线套件。"""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
OLD = HERE.with_name("c3views-service")
ROOT = HERE.parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    old_files = {p.name: sha(p.read_bytes()) for p in OLD.iterdir() if p.is_file()}
    core = (ROOT / "tmp/small-input-gates/biv150_c3_view_reuse.py").read_bytes()
    assert sha(core) == "ba085577f24684cb980cdd09c2978192ff9b8b3a70fa62aadc1cfd3efced61d4"
    suffix = (HERE / "service_append.py").read_bytes()
    policy = core + suffix
    (HERE / "biv150_c3_view_reuse.py").write_bytes(policy)
    runtime = load("c3views_v2_failure_test", HERE / "biv150_c3_view_reuse.py")
    preparer = load("c3views_v2_preparer", HERE / "prepare_c3views_service.py")
    outcomes = []
    for failure in ("before_counter", "after_counter", "json", "print"):
        class Counter:
            value = 100
            reads = 0
            def __getitem__(self, key):
                assert key == "selected_calls"
                self.reads += 1
                if (failure == "before_counter" and self.reads == 1
                        or failure == "after_counter" and self.reads == 2):
                    raise RuntimeError("injected observation counter failure")
                return self.value
        counts = Counter()
        manager = SimpleNamespace(counts=counts)
        returned = object()
        class Runner:
            calls = 0
            def execute_model(self, scheduled, *args, **kwargs):
                self.calls += 1
                counts.value += 42
                return returned
        original = Runner.execute_model
        state = runtime._bind_first_actual_execute(Runner, manager)
        cached = Runner.execute_model
        runner = Runner()
        scheduled = SimpleNamespace(total_num_scheduled_tokens=157)
        target = "json.dumps" if failure == "json" else "builtins.print"
        with patch(target, side_effect=OSError("injected observer emission failure")) as emitted:
            assert runner.execute_model(scheduled) is returned
            assert runner.calls == 1 and state["disabled"] and not state["reported"]
            assert Runner.execute_model is original
            reads = counts.reads
            assert cached(runner, scheduled) is returned
            assert runner.calls == 2 and counts.reads == reads
            assert emitted.call_count == (1 if failure in ("json", "print") else 0)
        outcomes.append({"failure": failure, "original_returns_preserved": True,
                         "execution_once_per_call": True, "observer_disabled_no_retry": True})
    # 原模型异常仍离开观察 try，不得吞掉或重试。
    class FailingRunner:
        calls = 0
        def execute_model(self, scheduled):
            self.calls += 1
            raise ValueError("original model error")
    instance = FailingRunner()
    runtime._bind_first_actual_execute(FailingRunner, SimpleNamespace(counts={"selected_calls": 0}))
    try:
        instance.execute_model(SimpleNamespace(total_num_scheduled_tokens=1))
    except ValueError as error:
        assert str(error) == "original model error" and instance.calls == 1
    else:
        raise AssertionError("原异常被吞")
    runner = (ROOT / "docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py").read_bytes()
    candidate = preparer.transform(runner)
    assert candidate == (OLD / "prepared-candidate/vllm_fl/worker/model_runner.py").read_bytes()
    assert policy[:-len(suffix)] == core
    assert old_files == {p.name: sha(p.read_bytes()) for p in OLD.iterdir() if p.is_file()}
    result = {"passed": True, "scope": "新增 observer 失败隔离；未执行旧套件或 GPU",
              "cases": outcomes, "model_exception_propagates": True, "old_package_unchanged": True,
              "core_policy_sha256": sha(core), "service_policy_sha256": sha(policy),
              "candidate_runner_sha256": sha(candidate),
              "preparer_sha256": sha((HERE / "prepare_c3views_service.py").read_bytes()),
              "suffix_sha256": sha(suffix)}
    (HERE / "observer-failure-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
