"""唯一CPU合同：actual内层分配/抢占片段+源码逆变换；不模拟GPU或整个调度器。"""
import ast
from collections import deque
import copy
import hashlib
import importlib.util
from pathlib import Path
import sys
import textwrap
from types import ModuleType, SimpleNamespace as NS
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.dont_write_bytecode = True


def load():
    package = ModuleType("preemption_snapshot_contract")
    package.__path__ = [str(ROOT / "patches/framework")]
    sys.modules[package.__name__] = package
    name = package.__name__ + ".biv150_preemption_snapshot"
    spec = importlib.util.spec_from_file_location(name, ROOT / "patches/framework/biv150_preemption_snapshot.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def actual_source():
    p = ROOT / "experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/sched/scheduler.py"
    raw = p.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090"
    source = raw.decode()
    cls, = [n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == "Scheduler"]
    method, = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "schedule"]
    return textwrap.dedent("".join(source.splitlines(keepends=True)[method.lineno - 1:method.end_lineno]))


def fragment(source, callback):
    loops = [n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.While)
             and any(isinstance(x, ast.Call) and isinstance(x.func, ast.Attribute)
                     and x.func.attr == "_preempt_request" for x in ast.walk(n))]
    loop, = [n for n in loops if isinstance(n.test, ast.Constant) and n.test.value is True]
    preface = ast.parse("def contract(self, request, num_new_tokens, token_budget, req_index, num_scheduled_tokens):\n    pass\n").body[0]
    # FCFS原分支只访问这些真实局部；PRIORITY不执行，但源码/AST仍原样保留。
    preface.body = ast.parse("scheduled_timestamp=123.0\npreempted_reqs=[]\n").body + [copy.deepcopy(loop)]
    preface.body += ast.parse("return new_blocks, token_budget, req_index, preempted_reqs\n").body
    namespace = {"SchedulingPolicy": NS(PRIORITY="PRIORITY"), "_biv150_capture_running_failure": callback}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[preface], type_ignores=[])), "<actual-allocation-fragment>", "exec"), namespace)
    return namespace["contract"]


class ForbiddenFuture:
    def __getattribute__(self, name):
        raise AssertionError("禁止访问future：" + name)


class Request:
    pass


class Output:
    def __init__(self, counts):
        self.num_scheduled_tokens = counts


class Scheduler:
    def __init__(self, results, status, preempt_error=None):
        self.policy, self.num_lookahead_tokens = "FCFS", 0
        self.events, self.results, self.preempt_error = [], list(results), preempt_error
        self.running = []
        for index in range(2):
            r = Request()
            r.request_id, r.status = "request-" + str(index), status
            r.num_computed_tokens, r.num_tokens = 32, 35
            r.num_output_tokens, r.num_prompt_tokens, r.max_tokens = 3, 32, 1024
            r.num_output_placeholders, r.num_preemptions, r.next_decode_eligible_step = 1, 0, 0
            r.is_prefill_chunk, r.resumable, r.streaming_queue = False, False, None
            self.running.append(r)
        self.requests = {r.request_id: r for r in self.running}
        blocks = {r.request_id: [NS(block_id=i * 2 + j + 1, ref_cnt=1, is_null=False, block_hash=None)
                                for j in range(2)] for i, r in enumerate(self.running)}
        single = NS(req_to_blocks=blocks, num_cached_block={rid: 0 for rid in blocks})
        self.kv_cache_manager = NS(coordinator=NS(single_type_managers=[single]),
            block_pool=NS(free_block_queue=NS(num_free_blocks=0)), max_model_len=131072,
            allocate_slots=self.allocate)

    def allocate(self, request, count, **kwargs):
        self.events.append(("allocate", request.request_id, count, kwargs))
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def _preempt_request(self, request, timestamp):
        self.events.append(("preempt", request.request_id, timestamp))
        if self.preempt_error is not None:
            raise self.preempt_error


