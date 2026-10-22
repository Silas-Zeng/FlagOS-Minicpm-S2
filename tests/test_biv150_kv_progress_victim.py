"""唯一CPU合同：actual Request/分配内层while、单次选择与精确反向；非GPU证明。"""
import ast
from collections import deque
import copy
import enum
import hashlib
import importlib.util
from pathlib import Path
import sys
import textwrap
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "kv_progress_victim_cpu"
package = ModuleType(PACKAGE)
package.__path__ = [str(ROOT / "patches/framework")]
sys.modules[PACKAGE] = package


def load(name, path):
    spec = importlib.util.spec_from_file_location(PACKAGE + "." + name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


P = load("biv150_kv_transaction", "patches/framework/candidates/biv150_kv_full_restore_transaction.py")
R = load("biv150_kv_protocol", "patches/framework/candidates/biv150_kv_progress_victim_protocol.py")


def actual_request():
    path = ROOT / "experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/request.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == R.EXPECTED_CAPACITY_REQUEST
    definitions = {n.name: n for n in ast.parse(path.read_text(encoding="utf-8")).body if isinstance(n, ast.ClassDef)}
    module = ModuleType("vllm.v1.request")
    module.__file__, module.__dict__["enum"] = str(path.resolve()), enum
    tree = ast.Module(body=[ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0),
                           definitions["RequestStatus"], definitions["Request"]], type_ignores=[])
    exec(compile(ast.fix_missing_locations(tree), str(path.resolve()), "exec"), module.__dict__)
    return module


def actual_schedule():
    path = ROOT / "experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/sched/scheduler.py"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090"
    text = path.read_text(encoding="utf-8")
    cls, = [n for n in ast.parse(text).body if isinstance(n, ast.ClassDef) and n.name == "Scheduler"]
    method, = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "schedule"]
    return textwrap.dedent("".join(text.splitlines(keepends=True)[method.lineno - 1:method.end_lineno]))


def fragment(source):
    loop, = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.While)
             and isinstance(n.test, ast.Constant) and n.test.value is True
             and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                     and x.func.attr == "_preempt_request" for x in ast.walk(n))]
    fn = ast.parse("def run(self, request, num_new_tokens, token_budget, req_index, scheduled_running_reqs, num_scheduled_tokens, req_to_new_blocks):\n    pass\n").body[0]
    fn.body = ast.parse("scheduled_timestamp=123.0\npreempted_reqs=[]\n").body + [copy.deepcopy(loop)]
    fn.body += ast.parse("return new_blocks, token_budget, req_index, preempted_reqs\n").body
    namespace = {"SchedulingPolicy": NS(PRIORITY=object()), "_biv150_progress_victim_index": R._progress_victim_index}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "<actual-running-innerwhile>", "exec"), namespace)
    return namespace["run"]


class NoTokenValues:
    def __init__(self, length): self.length = length
    def __len__(self): return self.length
    def __iter__(self): raise AssertionError("禁止读取token内容")
    def __getitem__(self, item): raise AssertionError("禁止读取token内容")


class ForbiddenFuture:
    def __getattribute__(self, name): raise AssertionError("禁止访问Future：" + name)


