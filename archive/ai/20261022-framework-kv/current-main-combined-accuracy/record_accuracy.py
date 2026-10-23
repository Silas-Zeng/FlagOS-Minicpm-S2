"""登记已封存的105题结果，不重跑评测或判卷。"""
import csv
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
run='20261023T142019Z-current-main-compute-order'
base=root/'experiments/accuracy'/run
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
review=read(base/'accuracy-review.json');coverage=read(base/'method-coverage.json')
post=read(base/'postflight-full.json');manifest=read(base/'manifest.json')
assert review['validity']=='valid' and review['samples']==review['expected_samples']==105
assert review['accuracy_gate']=='pass' and review['correct']==103
assert coverage['actual_p_observed'] is False and post['source_count']==446
database={phase:read(base/('database-'+phase)/'manifest.json') for phase in ('before','after')}
keys=('table_count','row_count','snapshot_sha256','schema_sha256','logical_content_sha256')
database={phase:{k:d[k] for k in keys} for phase,d in database.items()}
summary=dict(run_id=run,status='完整准确率通过，P分支未覆盖',base_commit='3283672b92fa30f93f652b242193999836a95f88',
    tree='5c77e68caff6aa0c8b6c230adb78a2d4c293cca1',source_count=446,
    change='当前normalized main仅增加计算顺序runner/helper两文件，原输入/采样请求顺序保持',
    test='原35d/6e045/SERVER，Math500 Level3全部105题，未改原采样参数',
    accuracy={k:review[k] for k in ('validity','accuracy_gate','correct','samples','exact_accuracy','threshold')},
    diagnostics=review['diagnostics'],actual_p_observed=False,normalization_selected=bool(coverage['normalization_selected']),
    database=database,database_unchanged=database['before']==database['after'],
    cleanup=dict(exit_code=0,ports_closed=post['ports_closed'],query=post['query'].strip(),
        driver_zombie_inactive=True,server_engine_evaluation_absent=True),
    transfer=dict(archive_bytes=4099545,archive_sha256='fdd9857c00f576e74b73da0e5cb63d06a322f406379577fd7f6f34ecfe29587b',
        sealed_files=728,imported_files=729,all_file_bytes_verified=True),
    evidence=dict(review=f'experiments/accuracy/{run}/accuracy-review.json',coverage=f'experiments/accuracy/{run}/method-coverage.json',
        seal=f'experiments/accuracy/{run}-control/evidence-seal.json'),
    conclusion='103/105（98.0952%）达到原95%门；105成功、无transport/空最终答案，1题达到原输出上限(index83)。完整题集通过，但P分支0命中，不能据此证明该分支准确率。保留候选，使用同一冻结446源码进入官方吞吐。',
    limits=['旧423收益和三题覆盖不继承为本轮结果','140324/141159因KV容量不同gain=null，约+6.59%只记表观变化','本轮仅BI-V150，不代表C500验证'])
output=root/'analysis/compute-order-current-main-accuracy.json'
with output.open('x',encoding='utf-8') as stream:json.dump(summary,stream,ensure_ascii=False,indent=2);stream.write('\n')
registry=root/'experiments/registry.csv'
with registry.open(encoding='utf-8-sig',newline='') as stream:
    reader=csv.DictReader(stream);fields=reader.fieldnames;rows=list(reader)
assert run not in {r['run_id'] for r in rows}
item=dict.fromkeys(fields,'')
item.update(run_id=run,local_date='2026-10-23',utc_start=manifest['started_utc'],profile_id='compute_order',
    phase='current_main_official_math500_level3_accuracy',device='Iluvatar BI-V150',
    vllm_commit=summary['base_commit'],flaggems_commit=manifest['flaggems_revision'],
    input_len='original_math500_level3',output_len='32768',concurrency='8',num_prompts='105',profiler='false',
    status='accuracy_pass_no_P_current_main',artifacts=f'experiments/accuracy/{run}',
    conclusion=summary['conclusion']+' 728原件逐项核、729导入，完整446源码/清理通过；DB前后如实保留，见analysis/compute-order-current-main-accuracy.json。')
with registry.open('a',encoding='utf-8',newline='') as stream:csv.DictWriter(stream,fieldnames=fields,lineterminator='\n').writerow(item)
path=root/'scripts/build_team_view.py';text=path.read_text(encoding='utf-8')
text=text.replace('保留候选，固定446项源码进入独立完整105题验证。','142019组合完整105题103正确（98.0952%）通过，P分支0命中，仅证明原题集通过；固定446源码进入官方4K/16K吞吐，结果待回收。',1)
anchor="    'compute-order': ['analysis/compute-order-current-main-pair.json'"
assert text.count(anchor)==1
text=text.replace(anchor,"    'compute-order': ['analysis/compute-order-current-main-accuracy.json', 'analysis/compute-order-current-main-pair.json'",1)
path.write_text(text,encoding='utf-8',newline='\n')
print(json.dumps(dict(summary=str(output),registry_rows=len(rows)+1,accuracy=summary['accuracy'],database_unchanged=summary['database_unchanged']),ensure_ascii=False))
