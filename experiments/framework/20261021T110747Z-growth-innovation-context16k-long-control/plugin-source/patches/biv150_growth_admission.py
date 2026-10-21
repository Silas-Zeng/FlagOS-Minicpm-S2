"""Opt-in MiniCPM output-growth admission gate; no persistent reservation ledger.

Only the audited scheduler's WAITING allocation may be declined. All running
allocations, KV ownership/mutations, queue operations and sampler work remain
in their original implementations. Install explicitly in the EngineCore process
before constructing its scheduler, not in a GPU worker's model-runner footer.
"""

from __future__ import annotations

from contextvars import ContextVar
import functools
import hashlib
import importlib
import os
from pathlib import Path


EXPECTED_SOURCES = {
    "vllm.v1.core.sched.scheduler": "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090",
    "vllm.v1.core.kv_cache_manager": "2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320",
    "vllm.v1.core.block_pool": "3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe",
    "vllm.v1.core.kv_cache_coordinator": "9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b",
    "vllm.v1.core.single_type_kv_cache_manager": "22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914",
}
_MARKER = "_biv150_growth_admission"
_SCHEDULER = ContextVar("biv150_growth_admission_scheduler", default=None)
_STATS = {"checked": 0, "deferred": 0}


def stats():
    return dict(_STATS)


def _fallback(reason):
    key = "fallback_" + reason
    _STATS[key] = _STATS.get(key, 0) + 1
    return None


def _eligible(scheduler, full_spec_cls, coordinator_cls, full_manager_cls):
    """Descriptor-only checks: no tensor reads, allocation, imports or device calls."""
    try:
        config = scheduler.vllm_config
        model, parallel = config.model_config, config.parallel_config
        text = model.hf_text_config
        manager = scheduler.kv_cache_manager
        groups = manager.kv_cache_config.kv_cache_groups
        if len(groups) != 1:
            return False
        spec = groups[0].kv_cache_spec
        coordinator = manager.coordinator
        return (
            Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
            and str(model.dtype) == "torch.bfloat16"
            and (text.hidden_size, text.num_hidden_layers,
                 text.num_attention_heads, text.num_key_value_heads) == (2048, 42, 16, 2)
            and all(getattr(parallel, name, None) == 1 for name in (
                "tensor_parallel_size", "pipeline_parallel_size", "data_parallel_size",
                "decode_context_parallel_size", "prefill_context_parallel_size"))
            and not parallel.use_ubatching
            and config.speculative_config is None
            and config.lora_config is None
            and not config.cache_config.kv_sharing_fast_prefill
            and not scheduler.is_encoder_decoder
            and not scheduler.has_mamba_layers
            and not scheduler.use_v2_model_runner
            and scheduler.connector is None
            and scheduler.ec_connector is None
            and scheduler.scheduler_reserve_full_isl is True
            and scheduler.num_lookahead_tokens == 0
            and scheduler.policy.value == "fcfs"
            and manager.max_model_len == scheduler.max_model_len
            and type(spec) is full_spec_cls
            and (spec.block_size, spec.num_kv_heads, spec.head_size,
                 spec.head_size_v) == (16, 2, 128, 128)
            and str(spec.dtype) == "torch.bfloat16"
            and spec.sliding_window is None
            and spec.attention_chunk_size is None
            and spec.non_causal is False
            and len(groups[0].layer_names) == 42
            and scheduler.block_size == 16
            and type(coordinator) is coordinator_cls
            and len(coordinator.single_type_managers) == 1
            and type(coordinator.single_type_managers[0]) is full_manager_cls
            and coordinator.single_type_managers[0]._max_admission_blocks_per_request is None
        )
    except (AttributeError, TypeError, ValueError):
        return False


def _future_tokens(request, max_model_len):
    # Request.max_tokens is the validated API generation cap, not a benchmark
    # constant. Include already scheduled async placeholders if they extend
    # beyond that cap. No request field is changed.
    fields = (request.num_prompt_tokens, request.max_tokens, request.num_tokens,
              request.num_computed_tokens, request.num_output_placeholders)
    if any(type(value) is not int or value < 0 for value in fields):
        return None
    prompt, maximum, current, computed, placeholders = fields
    if (prompt == 0 or maximum == 0 or current < prompt
            or current > max_model_len or computed > max_model_len
            or request.resumable or request.use_structured_output
            or request.has_encoder_inputs or request.mm_features
            or request.pooling_params is not None):
        return None
    return min(max_model_len, max(prompt + maximum, current + placeholders, computed))


def _remaining_blocks(manager, request, future, new_blocks, total_computed):
    # The audited predictor includes ref_cnt==0 cached blocks that a prefix
    # touch will remove from the free queue; already allocated/preallocated
    # blocks are subtracted, and shared referenced prefix blocks are not charged
    # twice. Never apply the recycling admission cap to a future-length budget.
    return manager.coordinator.get_num_blocks_to_allocate(
        request_id=request.request_id,
        num_tokens=future,
        new_computed_blocks=new_blocks,
        num_encoder_tokens=0,
        total_computed_tokens=total_computed,
        num_tokens_main_model=future,
        apply_admission_cap=False,
    )


