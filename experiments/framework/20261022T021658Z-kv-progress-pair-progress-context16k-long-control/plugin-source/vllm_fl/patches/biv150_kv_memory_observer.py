"""仅显式启用的启动显存标量观察器；不采样GPU、不修改容量计算。

沿原determine调用和原profiling contextmanager记录现成CPU标量；默认关闭。
输出只到stdout，原worker/runner源码、原返回、原异常和原CM抑制语义保留。
"""
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
from types import FunctionType

EXPECTED_WORKER = "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24"
EXPECTED_IO = "6d8b4adf9ad75a5b79569e4ccc132c1ee69fd525198b3c4e25e2d6de6f3fff55"
EXPECTED_PARENT = "419002195d13cf050c3ea9705d18a12456c890c27c470a1efadce7de27ded0b1"
EXPECTED_LOADED = {
    "vllm.v1.executor.uniproc_executor": "4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe",
    "vllm.v1.worker.worker_base": "7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe",
    "vllm_fl.worker.worker": EXPECTED_WORKER,
    "vllm_fl.dispatch.io_common": EXPECTED_IO,
}
EXPECTED_INIT_PREFIXES = {
    "stable": "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff",
    "capacity": "791c38c20a648f4868e56e24efdae7351671960462232defb85997738f41a2b8",
}
INIT_FOOTER = (b"\n    # _biv150_kv_memory_observer_v1\n"
               b"    from vllm_fl.patches.biv150_kv_memory_observer import install as _install_kv_memory_observer\n"
               b"    _install_kv_memory_observer(enabled=True)\n")
_ACTIVE = ContextVar("biv150_kv_memory_observer", default=None)
_MARKER = "_biv150_kv_memory_observer_v1"
_INSTALLED = False
_SNAPSHOT_FIELDS = ("torch_peak", "free_memory", "total_memory", "cuda_memory",
                    "torch_memory", "non_torch_memory", "timestamp", "auto_measure")
_PROFILE_FIELDS = ("weights_memory", "torch_peak_increase", "non_torch_increase",
                   "non_kv_cache_memory", "profile_time")
_WORKER_FIELDS = ("requested_memory", "non_torch_memory", "peak_activation_memory",
                  "cudagraph_memory_estimate", "available_kv_cache_memory_bytes")


def _scalar(value):
    if type(value) in (int, float, bool, str) or value is None:
        return value
    return {"unobserved_scalar_type": type(value).__name__}


def _fields(value, names):
    data = vars(value) if hasattr(value, "__dict__") else {}
    return {name: _scalar(data[name]) if name in data else {"unobserved_missing": True}
            for name in names}


def _function(function):
    """只读Python函数/原__wrapped__身份；不执行目标或格式化其参数。"""
    result, seen = [], set()
    for _ in range(6):
        if not isinstance(function, FunctionType) or id(function) in seen:
            break
        seen.add(id(function))
        code = function.__code__
        result.append({"module": function.__module__, "qualname": function.__qualname__,
                       "code_qualname": code.co_qualname, "source_file": code.co_filename,
                       "first_line": code.co_firstlineno})
        function = vars(function).get("__wrapped__")
    return result


def _caller_chain():
    frame = inspect.currentframe()
    result = []
    try:
        frame = frame.f_back.f_back if frame is not None and frame.f_back is not None else None
        for _ in range(7):
            if frame is None:
                break
            code = frame.f_code
            result.append({"qualname": code.co_qualname, "source_file": code.co_filename,
                           "line": frame.f_lineno})
            frame = frame.f_back
    finally:
        del frame
    return result


def _logger_state(logger):
    """只读现态，不调用isEnabledFor/日志方法或修改logger缓存/配置。"""
    chain, seen = [], set()
    current = logger
    for _ in range(6):
        if current is None or id(current) in seen:
            break
        seen.add(id(current))
        data = vars(current)
        handlers = []
        for handler in data.get("handlers", ()):
            hd = vars(handler)
            handlers.append({"class": type(handler).__module__ + "." + type(handler).__name__,
                             "level": _scalar(hd.get("level")),
                             "filters": [type(x).__module__ + "." + type(x).__name__
                                         for x in hd.get("filters", ())]})
        chain.append({"name": _scalar(data.get("name")), "level": _scalar(data.get("level")),
                      "disabled": _scalar(data.get("disabled")),
                      "propagate": _scalar(data.get("propagate")), "handlers": handlers,
                      "filters": [type(x).__module__ + "." + type(x).__name__
                                  for x in data.get("filters", ())]})
        current = data.get("parent")
    effective = next((x["level"] for x in chain if type(x["level"]) is int and x["level"]), 0)
    manager = vars(logger).get("manager")
    if manager is None:
        manager = getattr(type(logger), "manager", None)
    disabled = vars(manager).get("_disable") if manager is not None else None
    once = getattr(type(logger), "info_once", None)
    return {"chain": chain, "effective_level_derived": effective,
            "manager_disable": _scalar(disabled), "info_once_function": _function(once),
            "filters_executed": False, "log_configuration_changed": False}