class Contract(unittest.TestCase):
    def test_single_selection_actual_innerwhile_and_fallback(self):
        request_module = actual_request()
        output_module = ModuleType("vllm.v1.core.sched.output")
        class Output:
            def __init__(self, counts): self.num_scheduled_tokens = counts
        output_module.SchedulerOutput = Output
        original, changed = actual_schedule(), R._transform_progress_schedule(actual_schedule())
        self.assertEqual(changed.replace(R.PROGRESS_REPLACEMENT, R.PROGRESS_POP).replace(R.RESTORE_INSERTION, "", 1), original)
        compile(changed, "<whole-exact-schedule>", "exec")
        with self.assertRaises(RuntimeError): R._transform_progress_schedule(original + "\n")
        old_loop, new_loop = fragment(original), fragment(changed)
        records = []

        def make(results=None):
            rows = []
            # ID顺序与进展无关；相同进展64时必须取靠后的原位置。
            for i, (rid, count) in enumerate(zip(("zz", "xx", "aa", "mm", "bb"), (96, 80, 64, 64, 32))):
                request = request_module.Request.__new__(request_module.Request)
                request.request_id, request.status = rid, request_module.RequestStatus.RUNNING
                request._output_token_ids, request._all_token_ids = NoTokenValues(count), NoTokenValues(32 + count)
                request.num_prompt_tokens, request.max_tokens = 32, 128
                request.num_computed_tokens, request.num_output_placeholders = 32 + count, 11
                request.resumable, request.streaming_queue, request.is_prefill_chunk = False, None, False
                rows.append(request)
            owned = {r.request_id: [NS(block_id=i * 100 + j + 1, ref_cnt=1, is_null=False, block_hash=b"hashed")
                       for j in range(r.num_computed_tokens // 16)] for i, r in enumerate(rows)}
            single = NS(req_to_blocks=owned, num_cached_block={r.request_id: 0 for r in rows})
            manager = NS(max_model_len=131072, coordinator=NS(single_type_managers=[single]),
                         block_pool=NS(free_block_queue=NS(num_free_blocks=0)))
            scheduler = NS(policy=NS(name="FCFS"), running=rows, requests={r.request_id: r for r in rows},
                           num_lookahead_tokens=0, kv_cache_manager=manager, events=[], results=list(results or []))
            def allocate(request, count, **kw):
                scheduler.events.append(("allocate", request.request_id, count, kw))
                value = scheduler.results.pop(0)
                if isinstance(value, Exception): raise value
                return value
            def preempt(request, stamp): scheduler.events.append(("preempt", request.request_id, stamp))
            manager.allocate_slots, scheduler._preempt_request = allocate, preempt
            state = {"eligible": True, "engine": NS(scheduler=scheduler,
                batch_queue=deque([(ForbiddenFuture(), Output({r.request_id: 2 for r in rows}), ForbiddenFuture())])),
                "victim": None, "slot": P.HostSlot(1 << 30), "progress_victim_attempted": False,
                "counts": {"progress_victim_attempts": 0, "progress_victim_selected": 0}}
            # 此前只排row0；不能把这一步current token再从row3安全R扣除。
            return scheduler, state, [rows[0]], {rows[0].request_id: 1}, {rows[0].request_id: object()}

        def invoke(env, fn=new_loop):
            scheduler, state, scheduled, tokens, blocks = env
            request = scheduler.running[1]
            token = R._ACTIVE.set(state)
            try:
                return fn(scheduler, request, 1, 2047, 1, scheduled, tokens, blocks)
            finally:
                R._ACTIVE.reset(token)

        def index(env):
            scheduler, state, scheduled, tokens, blocks = env
            token = R._ACTIVE.set(state)
            try:
                return R._progress_victim_index(scheduler, scheduler.running[1], 1, 1, scheduled, tokens, blocks)
            finally:
                R._ACTIVE.reset(token)

        with patch.dict(sys.modules, {"vllm.v1.request": request_module, "vllm.v1.core.sched.output": output_module}), \
                patch.object(R, "_emit", side_effect=lambda state, event, **fields: records.append((event, fields))):
            R._CAPACITY_REQUEST_CHECKED, R._CAPACITY_REQUEST_CLASS = False, None
            self.assertIs(R._capacity_request_class(), request_module.Request)
            env = make()
            self.assertEqual(index(env), 3)
            self.assertEqual(index(env), -1)  # 同Engine不再遍历/选择。
            self.assertEqual(env[1]["counts"], {"progress_victim_attempts": 1, "progress_victim_selected": 1})
            self.assertEqual(records[-1][1]["selected_prefix_tokens"], 80)  # queued2；不是placeholder11。
            self.assertEqual(records[-1][1]["candidate_count"], 2)
            self.assertFalse(records[-1][1]["save_success_predicted"])
            allocated = object()
            env = make([None, allocated])
            survivors = list(env[0].running)
            result = invoke(env)
            self.assertIs(result[0], allocated)
            self.assertEqual((result[1], result[2]), (2047, 1))
            self.assertEqual(env[0].events[1], ("preempt", "mm", 123.0))
            self.assertEqual(env[0].running, survivors[:3] + survivors[4:])
            self.assertEqual([e[1] for e in env[0].events if e[0] == "allocate"], ["xx", "xx"])
            env = make([None, None, allocated])
            invoke(env)
            self.assertEqual([e[1] for e in env[0].events if e[0] == "preempt"], ["mm", "bb"])
            self.assertEqual(env[1]["counts"]["progress_victim_selected"], 1)  # 仅一次主动替换，后续原tail。
            # 三容器分别排除高进展tie项，资格之外只回原tail。
            for container in ("scheduled", "tokens", "blocks"):
                env = make()
                row = env[0].running[3]
                if container == "scheduled": env[2].append(row)
                elif container == "tokens": env[3][row.request_id] = 1
                else: env[4][row.request_id] = object()
                self.assertEqual(index(env), 2)
            # minremaining与maxconfirmed不是同一个集合时，仍分别保护。
            env = make()
            env[0].running[3].max_tokens = 65
            self.assertEqual(index(env), 2)
            for reason in ("identity", "streaming", "private", "cap", "prefix", "queued", "no_progress"):
                with self.subTest(reason=reason):
                    env = make([None, allocated])
                    for row in env[0].running[2:4]:
                        owned = env[0].kv_cache_manager.coordinator.single_type_managers[0].req_to_blocks[row.request_id]
                        if reason == "identity": env[0].requests[row.request_id] = object()
                        elif reason == "streaming": row.resumable = True
                        elif reason == "private":
                            for block in owned: block.ref_cnt = 2
                        elif reason == "cap":
                            row._all_token_ids = NoTokenValues(100000)
                            row.num_prompt_tokens, row.num_computed_tokens = 100000 - row.num_output_tokens, 100000
                        elif reason == "prefix": owned[0].is_null = True
                        elif reason == "no_progress": row._output_token_ids = NoTokenValues(32)
                    if reason == "queued": env[1]["engine"].batch_queue.append((ForbiddenFuture(), object(), ForbiddenFuture()))
                    baseline = make([None, allocated])
                    expected = invoke(baseline, old_loop)
                    actual = invoke(env)
                    self.assertIs(actual[0], expected[0])
                    self.assertEqual(env[0].events, baseline[0].events)
                    self.assertTrue(env[1]["progress_victim_attempted"])
                    self.assertEqual(env[1]["counts"]["progress_victim_selected"], 0)
            for held in ("victim", "owner", "bytes"):
                env = make()
                if held == "victim": env[1]["victim"] = object()
                elif held == "owner": env[1]["slot"].key = object()
                else: env[1]["slot"].used_bytes = 1
                self.assertEqual(index(env), -1)
                self.assertFalse(env[1]["progress_victim_attempted"])
            env = make([allocated])
            invoke(env)
            self.assertFalse(env[1]["progress_victim_attempted"])
            raised = RuntimeError("same-original")
            env = make([None])
            env[1]["engine"].batch_queue = deque([(ForbiddenFuture(), object(), ForbiddenFuture())])
            def fail(*args): raise raised
            env[0]._preempt_request = fail
            with self.assertRaises(RuntimeError) as caught: invoke(env)
            self.assertIs(caught.exception, raised)
            self.assertIsNone(raised.__context__)
            self.assertIsNone(R._ACTIVE.get())
        # FULL全部原有函数AST未改（install/Core只增加精确接入与state/counters）。
        full = ROOT / "patches/framework/candidates/biv150_kv_full_restore_protocol.py"
        self.assertEqual(hashlib.sha256(full.read_bytes()).hexdigest(), "1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8")
        old = {n.name: n for n in ast.parse(full.read_text()).body if isinstance(n, ast.FunctionDef)}
        new = {n.name: n for n in ast.parse(Path(R.__file__).read_text()).body if isinstance(n, ast.FunctionDef)}
        for name in old.keys() - {"_wrap_core", "install"}:
            self.assertEqual(ast.dump(old[name], include_attributes=False), ast.dump(new[name], include_attributes=False), name)
        for path, digest in (("biv150_kv_full_restore_worker.py", "5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477"),
                             ("biv150_kv_full_restore_transaction.py", "84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883")):
            self.assertEqual(hashlib.sha256((full.parent / path).read_bytes()).hexdigest(), digest)
        self.assertFalse(any(name in sys.modules for name in ("torch", "numpy", "vllm")))


if __name__ == "__main__": unittest.main()
