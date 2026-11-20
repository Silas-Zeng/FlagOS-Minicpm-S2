"""BI-V150 MiniCPM 的 RoPE 与 KV 写入融合；保留独立 Q/K 和原 Attention。"""
import hashlib
import inspect
import json
import os
from pathlib import Path
import types

import torch
from torch._C import _cuda_getCurrentRawStream as get_raw_stream
from vllm.model_executor.layers.attention import attention as attention_module
from vllm.utils.torch_utils import LayerNameType, _encode_layer_name, _resolve_layer_name, direct_register_custom_op

_FEATURE = "VLLM_FL_BIV150_ROPE_KV"
_REGISTERED = False
_KERNEL_READY = False
_KERNEL = None
_LAYERS = {}
_OBSERVED = set()
_SOURCE_PINS = {
    "attention": "3414faca4cc04c699dbb880ba1761230e1ed97035f2934604cad9a5490f4dba1",
    "rotary": "c81804498f08f072356a26b41967f211475df2694dabf5da9f488c074d1fdef5",
    "llama": "1e1003454985bf86d3868a7755bcf5324676881548b3895809edf0b76698d384",
}


def _require(condition, message):
    if not condition:
        raise RuntimeError("RoPE/KV: " + message)


def _cache_mode(cache_empty, has_metadata, has_slots, capturing):
    """空 cache 只允许早期非捕获 profile；已绑定 cache 不按 metadata 分支。"""
    if cache_empty:
        _require(not has_metadata and not has_slots and not capturing,
                 "无 cache 的 profile 不能形成真实 KV 图")
        return "profile"
    _require(has_slots, "已绑定 cache 缺少 GPU slot_mapping")
    return "bound"


def _validate_tensor_inputs(qkv, positions, table):
    rows = qkv.shape[0]
    _require(qkv.ndim == 2 and qkv.shape[1] == 2560 and qkv.stride() == (2560, 1),
             "QKV 不是固定合并布局")
    _require(qkv.dtype == torch.bfloat16 and qkv.device.type == "cuda", "QKV dtype/device")
    _require(positions.ndim == 1 and positions.shape[0] == rows
             and positions.stride() == (1,) and positions.dtype == torch.int64
             and positions.device == qkv.device, "positions 布局")
    _require(table.shape == (131072, 128) and table.stride() == (128, 1)
             and table.dtype == qkv.dtype and table.device == qkv.device, "原位置表布局")
    _require(rows > 0, "空行数")
    return rows


def _rope_kv(qkv: torch.Tensor, positions: torch.Tensor, table: torch.Tensor,
             layer_name: LayerNameType) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    rows = _validate_tensor_inputs(qkv, positions, table)
    _require(_KERNEL_READY, "融合核必须在模型 profile/capture 前完成预热")
    name = _resolve_layer_name(layer_name)
    metadata, layer, cache, slots = attention_module.get_attention_context(name)
    _require(_LAYERS.get(name) is layer, "非已安装的 Attention 实例")
    capturing = torch.cuda.is_current_stream_capturing()
    mode = _cache_mode(cache.numel() == 0, metadata is not None, slots is not None, capturing)
    if mode == "profile":
        # 此分支永不捕获。真实 AOT 中保留同一个 opaque op，绑定 cache 后在运行时选 bound。
        cache = torch.empty((1, 2, 16, 2, 128), dtype=qkv.dtype, device=qkv.device)
        slots = torch.full((rows,), -1, dtype=torch.int64, device=qkv.device)
    else:
        _require(cache.ndim == 5 and tuple(cache.shape[1:]) == (2, 16, 2, 128)
                 and cache.stride() == (8192, 4096, 256, 128, 1)
                 and cache.dtype == qkv.dtype and cache.device == qkv.device,
                 "KV cache 不是已验 block/KV/token/head 布局")
        _require(slots.ndim == 1 and slots.shape[0] >= rows and slots.stride() == (1,)
                 and slots.dtype == torch.int64 and slots.device == qkv.device,
                 "GPU slot_mapping 布局/长度")
    # 真实行由 GPU slot >= 0 决定。这里传 padded M，不能捕获 metadata 中的 Python actual 数值。
    q = torch.empty((rows, 2048), dtype=qkv.dtype, device=qkv.device)
    k = torch.empty((rows, 256), dtype=qkv.dtype, device=qkv.device)
    _KERNEL.run(qkv, positions, table, k, q, rows * 256, rows * 2048,
                cache, slots, rows, stream=get_raw_stream(qkv.device.index))
    # 与 installed unified_kv_cache_update 相同的 hidden-cache 副作用 + 显式 dep 合同。
    dep = torch.empty(0, dtype=qkv.dtype, device=qkv.device)
    if mode == "bound" and not capturing and name not in _OBSERVED:
        _OBSERVED.add(name)
        print("BIV150_ROPE_KV_BOUND", json.dumps({"layer": name, "rows": rows,
              "cache_blocks": cache.shape[0], "gpu_slots": True}), flush=True)
    return q, k, dep


