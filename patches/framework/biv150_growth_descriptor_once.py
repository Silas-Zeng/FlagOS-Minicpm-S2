"""One-shot CPU descriptors for an isolated diagnostic source, never a baseline.

Imported code is inert. Explicit install wraps constructor/allocation only to
observe original calls. The growth runtime and its source/eligibility guards
are not changed. No device query, request mutation, scheduling or RNG operation.
"""

from __future__ import annotations

import ast
import functools
import hashlib
import importlib
import json
import os
from pathlib import Path
import weakref


EXPECTED_GROWTH_SHA256 = "9245dd089a310620840a1c056544e66fb2dd0ea24f41ef8f0e4b22721bac7e49"
EXPECTED_INIT_SHA256 = "d9e2caf40f8d126ec4344b6c98605847f9b4be438eb9961a2eb3bb0f40671ef9"
_MARKER = "_biv150_growth_descriptor_once"
FOOTER = b"""
    # _biv150_growth_descriptor_once_general_plugin_v1
    from vllm_fl.patches.biv150_growth_descriptor_once import install as _install_growth_descriptor
    _install_growth_descriptor()
"""


def transform_source(source: bytes) -> bytes:
    """Pure bytes: apply only to a new isolated copy of exact growth init."""
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT_SHA256:
        raise RuntimeError("unaudited growth-descriptor plugin init")
    return source + FOOTER


def _type(value):
    return f"{type(value).__module__}.{type(value).__qualname__}"


def _scalar(value):
    if value is None or type(value) in (str, bool, int, float):
        return value
    return {"type": _type(value)}


def _emit(payload):
    # Diagnostics must never change a successful original call into a failure.
    try:
        print(json.dumps(payload, sort_keys=True), flush=True)
    except Exception:
        pass


def _ast_plan(growth):
    # Only the already hash-verified local runtime is parsed. No expression is
    # received from a request/log/environment or another untrusted source.
    tree = ast.parse(Path(growth.__file__).read_text(encoding="utf-8"))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_eligible")
    body = next(n for n in function.body if isinstance(n, ast.Try)).body
    setup = [(ast.unparse(n), compile(ast.Module(body=[n], type_ignores=[]),
                                     "trusted-growth-setup", "exec"))
             for n in body if isinstance(n, ast.Assign)]
    result = next(n.value for n in body if isinstance(n, ast.Return))
    if not isinstance(result, ast.BoolOp) or not isinstance(result.op, ast.And):
        raise RuntimeError("growth eligibility expression changed")
    checks = [(ast.unparse(n), compile(ast.Expression(body=n), "trusted-growth-guard", "eval"))
              for n in result.values]
    return setup, checks


def _constructor_report(scheduler, growth, setup, checks, classes, hashes):
    # Generator expressions resolve free names through eval globals. A shared
    # namespace avoids falsely reporting a missing parallel variable inside all().
    local = dict(growth._eligible.__globals__, scheduler=scheduler, full_spec_cls=classes[0],
                 coordinator_cls=classes[1], full_manager_cls=classes[2])
    setup_errors, guards = [], []
    for expression, code in setup:
        try:
            exec(code, local, local)
        except Exception as exc:
            setup_errors.append({"expression": expression, "error": repr(exc)})
    for expression, code in checks:
        item = {"expression": expression}
        try:
            item["passed"] = bool(eval(code, local, local))
        except Exception as exc:
            item.update(passed=False, error=repr(exc))
        guards.append(item)
    descriptors = {name + "_type": _type(local[name]) for name in
                   ("scheduler", "model", "parallel", "manager", "spec", "coordinator")
                   if name in local}
    groups = local.get("groups", ())
    try:
        descriptors["group_count"] = len(groups)
        descriptors["layer_count"] = len(groups[0].layer_names) if groups else None
    except Exception as exc:
        descriptors["group_descriptor_error"] = repr(exc)
    for name in ("use_v2_model_runner", "scheduler_reserve_full_isl", "block_size", "max_model_len"):
        descriptors[name] = _scalar(getattr(scheduler, name, "<missing>"))
    policy = getattr(scheduler, "policy", None)
    descriptors.update(policy_type=_type(policy), policy_value=_scalar(getattr(policy, "value", "<missing>")))
    spec = local.get("spec")
    descriptors["kv_spec"] = {name: (str(getattr(spec, name)) if name == "dtype" and hasattr(spec, name)
                                     else _scalar(getattr(spec, name, "<missing>")))
                               for name in ("block_size", "num_kv_heads", "head_size", "head_size_v",
                                            "dtype", "non_causal", "sliding_window", "attention_chunk_size")}
    # Preserve the original helper's result as well as individually evaluated
    # clauses; notably its early group-count condition is outside the AND.
    eligible = growth._eligible(scheduler, *classes)
    return dict(event="GROWTH_CONSTRUCTOR_DESCRIPTORS", pid=os.getpid(),
                eligible=eligible, setup_errors=setup_errors, guards=guards,
                descriptors=descriptors, source_sha256=hashes), eligible


