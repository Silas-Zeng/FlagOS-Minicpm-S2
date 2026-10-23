"""只比较已回收的两轮服务原件；不修改测量证据。"""
from pathlib import Path
import json,re

root=Path('experiments/framework')
names={'candidate':'20261022T153947Z-q-hoist-service-candidate-decode4k','baseline':'20261022T154518Z-cpu-combination-combined-decode4k'}
data={}
for arm,name in names.items():
 run=root/name;control=root/(name+'-control')
 m=json.loads((run/'manifest.json').read_text(encoding='utf-8'))
 result=json.loads(next(run.glob('decode-4k/results/*.json')).read_text(encoding='utf-8'))
 db=[json.loads((control/side/'manifest.json').read_text(encoding='utf-8')) for side in ['db-before','db-after']]
 data[arm]={'run_id':name,'manifest':m,'result':result,'db':db,
  'source':json.loads((control/'source-sha256.json').read_text(encoding='utf-8')),
  'kv':int(re.search(r'GPU KV cache size: ([\d,]+) tokens',(run/'server.log').read_text(encoding='utf-8')).group(1).replace(',','')),
  'command':(run/'load-commands.json').read_text(encoding='utf-8').replace(str('/workspace/experiments/minicpm-s2/framework/'+name),'<RUN>')}
 assert result['completed']==64 and result['failed']==0
a,b=data['candidate'],data['baseline']
assert a['manifest']['server_command']==b['manifest']['server_command']
assert a['manifest']['seed']==b['manifest']['seed']==721201
assert a['manifest']['decode_screen'] and b['manifest']['decode_screen']
assert not any(x['manifest'][k] for x in [a,b] for k in ['native_profile','host_profile'])
assert a['command']==b['command']
assert a['kv']==b['kv']==521936
keys=['snapshot_sha256','schema_sha256','logical_content_sha256','table_count','row_count']
db=[{k:d[k] for k in keys} for x in [a,b] for d in x['db']]
assert all(d==db[0] for d in db)
changed={k for k in a['source'].keys()|b['source'].keys() if a['source'].get(k)!=b['source'].get(k)}
assert changed=={'vllm_fl/worker/model_runner.py','vllm_fl/patches/biv150_q_fragment_service.py'}
result={'runs':names,'same_server_args_and_load':True,'kv_tokens':a['kv'],'db_four_endpoints':db[0],
 'declared_source_changes':sorted(changed),'benchmark':{k:x['result'] for k,x in data.items()},
 'throughput_fraction_gain':a['result']['total_token_throughput']/b['result']['total_token_throughput']-1,
 'duration_fraction_saved':1-a['result']['duration']/b['result']['duration'],
 'mean_ttft_fraction_change':a['result']['mean_ttft_ms']/b['result']['mean_ttft_ms']-1,
 'mean_tpot_fraction_change':a['result']['mean_tpot_ms']/b['result']['mean_tpot_ms']-1,
 'conclusion':'一次候选→基线短服务对照，保留局部与服务正信号；不是稳定统计收益、官方完整性能或模型准确率通过。TTFT本轮略退，不能只报吞吐。'}
Path('analysis/q-fragment-service-pair.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ['benchmark','db_four_endpoints']},ensure_ascii=False))
