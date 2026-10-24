"""仅汇总固定官方日志的多key事务证据；不替代CSV/源/清理或VERIFY1验收。"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

RUN = '20261022T231746Z-q-gqa-kv-swap-official'
STAGES = ('SAVE', 'SAVE_ACK_FREE', 'RESTORE_FULL', 'RESTORE_ACK', 'RESUME_PUBLISHED',
          'DROP', 'RUNNER_RESUME_STATE_CHECKED', 'RESUME_OUTPUT_PROCESSED')
UNKEYED = {'SAVE_ACK_FREE': 'SAVE', 'RESTORE_ACK': 'RESTORE_FULL',
           'RESUME_PUBLISHED': 'RESTORE_ACK'}


def summarize(path):
    raw = path.read_bytes()
    transactions, active, counters, errors, serials = {}, {}, {}, [], {}
    event_counts = Counter()
    def issue(line, reason):
        errors.append(dict(line=line, reason=reason))
    for line, text in enumerate(raw.decode('utf-8').splitlines(), 1):
        if 'BIV150_KV_PROTOCOL ' not in text:
            continue
        try:
            event = json.loads(text.split('BIV150_KV_PROTOCOL ', 1)[1])
            pid, name = event['pid'], event['event']
            if type(pid) is not int or type(name) is not str:
                raise ValueError('未知pid/event')
            event_counts[name] += 1
            current = {k: event[k] for k in ('saved', 'restored', 'published', 'rollbacks')}
            if any(type(v) is not int or v < counters.get(pid, {}).get(k, 0) for k, v in current.items()):
                raise ValueError('累计计数类型/单调性不符')
            counters[pid] = current
            if current['rollbacks'] or any(x in name for x in ('ERROR', 'EXCEPTION', 'ROLLBACK')):
                issue(line, '协议rollback/error事件或累计值非零')
            key = event.get('command', {}).get('key') if name == 'RPC_ACK' else event.get('key')
            inferred = name in UNKEYED
            if inferred:
                key = active.get(pid)
                if key is None:
                    raise ValueError('无key摘要没有同PID已观测唯一slot')
            if key is None:
                continue
            if (not isinstance(key, (list, tuple)) or len(key) != 4
                    or any(type(v) is not str or not v for v in key[:2])
                    or any(type(v) is not int or v < 1 for v in key[2:])):
                raise ValueError('事务key格式不符')
            key = tuple(key)
            tx = transactions.setdefault((pid, key), dict(pid=pid, key=list(key), stages={}, acks={}, errors=[]))
            stage = event['command']['kind'] if name == 'RPC_ACK' else name
            if stage not in STAGES:
                raise ValueError('该key出现非FULL链阶段：' + stage)
            if stage in tx['stages']:
                raise ValueError('同key阶段重复：' + stage)
            tx['stages'][stage] = dict(line=line, key_in_event=not inferred)
            if inferred:
                if UNKEYED[stage] not in tx['stages'] or event['prefix_tokens'] != tx['acks']['SAVE']['prefix_tokens']:
                    raise ValueError('无key阶段前置/相同prefix不符')
            elif name == 'RPC_ACK':
                command, reply = event['command'], event['worker_response']
                if (any(reply.get(k) != command[k] for k in ('key', 'operation_serial', 'kind', 'pages', 'nbytes'))
                        or reply.get('worker_pid') != pid or reply.get('successful') is not True
                        or reply.get('completed') is not True or reply.get('error') is not None
                        or reply.get('transferred_bytes') != command['nbytes']):
                    raise ValueError('RPC ACK echo/成功/完成/字节字段不符')
                serial = command['operation_serial']
                if type(serial) is not int or serial <= serials.get(pid, 0):
                    raise ValueError('同PID操作serial必须跨slot复用严格递增，不假设每key从1开始')
                serials[pid] = serial
                tx['acks'][stage] = {k: command[k] for k in ('operation_serial', 'prefix_tokens', 'nbytes')}
                tx['acks'][stage].update({k: reply.get(k) for k in ('copy_calls', 'saved_layers', 'saved_prefix_pages',
                    'diagnostic_verify_requested', 'save_verification_performed', 'verification_performed')})
                if stage == 'SAVE':
                    if pid in active or reply.get('host_held') is not True or reply.get('saved_layers') != 42:
                        raise ValueError('SAVE与单slot/42层描述冲突')
                    active[pid] = key
                elif active.get(pid) != key:
                    raise ValueError('FULL/DROP不是该PID当前slot')
                if stage == 'RESTORE_FULL' and (reply.get('zero_stage_executed') is not False
                        or reply.get('zero_calls') != 0 or reply.get('destination_bound') is not True
                        or reply.get('full_coverage') is not True or reply.get('full_coverage_bytes') != command['nbytes']):
                    raise ValueError('FULL绑定/整页覆盖/无ZERO字段不符')
                if stage == 'DROP':
                    if reply.get('dropped') is not True or reply.get('host_held') is not False or reply.get('host_payload_bytes') != 0:
                        raise ValueError('DROP未确认释放host')
                    active.pop(pid)
                elif reply.get('diagnostic_verify_requested') is not False or any(reply.get(k) is True for k in (
                        'save_verification_performed', 'verification_performed')):
                    raise ValueError('不符合本次VERIFY0，无新的42层回读资格')
            elif stage == 'RUNNER_RESUME_STATE_CHECKED':
                names = ('cached_state_same', 'generator_same', 'computed_prefix', 'output_token_ids',
                         'full_block_replacement', 'cpu_computed_prefix')
                if (any(event['checks'].get(k) is not True for k in names) or event.get('before_attention') is not True
                        or event.get('gpu_completion_claimed') is not False):
                    raise ValueError('runner CPU状态校验字段不符')
            elif stage == 'RESUME_OUTPUT_PROCESSED':
                tx['scheduled_tokens'] = event.get('scheduled_tokens')
                if event.get('after_original_update') is not True or type(tx['scheduled_tokens']) is not int or tx['scheduled_tokens'] <= 0:
                    raise ValueError('原output消费字段不符')
        except (KeyError, TypeError, ValueError) as error:
            issue(line, str(error))
    rows = list(transactions.values())
    for tx in rows:
        tx['missing_stages'] = [s for s in STAGES if s not in tx['stages']]
        ordered = [tx['stages'][s]['line'] for s in STAGES if s in tx['stages']]
        tx['ordered'] = ordered == sorted(ordered)
        acks = tx['acks']
        if set(acks) == {'SAVE', 'RESTORE_FULL', 'DROP'}:
            tx['descriptor_consistent'] = (len({a['prefix_tokens'] for a in acks.values()}) == 1
                and acks['SAVE']['nbytes'] == acks['RESTORE_FULL']['nbytes'] == acks['SAVE']['prefix_tokens'] * 43008
                and acks['DROP']['nbytes'] == 0 and [acks[s]['operation_serial'] for s in ('SAVE', 'RESTORE_FULL', 'DROP')]
                    == sorted(set(a['operation_serial'] for a in acks.values())))
        tx['errors'] = [e for e in errors if e['line'] in {s['line'] for s in tx['stages'].values()}]
        tx['complete_logged_chain'] = not tx['missing_stages'] and tx['ordered'] and tx.get('descriptor_consistent', False) and not tx['errors']
    count_match = len(counters) == 1 and all(c[k] == len(rows) for c in counters.values() for k in ('saved', 'restored', 'published'))
    return dict(run_id=RUN, log_sha256=hashlib.sha256(raw).hexdigest(), event_counts=dict(event_counts),
        engine_pids=sorted(counters), independent_key_count=len(rows), counters=counters,
        counter_totals_match_key_count=count_match, last_operation_serial_by_pid=serials,
        complete_logged_chains=sum(tx['complete_logged_chain'] for tx in rows), transactions=rows,
        incomplete_chains=[tx['key'] for tx in rows if not tx['complete_logged_chain']],
        unresolved_slots=[dict(pid=p, key=list(k)) for p, k in active.items()], errors=errors,
        passed_logged_chain_checks=bool(rows and count_match and not active and not errors and all(t['complete_logged_chain'] for t in rows)),
        limits=['无key摘要仅按同PID单slot和顺序关联；不虚构事件携带key。',
            'RPC ACK不单独证明源空闲；SAVE_ACK_FREE为原free成功后的协议记录，runner检查在attention前。',
            'output记录仅证明原update返回；不证明最终答案或逐层路由。VERIFY0没有新的42层字节回读。',
            '42层双向字节资格另见213134 VERIFY1；本摘要不替代源/CSV/清理或全部抢占覆盖验收。'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.run_dir.name != RUN:
        parser.error('仅接受固定231746官方run目录')
    result = summarize(args.run_dir / 'server.log')
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    raise SystemExit(0 if result['passed_logged_chain_checks'] else 1)
