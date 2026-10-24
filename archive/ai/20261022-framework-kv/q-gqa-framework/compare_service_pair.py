"""只读Q+GQA完整服务pair；复用async比较结构，不重验root已核seal。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
DRIVER_SHA = 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9'
BENCHMARK = '/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py'
BENCHMARK_SHA = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
MAP_SHA = '443555886596b94372076aa40e1b159f70475bca7f7a1e0fc901a69804566a34'
BASE_RUNNER = 'cc7f834d25ccbe5d839a731b8e9aa8bf7533bea6f2f937c394423b3844842dfe'
CAND_RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
GQA_SHA = '1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a'
Q_SHA = '51fcaf55133124c2e51dfa0385e1939bf908b65f8444ac63f912329f6ca73800'
RUNNER = 'vllm_fl/worker/model_runner.py'
GQA = 'vllm_fl/patches/biv150_gqa_decode.py'
Q = 'vllm_fl/patches/biv150_q_fragment_service.py'
Q_MARK = 'BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED '
G_MARK = 'BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED '
DB_KEYS = ('snapshot_sha256','schema_sha256','logical_content_sha256','table_count','row_count')


def read(path): return json.loads(path.read_text(encoding='utf-8'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def source_map(folder):
    return {p.relative_to(folder).as_posix():sha(p) for p in folder.rglob('*')
            if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(folder).parts)
            and p.suffix not in ('.pyc','.pyo')}


def engine_pid(prefix):
    found = re.search(r'EngineCore[^\s()]* pid=(\d+)',prefix)
    return int(found.group(1)) if found else None


def markers(log, marker):
    result=[]
    for line in log.splitlines():
        if marker in line:
            prefix,payload=line.split(marker,1)
            value=json.loads(payload)
            value['same_engine_log_pid']=engine_pid(prefix)==value.get('pid') and engine_pid(prefix) is not None
            result.append(value)
    return result


def load_arm(label, name, screen):
    run = Path(name)
    if not run.is_absolute(): run = ROOT/'experiments/framework'/name
    control=run.with_name(run.name+'-control')
    manifest=read(run/'manifest.json')
    (run/'finished-at.txt').read_text()
    case='context-16k-long' if screen=='context16k-long' else 'decode-4k'
    files=list((run/case/'results').glob('*.json'))
    if len(files)!=1: raise FileNotFoundError(f'{run.name}: unique complete benchmark missing')
    db={}
    for side in ('db-before','db-after'):
        value=read(control/side/'manifest.json')
        if value.get('status')!='complete': raise FileNotFoundError(f'{run.name}: incomplete {side}')
        db[side]={k:value[k] for k in DB_KEYS}
    log=(run/'server.log').read_text(encoding='utf-8',errors='replace')
    kv={int(x.replace(',','')) for x in re.findall(r'GPU KV cache size: ([\d,]+) tokens',log)}
    if len(kv)!=1: raise ValueError(f'{run.name}: KV size absent/nonunique')
    width=[]
    for line in log.splitlines():
        if 'BIV150_GQA_DECODE_FIRST_WIDTH ' in line:
            prefix,payload=line.split('BIV150_GQA_DECODE_FIRST_WIDTH ',1)
            width.append({'engine_pid':engine_pid(prefix),'raw':payload,
                          'values':{k:int(v) for k,v in re.findall(r'(seqs|builder_segments|segments|target_programs)=(\d+)',payload)}})
    installed=[]
    for line in log.splitlines():
        if 'BIV150_GQA_DECODE_INSTALL ' in line:
            prefix,payload=line.split('BIV150_GQA_DECODE_INSTALL ',1)
            installed.append({'engine_pid':engine_pid(prefix),'value':ast.literal_eval(payload)})
    qm,gm=markers(log,Q_MARK),markers(log,G_MARK)
    def actual(x,key):
        return (x.get('same_engine_log_pid') and x.get('actual_execute') is True
            and x.get('complete_step_return') is True and x.get('num_requests',0)>=2
            and x.get('scheduled_tokens',0)>0 and x.get(key,0)>0
            and x.get('gqa_python_count_excludes_graph_replay') is True)
    actual_ok=not qm and not gm
    if label=='candidate':
        actual_ok=(len(qm)==len(gm)==1 and actual(qm[0],'selected_calls_in_execute')
            and actual(gm[0],'gqa_calls_in_execute') and qm[0]['pid']==gm[0]['pid'])
    post=read(run/'postflight-full.json')
    command=json.loads((run/'load-commands.json').read_text(encoding='utf-8').replace(
        '/workspace/experiments/minicpm-s2/framework/'+run.name,'<RUN>'))
    external={k:v for k,v in manifest['sha256'].items() if not k.startswith(manifest['source_dir'].rstrip('/')+'/')}
    src=read(control/'source-sha256.json')
    driver_ok=sha(run/'screen-driver.py')==DRIVER_SHA
    server=None
    if driver_ok:
        for node in ast.parse((run/'screen-driver.py').read_text(encoding='utf-8')).body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SERVER' for t in node.targets):
                server=ast.literal_eval(node.value)
    data={'run_id':run.name,'exit_code':int((run/'exit-code').read_text()),'benchmark':read(files[0]),
        'kv_tokens':next(iter(kv)),'db':db,'q_actual_markers':qm,'gqa_actual_markers':gm,
        'gqa_first_width_attempts':width,'gqa_install_records':installed,
        'actual_marker_ok':actual_ok,'driver_sha256':sha(run/'screen-driver.py'),
        'source_count':len(src),'full_archived_source_matches_map':source_map(control/'plugin-source')==src,
        'postflight_idle_sources_ok':bool(post['query'].strip()=='68, 0' and all(post['ports_closed'].values())
            and not post['source_failures'] and post['source_count']==len(src)
            and 'No running processes found' in post['ixsmi']),
        'server_matches_original_driver':server is not None and manifest['server_command']==server}
    return {'data':data,'manifest':manifest,'source':src,'load':command,'external':external}


def compare(baseline,candidate,screen):
    arms={label:load_arm(label,name,screen) for label,name in (('baseline',baseline),('candidate',candidate))}
    a,b=arms['candidate'],arms['baseline'];am,bm=a['manifest'],b['manifest']
    reference=read(HERE/'base-source-sha256.json')
    if sha(HERE/'base-source-sha256.json')!=MAP_SHA or len(reference)!=412:
        raise ValueError('fixed complete clean6f map changed')
    expected_b=dict(reference);expected_b.update({RUNNER:BASE_RUNNER,GQA:GQA_SHA})
    expected_a=dict(expected_b);expected_a.update({RUNNER:CAND_RUNNER,Q:Q_SHA})
    data={label:x['data'] for label,x in arms.items()}
    db=[v['db'][side] for v in data.values() for side in ('db-before','db-after')]
    n,isl,osl,case=(32,16384,1024,'context-16k-long') if screen=='context16k-long' else (64,4096,128,'decode-4k')
    load=[['bash','/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh','<RUN>/'+case,case,str(isl),str(osl),'64',str(n),'721201']]
    changed=sorted(k for k in a['source'].keys()|b['source'].keys() if a['source'].get(k)!=b['source'].get(k))
    checks={
        'both_finished_exit0':all(v['exit_code']==0 for v in data.values()),
        'both_expected_success_and_tokens':all(v['benchmark']['completed']==n and v['benchmark']['failed']==0
            and v['benchmark']['total_input_tokens']==n*isl and v['benchmark']['total_output_tokens']==n*osl for v in data.values()),
        'both_original_SERVER':all(v['server_matches_original_driver'] for v in data.values()),
        'same_server_args':am['server_command']==bm['server_command'],
        'same_original_load':a['load']==b['load']==load,
        'same_seed721201':am['seed']==bm['seed']==721201,
        'both_unprofiled_selected_screen':all(not x['manifest']['native_profile'] and not x['manifest']['host_profile']
            and not x['manifest']['smoke_only'] and x['manifest']['smoke_repeats']==1
            and x['manifest']['context_long_screen']==(screen=='context16k-long')
            and x['manifest']['decode_screen']==(screen=='decode4k') and not x['manifest']['context_screen'] for x in arms.values()),
        'same_packages':am['packages']==bm['packages'],
        'same_cpu_quota_period':all(am['cpu_before'].get(k)==bm['cpu_before'].get(k) and am['cpu_before'].get(k) is not None for k in ('cpu.cfs_quota_us','cpu.cfs_period_us')),
        'same_KV':data['candidate']['kv_tokens']==data['baseline']['kv_tokens'],
        'same_DB_four_endpoints':all(x==db[0] for x in db),
        'baseline_exact_PR12_413':b['source']==expected_b,
        'candidate_exact_Q_GQA_414':a['source']==expected_a,
        'only_runner_Q_helper_changed':changed==sorted((RUNNER,Q)),
        'both_all_archived_bytes_match':all(v['full_archived_source_matches_map'] for v in data.values()),
        'same_installed_external_source_hashes':a['external']==b['external'],
        'both_original_benchmark_manifest_hash':all(x['manifest']['sha256'].get(BENCHMARK)==BENCHMARK_SHA for x in arms.values()),
        'both_original_driver_hash':all(v['driver_sha256']==DRIVER_SHA for v in data.values()),
        'both_GQA_install_and_engine_width_attempt':all(any(z['engine_pid'] is not None and z['value'].get('installed') is True for z in v['gqa_install_records']) and any(z['engine_pid'] is not None and z['values'].get('segments',0)>0 for z in v['gqa_first_width_attempts']) for v in data.values()),
        'candidate_Q_GQA_actual_separate_successful_execute':all(v['actual_marker_ok'] for v in data.values()),
        'both_postflight_idle_sources_ok':all(v['postflight_idle_sources_ok'] for v in data.values()),
    }
    ar,br=data['candidate']['benchmark'],data['baseline']['benchmark'];ok=all(checks.values())
    percentages={'total_token_throughput_change':100*(ar['total_token_throughput']/br['total_token_throughput']-1),
        'duration_saved':100*(1-ar['duration']/br['duration']),
        'mean_ttft_change':100*(ar['mean_ttft_ms']/br['mean_ttft_ms']-1),
        'mean_tpot_change':100*(ar['mean_tpot_ms']/br['mean_tpot_ms']-1)}
    return {'kind':'GQA baseline→GQA+Q one service pair','screen':screen,'runs':data,'checks':checks,
        'pair_comparable':ok,'status':'single_pair_only' if ok else 'confounded_no_performance_conclusion',
        'declared_source_changes':changed,'descriptive_percent':percentages,
        'single_pair_percent_if_comparable':percentages if ok else None,
        'limits':['Single pair only; no stable statistics or combination accuracy claim.',
            'Candidate Q/GQA markers require separate successful actual execute deltas; not full coverage or GPU completion ACK.',
            'GQA baseline has exact unmodified PR12 runner: FIRST_WIDTH is attempt/startup evidence, not per-execute or whole-window coverage.',
            'CUDA graph replay does not increment Python route counters; missing delta means unobserved.',
            'Seal validity reuses root full raw verification; this script verifies full archived source bytes and postflight report.',
            'Original load argv and benchmark manifest SHA are checked; load shell bytes are not separately archived by bc51.',
            'Matching args/packages/CPU quota/DB/KV is necessary, not proof of identical concurrent host work.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run',required=True)
    parser.add_argument('--candidate-run',required=True)
    parser.add_argument('--screen',choices=('context16k-long','decode4k'),default='context16k-long')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('do not overwrite an earlier review')
    try:result=compare(args.baseline_run,args.candidate_run,args.screen)
    except FileNotFoundError as error:
        print(json.dumps({'status':'pending_raw','reason':str(error),'output_written':False},ensure_ascii=False));return 2
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'pair_comparable':result['pair_comparable'],'checks':result['checks'],'descriptive_percent':result['descriptive_percent']},ensure_ascii=False))
    return 0 if result['pair_comparable'] else 1

if __name__=='__main__':raise SystemExit(main())
