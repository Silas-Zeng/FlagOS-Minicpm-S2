"""当前normalized main 445→仅P两路径446；复用原短pair可比门，不重跑原门。"""
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

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'experiments/registry.csv').is_file() and (p/'AGENTS.md').is_file())
if os.name=='nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT=Path('\\\\?\\UNC\\'+str(ROOT)[2:] if str(ROOT).startswith('\\\\') else '\\\\?\\'+str(ROOT))
HERE=ROOT/'tmp/current-main-baseline'
PROFILE=ROOT/'tmp/compute-order-main-profile'
BASE='20261023T140324Z-current-main-baseline-context16k'
CANDIDATE='20261023T141159Z-current-main-compute-order-context16k'
BASE_TREE='a6e53d5219addc76700718880f86c33ab014b311'
TARGET_TREE='5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
COMMIT='3283672b92fa30f93f652b242193999836a95f88'
RUNNER='vllm_fl/worker/model_runner.py'
HELPER='vllm_fl/patches/biv150_compute_order.py'
LINK='vllm_fl/configs/moe/E=256,N=512,device_name=nvidia.json'
LINKNAME='E=256,N=512,device_name=nvidia,model=Qwen3.6-35B-A3B-H100.json'
LAUNCHERS={'baseline':('launch_current_main_baseline.py','571a9690fb01c0b0efca0f28c0dc5dc71d90fe0de4323bd066ba479c38837802'),
           'candidate':('launch_compute_order_main.py','88b35410fc49d1d259ebad0cc910c623a5cea2723220707932e38544f3c89e02')}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))


def exact_launch(control,run,manifest,label):
    remote='/workspace/experiments/minicpm-s2'
    expected_run=BASE if label=='baseline' else CANDIDATE
    stamp=expected_run.split('-')[0]
    tag='baseline' if label=='baseline' else 'compute-order'
    source=f'{remote}/code/current-main-{tag}-3283672b-{stamp}'
    expected=['python3',remote+'/scripts/run_framework_screen.py',remote+'/framework/'+expected_run,
        '--source-dir',source,'--context-screen','--seed','721201',
        '--require-log-marker','BIV150_PREFILL_NORMALIZATION_INSTALL']
    actual=shlex.split((control/'command.txt').read_text(encoding='utf-8'))
    return dict(argv=actual,expected_argv=expected,matches=run.name==expected_run and actual==expected and manifest['source_dir']==source)


def library():
    # 原retest已审context-screen适配与8c0→03e公共20项，仅读函数定义。
    path=ROOT/'archive/ai/20261022-framework-kv/compute-order-retest/compare_service_pair.py'
    if sha(path)!='7a891612ee6492d7669a83f0d6dc3b6d2ac38b7589b26d796726c7ab4db895cc':
        raise ValueError('原retest reader变化')
    old=runpy.run_path(str(path))
    lib=old['library']()
    lib['ROOT'],lib['exact_launch']=ROOT,exact_launch
    return lib


def expected_sources():
    if sha(HERE/'launch_current_main_baseline.py')!=LAUNCHERS['baseline'][1]:
        raise ValueError('固定完整main工具变化')
    namespace=runpy.run_path(str(HERE/'launch_current_main_baseline.py'))
    base=namespace['expected_tree']()
    path=PROFILE/'candidate-manifest.json'
    if sha(path)!='0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4':
        raise ValueError('固定两路径manifest变化')
    candidate=read(path);target={k:dict(v) for k,v in base.items()}
    if set(candidate['changed_paths'])!={RUNNER,HELPER}:
        raise ValueError('不是声明两路径')
    for name,entry in candidate['changed_paths'].items():
        if target.get(name)!=entry['before']:raise ValueError('原main before blob不符')
        target[name]=entry['after']
    if (len(base)!=445 or len(target)!=446 or namespace['tree_oid'](base)!=BASE_TREE
            or namespace['tree_oid'](target)!=TARGET_TREE):
        raise ValueError('完整445/446 Git tree不符')
    return base,target,candidate