def _rope_kv_fake(qkv: torch.Tensor, positions: torch.Tensor, table: torch.Tensor,
                  layer_name: LayerNameType) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    rows = qkv.shape[0]
    return (qkv.new_empty((rows, 2048)), qkv.new_empty((rows, 256)), qkv.new_empty((0,)))


def _attention_after_write(layer, query, key, value, dep):
    # 固定目标的原 Attention.forward 后半：输出/view/原带装饰器 opaque attention 保持。
    rows = query.shape[0]
    output = torch.empty((rows, 2048), dtype=query.dtype, device=query.device)
    torch.ops.vllm.unified_attention_with_output(
        query.view(-1, 16, 128), key.view(-1, 2, 128), value.view(-1, 2, 128),
        output.view(-1, 16, 128), _encode_layer_name(layer.layer_name), kv_cache_dummy_dep=dep)
    return output


def _forward(self, positions, hidden_states):
    qkv, _ = self.qkv_proj(hidden_states)
    # 沿原 RotaryEmbedding 的 table dtype/device 合同；不重新算位置表或改旋转数学。
    table = self.rotary_emb._match_cos_sin_cache_dtype(qkv)
    q, k, dep = torch.ops.vllm.biv150_rope_kv(qkv, positions.flatten(), table,
                                             _encode_layer_name(self.attn.layer_name))
    # 原 V 仍是输入 view；custom op 只返回独立 Q/K，不把 alias 冒充新输出。
    v = qkv[:, 2304:]
    output = _attention_after_write(self.attn, q, k, v, dep)
    output, _ = self.o_proj(output)
    return output


def _model_scope(config):
    from vllm_fl.compile_semantics import native_model_matches
    hf = config.model_config.hf_config
    parallel = config.parallel_config
    return (native_model_matches(hf) and getattr(hf, "head_dim", None) == 128
            and getattr(hf, "max_position_embeddings", None) == 131072
            and config.model_config.dtype == torch.bfloat16
            and config.model_config.quantization is None
            and parallel.tensor_parallel_size == parallel.pipeline_parallel_size == 1
            and parallel.data_parallel_size == parallel.decode_context_parallel_size == 1
            and not parallel.use_ubatching and config.speculative_config is None
            and config.lora_config is None and config.kv_transfer_config is None
            and config.ec_transfer_config is None)


def _layer_scope(module, llama_class, rotary_class):
    from vllm.v1.attention.backend import AttentionType
    from vllm_fl.ops.rotary_embedding import RotaryEmbeddingFL
    a, rope = module.attn, module.rotary_emb
    return (type(module) is llama_class and "forward" not in module.__dict__
            and type(rope) in (rotary_class, RotaryEmbeddingFL)
            and (module.num_heads, module.num_kv_heads, module.head_dim,
                 module.q_size, module.kv_size) == (16, 2, 128, 2048, 256)
            and (rope.head_size, rope.rotary_dim, rope.max_position_embeddings,
                 rope.base, rope.is_neox_style) == (128, 128, 131072, 5000000, True)
            and not rope.use_flashinfer and not rope.use_aiter
            and rope.cos_sin_cache.shape == (131072, 128)
            and rope.cos_sin_cache.dtype == torch.bfloat16
            and rope.cos_sin_cache.stride() == (128, 1)
            and a.attn_type == AttentionType.DECODER and a.attn_backend.get_name() == "TRITON_ATTN"
            and not a.attn_backend.forward_includes_kv_cache_update
            and not a.use_direct_call and not a.calculate_kv_scales and a.query_quant is None
            and a.kv_sharing_target_layer_name is None and a.kv_cache_dtype in ("auto", "bfloat16")
            and a.head_size_v == 128 and a.sliding_window is None
            and not a.has_sink and not a.use_mm_prefix)


