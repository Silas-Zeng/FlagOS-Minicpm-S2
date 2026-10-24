"""只读八步native诊断；关联GPU graph，不把未覆盖时间解释成CPU空闲。"""
import argparse
from collections import defaultdict
import hashlib
import json
import os
from pathlib import Path
import runpy
import sqlite3
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
READER_SHA = '25c5ae091cbf289e80ff9dea979b6756fd31ee832cc75ae79b55046fd060a162'
SHA = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def union(intervals):
    out = []
    for left, right in sorted((a, b) for a, b in intervals if b > a):
        if out and left <= out[-1][1]:
            out[-1][1] = max(right, out[-1][1])
        else:
            out.append([left, right])
    return out


def cover(rows, left, right):
    selected = [r for r in rows if r['ts'] < right and r['end_ns'] > left]
    merged = union((max(left, r['ts']), min(right, r['end_ns'])) for r in selected)
    missing, cursor = [], left
    for a, b in merged:
        if a > cursor:
            missing.append([cursor, a])
        cursor = b
    if cursor < right:
        missing.append([cursor, right])
    return {'records': selected, 'interval_union_ns': merged,
            'covered_ns': sum(b-a for a, b in merged),
            'uncovered_ns': sum(b-a for a, b in missing), 'uncovered_intervals_ns': missing}


def sqlite_path(path):
    value = str(path.resolve())
    if os.name == 'nt' and value.startswith('\\\\?\\'):
        value = '\\\\' + value[8:] if value.startswith('\\\\?\\UNC\\') else value[4:]
    if os.name == 'nt' and len(value) >= 260:
        raise ValueError('SQLite URI需要显式短路径；不复制或修改原trace')
    return Path(value)


def cpu_window(events, checks):
    starts = [e for e in events if e.get('event') == 'start']
    ends = [e for e in events if e.get('event') in ('stop', 'incomplete')]
    checks['one_start_one_terminal'] = len(starts) == len(ends) == 1
    if not checks['one_start_one_terminal']:
        return None
    start, end = starts[0], ends[0]
    pid, ids, n = start.get('pid'), start.get('request_ids'), start.get('N', 0)
    checks['CPU_terminal_complete'] = end['event'] == 'stop' and end.get('result') == start.get('result') == 0
    checks['CPU_clock_MONOTONIC'] = 'CLOCK_MONOTONIC)' in start.get('clock_implementation', '')
    checks['CPU_same_pid_stable_N'] = (type(pid) is int and end.get('pid') == pid
        and type(n) is int and n >= 16 and start.get('M') == n
        and isinstance(ids, list) and len(ids) == len(set(ids)) == n)
    rows = end.get('executed_steps', [])
    checks['CPU_exactly_eight_steps'] = len(rows) == 8
    checks['CPU_window_order'] = (type(start.get('monotonic_ns')) is int
        and type(end.get('cpu_window_end_ns')) is int and type(end.get('monotonic_ns')) is int
        and start['monotonic_ns'] < end['cpu_window_end_ns'] <= end['monotonic_ns'])
    valid, errors, previous = [], [], None
    keys = ('execute_submit_start_ns', 'execute_return_ns', 'sample_submit_start_ns', 'sample_return_ns')
    for index, row in enumerate(rows):
        points = [row.get(k) for k in keys]
        ok = (checks['CPU_same_pid_stable_N'] and checks['CPU_window_order']
            and row.get('index') == index and row.get('N') == row.get('M') == n
            and row.get('request_ids') == ids and row.get('all_q_one') is True
            and row.get('phase') == 'pure_decode_no_lifecycle_change'
            and row.get('execute_returned') is True and row.get('sample_returned') is True
            and all(type(t) is int for t in points) and points == sorted(points)
            and start['monotonic_ns'] <= points[0] <= points[-1] <= end['cpu_window_end_ns']
            and (previous is None or previous <= points[0]))
        if ok:
            valid.append(row)
            previous = points[-1]
        else:
            errors.append(index)
    checks['CPU_all_rows_valid'] = len(valid) == len(rows) and bool(rows)
    return {'pid': pid, 'start': start, 'terminal': end, 'valid_rows': valid, 'invalid_row_indices': errors}


