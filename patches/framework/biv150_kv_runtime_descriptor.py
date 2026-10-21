"""Opt-in, once-only CPU metadata observations; no tensor values or GPU calls."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import wraps
import hashlib
import importlib
import inspect
import json
import math
import os
from pathlib import Path
import sys
import weakref

EXPECTED_INIT = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
INIT_FOOTER = (
    b"\n    # _biv150_kv_runtime_descriptor_v1\n"
    b"    from vllm_fl.patches.biv150_kv_runtime_descriptor import install as _install_kv_runtime_descriptor\n"
    b"    _install_kv_runtime_descriptor(enabled=True)\n"
)
EXPECTED_SOURCES = {
    "vllm.v1.engine.core": "27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71",
    "vllm.v1.executor.abstract": "419002195d13cf050c3ea9705d18a12456c890c27c470a1efadce7de27ded0b1",
    "vllm.v1.executor.uniproc_executor": "4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe",
    "vllm.v1.worker.worker_base": "7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe",
    "vllm_fl.worker.worker": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
    "vllm_fl.worker.model_runner": "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1",
}
ENV_DIRECTORY = "BIV150_KV_DESCRIPTOR_DIR"
MARKER = "BIV150_KV_RUNTIME_DESCRIPTOR"
_SEEN_CORE = weakref.WeakSet()
_SEEN_WORKER = weakref.WeakSet()
_INSTALLED = False
_SERIAL = 0


def transform_init(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT:
        raise RuntimeError("requires exact 080656 init; no candidate stacking")
    return source + INIT_FOOTER


def _dict(obj):
    # Do not invoke executor/proxy __getattr__, RPC, properties or GC scans.
    try:
        value = object.__getattribute__(obj, "__dict__")
        return value if type(value) is dict else {}
    except (AttributeError, TypeError):
        return {}


def _class(obj):
    if obj is None:
        return {"status": "unobserved"}
    cls = type(obj)
    return {"status": "observed_local_reference", "module": cls.__module__,
            "qualname": cls.__qualname__, "object_id_in_this_pid": id(obj)}


def _scope(config):
    try:
        model, parallel = config.model_config, config.parallel_config
        text = model.hf_text_config
        return (
            Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
            and str(model.dtype) == "torch.bfloat16" and model.quantization is None
            and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
                 text.num_key_value_heads) == (2048, 42, 16, 2)
            and all(getattr(parallel, name, None) == 1 for name in (
                "tensor_parallel_size", "pipeline_parallel_size",
                "decode_context_parallel_size", "data_parallel_size"))
            and parallel.use_ubatching is False
            and config.speculative_config is None and config.lora_config is None
            and config.kv_transfer_config is None and config.ec_transfer_config is None
        )
    except Exception:
        return False


def _cgroup():
    paths = ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max",
             "/sys/fs/cgroup/memory/memory.usage_in_bytes",
             "/sys/fs/cgroup/memory/memory.limit_in_bytes",
             "/sys/fs/cgroup/cpu/cpu.cfs_quota_us", "/sys/fs/cgroup/cpu/cpu.cfs_period_us",
             "/sys/fs/cgroup/cpu.max")
    result = {}
    for name in paths:
        try:
            result[name] = Path(name).read_text().strip()
        except OSError:
            result[name] = "unobserved"
    return result


def _directory():
    raw = os.environ.get(ENV_DIRECTORY, "")
    if not raw:
        raise RuntimeError("explicit unique-run descriptor directory is required")
    path = Path(raw)
    root = Path("/workspace/experiments/minicpm-s2/framework").resolve()
    resolved = path.resolve()
    if not path.is_absolute() or not resolved.is_relative_to(root) or resolved == root:
        raise RuntimeError("descriptor directory must be inside unique ROOT/framework run")
    return resolved


def _write(payload):
    global _SERIAL
    payload = {"schema_version": 1, "pid": os.getpid(),
               "utc": datetime.now(timezone.utc).isoformat(),
               "tensor_values_read": False, "gpu_synchronization_requested": False,
               "gpu_buffers_allocated": False, "scheduling_changed": False,
               "current_stream": "unobserved; no device/stream API invoked",
               "source_sha256": EXPECTED_SOURCES, **payload}
    raw = (json.dumps(payload, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode()
    directory = _directory()
    directory.mkdir(parents=True, exist_ok=True)
    _SERIAL += 1
    path = directory / (payload["kind"] + "-" + str(os.getpid()) + "-" + str(_SERIAL) + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
    _notice("OBSERVED", kind=payload["kind"], path=str(path), status=payload["status"])


def _notice(action, **fields):
    try:
        print(MARKER + "_" + action + " " + json.dumps({"pid": os.getpid(), **fields}, sort_keys=True), flush=True)
    except Exception:
        pass


def _safe_observe(kind, function, obj, seen, *args):
    try:
        if obj in seen:
            return
        seen.add(obj)
        payload = function(obj, *args)
        _write(payload)
    except Exception as error:
        failure = {"kind": kind, "status": "observation_error", "error_type": type(error).__name__,
                   "error": str(error)[:500]}
        _notice("ERROR", **failure)
        try:
            _write(failure)
        except Exception as write_error:
            _notice("WRITE_ERROR", kind=kind, error_type=type(write_error).__name__)


def _tensor(tensor, torch_module, aliases):
    # These APIs read TensorImpl/Storage descriptors. Never index, clone, copy,
    # item(), cpu(), numpy(), synchronize(), inspect streams or query readiness.
    if type(tensor) is not torch_module.Tensor:
        return {"status": "unobserved_non_plain_tensor", "type": _class(tensor)}
    shape = tuple(int(n) for n in tensor.shape)
    storage = tensor.untyped_storage()
    storage_bytes = int(storage.nbytes())
    key = (str(tensor.device), int(storage.data_ptr()), storage_bytes)
    if key not in aliases:
        aliases[key] = "storage-" + str(len(aliases))
    return {"status": "observed", "shape": list(shape),
            "stride": [int(n) for n in tensor.stride()], "dtype": str(tensor.dtype),
            "device": str(tensor.device), "storage_offset_elements": int(tensor.storage_offset()),
            "element_size_bytes": int(tensor.element_size()),
            "logical_nbytes": math.prod(shape) * int(tensor.element_size()),
            "storage_nbytes": storage_bytes, "storage_alias_group": aliases[key]}


def _worker(worker, runner_class):
    config = _dict(worker).get("vllm_config")
    if not _scope(config):
        return {"kind": "worker-kv", "status": "scope_rejected", "worker": _class(worker)}
    runner = _dict(worker).get("model_runner")
    if type(runner) is not runner_class:
        return {"kind": "worker-kv", "status": "unobserved_runner_type", "runner": _class(runner)}
    torch_module = sys.modules["torch"]
    data = _dict(runner)
    cache_config = data.get("kv_cache_config")
    groups = cache_config.kv_cache_groups
    aliases, flat, layers, group_rows = {}, [], [], []
    caches = data.get("kv_caches")
    if type(caches) is list:
        flat = [{"runner_list_index": i, **_tensor(tensor, torch_module, aliases)}
                for i, tensor in enumerate(caches)]
    context = runner.compilation_config.static_forward_context
    for index, group in enumerate(groups):
        spec = group.kv_cache_spec
        group_rows.append({"group_index": index, "spec_class": _class(spec),
                           "block_size": int(spec.block_size), "dtype": str(spec.dtype),
                           "num_kv_heads": int(spec.num_kv_heads), "head_size": int(spec.head_size),
                           "layer_names": list(group.layer_names)})
        for name in group.layer_names:
            layer = context.get(name)
            # Attention.kv_cache is a direct Python attribute; no module call.
            cache = _dict(layer).get("kv_cache")
            values = cache if type(cache) is list else [cache]
            layers.append({"layer_name": name, "group_index": index, "layer_class": _class(layer),
                           "kv_views": [_tensor(value, torch_module, aliases) for value in values]})
    cross_layers = data.get("cross_layers_kv_cache")
    cross_descriptor = ({"status": "unobserved_missing_attribute"}
                        if "cross_layers_kv_cache" not in data else
                        {"status": "observed_none"} if cross_layers is None else
                        _tensor(cross_layers, torch_module, aliases))
    complete = (len(layers) == 42 and len(flat) == 42
                and all(row["status"] == "observed" for row in flat)
                and all(row["kv_views"] and all(view["status"] == "observed"
                                                for view in row["kv_views"]) for row in layers))
    return {"kind": "worker-kv", "status": "observed_complete" if complete else "observed_partial",
            "phase": "worker_initialize_from_config_successfully_returned",
            "worker": _class(worker), "runner": _class(runner), "cgroup_snapshot": _cgroup(),
            "runner_kv_cache_list_type": _class(caches), "runner_kv_cache_count": len(flat),
            "layer_count": len(layers), "groups": group_rows, "layers": layers,
            "runner_kv_cache_list": flat, "storage_alias_group_count": len(aliases),
            "kernel_block_sizes": list(data.get("_kernel_block_sizes", [])),
            "configured_num_blocks": int(cache_config.num_blocks),
            "cross_layers_kv_cache": cross_descriptor,
            "shared_kv_cache_layers": dict(data.get("shared_kv_cache_layers", {})),
            "limits": ["元信息不证明KV数据或copy完成。", "当前pid的storage alias分组，不跨进程比较指针。",
                       "列表顺序不推断layer顺序；layer映射仅来自实际static_forward_context直接kv_cache属性。"]}


def _core(engine):
    data = _dict(engine)
    if not _scope(data.get("vllm_config")):
        return {"kind": "core-objects", "status": "scope_rejected", "engine": _class(engine)}
    executor = data.get("model_executor")
    wrapper = _dict(executor).get("driver_worker")
    worker = _dict(wrapper).get("worker")
    runner = _dict(worker).get("model_runner")
    return {"kind": "core-objects", "status": "observed", "phase": "first_engine_step_after_constructor",
            "engine": _class(engine), "executor": _class(executor),
            "driver_worker_wrapper": _class(wrapper), "direct_worker": _class(worker),
            "direct_runner": _class(runner), "scheduler": _class(data.get("scheduler")),
            "batch_queue_size": data.get("batch_queue_size"), "async_scheduling": data.get("async_scheduling"),
            "access": "仅实际对象__dict__直接引用；不存在即unobserved，不调用RPC/代理getattr或假定同进程。",
            "cgroup_snapshot": _cgroup()}


def _wrap_worker(original, runner_class):
    @wraps(original)
    def wrapped(self, *args, **kwargs):
        result = original(self, *args, **kwargs)
        _safe_observe("worker-kv", _worker, self, _SEEN_WORKER, runner_class)
        return result
    return wrapped


def _wrap_core(original):
    @wraps(original)
    def wrapped(self, *args, **kwargs):
        _safe_observe("core-objects", _core, self, _SEEN_CORE)
        return original(self, *args, **kwargs)
    return wrapped


def install(*, enabled=False):
    global _INSTALLED
    if enabled is not True or _INSTALLED:
        return False
    try:
        _directory()
        platform = importlib.import_module("vllm.platforms").current_platform
        if getattr(platform, "vendor_name", "") != "iluvatar":
            raise RuntimeError("requires Iluvatar platform")
        modules = {name: importlib.import_module(name) for name in EXPECTED_SOURCES}
        for name, expected in EXPECTED_SOURCES.items():
            if hashlib.sha256(Path(modules[name].__file__).read_bytes()).hexdigest() != expected:
                raise RuntimeError("unaudited descriptor source: " + name)
        init = Path(importlib.import_module("vllm_fl").__file__).read_bytes()
        if not init.endswith(INIT_FOOTER) or hashlib.sha256(init[:-len(INIT_FOOTER)]).hexdigest() != EXPECTED_INIT:
            raise RuntimeError("unexpected general-plugin init/footer")
        core = modules["vllm.v1.engine.core"].EngineCore
        worker = modules["vllm_fl.worker.worker"].WorkerFL
        runner = modules["vllm_fl.worker.model_runner"].ModelRunnerFL
        targets = ((core, "step"), (core, "step_with_batch_queue"), (worker, "initialize_from_config"))
        originals = [getattr(cls, name) for cls, name in targets]
        for (cls, name), function in zip(targets, originals):
            module = modules[cls.__module__]
            if (inspect.unwrap(function) is not function
                    or function.__qualname__ != cls.__name__ + "." + name
                    or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
                raise RuntimeError("unexpected descriptor method wrapper")
        wrappers = (_wrap_core(originals[0]), _wrap_core(originals[1]), _wrap_worker(originals[2], runner))
        for (cls, name), function in zip(targets, wrappers):
            setattr(cls, name, function)
        _INSTALLED = True
        _notice("INSTALLED", observations_complete=False, scheduling_changed=False)
        return True
    except Exception as error:
        _notice("REJECTED", error_type=type(error).__name__, error=str(error)[:500])
        return False
