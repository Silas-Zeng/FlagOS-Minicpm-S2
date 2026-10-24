"""一次真实计算序命中的原序/P logits 诊断；无采样、状态回滚或数值容差放宽。"""
import hashlib
import json
import os
from pathlib import Path
import sys

ENV = 'BIV150_COMPUTE_ORDER_STRUCTURE_DIR'
_ATTEMPT = '_biv150_compute_order_structure_attempted'
_PENDING = {}
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
        session.scheduler_output = scheduler_output
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
        print('BIV150_COMPUTE_ORDER_STRUCTURE_UNSUPPORTED ' + str(folder), flush=True)
        return None


class Session:
    """原序仅prepare快照→P生产一次；只验证整数映射及真实采样入口。"""
    def __init__(self, runner, plan, folder, torch, original, permuted):
        import numpy as np
        self.runner, self.plan, self.folder, self.torch = runner, plan, folder, torch
        self.batch = runner.input_batch
        self.req_ids = tuple(self.batch.req_ids)
        self.sampling_metadata = self.batch.sampling_metadata
        self.sampler = runner.sampler
        self.stream = torch.cuda.current_stream(0)
        self.sample_calls = 0
        self.logits = None
        self.original_ids = self.original_positions = None

    def shadow(self, *, input_ids, positions, inputs_embeds, intermediate_tensors, model_kwargs,
               attn_metadata, slot_mappings, batch_desc, mode, num_tokens, num_tokens_across_dp,
               ubatch_slices):
        import numpy as np
        if (inputs_embeds is not None or intermediate_tensors is not None or model_kwargs
                or num_tokens != self.plan.total or num_tokens_across_dp is not None or ubatch_slices
                or mode != self.plan.state['mode'].NONE or self.torch.cuda.current_stream(0) != self.stream):
            raise RuntimeError('原序prepare实际上下文未知，诊断中止')
        # .cpu()默认阻塞；原H2D完成后才可重写共用pinned staging。
        self.original_ids = input_ids.detach().cpu().clone().numpy()
        self.original_positions = positions.detach().cpu().clone().numpy()
        n, m = self.plan.number, self.plan.total
        q = np.array([self.scheduler_output.num_scheduled_tokens[rid] for rid in self.req_ids], dtype=np.int64)
        if (len(self.req_ids) != n or q.shape != (n,) or int(q.sum()) != m
                or self.original_ids.shape != (m,) or self.original_positions.shape != (m,)):
            raise RuntimeError('完整M/原N请求行范围不符')
        # 独立从原请求序q构造stable q1分区，不能复用Plan.ends/inverse作为期望值。
        starts = np.concatenate(([0], np.cumsum(q)))
        order = [i for i, count in enumerate(q) if count == 1] + [i for i, count in enumerate(q) if count != 1]
        tokens = np.concatenate([np.arange(starts[i], starts[i + 1], dtype=np.int64) for i in order])
        self.token_inverse = np.argsort(tokens)
        self.expected_logits = self.token_inverse[starts[1:] - 1]
        self.expected_order = order
        np.savez(self.folder / 'original-prepared.npz', input_ids=self.original_ids,
            positions=self.original_positions, original_q=q)
        _write(self.folder, 'started.json', dict(status='original_preparation_captured_no_model_forward',
            pid=os.getpid(), N=n, M=m, original_request_ids=list(self.req_ids),
            independent_compute_request_order=order, original_model_forward_calls=0))

    def prepared(self, *, input_ids, positions):
        import numpy as np
        ids = input_ids.detach().cpu().clone().numpy()
        pos = positions.detach().cpu().clone().numpy()
        n, m = self.plan.number, self.plan.total
        if ids.shape != (m,) or pos.shape != (m,) or self.torch.cuda.current_stream(0) != self.stream:
            raise RuntimeError('P实际M不符')
        self.mapping = dict(full_M_input_ids_inverse_bit_equal=bool(ids.dtype == self.original_ids.dtype and np.array_equal(
                ids[self.token_inverse], self.original_ids)),
            full_M_positions_inverse_bit_equal=bool(pos.dtype == self.original_positions.dtype and np.array_equal(pos[self.token_inverse], self.original_positions)),
            plan_request_permutation_matches_independent_partition=bool(
                np.array_equal(self.plan.permutation, self.expected_order)))
        np.savez(self.folder / 'permuted-prepared.npz', input_ids=ids, positions=pos,
            token_inverse=self.token_inverse, expected_original_row_logits_indices=self.expected_logits)
        if not all(self.mapping.values()):
            _write(self.folder, 'structure.json', dict(status='full_M_mapping_failed', **self.mapping))
            raise RuntimeError('P完整M整数映射不符；不重试原路')
        self.check_identity()

    def check_identity(self):
        runner = self.runner
        if (runner.input_batch is not self.batch or tuple(self.batch.req_ids) != self.req_ids
                or self.batch.num_reqs != self.plan.number
                or self.batch.sampling_metadata is not self.sampling_metadata or runner.sampler is not self.sampler):
            raise RuntimeError('原InputBatch/请求序/采样入口身份发生变化')

    def finish(self, logits, *, logits_indices):
        import numpy as np
        actual = logits_indices.detach().cpu().clone().numpy()
        equal = actual.shape == self.expected_logits.shape and np.array_equal(actual, self.expected_logits)
        n = self.plan.number
        if not equal or logits.ndim != 2 or logits.shape[0] != n:
            raise RuntimeError('实际GPU logits_indices/N行不符')
        self.check_identity()
        self.logits = logits  # 原execute state同一tensor引用，不复制hidden或再算logits。
        result = dict(status='full_M_and_N_indices_verified_waiting_actual_sample', pid=os.getpid(),
            N=n, M=self.plan.total, Dprefix=self.plan.prefix, outside=self.plan.outside,
            **self.mapping, actual_GPU_logits_indices=actual.tolist(),
            expected_original_request_row_indices=self.expected_logits.tolist(),
            original_request_ids=list(self.req_ids), original_InputBatch_and_sampling_identity=True,
            original_model_forward_calls=0, P_model_forward_returned=True,
            slots_seq_table_scope_reuses_085500_evidence=True,
            no_extra_sampling_or_rng_calls=True, no_precision_or_accuracy_claim=True)
        _write(self.folder, 'structure.json', result)
        key = id(self.runner)
        if key in _PENDING:
            raise RuntimeError('同runner已有未消费结构诊断')
        _PENDING[key] = self


