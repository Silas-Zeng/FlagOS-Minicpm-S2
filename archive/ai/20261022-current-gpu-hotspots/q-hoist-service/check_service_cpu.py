"""仅新增服务接线合同：CPU替身，不证明实际JIT/设备/数值。"""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import runpy
import sys
import textwrap
from types import ModuleType, SimpleNamespace as NS

HERE = Path(__file__).parent
FOOTER = (HERE / "service_append.py").read_bytes()
KEY = "vllm_fl.patches.biv150_q_fragment_service"
checks = []


def require(value, name):
    if not value:
        raise AssertionError(name)
    checks.append(name)


class Manager:
    def __init__(self):
        self.selected = 0
        self.read_failure = False

    def snapshot(self):
        if self.read_failure:
            raise ValueError("observation only")
        return {"selected_calls": self.selected}


def fixture(*, init_error=None, execute_error=None, install_error=None):
    manager = Manager()
    installs = []

    class Runner:
        def __init__(self):
            self.init_calls = 1
            if init_error:
                raise init_error
            self.vllm_config = NS(
                model_config=NS(model="/workspace/MiniCPM5-2B", dtype="bf16",
                                is_encoder_decoder=False,
                                hf_text_config=NS(hidden_size=2048, num_hidden_layers=42,
                                                  num_attention_heads=16, num_key_value_heads=2)),
                parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
                                   decode_context_parallel_size=1, data_parallel_size=1,
                                   use_ubatching=False),
                speculative_config=None, lora_config=None,
                cache_config=NS(kv_sharing_fast_prefill=False),
                compilation_config=NS(cudagraph_mode="decode_only"))
            self.input_batch = NS(num_reqs=2)
            self.calls = 0
            self.result = object()

        def execute_model(self, scheduler_output):
            self.calls += 1
            if execute_error:
                raise execute_error
            manager.selected += 1
            return self.result

    def install(*, artifact_dir):
        installs.append(artifact_dir)
        if install_error:
            raise install_error
        return manager

    fake = ModuleType(KEY)
    fake.install = install
    sys.modules[KEY] = fake
    namespace = {"torch": NS(bfloat16="bf16"),
                 "CUDAGraphMode": NS(FULL_DECODE_ONLY="decode_only"),
                 "ModelRunnerFL": Runner}
    old_execute = Runner.execute_model
    exec(compile(textwrap.dedent(FOOTER.decode()), "runner-service-footer", "exec"), namespace)
    return Runner, manager, installs, namespace, old_execute


def main():
    old = sys.modules.get(KEY)
    env_before = os.environ.get("BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR")
    os.environ["BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR"] = str(HERE.resolve() / "not-created-by-contract")
    try:
        Runner, manager, installs, namespace, original = fixture()
        log = io.StringIO()
        with contextlib.redirect_stdout(log):
            runner = Runner()
            # ctor不能伪称真实execute；单请求smoke不能作为多请求命中。
            require(len(installs) == 1 and runner.calls == 0, "install_after_original_ctor_once")
            runner.input_batch.num_reqs = 1
            require(runner.execute_model(NS(total_num_scheduled_tokens=8)) is runner.result,
                    "smoke_return_identity")
            require("FIRST_ACTUAL" not in log.getvalue(), "smoke_not_screen_selection")
            runner.input_batch.num_reqs = 2
            require(runner.execute_model(NS(total_num_scheduled_tokens=128)) is runner.result,
                    "actual_return_identity")
            require(Runner.execute_model is original, "observer_retired_after_first_selection")
        require(log.getvalue().count("FIRST_ACTUAL_EXECUTE_SELECTED") == 1,
                "one_real_execute_marker")
        require(runner.calls == 2 and manager.selected == 2, "one_original_call_per_execute")

        error = RuntimeError("original execute error")
        Runner, manager, _, _, original = fixture(execute_error=error)
        with contextlib.redirect_stdout(io.StringIO()):
            runner = Runner()
        manager.read_failure = True
        try:
            runner.execute_model(NS(total_num_scheduled_tokens=128))
        except RuntimeError as caught:
            require(caught is error and caught.__context__ is None and runner.calls == 1,
                    "observation_failure_preserves_original_error_context")
        else:
            raise AssertionError("original error swallowed")

        Runner, manager, _, namespace, original = fixture()
        with contextlib.redirect_stdout(io.StringIO()):
            runner = Runner()
        def failing_print(*args, **kwargs):
            raise OSError("log write failed")
        namespace["print"] = failing_print
        require(runner.execute_model(NS(total_num_scheduled_tokens=128)) is runner.result
                and runner.calls == 1 and Runner.execute_model is original,
                "emit_failure_returns_original_and_retires")

        Runner, _, _, _, _ = fixture(install_error=ValueError("no manager"))
        with contextlib.redirect_stdout(io.StringIO()):
            runner = Runner()
        require(runner.init_calls == 1 and not hasattr(runner, "_biv150_q_fragment_service_manager"),
                "install_failure_preserves_constructor")

        ctor_error = RuntimeError("original ctor error")
        Runner, _, installs, _, _ = fixture(init_error=ctor_error)
        try:
            Runner()
        except RuntimeError as caught:
            require(caught is ctor_error and caught.__context__ is None and not installs,
                    "constructor_exception_no_install")
        else:
            raise AssertionError("ctor error swallowed")

        prep = runpy.run_path(str(HERE / "prepare_q_hoist_service.py"))
        base = Path("docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py").read_bytes()
        changed = prep["transform"](base, FOOTER)
        require(changed[:-len(FOOTER)] == base, "exact_runner_prefix_and_inverse")
        require(not any(x in sys.modules for x in ("torch", "triton", "vllm")),
                "no_framework_device_import")
        receipt = {"passed": True, "checks": checks,
                   "footer_sha256": hashlib.sha256(FOOTER).hexdigest(),
                   "candidate_runner_sha256": hashlib.sha256(changed).hexdigest(),
                   "test_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   "limit": "CPU stub only; no actual helper/compiler/GPU or complete-source copy executed"}
        (HERE / "service-cpu-check.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(receipt, ensure_ascii=False))
    finally:
        if old is None:
            sys.modules.pop(KEY, None)
        else:
            sys.modules[KEY] = old
        if env_before is None:
            os.environ.pop("BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR", None)
        else:
            os.environ["BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR"] = env_before


if __name__ == "__main__":
    main()
