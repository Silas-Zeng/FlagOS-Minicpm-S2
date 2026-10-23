"""只读一次QGQA414→既有KV422服务pair；复用有限准入可比项/c0事务门。"""
import argparse
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import runpy
import shlex

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
if os.name == 'nt':
    value = str(ROOT)
    if not value.startswith('\\\\?\\'):
        ROOT = Path('\\\\?\\UNC\\'+value[2:] if value.startswith('\\\\') else '\\\\?\\'+value)
    HERE = ROOT/'tmp/q-gqa-kv-swap'
FINITE = ROOT/'tmp/finite-growth-admission/compare_service_pair.py'
FINITE_SHA = '03e523ce54a1fb965c132564b5aec06d062aac7a822e77eb250249a7593162c6'
PROTOCOL = ROOT/'scripts/review_kv_observed_pair_run.py'
PROTOCOL_SHA = 'c0c80dcf81b2fc0727f06b43d166a61ad042916ee300511243c2aae42cb14c00'
LAUNCHER_SHA = 'f5ea8719d6d3fe50b4695a3024307bd0689763e3614a4c3a20ed3d737fa9f817'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))


def require(value, message):
    if not value:
        raise ValueError(message)


def exact_launch(control, run, manifest, label):
    remote='/workspace/experiments/minicpm-s2'
    source=remote+'/code/'+('q-gqa-service-candidate-20261022T184141Z' if label=='baseline'
                           else 'q-gqa-kv-swap-20261022T213134Z')
    marker='BIV150_Q_FRAGMENT_SERVICE_INSTALLED' if label=='baseline' else 'BIV150_KV_PROTOCOL_INSTALLED'
    expected=['env','-u','BIV150_FINITE_GROWTH_ADMISSION','BIV150_KV_VERIFY_RESTORE=0',
        f'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR={remote}/framework/{run.name}-control/q-hoist-artifacts',
        'python3',remote+'/scripts/run_framework_screen.py',remote+'/framework/'+run.name,
        '--source-dir',source,'--context-long-screen','--seed','721201','--require-log-marker',marker]
    actual=shlex.split((control/'command.txt').read_text(encoding='utf-8'))
    return {'argv':actual,'expected_argv':expected,'matches':actual==expected and manifest['source_dir']==source}


def libraries():
    require(sha(FINITE)==FINITE_SHA and sha(PROTOCOL)==PROTOCOL_SHA, '原已审解析器变化')
    text=FINITE.read_text(encoding='utf-8'); prefix, sep, _=text.partition('\ndef compare(')
    require(sep, '原库提取边界变化')
    ns={'__file__':str(FINITE),'__name__':'readonly_pair_library'}
    exec(compile(prefix,str(FINITE)+':library','exec'),ns)
    ns['ROOT']=ROOT  # Windows旧库路径也必须保留extended绝对前缀。
    ns['exact_launch']=exact_launch
    compare=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name=='compare')
    checks=next(n for n in compare.body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='checks' for t in n.targets))
    removed={'candidate_exact_finite_admission_415','only_init_finite_helper_changed',
             'candidate_actual_finite_defer_same_Engine_as_Q_GQA',
             'both_exact_control_launch_only_finite_ENV_marker_difference'}
    entries=[(k,v) for k,v in zip(checks.value.keys,checks.value.values) if ast.literal_eval(k) not in removed]
    require(len(entries)==20, '原公共可比项数量变化')
    checks.value.keys,checks.value.values=map(list,zip(*entries))
    code=('def common_checks(arms, expected_b, db, load):\n'
        '    a,b=arms["candidate"],arms["baseline"]; am,bm=a["manifest"],b["manifest"]\n'
        '    data={k:v["data"] for k,v in arms.items()}\n'
        '    n,isl,osl,screen=32,16384,1024,"context16k-long"\n'
        +'\n'.join('    '+line for line in ast.unparse(checks).splitlines())+'\n    return checks\n')
    exec(compile(code,str(FINITE)+':common_checks','exec'),ns)
    ptext=PROTOCOL.read_text(encoding='utf-8')
    pfun=next(n for n in ast.parse(ptext).body if isinstance(n,ast.FunctionDef) and n.name=='inspect_protocol')
    pcode=ast.get_source_segment(ptext,pfun)
    needle='save["worker_response"]["copy_calls"] == 42 * source_runs'
    require(pcode.count(needle)==1,'原SAVE计数切口变化')
    pcode=pcode.replace(needle,'save["worker_response"]["copy_calls"] == save["worker_response"]["linear_calls"] + save["worker_response"]["pitched_calls"]')
    pns={'json':json,'require':require};exec(compile(pcode,str(PROTOCOL)+':pitched_save','exec'),pns)
    return ns,pns['inspect_protocol']


