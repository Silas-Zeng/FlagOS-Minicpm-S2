"""默认关闭：原RUNNING分配失败后、原victim选择前一次CPU描述符快照。"""
from collections import deque
from contextvars import ContextVar
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap
from types import FunctionType
import weakref

from . import biv150_kv_completion_probe as scope_probe

EXPECTED_SCOPE = "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6"
EXPECTED_INIT = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
EXPECTED_RUNNER = "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"
EXPECTED_SCHEDULE = "87a6016cdb08ae0d5bdb3fc2c14cb6974467a76b58d0ed41c35aadf1b697a8dd"
EXTRA_SOURCES = {
    "vllm.v1.kv_cache_interface": "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003",
    "vllm.v1.core.sched.output": "f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d",
}
INIT_FOOTER = (b"\n    # _biv150_preemption_snapshot_v1\n"
               b"    from vllm_fl.patches.biv150_preemption_snapshot import install as _install_preemption_snapshot\n"
               b"    _install_preemption_snapshot(enabled=True)\n")
ANCHOR = ("                # The request cannot be scheduled.\n"
          "                # Preempt the lowest-priority request.\n")
INSERTION = ("                _biv150_capture_running_failure(self, request, num_new_tokens, "
             "token_budget, req_index, num_scheduled_tokens)\n")
_ACTIVE = ContextVar("biv150_preemption_snapshot", default=None)
_STATES = weakref.WeakKeyDictionary()
_INSTALLED = False


def transform_init(source):
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT:
        raise RuntimeError("只接受原stable e043 init，不叠现有候选")
    return source + INIT_FOOTER


def transform_schedule(source):
    if hashlib.sha256(source.encode()).hexdigest() != EXPECTED_SCHEDULE or source.count(ANCHOR) != 1:
        raise RuntimeError("只接受exact df780原schedule方法")
    changed = source.replace(ANCHOR, INSERTION + ANCHOR)
    if changed.count(INSERTION) != 1 or changed.replace(INSERTION, "", 1) != source:
        raise RuntimeError("单callback逆变换不符")
    return changed


def _emit(event, **fields):
    try:
        print("BIV150_PREEMPTION_SNAPSHOT " + json.dumps({"event": event, "pid": os.getpid(),
              "observational_only": True, "gpu_values_read": False, "future_readiness_evaluated": False,
              "victim_policy_changed": False, **fields}, sort_keys=True), flush=True)
    except Exception:
        pass


def _integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("非预期的CPU整数描述符")
    return value


def _token_counts(value):
    if type(value) is not dict or any(type(k) is not str or type(v) is not int or v < 0 for k, v in value.items()):
        raise ValueError("不支持的scheduled token映射")
    return dict(value)