def _emit(event, **fields):
    try:
        print("BIV150_KV_MEMORY_OBSERVER " + json.dumps(
            {"event": event, "pid": os.getpid(), "observational_only": True,
             "new_gpu_samples": False, **fields}, sort_keys=True), flush=True)
    except Exception:
        # 观察输出失败不能覆盖原方法返回/异常或变成原CM的抑制决定。
        pass


def _wrap_profile(original):
    @contextmanager
    @wraps(original)
    def observed(*args, **kwargs):
        # 必须保留原with，包含原__enter__/__exit__及其异常抑制行为。
        with original(*args, **kwargs) as result:
            try:
                active = _ACTIVE.get()
                if active is not None:
                    active["profile_context_calls"] += 1
                    active["profile_result"] = result
            except Exception:
                pass
            yield result
    setattr(observed, _MARKER, True)
    return observed


def _finish_record(record, worker, module, returned, error_type):
    data = vars(worker)
    profile = record.pop("profile_result", None)
    profile_data = vars(profile) if profile is not None else {}
    result = {**record, "returned": _scalar(returned), "error_type": error_type,
              "worker_fields": _fields(worker, _WORKER_FIELDS),
              "init_snapshot": _fields(data.get("init_snapshot"), _SNAPSHOT_FIELDS),
              "profile": _fields(profile, _PROFILE_FIELDS),
              "logger_after": _logger_state(module.logger)}
    for name in ("before_create", "before_profile", "after_profile"):
        result[name] = _fields(profile_data.get(name), _SNAPSHOT_FIELDS)
    before = profile_data.get("before_profile")
    before_peak = vars(before).get("torch_peak") if before is not None else None
    increase = profile_data.get("torch_peak_increase")
    derived = {}
    if type(before_peak) is int and type(increase) is int:
        derived["profile_torch_peak_reconstructed"] = before_peak + increase
    requested, non_kv, available = (data.get("requested_memory"),
                                  profile_data.get("non_kv_cache_memory"),
                                  data.get("available_kv_cache_memory_bytes"))
    if all(type(x) in (int, float) for x in (requested, non_kv, available)):
        derived["graph_deduction_reconstructed"] = requested - non_kv - available
    result["derived_only_not_new_samples"] = derived
    _emit("DETERMINE_RETURN" if error_type is None else "DETERMINE_RAISED", **result)


def _wrap_determine(original, module, identity):
    @wraps(original)
    def observed(self, *args, **kwargs):
        record = {"original_identity": identity, "profile_context_calls": 0}
        try:
            record.update(caller_chain=_caller_chain(), logger_before=_logger_state(module.logger))
        except Exception as error:
            record["metadata_error_type"] = type(error).__name__
        token = _ACTIVE.set(record)
        returned, error_type = None, None
        try:
            returned = original(self, *args, **kwargs)
            return returned
        except BaseException as error:
            error_type = type(error).__name__
            raise
        finally:
            _ACTIVE.reset(token)
            try:
                _finish_record(record, self, module, returned, error_type)
            except Exception as error:
                _emit("OBSERVATION_INCOMPLETE", error_type=type(error).__name__,
                      original_error_type=error_type, returned=_scalar(returned))
    setattr(observed, _MARKER, True)
    return observed


def _loaded_context(executor):
    """原父RPC入口时才检查自然已加载模块；绝不import worker/设备模块。"""
    modules = {name: sys.modules.get(name) for name in EXPECTED_LOADED}
    for name, expected in EXPECTED_LOADED.items():
        module = modules[name]
        if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("自然加载模块缺失或source不符：" + name)
    if type(executor) is not modules["vllm.v1.executor.uniproc_executor"].UniProcExecutor:
        raise RuntimeError("仅实际UniProcExecutor")
    wrapper = vars(executor).get("driver_worker")
    if type(wrapper) is not modules["vllm.v1.worker.worker_base"].WorkerWrapperBase:
        raise RuntimeError("实际driver wrapper尚未创建")
    instance = vars(wrapper).get("worker")
    module, io = modules["vllm_fl.worker.worker"], modules["vllm_fl.dispatch.io_common"]
    worker = module.WorkerFL
    if type(instance) is not worker:
        raise RuntimeError("实际WorkerFL尚未创建")
    original, profiling = vars(worker)["determine_available_memory"], module.memory_profiling_fl
    inner, profile_inner = vars(original).get("__wrapped__"), vars(profiling).get("__wrapped__")
    worker_path, io_path = Path(module.__file__).resolve(), Path(io.__file__).resolve()
    if (not isinstance(original, FunctionType) or not isinstance(inner, FunctionType)
            or vars(inner).get("__wrapped__") is not None
            or original.__qualname__ != "WorkerFL.determine_available_memory"
            or inner.__qualname__ != "WorkerFL.determine_available_memory"
            or Path(original.__code__.co_filename).resolve() != io_path
            or Path(inner.__code__.co_filename).resolve() != worker_path
            or not isinstance(profiling, FunctionType) or not isinstance(profile_inner, FunctionType)
            or profile_inner.__qualname__ != "memory_profiling_fl"
            or Path(profile_inner.__code__.co_filename).resolve() != worker_path
            or not inspect.isgeneratorfunction(profile_inner)):
        raise RuntimeError("determine/profile原包装身份不符")
    identity = {"loaded_source_sha256": dict(EXPECTED_LOADED),
                "executor_class": type(executor).__module__ + "." + type(executor).__name__,
                "determine_chain": _function(original), "profiling_chain": _function(profiling)}
    return module, worker, original, profiling, identity


