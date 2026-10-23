"""一次真实计算序命中的原序/P logits 诊断；无采样、状态回滚或数值容差放宽。"""
import hashlib
import json
import os
from pathlib import Path
import sys

ENV = 'BIV150_COMPUTE_ORDER_SHADOW_DIR'
_ATTEMPT = '_biv150_compute_order_shadow_attempted'
_HOLD = []  # 异常/未 settle 时仍保留现场，禁止释放后继续服务。
PINS = {
    'vllm.model_executor.models.llama': '1e1003454985bf86d3868a7755bcf5324676881548b3895809edf0b76698d384',
    'vllm.model_executor.layers.linear': '0bd60103d85d7183791077c46e0770d0a2adc8e8811b162b9084c3cbe92ba662',
    'vllm.model_executor.layers.layernorm': '696615d858292fea7a2942480803cd4c7d2d1e88d818bfe5cd9d695ac464f37c',
    'vllm.model_executor.layers.activation': '757209cef4b5cc091d29d95b4a6b29f2511984110c9b66810c760d4499cb156c',
    'vllm.v1.attention.backends.triton_attn': '1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605',
    'vllm.v1.attention.ops.triton_reshape_and_cache_flash': 'f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb',
}
ATTENTION = '3414faca4cc04c699dbb880ba1761230e1ed97035f2934604cad9a5490f4dba1'


