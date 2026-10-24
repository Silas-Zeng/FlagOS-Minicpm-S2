"""allocator 无状态快返的原 decode4k 单配对；复用已验公共门。"""
import argparse, csv, hashlib, json, os, re, runpy, shlex
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\'+str(ROOT))
HERE=ROOT/'tmp/next-kv-noop-allocate'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))

def exact_launch(control,run,manifest,label):
    remote='/workspace/experiments/minicpm-s2'
    match=re.fullmatch(r'(\d{8}T\d{6}Z)-allocator-noop-'+label+'-decode4k',run.name)
    if not match:return {'matches':False,'reason':'非声明的UTC/run ID'}
    source=(remote+'/code/q-gqa-kv-swap-20261022T213134Z' if label=='baseline'
            else remote+'/code/allocator-noop-candidate-'+match.group(1))
    expected=['env','-u','BIV150_FINITE_GROWTH_ADMISSION','BIV150_KV_VERIFY_RESTORE=0',
        f'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR={remote}/framework/{run.name}-control/q-hoist-artifacts',
        'python3',remote+'/scripts/run_framework_screen.py',remote+'/framework/'+run.name,
        '--source-dir',source,'--decode-screen','--seed','721201',
        '--require-log-marker','BIV150_KV_PROTOCOL_INSTALLED']
    actual=shlex.split((control/'command.txt').read_text(encoding='utf-8'))
    return {'argv':actual,'expected_argv':expected,'matches':actual==expected and manifest['source_dir']==source}

