"""BI-V150 MiniCPM M64 down的无损N128布局；加载时计入显存。"""
import os

import torch

from vllm_fl.patches import biv150_nonly_down_kernel as kernel

_DEFINITION = None
_IMPLEMENTATION = None
_INSTALLED = False
_OBSERVED = False
_STATE = {"layers": 0, "packed_bytes": 0}


def _after_loading(layer):
    """由原process_weights_after_loading之后调用，不在forward/capture中分配。"""
    weight = getattr(layer, "weight", None)
    if (not layer.prefix.endswith(".mlp.down_proj") or weight is None
            or tuple(weight.shape) != (2048, 6144)
            or weight.dtype != torch.bfloat16 or weight.device.type != "cuda"
            or not weight.is_contiguous() or hasattr(layer, "_biv150_native_wq")):
        return
    with torch.cuda.device(weight.device):
        prop = torch.cuda.get_device_properties(weight.device)
        if "BI-V150" not in prop.name or prop.multi_processor_count != 16:
            return
        # 原权重保持给全部其它M；纯BF16重排，缓冲区归该层所有。
        packed = weight.detach().reshape(16, 128, 6144).permute(0, 2, 1).contiguous()
        old = getattr(layer, "_biv150_nonly_down_weight", None)
        layer.register_buffer("_biv150_nonly_down_weight", packed, persistent=False)
        if old is None:
            _STATE["layers"] += 1
        else:
            _STATE["packed_bytes"] -= old.numel() * old.element_size()
        _STATE["packed_bytes"] += packed.numel() * packed.element_size()
        if _STATE["layers"] in (1, 42):
            print("BIV150_NONLY_DOWN_WEIGHT", {
                "prefix": layer.prefix, **_STATE,
                "allocation": "process_weights_after_loading, before KV memory profiling",
                "keeps_original_weight": True,
            }, flush=True)


def _linear(x, weight, packed):
    global _OBSERVED
    if not (x.ndim == weight.ndim == 2 and packed.ndim == 3
            and tuple(x.shape) == (64, 6144)
            and tuple(weight.shape) == (2048, 6144)
            and tuple(packed.shape) == (16, 6144, 128)
            and x.dtype == weight.dtype == packed.dtype == torch.bfloat16
            and x.device == weight.device == packed.device and x.device.type == "cuda"
            and x.is_contiguous() and weight.is_contiguous() and packed.is_contiguous()):
        # 保持main6971原M1–8及M>8路径；不把M63组件正确性泛化为生产资格。
        return torch.ops.biv150_stable_small_o.linear(x, weight)
    output = torch.empty((64, 2048), device=x.device, dtype=x.dtype)
    compiled = kernel.launch_into(x, packed, output, kernel.CONFIG)
    if not _OBSERVED and not torch.cuda.is_current_stream_capturing():
        _OBSERVED = True
        metadata = getattr(compiled, "metadata", None)
        print("BIV150_NONLY_DOWN_SELECTED", {
            "rows": 64, "input_columns": 6144, "output_columns": 2048,
            "packed_shape": tuple(packed.shape), "config": kernel.CONFIG,
            "kernel_hash": getattr(metadata, "hash", None),
            "use_sme": getattr(metadata, "use_sme", None),
            "shared": getattr(metadata, "shared", None),
        }, flush=True)
    return output


def _register():
    global _DEFINITION, _IMPLEMENTATION
    if _DEFINITION is not None:
        return
    definition = torch.library.Library("biv150_nonly_down", "DEF")
    definition.define("linear(Tensor input, Tensor weight, Tensor packed) -> Tensor")
    implementation = torch.library.Library("biv150_nonly_down", "IMPL", "CUDA")
    implementation.impl("linear", _linear)

    @torch.library.register_fake("biv150_nonly_down::linear")
    def fake(x, weight, packed):
        return torch.empty((x.shape[0], weight.shape[0]), dtype=x.dtype, device=x.device)

    _DEFINITION, _IMPLEMENTATION = definition, implementation


def install():
    global _INSTALLED
    if os.environ.get("VLLM_FL_BIV150_NONLY_DOWN", "1") != "1":
        return {"installed": False, "reason": "disabled"}
    if _INSTALLED:
        return {"installed": True, "reason": "already installed"}
    from vllm.platforms import current_platform
    from vllm_fl.patches.biv150_native_w8a8 import _eligible_model
    from vllm_fl.patches import biv150_stable_small_o
    if getattr(current_platform, "vendor_name", None) != "iluvatar" or not _eligible_model():
        return {"installed": False, "reason": "unsupported platform or model"}
    from vllm.distributed import get_tensor_model_parallel_world_size
    if get_tensor_model_parallel_world_size() != 1:
        return {"installed": False, "reason": "TP1 required"}
    if not biv150_stable_small_o.install().get("installed"):
        return {"installed": False, "reason": "original stable projection path unavailable"}
    from vllm.model_executor.layers.linear import UnquantizedLinearMethod
    after_original = UnquantizedLinearMethod.process_weights_after_loading
    apply_original = UnquantizedLinearMethod.apply
    _register()

    def after(self, layer):
        result = after_original(self, layer)
        _after_loading(layer)
        return result

    def apply(self, layer, x, bias=None):
        packed = getattr(layer, "_biv150_nonly_down_weight", None)
        if (bias is not None or packed is None or not layer.prefix.endswith(".mlp.down_proj")
                or hasattr(layer, "_biv150_native_wq")):
            return apply_original(self, layer, x, bias)
        # M64分流留在opaque内部，保持Dynamo的动态行维。
        output = torch.ops.biv150_nonly_down.linear(
            x.reshape(-1, 6144), layer.weight, packed)
        return output.reshape(*x.shape[:-1], 2048)

    UnquantizedLinearMethod.process_weights_after_loading = after
    UnquantizedLinearMethod.apply = apply
    _INSTALLED = True
    return {"installed": True, "scope": "BF16 TP1 MiniCPM down M64 only",
            "packed_per_layer_bytes": 25165824, "expected_layers": 42,
            "expected_extra_bytes": 1056964608,
            "other_rows": "original stable projection opaque",
            "weight_lifetime": "layer-owned nonpersistent buffer, allocated before KV profile"}
