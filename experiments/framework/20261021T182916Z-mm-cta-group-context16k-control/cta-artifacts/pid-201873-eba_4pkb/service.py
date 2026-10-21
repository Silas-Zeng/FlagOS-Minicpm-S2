"""已过逐位门的 gate-up CTA group8 隔离服务入口；其余路径原样回退。

不改注册函数、installed 文件、调优 DB、模型或采样。只在受审模型的
execute/_dummy_run 作用域内，使用实际 LibEntry 已选中且完全相同的 C0。
"""
from __future__ import annotations

import atexit
from contextvars import ContextVar
import functools
import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile

EXPECTED_RUNNER = "787665d3cf6dabc1afc2bdf7069fab4802fd5f6bfb0baedd119229b5b8ce1775"
EXPECTED_POLICY = "06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1"
EXPECTED_MM = "4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090"
EXPECTED_LIBENTRY = "414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025"
EXPECTED_TRITON = "df3092178f70be89b50d22905cedae5bac414cc38677053616fc56802c91af30"
EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
EXPECTED_CANDIDATE = "30d0f046071fc4cf122d43af0d087259abc082ad10ec36f69b73ad6a22b343ab"
_MARKER = "_biv150_mm_cta_group_service_v1"
_ACTIVE = ContextVar(_MARKER, default=None)
_STATE = "_biv150_mm_cta_group_state"
TUNE = {"BLOCK_M": 256, "BLOCK_N": 256, "BLOCK_K": 32, "SPLIT_K": 1}
LAUNCH = {"num_warps": 16, "num_stages": 2, "num_ctas": 1}
HEUR = {"EVEN_K": True, "UPGRADE": False, "UPGRADE_A_OFFS": False,
        "UPGRADE_B_OFFS": False, "UPGRADE_C_OFFS": False}
CALL_KWARGS = ("acc_dtype", "input_precision", "fp8_fast_accum", "GROUP_M", "AB_DTYPE")
GRID = (384, 1, 1)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=True, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def _scope(runner, torch):
    config = runner.vllm_config
    model, parallel = config.model_config, config.parallel_config
    text = model.hf_text_config
    return (
        Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
        and model.dtype == torch.bfloat16 and model.quantization is None
        and (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
             text.num_attention_heads, text.num_key_value_heads) == (2048, 6144, 42, 16, 2)
        and all(getattr(parallel, name, None) == 1 for name in (
            "tensor_parallel_size", "pipeline_parallel_size", "decode_context_parallel_size", "data_parallel_size"))
        and parallel.use_ubatching is False
        and config.speculative_config is None and config.lora_config is None
        and getattr(config, "kv_transfer_config", None) is None
        and getattr(config, "ec_transfer_config", None) is None
        and config.cache_config.kv_sharing_fast_prefill is False
        and runner.is_pooling_model is False and runner.supports_mm_inputs is False
        and runner.enable_prompt_embeds is False and runner.use_aux_hidden_state_outputs is False
        and model.is_encoder_decoder is False
        and getattr(config.compilation_config.cudagraph_mode, "name", None) == "FULL_DECODE_ONLY"
    )


def _safe_runner(runner):
    return (runner.cross_layers_kv_cache is None
            and runner.cross_layers_attn_backend is None
            and not runner.shared_kv_cache_layers)