def compare(baseline,candidate,pins):
    shared=ROOT/'tmp/skip-computed-h2d-service/compare_service_pair.py'
    assert sha(shared)=='8c0fc7925947dd2b46db24abff1f3fe94dffeff66dd5dfa42989d223a8130efa'
    previous=runpy.run_path(str(shared));previous['library'].__globals__['exact_launch']=exact_launch
    lib=previous['library']()
    arms={label:lib['load_arm'](label,name,'decode4k') for label,name in (('baseline',baseline),('candidate',candidate))}
    baseline_map=ROOT/'tmp/allocator-noop-baseline/expected-source-sha256.json'
    assert sha(baseline_map)=='82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
    expected_b=read(baseline_map); expected_file=HERE/'expected-source-sha256.json'
    assert sha(expected_file)==pins['candidate_map_sha256']
    expected_a=read(expected_file)
    data={k:v['data'] for k,v in arms.items()};db=[v['db'][s] for v in data.values() for s in ('db-before','db-after')]
    load=[['bash','/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh','<RUN>/decode-4k',
           'decode-4k','4096','128','64','64','721201']]
    checks=lib['common_checks'](arms,expected_b,db,load)
    checks['baseline_exact_422']=checks.pop('baseline_exact_current_QGQA_414')
    logs={}; extras={}
    for label,arm in arms.items():
        run=ROOT/'experiments/framework'/data[label]['run_id'];control=run.with_name(run.name+'-control')
        logs[label]=(run/'server.log').read_text(encoding='utf-8',errors='replace')
        gpu=list(csv.DictReader((run/'gpu.csv').open(encoding='utf-8')))
        post=read(run/'postflight-full.json')
        extras[label]={'frozen_launcher':sha(control/'launch.sh')==pins[label+'_launcher_sha256'],
            'single_BIV150_32GiB':bool(gpu) and all(x['memory.total'].strip()=='32768 MiB' and 'BI-V150' in x['gpu_name'] for x in gpu),
            'owned_gone':all(v is None or '\nState:\tZ ' in v for v in post['owned_process_status'].values())}
    marker=pins['actual_marker']+' '
    actual=[json.loads(line.split(marker,1)[1]) for line in logs['candidate'].splitlines() if marker in line]
    pid=data['candidate']['q_actual_markers'][0]['pid']
    # 字段与最终生产marker冻结；准备期无pins文件，不能提前运行结论。
    observed=[v for v in actual if v.get('pid')==pid and all(v.get(k)==value for k,value in pins['required_actual_fields'].items())
              and type(v.get('selected_in_core_step')) is int and v['selected_in_core_step']>0
              and type(v.get('running')) is int and v['running']>=2
              and v.get('selected_total',0)>=v['selected_in_core_step']]
    armed_marker='BIV150_ALLOCATOR_NOOP_ARMED '
    armed=[json.loads(line.split(armed_marker,1)[1]) for line in logs['candidate'].splitlines() if armed_marker in line]
    armed=[v for v in armed if v.get('pid')==pid and v.get('source_scope')=='fixed422' and v.get('no_device_calls') is True]
    control=ROOT/'experiments/framework'/(candidate+'-control')
    cpu_proof=(sha(control/'cpu-check.json')==pins['cpu_check_sha256']
               and read(control/'cpu-check.json')['cpu_fragment_go'] is True
               and sha(control/'prepare_source.py')==pins['preparer_sha256']
               and sha(control/'cpu-tested-core.py')==pins['cpu_core_sha256']
               and (control/'biv150_noop_allocate.py').read_bytes().startswith((control/'cpu-tested-core.py').read_bytes()))
    changed=sorted(k for k in arms['baseline']['source'].keys()|arms['candidate']['source'].keys()
                   if arms['baseline']['source'].get(k)!=arms['candidate']['source'].get(k))
    checks.update(candidate_exact_423=arms['candidate']['source']==expected_a and len(expected_a)==423,
        only_init_and_noop_helper=changed==sorted(['vllm_fl/__init__.py','vllm_fl/patches/biv150_noop_allocate.py']),
        both_original_launch=all(v['launch']['matches'] for v in data.values()),
        both_frozen_launchers=all(v['frozen_launcher'] for v in extras.values()),
        both_single_BIV150_32GiB=all(v['single_BIV150_32GiB'] for v in extras.values()),
        both_owned_gone=all(v['owned_gone'] for v in extras.values()),
        both_original_six_CPU=all(int(v['manifest']['cpu_before']['cpu.cfs_quota_us'])/int(v['manifest']['cpu_before']['cpu.cfs_period_us'])==6 for v in arms.values()),
        candidate_actual_noop_same_Engine=len(observed)==1 and marker not in logs['baseline'],
        candidate_exact_scope_armed_same_Engine=len(armed)==1,
        candidate_passed_CPU_core_unchanged=cpu_proof,
        neither_finite=all(not v['finite_markers'] for v in data.values()))
    ar,br=data['candidate']['benchmark'],data['baseline']['benchmark'];ok=all(checks.values())
    percent={'total_token_throughput_change':100*(ar['total_token_throughput']/br['total_token_throughput']-1),
        'duration_saved':100*(1-ar['duration']/br['duration']),
        'mean_ttft_change':100*(ar['mean_ttft_ms']/br['mean_ttft_ms']-1),
        'mean_tpot_change':100*(ar['mean_tpot_ms']/br['mean_tpot_ms']-1)}
    return {'kind':'422→allocator无状态快返423原decode4k单pair','runs':data,'checks':checks,'pair_comparable':ok,
        'status':'single_pair_only' if ok else 'confounded_no_performance_conclusion',
        'gain':percent if ok else None,'descriptive_percent':percent,'actual_markers':actual,
        'declared_source_changes':changed,'reader_sha256':sha(Path(__file__)),'pins':pins,
        'limits':['单pair不证明稳定收益或新accuracy；任一可比项失败gain=null，不重启凑容量。',
                  '此4K短负载不要求SAVE/FULL；原422字节正确性和准确率引用已保存结果，新快返仅CPU边界加本次服务。',
                  '原seal逐文件核由root导入复用；当前重核完整归档源、后态、原公共DB/KV/参数/环境门。',
                  'Q/GQA及allocator标记只证明所见真实命中，不表示全程覆盖或GPU完成。']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run',required=True);parser.add_argument('--candidate-run',required=True)
    parser.add_argument('--pins',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();assert not args.output.exists()
    result=compare(args.baseline_run,args.candidate_run,read(args.pins))
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:result[k] for k in ('status','checks','gain')},ensure_ascii=False))
    raise SystemExit(0 if result['pair_comparable'] else 1)
