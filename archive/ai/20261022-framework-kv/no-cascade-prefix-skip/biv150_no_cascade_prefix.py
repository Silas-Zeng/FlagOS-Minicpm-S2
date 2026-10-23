"""默认关闭：只在实际单组Triton/no-cascade服务省去公共前缀统计。

APC查询/哈希/分配/释放均不改。observe只计CPU成本；skip返回同组数零。
模块导入仅stdlib；由已构造EngineCore的首次step接入install_on_engine。
"""
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
from time import perf_counter_ns, thread_time_ns
from types import MethodType

EXPECTED = {
    "vllm.v1.engine.core": "27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71",
    "vllm.v1.executor.uniproc_executor": "4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe",
    "vllm.v1.worker.worker_base": "7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe",
    "vllm_fl.worker.worker": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
    "vllm_fl.worker.model_runner": "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141",
    "vllm.v1.core.sched.scheduler": "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090",
    "vllm.v1.core.sched.async_scheduler": "da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884",
    "vllm.v1.core.kv_cache_manager": "2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320",
    "vllm.v1.core.kv_cache_coordinator": "9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b",
    "vllm.v1.core.single_type_kv_cache_manager": "22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914",
    "vllm.v1.kv_cache_interface": "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003",
    "vllm.v1.attention.backends.triton_attn": "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605",
    "vllm.v1.attention.backend": "c524988a2223ec556bdb128a31c255075f0d07e7643e803b447975cd9c30a6b8",
}


def _data(obj):
    value = object.__getattribute__(obj, "__dict__")
    if type(value) is not dict:
        raise ValueError("非实际本地对象")
    return value


def _modules():
    modules = {}
    for name, expected in EXPECTED.items():
        module = sys.modules.get(name)
        if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
            raise ValueError("未自然加载/来源未知: " + name)
        modules[name] = module
    return modules


