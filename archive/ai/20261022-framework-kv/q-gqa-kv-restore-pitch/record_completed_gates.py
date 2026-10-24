"""读已核的原件，记录422准确率及单层H2D门；不访问设备。"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
name='20261022T215836Z-q-gqa-kv-swap'
run=ROOT/'experiments/accuracy'/name
control=run.with_name(name+'-control')
review=read(run/'accuracy-review.json');post=read(run/'postflight-full.json')
source=read(control/'source-sha256.json')
expected=ROOT/'tmp/q-gqa-kv-swap/expected-source-sha256.json'
assert sha(expected)=='82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
assert source==read(expected) and len(source)==422
assert post['source_count']==422 and not post['source_failures'] and not post['archived_source_failures']
assert review['validity']=='valid' and review['samples']==105
manifest=read(run/'manifest.json');old=read(ROOT/'experiments/accuracy/20261022T184819Z-q-gqa-framework/manifest.json')
assert manifest['server_command']==old['server_command']
assert all(v==old['sha256'][k] for k,v in manifest['sha256'].items() if not k.startswith('plugin/'))
command=(control/'command.txt').read_text(encoding='utf-8')
assert 'BIV150_KV_VERIFY_RESTORE=0' in command and '-u BIV150_FINITE_GROWTH_ADMISSION' in command
keys=('table_count','row_count','snapshot_sha256','schema_sha256','logical_content_sha256')
db={n:{k:read(run/('database-'+n)/'manifest.json')[k] for k in keys} for n in ('before','after')}
log=(run/'server.log').read_text(encoding='utf-8')
markers={}
for marker in ('BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED','BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED'):
    rows=[json.loads(s.split(marker+' ',1)[1]) for s in log.splitlines() if marker+' ' in s]
    assert rows and all(x['actual_execute'] is True and x['complete_step_return'] is True for x in rows)
    markers[marker]=rows
events=[json.loads(s.split('BIV150_KV_PROTOCOL ',1)[1]) for s in log.splitlines() if 'BIV150_KV_PROTOCOL ' in s]
result={'run_id':name,'accuracy':review,'source_count':422,'source_map_sha256':sha(expected),
        'original_nonplugin_sources_and_SERVER_unchanged':True,'database':db,'database_unchanged':db['before']==db['after'],
        'actual_Q_GQA_markers':markers,'KV_events':events,
        'KV_actual_transfer_count':sum(e['event']=='RPC_ACK' for e in events),
        'KV_capacity_tokens':[int(x.replace(',','')) for x in re.findall(r'GPU KV cache size: ([\d,]+) tokens',log)],
        'sealed_files':len(read(control/'evidence-seal.json')['files']),
        'limitations':['本次准确率未出现真实SAVE/FULL事务；真实恢复字节正确性引用213134的42层VERIFY1，不能把安装标记说成事务命中。',
                       '103/105仅表示本次通过；不与旧101/105解释为精度提升，不是性能结果。',
                       '关闭阶段的EngineDeadError/ResourceWarning/semaphore警告留在原日志；postflight确认设备/端口/owned进程清理。']}
with (ROOT/'analysis/q-gqa-kv-swap-accuracy.json').open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
name='20261022T222047Z-kv-pitched-restore-gate';run=ROOT/'experiments/framework'/name
raw=read(run/'results.json');manifest=read(run/'manifest.json')
assert raw['status']=='pass' and all(raw['case']['checks'].values())
summary={'run_id':name,'status':raw['status'],'bridge_sha256':raw['bridge_sha256'],
         'case':{k:v for k,v in raw['case'].items() if k!='source_evidence'},'RNG_unchanged':raw['RNG_unchanged'],
         'source_unchanged':manifest['source_unchanged'],'database_unchanged':manifest['db_before']==manifest['db_after'],
         'sealed_files':88,'performance_gain_claim':None,'scope':raw['scope']}
with (ROOT/'analysis/kv-pitched-restore-method.json').open('x',encoding='utf-8') as f:json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'accuracy':review['correct'],'samples':review['samples'],'DB':db,'KV_transfers':result['KV_actual_transfer_count'],
                  'method_status':raw['status'],'new_SO':raw['bridge_sha256']},ensure_ascii=False))