def archived_git(control,expected):
    recorded=read(control/'source-git-blobs.json')
    errors=[];flat={}
    for name,entry in expected.items():
        data=(control/'plugin-source'/name).read_bytes()
        flat[name]=hashlib.sha256(data).hexdigest()
        if entry['mode']=='120000':
            if name!=LINK or entry['sha']!='e0f0558233316d08efb00d75dce9ff2fd1a1f530':
                errors.append(name+':unknown_symlink')
            if data!=(control/'plugin-source'/Path(LINK).parent/LINKNAME).read_bytes():
                errors.append(name+':materialized_target_mismatch')
        else:
            oid=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            if oid!=entry['sha']:errors.append(name+':blob_mismatch')
    return dict(matches=recorded==expected and not errors,errors=errors,flat=flat)


def normalization(log,lib):
    installed=[];selected=[]
    for line in log.splitlines():
        for marker,destination in (('BIV150_PREFILL_NORMALIZATION_INSTALL ',installed),
                                   ('BIV150_PREFILL_NORMALIZATION_SELECTED ',selected)):
            if marker in line:
                prefix,payload=line.split(marker,1)
                destination.append(dict(pid=lib['engine_pid'](prefix),value=ast.literal_eval(payload)))
    pids={x['pid'] for x in installed if x['pid'] is not None and x['value'].get('installed') is True}
    good=[x for x in selected if x['pid'] in pids and isinstance(x['value'],tuple)
        and len(x['value'])==3 and all(type(v) is int and v>0 for v in x['value'])]
    return dict(installed=installed,selected=selected,pid=next(iter(pids)) if len(pids)==1 else None,
        matches=len(pids)==1 and bool(good))


