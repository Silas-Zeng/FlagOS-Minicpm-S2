"""仅接受075834本站main56/native14f完整16K原官方控制，不等待或替代旧成绩。"""
import csv,hashlib,json,math
from pathlib import Path
from head_activation import kv_tokens
ROOT=Path('/workspace/experiments/minicpm-s2')
HERE=Path(__file__).resolve().parent
RUN='20261027T075834Z-main56-control-16k-four-rounds'
COMMIT='56f1838192abc940b3fb9accef490022ac125000'
TREE='1e9af62de05aad53ee61c814054624de8e252dd0'
SO='14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
DB=Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def require(ok,message):
    if not ok:raise ValueError(message)

def capture(*,root=ROOT,database=DB,manifest_path=None):
    root=Path(root);manifest=read(manifest_path or HERE/'team-source-manifest.json')
    require(manifest['commit']==COMMIT and manifest['tree']==TREE and manifest['source_count']==807,'控制完整807源身份不符')
    hashes={p:v['sha256'] for p,v in manifest['files'].items()}
    run=root/'official'/RUN;control=run.with_name(RUN+'-control')
    require(control.is_dir() and not control.is_symlink(),'075834控制尚未完成，不启动或排队')
    state=read(control/'state.json')
    require(state.get('base_commit')==COMMIT and state.get('tree')==TREE and state.get('source_count')==807
        and Path(state['run'])==run and Path(state['control'])==control
        and read(control/'source-sha256.json')==hashes,'控制不是本次main56完整源码')
    require(all(state.get(k) is True for k in ('completed','database_restored','source_unchanged','native_unchanged'))
        and state.get('driver_exit_code')==0 and not state.get('error') and not state.get('cleanup_error')
        and (control/'exit-code').read_text().strip()=='0','控制尚未完整收尾清理')
    graph=read(control/'model-path-evidence.json')
    require(state.get('model_path')==graph and graph.get('valid') is True
        and graph.get('tree')==TREE and graph.get('source_count')==807
        and graph.get('prefill_activation',{}).get('valid') is True
        and graph.get('provider',{}).get('valid') is True and graph.get('q32',{}).get('valid') is True
        and graph.get('graph',{}).get('native',{}).get('layers')==list(range(4,38)),'控制原优化栈/provider未闭合')
    native=read(control/'native/build-manifest.json')
    require(native.get('library_sha256')==SO and sha(control/'native/biv150_native_w8a8.so')==SO,'控制非本站native14f')
    initial=sha(control/'database-original.sqlite')
    require(initial==state.get('database_before_sha256') and sha(database)==initial,'候选起始DB与本次控制不同')
    result=read(run/'result.json');validation=result.get('validation',{})
    require(state.get('result')==result and result.get('benchmark_completed') is True and result.get('exit_code')==0
        and not result.get('cleanup_errors') and (run/'exit-code').read_text().strip()=='0'
        and validation.get('complete') is True and validation.get('raw_rows')==4 and validation.get('summary_rows')==1
        and validation.get('runs_per_case')==4 and validation.get('skip_first')==1
        and validation.get('summary_means_verified') is True,'控制不是原官方16K四轮')
    files=[control/'state.json',control/'source-sha256.json',control/'model-path-evidence.json',
        control/'native/build-manifest.json',control/'database-original.sqlite',run/'result.json',run/'server.log']
    for relative,digest in validation['sha256'].items():
        path=(run/relative).resolve(strict=True)
        require(path.is_relative_to(run.resolve()) and sha(path)==digest,'控制CSV身份变化');files.append(path)
    raw_files=sorted((run/'benchmark_results').glob('raw_runs_*.csv'))
    require(len(raw_files)==1,'控制raw CSV不唯一');raw=raw_files[0]
    with raw.open(newline='',encoding='utf-8-sig') as stream:rows=list(csv.DictReader(stream))
    require(len(rows)==4 and all(tuple(int(row[k]) for k in ('Prefill','Decode','Conc','Num Prompts'))==(16384,1024,64,128)
        and row['Run Status']=='SUCCESS' and float(row['Successful Requests'])==128
        and float(row['Total Input Tokens'])==16384*128 and float(row['Total Output Tokens'])==1024*128 for row in rows),'控制16K请求/输入输出数不符')
    rates=[float(row['Total tok/s']) for row in rows]
    require(all(math.isfinite(x) and x>0 for x in rates),'控制吞吐非法')
    files.append(raw)
    return dict(run=str(run),control=str(control),commit=COMMIT,tree=TREE,source_count=807,native_sha256=SO,
        rates=rates,first_warm={16384:rates[1]},warm_mean=sum(rates[1:])/3,raw_csv=str(raw),raw_csv_sha256=sha(raw),
        kv_tokens=kv_tokens(run/'server.log'),initial_database_sha256=initial,files={str(p):sha(p) for p in files},
        limitation='仅本站075834 main56/native14f原官方16K；不继承旧main或队友native5cbb成绩、准确率或multi2覆盖率。')
