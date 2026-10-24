import csv,hashlib,json,re,shutil
from pathlib import Path
root=Path.cwd()
name='20261023T054306Z-compute-order-baseline-context16k'
run=root/'experiments/framework'/name
control=run.with_name(name+'-control')
progress=run.with_name(name+'-progress')
manifest=json.loads((run/'manifest.json').read_text())
files=list(run.glob('*/results/*.json'));assert len(files)==1
result=json.loads(files[0].read_text())
before=json.loads((control/'db-before/manifest.json').read_text())
after=json.loads((control/'db-after/manifest.json').read_text())
fields=['snapshot_sha256','schema_sha256','logical_content_sha256','table_count','row_count']
assert {k:before[k] for k in fields}=={k:after[k] for k in fields}
post=json.loads((run/'postflight-full.json').read_text())
kv=int(re.search(r'GPU KV cache size: ([0-9,]+) tokens',(run/'server.log').read_text()).group(1).replace(',',''))
record={'run_id':name,'status':'baseline_complete_candidate_not_deployed','source_count':422,
'sealed_files':560,'archive_bytes':3306907,'archive_sha256':'64e2410f54185d95f6e2e6d68ff98a10fc4b49a3846621e3338f9952721b4e7b',
'import':{'added':561,'matched_existing':0,'complete':True,'transfer_exit_before_import':0},
'commands':str((control/'command.txt').relative_to(root)).replace('\\','/'),
'load':{'input_len':16384,'output_len':128,'max_concurrency':64,'num_prompts':32,'seed':721201},
'result':{k:result[k] for k in ['completed','failed','duration','total_token_throughput','output_throughput','mean_ttft_ms','mean_tpot_ms']},
'kv_capacity_tokens':kv,'database_unchanged':True,'database':{k:after[k] for k in fields},
'cleanup':{'gpu':post['query'].strip(),'ports_closed':post['ports_closed'],'source_failures':post['source_failures']},
'gain':None,'decision':'保留原422短负载基线；候选未部署，无性能收益结论。KV521936不同于旧044216诊断521840；后续候选须匹配源码差异、DB/KV与参数，不能靠重启或假buffer凑容量。'}
with (progress/'completion.json').open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
archive=root/'archive/ai/20261022-framework-kv/compute-order-owner';archive.mkdir(parents=True,exist_ok=False)
for p in (root/'tmp/compute-order-owner').glob('*.py'):shutil.copyfile(p,archive/p.name)
# 当前只新增已完成基线登记，不改旧测量。
registry=root/'experiments/registry.csv'
with registry.open(encoding='utf-8',newline='') as f:
 reader=csv.DictReader(f);names=reader.fieldnames;rows=list(reader)
assert name not in {r['run_id'] for r in rows}
row=dict.fromkeys(names,'')
row.update(run_id=name,local_date='2026-10-23',utc_start=manifest['started_utc'],profile_id='compute_order',phase='baseline_context16k_short_output',device='Iluvatar BI-V150',
vllm_commit=manifest['plugin_base_revision'],flaggems_commit=manifest['flaggems_revision'],input_len=16384,output_len=128,concurrency=64,num_prompts=32,profiler='false',status='baseline_complete_candidate_not_deployed',artifacts='experiments/framework/'+name,
conclusion='原422短负载基线，32成功0失败、exit0，104.312939462s、5065.373507102 total tok/s；560原件逐文件核对导入。原bc51/SERVER/seed721201、VERIFY0、finiteunset、无profiler；KV521936，DB554表/20517行三SHA前后不变。候选仍在CPU实现和互审，gain=null；后续先正确性并检查同DB/KV等可比条件，不与旧coverage诊断比较性能；设备68MiB/0、双栈9031关闭。')
with registry.open('a',encoding='utf-8',newline='') as f:csv.DictWriter(f,fieldnames=names,lineterminator='\n').writerow(row)
print(json.dumps(record,ensure_ascii=False))