def _wrap_parent(original, parent_class):
    @wraps(original)
    def observed(self, *args, **kwargs):
        attachment, returned, error_type = None, None, None
        restored = {"worker_method": None, "profiling_context": None, "parent_method": False}
        try:
            try:
                module, worker, method, profiling, identity = _loaded_context(self)
                new_method, new_profile = _wrap_determine(method, module, identity), _wrap_profile(profiling)
                attachment = (module, worker, method, profiling, new_method, new_profile)
                module.memory_profiling_fl = new_profile
                worker.determine_available_memory = new_method
            except Exception as error:
                _emit("NOT_ACTIVATED", error_type=type(error).__name__, error=str(error)[:300])
            # 无论观察资格是否满足，原父RPC只调用一次，原list/异常直接传回。
            returned = original(self, *args, **kwargs)
            return returned
        except BaseException as error:
            error_type = type(error).__name__
            raise
        finally:
            # 单次启动调用结束即恢复；不留后续profile或运行期hook。
            if attachment is not None:
                module, worker, method, profiling, new_method, new_profile = attachment
                try:
                    if vars(worker).get("determine_available_memory") is new_method:
                        worker.determine_available_memory = method
                    restored["worker_method"] = vars(worker).get("determine_available_memory") is method
                    if module.memory_profiling_fl is new_profile:
                        module.memory_profiling_fl = profiling
                    restored["profiling_context"] = module.memory_profiling_fl is profiling
                except Exception:
                    pass
            try:
                if vars(parent_class).get("determine_available_memory") is observed:
                    parent_class.determine_available_memory = original
                restored["parent_method"] = vars(parent_class).get("determine_available_memory") is original
            except Exception:
                pass
            values = ([_scalar(x) for x in returned] if type(returned) is list else _scalar(returned))
            _emit("PARENT_RETURN" if error_type is None else "PARENT_RAISED",
                  error_type=error_type, original_chain=_function(original),
                  returned=values, returned_type=type(returned).__name__, restored=restored)
    setattr(observed, _MARKER, True)
    return observed


def install(*, enabled=False):
    """完整既有footer之后只武装已加载父类入口；默认无动作/无提前import。"""
    global _INSTALLED
    if enabled is not True or _INSTALLED:
        return False
    try:
        plugin = sys.modules.get("vllm_fl")
        init = Path(plugin.__file__).read_bytes() if plugin is not None else b""
        if (not init.endswith(INIT_FOOTER)
                or hashlib.sha256(init[:-len(INIT_FOOTER)]).hexdigest()
                not in EXPECTED_INIT_PREFIXES.values()):
            raise RuntimeError("observer必须位于完整stable/capacity原footer之后")
        module = sys.modules.get("vllm.v1.executor.abstract")
        if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED_PARENT:
            raise RuntimeError("原父类模块尚未自然加载或source不符")
        parent = module.Executor
        original = vars(parent)["determine_available_memory"]
        if (not isinstance(original, FunctionType) or vars(original).get("__wrapped__") is not None
                or original.__qualname__ != "Executor.determine_available_memory"
                or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise RuntimeError("父determine原方法身份不符")
        parent.determine_available_memory = _wrap_parent(original, parent)
        _INSTALLED = True
        _emit("ARMED", parent_source_sha256=EXPECTED_PARENT, parent_chain=_function(original),
              default_enabled=False, observations_complete=False,
              stdout_bypasses_worker_logger=True, source_files_changed=False)
        return True
    except Exception as error:
        _emit("REJECTED", error_type=type(error).__name__, error=str(error)[:300])
        return False