class Manager:
    def __init__(self, engine, mode):
        if mode not in ("observe", "skip"):
            raise ValueError("mode只能为observe或skip")
        modules = _modules()
        if type(engine) is not modules["vllm.v1.engine.core"].EngineCoreProc:
            raise ValueError("非实际EngineCoreProc")
        executor = engine.model_executor
        if type(executor) is not modules["vllm.v1.executor.uniproc_executor"].UniProcExecutor:
            raise ValueError("非单进程UniProc")
        wrapper = _data(executor).get("driver_worker")
        if type(wrapper) is not modules["vllm.v1.worker.worker_base"].WorkerWrapperBase:
            raise ValueError("非原worker wrapper")
        worker = _data(wrapper).get("worker")
        if type(worker) is not modules["vllm_fl.worker.worker"].WorkerFL:
            raise ValueError("非原WorkerFL")
        runner = _data(worker).get("model_runner")
        if type(runner) is not modules["vllm_fl.worker.model_runner"].ModelRunnerFL:
            raise ValueError("非原6f runner")
        config = engine.vllm_config
        model, parallel = config.model_config, config.parallel_config
        text = model.hf_text_config
        if not (
            Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
            and str(model.dtype) == "torch.bfloat16" and model.quantization is None
            and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
                 text.num_key_value_heads) == (2048, 42, 16, 2)
            and all(getattr(parallel, key, None) == 1 for key in (
                "tensor_parallel_size", "pipeline_parallel_size", "data_parallel_size",
                "decode_context_parallel_size"))
            and parallel.use_ubatching is False
            and config.speculative_config is None and config.lora_config is None
            and config.kv_transfer_config is None and config.ec_transfer_config is None
        ):
            raise ValueError("模型/并行/feature不在当前子集")
        scheduler = engine.scheduler
        if type(scheduler) is not modules["vllm.v1.core.sched.async_scheduler"].AsyncScheduler:
            raise ValueError("非实际AsyncScheduler")
        manager = scheduler.kv_cache_manager
        if type(manager) is not modules["vllm.v1.core.kv_cache_manager"].KVCacheManager:
            raise ValueError("非原KVCacheManager")
        coordinator = manager.coordinator
        if type(coordinator) is not modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator:
            raise ValueError("非原单组coordinator")
        groups = manager.kv_cache_config.kv_cache_groups
        if len(groups) != 1 or type(groups[0].kv_cache_spec) is not modules["vllm.v1.kv_cache_interface"].FullAttentionSpec:
            raise ValueError("非单组FullAttention")
        singles = coordinator.single_type_managers
        if len(singles) != 1 or type(singles[0]) is not modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager:
            raise ValueError("非原FullAttentionManager")
        backend = modules["vllm.v1.attention.backends.triton_attn"]
        capability = modules["vllm.v1.attention.backend"].AttentionMetadataBuilder.use_cascade_attention
        if (inspect.unwrap(capability) is not capability
            or Path(capability.__code__.co_filename).resolve() != Path(modules["vllm.v1.attention.backend"].__file__).resolve()):
            raise ValueError("cascade能力方法被动态替换")
        attn_groups = runner.attn_groups
        if len(attn_groups) != 1 or len(attn_groups[0]) != 1:
            raise ValueError("未知attention group")
        self.builders = []
        self.groups = tuple(attn_groups[0])
        layer_names = []
        for group in self.groups:
            if _data(group).get("backend") is not backend.TritonAttentionBackend:
                raise ValueError("存在非Triton后端")
            builder = group.get_metadata_builder()
            if (type(builder) is not backend.TritonAttentionMetadataBuilder
                or type(builder).use_cascade_attention is not capability
                or "use_cascade_attention" in _data(builder)):
                raise ValueError("builder不再继承固定False能力")
            self.builders.append(builder)
            layer_names.extend(group.layer_names)
        if len(layer_names) != 42 or set(layer_names) != set(groups[0].layer_names):
            raise ValueError("非完整42层Triton")
        original = manager.get_num_common_prefix_blocks
        if ("get_num_common_prefix_blocks" in _data(manager)
            or original.__func__ is not type(manager).get_num_common_prefix_blocks
            or inspect.unwrap(original.__func__) is not original.__func__
            or Path(original.__func__.__code__.co_filename).resolve() != Path(modules["vllm.v1.core.kv_cache_manager"].__file__).resolve()):
            raise ValueError("前置prefix统计wrapper不受支持")
        self.engine, self.runner, self.manager = engine, runner, manager
        self.mode, self.original, self.active = mode, original, False
        self.capability, self.backend, self.attn_groups = capability, backend, attn_groups
        self.single = singles[0]
        self.counts = {"selected_calls": 0, "fallback_calls": 0, "observation_errors": 0,
                       "single_request_calls": 0, "single_request_ns": 0,
                       "multiple_request_calls": 0, "multiple_request_ns": 0,
                       "single_request_thread_cpu_ns": 0, "multiple_request_thread_cpu_ns": 0}
        self.wrapper = None

    def _eligible_now(self):
        # 仅N1才调用：一次安装核完整42层；热guard不再遍历层或group集合。
        group, builder = self.groups[0], self.builders[0]
        return (self.runner.attn_groups is self.attn_groups
            and len(self.attn_groups) == 1 and len(self.attn_groups[0]) == 1
            and self.attn_groups[0][0] is group
            and _data(group).get("backend") is self.backend.TritonAttentionBackend
            and type(builder).use_cascade_attention is self.capability
            and "use_cascade_attention" not in _data(builder))

    def install(self):
        if self.active:
            return self
        if self.manager.get_num_common_prefix_blocks != self.original:
            raise ValueError("prefix统计已被其它owner替换")
        owner = self
        @wraps(self.original)
        def wrapped(manager, running_request_id):
            eligible = False
            try:
                if owner.mode == "skip":
                    eligible = (len(owner.single.req_to_blocks) == 1
                                and running_request_id in owner.single.req_to_blocks
                                and owner._eligible_now())
            except Exception:
                pass
            if owner.mode == "skip" and eligible:
                owner.counts["selected_calls"] += 1
                if owner.counts["selected_calls"] == 1:
                    _emit("FIRST_SELECTED", **owner.snapshot())
                return [0]
            if owner.mode == "skip":
                owner.counts["fallback_calls"] += 1
                return owner.original(running_request_id)
            start = cpu_start = bucket = None
            try:
                bucket = ("single_request" if len(manager.coordinator.single_type_managers[0].req_to_blocks) == 1
                          else "multiple_request")
                start = perf_counter_ns()
                cpu_start = thread_time_ns()
            except Exception:
                pass
            # 原callee恰一次，异常不捕获/重试，也不置于观察except上下文内。
            result = owner.original(running_request_id)
            try:
                cpu_elapsed = thread_time_ns() - cpu_start if cpu_start is not None else None
                elapsed = perf_counter_ns() - start if start is not None else None
                if start is not None:
                    owner.counts[bucket + "_ns"] += elapsed
                    owner.counts[bucket + "_thread_cpu_ns"] += cpu_elapsed
                    owner.counts[bucket + "_calls"] += 1
            except Exception:
                owner.counts["observation_errors"] += 1
            calls = owner.counts["single_request_calls"] + owner.counts["multiple_request_calls"]
            if calls and calls & (calls - 1) == 0:
                _emit("CPU_COST_PARTIAL", partial=True, **owner.snapshot())
            return result
        self.wrapper = MethodType(wrapped, self.manager)
        self.manager.get_num_common_prefix_blocks = self.wrapper
        self.active = True
        return self

    def restore(self):
        if self.active and _data(self.manager).get("get_num_common_prefix_blocks") is self.wrapper:
            del self.manager.__dict__["get_num_common_prefix_blocks"]
        self.active = False

    def snapshot(self):
        return {"mode": self.mode, "active": self.active, "counts": dict(self.counts),
                "scope": "MiniCPM5-2B/clean6f/samePID-UniProc/normal42/Triton/no-cascade",
                "apc_query_hash_allocation_free_changed": False,
                "device_api_calls": False, "timing_is_cpu_only": True,
                "clock_limits": "*_ns is callee wall (perf_counter_ns); *_thread_cpu_ns is calling-thread CPU; adjacent clock cost included; no E2E gain inferred"}


