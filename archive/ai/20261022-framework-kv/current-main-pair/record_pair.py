"""登记已回收的140324/141159，不改原始证据或重跑测量。"""
import csv
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
pair = json.loads((root / 'analysis/compute-order-current-main-pair.json').read_text(encoding='utf-8'))
assert pair['gain'] is None and [k for k,v in pair['checks'].items() if not v] == ['same_KV']
percent = pair['descriptive_percent']['total_token_throughput_change']
registry = root / 'experiments/registry.csv'
with registry.open(encoding='utf-8-sig', newline='') as stream:
    reader = csv.DictReader(stream); fields = reader.fieldnames; rows = list(reader)
ids = {r['run_id'] for r in rows}
new = []
for label, arm in pair['runs'].items():
    run = arm['run_id']; assert run not in ids
    manifest = json.loads((root / 'experiments/framework' / run / 'manifest.json').read_text(encoding='utf-8'))
    result = arm['benchmark']
    note = (f"当前normalized main328{'基线445项' if label == 'baseline' else '加两文件P候选446项'}，原bc51/SERVER/16K128/32请求/seed721201；"
        f"32成功0失败、{result['duration']:.9f}s、{result['total_token_throughput']:.9f} total tok/s；"
        f"本对照表观吞吐+{percent:.6f}%，但KV容量不同（521840→521936），33项仅same_KV失败、gain=null，不能归因收益；"
        "DB四端565/20919三hash相同，两侧完整源码/清理/同Engine normalization通过，候选Engine21398实际P N17/M2048/outside14。"
        "491/493原件分别逐项核并导入，原包保留；保留候选，固定源码进入独立完整105题验证，不重复短测凑容量。"
        "旧423收益与三题质量不作为新组合成绩。详analysis/compute-order-current-main-pair.json。")
    item = dict.fromkeys(fields, '')
    item.update(run_id=run,local_date='2026-10-23',utc_start=manifest['started_utc'],profile_id='compute_order',
        phase='current_main_'+label+'_context16k',device='Iluvatar BI-V150',
        vllm_commit='3283672b92fa30f93f652b242193999836a95f88',flaggems_commit=manifest['flaggems_revision'],
        input_len='16384',output_len='128',concurrency='64',num_prompts='32',profiler='false',
        status='confounded_kv_capacity_current_main',artifacts='experiments/framework/'+run,conclusion=note)
    new.append(item)
with registry.open('a',encoding='utf-8',newline='') as stream:
    csv.DictWriter(stream,fieldnames=fields,lineterminator='\n').writerows(new)

path = root / 'scripts/build_team_view.py'
text = path.read_text(encoding='utf-8')
lines = text.splitlines()
summary = ('计算行重排以适配Attention路径，采样保持原请求顺序。当前已适配队友normalized main328，仅改runner/helper两文件。'
    '140324→141159两侧32/0、4435.97→4728.30 tok/s，候选实际P命中；KV521840→521936，33项仅容量失配，gain=null，表观约+6.59%不能归因收益。'
    '保留候选，固定446项源码进入独立完整105题验证。旧423的可比单pair+5.124857%、三题实际P质量、结构映射与单行参考分别保留，不能代替新组合结果。')
for i,line in enumerate(lines):
    if line.startswith("    'compute-order': ('计算顺序"):
        lines[i] = "    'compute-order': " + repr(('计算顺序与采样顺序分离', summary, [])) + ','
    elif line.startswith("    'compute-order': ['analysis/"):
        lines[i] = line.replace("['analysis/", "['analysis/compute-order-current-main-pair.json', 'archive/ai/20261022-framework-kv/compute-order-main-profile/README.md', 'analysis/", 1)
text = '\n'.join(lines) + '\n'
anchor = "    if state == 'client_validation_failed_before_requests':\n"
assert text.count(anchor) == 1
text = text.replace(anchor, "    if state == 'confounded_kv_capacity_current_main':\n        return '保留基线与候选；KV容量不同，不计归因收益，组合准确率另验。'\n" + anchor)
path.write_text(text,encoding='utf-8',newline='\n')
print(json.dumps({'added_runs':[r['run_id'] for r in new],'rows':len(rows)+len(new),'gain':None,'descriptive_percent':percent}))