def compare(baseline,candidate):
    if baseline!=BASE or candidate!=CANDIDATE:raise ValueError('只比较声明的140324/141159')
    lib=library();bgit,agit,frozen=expected_sources()
    arms={label:lib['load_arm'](label,name,'context16k') for label,name in (('baseline',baseline),('candidate',candidate))}
    data={k:v['data'] for k,v in arms.items()}
    controls={k:ROOT/'experiments/framework'/(v['run_id']+'-control') for k,v in data.items()}
    git_proof={k:archived_git(controls[k],expected) for k,expected in (('baseline',bgit),('candidate',agit))}
    expected_b=git_proof['baseline']['flat']
    expected_a=dict(expected_b)
    expected_a.update({name:entry['sha256'] for name,entry in frozen['changed_paths'].items()})
    db=[v['db'][side] for v in data.values() for side in ('db-before','db-after')]
    load=[['bash','/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh','<RUN>/context-16k',
        'context-16k','16384','128','64','32','721201']]
    checks=lib['common_checks'](arms,expected_b,db,load)
    checks['baseline_exact_current_main_445']=checks.pop('baseline_exact_current_QGQA_414')
    # 当前main无实验Q observer；替换这一专属项，保留其余19项表达式。
    checks.pop('both_Q_GQA_actual_separate_successful_execute')
    extras={};logs={}
    for label,arm in arms.items():
        control=controls[label];run=control.with_name(data[label]['run_id'])
        log=(run/'server.log').read_text(encoding='utf-8',errors='replace');logs[label]=log
        norm=normalization(log,lib)
        gpu=list(csv.DictReader((run/'gpu.csv').open(encoding='utf-8')))
        post=read(run/'postflight-full.json');tool,pin=LAUNCHERS[label]
        purpose=read(control/'purpose.json')
        extras[label]=dict(normalization=norm,
            frozen_launcher=sha(control/tool)==pin,
            main_tree_copy=sha(control/'main-tree.json')=='0f054156787c216c94f24062cf2ef865369a982ff32ff76a9638fa3bfb70e222',
            purpose_matches=purpose['commit']==COMMIT and purpose['tree']==(BASE_TREE if label=='baseline' else TARGET_TREE),
            single_BIV150_32GiB=bool(gpu) and all(row['memory.total'].strip()=='32768 MiB' and 'BI-V150' in row['gpu_name'] for row in gpu),
            owned_gone=all(value is None or '\nState:\tZ ' in value for value in post['owned_process_status'].values()),
            gqa_same_engine=any(z['engine_pid']==norm['pid'] and z['value'].get('installed') is True for z in data[label]['gqa_install_records'])
                and any(z['engine_pid']==norm['pid'] and z['values'].get('segments',0)>0 for z in data[label]['gqa_first_width_attempts']))
    marker='BIV150_COMPUTE_ORDER_FIRST_SELECTED '
    actual=lib['markers'](logs['candidate'],marker)
    pid=extras['candidate']['normalization']['pid']
    observed=[v for v in actual if v.get('same_engine_log_pid') and v.get('pid')==pid
        and all(type(v.get(k)) is int for k in ('N','M','Dall','Dprefix','outside','sampler_rows'))
        and 0<v['Dprefix']<v['Dall']<v['N']<v['M'] and v['outside']==v['Dall']-v['Dprefix']
        and v['sampler_rows']==v['N'] and v.get('original_model_forward_returned') is True
        and v.get('runtime_mode')=='NONE' and v.get('inverse_logits_order')=='original_request_rows'
        and v.get('token_bitwise_equivalence_claimed') is False]
    changed=sorted(k for k in arms['baseline']['source'].keys()|arms['candidate']['source'].keys()
        if arms['baseline']['source'].get(k)!=arms['candidate']['source'].get(k))
    checks.update(both_normalization_installed_and_selected_same_Engine=all(v['normalization']['matches'] for v in extras.values()),
        both_GQA_and_normalization_same_Engine=all(v['gqa_same_engine'] for v in extras.values()),
        candidate_exact_main_plus_P_446=arms['candidate']['source']==expected_a and len(expected_a)==446,
        only_runner_and_compute_helper_changed=changed==sorted((RUNNER,HELPER)) and len(expected_b)==445,
        both_complete_frozen_Git_trees=all(v['matches'] for v in git_proof.values()),
        both_original_launch=all(v['launch']['matches'] for v in data.values()),
        both_frozen_launchers=all(v['frozen_launcher'] and v['main_tree_copy'] and v['purpose_matches'] for v in extras.values()),
        candidate_manifest_frozen=sha(controls['candidate']/'candidate-manifest.json')=='0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4',
        both_single_BIV150_32GiB=all(v['single_BIV150_32GiB'] for v in extras.values()),
        both_owned_gone=all(v['owned_gone'] for v in extras.values()),
        both_six_CPU=all(int(v['manifest']['cpu_before']['cpu.cfs_quota_us'])/int(v['manifest']['cpu_before']['cpu.cfs_period_us'])==6 for v in arms.values()),
        candidate_actual_P_same_Engine=len(actual)==len(observed)==1 and marker not in logs['baseline'],
        neither_P_scope_rejected=all('BIV150_COMPUTE_ORDER_SCOPE_REJECTED ' not in value for value in logs.values()),
        neither_finite=all(not v['finite_markers'] for v in data.values()))
    ar,br=data['candidate']['benchmark'],data['baseline']['benchmark']
    percent=dict(total_token_throughput_change=100*(ar['total_token_throughput']/br['total_token_throughput']-1),
        duration_saved=100*(1-ar['duration']/br['duration']),mean_ttft_change=100*(ar['mean_ttft_ms']/br['mean_ttft_ms']-1),
        mean_tpot_change=100*(ar['mean_tpot_ms']/br['mean_tpot_ms']-1))
    ok=all(checks.values())
    return dict(kind='normalized main445→P两路径446原context16k128单pair',runs=data,checks=checks,
        new_evidence=extras,Git_source_proof={k:{x:y for x,y in v.items() if x!='flat'} for k,v in git_proof.items()},
        pair_comparable=ok,status='single_pair_only' if ok else 'confounded_no_performance_conclusion',
        gain=percent if ok else None,descriptive_percent=percent,actual_markers=actual,declared_source_changes=changed,
        reader_sha256=sha(Path(__file__)),limits=['仅单pair，不证明稳定收益；任一可比项失败gain=null，不重启凑KV/DB。',
            '当前normalized main不继承旧423收益或其3题辅助质量；新组合准确率另验。',
            'FIRST_SELECTED仅原forward返回及原采样行逆映射声明，不等采样/GPU完成或全程覆盖。',
            '复用root已验seal/唯一symlink导入，不重跑方法门；十九项原公共门保留，实验Q observer专属项改当前normalization证据。'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run',default=BASE);parser.add_argument('--candidate-run',default=CANDIDATE)
    parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise FileExistsError('不覆盖已有pair结果')
    try:result=compare(args.baseline_run,args.candidate_run)
    except FileNotFoundError as error:
        print(json.dumps(dict(status='pending_raw',reason=str(error),output_written=False),ensure_ascii=False));raise SystemExit(2)
    with args.output.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({k:result[k] for k in ('status','checks','gain')},ensure_ascii=False))
    raise SystemExit(0 if result['pair_comparable'] else 1)
