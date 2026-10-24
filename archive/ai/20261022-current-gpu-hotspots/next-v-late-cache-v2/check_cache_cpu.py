"""只核新增隔离/失败路径和原门复用；不导入 torch/Triton、不调用设备。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS
sys.dont_write_bytecode = True
here = Path(__file__).parent
start = time.perf_counter_ns()
spec = importlib.util.spec_from_file_location("cache_probe_cpu", here / "cache_experiment.py")
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
checks = []
def record(name, condition=True):
    assert condition, name
    checks.append(name)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

old = (here.parent / "next-prefill-v-late/validate_prefill_v_late.py").read_text()
new = (here / "validate_prefill_v_late_cache.py").read_text()
anchor1, anchor2 = '            checks = {', '        q, k, v, cache, metadata = timed_case'
record("原数值/完整KV/RNG/指针流/scale正确性块逐字保留",
       old[old.index(anchor1):old.index(anchor2)] == new[new.index(anchor1):new.index(anchor2)])
for name in ("cpu_snapshot", "timed_batch", "prepare_pages"):
    def node(raw): return next(x for x in ast.parse(raw).body if isinstance(x, ast.FunctionDef) and x.name == name)
    record(name + " 原计时/输入方法AST未改", ast.dump(node(old)) == ast.dump(node(new)))
record("原policy89134字节保留", sha(here / "biv150_prefill_v_late.py") == "89134ef1d49d532d91d460094ae7a0563d1546c7d1b8b529490b77ecfa16ab08")
c = (here / "cache_bridge.c").read_text()
record("只存在一次函数cache setter；无context/dynamic setter",
       c.count("cuFuncSetCacheConfig(") == 1 and "cuCtx" not in c and "cuFuncSetAttribute(" not in c)

class Kernel:
    def __init__(self, module, function, binary=b"same binary", h="same compile hash"):
        self.module, self.function, self.kernel, self.hash = module, function, binary, h
        self.metadata, self.packed_metadata = NS(shared=49152), (8, 1, 49152)
        self.n_regs, self.n_spills = 100, 0
class Jit:
    def __init__(self, compiled): self.compiled, self.calls, self.error = compiled, 0, None
    def __getitem__(self, grid):
        def invoke(*args, **kwargs):
            self.calls += 1
            if self.error is not None: raise self.error
            return self.compiled
        return invoke
class Manager:
    def __init__(self, jit): self.candidate, self.active = jit, False
    def install(self): self.active = True
    def restore(self): self.active = False
class Bridge:
    def __init__(self, rc=0): self.mutations, self.rc = [], rc
    def attributes(self, function): return {"max_dynamic_shared": [0, 49152], "preferred_carveout": [0, -1]}
    def prefer_shared(self, function):
        self.mutations.append(function)
        return {"return_code": self.rc, "success_code": 0, "preference_enum": 1}

def fixture(rc=0, alias=False, different_binary=False):
    a, b, original = Kernel(10, 100), Kernel(20, 200), Kernel(30, 300, b"original", "original")
    b.metadata = a.metadata
    if alias: b.function = a.function
    if different_binary: b.kernel = b"different"
    ja, jb, bridge = Jit(a), Jit(b), Bridge(rc)
    manager = Manager(ja)
    pair = p.CachePair(manager, here / "cache_bridge.c")
    def setup(): pair.shared_jit, pair.bridge = jb, bridge
    pair._load_bridge_and_clone = setup
    pair._originals = lambda: [original]
    sync = []
    torch = NS(cuda=NS(synchronize=lambda: sync.append(1)))
    callback = lambda: manager.candidate[(1, 1)](example=1)
    return pair, manager, torch, callback, ja, jb, bridge, sync

pair, manager, torch, callback, ja, jb, bridge, sync = fixture()
pair.prepare(torch, callback)
record("A/B各warm恰一次且完成后只改B", ja.calls == jb.calls == 1 and len(sync) == 2 and bridge.mutations == [200])
record("warm捕获撤销且动态上限不设", manager.candidate is jb and not manager.active and not pair.report["dynamic_shared_optin_changed"])
pair.select("late_v_default")
record("A窗口选择原JIT，无capture wrapper", manager.candidate is ja and manager.active)
pair.select("candidate")
record("B窗口选择独立JIT", manager.candidate is jb and manager.active)
pair.select("baseline")
record("baseline窗口不安装candidate", not manager.active)

for name, kwargs in (("共享句柄", {"alias": True}), ("binary不一致", {"different_binary": True}), ("API失败", {"rc": 801})):
    pair, manager, torch, callback, ja, jb, bridge, sync = fixture(**kwargs)
    try: pair.prepare(torch, callback)
    except RuntimeError: pass
    else: raise AssertionError(name + " 未停止")
    record(name + " 不进入计时且恢复binding", not pair.ready and not manager.active)
    record(name + " setter次数正确", bridge.mutations == ([200] if name == "API失败" else []))
    if name == "API失败": record("失败API返回码落入结果", pair.report["mutations"][0]["return_code"] == 801)
pair, manager, torch, callback, ja, jb, bridge, sync = fixture()
error = RuntimeError("original launch failed")
ja.error = error
try: pair.prepare(torch, callback)
except RuntimeError as caught: record("原launch错误不重试、不改写", caught is error and ja.calls == 1 and jb.calls == 0)
else: raise AssertionError("lost launch error")
record("launch失败不设cache且恢复", not bridge.mutations and not manager.active)

receipt = {"status": "pass", "checks": checks, "elapsed_seconds": (time.perf_counter_ns() - start) / 1e9,
    "gpu_or_ssh": False, "c_bridge_compilation": "not run locally; must compile against installed SDK in isolated worker",
    "sha256": {x.name: sha(x) for x in here.iterdir() if x.suffix in (".py", ".c", ".sh")},
    "command": [sys.executable, "-X", "utf8", str(Path(__file__))]}
(here / "cpu-check.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"status": "pass", "checks": len(checks), "elapsed_seconds": receipt["elapsed_seconds"]}))