def _warm_kernel(table, device):
    global _KERNEL, _KERNEL_READY
    if _KERNEL_READY:
        return
    _require(not torch.cuda.is_current_stream_capturing(), "首次 Triton 编译不得位于 capture")
    from vllm_fl.patches.biv150_rope_kv_kernel import rope_kv_fused
    _KERNEL = rope_kv_fused
    # 一次私有预热；所有 slot=-1，不读取/改写模型 KV。完成后不保留 scratch。
    table = table.to(device=device, dtype=torch.bfloat16)
    qkv = torch.zeros((2048, 2560), dtype=torch.bfloat16, device=device)
    positions = torch.zeros(2048, dtype=torch.int64, device=device)
    slots = torch.full((2048,), -1, dtype=torch.int64, device=device)
    cache = torch.empty((1, 2, 16, 2, 128), dtype=torch.bfloat16, device=device)
    q = torch.empty((2048, 2048), dtype=torch.bfloat16, device=device)
    k = torch.empty((2048, 256), dtype=torch.bfloat16, device=device)
    for rows in (2048, 64, 32, 1):
        _KERNEL.run(qkv, positions, table, k, q, rows * 256, rows * 2048,
                    cache, slots, rows, stream=get_raw_stream(device.index))
    torch.cuda.synchronize(device)
    _require(bool(getattr(_KERNEL, "launchers", None)), "预热后没有可复用 launcher")
    _KERNEL_READY = True
    print("BIV150_ROPE_KV_WARMED", json.dumps({"rows": [2048, 64, 32, 1],
          "capture": False, "scratch_retained": False,
          "launcher_configs": [str(getattr(fn, "config", None))
                               for fn in (_KERNEL.launchers or [])]}), flush=True)


def install_on_model(model, config, device):
    """Worker.load_model 后、任何 profile/capture 前调用；不改 runner/P/Q 原件。"""
    global _REGISTERED
    if os.environ.get(_FEATURE, "1") != "1" or not _model_scope(config):
        return {"installed": False, "reason": "unsupported or disabled model"}
    props = torch.cuda.get_device_properties(device)
    if "BI-V150" not in props.name or props.multi_processor_count != 16 or props.major != 7:
        return {"installed": False, "reason": "unsupported hardware"}
    from vllm.model_executor.models.llama import LlamaAttention
    from vllm.model_executor.layers.rotary_embedding.base import RotaryEmbedding
    for module, pin in ((attention_module, _SOURCE_PINS["attention"]),
                        (inspect.getmodule(RotaryEmbedding), _SOURCE_PINS["rotary"]),
                        (inspect.getmodule(LlamaAttention), _SOURCE_PINS["llama"])):
        _require(hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == pin,
                 "installed attention/rotary/llama source changed")
    layers = [m for m in model.modules() if type(m) is LlamaAttention]
    if len(layers) == 42 and all(getattr(m.forward, "__func__", None) is _forward
                               and _LAYERS.get(m.attn.layer_name) is m.attn for m in layers):
        return {"installed": True, "already": True, "layers": 42}
    _require(LlamaAttention.forward.__module__ == "vllm.model_executor.models.llama"
             and LlamaAttention.forward.__code__.co_qualname == "LlamaAttention.forward",
             "LlamaAttention 已有未知 class wrapper")
    if len(layers) != 42 or not all(_layer_scope(m, LlamaAttention, RotaryEmbedding) for m in layers):
        return {"installed": False, "reason": "unsupported Attention/Rotary instances"}
    names = [m.attn.layer_name for m in layers]
    _require(len(set(names)) == 42, "重复 layer identity")
    _warm_kernel(layers[0].rotary_emb.cos_sin_cache, device)
    if not _REGISTERED:
        direct_register_custom_op(op_name="biv150_rope_kv", op_func=_rope_kv,
                                  mutates_args=[], fake_impl=_rope_kv_fake)
        _REGISTERED = True
    for module in layers:
        _LAYERS[module.attn.layer_name] = module.attn
        module.forward = types.MethodType(_forward, module)
    result = {"installed": True, "layers": 42, "kernel_warmed": _KERNEL_READY,
              "original_kv_update_bypassed_only_here": True, "qk_outputs_retained": True}
    print("BIV150_ROPE_KV_INSTALL", json.dumps(result, sort_keys=True), flush=True)
    return result
