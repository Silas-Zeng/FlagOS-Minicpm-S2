"""仅真实 mixed 批次提前执行末层采样选行；返回原 M 行布局。"""
import functools
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import types

import numpy as np
import torch
from torch import nn
from vllm.compilation.backends import set_model_tag
from vllm.compilation.decorators import support_torch_compile
from vllm.config import CUDAGraphMode, CompilationMode
from vllm.forward_context import get_forward_context, is_forward_context_available

_FEATURE = "VLLM_FL_BIV150_FINAL_FFN_ROWS"
_MARKER = "_biv150_final_ffn_rows"
_TAG = "biv150_final_ffn_rows"
_PINS = {
    "vllm.model_executor.models.llama": "1e1003454985bf86d3868a7755bcf5324676881548b3895809edf0b76698d384",
    "vllm.compilation.decorators": "dd7167637a478aeaea3f2410a727ddefc702bda1d9bf632831c2a8b4811ebb1e",
    "vllm.compilation.backends": "aa329761c7b8a959f64d303f3dbb790781e1e1f23d0fc6e3755aeb6de083e48a",
    "vllm.compilation.wrapper": "c1b1fca679ea16aa07a696831a810c0d531da2bb0ea32dd6f1a95cdaef36de07",
    "vllm.compilation.piecewise_backend": "6525318ff3ca2e4978e24dd9232a7ae0a02e920e19604b83db6f6043d1f8a54d",
    "vllm_fl.worker.model_runner": "677def25d5391887145b0bbabb2222531887c6f7c48b6ea53c1859ad08d8ef61",
    "vllm_fl.patches.biv150_compute_order": "fb8509c5fe7e92960b95c4891a42aa72a236fc98ef54724296fe2779e293f44a"
}


@support_torch_compile(dynamic_arg_dims={
    "input_ids": {0: "tokens"}, "positions": {0: "tokens"},
    "tail_logits_indices": {0: "samples"},
})
class DenseFinalRows(nn.Module):
    """独立编译入口；只共享已经加载的模块，不创建或复制参数。"""
    def __init__(self, *, backbone, vllm_config):
        super().__init__()
        self.embed_tokens = backbone.embed_tokens
        self.layers = backbone.layers
        self.norm = backbone.norm
        self.training = backbone.training

    def forward(self, input_ids: torch.Tensor, positions: torch.Tensor,
                tail_logits_indices: torch.Tensor) -> torch.Tensor:
        hidden = self.embed_tokens(input_ids)
        residual = None
        for index in range(41):
            hidden, residual = self.layers[index](positions, hidden, residual)
        last = self.layers[41]
        hidden, residual = last.input_layernorm(hidden, residual)
        # 所有 Attention、KV 写入与 o_proj 仍覆盖全部 M 行。
        hidden = last.self_attn(positions=positions, hidden_states=hidden)
        selected = hidden[tail_logits_indices]
        selected_residual = residual[tail_logits_indices]
        selected, selected_residual = last.post_attention_layernorm(selected, selected_residual)
        selected = last.mlp(selected)
        selected, _ = self.norm(selected, selected_residual)
        # 原 runner 仍执行 hidden_states[logits_indices]；未选行没有其他消费者。
        dense = selected.new_zeros((input_ids.shape[0], 2048))
        dense.index_copy_(0, tail_logits_indices.to(dtype=torch.int64), selected)
        return dense


class _Epoch:
    """一轮 execute 内一次 prepare→forward；失败与提前返回均清空。"""
    def __init__(self):
        self.number = 0
        self.active = False
        self.output = None
        self.pending = None
        self.prepared = False
        self.forwarded = False
        self.selected = 0

    def enter(self, output):
        if self.active:
            raise RuntimeError("末层选行 execute 不允许重入")
        self.number += 1
        self.active, self.output = True, output
        self.pending = None
        self.prepared = self.forwarded = False

    def leave(self):
        self.pending = self.output = None
        self.active = self.prepared = self.forwarded = False

    def stage(self, output, indices, proof):
        if not self.active or output is not self.output or self.prepared or self.forwarded:
            return False
        self.prepared = True
        if proof is not None:
            self.pending = (self.number, indices, proof)
        return True

    def consume(self):
        pending, self.pending = self.pending, None
        if not self.active or self.forwarded:
            return None
        self.forwarded = True
        if pending is None or pending[0] != self.number:
            return None
        return pending


