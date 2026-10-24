"""仅读已有累计metadata快照，不读取trace、不推导吞吐或完整forward覆盖。"""
import argparse
import json
from pathlib import Path


def summarize(events_path):
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    snapshots = []
    for event in events:
        if event.get('event') in ('mixed_plan_coverage_partial', 'mixed_plan_coverage'):
            snapshots.append((event, event))
        elif isinstance(event.get('mixed_plan_coverage_partial'), dict):
            snapshots.append((event, event['mixed_plan_coverage_partial']))
    if not snapshots:
        raise ValueError('没有已保存的metadata coverage快照，不能按零遗漏处理')
    if len({event['pid'] for event, _ in snapshots}) != 1:
        raise ValueError('多PID累计快照不能混合')
    counts = [coverage['execute_calls'] for _, coverage in snapshots]
    if counts != sorted(counts):
        raise ValueError('累计execute_calls逆退，不能选末次快照')
    event, coverage = snapshots[-1]
    rows = []
    for key, count in coverage['histogram'].items():
        n, m, dall, prefix, outside, planned = map(int, key.split('/'))
        if not (type(count) is int and count > 0 and 0 < dall < n <= m
                and 0 <= planned <= prefix <= dall and outside == dall - prefix):
            raise ValueError('未知mixed histogram几何或频次')
        rows.append(dict(N=n, M=m, Dall=dall, Dprefix=prefix, outside=outside,
            plan_prefix_tokens=planned, frequency=count))
    rows.sort(key=lambda row: tuple(row[key] for key in ('N', 'M', 'Dall', 'Dprefix', 'outside', 'plan_prefix_tokens')))
    if sum(row['frequency'] for row in rows) != coverage['mixed_steps']:
        raise ValueError('histogram累计频次不等mixed_steps')
    total = sum(row['Dall'] * row['frequency'] for row in rows)
    outside = sum(row['outside'] * row['frequency'] for row in rows)
    unplanned = sum((row['Dall'] - row['plan_prefix_tokens']) * row['frequency'] for row in rows)
    counter_names = ('execute_calls', 'metadata_steps', 'mixed_steps', 'unsupported_steps',
        'multiple_builds', 'observation_errors', 'native_window_metadata_skipped',
        'scalar_pure_steps_skipped', 'single_attention_group_verified')
    return dict(source=str(events_path), pid=event['pid'], snapshot_count=len(snapshots),
        first_saved_execute_calls=counts[0], last_saved_execute_calls=counts[-1],
        selected_event=event['event'], selected_monotonic_ns=event.get('monotonic_ns'),
        shutdown_snapshot_seen=any(e.get('event') == 'mixed_plan_coverage' for e, _ in snapshots),
        workload_complete=False, scope='截至末次已保存快照的累计CPU metadata plan；不保证覆盖整个负载',
        counters={key: coverage[key] for key in counter_names},
        eligible_definition='metadata_steps仅为通过实际类型、形状、CPU offsets检查的首次build；包含非mixed项，不等全部execute',
        histogram=rows, mixed_q1_total=total, mixed_q1_outside_prefix=outside,
        outside_q1_ratio=None if total == 0 else outside / total,
        mixed_q1_not_in_plan=unplanned,
        unplanned_q1_ratio=None if total == 0 else unplanned / total,
        limits=['累计快照只取末次，不把多份快照相加；无q1样本时比例为null，不能称0遗漏。',
            '比例仅按q1请求步数及形状频次计数，无K长度、层数或耗时加权。',
            'q1不保证已确认decode身份；outside是首连续q1段之外，unplanned另含段内未进入plan的q1。',
            'metadata plan不证明forward实际执行或收益；unsupported、错误、多build和刻意跳过范围须同时阅读。',
            '1024输出单波32请求的零遗漏不能排除128输出或官方多波负载的机会。'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = summarize(args.run_dir / 'native-events.jsonl')
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as stream:
            stream.write(text)
    else:
        print(text, end='')