class SnapshotContract(unittest.TestCase):
    def test_exact_source_failure_branch_and_original_semantics(self):
        m = load()
        self.assertFalse(m.install())
        source = actual_source()
        changed = m.transform_schedule(source)
        self.assertEqual(changed.replace(m.INSERTION, "", 1), source)
        compile(changed, "<actual-full-schedule>", "exec")
        original_ast, changed_ast = ast.parse(source), ast.parse(changed)
        calls = [n for n in ast.walk(changed_ast) if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and isinstance(n.value.func, ast.Name) and n.value.func.id == "_biv150_capture_running_failure"]
        self.assertEqual(len(calls), 1)
        for n in ast.walk(changed_ast):
            if hasattr(n, "body") and isinstance(n.body, list) and calls[0] in n.body:
                n.body.remove(calls[0])
        self.assertEqual(ast.dump(original_ast, include_attributes=False), ast.dump(changed_ast, include_attributes=False))
        with self.assertRaises(RuntimeError):
            m.transform_schedule(source + "\n")
        status, allocated = object(), object()
        original = fragment(source, lambda *args: self.fail("原方法不应调callback"))
        observed = fragment(changed, m._capture_running_failure)

        def invoke(fn, results, *, queue_bad=False, preempt_error=None, repeat=False):
            scheduler = Scheduler(results, status, preempt_error)
            output = Output({"request-0": 1})
            engine = NS(scheduler=scheduler, batch_queue=deque([(ForbiddenFuture(), output, ForbiddenFuture())]))
            if queue_bad:
                engine.batch_queue.append((ForbiddenFuture(), object(), ForbiddenFuture()))
            state = {"attempted": False}
            classes = {"request": Request, "request_status": NS(RUNNING=status), "output": Output}
            frame = {"engine": engine, "state": state, "classes": classes}
            records = []
            token = m._ACTIVE.set(frame)
            try:
                with patch.object(m, "_emit", side_effect=lambda event, **kw: records.append((event, kw))):
                    result = fn(scheduler, scheduler.running[0], 1, 2048, 0, {})
                    if repeat:
                        m._capture_running_failure(scheduler, scheduler.running[0], 1, 2048, 0, {})
                return result, scheduler, records
            finally:
                m._ACTIVE.reset(token)

        before, before_sched, _ = invoke(original, [None, allocated])
        after, after_sched, records = invoke(observed, [None, allocated], repeat=True)
        self.assertIs(before[0], after[0])
        self.assertEqual(before_sched.events, after_sched.events)
        self.assertEqual([r.request_id for r in before_sched.running], [r.request_id for r in after_sched.running])
        self.assertEqual([x[0] for x in records], ["FIRST_RUNNING_FAILURE"])
        payload = records[0][1]
        self.assertTrue(payload["complete"])
        self.assertEqual(payload["original_tail_victim_request_id"], "request-1")
        self.assertEqual(payload["required_new_blocks_derived_from_exact_fast_path"], 1)
        self.assertEqual(payload["running"][0]["snapshot_prefix_tokens"], 16)
        self.assertEqual(payload["running"][0]["queued_scheduled_span"], 1)
        self.assertEqual(payload["running"][0]["private_single_ref_unique_pages"], 2)
        _, _, no_failure = invoke(observed, [allocated])
        self.assertEqual(no_failure, [])
        _, still_original, incomplete = invoke(observed, [None, allocated], queue_bad=True)
        self.assertEqual(still_original.events, before_sched.events)
        self.assertEqual([x[0] for x in incomplete], ["SNAPSHOT_INCOMPLETE"])
        for preempt in (False, True):
            exception = RuntimeError("same-original-exception")
            for fn in (original, observed):
                with self.assertRaises(RuntimeError) as caught:
                    invoke(fn, [None, allocated] if preempt else [exception], preempt_error=exception if preempt else None)
                self.assertIs(caught.exception, exception)
        self.assertIsNone(m._ACTIVE.get())

        class Engine:
            batch_queue = deque()
        result, raised = object(), RuntimeError("same-core-exception")
        engine = Engine()
        with patch.object(m.scope_probe, "_scope", return_value=True), patch.object(m, "_emit"):
            wrapper = m._wrap_core(lambda self: result, {})
            self.assertIs(wrapper(engine), result)
            self.assertIsNone(m._ACTIVE.get())
            def fail(self):
                raise raised
            with self.assertRaises(RuntimeError) as caught:
                m._wrap_core(fail, {})(engine)
            self.assertIs(caught.exception, raised)
            self.assertIsNone(m._ACTIVE.get())
            metadata_error, original_error = ValueError("metadata"), RuntimeError("original")
            def original_failure(self):
                raise original_error
            with patch.object(m, "_STATES") as bad_states:
                bad_states.get.side_effect = metadata_error
                with self.assertRaises(RuntimeError) as caught:
                    m._wrap_core(original_failure, {})(engine)
            self.assertIs(caught.exception, original_error)
            self.assertIsNone(original_error.__context__)
            late, late_classes = Engine(), {"late_classes": True}
            def late_original(engine_self):
                self.assertIs(m._ACTIVE.get()["classes"], late_classes)
                return result
            with patch.object(m, "_arm_schedule", return_value=late_classes) as arm:
                late_wrapper = m._wrap_core(late_original)
                self.assertIs(late_wrapper(late), result)
                self.assertIs(late_wrapper(late), result)
                self.assertEqual(arm.call_count, 1)
                self.assertIsNone(m._ACTIVE.get())
            rejected, rejected_exception = Engine(), RuntimeError("original-after-late-reject")
            def rejected_original(engine_self):
                self.assertIsNone(m._ACTIVE.get())
                raise rejected_exception
            with patch.object(m, "_arm_schedule", side_effect=ValueError("not naturally loaded")) as arm:
                rejected_wrapper = m._wrap_core(rejected_original)
                for _ in range(2):
                    with self.assertRaises(RuntimeError) as caught:
                        rejected_wrapper(rejected)
                    self.assertIs(caught.exception, rejected_exception)
                    self.assertIsNone(rejected_exception.__context__)
                self.assertEqual(arm.call_count, 1)


if __name__ == "__main__":
    unittest.main()
