"""隔离6f候选：仅批量写CPU异步单token占位符；不安装、不操作GPU。"""
import hashlib
from pathlib import Path
import sys
import numpy as np

EXPECTED_INPUT_BATCH = 'de1ea4fc9d43fc6079dd375e407c2b6d93f5e1a11f49732d13654c41eaf30a65'
STATE = '_biv150_async_bookkeeping'


def _initial_state(runner):
    module = sys.modules.get('vllm.v1.worker.gpu_input_batch')
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED_INPUT_BATCH:
        return None
    batch = runner.input_batch
    if type(batch) is not module.InputBatch:
        return None
    config = runner.vllm_config
    model, parallel = config.model_config, config.parallel_config
    text = model.hf_text_config
    if not (
        Path(str(model.model).rstrip('/\\')).name == 'MiniCPM5-2B'
        and str(model.dtype) == 'torch.bfloat16' and model.quantization is None
        and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads,
             text.num_key_value_heads) == (2048, 42, 16, 2)
        and all(getattr(parallel, k, None) == 1 for k in (
            'tensor_parallel_size', 'pipeline_parallel_size', 'data_parallel_size',
            'decode_context_parallel_size'))
        and not parallel.use_ubatching and config.speculative_config is None
        and config.lora_config is None and not runner.supports_mm_inputs
        and not runner.is_pooling_model and not runner.enable_prompt_embeds
    ):
        return None
    rows = runner.arange_np
    if (type(rows) is not np.ndarray or rows.ndim != 1 or rows.dtype != np.int64
            or not np.array_equal(rows, np.arange(rows.size, dtype=np.int64))):
        return None
    arrays = (batch.token_ids_cpu, batch.is_token_ids, batch.num_tokens_no_spec)
    if (any(type(a) is not np.ndarray or not a.flags.c_contiguous for a in arrays)
            or any(np.shares_memory(a, b) for i, a in enumerate((*arrays, rows))
                   for b in (*arrays, rows)[i+1:])):
        return None
    return {'batch':batch, 'rows':rows, 'request_type':module.CachedRequestState,
            'arrays':arrays, 'selected':0, 'disabled':False}


def try_bulk_bookkeeping(runner, n, sampled_token_ids, invalid, scheduler_output):
    # N1/2等小批原路：不读配置/数组/时间/日志，不初始化状态。
    if n < 16:
        return False
    try:
        if (not runner.use_async_scheduling or runner.speculative_config is not None
                or runner.num_spec_tokens or runner.prev_num_spec_tokens or invalid
                or tuple(sampled_token_ids.shape) != (n, 1)
                or sampled_token_ids.device.type != 'cuda'
                or scheduler_output.total_num_scheduled_tokens != n):
            return False
        state = getattr(runner, STATE, None)
        if state is None:
            state = _initial_state(runner)
            if state is None:
                return False
            setattr(runner, STATE, state)
        batch = runner.input_batch
        if state['disabled'] or batch is not state['batch'] or runner.arange_np is not state['rows']:
            return False
        ids, flags, counts = batch.token_ids_cpu, batch.is_token_ids, batch.num_tokens_no_spec
        if (ids is not state['arrays'][0] or flags is not state['arrays'][1]
                or counts is not state['arrays'][2]
                or n != batch.num_reqs or type(ids) is not np.ndarray or type(flags) is not np.ndarray
                or type(counts) is not np.ndarray or ids.dtype != np.int32
                or flags.dtype != np.bool_ or counts.dtype != np.int32
                or ids.ndim != 2 or flags.shape != ids.shape or counts.ndim != 1
                or ids.shape[0] < n or counts.size < n or state['rows'].size < n
                or ids.shape[1] != runner.max_model_len
                or not ids.flags.writeable or not flags.flags.writeable or not counts.flags.writeable):
            return False
        # snapshot必须独立于后续计数写回；所有guard与映射检查先于任何数组写。
        starts = counts[:n].copy()
        if starts.min() < 0 or starts.max() >= runner.max_model_len:
            return False
        req_ids = batch.req_ids
        if len(req_ids) != n:
            return False
        histories = []
        for i, rid in enumerate(req_ids):
            req = runner.requests[rid]
            if (type(req) is not state['request_type'] or req.req_id != rid
                    or batch.req_id_to_index.get(rid) != i or type(req.output_token_ids) is not list):
                return False
            histories.append(req.output_token_ids)
        rows = state['rows'][:n]
        ends = starts + 1
    except Exception:
        return False  # 尚未变更；原caller在except外执行原loop。

    # 第一次写之后不捕异常/不fallback/不重试；不改D2H/event/独立输出快照。
    ids[rows, starts] = -1
    flags[rows, starts] = True
    counts[:n] = ends
    for history in histories:
        history.extend([-1])
    state['selected'] += 1
    return True
