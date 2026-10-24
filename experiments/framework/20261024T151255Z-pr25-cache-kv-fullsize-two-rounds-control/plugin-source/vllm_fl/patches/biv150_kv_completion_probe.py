"""Opt-in observations around actual KV failures; never changes scheduling.

The engine context adds only a counter/ContextVar on normal steps. Request,
queue and block descriptors are read only near failed RUNNING allocations,
preemption and a later successful resume. No future method, wait, CUDA call,
allocator, refcount or request field is changed. Snapshots are incomplete.
"""
from __future__ import annotations

import atexit
from contextvars import ContextVar
from functools import wraps
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import weakref


EXPECTED_SOURCES = {
    "vllm.v1.engine.core": "27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71",
    "vllm.v1.core.sched.scheduler": "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090",
    "vllm.v1.core.sched.async_scheduler": "da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884",
    "vllm.v1.core.kv_cache_manager": "2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320",
    "vllm.v1.core.kv_cache_coordinator": "9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b",
    "vllm.v1.core.single_type_kv_cache_manager": "22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914",
    "vllm.v1.core.block_pool": "3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe",
    "vllm.v1.request": "06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80",
}
EXPECTED_INIT = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
INIT_FOOTER = (b"\n    # _biv150_kv_completion_probe_v1\n"
               b"    from vllm_fl.patches.biv150_kv_completion_probe import install as _install_kv_completion_probe\n"
               b"    _install_kv_completion_probe(enabled=True)\n")
_MARKER = "_biv150_kv_completion_probe_v1"
_STATE = "_biv150_kv_completion_probe_state"
_ACTIVE = ContextVar("biv150_kv_completion_probe", default=None)
_REFERENCES = []


def transform_init(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT:
        raise RuntimeError("requires exact SQL+C3 general-plugin init")
    return source + INIT_FOOTER


def _emit(state, reason):
    try:
        print("BIV150_KV_COMPLETION_PROBE " + json.dumps({
            "pid": os.getpid(), "reason": reason, "workload_complete": False,
            "future_readiness_evaluated": False,
            "reclaim_coverage_is_capacity_hypothesis": True,
            "resume_gap_is_exposure_not_executed_gpu_work": True,
            **state["public"], **state["counts"],
        }, sort_keys=True), flush=True)
    except Exception:
        pass


def _observe(state, function, *args):
    try:
        return function(*args)
    except Exception:
        state["counts"]["observation_errors"] += 1
        return None


def _scope(engine, classes):
    try:
        config, scheduler = engine.vllm_config, engine.scheduler
        model, parallel = config.model_config, config.parallel_config
        text, manager = model.hf_text_config, scheduler.kv_cache_manager
        groups = manager.kv_cache_config.kv_cache_groups
        spec = groups[0].kv_cache_spec if len(groups) == 1 else None
        return (
            Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
            and str(model.dtype) == "torch.bfloat16" and model.quantization is None
            and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
                 text.num_key_value_heads) == (2048, 42, 16, 2)
            and all(getattr(parallel, key, None) == 1 for key in (
                "tensor_parallel_size", "pipeline_parallel_size",
                "decode_context_parallel_size", "data_parallel_size"))
            and parallel.use_ubatching is False and config.speculative_config is None
            and config.lora_config is None and engine.async_scheduling is True
            and type(scheduler) in classes["schedulers"]
            and scheduler.use_v2_model_runner is True
            and scheduler.defer_block_free is False and scheduler.has_mamba_layers is False
            and scheduler.connector is None and scheduler.ec_connector is None
            and scheduler.num_lookahead_tokens == 0
            and scheduler.policy.name == "FCFS" and scheduler.block_size == 16
            and type(manager) is classes["manager"]
            and type(manager.coordinator) is classes["coordinator"]
            and len(manager.coordinator.single_type_managers) == 1
            and type(manager.coordinator.single_type_managers[0]) is classes["full_manager"]
            and type(spec) is classes["full_spec"]
            and len(groups[0].layer_names) == 42
            and spec.block_size == 16 and str(spec.dtype) == "torch.bfloat16"
            and spec.num_kv_heads == 2 and spec.head_size == 128
        )
    except Exception:
        return False


