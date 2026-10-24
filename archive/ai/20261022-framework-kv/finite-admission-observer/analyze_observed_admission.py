"""只读解析一次已封存的稀疏准入日志；不以诊断吞吐推断收益。"""
import collections
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long'
OUT = ROOT / 'analysis/finite-admission-observation.json'
MARKER = 'BIV150_ADMISSION_OBSERVER '


def summarize(result):
    timeline = []
    budgets = []
    for event in result['timeline']:
        item = {key: event[key] for key in ('event', 'log_line', 'step', 'n', 'free', 'budget')}
        item['candidate'] = {key: event['candidate'][key] for key in ('request', 'status', 'output', 'known', 'issued', 'placeholders', 'owned', 'current_q', 'queued_q')}
        item['running_summary'] = {key: event['summary'][key] for key in ('output_range', 'remaining_to_first_max', 'current_q_histogram', 'placeholders_histogram', 'queued_q_histogram')}
        item['queue_frame_count'] = len(event['queue'])
        item['logical_owned_plus_free'] = event['summary']['owned_logical_sum'] + event['free']
        for key in ('allocation_args', 'after_allocate_free_blocks', 'new_allocated_block_counts', 'allocator_returned_none'):
            if key in event:
                item[key] = event[key]
        if 'after' in event:
            item['after_admission'] = {key: event['after'][key] for key in ('n', 'free')}
            item['after_admission']['candidate_issued_before_update'] = event['after']['candidate']['issued']
            item['after_admission']['candidate_current_q'] = event['after']['candidate']['current_q']
        timeline.append(item)
        if event['step'] not in (268, 276, 1067, 1076):
            continue
        horizon = event['summary']['remaining_to_first_max']
        existing = sum(max(0, math.ceil(min(row['prompt'] + row['max_output'],
                            max(row['known'] + horizon + 2, row['issued'] + row['current_q'])) / 16) - row['owned'])
                       for row in event['rows'])
        candidate = event['candidate']
        candidate_need = math.ceil(min(candidate['prompt'] + candidate['max_output'], candidate['known'] + horizon + 2) / 16) - candidate['owned']
        full = sum(max(0, math.ceil((row['prompt'] + row['max_output']) / 16) - row['owned']) for row in event['rows']) + math.ceil((candidate['prompt'] + candidate['max_output']) / 16) - candidate['owned']
        budgets.append(dict(step=event['step'], free=event['free'], horizon_output_steps=horizon,
                            arithmetic_phase_margin=2, existing_growth_pages=existing,
                            candidate_total_pages=candidate_need, finite_total=existing+candidate_need,
                            finite_slack=event['free']-existing-candidate_need, full_output_total=full,
                            full_output_slack=event['free']-full))
    return dict(run=result['run'], source='server.log，行号见timeline',
        seals='root已逐477项验收，本分析不重验', diagnostic_only=True,
        result=dict(completed=32, failed=0, output_tokens=32768, pool_pages_including_null=32621,
                    throughput_is_not_performance_evidence=True,
                    db_tables=529, db_rows=19769, db_three_hashes_unchanged='复用root封存验收'),
        event_counts=result['event_counts'], final_event_present=False,
        final_event_limit='无FINAL行，不能用进程正常结束替代末态采样；已有7个事件相位自洽，无disabled/scope-rejected事件',
        timeline=timeline, conditional_capacity_budgets=budgets,
        budget_definition=dict(
            horizon='当前resident最小(max_tokens-confirmed_output)，假定其继续每轮decode；不是EOS预测或墙钟',
            target='min(prompt+max_tokens, max(known_tokens+H+2, issued_computed+current_scheduled))',
            existing='逐请求max(0,ceil(target/16)-owned_logical_pages)之和；候选保完整目标页，不扣未知可回收APC',
            caveat='额外2是保守算术相位余量，不是队列2必定多2个独立token的证明；queued已在issued中，不再次加queued_q',
            new_request_scope='268/276候选APC、external、lookahead、reserved均0。该算术不是完整调度仿真或通用reserve实现'),
        findings=[
            'full_sequence_must_fit=true只要求完整当前输入能放下，实际268/276首chunk分别只分52/37页；并非原框架没有整输入准入保护。',
            '268/276当前running最后一条仍是prefill，但当前1196/1427恰补完prompt；其旧queue分别2020/2019 token已含在issued内。其他28/29条当前q1且placeholder1。不能凭旧prefill标志当全decode，也不能重复计pending。',
            '有限窗口可保留第30条：268总2525<=2702，而全输出2722>2702；第31条仍须延后：276总2559>1664。两者不是同一策略。首释放之后必须重新检验，不能一次horizon证明后续全部安全。',
            '612 free0在running_index1分配1 token失败；尾r31已生成327，613确认为328并保留在请求历史中。此时30条继续生成，不能将等待恢复区间视作GPU空闲。',
            'r31 APC由613的16480 token降至1067的3040，known16712保持，恢复差额13672；此差额是本轮重算工作量边界，不是已测可消除GPU时间。',
            '若延后r31，需完整16K prefill且从0生成，而原恢复只补13672并已保留328输出。晚移的初始prefill增量为2712 token，总体仍有删重复prefill机会，但不能只统计这一收益侧。',
            'r32原到1076才从0准入，r31此时330输出。丢328早期输出可能主要将尾段N1改为N2，不能直接声称总时长必加328步，也不能声称其没有成本。',
            '在固定每轮推进/同cap的简化算术中，r31完整prefill约9块对原恢复7块，而首、次释放相隔9步；因此第32条不必因额外2块自动延后。真实批次时长、APC与异步回收改变仍需核实，非反事实事实。',
            '各快照logical_owned+free都为32620=pool-1，但没有直接记录页refcount，不能据逻辑页数承诺某请求唯一可释放页数。'],
        decision=dict(status='等待当前QGQA native后估净收益，保留有限窗口机制但不实现策略',
                      reason='已证明它可比全reserve少延后一个resident且有真实重算可删；尚缺当前重算与新增尾N2边际代价，旧3.486秒不能当本轮可删收益。',
                      next='复用root已启动192308当前QGQA native证据，再决定是否只做一个有限窗口候选；不额外重跑191047或扩扫。',
                      stop_if='若当前可删重复prefill预算不能覆盖晚移prefill、尾批次及准入检查成本，或首释放后的容量安全需复杂预测，则停止该点。'),
        limitations=result['limitations'] + ['只看到临界稀疏事件，不是完整请求时间线；32条均生成满1024是事后结果，运行策略不能预知EOS',
            '本轮诊断额外CPU采样成本不计性能，未改策略/官方参数/模型/算子，也未运行新的GPU实验'])


