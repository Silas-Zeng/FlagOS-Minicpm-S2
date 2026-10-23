"""单computed H2D短服务pair；复用03e公共门，不重跑方法门/原seal。"""
import argparse
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent
if os.name=='nt':
    value=str(ROOT)
    if not value.startswith('\\\\?\\'):
        ROOT=Path('\\\\?\\UNC\\'+value[2:] if value.startswith('\\\\') else '\\\\?\\'+value)
    HERE=ROOT/'tmp/skip-computed-h2d-service'
LEGACY=ROOT/'tmp/finite-growth-admission/compare_service_pair.py'
LEGACY_SHA='03e523ce54a1fb965c132564b5aec06d062aac7a822e77eb250249a7593162c6'
RUNNER='vllm_fl/worker/model_runner.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def require(value,message):
    if not value:raise ValueError(message)


def exact_launch(control,run,manifest,label):
    match=re.fullmatch(r'(\d{8}T\d{6}Z)-skip-computed-h2d-service-'+label+r'-decode4k',run.name)
    if not match:return {'matches':False,'reason':'非固定UTC/variant run ID'}
    root='/workspace/experiments/minicpm-s2'
    source=root+'/code/skip-computed-h2d-service-'+label+'-'+match.group(1)
    expected=['env','-u','BIV150_FINITE_GROWTH_ADMISSION',
        f'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR={root}/framework/{run.name}-control/q-hoist-artifacts',
        'python3',root+'/scripts/run_framework_screen.py',root+'/framework/'+run.name,'--source-dir',source,
        '--decode-screen','--seed','721201','--require-log-marker','BIV150_Q_FRAGMENT_SERVICE_INSTALLED']
    actual=shlex.split((control/'command.txt').read_text(encoding='utf-8'))
    return {'argv':actual,'expected_argv':expected,'matches':actual==expected and manifest['source_dir']==source}


def library():
    require(sha(LEGACY)==LEGACY_SHA,'原03e解析器变化')
    text=LEGACY.read_text(encoding='utf-8');prefix,sep,_=text.partition('\ndef compare(')
    require(sep,'原公共库提取边界变化')
    ns={'__file__':str(LEGACY),'__name__':'readonly_h2d_pair_library'}
    exec(compile(prefix,str(LEGACY)+':library','exec'),ns)
    ns['ROOT']=ROOT;ns['exact_launch']=exact_launch
    node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='compare')
    checks=next(n for n in node.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='checks' for t in n.targets))
    removed={'candidate_exact_finite_admission_415','only_init_finite_helper_changed',
        'candidate_actual_finite_defer_same_Engine_as_Q_GQA','both_exact_control_launch_only_finite_ENV_marker_difference'}
    entries=[(k,v) for k,v in zip(checks.value.keys,checks.value.values) if ast.literal_eval(k) not in removed]
    require(len(entries)==20,'原20公共可比项变化');checks.value.keys,checks.value.values=map(list,zip(*entries))
    code=('def common_checks(arms,expected_b,db,load):\n'
        '    a,b=arms["candidate"],arms["baseline"];am,bm=a["manifest"],b["manifest"]\n'
        '    data={k:v["data"] for k,v in arms.items()}\n'
        '    n,isl,osl,screen=64,4096,128,"decode4k"\n'
        +'\n'.join('    '+x for x in ast.unparse(checks).splitlines())+'\n    return checks\n')
    exec(compile(code,str(LEGACY)+':decode4k_checks','exec'),ns)
    return ns