def before_sample(runner, scheduler_output, logits, spec_decode_metadata):
    session = _PENDING.get(id(runner))
    if session is None:
        return None
    session.check_identity()
    if (scheduler_output is not session.scheduler_output or logits is not session.logits
            or spec_decode_metadata is not None or session.sample_calls != 0
            or logits.ndim != 2 or logits.shape[0] != session.plan.number):
        raise RuntimeError('实际_sample不是选中execute的原N行/同一步')
    session.sample_calls += 1
    _write(session.folder, 'sample-started.json', dict(status='original_sample_call_entering',
        pid=os.getpid(), N=session.plan.number, same_scheduler_output=True, same_logits_tensor=True,
        same_InputBatch=True, same_sampling_metadata=True, same_sampler=True,
        original_request_ids=list(session.req_ids), sample_call_number=session.sample_calls))
    return session


def after_sample(session, runner, scheduler_output, sampler_output):
    if session is None:
        return
    # 原_sample内部update_async_output_token_ids的合法history修改不拿来判失败。
    session.check_identity()
    shape = tuple(sampler_output.sampled_token_ids.shape)
    if (session.runner is not runner or scheduler_output is not session.scheduler_output
            or session.sample_calls != 1 or shape != (session.plan.number, 1)
            or _PENDING.get(id(runner)) is not session):
        raise RuntimeError('原_sample返回关联/原N单token形状不符')
    _write(session.folder, 'sample-link.json', dict(status='structure_and_actual_sample_link_completed',
        pid=os.getpid(), N=session.plan.number, M=session.plan.total, outside=session.plan.outside,
        same_execute_scheduler_output=True, original_sample_returned=True,
        original_sample_calls=1, sampled_shape=list(shape),
        original_request_ids=list(session.req_ids), original_sampler_row_order_preserved=True,
        unchanged_original_sample_body=True, no_sampling_replay=True,
        no_token_bitwise_or_model_accuracy_claim=True))
    print('BIV150_COMPUTE_ORDER_STRUCTURE_SAMPLED ' + json.dumps(dict(pid=os.getpid(),
        N=session.plan.number, M=session.plan.total, outside=session.plan.outside,
        same_execute=True, original_sample_calls=1)), flush=True)
    del _PENDING[id(runner)]
    session.logits = None
