"""局部实验工具，默认不安装：末层Attention之后只为实际logit行计算尾段。"""
from __future__ import annotations

import hashlib
from pathlib import Path

EXPECTED = {
    "llama": ("vllm.model_executor.models.llama", "1e1003454985bf86d3868a7755bcf5324676881548b3895809edf0b76698d384"),
    "linear": ("vllm.model_executor.layers.linear", "0bd60103d85d7183791077c46e0770d0a2adc8e8811b162b9084c3cbe92ba662"),
    "layernorm": ("vllm.model_executor.layers.layernorm", "696615d858292fea7a2942480803cd4c7d2d1e88d818bfe5cd9d695ac464f37c"),
    "activation": ("vllm.model_executor.layers.activation", "757209cef4b5cc091d29d95b4a6b29f2511984110c9b66810c760d4499cb156c"),
}


def query_end_rows(lengths, rows):
    """只接受已知的正整数CPU query长度；不读取GPU索引或按benchmark ID分派。"""
    if (not isinstance(rows, int) or isinstance(rows, bool) or rows <= 0
            or not isinstance(lengths, (tuple, list)) or not lengths):
        raise ValueError("positive CPU lengths/rows required")
    cursor, ends = 0, []
    for length in lengths:
        if type(length) is not int or length <= 0:
            raise ValueError("positive builtin query lengths required")
        cursor += length
        ends.append(cursor - 1)
    if cursor != rows:
        raise ValueError("query lengths must cover exactly the valid input rows")
    return tuple(ends)


def create(config, source_dir):
    """只在设备child内构造约80MiB随机权重的真实局部类，不构造模型／KV。"""
    import importlib
    import torch

    text = config.model_config.hf_text_config
    parallel = config.parallel_config
    if (Path(str(config.model_config.model).rstrip("/\\")).name != "MiniCPM5-2B"
            or config.model_config.dtype != torch.bfloat16
            or config.model_config.quantization is not None or config.quant_config is not None
            or config.speculative_config is not None or config.lora_config is not None
            or config.model_config.is_encoder_decoder
            or tuple(text.architectures) != ("LlamaForCausalLM",)
            or (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
                text.num_attention_heads, text.num_key_value_heads) != (2048, 6144, 42, 16, 2)
            or text.hidden_act != "silu" or text.rms_norm_eps != 1e-6
            or any(getattr(parallel, name) != 1 for name in
                   ("tensor_parallel_size", "pipeline_parallel_size", "data_parallel_size"))):
        raise RuntimeError("only the original single-device MiniCPM5-2B BF16 text tail")
    modules, sources = {}, {}
    for name, (qualified, expected) in EXPECTED.items():
        module = importlib.import_module(qualified)
        actual = Path(module.__file__)
        archived = Path(source_dir) / (name + ".py")
        if any(hashlib.sha256(path.read_bytes()).hexdigest() != expected for path in (actual, archived)):
            raise RuntimeError("exact installed/archived source required: " + name)
        modules[name] = module
        sources[name] = {"path": str(actual), "sha256": expected}

    # disable_tp=True明确使用真实类的TP1分支，不创建假的distributed group。
    old_dtype = torch.get_default_dtype()
    try:
        torch.set_default_dtype(torch.bfloat16)
        output_projection = modules["linear"].RowParallelLinear(
            2048, 2048, bias=False, quant_config=None, reduce_results=False,
            disable_tp=True, prefix="model.layers.41.self_attn.o_proj").to("cuda").eval()
        mlp = modules["llama"].LlamaMLP(
            2048, 6144, "silu", quant_config=None, bias=False, reduce_results=False,
            disable_tp=True, prefix="model.layers.41.mlp").to("cuda").eval()
        post_norm = modules["layernorm"].RMSNorm(2048, eps=1e-6).to("cuda").eval()
        final_norm = modules["layernorm"].RMSNorm(2048, eps=1e-6).to("cuda").eval()
    finally:
        torch.set_default_dtype(old_dtype)

    class Tail:
        def __init__(self):
            self.parts = (output_projection, post_norm, mlp, final_norm)
            self.sources = sources

        def __call__(self, attention_output, residual):
            # 对应 actual LlamaAttention最后的O投影、Decoder后半段及Model最终norm。
            if (attention_output.dtype != torch.bfloat16 or residual.dtype != torch.bfloat16
                    or attention_output.device != residual.device
                    or attention_output.device.type != "cuda"
                    or attention_output.ndim != 2 or attention_output.shape[1] != 2048
                    or residual.shape != attention_output.shape
                    or not attention_output.is_contiguous() or not residual.is_contiguous()):
                raise RuntimeError("plain contiguous BF16 tail matrices required")
            hidden, bias = output_projection(attention_output)
            if bias is not None:
                raise RuntimeError("unexpected output bias")
            hidden, updated_residual = modules["layernorm"].RMSNorm.forward_native(
                post_norm, hidden, residual)
            hidden = modules["llama"].LlamaMLP.forward(mlp, hidden)
            hidden, updated_residual = modules["layernorm"].RMSNorm.forward_native(
                final_norm, hidden, updated_residual)
            return hidden, updated_residual

        def selected(self, attention_output, residual, indices):
            # 两份gather都在候选计时内，不能只裁Attention output而保留错误的residual行。
            selected_output = torch.index_select(attention_output, 0, indices)
            selected_residual = torch.index_select(residual, 0, indices)
            return self(selected_output, selected_residual)

    return Tail()
