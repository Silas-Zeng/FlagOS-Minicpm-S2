"""唯一新增 CPU 合同：真 run AST 的非空 hook 尾部不变；非设备验证。"""
from pathlib import Path
import ast
import copy
import hashlib
import json
import runpy
import sys
from types import SimpleNamespace as NS

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
runtime = HERE / "biv150_attention_key_recipe.py"
policy = runpy.run_path(str(runtime))
jit = ROOT / "experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/runtime/jit.py"
source = policy["_require_file"](jit, policy["EXPECTED_JIT"])
original_tree = ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(policy["_method_tree"](source))], type_ignores=[]))
events, records = [], []
box = {"G": 1, "stream": "current-nondefault-stream"}
sentinel = RuntimeError("hook 原异常")


class HookChain:
    """CPU stub，模拟非 None 可调用链；不是安装类或设备证明。"""
    failure = False

    def __init__(self, name):
        self.name = name

    def __call__(self, metadata):
        events.append((self.name, metadata))
        if self.failure:
            raise sentinel


enter, exit_hook = HookChain("enter"), HookChain("exit")
assert enter is not None and bool(enter)
knobs = NS(runtime=NS(debug=False, launch_enter_hook=enter, launch_exit_hook=exit_hook),
           compilation=NS(instrumentation_mode=""))


class Compiled:
    function = "function"
    packed_metadata = "packed"

    def launch_metadata(self, grid, stream, *args):
        data = (grid, stream, args)
        events.append(("metadata", data))
        return data

    def run(self, *args):
        events.append(("launch", args))
        args[7](args[6])
        args[8](args[6])


compiled = Compiled()


def binder(*args, **kwargs):
    events.append(("binder", args))
    return {"ptr": args[0]}, [("pointer", "aligned")], {"debug": False, "instrumentation_mode": ""}


def cache_key(*args):
    events.append(("key",))
    return "key"


globals_dict = {"knobs": knobs, "compute_cache_key": cache_key,
                "_flagprism": NS(apply_compile_options=lambda kwargs: events.append(("flagprism",))),
                "driver": NS(active=NS(get_current_device=lambda: 0,
                                       get_current_stream=lambda device: box["stream"]))}
original_local, new_local = {}, {}
exec(compile(original_tree, str(jit), "exec"), globals_dict, original_local)
exec(compile(policy["_factory_tree"](source), str(jit), "exec"), globals_dict, new_local)
self = NS(debug=False, pre_run_hooks=[], device_caches={0: ({"key": compiled}, {}, None, None, binder)},
          used_global_vals={("G", 0): (1, box)})
original = original_local["run"]
new = new_local["_biv_factory"](lambda *args: ("key", compiled), lambda *args: records.append(args[-1]))
assert new.__globals__ is globals_dict
assert original(self, "fresh-A", grid=(3, 2), warmup=False) is compiled
baseline = list(events)
events.clear()
assert new(self, "fresh-A", grid=(3, 2), warmup=False) is compiled
assert events == [row for row in baseline if row[0] != "key"]
assert records == [True]
assert [row[0] for row in events] == ["flagprism", "binder", "metadata", "launch", "enter", "exit"]

# 不保留旧 bound 参数/旧 stream，且原 2D grid 不被补维后传给 metadata。
events.clear()
box["stream"] = "next-current-stream"
new(self, "fresh-B", grid=(7, 2), warmup=False)
assert ("metadata", ((7, 2), "next-current-stream", ("fresh-B",))) in events

# 全局变更和 hook 原异常都在原 tail 抛出；不能重试或附加 context。
events.clear()
box["G"] = 2
try:
    new(self, "fresh-C", grid=(3, 2), warmup=False)
except RuntimeError as exc:
    assert "Global variable G has changed" in str(exc) and exc.__context__ is None
else:
    raise AssertionError("global 变更没拒绝")
assert not any(row[0] == "launch" for row in events)
box["G"] = 1
events.clear()
enter.failure = True
try:
    new(self, "fresh-D", grid=(3, 2), warmup=False)
except RuntimeError as exc:
    assert exc is sentinel and exc.__context__ is None
else:
    raise AssertionError("hook 异常被吞")
assert sum(row[0] == "launch" for row in events) == 1
assert sum(row[0] == "enter" for row in events) == 1
assert not any(row[0] == "exit" for row in events)
assert not any(name in sys.modules for name in ("torch", "triton", "vllm"))

result = {"status": "CPU_nonNone_hook_original_tail_contract_passed_not_device_validation",
          "runtime_sha256": hashlib.sha256(runtime.read_bytes()).hexdigest(),
          "check_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          "jit_sha256": hashlib.sha256(jit.read_bytes()).hexdigest(),
          "checks": ["exact_AST_reverse", "original_tail_AST", "nonNone_hooks_invoked_once_same_metadata_order",
                     "only_key_recipe_skipped", "original_2D_grid_metadata", "fresh_args_current_stream",
                     "dynamic_globals", "same_hook_exception_no_retry_no_context", "no_framework_import"],
          "limitations": ["CPU HookChain/compiled/binder stubs; not actual hooks implementation or numerical/stream GPU proof."]}
(HERE / "cpu-hook-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
