"""四题诊断：仅记录实际P outside行与原采样成功；不触碰采样值或随机状态。"""
import json
import os
from pathlib import Path

_DONE = set()
_PENDING = {}
ENV = 'BIV150_COMPUTE_ORDER_MATH4_DIR'


def after_forward(runner, plan, output, scheduled, logits):
    if plan is None or not os.environ.get(ENV) or len(_DONE) >= 4:
        return
    batch = runner.input_batch
    req_ids = tuple(batch.req_ids)
    n = batch.num_reqs
    if (len(req_ids) != n or len(scheduled) != n or plan.number != n
            or logits.ndim != 2 or logits.shape[0] != n or id(runner) in _PENDING):
        raise RuntimeError('math4 forward/原N行关联不符')
    rows = []
    for row in range(plan.prefix, n):
        rid = req_ids[row]
        if int(scheduled[row]) != 1 or not rid.startswith('chatcmpl-') or rid in _DONE:
            continue
        position = int(batch.num_computed_tokens_cpu[row])
        prompt = int(batch.num_prompt_tokens_cpu_tensor[row].item())
        if position < prompt or len(_DONE) + len(rows) >= 4:
            continue
        rows.append(dict(internal_request_id=rid, original_row=row,
            query_tokens=1, input_position=position, prompt_len=prompt,
            predicted_output_token_index_0based=position - prompt + 1))
    if rows:
        _PENDING[id(runner)] = dict(output=output, logits=logits, batch=batch,
            req_ids=req_ids, metadata=batch.sampling_metadata, sampler=runner.sampler,
            N=n, M=plan.total, Dprefix=plan.prefix, Dall=plan.dall,
            outside=plan.outside, rows=rows, calls=0)


def before_sample(runner, output, logits, spec):
    ticket = _PENDING.get(id(runner))
    if ticket is None:
        return None
    if (output is not ticket['output'] or logits is not ticket['logits'] or spec is not None
            or runner.input_batch is not ticket['batch']
            or tuple(runner.input_batch.req_ids) != ticket['req_ids']
            or runner.input_batch.sampling_metadata is not ticket['metadata']
            or runner.sampler is not ticket['sampler'] or ticket['calls'] != 0):
        raise RuntimeError('math4 sample入口与原execute不符')
    ticket['calls'] = 1
    return ticket


def after_sample(ticket, runner, output, sampled):
    if ticket is None:
        return
    if (output is not ticket['output'] or _PENDING.get(id(runner)) is not ticket
            or ticket['calls'] != 1 or tuple(sampled.sampled_token_ids.shape) != (ticket['N'], 1)
            or runner.input_batch is not ticket['batch']
            or tuple(runner.input_batch.req_ids) != ticket['req_ids']
            or runner.input_batch.sampling_metadata is not ticket['metadata']
            or runner.sampler is not ticket['sampler']):
        raise RuntimeError('math4 sample返回关联不符')
    folder = Path(os.environ[ENV]) / str(os.getpid())
    if not folder.is_absolute():
        raise ValueError('math4输出须绝对路径')
    folder.mkdir(parents=True, exist_ok=True)
    for row in ticket['rows']:
        rid = row['internal_request_id']
        record = dict(status='actual_outside_and_original_sample_returned', pid=os.getpid(),
            N=ticket['N'], M=ticket['M'], Dprefix=ticket['Dprefix'], Dall=ticket['Dall'],
            outside=ticket['outside'], original_sample_calls=1, same_scheduler_output=True,
            sampler_rows=ticket['N'], position_source='original_CPU_metadata_used_by_verified_P',
            gpu_completion_claimed=False, **row)
        # 固定最多四题，只首个有效outside时点；完整rid写字段，不用它构造路径。
        with (folder / ('outside-' + str(len(_DONE)) + '.json')).open('x', encoding='utf-8') as f:
            json.dump(record, f, ensure_ascii=False, indent=2)
        _DONE.add(rid)
        print('BIV150_COMPUTE_ORDER_MATH4_SAMPLED ' + json.dumps(record), flush=True)
    _PENDING.pop(id(runner))