def _state(engine, classes):
    state = getattr(engine, _STATE, None)
    if state is None:
        names = ("core_calls", "schedule_calls", "running_allocation_failures",
                 "failure_steps", "failure_with_terminal_frame", "reclaim_covers_deficit_events",
                 "preemptions", "resumed_requests", "resumed_cache_hit_tokens",
                 "resumed_processed_prefix_floor_tokens", "resumed_prefix_gap_exposure_tokens",
                 "dropped_pending_lifecycles", "observation_errors")
        state = {"counts": dict.fromkeys(names, 0), "pending": {}, "last_failed_step": None,
                 "eligible": _scope(engine, classes), "public": {}}
        state["public"] = {"eligible": state["eligible"],
                           "batch_queue_enabled": engine.batch_queue is not None,
                           "batch_queue_capacity": engine.batch_queue_size}
        setattr(engine, _STATE, state)
        _REFERENCES.append(weakref.ref(engine))
        _emit(state, "first_checked")
    return state


def _queue(engine):
    return tuple(engine.batch_queue) if engine.batch_queue is not None else ()


def _failure(frame, manager, request, num_new_tokens):
    state, engine = frame["state"], frame["engine"]
    counts = state["counts"]
    counts["running_allocation_failures"] += 1
    if state["last_failed_step"] != counts["schedule_calls"]:
        state["last_failed_step"] = counts["schedule_calls"]
        counts["failure_steps"] += 1
    main_tokens = request.num_computed_tokens + num_new_tokens
    needed = manager.coordinator.get_num_blocks_to_allocate(
        request_id=request.request_id, num_tokens=min(main_tokens, manager.max_model_len),
        new_computed_blocks=manager.empty_kv_cache_blocks.blocks, num_encoder_tokens=0,
        total_computed_tokens=request.num_computed_tokens,
        num_tokens_main_model=main_tokens)
    free = manager.block_pool.get_num_free_blocks()
    queued = _queue(engine)
    queued_ids = {rid for _, output, _ in queued for rid in output.num_scheduled_tokens}
    terminal = [r for r in engine.scheduler.running
                if r.num_output_placeholders > 0
                and r.num_computed_tokens + 2 - r.num_output_placeholders
                >= r.num_prompt_tokens + r.max_tokens
                and r.request_id in queued_ids]
    blocks = manager.coordinator.single_type_managers[0].req_to_blocks
    private = {block.block_id for r in terminal for block in blocks.get(r.request_id, ())
               if block.ref_cnt == 1 and not block.is_null}
    deficit = max(0, needed - free)
    counts["failure_with_terminal_frame"] += int(bool(terminal))
    counts["reclaim_covers_deficit_events"] += int(deficit > 0 and len(private) >= deficit)
    if "first_failure" not in state["public"]:
        state["public"]["first_failure"] = {
            "free_blocks": free, "required_new_blocks": needed, "deficit_blocks": deficit,
            "queued_frames": len(queued), "terminal_pending_requests": len(terminal),
            "terminal_single_ref_private_blocks": len(private)}
        _emit(state, "first_running_allocation_failure")


def _preempt_snapshot(engine, request):
    # Subtract every already-queued input span, even if its future may be ready.
    # This conservative floor never calls future.done/result or waits for it.
    inflight = sum(output.num_scheduled_tokens.get(request.request_id, 0)
                   for _, output, _ in _queue(engine))
    issued = request.num_computed_tokens
    return {"request": request, "processed_prefix_floor":
            max(0, min(issued - inflight, request.num_tokens))}


def _resumes(frame, output):
    state, scheduler = frame["state"], frame["engine"].scheduler
    pending = state["pending"]
    starts = [(r.req_id, r.num_computed_tokens) for r in output.scheduled_new_reqs]
    cached = output.scheduled_cached_reqs
    starts.extend(zip(cached.req_ids, cached.num_computed_tokens))
    for rid, prefix in starts:
        item = pending.get(rid)
        if item is None:
            continue
        if scheduler.requests.get(rid) is not item["request"]:
            state["counts"]["dropped_pending_lifecycles"] += 1
        else:
            floor = item["processed_prefix_floor"]
            state["counts"]["resumed_requests"] += 1
            state["counts"]["resumed_cache_hit_tokens"] += prefix
            state["counts"]["resumed_processed_prefix_floor_tokens"] += floor
            state["counts"]["resumed_prefix_gap_exposure_tokens"] += max(0, floor - prefix)
        del pending[rid]


def _prune(frame):
    state, requests = frame["state"], frame["engine"].scheduler.requests
    for rid, item in tuple(state["pending"].items()):
        if requests.get(rid) is not item["request"]:
            del state["pending"][rid]
            state["counts"]["dropped_pending_lifecycles"] += 1


