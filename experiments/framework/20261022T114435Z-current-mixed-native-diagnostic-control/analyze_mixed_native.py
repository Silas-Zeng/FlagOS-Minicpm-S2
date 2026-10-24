"""复用现有 ixsys SQLite reader，仅补kernel同名聚合和保守路径分类。"""
import argparse
import ast
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3

EXPECTED_READER = '25c5ae091cbf289e80ff9dea979b6756fd31ee832cc75ae79b55046fd060a162'


def category(name, parameters):
    lower = name.lower()
    if 'reduce_segments' in lower:
        return 'Attention-reduce'
    if 'kernel_unified_attention' in lower:
        try:
            grid = parameters.get('grid')
            grid = ast.literal_eval(grid) if isinstance(grid, str) else grid
            if isinstance(grid, (tuple, list)) and len(grid) in (2, 3):
                z = 1 if len(grid) == 2 else grid[2]
                if type(z) is int and z > 1:
                    return 'Attention-3D'
                if z == 1:
                    return 'Attention-2D'
        except (ValueError, SyntaxError, TypeError):
            pass
        return 'Attention-dimension-unobserved'
    if 'reshape_and_cache' in lower:
        return 'KV-writer'
    if 'mm_kernel' in lower or 'gemm' in lower or 'matmul' in lower:
        return 'GEMM'
    if 'linear_kernel' in lower:
        return 'Linear-LM-head-shape-unobserved'
    if any(token in lower for token in (
            'weighted_hist', 'row_stats_partial', 'row_max_reduce', 'hist_walk',
            'apply_mask', 'softmax_kernel', 'exponential', 'argmax_kernel', 'true_div')):
        return 'Sampler-and-vocab-elementwise-name-based'
    return 'Other-or-unattributed'


def aggregate(groups, by_category=False):
    result = defaultdict(lambda: {'calls': 0, 'sum_ms': 0., 'kernel_names': set()})
    total = sum(g['duration']['sum_ms'] for g in groups)
    for group in groups:
        name = group['kernel_name']
        key = category(name, group['parameters']) if by_category else name
        row = result[key]
        row['calls'] += group['count']
        row['sum_ms'] += group['duration']['sum_ms']
        row['kernel_names'].add(name)
    rows = []
    for name, row in result.items():
        rows.append({'category' if by_category else 'name': name,
                     'calls': row['calls'], 'sum_ms': row['sum_ms'],
                     'observed_kernel_sum_percent': row['sum_ms'] / total * 100 if total else None,
                     'mean_ms': row['sum_ms'] / row['calls'] if row['calls'] else None,
                     'kernel_names': sorted(row['kernel_names'])})
    return sorted(rows, key=lambda r: -r['sum_ms'])


def observed_bounds(connection, reader, table):
    columns = [r[1] for r in connection.execute('PRAGMA table_info(' + reader.ident(table) + ')')]
    if 'ts' not in columns or 'dur' not in columns:
        return {'observed': False}
    intervals = connection.execute('SELECT ts,ts+dur FROM ' + reader.ident(table)
                                   + ' WHERE dur>0 ORDER BY ts').fetchall()
    if not intervals:
        return {'observed': False}
    begin, end = intervals[0]
    union = 0
    for left, right in intervals[1:]:
        if left > end:
            union += end - begin
            begin, end = left, right
        else:
            end = max(end, right)
    union += end - begin
    span = max(r[1] for r in intervals) - intervals[0][0]
    return {'observed': True, 'first_ts_ns': intervals[0][0],
            'last_end_ns': max(r[1] for r in intervals), 'span_ms': span / 1e6,
            'kernel_interval_union_ms': union / 1e6,
            'uncovered_inside_kernel_span_ms': (span - union) / 1e6,
            'limit': 'Observed intervals only; missing kernels/graph activity prevent CPU-idle or GPU-util inference.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--summarizer-path', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError('new output required')
    raw_reader = args.summarizer_path.read_bytes()
    if hashlib.sha256(raw_reader).hexdigest() != EXPECTED_READER:
        raise RuntimeError('existing SQLite reader changed')
    spec = importlib.util.spec_from_file_location('existing_native_reader', args.summarizer_path)
    reader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(reader)
    trace = args.trace.resolve(strict=True)
    with sqlite3.connect(trace.as_uri() + '?mode=ro', uri=True) as connection:
        summary = reader.summarize(connection, 'ns', 0)
        sources = []
        for source in summary['kernel_sources']:
            groups = source['groups']
            sources.append({'table': source['table'], 'calls': sum(g['count'] for g in groups),
                            'sum_ms': source['duration']['sum_ms'],
                            'by_kernel_name': aggregate(groups), 'by_category': aggregate(groups, True),
                            'attention_launch_groups': [g for g in groups if category(
                                g['kernel_name'], g['parameters']).startswith('Attention')],
                            'bounds': observed_bounds(connection, reader, source['table'])})
    events_path = trace.with_name('native-events.jsonl')
    events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines()] if events_path.exists() else []
    start = [e for e in events if e.get('event') == 'start']
    stop = [e for e in events if e.get('event') == 'stop']
    complete_mixed = bool(len(start) == len(stop) == 1 and start[0]['pid'] == stop[0]['pid']
        and stop[0].get('result') == 0 and len(stop[0].get('executed_shapes', [])) == 3
        and len(stop[0].get('executed_scheduled_tokens', [])) == 3
        and all(n >= 2 and total > n and maximum > 1 for n, total, maximum in stop[0]['executed_shapes'])
        and all(len(values) >= 2 and 1 in values and max(values) > 1
                for values in stop[0]['executed_scheduled_tokens']))
    result = {'kind': 'current mixed native GPU evidence; no performance verdict',
              'trace': str(trace), 'trace_sha256': hashlib.sha256(trace.read_bytes()).hexdigest(),
              'reader_sha256': EXPECTED_READER, 'current_three_mixed_window_valid': complete_mixed,
              'start_stop_events': start + stop, 'kernel_sources_reported_separately': sources,
              'graph_sources_reported_separately': [{k: source[k] for k in ('table', 'records', 'duration', 'groups')}
                                                     for source in summary['graph_sources']],
              'graph_visibility': summary['graph_visibility'],
              'limits': ['Ranks refer only to observed kernel sums, not E2E or throughput.',
                         '2D/3D classification uses actual54c grid.z: 1 versus >1; grids are not tensor shapes.',
                         'Sampler/linear labels require source/shape attribution; no new shape is guessed.',
                         'Graph aggregates are not added to kernel sums or assumed to expose graph nodes.',
                         'Run only after profiler has stopped/flushed; cold/JIT gaps may remain after two warm mixed steps.']}
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(json.dumps({'output': str(args.output), 'current_three_mixed_window_valid': complete_mixed,
                      'sources': [{'table': s['table'], 'calls': s['calls'], 'sum_ms': s['sum_ms'],
                                   'top': s['by_kernel_name'][:8], 'categories': s['by_category']}
                                  for s in sources]}, ensure_ascii=False))
    return 0 if sources and summary.get('has_timed_gpu_kernels') else 2


if __name__ == '__main__':
    raise SystemExit(main())
