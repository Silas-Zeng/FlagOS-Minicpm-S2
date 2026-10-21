"""为已过门87c6/a6d省mask实现准备独立服务入口，不叠CTA或mapped。

只在受审MiniCPM模型execute/dummy作用域内启用原policy；capture和其它
配置全部经原C2返回。没有新FP、metadata、KV写、采样或RNG实现。
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

EXPECTED_RUNNER = "4467ac262bb22edca90c106ae2361efe5e8917ec7115d51c07d4d3e35245703a"
EXPECTED_POLICY = "87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6"
EXPECTED_GENERATED = "a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
EXPECTED_SQL = "ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e"
EXPECTED_MODEL = "59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180"
_MARKER = "_biv150_visible_prefix_service_v1"
_STATE = "_biv150_visible_prefix_state"
_ACTIVE = ContextVar(_MARKER, default=None)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


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
    return (runner.cross_layers_kv_cache is None and runner.cross_layers_attn_backend is None
            and not runner.shared_kv_cache_layers)


class ScopedVisiblePrefix:
    """只增加外层执行scope；inner的87c6 descriptor/FP策略保持原样。"""
    def __init__(self, inner, torch, directory):
        self.inner, self.original, self.torch, self.directory = inner, inner.original, torch, directory
        self.first = self.first_real_large = None
        self.compiled = {}
        self.real_calls = self.real_selected = self.real_large_steps = 0

    def __getattr__(self, name):
        return getattr(self.inner, name)

    def flush(self):
        write(self.directory / "status.json", {
            "pid": os.getpid(), "selected": self.inner.selected_launches, "fallback": self.inner.fallback_launches,
            "real_calls": self.real_calls, "real_selected": self.real_selected, "real_large_steps": self.real_large_steps,
            "first_selected": self.first, "first_real_large_selected": self.first_real_large,
            "compiled_first_seen": self.compiled, "policy_sha256": EXPECTED_POLICY,
            "generated_sha256": EXPECTED_GENERATED, "accuracy": "not evaluated", "official_performance": "not evaluated"})

    def __getitem__(self, grid):
        def invoke(*args, **kwargs):
            scope = _ACTIVE.get()
            if scope is None or scope[0] is not self or self.torch.cuda.is_current_stream_capturing():
                return self.original[grid](*args, **kwargs)
            before = self.inner.selected_launches
            result = self.inner[grid](*args, **kwargs)
            if self.inner.selected_launches > before:
                key = str(getattr(result, "hash", None))
                if key not in self.compiled:
                    record = {"pid": os.getpid(), "compiled_hash": getattr(result, "hash", None),
                              "real_execute": scope[1], "selected_at_first_seen": self.inner.selected_launches,
                              "num_seqs": kwargs.get("num_seqs"), "query_rows": int(kwargs["query_ptr"].shape[0]),
                              "BLOCK_M": 128, "BLOCK_Q": 16, "TILE_SIZE": 64, "num_warps": 8, "num_stages": 1,
                              "registers": getattr(result, "n_regs", None), "spills": getattr(result, "n_spills", None),
                              "shared_bytes": getattr(getattr(result, "metadata", None), "shared", None)}
                    self.compiled[key] = record
                    if self.first is None:
                        self.first = record
                    self.flush()
                    print("BIV150_VISIBLE_PREFIX_FIRST_SELECTED", json.dumps(record), flush=True)
            return result
        return invoke


def _enable(runner):
    torch = importlib.import_module("torch")
    if not _scope(runner, torch) or not _safe_runner(runner):
        return None
    if digest(Path(str(runner.model_config.model)) / "config.json") != EXPECTED_MODEL:
        raise RuntimeError("未经审阅的MiniCPM config")
    if torch.cuda.device_count() != 1:
        raise RuntimeError("prefix service要求单BI-V150")
    props = torch.cuda.get_device_properties(0)
    if "BI-V150" not in props.name or props.multi_processor_count != 16:
        raise RuntimeError("未经审阅的BI-V150 slice")
    attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
    if isinstance(attention.kernel_unified_attention, ScopedVisiblePrefix):
        return attention.kernel_unified_attention
    policy = importlib.import_module("vllm_fl.patches.biv150_prefill_visible_prefix")
    c3 = importlib.import_module("vllm_fl.patches.biv150_mixed_decode")
    sql = importlib.import_module("vllm_fl.patches.biv150_sql_reflection")
    if digest(policy.__file__) != EXPECTED_POLICY or digest(c3.__file__) != EXPECTED_C3 or digest(sql.__file__) != EXPECTED_SQL:
        raise RuntimeError("未经审阅的prefix/SQL/C3源码")
    helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
    backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
    if not all(getattr(function, "_biv150_natural_prefix_wrapper", False) for function in (
            backend.TritonAttentionMetadataBuilder.build, backend.TritonAttentionImpl.forward)):
        raise RuntimeError("prefix service要求既有C3先安装")
    base = Path(os.environ["BIV150_VISIBLE_PREFIX_ARTIFACTS"]).resolve()
    if not base.is_relative_to(Path("/workspace/experiments/minicpm-s2").resolve()):
        raise RuntimeError("prefix artifacts必须位于本次实验目录")
    base.mkdir(parents=True, exist_ok=True)
    directory = Path(tempfile.mkdtemp(prefix=f"pid-{os.getpid()}-", dir=base))
    generated = directory / "triton_unified_attention_visible_prefix.py"
    inner = policy.create(attention, helpers, backend, generated)
    if digest(generated) != EXPECTED_GENERATED:
        raise RuntimeError("派生prefix kernel与受测a6d不同")
    for name, path in (("policy.py", policy.__file__), ("service.py", __file__),
                       ("attention_original.py", attention.__file__), ("helpers.py", helpers.__file__),
                       ("backend.py", backend.__file__), ("c3.py", c3.__file__)):
        (directory / name).write_bytes(Path(path).read_bytes())
    write(directory / "install.json", {"pid": os.getpid(), "source_sha256": {
        p.name: digest(p) for p in directory.iterdir() if p.is_file()},
        "order": "original SQL -> C2 -> C3 -> model-scoped visible-prefix proxy",
        "scope": "87c6 eligibility unchanged; capture and nonmatching calls through original C2"})
    proxy = ScopedVisiblePrefix(inner, torch, directory)
    attention.kernel_unified_attention = proxy
    atexit.register(proxy.flush)
    proxy.flush()
    print("BIV150_VISIBLE_PREFIX_READY", json.dumps({"pid": os.getpid(), "directory": str(directory)}), flush=True)
    return proxy


def install(runner_cls):
    module = sys.modules.get(runner_cls.__module__)
    if runner_cls.__name__ != "ModelRunnerFL" or module is None or digest(module.__file__) != EXPECTED_RUNNER:
        raise RuntimeError("prefix installer只接受独立exact SQL+C3 runner")
    names = ("__init__", "execute_model", "_dummy_run", "shutdown")
    marked = [bool(getattr(getattr(runner_cls, name), _MARKER, False)) for name in names]
    if any(marked):
        if not all(marked):
            raise RuntimeError("部分安装的prefix runner wrappers")
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
            before = proxy.inner.selected_launches if proxy is not None else 0
            token = _ACTIVE.set((active, name == "execute_model") if active is not None else None)
            try:
                result = original(self, *args, **kwargs)
            finally:
                _ACTIVE.reset(token)
            if name == "execute_model" and proxy is not None:
                proxy.real_calls += 1
                delta = proxy.inner.selected_launches - before
                proxy.real_selected += delta
                if delta:
                    output = args[0] if args else kwargs["scheduler_output"]
                    budgets = output.num_scheduled_tokens
                    maximum = max(budgets.values(), default=0)
                    if maximum >= 128:
                        proxy.real_large_steps += 1
                        if proxy.first_real_large is None:
                            proxy.first_real_large = {"pid": os.getpid(), "selected_delta": delta,
                                "max_query_scheduled": maximum, "total_scheduled": sum(budgets.values()),
                                "requests": len(budgets), "at_least_one_complete_visible_tile_possible": True}
                            proxy.flush()
                            print("BIV150_VISIBLE_PREFIX_REAL_LARGE_SELECTED", json.dumps(proxy.first_real_large), flush=True)
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
    return {"installed": True, "scope": "unmodified 87c6 prefix-mask only; no CTA/mapped", "accuracy": "not evaluated"}