def _write(folder, name, value):
    (folder / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def _rng(runner, torch):
    return [torch.get_rng_state().clone(), torch.cuda.get_rng_state(0).clone()] + [
        generator.get_state().clone() for _, generator in sorted(runner.input_batch.generators.items())]


def _same_rng(before, after, torch):
    return len(before) == len(after) and all(torch.equal(a, b) for a, b in zip(before, after))


def _geometry(runner, plan, scheduled, np):
    n, total = plan.number, plan.total
    q = scheduled.astype(np.int64, copy=True)
    c = runner.input_batch.num_computed_tokens_cpu[:n].astype(np.int64, copy=True)
    table = runner.input_batch.block_table[0]
    owned = table.num_blocks_per_row[:n]
    pages = table.block_table.np[:n]
    pool = runner.kv_cache_config.num_blocks
    prefix_masks, segments = {}, []
    for i in range(n):
        if c[i] < 0 or q[i] < 1 or c[i] + q[i] > runner.max_model_len:
            raise ValueError('请求逻辑范围不明')
        need = (int(c[i] + q[i]) + 15) // 16
        if need > int(owned[i]) or need > pages.shape[1]:
            raise ValueError('本步写超出当前owned页')
        active_pages = pages[i, :need]
        if np.any(active_pages <= 0) or np.any(active_pages >= pool):
            raise ValueError('null/越界物理页')
        for j in range((int(c[i]) + 15) // 16):
            mask = (1 << min(16, int(c[i]) - j * 16)) - 1
            p = int(pages[i, j])
            prefix_masks[p] = prefix_masks.get(p, 0) | mask
        positions = np.arange(int(c[i]), int(c[i] + q[i]), dtype=np.int64)
        segments.append(pages[i, positions // 16].astype(np.int64) * 16 + positions % 16)
    canonical = np.concatenate(segments)
    if canonical.shape != (total,) or len(np.unique(canonical)) != total:
        raise ValueError('当前写slot有alias')
    for slot in canonical.tolist():
        if prefix_masks.get(slot // 16, 0) & (1 << (slot % 16)):
            raise ValueError('当前写slot与活动请求旧prefix相交')
    permuted = np.concatenate([segments[int(i)] for i in plan.permutation])
    return canonical, permuted, c, q


def create(runner, plan, scheduler_output, scheduled):
    """首次自然Plan、首次原prepare之前；不符合时只跳诊断，候选仍按原逻辑。"""
    if plan is None or not os.environ.get(ENV) or getattr(runner, _ATTEMPT, False):
        return None
    setattr(runner, _ATTEMPT, True)
    folder = Path(os.environ[ENV]).resolve() / str(os.getpid())
    folder.mkdir(parents=True, exist_ok=False)
    import numpy as np
    import torch
    try:
        for name, pin in PINS.items():
            module = sys.modules.get(name)
            if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
                raise ValueError('actual源不匹配：' + name)
        backend = sys.modules['vllm.v1.attention.backends.triton_attn']
        llama = sys.modules['vllm.model_executor.models.llama']
        model = runner.get_model()
        if (type(model) is not llama.LlamaForCausalLM or type(model.model) is not llama.LlamaModel
                or model.training or len(model.model.layers) != 42
                or runner.num_accepted_tokens_event is not None or runner.input_batch.req_prompt_embeds
                or runner.calculate_kv_scales or runner.use_aux_hidden_state_outputs
                or runner.broadcast_pp_output or runner.is_pooling_model
                or runner.vllm_config.kv_transfer_config is not None
                or runner.vllm_config.ec_transfer_config is not None
                or scheduler_output.scheduled_encoder_inputs
                or scheduler_output.scheduled_spec_decode_tokens
                or torch.cuda.is_current_stream_capturing()):
            raise ValueError('非已闭合普通text/noSpec/TP1稳态')
        # 防止额外用户hook或训练支路改变第二次forward的状态/RNG。
        for module in model.modules():
            if module.training or module._forward_hooks or module._forward_pre_hooks or module._backward_hooks:
                raise ValueError('模型训练态或实例hook未闭合')
        hooks = torch.nn.modules.module
        if hooks._global_forward_hooks or hooks._global_forward_pre_hooks or hooks._global_backward_hooks:
            raise ValueError('存在全局module hook')
        contexts = runner.compilation_config.static_forward_context
        if len(contexts) != 42 or len(runner.kv_caches) != 42:
            raise ValueError('非42层普通cache')
        signatures = []
        cache_ids = {id(t) for t in runner.kv_caches}
        for name, layer in contexts.items():
            if hashlib.sha256(Path(type(layer).forward.__code__.co_filename).read_bytes()).hexdigest() != ATTENTION:
                raise ValueError('非已核actual Attention.forward')
            if (layer.calculate_kv_scales or layer.query_quant is not None
                    or layer.kv_sharing_target_layer_name is not None
                    or type(layer.impl) is not backend.TritonAttentionImpl
                    or layer.attn_backend is not backend.TritonAttentionBackend
                    or backend.TritonAttentionBackend.forward_includes_kv_cache_update
                    or layer.impl._kv_quant_mode != 0 or layer.impl.attn_type != backend.AttentionType.DECODER
                    or id(layer.kv_cache) not in cache_ids):
                raise ValueError('Attention有量化/校准/共享/未知writer')
            t = layer.kv_cache
            pool = runner.kv_cache_config.num_blocks
            if (tuple(t.shape) != (pool, 2, 16, 2, 128) or tuple(t.stride()) != (8192, 4096, 256, 128, 1)
                    or t.dtype != torch.bfloat16 or str(t.device) != 'cuda:0' or t.storage_offset() != 0):
                raise ValueError('非normal42 NHD cache')
            storage = t.untyped_storage()
            if storage.nbytes() != pool * 16384:
                raise ValueError('cache storage范围未知')
            signatures.append((storage.data_ptr(), storage.nbytes()))
        ranges = sorted((ptr, ptr + size) for ptr, size in signatures)
        if any(b > c for (_, b), (c, _) in zip(ranges, ranges[1:])):
            raise ValueError('42层cache storage相交')
        original, permuted, c, q = _geometry(runner, plan, scheduled, np)
        session = Session(runner, plan, folder, torch, original, permuted)
        session.qualification = dict(pid=os.getpid(), N=plan.number, M=plan.total,
            Dprefix=plan.prefix, Dall=plan.dall, outside=plan.outside,
            current_slots_unique=True, current_vs_all_active_prefix_disjoint=True,
            layers=42, normal_cache_nonalias=True, computed=c.tolist(), scheduled=q.tolist(),
            permutation=plan.permutation.tolist(), sampler_order='original_request_rows',
            extra_sampling_calls=0, numerical_tolerance_calibrated=False)
        _write(folder, 'qualification.json', session.qualification)
        _HOLD.append(session)
        return session
    except Exception as error:
        _write(folder, 'result.json', dict(status='unsupported_before_shadow', pid=os.getpid(),
            reason=type(error).__name__ + ': ' + str(error), actual_P_numerical_coverage=False))
        print('BIV150_COMPUTE_ORDER_SHADOW_UNSUPPORTED ' + str(folder), flush=True)
        return None


class Session:
    def __init__(self, runner, plan, folder, torch, original, permuted):
        self.runner, self.plan, self.folder, self.torch = runner, plan, folder, torch
        self.original, self.permuted = original, permuted
        self.stream = torch.cuda.current_stream(0)
        self.started = False

    def check_slots(self, slots, *, permuted):
        import numpy as np
        if type(slots) is not dict or len(slots) != 42:
            raise RuntimeError('actual每层slot字典不匹配；诊断中止')
        values = list(slots.values())
        first = values[0]
        if (first.ndim != 1 or first.shape[0] != self.plan.total
                or any(t.data_ptr() != first.data_ptr() or tuple(t.shape) != tuple(first.shape) for t in values)
                or self.torch.cuda.current_stream(0) != self.stream):
            raise RuntimeError('actual writer slot/currentstream不匹配')
        actual = first.detach().cpu().numpy()  # 首次forward之前阻塞，兼做原H2D完成边界。
        if not np.array_equal(actual, self.permuted if permuted else self.original):
            raise RuntimeError('actual writer slots与CPU安全几何不符')

    def shadow(self, *, input_ids, positions, inputs_embeds, intermediate_tensors, model_kwargs,
               attn_metadata, slot_mappings, batch_desc, mode, num_tokens, num_tokens_across_dp,
               ubatch_slices):
        from vllm.forward_context import set_forward_context
        if (inputs_embeds is not None or intermediate_tensors is not None or model_kwargs
                or num_tokens != self.plan.total or num_tokens_across_dp is not None or ubatch_slices
                or mode != self.plan.state['mode'].NONE):
            raise RuntimeError('shadow实际上下文未知；不执行原序forward')
        self.check_slots(slot_mappings, permuted=False)
        self.rng_before = _rng(self.runner, self.torch)
        self.started = True
        _write(self.folder, 'started.json', dict(status='shadow_started', pid=os.getpid()))
        # 此处之后无捕获回原路；任何异常终止本次服务，不能重试生产forward。
        with set_forward_context(attn_metadata, self.runner.vllm_config, num_tokens=num_tokens,
                num_tokens_across_dp=None, cudagraph_runtime_mode=mode, batch_descriptor=batch_desc,
                ubatch_slices=ubatch_slices, slot_mapping=slot_mappings, skip_compiled=False):
            hidden = self.runner._model_forward(input_ids=input_ids, positions=positions,
                intermediate_tensors=None, inputs_embeds=None)
        ends = self.runner.query_start_loc.gpu[1:self.plan.number + 1] - 1
        logits = self.runner.model.compute_logits(hidden[ends])
        # 阻塞且独立CPU storage：所有原序H2D/forward完成才允许重写原pinned staging。
        self.baseline = logits.detach().float().cpu().clone()
        if not _same_rng(self.rng_before, _rng(self.runner, self.torch), self.torch):
            raise RuntimeError('原序shadow改变RNG；终止，不恢复/掩盖')
        import numpy as np
        np.save(self.folder / 'original-logits.npy', self.baseline.numpy(), allow_pickle=False)
        self.original_metadata = attn_metadata  # 保留动态plan与异步tensor至生产完成。

    def finish(self, logits):
        import numpy as np
        torch = self.torch
        production = logits.detach().float().cpu().clone()
        np.save(self.folder / 'permuted-logits.npy', production.numpy(), allow_pickle=False)
        if production.shape != self.baseline.shape or production.shape[0] != self.plan.number:
            raise RuntimeError('两路原N logits形状不一致')
        finite = torch.isfinite(self.baseline) & torch.isfinite(production)
        delta = (production - self.baseline).abs()
        good = delta[finite]
        per_row = []
        for i in range(self.plan.number):
            v = delta[i][finite[i]]
            per_row.append(dict(row=i, all_finite=bool(finite[i].all()),
                max_abs=float(v.max()) if v.numel() else None,
                mean_abs=float(v.mean()) if v.numel() else None,
                original_top1=int(self.baseline[i].argmax()), permuted_top1=int(production[i].argmax())))
        rng_equal = _same_rng(self.rng_before, _rng(self.runner, torch), torch)
        result = dict(status='diagnostic_completed', **self.qualification,
            original_and_P_logits_shape=list(production.shape),
            strict_bits=bool(torch.equal(self.baseline.view(torch.int32), production.view(torch.int32))),
            comparison_storage='float32_CPU_snapshot_bits',
            original_all_finite=bool(torch.isfinite(self.baseline).all()),
            permuted_all_finite=bool(torch.isfinite(production).all()),
            max_abs=float(good.max()) if good.numel() else None,
            mean_abs=float(good.mean()) if good.numel() else None,
            top1_equal_rows=sum(r['original_top1'] == r['permuted_top1'] for r in per_row),
            rng_unchanged_before_sampling=rng_equal, per_row=per_row,
            no_accuracy_or_token_bitwise_claim=True, diagnostic_not_performance=True)
        _write(self.folder, 'result.json', result)
        print('BIV150_COMPUTE_ORDER_SHADOW_COMPLETED ' + json.dumps(dict(pid=os.getpid(),
            N=self.plan.number, M=self.plan.total, strict_bits=result['strict_bits'],
            max_abs=result['max_abs'], rng_unchanged=rng_equal)), flush=True)
        if not rng_equal or not result['original_all_finite'] or not result['permuted_all_finite']:
            raise RuntimeError('shadow诊断发现RNG变化或非有限值')