class Group8Kernel:
    """保留原 LibEntry 为回退；缓存编译结果，不持有任一次 A/B/C。"""
    def __init__(self, original, candidate, torch, tl, policy, directory):
        self.original, self.candidate = original, candidate
        self.torch, self.policy, self.directory = torch, policy, directory
        self.meta = dict(acc_dtype=tl.float32, input_precision=None, fp8_fast_accum=True,
                         GROUP_M=8, AB_DTYPE=tl.bfloat16, **TUNE, **HEUR)
        self.cache = {}
        self.selected = self.bootstrap_fallbacks = self.config_fallbacks = 0
        self.real_calls = self.real_selected = self.real_steps = 0
        self.first = self.first_real = None

    def __getattr__(self, name):
        return getattr(self.original, name)

    def flush(self):
        write(self.directory / "status.json", {
            "pid": os.getpid(), "selected": self.selected,
            "bootstrap_fallbacks": self.bootstrap_fallbacks, "config_fallbacks": self.config_fallbacks,
            "real_calls": self.real_calls, "real_selected": self.real_selected, "real_steps": self.real_steps,
            "first_selected": self.first, "first_real_selected": self.first_real,
            "scope": "BF16 M2048 N12288 K2048 A(K,1) B(1,K) C(N,1); actual cached C0; model-scoped",
            "accuracy": "not evaluated", "official_performance": "not evaluated"})

    def _eligible(self, args, kwargs):
        if (len(args) != 12 or tuple(args[3:6]) != (2048, 12288, 2048)
                or _ACTIVE.get() is not self or set(kwargs) != set(CALL_KWARGS)
                or any(kwargs[name] != self.meta[name] for name in CALL_KWARGS)):
            return False
        a, b, out = args[:3]
        torch = self.torch
        return (
            all(t.ndim == 2 and t.dtype == torch.bfloat16 and t.device.type == "cuda" for t in (a, b, out))
            and a.device == b.device == out.device and a.device.index == 0
            and tuple(a.shape) == (2048, 2048) and tuple(b.shape) == (2048, 12288)
            and tuple(out.shape) == (2048, 12288)
            and tuple(a.stride()) == (2048, 1) and tuple(b.stride()) == (1, 2048)
            and tuple(out.stride()) == (12288, 1)
            and tuple(args[6:]) == (2048, 1, 1, 2048, 12288, 1)
            and all(t.data_ptr() % 16 == 0 for t in (a, b, out))
            and len({t.untyped_storage().data_ptr() for t in (a, b, out)}) == 3
            and torch.cuda.current_device() == 0 and not torch.cuda.is_current_stream_capturing())

    def __getitem__(self, grid):
        original_launch = self.original[grid]

        def invoke(*args, **kwargs):
            if not self._eligible(args, kwargs):
                return original_launch(*args, **kwargs)
            # 对照 exact LibEntry:1616–1672；12 runtime参数均 specialize，无DNS。
            consts = [kwargs[name] for name in self.policy.PARAMETERS[12:] if name in kwargs]
            key = self.original.key(list(args), [], consts)
            entry = self.original.kernel_cache[0].get(key)
            if entry is None:
                self.bootstrap_fallbacks += 1
                return original_launch(*args, **kwargs)
            expected = dict(**LAUNCH, **TUNE, **HEUR)
            if (not isinstance(entry, tuple) or len(entry) != 5
                    or entry[1] != expected or entry[2] != TUNE or entry[3] != HEUR or entry[4] != ()
                    or not callable(grid)
                    or tuple(grid({**dict(zip(self.policy.PARAMETERS, args)), **kwargs, **entry[1]})) != GRID[:2]):
                self.config_fallbacks += 1
                return original_launch(*args, **kwargs)
            cached = self.cache.get(key)
            if cached is None or cached[0] is not entry:
                compiled = self.candidate[GRID](*args, **self.meta, **LAUNCH)
                self.cache[key] = (entry, compiled)
            else:
                compiled = cached[1]
                # 真实当前指针+26实参，不能缓存 gate.prepare 捕获旧tensor的闭包。
                all_args = args + tuple(self.meta[name] for name in self.policy.PARAMETERS[12:])
                compiled[GRID](*all_args)
            self.selected += 1
            if self.first is None:
                self.first = {"pid": os.getpid(), "M": 2048, "N": 12288, "K": 2048,
                              "config": dict(**TUNE, **LAUNCH), "grid": list(GRID),
                              "compiled_hash": getattr(compiled, "hash", None),
                              "original_compiled_hash": getattr(entry[0], "hash", None),
                              "registers": getattr(compiled, "n_regs", None),
                              "spills": getattr(compiled, "n_spills", None),
                              "shared_bytes": getattr(getattr(compiled, "metadata", None), "shared", None)}
                self.flush()
                print("BIV150_MM_CTA_GROUP_FIRST_SELECTED", json.dumps(self.first), flush=True)
            return compiled, entry[1]

        return invoke


