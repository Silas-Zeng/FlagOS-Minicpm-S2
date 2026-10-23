"""复用已验封存与原官方validation，登记绝对结果；不重算均值或运行测试。"""
from pathlib import Path
import csv
import hashlib
import io
import json
import re

ROOT = Path(__file__).resolve().parents[2]
NAME = '20261022T231746Z-q-gqa-kv-swap-official'
run = ROOT / 'experiments/official' / NAME
control = run.with_name(NAME + '-control')
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
result = read(run / 'result.json')
seal = read(control / 'evidence-seal.json')
transactions = read(ROOT / 'analysis/q-gqa-kv-official-transactions.json')
assert result['exit_code'] == 0 and result['validation']['complete']
assert transactions['passed_logged_chain_checks']
assert transactions['log_sha256'] == seal['files'][NAME+'/server.log']
summary_path = next(run.glob('benchmark_results/summary*.csv'))
rows = list(csv.DictReader(summary_path.open(encoding='utf-8')))
raw_path = next(run.glob('benchmark_results/raw*.csv'))
raw = list(csv.DictReader(raw_path.open(encoding='utf-8')))
db = {}
for label in ('before', 'after'):
    m = read(run / ('database-'+label) / 'manifest.json')
    db[label] = {k:m[k] for k in ('table_count','row_count','snapshot_sha256','schema_sha256','logical_content_sha256')}
log = (run/'server.log').read_text(encoding='utf-8')
kv = int(re.search(r'GPU KV cache size: ([\d,]+) tokens',log).group(1).replace(',',''))
analysis = dict(run_id=NAME, status='completed_official_absolute_result_no_gain_claim',
    source_count=422, sealed_files=len(seal['files']), validation=result['validation'],
    successful_requests=sum(int(float(r['Successful Requests'])) for r in raw),
    summary=rows, KV_tokens=kv, database=db, recorded_key_chains=transactions['complete_logged_chains'],
    transaction_analysis='analysis/q-gqa-kv-official-transactions.json',
    accuracy_reference='20261022T215836Z-q-gqa-kv-swap: 103/105；本轮未重跑',
    gain=None, decision='保留原件和当前候选；没有新因果收益声明。下一步依据已完成短诊断的实际GPU区间。',
    limits=['原官方每case四轮、丢首轮，直接保留原第2–4轮均值。',
        'DB544/20246→554/20517；不能与旧414跨DB及KV条件算因果收益。',
        '16条已记录key链完整不证明全部抢占覆盖；在途11次metrics仅为局部观察。',
        'VERIFY0不产生新的42层逐字节验证；该资格沿用独立VERIFY1。'])
output = ROOT/'analysis/q-gqa-kv-official-final.json'
with output.open('x', encoding='utf-8') as f:
    json.dump(analysis,f,ensure_ascii=False,indent=2);f.write('\n')
registry = ROOT/'experiments/registry.csv'
with registry.open(encoding='utf-8',newline='') as f:
    reader=csv.DictReader(f); fields=reader.fieldnames; entries=list(reader)
selected=[r for r in entries if r['run_id']==NAME]
assert len(selected)==1
selected[0].update(status=analysis['status'],artifacts='experiments/official/'+NAME,
    conclusion='原422官方两case×4完成exit0、1536成功，717原件全核；原8行raw/2摘要/丢首轮2–4均值不改。4K总4957.95/output991.59 tok/s、264.56s；16K总3669.74/output215.87 tok/s、607.19s。KV521840、DB544/20246→554/20517，gain=null，不与旧414跨条件算收益。原Q/GQA同Engine各42实际命中；16独立key的SAVE/FULL/DROP/runner/output链完整，rollback0；VERIFY0资格与准确率103/105另见既有门。原owner清理；详analysis/q-gqa-kv-official-final.json。')
native='20261023T002156Z-q-gqa-puredecode-native-diagnostic'
assert not any(r['run_id']==native for r in entries)
entry=dict(selected[0]); entry.update(run_id=native,utc_start='2026-10-23T00:21:56+00:00',
    profile_id='q_gqa_puredecode_native',phase='current422_puredecode_and_mixed_coverage',
    input_len='16384',output_len='1024',concurrency='64',num_prompts='32',profiler='true',
    status='finished_native_pending_remote_evidence',
    artifacts='experiments/framework/'+native+'-progress',
    conclusion='官方封存后串行启动，driver390086/Engine390300；已实核exit0、8 CPU步/8实际GPU graph初验、device68MiB/0与server wrapper退出。随后SSH公钥认证被网关拒绝，尚未执行封存/导入，独立graph reader与完整mixed摘要待原件；不能以局部hist尾部判全负载零遗漏，无性能收益声明。代码、命令和初验快照已保存；恢复连接先查原run，不重启。')
entries.append(entry)
buf=io.StringIO(newline=''); writer=csv.DictWriter(buf,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows(entries)
registry.write_bytes(buf.getvalue().encode('utf-8'))
print(json.dumps({'official':NAME,'successful_requests':analysis['successful_requests'],'chains':analysis['recorded_key_chains'],
    'DB':{k:(v['table_count'],v['row_count']) for k,v in db.items()},'registry_rows':len(entries)},ensure_ascii=False))
