"""4K原有效前缀＋独立16K控制；原中断run和旧parser回执原样保留。"""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT=Path('/workspace/experiments/minicpm-s2')
HERE=Path(__file__).resolve().parent
RUN4='20261026T154111Z-main594-official-control-four-rounds'
RUN16='20261026T164443Z-main594-control-16k-four-rounds'
COMMIT='594ae2a9d17aadc4587ad54ade2b34e17f4af990'
TREE='5a406f3c5b8d35d4ba9f3d8493270d67a9bd57a7'
SO='14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
READER='c564bf25197a0d26b1f6eac013654f51779782b732e06feadae4bf54d5e23c55'
DB=Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())
def require(ok,message):
    if not ok:raise ValueError(message)

def capture(*,root=ROOT,database=DB,manifest_path=None):
    """两份真实控制均闭合后才准入；不创建队列，不把它们合成单一8轮run。"""
    root=Path(root);manifest=read(manifest_path or HERE/'team-source-manifest.json')
    require(manifest['commit']==COMMIT and manifest['tree']==TREE and manifest['source_count']==690,'控制源码manifest不符')
    hashes={p:v['sha256'] for p,v in manifest['files'].items()}
    cases={};files=[];initials=[]
    for size,name in ((4096,RUN4),(16384,RUN16)):
        run=root/'official'/name;control=run.with_name(name+'-control')
        require(control.is_dir() and not control.is_symlink(),'对应控制尚未就绪，不启动候选')
        state=read(control/'state.json')
        require(state.get('base_commit')==COMMIT and state.get('tree')==TREE and state.get('source_count')==690
            and Path(state['run'])==run and Path(state['control'])==control
            and read(control/'source-sha256.json')==hashes,'控制不是同main594完整690源')
        graph=read(control/'model-path-evidence.json')
        require(graph.get('tree')==TREE and graph.get('source_count')==690
            and graph.get('prefill_activation',{}).get('valid') is True
            and graph.get('graph',{}).get('native',{}).get('layers')==list(range(4,38)),'控制prefill/native实际路径不符')
        native=read(control/'native/build-manifest.json')
        require(native.get('library_sha256')==SO and sha(control/'native/biv150_native_w8a8.so')==SO,'控制不是本站native14f')
        initial=sha(control/'database-original.sqlite');initials.append(initial)
        require(initial==state.get('database_before_sha256'),'控制初始DB原件不符')
        if size==4096:
            recovery=read(control/'interruption-recovery.json')
            supplement_path=control/'posthoc-provider-recovery/result.json';supplement=read(supplement_path)
            require(recovery.get('status')=='interrupted_after_four_4k_rounds_during_first_16k'
                and recovery.get('original_state_preserved') is True and state.get('completed') is False
                and recovery.get('original_state_sha256')==sha(control/'state.json')
                and recovery.get('source_unchanged') is True and recovery.get('native_unchanged') is True
                and recovery.get('database_restored_sha256')==initial
                and all(value is False for value in recovery.get('original_processes',{}).values()),'原4K外部中断恢复回执未闭合')
            require(supplement.get('reader_sha256')==READER
                and supplement.get('original_model_path_sha256')==sha(control/'model-path-evidence.json')
                and supplement.get('source_unchanged') is True and supplement.get('original_run_preserved') is True
                and supplement.get('model_path_valid') is True and supplement.get('provider',{}).get('valid') is True
                and supplement.get('provider',{}).get('generated_out_modules'),'原4K真实provider独立补充未闭合')
            raw=Path(recovery['completed_4k']['csv'])
            require(raw.resolve().is_relative_to((run/'benchmark_results').resolve()),'原4K CSV越界')
            files += [control/'interruption-recovery.json',supplement_path]
            scope='原run最先4K四轮；16K外部中断，原completed=false及旧parser=false保留'
        else:
            require(all(state.get(k) is True for k in ('completed','database_restored','source_unchanged','native_unchanged'))
                and state.get('driver_exit_code')==0 and not state.get('error') and not state.get('cleanup_error')
                and (control/'exit-code').read_text().strip()=='0','独立16K控制尚未完整完成清理')
            require(state.get('model_path')==graph and graph.get('valid') is True
                and graph.get('provider',{}).get('valid') is True,'独立16K实际provider未闭合')
            result=read(run/'result.json');validation=result.get('validation',{})
            require(state.get('result')==result and result.get('benchmark_completed') is True and result.get('exit_code')==0
                and not result.get('cleanup_errors') and (run/'exit-code').read_text().strip()=='0'
                and validation.get('complete') is True and validation.get('raw_rows')==4 and validation.get('summary_rows')==1
                and validation.get('runs_per_case')==4 and validation.get('skip_first')==1
                and validation.get('summary_means_verified') is True,'独立16K不是完整官方单档四轮')
            for relative,digest in validation['sha256'].items():
                path=(run/relative).resolve(strict=True)
                require(path.is_relative_to(run.resolve()) and sha(path)==digest,'独立16K CSV身份变化')
                files.append(path)
            raw_files=sorted((run/'benchmark_results').glob('raw_runs_*.csv'))
            require(len(raw_files)==1,'独立16K raw CSV不唯一');raw=raw_files[0]
            files.append(run/'result.json');scope='独立16K新服务完整四轮；与候选16K新服务对称'
        with raw.open(newline='',encoding='utf-8-sig') as stream:rows=list(csv.DictReader(stream))
        prompts=256 if size==4096 else 128;expected=(size,1024,64,prompts)
        require(len(rows)==4 and all(tuple(int(row[k]) for k in ('Prefill','Decode','Conc','Num Prompts'))==expected
            and row['Run Status']=='SUCCESS' and float(row['Successful Requests'])==prompts
            and float(row['Total Input Tokens'])==size*prompts and float(row['Total Output Tokens'])==1024*prompts for row in rows),'控制单档4轮请求/输入输出数不符')
        rates=[float(row['Total tok/s']) for row in rows]
        require(all(math.isfinite(value) and value>0 for value in rates),'控制吞吐非有效正数')
        if size==4096:
            require(recovery['completed_4k']['rows']==4 and recovery['completed_4k']['successful_requests']==1024
                and recovery['completed_4k']['total_toks']==rates,'4K恢复回执与原四轮CSV不符')
        cases[size]=dict(run=str(run),control=str(control),raw_csv=str(raw),raw_csv_sha256=sha(raw),rates=rates,
            first_warm=rates[1],warm_mean=sum(rates[1:])/3,protocol=scope)
        files += [control/'state.json',control/'source-sha256.json',control/'model-path-evidence.json',control/'native/build-manifest.json',control/'database-original.sqlite',raw]
    require(len(set(initials))==1 and sha(database)==initials[0],'两档控制及当前候选起始DB不一致')
    return dict(cases=cases,first_warm={size:case['first_warm'] for size,case in cases.items()},
        commit=COMMIT,tree=TREE,native_sha256=SO,initial_database_sha256=initials[0],files={str(p):sha(p) for p in files},
        limitation='两次新服务协议的分档对照；未重写原run完成状态，不继承旧main/队友native成绩或准确率')