def _enable(runner):
    torch = importlib.import_module("torch")
    if not _scope(runner, torch) or not _safe_runner(runner):
        return None
    if digest(Path(str(runner.model_config.model)) / "config.json") != EXPECTED_MODEL:
        raise RuntimeError("未经审阅的 MiniCPM config")
    fg = importlib.import_module("flag_gems")
    if fg.vendor_name != "iluvatar" or torch.cuda.device_count() != 1:
        raise RuntimeError("CTA service 要求单 BI-V150")
    if fg.current_work_registrar is None or "mm" not in fg.all_registered_keys():
        return None
    props = torch.cuda.get_device_properties(0)
    if "BI-V150" not in props.name or props.multi_processor_count != 16:
        raise RuntimeError("未经审阅的 BI-V150 slice")
    # 从实际注册函数的 globals 找 alias，避免另 import 一个未被 dispatcher 使用的同源模块。
    module = sys.modules.get(fg.mm.__module__)
    if (module is None or digest(module.__file__) != EXPECTED_MM
            or fg.mm is not module.mm or fg.mm_out is not module.mm_out
            or module.mm.__globals__ is not vars(module) or module.mm_out.__globals__ is not vars(module)
            or any(not any(row[0] == name and row[1] is callback for row in fg._FULL_CONFIG)
                   for name, callback in (("mm", module.mm), ("mm.out", module.mm_out)))):
        raise RuntimeError("实际 FlagGems mm 注册不使用 pinned Iluvatar module")
    if isinstance(module.mm_kernel, Group8Kernel):
        return module.mm_kernel
    libentry = importlib.import_module("flag_gems.utils.libentry")
    triton = importlib.import_module("triton")
    if digest(libentry.__file__) != EXPECTED_LIBENTRY or digest(triton.__file__) != EXPECTED_TRITON:
        raise RuntimeError("未经审阅的 compiled launch runtime")
    original = module.mm_kernel
    policy = importlib.import_module("vllm_fl.patches.biv150_mm_cta_group")
    if (digest(policy.__file__) != EXPECTED_POLICY or type(original) is not libentry.LibEntry
            or tuple(original.arg_names) != policy.PARAMETERS
            or original.specialize_indices != list(range(12)) or original.do_not_specialize_indices
            or original._has_flagtune_tuner):
        raise RuntimeError("未经审阅的原 mm LibEntry contract")
    base = Path(os.environ["BIV150_MM_CTA_ARTIFACTS"]).resolve()
    if not base.is_relative_to(Path("/workspace/experiments/minicpm-s2").resolve()):
        raise RuntimeError("CTA artifacts 必须位于本次实验目录")
    base.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f"pid-{os.getpid()}-", dir=base))
    raw = policy.transform_source(Path(module.__file__).read_bytes(), grouped=True)
    if hashlib.sha256(raw).hexdigest() != EXPECTED_CANDIDATE:
        raise RuntimeError("派生 CTA kernel 与受测门不同")
    candidate = policy._load(directory / "mm_group8.py", raw)
    for name, path in (("mm_original.py", module.__file__), ("policy.py", policy.__file__),
                       ("service.py", __file__), ("libentry.py", libentry.__file__)):
        (directory / name).write_bytes(Path(path).read_bytes())
    proxy = Group8Kernel(original, candidate, torch, importlib.import_module("triton.language"), policy, directory)
    write(directory / "install.json", {"pid": os.getpid(), "actual_mm_module": module.__name__,
                                       "mm_registered_identity": True, "model_config_sha256": EXPECTED_MODEL,
                                       "source_sha256": {p.name: digest(p) for p in directory.iterdir() if p.is_file()},
                                       "scope": "only gate-up, current C0, execute/dummy context; down untouched"})
    module.mm_kernel = proxy
    atexit.register(proxy.flush)
    proxy.flush()
    print("BIV150_MM_CTA_GROUP_READY", json.dumps({"pid": os.getpid(), "directory": str(directory)}), flush=True)
    return proxy


def install(runner_cls):
    """SQL/C2/C3 footer之后包装；不改原方法体/返回值/调用顺序。"""
    module = sys.modules.get(runner_cls.__module__)
    if module is None or digest(module.__file__) != EXPECTED_RUNNER:
        raise RuntimeError("CTA installer requires exact isolated SQL+C3 runner")
    names = ("__init__", "execute_model", "_dummy_run", "shutdown")
    marked = [bool(getattr(getattr(runner_cls, name), _MARKER, False)) for name in names]
    if any(marked):
        if not all(marked):
            raise RuntimeError("部分安装的 CTA runner wrappers")
        return {"installed": True, "already_installed": True}
    originals = {name: getattr(runner_cls, name) for name in names}

    @functools.wraps(originals["__init__"])
    def initialize(self, *args, **kwargs):
        originals["__init__"](self, *args, **kwargs)
        setattr(self, _STATE, _enable(self))

    def scoped(name):
        original = originals[name]
        @functools.wraps(original)
        def call(self, *args, **kwargs):
            proxy = getattr(self, _STATE, None)
            active = proxy if proxy is not None and _safe_runner(self) else None
            before = proxy.selected if proxy is not None else 0
            token = _ACTIVE.set(active)
            try:
                result = original(self, *args, **kwargs)
            finally:
                _ACTIVE.reset(token)
            if name == "execute_model" and proxy is not None:
                proxy.real_calls += 1
                delta = proxy.selected - before
                if delta:
                    proxy.real_steps += 1
                    proxy.real_selected += delta
                    if proxy.first_real is None:
                        output = args[0] if args else kwargs["scheduler_output"]
                        budgets = output.num_scheduled_tokens
                        proxy.first_real = {"pid": os.getpid(), "selected_delta": delta,
                                            "total_scheduled": sum(budgets.values()), "requests": len(budgets),
                                            "max_scheduled": max(budgets.values(), default=0)}
                        proxy.flush()
                        print("BIV150_MM_CTA_GROUP_REAL_SELECTED", json.dumps(proxy.first_real), flush=True)
            return result
        return call

    @functools.wraps(originals["shutdown"])
    def shutdown(self, *args, **kwargs):
        try:
            return originals["shutdown"](self, *args, **kwargs)
        finally:
            proxy = getattr(self, _STATE, None)
            if proxy is not None:
                proxy.flush()

    replacements = {"__init__": initialize, "execute_model": scoped("execute_model"),
                    "_dummy_run": scoped("_dummy_run"), "shutdown": shutdown}
    for name, replacement in replacements.items():
        setattr(replacement, _MARKER, True)
        setattr(runner_cls, name, replacement)
    return {"installed": True, "scope": "strict MiniCPM BF16 gate-up group8 only", "accuracy": "not evaluated"}