def pitched_save(log, geometry):
    events=[json.loads(s.split('BIV150_KV_PROTOCOL ',1)[1]) for s in log.splitlines() if 'BIV150_KV_PROTOCOL {' in s]
    save=next(e for e in events if e['event']=='RPC_ACK' and e['command']['kind']=='SAVE')
    reply=save['worker_response']; ids=save['command']['pages']
    planner=HERE/'biv150_kv_pitched_copy.py'
    require(sha(planner)=='818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd','冻结818e变化')
    plan=runpy.run_path(str(planner))['make_plan'](ids,max(ids)+1)
    linear=pitched=fallbacks=0
    for segment in plan.segments:
        if segment.height>1 and segment.source_step>1:
            if segment.source_step*16384>reply['save_max_pitch_bytes']:
                linear+=segment.height;fallbacks+=1
            else:pitched+=1
        else:linear+=1
    require(reply['save_implementation']=='C_batch_positive_stride_full_R' and reply['save_layers']==42
        and reply['save_runtime_sha256']==sha(planner)
        and reply['save_bridge_sha256']=='9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0'
        and reply['save_submission_completion_ack'] is False
        and reply['save_segments_per_layer']==len(plan.segments) and reply['linear_calls']==42*linear
        and reply['pitched_calls']==42*pitched and reply['fallback_pitched_segments']==42*fallbacks
        and reply['original_c95f_calls']==42*geometry['source_runs'], 'pitched-SAVE动态几何/身份不符')
    require(reply['save_verification_performed'] is False and reply.get('save_verification_bytes',0)==0,
            'VERIFY0不可做SAVE源回读')
    return {k:reply[k] for k in ('linear_calls','pitched_calls','fallback_pitched_segments','save_segments_per_layer','save_current_stream_handle')}


