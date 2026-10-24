"""比较两次启动分项与原 smoke，不能据此报告性能或定位具体 allocator。"""
from pathlib import Path
import json
import re
import sys

root = Path(__file__).resolve().parents[2]
results = {}
for side, name in zip(('baseline', 'finite'), sys.argv[1:], strict=True):
    run = root / 'experiments/framework' / name
    control = run.with_name(name + '-control')
    validation = json.loads((control / 'observation-validation.json').read_text(encoding='utf-8'))
    assert validation['status'] == 'pass' and all(validation['checks'].values())
    assert (control / 'runner-exit-code').read_text(encoding='utf-8').strip() == '0'
    event = next(e for e in validation['events'] if e['event'] == 'DETERMINE_RETURN')
    log = (run / 'server.log').read_text(encoding='utf-8', errors='replace')
    matches = re.findall(r'GPU KV cache size: ([\d,]+) tokens', log)
    assert len(matches) == 1
    smoke = json.loads((run / 'smoke.json').read_text(encoding='utf-8'))
    db = {}
    for phase in ('db-before', 'db-after'):
        files = list((control / phase).glob('*.json'))
        assert len(files) == 1
        db[phase] = json.loads(files[0].read_text(encoding='utf-8'))
    results[side] = {'run': name, 'kv_tokens': int(matches[0].replace(',', '')),
        'returned_bytes': event['returned'], 'worker_fields': event['worker_fields'],
        'profile': event['profile'], 'init_snapshot': event['init_snapshot'],
        'before_profile': event['before_profile'], 'after_profile': event['after_profile'],
        'derived': event['derived_only_not_new_samples'], 'db': db,
        'smoke_choice': smoke['choices'][0],
        'q_installed': 'BIV150_Q_FRAGMENT_SERVICE_INSTALLED' in log,
        'gqa_installed': 'BIV150_GQA_DECODE_INSTALL' in log,
        'actual_q_gqa_selected': 'BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED' in log,
        'finite_installed': 'BIV150_FINITE_GROWTH_ADMISSION_INSTALLED' in log}
a, b = results['baseline'], results['finite']
deltas = {}
for group in ('worker_fields', 'profile', 'init_snapshot', 'before_profile', 'after_profile'):
    deltas[group] = {key: b[group][key] - value for key, value in a[group].items()
        if type(value) in (int, float) and type(b[group].get(key)) in (int, float)
        and key not in ('timestamp', 'profile_time')}
out = {'kind': '启动标量诊断；不作性能pair、不回填历史因果', 'runs': results,
       'finite_minus_baseline': deltas,
       'kv_token_difference': b['kv_tokens'] - a['kv_tokens'],
       'available_byte_difference': b['returned_bytes'] - a['returned_bytes'],
       'same_smoke_text': a['smoke_choice']['text'] == b['smoke_choice']['text'],
       'same_smoke_token_ids': isinstance(a['smoke_choice'].get('token_ids'), list)
           and len(a['smoke_choice']['token_ids']) == 32
           and a['smoke_choice']['token_ids'] == b['smoke_choice'].get('token_ids'),
       'db_four_endpoint_checks': {key: len({r['db'][phase][key] for r in results.values()
           for phase in ('db-before', 'db-after')}) == 1 for key in
           ('snapshot_sha256', 'schema_sha256', 'logical_content_sha256', 'table_count', 'row_count')},
       'strict_performance_gain': None}
path = root / 'analysis/current-kv-memory-smokes.json'
with path.open('w', encoding='utf-8') as stream:
    json.dump(out, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({key: value for key, value in out.items() if key != 'runs'}, ensure_ascii=True))