def _scope(runner):
    from vllm_fl.compile_semantics import native_model_matches
    c = runner.vllm_config
    p = c.parallel_config
    return (native_model_matches(c.model_config.hf_config)
            and c.model_config.dtype == torch.bfloat16 and c.model_config.quantization is None
            and not c.model_config.is_encoder_decoder
            and all(getattr(p, name, None) == 1 for name in (
                "tensor_parallel_size", "pipeline_parallel_size",
                "decode_context_parallel_size", "data_parallel_size"))
            and not p.use_ubatching and c.speculative_config is None
            and c.lora_config is None and c.kv_transfer_config is None and c.ec_transfer_config is None
            and c.compilation_config.mode == CompilationMode.VLLM_COMPILE
            and c.compilation_config.cudagraph_mode == CUDAGraphMode.FULL_DECODE_ONLY
            and not c.compilation_config.cudagraph_copy_inputs
            and c.compilation_config.backend == "inductor"
            # 本实例 range 编译保留 M/S；single-size 会把所有符号强设同一值。
            and c.compilation_config.compile_sizes == []
            and c.compilation_config.compile_ranges_endpoints == [2048]
            and c.compilation_config.dynamic_shapes_config.type.name == "BACKED"
            and runner.max_num_tokens == 2048
            and not c.cache_config.kv_sharing_fast_prefill
            and runner.speculative_config is None and not runner.num_prompt_logprobs
            and not runner.use_aux_hidden_state_outputs and not runner.broadcast_pp_output
            and not runner.is_pooling_model and not runner.supports_mm_inputs
            and not runner.enable_prompt_embeds and not runner.uses_mrope and runner.uses_xdrope_dim == 0
            and not runner.use_async_spec_decode and runner.num_spec_tokens == 0
            and runner.use_async_scheduling and runner.prepare_inputs_event is not None
            and not runner.routed_experts_initialized and not runner.shared_kv_cache_layers
            and runner.cross_layers_kv_cache is None)


def _cpu_plan(runner, output, scheduled, compute_order):
    """只用原 CPU 调度合同证明唯一性；绝不重建或读回 GPU indices。"""
    n, total = runner.input_batch.num_reqs, output.total_num_scheduled_tokens
    ids = runner.input_batch.req_ids
    if (type(total) is not int or not 2 <= n <= 64 or not n < total <= runner.max_num_tokens
            or type(scheduled) is not np.ndarray or scheduled.dtype != np.int32
            or scheduled.shape != (n,) or not scheduled.flags.c_contiguous
            or len(ids) != n or len(set(ids)) != n
            or any(runner.input_batch.req_id_to_index.get(rid) != i for i, rid in enumerate(ids))
            or any(output.num_scheduled_tokens.get(rid) != int(scheduled[i]) for i, rid in enumerate(ids))
            or int(scheduled.min()) != 1 or int(scheduled.max()) <= 1
            or int(scheduled.sum()) != total or output.scheduled_spec_decode_tokens
            or output.scheduled_encoder_inputs):
        return None
    # 正数累计和严格递增；P 仅是对这组末位置的双射重排。
    if compute_order is not None:
        from vllm_fl.patches import biv150_compute_order as p
        if type(compute_order) is not p.Plan:
            return None
        perm, inverse = compute_order.permutation, compute_order.inverse
        if (compute_order.number != n or compute_order.total != total
                or not np.array_equal(np.sort(perm), np.arange(n))
                or not np.array_equal(inverse[perm], np.arange(n))
                or not np.array_equal(compute_order.scheduled, scheduled[perm])
                or not np.array_equal(compute_order.ends_by_original,
                                      np.cumsum(scheduled[perm], dtype=np.int32)[inverse])):
            return None
    return {"M": total, "S": n, "p_reordered": compute_order is not None}


def _can_forward(runner, indices, proof, input_ids, positions, intermediate_tensors, inputs_embeds, kwargs):
    if (not _scope(runner) or kwargs or intermediate_tensors is not None or inputs_embeds is not None
            or not is_forward_context_available() or torch.cuda.is_current_stream_capturing()):
        return False
    context = get_forward_context()
    descriptor = context.batch_descriptor
    if (context.cudagraph_runtime_mode != CUDAGraphMode.NONE or context.skip_compiled
            or context.ubatch_slices is not None or context.dp_metadata is not None
            or not isinstance(context.attn_metadata, dict) or not context.attn_metadata
            or descriptor is None or descriptor.num_tokens != proof["M"]
            or descriptor.num_reqs not in (None, proof["S"])):
        return False
    return (isinstance(input_ids, torch.Tensor) and isinstance(positions, torch.Tensor)
            and isinstance(indices, torch.Tensor)
            and input_ids.shape == (proof["M"],) and input_ids.dtype == torch.int32
            and positions.shape == (proof["M"],) and positions.dtype == torch.int64
            and indices.shape == (proof["S"],) and indices.dtype == torch.int32
            and all(t.device == runner.device and t.stride() == (1,)
                    for t in (input_ids, positions, indices)))