def read(run):
    trace, events_path = run/'native-trace.json', run/'native-events.jsonl'
    checks = {}
    result = {'kind': 'puredecode graph/API同钟局部诊断，无优化性能结论',
        'run': str(run), 'status': 'unsupported_complete_window', 'complete': False,
        'checks': checks, 'partial_evidence_available': False,
        'limits': ['未覆盖只表示同进程可见GPU活动未覆盖，不能称CPU idle、GPU idle或可兑现收益。',
            'Graph为GPU聚合区间，不证明内部节点完整；host API覆盖不计入GPU busy。',
            '边界sync排空queue2；前两步不用于内侧间隔判读，此窗口不是自然吞吐。',
            'sampler归属仅按同pid/correlationId的launch API位于CPU sample作用域，不按kernel名字猜测。',
            'clock offset范围是已观察snapshot散布，不是假定全程时钟误差上界。',
            '边缘缺失保partial关联，不自动要求补跑；是否足以回答问题由owner决定。']}
    try:
        result['input_sha256'] = {p.name: SHA(p) for p in (trace, events_path)}
        checks['terminal_run_exit0'] = (run/'exit-code').read_text(encoding='utf-8').strip() == '0'
        events = [json.loads(line) for line in events_path.read_text(encoding='utf-8').splitlines() if line.strip()]
        window = cpu_window(events, checks)
        result['CPU_window'] = window
        if window is None:
            return result
        helper = ROOT/'scripts/summarize_native_trace.py'
        if SHA(helper) != READER_SHA:
            raise ValueError('既有SQLite reader身份变化')
        lib = runpy.run_path(str(helper))
        result['reused_reader_sha256'] = READER_SHA
        with sqlite3.connect(sqlite_path(trace).as_uri()+'?mode=ro&immutable=1', uri=True) as con:
            schema = lib['schema_of'](con)
            result['trace_schema'] = {k: v for k, v in schema.items() if k in (
                'cuda_graph_data', 'cuda_api_data', 'cuda_kernel_data', 'cuda_memcpy_data',
                'cuda_memset_data', 'cu_memcpy', 'cu_memset', 'clock_snapshot', 'metadata')}
            version = con.execute("SELECT str_value FROM metadata WHERE name='ixsys_version'").fetchall()
            checks['known_ixsys_ns_format'] = version == [('V4.4.0',)]
            result['format'] = {'version_rows': version, 'time_unit': 'ns',
                'basis': '已核ixsys V4.4.0/Perfetto SQL ts,dur格式；其它版本不推同钟归属'}
            clocks = con.execute("SELECT ts,clock_value FROM clock_snapshot WHERE clock_name='MONOTONIC' ORDER BY ts").fetchall()
            clocks = [(a,b) for a,b in clocks if type(a) is int and type(b) is int]
            checks['clock_snapshots_present'] = bool(clocks)
            checks['clock_snapshots_monotone'] = bool(clocks) and all(a[1] <= b[1] for a,b in zip(clocks,clocks[1:]))
            offsets = sorted(b-a for a,b in clocks)
            offset = offsets[len(offsets)//2] if offsets else None
            checks['clock_snapshots_bracket_CPU_window'] = bool(clocks) and (
                clocks[0][1] <= window['start']['monotonic_ns']
                and window['terminal']['monotonic_ns'] <= clocks[-1][1])
            result['clock_mapping'] = {'samples': len(clocks), 'trace_to_monotonic_offset_ns': offset,
                'observed_offset_min_ns': min(offsets) if offsets else None,
                'observed_offset_max_ns': max(offsets) if offsets else None,
                'method': 'monotonic - median observed(clock_value-ts); preserve observed offset spread'}
            visibility = {}

            def activity(kind, choices):
                table = next((t for t in choices if t in schema), None)
                if table is None:
                    visibility[kind] = {'status': 'not_recorded_or_unsupported'}
                    return []
                query, resolution, cols = lib['event_query'](con, schema, table)
                wanted = {k: lib['column'](cols, k) for k in ('ts','dur','processId')}
                if not all(wanted.values()):
                    visibility[kind] = {'status': 'no_timing_or_pid', 'table': table, 'rows': schema[table]['rows']}
                    return []
                cursor = con.execute('SELECT * FROM ('+query+') WHERE '+lib['ident'](wanted['processId'])+'=?', (window['pid'],))
                out, truncated = [], 0
                for raw in cursor:
                    row = dict(zip(cols,raw)); ts, dur = row[wanted['ts']], row[wanted['dur']]
                    if type(ts) is not int or type(dur) is not int or dur < 0:
                        truncated += 1
                        continue
                    out.append({k: row.get(k) for k in ('id','name','processId','threadId','correlationId',
                        'deviceId','contextId','streamId','latency')} | {'ts': ts, 'dur': dur, 'end_ns': ts+dur, 'kind': kind})
                visibility[kind] = {'status': 'timed_rows' if out else 'no_positive_evidence',
                    'table': table, 'resolution': resolution, 'records': len(out), 'truncated_rows': truncated}
                return out

            graphs = activity('graph', ('cuda_graph_data','cuda_graph'))
            apis = activity('host_API', ('cuda_api_data','cuda_api'))
            kernels = activity('kernel', ('cuda_kernel_data','cuda_kernel'))
            copies = activity('memcpy', ('cuda_memcpy_data','cuda_memcpy','cu_memcpy'))
            sets = activity('memset', ('cuda_memset_data','cuda_memset','cu_memset'))
        result['activity_visibility'] = visibility
        by_api, by_graph = defaultdict(list), defaultdict(list)
        for row in apis:
            if row['name'] == 'cudaGraphLaunch':
                by_api[row['correlationId']].append(row)
        for row in graphs:
            by_graph[row['correlationId']].append(row)
        pairs, unlinked = [], []
        for corr in by_api.keys() | by_graph.keys():
            aa, gg = by_api[corr], by_graph[corr]
            if corr is not None and len(aa) == len(gg) == 1 and gg[0]['dur'] > 0:
                pairs.append({'correlationId': corr, 'API': aa[0], 'GPU_graph': gg[0],
                    'latency_consistent': gg[0]['latency'] == gg[0]['ts']-aa[0]['ts']})
            else:
                unlinked.append({'correlationId': corr, 'APIs': aa, 'GPU_graphs': gg})
        result['unique_raw_correlations'] = sorted(pairs, key=lambda p: p['API']['ts'])
        result['unlinked_or_ambiguous'] = unlinked
        clock_ok = all(checks[k] for k in ('CPU_clock_MONOTONIC','CPU_same_pid_stable_N',
            'known_ixsys_ns_format','clock_snapshots_present','clock_snapshots_monotone'))
        if not clock_ok:
            return result
        def inside(row, begin, end):
            # 只接收在全部已观察offset选择下都落入同一CPU作用域的API；
            # 靠近端点的归属保留unknown，不用容差放宽phase。
            return (clocks[0][1] <= begin <= end <= clocks[-1][1]
                and begin-min(offsets) <= row['ts'] and row['end_ns'] <= end-max(offsets))

        mapped, mapping_reasons = [], {}
        for step in window['valid_rows']:
            matches = [p for p in pairs if inside(p['API'],step['execute_submit_start_ns'],step['execute_return_ns'])]
            if len(matches) == 1:
                pair = matches[0]
                if pair['latency_consistent']:
                    mapped.append({'step_index': step['index'], **pair,
                        'execute_trace_interval_nominal_ns': [step['execute_submit_start_ns']-offset, step['execute_return_ns']-offset],
                        'sample_trace_interval_nominal_ns': [step['sample_submit_start_ns']-offset, step['sample_return_ns']-offset]})
                else:
                    mapping_reasons[step['index']] = 'GPU_latency_field_inconsistent'
            else:
                mapping_reasons[step['index']] = 'no_unique_graph_API_inside_execute_and_clock_snapshot_bracket'
        # 一个pair不能因时钟边界容差同时归给两个step。
        repeated = {p['correlationId'] for p in mapped if sum(q['correlationId']==p['correlationId'] for q in mapped) != 1}
        mapped = [p for p in mapped if p['correlationId'] not in repeated]
        result['partial_step_associations'] = mapped
        result['step_mapping_reasons'] = mapping_reasons
        result['ambiguous_reused_correlations'] = sorted(repeated)
        result['partial_evidence_available'] = bool(mapped)
        checks['unique_eight_graph_API_pairs'] = len(pairs) == len(graphs) == len(by_api) == 8 and not unlinked
        checks['all_eight_CPU_steps_mapped'] = len(mapped) == 8 and {p['step_index'] for p in mapped} == set(range(8))
        checks['all_latencies_consistent'] = bool(pairs) and all(p['latency_consistent'] for p in pairs)
        checks['no_graph_API_truncation'] = all(visibility[k].get('truncated_rows') == 0 for k in ('graph','host_API'))
        checks['graphs_finish_before_profiler_stop'] = bool(mapped) and all(
            p['GPU_graph']['end_ns'] <= window['terminal']['monotonic_ns']-max(offsets) for p in mapped)
        api_corr = defaultdict(list)
        for row in apis:
            api_corr[row['correlationId']].append(row)
        for row in kernels+copies+sets:
            matched = api_corr[row['correlationId']]
            phases = []
            if row['correlationId'] is not None and len(matched) == 1:
                for step in window['valid_rows']:
                    for phase, a, b in (('execute', 'execute_submit_start_ns','execute_return_ns'),
                            ('sample','sample_submit_start_ns','sample_return_ns')):
                        if inside(matched[0],step[a],step[b]):
                            phases.append({'step_index':step['index'],'CPU_launch_phase':phase})
            row['launch_scope'] = phases[0] if len(phases) == 1 else 'unattributed_or_ambiguous'
        per_step = {p['step_index']:p for p in mapped}
        gaps = []
        for index in range(2,7):
            if index not in per_step or index+1 not in per_step:
                continue
            left, right = per_step[index]['GPU_graph']['end_ns'], per_step[index+1]['GPU_graph']['ts']
            gap = {'left_step':index,'right_step':index+1,'begin_trace_ns':left,'end_trace_ns':right,
                'graph_overlap_ns':max(0,left-right),'scope':'inner only; first two boundary-perturbed steps omitted'}
            if right > left:
                gap['GPU_visible'] = cover(kernels+copies+sets+graphs,left,right)
                gap['host_API_visible_separate'] = cover(apis,left,right)
                gap['sample_launch_GPU_visible'] = cover([r for r in kernels+copies+sets
                    if isinstance(r['launch_scope'],dict) and r['launch_scope']['CPU_launch_phase']=='sample'],left,right)
            gaps.append(gap)
        result['inner_graph_intervals'] = gaps
        result['complete'] = all(checks.values())
        result['status'] = 'supported_complete_window' if result['complete'] else 'unsupported_complete_window'
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as error:
        result['read_error'] = type(error).__name__+': '+str(error)
    finally:
        result['unsupported_reasons'] = [k for k,v in checks.items() if not v]
        result['reader_sha256'] = SHA(Path(__file__))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖既有分析')
    run = args.run_dir
    if not run.is_absolute():
        run = run.resolve() if run.exists() else ROOT/'experiments/framework'/run
    result = read(run)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({k:result[k] for k in ('status','complete','partial_evidence_available','unsupported_reasons')},ensure_ascii=False))
    raise SystemExit(0 if result['complete'] else 1)