def install():
    growth = importlib.import_module("vllm_fl.patches.biv150_growth_admission")
    if hashlib.sha256(Path(growth.__file__).read_bytes()).hexdigest() != EXPECTED_GROWTH_SHA256:
        raise RuntimeError("unaudited growth runtime for descriptor diagnostic")
    modules = {name: importlib.import_module(name) for name in growth.EXPECTED_SOURCES}
    hashes = {}
    for name, module in modules.items():
        digest = hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest()
        if digest != growth.EXPECTED_SOURCES[name]:
            raise RuntimeError("unaudited growth diagnostic dependency " + name)
        hashes[name] = digest
    hashes.update(growth_runtime=EXPECTED_GROWTH_SHA256,
                  diagnostic_module=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    scheduler_cls = modules["vllm.v1.core.sched.scheduler"].Scheduler
    manager_cls = modules["vllm.v1.core.kv_cache_manager"].KVCacheManager
    init, allocate = scheduler_cls.__init__, manager_cls.allocate_slots
    marked = (getattr(init, _MARKER, False), getattr(allocate, _MARKER, False))
    if all(marked):
        return {"installed": True, "already_installed": True}
    if any(marked):
        raise RuntimeError("partial descriptor diagnostic installation")
    if not (getattr(scheduler_cls.schedule, growth._MARKER, False)
            and getattr(allocate, growth._MARKER, False)):
        raise RuntimeError("diagnostic requires the installed audited growth wrappers")
    growth._require_original(init, modules["vllm.v1.core.sched.scheduler"], "Scheduler.__init__")
    classes = (importlib.import_module("vllm.v1.kv_cache_interface").FullAttentionSpec,
               modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator,
               modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager)
    status = importlib.import_module("vllm.v1.request").RequestStatus
    setup, checks = _ast_plan(growth)
    state = {"constructor": False, "allocation": False, "eligible": False, "scheduler": None}

    @functools.wraps(init)
    def diagnostic_init(scheduler, *args, **kwargs):
        result = init(scheduler, *args, **kwargs)
        if not state["constructor"]:
            state["constructor"] = True
            try:
                state["scheduler"] = weakref.ref(scheduler)
                payload, state["eligible"] = _constructor_report(
                    scheduler, growth, setup, checks, classes, hashes)
            except Exception as exc:
                payload = dict(event="GROWTH_CONSTRUCTOR_DIAGNOSTIC_ERROR", pid=os.getpid(), error=repr(exc))
            _emit(payload)
        return result

    @functools.wraps(allocate)
    def diagnostic_allocate(manager, request, count, *args, **kwargs):
        scheduler = state["scheduler"]() if state["scheduler"] is not None else None
        capture = (state["eligible"] and not state["allocation"] and scheduler is not None
                   and scheduler.kv_cache_manager is manager and bool(scheduler.running)
                   and request.status in (status.WAITING, status.PREEMPTED))
        if not capture:
            return allocate(manager, request, count, *args, **kwargs)
        state["allocation"] = True
        payload = dict(event="GROWTH_FIRST_WAITING_ALLOCATION", pid=os.getpid())
        try:
            payload.update(running_count=len(scheduler.running), num_new_tokens=_scalar(count),
                           request_status=str(request.status), positional_tail_count=len(args),
                           keyword_names=sorted(kwargs),
                           kwargs={k: _scalar(v) for k, v in kwargs.items() if k != "new_computed_blocks"},
                           request_fields={k: _scalar(getattr(request, k, "<missing>")) for k in
                               ("num_prompt_tokens", "max_tokens", "num_tokens", "num_computed_tokens",
                                "num_output_placeholders", "resumable", "use_structured_output",
                                "has_encoder_inputs", "pooling_params")}, stats_before=growth.stats())
            prefix = kwargs.get("new_computed_blocks")
            payload["new_computed_group_lengths"] = [len(g) for g in prefix.blocks] if prefix is not None else None
            payload["mm_feature_count"] = len(getattr(request, "mm_features", ()) or ())
        except Exception as exc:
            payload["diagnostic_read_error"] = repr(exc)
        try:
            result = allocate(manager, request, count, *args, **kwargs)
            payload["original_returned_blocks"] = result is not None
            return result
        except Exception as exc:
            payload["original_exception"] = repr(exc)
            raise
        finally:
            try:
                payload["stats_after"] = growth.stats()
            except Exception as exc:
                payload["diagnostic_stats_error"] = repr(exc)
            _emit(payload)

    setattr(diagnostic_init, _MARKER, True)
    setattr(diagnostic_allocate, _MARKER, True)
    scheduler_cls.__init__, manager_cls.allocate_slots = diagnostic_init, diagnostic_allocate
    return {"installed": True, "one_shot": True, "performance_evidence": False}