def compare(baseline,candidate):
    lib,inspect_protocol=libraries()
    arms={label:lib['load_arm'](label,name,'context16k-long') for label,name in (('baseline',baseline),('candidate',candidate))}
    expected={}
    for label,name,pin in (('baseline','base-source-sha256.json','bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'),
                           ('candidate','expected-source-sha256.json','82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136')):
        require(sha(HERE/name)==pin,'完整输入/输出map变化');expected[label]=read(HERE/name)
    data={k:v['data'] for k,v in arms.items()};db=[v['db'][s] for v in data.values() for s in ('db-before','db-after')]
    load=[['bash','/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh','<RUN>/context-16k-long',
           'context-16k-long','16384','1024','64','32','721201']]
    checks=lib['common_checks'](arms,expected['baseline'],db,load)
    logs={};source_proofs=[];gpu_ok=[];owned_ok=[];launch_pins=[]
    for label,arm in arms.items():
        run=ROOT/'experiments/framework'/data[label]['run_id'];control=run.with_name(run.name+'-control')
        logs[label]=(run/'server.log').read_text(encoding='utf-8',errors='replace')
        source_proofs.append(read(control/'original-source-evidence/source-sha256.json')==expected[label])
        rows=list(csv.DictReader((run/'gpu.csv').open(encoding='utf-8')))
        gpu_ok.append(bool(rows) and all(x['memory.total'].strip()=='32768 MiB' and 'BI-V150' in x['gpu_name'] for x in rows))
        owned_ok.append(all(x is None or '\nState:\tZ ' in x for x in read(run/'postflight-full.json')['owned_process_status'].values()))
        launch_pins.append(sha(control/'launch.sh')==LAUNCHER_SHA)
    protocol_ok=False;protocol_data=None;protocol_error=None
    try:
        pid=data['candidate']['q_actual_markers'][0]['pid']
        protocol_data=inspect_protocol(logs['candidate'],'full',pid)
        protocol_data['pitched_save']=pitched_save(logs['candidate'],protocol_data)
        protocol_ok=True
    except (ValueError,KeyError,IndexError,StopIteration,TypeError) as error:
        protocol_error=repr(error)
    changed=sorted(k for k in arms['baseline']['source'].keys()|arms['candidate']['source'].keys()
                   if arms['baseline']['source'].get(k)!=arms['candidate']['source'].get(k))
    allowed=sorted(k for k in expected['baseline'].keys()|expected['candidate'].keys() if expected['baseline'].get(k)!=expected['candidate'].get(k))
    checks.update(candidate_exact_swap_422=arms['candidate']['source']==expected['candidate'],
        only_declared_init_and_eight_KV_paths=changed==allowed and len(allowed)==9,
        both_exact_VERIFY0_launch=all(v['launch']['matches'] for v in data.values()) and all(launch_pins),
        both_original_source_evidence=all(source_proofs),both_single_BIV150_32GiB_samples=all(gpu_ok),
        both_original_six_CPU_quota=all(int(x['manifest']['cpu_before']['cpu.cfs_quota_us'])/int(x['manifest']['cpu_before']['cpu.cfs_period_us'])==6 for x in arms.values()),
        both_owned_processes_gone=all(owned_ok),candidate_actual_VERIFY0_full_consumer=protocol_ok,
        baseline_no_KV_protocol='BIV150_KV_PROTOCOL ' not in logs['baseline'],
        neither_finite=all(not v['finite_markers'] for v in data.values()))
    ar,br=data['candidate']['benchmark'],data['baseline']['benchmark'];ok=all(checks.values())
    percent={'total_token_throughput_change':100*(ar['total_token_throughput']/br['total_token_throughput']-1),
        'duration_saved':100*(1-ar['duration']/br['duration']),'mean_ttft_change':100*(ar['mean_ttft_ms']/br['mean_ttft_ms']-1),
        'mean_tpot_change':100*(ar['mean_tpot_ms']/br['mean_tpot_ms']-1)}
    return {'kind':'QGQA414 vs原FULL/pitched-SAVE422一次VERIFY0服务pair','runs':data,'checks':checks,
        'pair_comparable':ok,'gain':percent if ok else None,'descriptive_percent':percent,
        'candidate_protocol':protocol_data,'protocol_error':protocol_error,'declared_source_changes':changed,
        'status':'single_pair_only' if ok else 'confounded_no_performance_conclusion',
        'reader_sha256':sha(Path(__file__)),'reused_readers_sha256':[FINITE_SHA,PROTOCOL_SHA],
        'limits':['单pair不证明稳定收益或新组合accuracy；失配gain=null，不追加重启。',
            'VERIFY1/490原件复用root验收，不重跑旧门/旧原件；本轮VERIFY0必须无回读。',
            'Q/GQA可不同execute首次命中，不证明恢复步全部层路由/graph replay全覆盖。',
            '匹配包/CPUquota/DB/KV不是全部host干扰相同的证明；共享cgroup时间不是Engine独占损失。',
            'root封存已核原seal；此入口复核完整归档源/后态及既有可比项，不再扫seal。']}


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
