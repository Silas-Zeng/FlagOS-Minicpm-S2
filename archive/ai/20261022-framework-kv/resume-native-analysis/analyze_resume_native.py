"""只读分析已结束的恢复窗口；复用现有 native reader/分类，不给性能结论。"""
import argparse
import ast
import bisect
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sqlite3
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
READER_SHA = '25c5ae091cbf289e80ff9dea979b6756fd31ee832cc75ae79b55046fd060a162'
ANALYZER_SHA = 'cb65e1dfc2f745c461bf721b563e7b2d8ac4959a2741064bf5c84bf9bf628b91'


def load_checked(path, expected, name):
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('既有分析模块身份变化: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def window_evidence(events):
    selected = {kind: [e for e in events if e.get('event') == kind]
                for kind in ('preempt_observed', 'start', 'stop', 'shutdown_incomplete')}
    checks = {'one_preempt_start_stop': all(len(selected[k]) == 1 for k in
              ('preempt_observed', 'start', 'stop')), 'no_incomplete_stop': not selected['shutdown_incomplete']}
    result = {'events': selected, 'checks': checks, 'valid': False}
    if not checks['one_preempt_start_stop']:
        return result
    preempt, start, stop = (selected[k][0] for k in ('preempt_observed', 'start', 'stop'))
    steps = stop.get('executed_steps', [])
    rid = start.get('target_request_id')
    checks.update(
        same_pid=preempt.get('pid') == start.get('pid') == stop.get('pid'),
        same_request=rid is not None and preempt.get('target_request_id') == rid == stop.get('target_request_id'),
        start_stop_ok=start.get('result') == stop.get('result') == 0,
        bounded_steps=1 <= len(steps) <= 8,
        resume_first=bool(steps and steps[0].get('target_q', 0) > 1 and steps[0].get('payload_computed') is not None),
        event_order=preempt.get('monotonic_ns', 0) <= start.get('monotonic_ns', 0) < stop.get('monotonic_ns', 0),
        step_fields=bool(steps) and all(
            row.get('target_request_id') == rid and row.get('execute_returned') is True
            and row.get('N') == len(row.get('scheduled_q', []))
            and row.get('M') == sum(row.get('scheduled_q', []))
            and row.get('max_q') == max(row.get('scheduled_q', []), default=0)
            and start['monotonic_ns'] <= row.get('execute_submit_start_ns', 0)
            <= row.get('execute_return_ns', 0) <= stop['monotonic_ns'] for row in steps))
    result.update(valid=all(checks.values()),
        observed_event_window_ms=(stop['monotonic_ns'] - start['monotonic_ns']) / 1e6,
        target_scheduled_tokens_in_window=sum(row.get('target_q', 0) for row in steps),
        all_requests_scheduled_tokens_in_window=sum(row.get('M', 0) for row in steps),
        limits=['窗口含同时调度的其他请求和 execute 外的 sampler；不能归为 victim 因果耗时。',
                'CPU known/computed、原 execute 返回及累计 scheduled tokens 均不证明 GPU 完成或实际重算量。',
                'monotonic 事件窗口与 trace 原始 ts 未做时钟校准，不能用两者相减定位逐步 GPU 成本。'])
    return result


def histogram_evidence(events, server_log):
    samples = []
    for event in events:
        data = event.get('histogram') if event.get('event') in ('decode_histogram_partial', 'decode_histogram') else event.get('decode_histogram_partial')
        if data is not None:
            samples.append((event, {int(k): int(v) for k, v in data.items()}))
    if not samples:
        return {'observed': False, 'decision': '无直方图证据，不能据此决定图键。'}
    pids = {e.get('pid') for e, _ in samples}
    if len(pids) != 1:
        return {'observed': False, 'pids': sorted(pids), 'decision': '多PID直方图不得合并。'}
    event, counts = max(samples, key=lambda item: item[0].get('monotonic_ns', 0))
    matches = re.findall(r"cudagraph_capture_sizes['\"]?\s*:\s*(\[[0-9,\s]+\])", server_log)
    size_lists = {tuple(ast.literal_eval(match)) for match in matches}
    sizes = sorted(next(iter(size_lists))) if len(size_lists) == 1 else []
    rows = []
    for n, count in sorted(counts.items()):
        index = bisect.bisect_left(sizes, n)
        padded = sizes[index] if sizes and index < len(sizes) else None
        rows.append({'N': n, 'calls': count, 'configured_bucket_inferred': padded,
                     'extra_rows_per_call': padded - n if padded is not None else None})
    total = sum(counts.values())
    extra = sum(r['calls'] * r['extra_rows_per_call'] for r in rows if r['extra_rows_per_call'] is not None)
    eligible = [r for r in rows if r['configured_bucket_inferred'] is not None]
    return {'observed': True, 'pid': event.get('pid'), 'snapshot_event': event.get('event'),
            'snapshot_monotonic_ns': event.get('monotonic_ns'), 'observed_calls': total,
            'partial': True, 'includes_driver_smoke': True, 'configured_capture_sizes': sizes,
            'rows': rows, 'mapped_calls': sum(r['calls'] for r in eligible),
            'unaligned_calls': sum(r['calls'] for r in eligible if r['extra_rows_per_call']),
            'inferred_extra_row_calls': extra,
            'decision': '仅供筛选；图档位是配置推算，未观察实际 dispatcher 选择，不自动授权新图键。',
            'limits': ['最后稀疏快照不是完整负载直方图；包含单请求 smoke，不猜测或扣除其次数。',
                       '只汇总最后快照，不累加多次累计快照。原档位内相邻 M 的 GEMM tile 可能相同；空 Attention 提前返回。',
                       '额外行数不是 GPU 时间或收益预测；还需确认持续暴露与 reduction/逐元素等真实工作。']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run = args.run.resolve(strict=True)
    output = args.output.resolve()
    if output.exists() or output.is_relative_to(run):
        raise ValueError('输出必须是原件目录外的新文件')
    reader = load_checked(ROOT / 'scripts/summarize_native_trace.py', READER_SHA, 'resume_existing_reader')
    helper = load_checked(ROOT / 'tmp/current-mixed-native/analyze_mixed_native.py', ANALYZER_SHA, 'resume_existing_helper')
    trace = run / 'native-trace.json'
    events_path = run / 'native-events.jsonl'
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines() if line.strip()]
    with sqlite3.connect(trace.as_uri() + '?mode=ro&immutable=1', uri=True) as connection:
        connection.execute('PRAGMA query_only=ON')
        summary = reader.summarize(connection, 'ns', 0)
        sources = []
        for source in summary['kernel_sources']:
            categories = helper.aggregate(source['groups'], True)
            total = source['duration']['sum_ms']
            focus = {k: sum(row['sum_ms'] for row in categories if row['category'] == k)
                     for k in ('Attention-2D', 'GEMM')}
            focus['Other-visible'] = total - sum(focus.values())
            sources.append({'table': source['table'], 'role': source['role'],
                'calls': source['records'], 'sum_ms': total,
                'focus_sum_ms': focus, 'by_category': categories,
                'by_kernel_name': helper.aggregate(source['groups']),
                'bounds': helper.observed_bounds(connection, reader, source['table'])})
    window = window_evidence(events)
    result = {'kind': '恢复窗口可见 GPU 活动诊断，无性能结论', 'run': str(run),
        'input_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (trace, events_path)},
        'reused_reader_sha256': READER_SHA, 'reused_classifier_sha256': ANALYZER_SHA,
        'window': window, 'partial_decode_histogram': histogram_evidence(events, (run / 'server.log').read_text(encoding='utf-8')),
        'kernel_sources_reported_separately': sources,
        'graph_sources_reported_separately': summary['graph_sources'], 'graph_visibility': summary['graph_visibility'],
        'limits': ['kernel 时长求和可重叠，不是窗口延迟/利用率/吞吐；各表不相加。',
                   '全窗口含其他请求、sampler与可能的冷调优，不能归因为单一 victim。',
                   '复用已核 ixsys SQLite ns 解释；kernel span 仅可见首末 kernel，缺失图节点不能按空档推 CPU 等待。',
                   '2D/3D沿用真实 Attention grid.z 分类；图节点可见性不因存在 kernel 自动确认。']}
    with output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'output': str(output), 'window_valid': window['valid'],
        'sources': [{k: s[k] for k in ('table', 'calls', 'sum_ms', 'focus_sum_ms', 'bounds')} for s in sources],
        'histogram_calls': result['partial_decode_histogram'].get('observed_calls')}, ensure_ascii=False))
    return 0 if window['valid'] and summary['has_timed_gpu_kernels'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
