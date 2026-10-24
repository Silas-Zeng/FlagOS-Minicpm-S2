"""仅原CPU批生命周期与一次到达信号；不改批、调度、采样或GPU工作。"""
import hashlib
import json
import os
from pathlib import Path
import re
import time

ENV = 'BIV150_COMPUTE_ORDER_MATH4_EVENT_DIR'
_STATE = None


def _write(state, name, value):
    path = state['folder'] / name
    if path.exists():
        raise FileExistsError('不覆盖既有事件信号')
    pending = path.with_name(path.name + '.pending-' + str(os.getpid()))
    with pending.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    pending.rename(path)  # 本进程唯一writer；完整JSON关闭后才对client发布。


def _emit(state, event, frame, **extra):
    value = dict(event=event, pid=os.getpid(), monotonic_ns=time.monotonic_ns(),
                 cpu_scheduling_observation_only=True, gpu_completion_claimed=False,
                 **frame, **extra)
    with (state['folder'] / 'observer-events.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False) + '\n')
    return value


def _internal(rid, external):
    return re.fullmatch(re.escape(external) + r'-[0-9a-f]{8}', rid) is not None


def _plan_reason(runner, output, q, plan):
    if plan is not None:
        return 'actual_plan_created'
    if max(q) <= 1:
        return 'pure_q1_no_plan'
    if not 3 <= len(q) <= 64:
        return 'N_outside_3_to_64'
    if q[0] != 1:
        return 'first_row_not_q1'
    prefix = next(i for i, value in enumerate(q) if value != 1)
    if sum(value == 1 for value in q) == prefix:
        return 'all_q1_already_in_prefix'
    if output.scheduled_cached_reqs.resumed_req_ids or output.__dict__.get('_biv150_kv_protocol_v1_resume') is not None:
        return 'resumed_step_excluded'
    if runner.__dict__.get('_biv150_compute_order_buffers') is False:
        return 'actual_plan_cold_scope_rejected'
    return 'actual_plan_none_other_guard_not_inferred'


def observe_batch(runner, output, scheduled, plan):
    """在原_update_states和make_plan之后、原_prepare_inputs之前调用一次。"""
    global _STATE
    location = os.environ.get(ENV)
    if not location or _STATE is False:
        return
    try:
        if _STATE is None:
            folder = Path(location)
            if not folder.is_absolute() or not folder.is_dir():
                raise ValueError('events须为本次独立绝对目录')
            path = folder / 'background-request-ids.json'
            if not path.exists():
                return  # client须原子发布身份；启动/smoke不推测背景RID。
            raw = path.read_bytes()
            config = json.loads(raw)
            ids = config.get('engine_input_request_ids')
            if (set(config) != {'engine_input_request_ids'} or type(ids) is not list or len(ids) != 2
                    or len(set(ids)) != 2 or any(type(x) is not str or not x or x.startswith('chatcmpl-') for x in ids)):
                raise ValueError('须两条actual engine-input子请求ID，不是HTTP头或顶层响应ID')
            if runner.reorder_batch_threshold is not None:
                raise ValueError('当前builder重排不是已核None')
            _STATE = dict(folder=folder, runner=runner, external=tuple(ids), bound=[None, None],
                finished=set(), math={}, step=0, pair=False, released=False,
                terminal=False, post_tail=False, reasons=set(), config_sha256=hashlib.sha256(raw).hexdigest())
        state = _STATE
        if state['runner'] is not runner:
            raise ValueError('同进程出现第二runner')
        if state['terminal']:
            return
        batch = runner.input_batch
        reqs, q = tuple(batch.req_ids), [int(value) for value in scheduled]
        if len(reqs) != batch.num_reqs or len(reqs) != len(q) or len(set(reqs)) != len(reqs) or not q or min(q) <= 0:
            raise ValueError('原批CPU几何不合法')
        state['step'] += 1
        current_finished = set(output.finished_req_ids)
        for index, external in enumerate(state['external']):
            matches = {rid for rid in set(reqs) | current_finished if _internal(rid, external)}
            if len(matches) > 1:
                raise ValueError('同external有多个internal RID')
            if matches:
                rid = matches.pop()
                if state['bound'][index] not in (None, rid):
                    raise ValueError('背景RID被重新绑定')
                state['bound'][index] = rid
        new_finished = current_finished - state['finished']
        state['finished'].update(current_finished)
        rows = {rid: index for index, rid in enumerate(reqs)}
        computed = [int(value) for value in batch.num_computed_tokens_cpu[:len(q)]]
        prompt = [int(value) for value in batch.num_prompt_tokens_cpu_tensor[:len(q)].tolist()]
        frame = dict(step=state['step'], req_ids=list(reqs), q=q, computed=computed,
            prompt_len=prompt, N=len(q), M=sum(q), finished_req_ids=sorted(current_finished),
            background_internal_ids=list(state['bound']), plan_created=plan is not None,
            plan_reason=_plan_reason(runner, output, q, plan),
            config_sha256=state['config_sha256'])
        if state['step'] == 1:
            _emit(state, 'identities_armed', frame)
        math_now = [rid for rid in reqs if rid.startswith('chatcmpl-')]
        for rid in math_now:
            if rid not in state['math']:
                if len(state['math']) >= 4:
                    raise ValueError('出现多于四条chat请求')
                state['math'][rid] = False
                _emit(state, 'math_first_present', frame, request_id=rid, row=rows[rid])
            row = rows[rid]
            if not state['math'][rid] and q[row] == 1 and computed[row] >= prompt[row]:
                state['math'][rid] = True
                _emit(state, 'math_first_decode_q1', frame, request_id=rid, row=row)
        for rid in set(state['bound']) - {None}:
            if rid in new_finished:
                _emit(state, 'background_finished_reported', frame, request_id=rid)
        a, b = state['bound']
        both_q1 = all(rid in rows and q[rows[rid]] == 1 and computed[rows[rid]] >= prompt[rows[rid]]
                      for rid in (a, b))
        if both_q1 and not state['pair']:
            value = _emit(state, 'background_both_decode_q1', frame)
            _write(state, 'background-both-q1.json', value)
            state['pair'] = True
        # release只看本步真实行序，不把HTTP结束或预期输出长度当填洞证明。
        all_math = len(state['math']) == 4 and all(rid in rows and q[rows[rid]] == 1
            and computed[rows[rid]] >= prompt[rows[rid]] for rid in state['math'])
        k = rows.get(b, -1)
        eligible = (state['pair'] and not state['released'] and a in state['finished']
            and a not in rows and b in rows and b not in state['finished'] and k > 0
            and q[k] == 1 and computed[k] >= prompt[k]
            and all_math and reqs[0] in state['math'] and q[0] == 1
            and any(rows[rid] > k for rid in state['math']))
        if eligible:
            value = _emit(state, 'release_background_tail', frame, remaining_background_row=k,
                math_rows=sorted(rows[rid] for rid in state['math']))
            _write(state, 'release-background-tail.json', value)
            state['released'] = True
        if state['released']:
            new_prefill = [rid for rid in reqs if rid not in state['bound'] and rid not in state['math'] and q[rows[rid]] > 1]
            if new_prefill and not state['post_tail']:
                _emit(state, 'first_tail_prefill_present', frame, request_ids=new_prefill)
                state['post_tail'] = True
            reason = frame['plan_reason']
            if reason not in state['reasons'] and len(state['reasons']) < 8:
                state['reasons'].add(reason)
                _emit(state, 'post_release_plan_state', frame)
        elif ((a is not None and b is not None and a in state['finished'] and b in state['finished'])
              or any(rid in state['finished'] for rid in state['math'])):
            value = _emit(state, 'uncovered_release_geometry_lost', frame)
            _write(state, 'uncovered.json', value)
            state['terminal'] = True
    except Exception as error:
        # 诊断失败只禁新信号，原model/sample均不在try内且不重试。
        state = _STATE if isinstance(_STATE, dict) else None
        _STATE = False
        try:
            folder = Path(location)
            if folder.is_absolute() and folder.is_dir():
                with (folder / 'observer-error.json').open('x', encoding='utf-8') as stream:
                    json.dump(dict(status='diagnostic_disabled', pid=os.getpid(),
                        error_type=type(error).__name__, message=str(error)), stream, ensure_ascii=False)
        except Exception:
            pass