def _bind_wrappers(runner, dense):
    state = _Epoch()
    original_execute = runner.execute_model
    original_prepare = runner._prepare_inputs
    original_forward = runner._model_forward

    @functools.wraps(original_execute)
    def execute(self, scheduler_output, intermediate_tensors=None):
        state.enter(scheduler_output)
        try:
            # 保存的 bound method 保留原 managed_inference_mode 装饰层。
            return original_execute(scheduler_output, intermediate_tensors)
        finally:
            state.leave()

    @functools.wraps(original_prepare)
    def prepare(self, scheduler_output, num_scheduled_tokens, compute_order=None):
        state.pending = None
        result = original_prepare(scheduler_output, num_scheduled_tokens, compute_order=compute_order)
        if state.active and scheduler_output is state.output and _scope(self):
            proof = _cpu_plan(self, scheduler_output, num_scheduled_tokens, compute_order)
            if result[1] is not None:
                proof = None
            state.stage(scheduler_output, result[0], proof)
        return result

    @functools.wraps(original_forward)
    def forward(self, input_ids=None, positions=None, intermediate_tensors=None, inputs_embeds=None, **kwargs):
        pending = state.consume()
        if pending is not None:
            epoch, indices, proof = pending
            if _can_forward(self, indices, proof, input_ids, positions, intermediate_tensors, inputs_embeds, kwargs):
                # 显式 Tensor 入编译边界；tag 也覆盖 AOT 恢复创建 backend 的过程。
                # 一旦提交候选，不捕获异常重跑原模型，避免重复 KV/模型副作用。
                with set_model_tag(_TAG):
                    result = dense(input_ids, positions, indices)
                state.selected += 1
                if state.selected == 1:
                    print("BIV150_FINAL_FFN_ROWS_FIRST_SELECTED", json.dumps({
                        **proof, "epoch": epoch, "runtime_mode": "NONE", "backend_prefix": _TAG,
                        "dense_rows": proof["M"], "original_gpu_indices": True,
                        "original_runner_gather": True, "o_proj_pruned": False}), flush=True)
                return result
        return original_forward(input_ids=input_ids, positions=positions,
            intermediate_tensors=intermediate_tensors, inputs_embeds=inputs_embeds, **kwargs)

    replacements = {"execute_model": execute, "_prepare_inputs": prepare, "_model_forward": forward}
    try:
        for name, function in replacements.items():
            setattr(runner, name, types.MethodType(function, runner))
        setattr(runner, _MARKER, {"epoch": state, "module": dense})
    except BaseException:
        for name in replacements:
            runner.__dict__.pop(name, None)
        runner.__dict__.pop(_MARKER, None)
        raise
    return state


def install_on_runner(runner):
    """load 后安装；原 self.model/profile/capture 不替换，不预分配设备缓冲。"""
    if os.environ.get(_FEATURE, "1") != "1":
        return {"installed": False, "reason": "disabled"}
    if hasattr(runner, _MARKER):
        return {"installed": True, "already": True}
    try:
        if not _scope(runner):
            return {"installed": False, "reason": "unsupported model/runner"}
        props = torch.cuda.get_device_properties(runner.device)
        if "BI-V150" not in props.name or props.multi_processor_count != 16 or props.major != 7:
            return {"installed": False, "reason": "unsupported device"}
        from vllm.model_executor.models import llama
        from vllm.compilation import piecewise_backend  # 读取已核 range 语义身份，不执行编译。
        from vllm_fl.worker import model_runner
        for name, pin in _PINS.items():
            module = sys.modules.get(name)
            if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
                return {"installed": False, "reason": "source changed: " + name}
        if type(runner) is not model_runner.ModelRunnerFL:
            return {"installed": False, "reason": "unknown runner class"}
        for name in ("execute_model", "_prepare_inputs", "_model_forward"):
            method = getattr(runner, name)
            original = inspect.unwrap(method.__func__)
            if (name in runner.__dict__ or method.__func__ is not getattr(type(runner), name)
                    or original.__globals__ is not vars(model_runner)
                    or original.__code__.co_qualname != "ModelRunnerFL." + name):
                return {"installed": False, "reason": "unknown runner binding: " + name}
        model = runner.get_model()
        backbone = model.model
        if (type(model) is not llama.LlamaForCausalLM or type(backbone) is not llama.LlamaModel
                or backbone.start_layer != 0 or backbone.end_layer != 42 or len(backbone.layers) != 42
                or any(type(layer) is not llama.LlamaDecoderLayer for layer in backbone.layers)
                or any("forward" in obj.__dict__ for obj in (model, backbone, *backbone.layers))
                or any(type(layer.self_attn) is not llama.LlamaAttention
                       or "forward" in layer.self_attn.__dict__ for layer in backbone.layers)
                or hasattr(backbone.layers[41].mlp.gate_up_proj, "_biv150_native_wq")):
            return {"installed": False, "reason": "unknown normal42 backbone"}
        with set_model_tag(_TAG):
            dense = DenseFinalRows(backbone=backbone, vllm_config=runner.vllm_config)
        if dense.layers is not backbone.layers or dense.embed_tokens is not backbone.embed_tokens or dense.norm is not backbone.norm:
            raise RuntimeError("末层入口没有共享原权重模块")
        state = _bind_wrappers(runner, dense)
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        # 未选择模型执行，静态未知布局保持原路；不捕获已提交 forward 的异常。
        return {"installed": False, "reason": repr(error)}
    receipt = {"installed": True, "layers": 42, "selected_ffn_layer": 41,
               "backend_prefix": _TAG, "explicit_samples_tensor": True,
               "shared_weights": True, "dense_output": True, "runner_source_unchanged": True,
               "profile_and_capture_original": True, "epoch": state.number}
    print("BIV150_FINAL_FFN_ROWS_INSTALL", json.dumps(receipt), flush=True)
    return receipt