def install_on_engine(engine, *, mode="observe"):
    """须EngineCore构造完后调用；未知source/scope抛出，调用方原路继续。"""
    return Manager(engine, mode).install()



def _emit(event, **values):
    try:
        print("BIV150_NO_CASCADE_PREFIX " + json.dumps({"pid": os.getpid(), "event": event, **values}, sort_keys=True), flush=True)
    except Exception:
        pass


def install(*, enabled=False, mode="observe"):
    """general plugin可显式调用；首次Core.step才核自然加载worker/后端。

    返回包含restore方法的句柄；默认disabled不改任何对象。此入口不部署自身。
    """
    if enabled is not True:
        return None
    if mode not in ("observe", "skip"):
        raise ValueError("未知mode")
    module = sys.modules.get("vllm.v1.engine.core")
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED[module.__name__]:
        raise ValueError("原EngineCore尚未自然加载")
    core = module.EngineCore
    original = core.step_with_batch_queue
    if (inspect.unwrap(original) is not original
        or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
        raise ValueError("Core已有非原wrapper，禁止叠加")
    managers = []
    @wraps(original)
    def step(engine, *args, **kwargs):
        key = "_biv150_no_cascade_prefix_checked"
        if not getattr(engine, key, False):
            setattr(engine, key, True)
            try:
                manager = install_on_engine(engine, mode=mode)
                managers.append(manager)
                _emit("ARMED", **manager.snapshot())
            except Exception as error:
                _emit("SCOPE_REJECTED", reason=type(error).__name__ + ": " + str(error)[:160])
        # 不在scope检查的except上下文中调用原方法，不更改原异常context。
        return original(engine, *args, **kwargs)
    def restore():
        for manager in managers:
            _emit("FINAL_CPU_COST", workload_complete_not_asserted=True, **manager.snapshot())
            manager.restore()
            manager.engine.__dict__.pop("_biv150_no_cascade_prefix_checked", None)
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original
    core.step_with_batch_queue = step
    return {"restore": restore, "managers": managers, "mode": mode}