def _wrap_core(original, classes):
    @wraps(original)
    def core(self, *args, **kwargs):
        if _ACTIVE.get() is not None:
            return original(self, *args, **kwargs)
        try:
            state = _state(self, classes)
        except Exception:
            return original(self, *args, **kwargs)
        if not state["eligible"]:
            return original(self, *args, **kwargs)
        state["counts"]["core_calls"] += 1
        frame = {"engine": self, "state": state}
        token = _ACTIVE.set(frame)
        try:
            return original(self, *args, **kwargs)
        finally:
            _ACTIVE.reset(token)
            if state["pending"]:
                _observe(state, _prune, frame)
            if state["counts"]["core_calls"] % 64 == 0:
                _emit(state, "periodic")
    return core


def _wrap_schedule(original):
    @wraps(original)
    def schedule(self, *args, **kwargs):
        frame = _ACTIVE.get()
        active = frame is not None and frame["engine"].scheduler is self
        if active:
            frame["state"]["counts"]["schedule_calls"] += 1
        result = original(self, *args, **kwargs)
        if active and frame["state"]["pending"]:
            _observe(frame["state"], _resumes, frame, result)
        return result
    return schedule


def _wrap_allocate(original):
    @wraps(original)
    def allocate(self, request, num_new_tokens, *args, **kwargs):
        result = original(self, request, num_new_tokens, *args, **kwargs)
        frame = _ACTIVE.get()
        if result is None and frame is not None and frame["engine"].scheduler.kv_cache_manager is self:
            def observe_failure():
                if request.status.name == "RUNNING":
                    _failure(frame, self, request, num_new_tokens)
            _observe(frame["state"], observe_failure)
        return result
    return allocate


def _wrap_preempt(original):
    @wraps(original)
    def preempt(self, request, *args, **kwargs):
        frame = _ACTIVE.get()
        active = frame is not None and frame["engine"].scheduler is self
        item = _observe(frame["state"], _preempt_snapshot, frame["engine"], request) if active else None
        result = original(self, request, *args, **kwargs)
        if active:
            def record_preemption():
                frame["state"]["counts"]["preemptions"] += 1
                if item is not None:
                    frame["state"]["pending"][request.request_id] = item
            _observe(frame["state"], record_preemption)
        return result
    return preempt


def _at_exit():
    for reference in _REFERENCES:
        try:
            engine = reference()
            if engine is not None:
                _emit(getattr(engine, _STATE), "process_exit")
        except Exception:
            pass


def install(*, enabled=False):
    if enabled is not True:
        return False
    modules = {name: importlib.import_module(name) for name in EXPECTED_SOURCES}
    core = modules["vllm.v1.engine.core"].EngineCore
    if getattr(core, _MARKER, False):
        return False
    for name, expected in EXPECTED_SOURCES.items():
        if hashlib.sha256(Path(modules[name].__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("unaudited KV completion probe source: " + name)
    scheduler = modules["vllm.v1.core.sched.scheduler"].Scheduler
    manager = modules["vllm.v1.core.kv_cache_manager"].KVCacheManager
    classes = {
        "schedulers": (scheduler, modules["vllm.v1.core.sched.async_scheduler"].AsyncScheduler),
        "manager": manager,
        "coordinator": modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator,
        "full_manager": modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager,
        "full_spec": importlib.import_module("vllm.v1.kv_cache_interface").FullAttentionSpec,
    }
    targets = ((core, "step"), (core, "step_with_batch_queue"),
               (scheduler, "schedule"), (scheduler, "_preempt_request"), (manager, "allocate_slots"))
    originals = [getattr(cls, name) for cls, name in targets]
    for (cls, _), function in zip(targets, originals):
        module = modules[cls.__module__]
        if inspect.unwrap(function) is not function or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve():
            raise RuntimeError("unexpected pre-existing KV probe method wrapper")
    wrappers = (_wrap_core(originals[0], classes), _wrap_core(originals[1], classes),
                _wrap_schedule(originals[2]), _wrap_preempt(originals[3]), _wrap_allocate(originals[4]))
    for (cls, name), function in zip(targets, wrappers):
        setattr(cls, name, function)
    setattr(core, _MARKER, True)
    atexit.register(_at_exit)
    print("BIV150_KV_COMPLETION_PROBE_INSTALLED pid=" + str(os.getpid()) + " scheduling_changed=0", flush=True)
    return True