def main():
    events = []
    for line_number, line in enumerate((RUN / 'server.log').read_text(encoding='utf-8').splitlines(), 1):
        if MARKER in line:
            prefix, body = line.split(MARKER, 1)
            value = json.JSONDecoder().raw_decode(body)[0]
            events.append(dict(value, log_line=line_number, log_prefix=prefix))
    aliases = {}

    def alias(rid):
        if rid not in aliases:
            aliases[rid] = f'r{len(aliases)+1:02d}'
        return aliases[rid]

    def row(value, state):
        rid = value['request_id']
        queued = sum(f['scheduled_tokens'].get(rid, 0) for f in state['queued_frames'])
        return dict(request=alias(rid), status=value['status'], prompt=value['prompt_tokens'],
                    output=value['confirmed_output_tokens'], max_output=value['max_tokens'],
                    known=value['known_tokens'], issued=value['issued_computed_tokens'],
                    placeholders=value['output_placeholders'], owned=value['owned_logical_pages'],
                    cached=value['cached_full_pages'], current_q=state['current_scheduled_tokens_not_yet_issued'].get(rid, 0),
                    queued_q=queued, prefill=value['is_prefill_chunk'], preemptions=value['num_preemptions'])

    timeline = []
    for event in events:
        state = event.get('before_allocate', event.get('state'))
        if state is None:
            continue
        rows = [row(r, state) for r in state['running']]
        candidate = event.get('candidate_before', event.get('candidate'))
        item = dict(event=event['event'], log_line=event['log_line'], step=state['scheduler_step'],
                    n=state['running_count'], free=state['free_blocks'],
                    pool=state['pool_blocks_including_null'], watermark=state['watermark_blocks'],
                    budget=state['remaining_token_budget'], rows=rows,
                    candidate=row(candidate, state),
                    queue=[{alias(k): v for k, v in f['scheduled_tokens'].items()} for f in state['queued_frames']],
                    phase='原分配前；issued不含current_q，queued_q已在issued内；GPU完成未知',
                    physical_releasable_pages_unknown=True)
        for field in ('allocation_args', 'after_allocate_free_blocks', 'new_allocated_block_counts',
                      'first_attempt', 'attempt_index', 'allocator_returned_none', 'failed_running_index', 'num_new_tokens'):
            if field in event:
                item[field] = event[field]
        if 'after_admission_before_update' in event:
            after = event['after_admission_before_update']
            item['after'] = dict(n=after['running_count'], free=after['free_blocks'],
                                 candidate=row(event['candidate_after'], after),
                                 current_q={alias(k): v for k, v in after['current_scheduled_tokens_not_yet_issued'].items()},
                                 phase='已append RUNNING并赋computed；尚未_update_after_schedule')
        item['summary'] = dict(
            output_range=[min(r['output'] for r in rows), max(r['output'] for r in rows)],
            output_sum=sum(r['output'] for r in rows),
            remaining_to_first_max=min(r['max_output']-r['output'] for r in rows),
            owned_logical_sum=sum(r['owned'] for r in rows),
            current_q_histogram=dict(collections.Counter(r['current_q'] for r in rows)),
            placeholders_histogram=dict(collections.Counter(r['placeholders'] for r in rows)),
            queued_q_histogram=dict(collections.Counter(r['queued_q'] for r in rows)),
            all_max_output_values=sorted({r['max_output'] for r in rows}),
            all_prompt_values=sorted({r['prompt'] for r in rows}))
        timeline.append(item)
    result = dict(run=RUN.name, source='server.log', raw_seal_verification='root已核477项，本分析不重复',
                  diagnostic_only=True, event_counts=dict(collections.Counter(e['event'] for e in events)),
                  control_events=[e for e in events if 'before_allocate' not in e and 'state' not in e],
                  request_aliases={v:k for k,v in aliases.items()}, timeline=timeline,
                  limitations=['稀疏CPU快照没有逐步真实页refcount、EOS未来或GPU完成证明',
                               '原队列帧与current_q相位分开，不能重复累计pending',
                               '诊断运行不是性能对照；延后准入会丢失本可完成的生成进度，不能只统计省重算'])
    compact = summarize(result)
    OUT.write_text(json.dumps(compact, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(output=str(OUT.relative_to(ROOT)), counts=result['event_counts'],
                          budgets=compact['conditional_capacity_budgets'], decision=compact['decision']), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