def _growth_demand(scheduler, request, kwargs, running_status):
    """Return (free, required) or None for original allocation; never mutate KV."""
    manager = scheduler.kv_cache_manager
    running = scheduler.running
    # A finite set of running requests can drain. Once empty the original
    # scheduler can always try the FCFS head, including oversized/odd requests.
    # No stale request-ID reservation can survive completion or cancellation.
    if not running:
        return _fallback("empty_running")
    if any(kwargs.get(name, 0) != 0 for name in (
            "num_lookahead_tokens", "num_external_computed_tokens", "num_encoder_tokens",
            "reserved_blocks")) or kwargs.get("delay_cache_blocks", False):
        return _fallback("allocation_scope")
    capacity = manager.block_pool.num_gpu_blocks - 1  # original null block
    required = manager.watermark_blocks
    seen = set()
    for active in (*running, request):
        if active.request_id in seen:
            return _fallback("duplicate_request")
        seen.add(active.request_id)
        if active is not request and active.status != running_status:
            return _fallback("running_status")
        future = _future_tokens(active, scheduler.max_model_len)
        if future is None:
            return _fallback("request_scope")
        if (future + scheduler.block_size - 1) // scheduler.block_size > capacity:
            return _fallback("oversized_future")
        prefix = kwargs.get("new_computed_blocks") if active is request else None
        new_blocks = (manager.empty_kv_cache_blocks.blocks
                      if prefix is None else prefix.blocks)
        computed = active.num_computed_tokens
        if active is request:
            computed += kwargs.get("num_new_computed_tokens", 0)
        required += _remaining_blocks(manager, active, future, new_blocks, computed)
    return manager.block_pool.get_num_free_blocks(), required


def _wrap_allocate(original, waiting_statuses, running_status):
    @functools.wraps(original)
    def allocate_slots(manager, request, num_new_tokens, *args, **kwargs):
        scheduler = _SCHEDULER.get()
        if (scheduler is not None and scheduler.kv_cache_manager is manager
                and request.status in waiting_statuses and not args
                and kwargs.get("full_sequence_must_fit") is True):
            try:
                demand = _growth_demand(scheduler, request, kwargs, running_status)
            except (AttributeError, TypeError, ValueError):
                demand = _fallback("unknown_state")
            if demand is not None:
                _STATS["checked"] += 1
                free, required = demand
                if _STATS["checked"] == 1:
                    print("BIV150_GROWTH_ADMISSION_FIRST_CHECKED "
                          f"pid={os.getpid()} free_blocks={free} future_blocks={required}",
                          flush=True)
                if required > free:
                    _STATS["deferred"] += 1
                    if _STATS["deferred"] == 1:
                        print("BIV150_GROWTH_ADMISSION_FIRST_DEFERRED "
                              f"free_blocks={free} future_blocks={required}", flush=True)
                    # The original WAITING loop breaks on None. No pop/reorder
                    # occurs and no already selected RUNNING request is changed.
                    return None
        return original(manager, request, num_new_tokens, *args, **kwargs)
    setattr(allocate_slots, _MARKER, True)
    return allocate_slots


def _wrap_schedule(original, full_spec_cls, coordinator_cls, full_manager_cls):
    @functools.wraps(original)
    def schedule(scheduler, *args, **kwargs):
        token = _SCHEDULER.set(
            scheduler if _eligible(scheduler, full_spec_cls, coordinator_cls, full_manager_cls)
            else None)
        try:
            return original(scheduler, *args, **kwargs)
        finally:
            _SCHEDULER.reset(token)
    setattr(schedule, _MARKER, True)
    return schedule


def _require_original(function, module, qualname):
    if (getattr(function, "__module__", None) != module.__name__
            or getattr(function, "__qualname__", None) != qualname
            or hasattr(function, "__wrapped__")
            or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
        raise RuntimeError(f"growth-admission refuses replaced dependency {qualname}")


def install(*, enabled=False):
    """Explicit code opt-in; default off even when this module is imported."""
    if enabled is not True:
        return {"installed": False, "reason": "disabled by default"}
    platform = importlib.import_module("vllm.platforms").current_platform
    if getattr(platform, "vendor_name", None) != "iluvatar":
        return {"installed": False, "reason": "non-iluvatar"}
    modules = {name: importlib.import_module(name) for name in EXPECTED_SOURCES}
    for name, module in modules.items():
        actual = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        if actual != EXPECTED_SOURCES[name]:
            raise RuntimeError(f"unaudited growth-admission source {name}: {actual}")
    scheduler_cls = modules["vllm.v1.core.sched.scheduler"].Scheduler
    manager_cls = modules["vllm.v1.core.kv_cache_manager"].KVCacheManager
    old_schedule, old_allocate = scheduler_cls.schedule, manager_cls.allocate_slots
    marked = (getattr(old_schedule, _MARKER, False), getattr(old_allocate, _MARKER, False))
    if any(marked):
        if not all(marked):
            raise RuntimeError("partial growth-admission installation")
        return {"installed": True, "already_installed": True}
    _require_original(old_schedule, modules["vllm.v1.core.sched.scheduler"], "Scheduler.schedule")
    _require_original(old_allocate, modules["vllm.v1.core.kv_cache_manager"], "KVCacheManager.allocate_slots")
    if old_schedule.__globals__["KVCacheManager"] is not manager_cls:
        raise RuntimeError("growth-admission refuses mismatched scheduler manager alias")
    status = importlib.import_module("vllm.v1.request").RequestStatus
    full_spec = importlib.import_module("vllm.v1.kv_cache_interface").FullAttentionSpec
    coordinator = modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator
    full_manager = modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager
    manager_cls.allocate_slots = _wrap_allocate(
        old_allocate, (status.WAITING, status.PREEMPTED), status.RUNNING)
    scheduler_cls.schedule = _wrap_schedule(old_schedule, full_spec, coordinator, full_manager)
    print("BIV150_GROWTH_ADMISSION_INSTALLED opt_in=1 future_output_budget=1", flush=True)
    return {"installed": True, "persistent_reservations": False,
            "scope": "single-group BF16 MiniCPM FCFS waiting admissions only",
            "sources": dict(EXPECTED_SOURCES)}