def compare(baseline,candidate):
    lib=library();arms={label:lib['load_arm'](label,name,'decode4k') for label,name in (('baseline',baseline),('candidate',candidate))}
    expected={}
    for label,name,pin in (('baseline','base-source-sha256.json','bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'),
        ('candidate','expected-source-sha256.json','425245ed4b8a0f086dc1ac99807d137f21f0128aaa1ada45a576c19bd639c0dd')):
        require(sha(HERE/name)==pin,'冻结完整map变化');expected[label]=read(HERE/name)
    data={k:v['data'] for k,v in arms.items()};db=[v['db'][s] for v in data.values() for s in ('db-before','db-after')]
    load=[['bash','/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh','<RUN>/decode-4k',
           'decode-4k','4096','128','64','64','721201']]
    checks=lib['common_checks'](arms,expected['baseline'],db,load)
    extra={};gate_refs=[]
    for label,arm in arms.items():
        run=ROOT/'experiments/framework'/data[label]['run_id'];control=run.with_name(run.name+'-control')
        log=(run/'server.log').read_text(encoding='utf-8',errors='replace')
        pid=(data[label]['q_actual_markers'] or [{}])[0].get('pid')
        marker='BIV150_CPU_METADATA_FIRST_SELECTED '
        metadata=[line for line in log.splitlines() if marker in line
            and lib['engine_pid'](line.split(marker,1)[0])==pid
            and line.split(marker,1)[1].strip()=='positions_seq_h2d=2']
        prep=read(control/'preparation.json');gate=prep['method_gate']
        gate_ok=(gate['passed'] is True and sha(control/'method-gate-results.json')==gate['results_sha256']
            and sha(control/'method-gate-manifest.json')==gate['manifest_sha256']
            and read(control/'method-gate-results.json')['status']=='pass')
        gate_refs.append(gate)
        rows=list(csv.DictReader((run/'gpu.csv').open(encoding='utf-8')))
        post=read(run/'postflight-full.json')
        extra[label]={'metadata_first_selected_lines':metadata,'method_gate_reference':gate,
            'method_gate_receipt_matches_archived_summary':gate_ok,
            'frozen_launcher_preparer':sha(control/'launch.sh')=='c342134afdf2414c0c3931b24dcb8f8a4508a4ebd2dc7fc7ce2bffb738f22251'
                and sha(control/'prepare_service_source.py')=='e174044c38fe21351c23922d1307003a47e876513a8864a03eb5e3be4c96f1f3',
            'GPU_BIV150_32GiB':bool(rows) and all(x['memory.total'].strip()=='32768 MiB' and 'BI-V150' in x['gpu_name'] for x in rows),
            'owned_processes_gone':all(x is None or '\nState:\tZ ' in x for x in post['owned_process_status'].values())}
    changed=sorted(k for k in arms['baseline']['source'].keys()|arms['candidate']['source'].keys()
                   if arms['baseline']['source'].get(k)!=arms['candidate']['source'].get(k))
    checks.update(candidate_exact_single_H2D_414=arms['candidate']['source']==expected['candidate'],
        only_runner_changed_other_413_identical=changed==[RUNNER] and len(arms['baseline']['source'])==len(arms['candidate']['source'])==414,
        both_exact_original_ENV_and_launch=all(v['launch']['matches'] for v in data.values()),
        both_e174_c342_wiring=all(x['frozen_launcher_preparer'] for x in extra.values()),
        both_same_passed_method_gate_reference=gate_refs[0]==gate_refs[1] and all(x['method_gate_receipt_matches_archived_summary'] for x in extra.values()),
        both_actual_metadata_first_selection_same_Engine=all(len(x['metadata_first_selected_lines'])==1 for x in extra.values()),
        both_single_BIV150_32GiB=all(x['GPU_BIV150_32GiB'] for x in extra.values()),
        both_six_CPU_quota=all(int(x['manifest']['cpu_before']['cpu.cfs_quota_us'])/int(x['manifest']['cpu_before']['cpu.cfs_period_us'])==6 for x in arms.values()),
        both_owned_processes_gone=all(x['owned_processes_gone'] for x in extra.values()),
        neither_finite=all(not v['finite_markers'] for v in data.values()))
    ar,br=data['candidate']['benchmark'],data['baseline']['benchmark'];ok=all(checks.values())
    percent={'total_token_throughput_change':100*(ar['total_token_throughput']/br['total_token_throughput']-1),
        'duration_saved':100*(1-ar['duration']/br['duration']),'mean_ttft_change':100*(ar['mean_ttft_ms']/br['mean_ttft_ms']-1),
        'mean_tpot_change':100*(ar['mean_tpot_ms']/br['mean_tpot_ms']-1)}
    return {'kind':'单computed H2D 414→414原decode4K一次pair','runs':data,'new_evidence':extra,'checks':checks,
        'pair_comparable':ok,'gain':percent if ok else None,'descriptive_percent':percent,'declared_source_changes':changed,
        'reader_sha256':sha(Path(__file__)),'reused_reader_sha256':LEGACY_SHA,
        'limits':['单pair不证明稳定收益/新accuracy；失配gain=null，不追加重启。',
            '214819方法门PASS与原seal复用root验收；这里只读本次control附证，不重跑方法门。',
            'metadata原标记仅同Engine首次真实_prepare_inputs选择，不是全程/该execute模型完成或GPU完成。',
            'Q/GQA可不同execute首命中，graph replay不增Python计数；CPUquota/DB/KV匹配不保证所有host干扰相同。',
            '共享cgroup时间非Engine独占损失，Exporter CPU非全部worker CPU；不把描述比率当失配时收益。']}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run',required=True);parser.add_argument('--candidate-run',required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖旧结论')
    try:result=compare(args.baseline_run,args.candidate_run)
    except FileNotFoundError as error:
        print(json.dumps({'status':'pending_raw','reason':str(error),'output_written':False},ensure_ascii=False));raise SystemExit(2)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'pair_comparable':result['pair_comparable'],'gain':result['gain'],'checks':result['checks']},ensure_ascii=False))
    raise SystemExit(0 if result['pair_comparable'] else 1)