def _snapshot(frame, scheduler, failed_request, num_new_tokens, token_budget, req_index, scheduled):
    engine, classes = frame["engine"], frame["classes"]
    running = tuple(scheduler.running)
    if (not running or running[req_index] is not failed_request
            or any(type(r) is not classes["request"] or r.status is not classes["request_status"].RUNNING for r in running)
            or type(engine.batch_queue) is not deque):
        raise ValueError("非actual RUNNING队列/请求/异步队列")
    scheduled = _token_counts(scheduled)
    queued, spans = [], {}
    for index, entry in enumerate(engine.batch_queue):
        if type(entry) is not tuple or len(entry) != 3 or type(entry[1]) is not classes["output"]:
            raise ValueError("未知queued frame，不能默认为0")
        counts = _token_counts(entry[1].num_scheduled_tokens)
        queued.append({"deque_index": index, "output_object_id": id(entry[1]), "scheduled_tokens": counts})
        for rid, count in counts.items():
            spans[rid] = spans.get(rid, 0) + count
    manager = scheduler.kv_cache_manager
    single = manager.coordinator.single_type_managers[0]
    rows = []
    for index, request in enumerate(running):
        rid = request.request_id
        if type(rid) is not str or scheduler.requests.get(rid) is not request:
            raise ValueError("request对象生命周期不符")
        issued = _integer(request.num_computed_tokens)
        known = _integer(request.num_tokens)
        output = _integer(request.num_output_tokens)
        prompt = _integer(request.num_prompt_tokens)
        maximum = _integer(request.max_tokens)
        outstanding = spans.get(rid, 0)
        stable = max(0, min(issued - outstanding, known - 1))
        prefix = stable // 16 * 16
        blocks = single.req_to_blocks.get(rid)
        if type(blocks) is not list:
            raise ValueError("缺原owned list，不能伪造空列表")
        ids, private, shared, hashed, null = set(), set(), set(), set(), 0
        for block in blocks:
            bid, ref = _integer(block.block_id), _integer(block.ref_cnt)
            if block.is_null:
                null += 1
                continue
            ids.add(bid)
            if ref == 1:
                private.add(bid)
            if ref > 1:
                shared.add(bid)
            if block.block_hash is not None:
                hashed.add(bid)
        prefix_blocks = blocks[:prefix // 16]
        coverage = (prefix >= 16 and len(prefix_blocks) == prefix // 16
                    and all(not b.is_null for b in prefix_blocks)
                    and len({b.block_id for b in prefix_blocks}) == prefix // 16)
        rows.append({"running_index": index, "request_id": rid, "request_object_id": id(request),
            "prompt_tokens": prompt, "legal_max_output_tokens": maximum, "confirmed_output_tokens": output,
            "remaining_output_upper_bound": max(0, maximum - output), "known_tokens": known,
            "issued_computed_tokens": issued, "output_placeholders": _integer(request.num_output_placeholders),
            "queued_scheduled_span": outstanding, "stable_prefix_floor_tokens": stable,
            "current_schedule_tokens_not_yet_issued": scheduled.get(rid, 0),
            "num_preemptions": _integer(request.num_preemptions),
            "next_decode_eligible_step": _integer(request.next_decode_eligible_step),
            "is_prefill_chunk": request.is_prefill_chunk, "owned_logical_pages": len(blocks),
            "owned_nonnull_unique_pages": len(ids), "private_single_ref_unique_pages": len(private),
            "shared_unique_pages": len(shared), "hashed_unique_pages": len(hashed), "null_page_references": null,
            "snapshot_prefix_tokens": prefix, "snapshot_payload_bytes": prefix * 43008,
            "snapshot_logical_page_coverage": coverage, "snapshot_payload_within_1gib": prefix >= 16 and prefix * 43008 <= 1 << 30,
            "nonstreaming": request.resumable is False and request.streaming_queue is None})
    # exact FullAttention RUNNING fast path：无new prefix/encoder/lookahead/watermark，纯整数同原需求。
    rid = failed_request.request_id
    if rid not in single.num_cached_block:
        raise ValueError("失败请求不在原RUNNING predictor fast path")
    free = _integer(manager.block_pool.free_block_queue.num_free_blocks)
    slots = min(min(_integer(failed_request.num_computed_tokens), manager.max_model_len)
                + _integer(num_new_tokens, 1), manager.max_model_len)
    required = max((slots + 15) // 16 - len(single.req_to_blocks[rid]), 0)
    return {"complete": True, "running": rows, "running_count": len(rows),
        "failed_request_id": rid, "failed_running_index": _integer(req_index),
        "failed_num_new_tokens": num_new_tokens, "token_budget_at_failure": _integer(token_budget),
        "current_scheduled_tokens": scheduled, "queued_frames": queued,
        "original_tail_victim_request_id": running[-1].request_id,
        "free_blocks": free, "required_new_blocks_derived_from_exact_fast_path": required,
        "required_blocks_direct_allocator_sample": False, "failure_matches_derived_deficit": required > free,
        "host_headroom_observed": False, "save_success_predicted": False,
        "limits": ["仅一次CPU诊断快照，页遍历/日志开销不作性能测量。", "computed减queued是真下界；本schedule尚未issued的tokens只单列，不再扣。",
                   "remaining是合法max上界，非EOS或完成时间预测。", "1GiB只payload cap，不证明pinned余量/可成功SAVE。",
                   "私有页数量按唯一物理页，不乘42；原victim选择与调度返回不变。"]}


def _capture_running_failure(scheduler, request, num_new_tokens, token_budget, req_index, scheduled):
    frame = _ACTIVE.get()
    if frame is None or frame["engine"].scheduler is not scheduler or frame["state"]["attempted"]:
        return
    frame["state"]["attempted"] = True
    try:
        payload = _snapshot(frame, scheduler, request, num_new_tokens, token_budget, req_index, scheduled)
        _emit("FIRST_RUNNING_FAILURE", **payload)
    except Exception as error:
        _emit("SNAPSHOT_INCOMPLETE", complete=False, error_type=type(error).__name__, error=str(error)[:300])


def _wrap_core(original, classes):
    @wraps(original)
    def step(self, *args, **kwargs):
        try:
            state = _STATES.get(self)
            if state is None:
                state = {"eligible": scope_probe._scope(self, classes) and type(self.batch_queue) is deque,
                         "attempted": False}
                _STATES[self] = state
                _emit("FIRST_CHECKED", eligible=state["eligible"])
        except Exception as error:
            _emit("SCOPE_INCOMPLETE", complete=False, error_type=type(error).__name__)
            state = None
        if state is None:
            # 原方法必须在except块结束后调用，不给原异常添观察异常作为__context__。
            return original(self, *args, **kwargs)
        if not state["eligible"] or state["attempted"]:
            return original(self, *args, **kwargs)
        token = _ACTIVE.set({"engine": self, "state": state, "classes": classes})
        try:
            return original(self, *args, **kwargs)
        finally:
            _ACTIVE.reset(token)
    return step


def install(*, enabled=False):
    global _INSTALLED
    if enabled is not True or _INSTALLED:
        return False
    try:
        if hashlib.sha256(Path(scope_probe.__file__).read_bytes()).hexdigest() != EXPECTED_SCOPE:
            raise RuntimeError("scope helper非冻结a4de")
        plugin = sys.modules.get("vllm_fl")
        init = Path(plugin.__file__).read_bytes() if plugin else b""
        if not init.endswith(INIT_FOOTER) or hashlib.sha256(init[:-len(INIT_FOOTER)]).hexdigest() != EXPECTED_INIT:
            raise RuntimeError("只接受stable init完整末尾append")
        if hashlib.sha256((Path(plugin.__file__).parent / "worker/model_runner.py").read_bytes()).hexdigest() != EXPECTED_RUNNER:
            raise RuntimeError("只接受原e155 runner")
        modules = {name: sys.modules.get(name) for name in {**scope_probe.EXPECTED_SOURCES, **EXTRA_SOURCES}}
        for name, expected in {**scope_probe.EXPECTED_SOURCES, **EXTRA_SOURCES}.items():
            module = modules[name]
            if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
                raise RuntimeError("自然加载源缺失/不符：" + name)
        core, scheduler = modules["vllm.v1.engine.core"].EngineCore, modules["vllm.v1.core.sched.scheduler"].Scheduler
        async_scheduler = modules["vllm.v1.core.sched.async_scheduler"].AsyncScheduler
        manager_class = modules["vllm.v1.core.kv_cache_manager"].KVCacheManager
        original, core_original = scheduler.schedule, core.step_with_batch_queue
        for method, module_name, qualname in ((original, scheduler.__module__, "Scheduler.schedule"),
                                             (core_original, core.__module__, "EngineCore.step_with_batch_queue"),
                                             (scheduler._preempt_request, scheduler.__module__, "Scheduler._preempt_request"),
                                             (manager_class.allocate_slots, manager_class.__module__, "KVCacheManager.allocate_slots")):
            if (not isinstance(method, FunctionType) or inspect.unwrap(method) is not method
                    or method.__code__.co_freevars or method.__qualname__ != qualname
                    or Path(method.__code__.co_filename).resolve() != Path(modules[module_name].__file__).resolve()):
                raise RuntimeError("原方法被包裹/身份不符")
        if async_scheduler.schedule is not original:
            raise RuntimeError("Async原schedule继承改变")
        source = textwrap.dedent(inspect.getsource(original))
        changed = transform_schedule(source)
        namespace = dict(original.__globals__)
        namespace["_biv150_capture_running_failure"] = _capture_running_failure
        exec(compile(changed, "<biv150-preemption-snapshot-schedule>", "exec"), namespace)
        classes = {"schedulers": (scheduler, async_scheduler), "manager": modules["vllm.v1.core.kv_cache_manager"].KVCacheManager,
            "coordinator": modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator,
            "full_manager": modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager,
            "full_spec": modules["vllm.v1.kv_cache_interface"].FullAttentionSpec,
            "request": modules["vllm.v1.request"].Request, "request_status": modules["vllm.v1.request"].RequestStatus,
            "output": modules["vllm.v1.core.sched.output"].SchedulerOutput}
        wrapped_core = _wrap_core(core_original, classes)
        scheduler.schedule, core.step_with_batch_queue = namespace["schedule"], wrapped_core
        _INSTALLED = True
        _emit("INSTALLED", schedule_source_sha256=EXPECTED_SCHEDULE, source_reverse_exact=True, default_enabled=False)
        return True
    except Exception as error:
        _emit("REJECTED", error_type=type(error).__name__, error=str(error)[:300])
        return False
