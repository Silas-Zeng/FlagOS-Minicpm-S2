"""PR24 新二进制移植检查和一次16K短测；复用已验证源码，不作收益声明。"""
import argparse, ast, datetime, fcntl, hashlib, importlib.metadata, json, os
from pathlib import Path
import re, shutil, socket, subprocess, sys, traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
PIN = '1ad9a708ee77323372f0fa5975a04a52d294852c'
SCRIPTS = {'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
           'run_diagnostic_load.sh': '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378',
           'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
           'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(path, value): Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n')
def idle():
    for family, host in [(socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')]:
        with socket.socket(family) as sock:
            sock.settimeout(1)
            if sock.connect_ex((host,9031)) == 0: raise RuntimeError('9031 busy: '+host)
    query = subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip()
    full = subprocess.check_output(['ixsmi'],text=True)
    if query != '68, 0' or 'No running processes found' not in full: raise RuntimeError('GPU busy: '+query)
    return query

def verify(source, manifest):
    actual = {}
    for p in sorted(source.rglob('*')):
        rel = p.relative_to(source)
        if '__pycache__' in rel.parts or p.suffix in ('.pyc','.pyo'): continue
        if p.is_symlink():
            if not p.resolve().is_relative_to(source): raise RuntimeError('symlink outside source')
            data, mode = os.readlink(p).encode(), '120000'
        elif p.is_file(): data, mode = p.read_bytes(), '100755' if p.stat().st_mode & 0o111 else '100644'
        else: continue
        actual[rel.as_posix()] = dict(sha256=hashlib.sha256(data).hexdigest(),git_sha=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),mode=mode)
    if actual != manifest['files']: raise RuntimeError('source closure mismatch')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--control',type=Path,required=True)
    ap.add_argument('--manifest',type=Path,required=True);args=ap.parse_args()
    source, control = args.source.resolve(), args.control.resolve()
    if not source.is_relative_to(ROOT/'code') or not control.is_relative_to(ROOT/'framework'): raise RuntimeError('outside workspace')
    manifest=json.loads(args.manifest.read_text()); assert manifest['commit']==PIN
    verify(source,manifest)
    control.mkdir(exist_ok=False)
    shutil.copy2(args.manifest,control/'source-manifest.json');shutil.copy2(__file__,control/'run_baseline.py')
    state=dict(owner_pid=os.getpid(),started_utc=utc(),source=str(source),commit=PIN,tree=manifest['tree'],source_count=manifest['source_count'])
    save(control/'state.json',state)
    lock=(ROOT/'framework-device.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    idle()
    for name,pin in SCRIPTS.items():
        if sha(ROOT/'scripts'/name)!=pin: raise RuntimeError('driver changed: '+name)
        shutil.copy2(ROOT/'scripts'/name,control/name)
    backup=control/'database-original.sqlite';shutil.copy2(DB,backup)
    original=sha(backup)
    env={k:v for k,v in os.environ.items() if not k.startswith(('BIV150_','VLLM_FL_BIV150_','MINICPM_NATIVE_','MINICPM_DECODE_GAP_'))}
    env.update(PYTHONPATH=str(source),PYTHONUNBUFFERED='1',MAX_JOBS='2',TORCH_CUDA_ARCH_LIST='7.1')
    build=control/'native';library=build/'biv150_native_w8a8.so'
    run=control.with_name(control.name.removesuffix('-control'))
    commands=[]
    def stage(name, command):
        commands.append(dict(stage=name,command=command));save(control/'commands.json',commands)
        with (control/(name+'.log')).open('x') as log:
            child=subprocess.Popen(command,cwd=source,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage=name,pid=child.pid,stage_started_utc=utc());save(control/'state.json',state)
            code=child.wait()
        state.update(stage_exit_code=code);save(control/'state.json',state)
        if code: raise RuntimeError(name+' failed: '+str(code))
    success=False
    try:
        stage('build',[sys.executable,str(source/'tools/build_biv150_native_w8a8.py'),'--build-dir',str(build)])
        import torch, triton
        compiler=shutil.which('nvcc') or shutil.which('clang++') or shutil.which('c++')
        compiler_result=subprocess.run([compiler,'--version'],capture_output=True,text=True) if compiler else None
        receipt=dict(source=str(source),source_commit=PIN,source_tree=manifest['tree'],library=str(library),library_sha256=sha(library),
                     source_sha256={name:manifest['files'][name]['sha256'] for name in ['csrc/iluvatar/native_w8a8.cpp','csrc/iluvatar/native_w8a8.cu','tools/build_biv150_native_w8a8.py']},
                     build_command=commands[-1]['command'],build_log=str(control/'build.log'),build_log_sha256=sha(control/'build.log'),
                     exit_code=0,python=sys.version,packages={**{name:importlib.metadata.version(name) for name in ['torch','vllm','flag-gems']},'triton':triton.__version__},
                     abi=dict(torch_version=torch.__version__,cxx11_abi=torch._C._GLIBCXX_USE_CXX11_ABI),
                     compiler=dict(command=[compiler,'--version'],exit_code=compiler_result.returncode,stdout=compiler_result.stdout,stderr=compiler_result.stderr) if compiler_result else None,
                     build_ninja=str(build/'build.ninja'),build_ninja_sha256=sha(build/'build.ninja'),
                     environment={k:env[k] for k in ['PYTHONPATH','MAX_JOBS','TORCH_CUDA_ARCH_LIST']})
        save(control/'native-build-manifest.json',receipt)
        env['BIV150_NATIVE_W8A8_LIBRARY']=str(library)
        idle()
        stage('operator-check',[sys.executable,str(source/'tools/check_biv150_gate_auto.py'),'--library',str(library),'--out',str(control/'operator-check.json')])
        numerical=json.loads((control/'operator-check.json').read_text())
        if len(numerical['records']) !=9 or not all(r['passed'] for r in numerical['records']) or not numerical['original_weight_fallback_unchanged']: raise RuntimeError('native checks incomplete')
        idle();verify(source,manifest)
        fcntl.flock(lock,fcntl.LOCK_UN)
        stage('screen',[sys.executable,str(ROOT/'scripts/run_framework_screen.py'),str(run),'--source-dir',str(source),'--context-screen','--seed','721201','--require-log-marker','BIV150_NATIVE_W8A8_INSTALL'])
        log=(run/'server.log').read_text(errors='replace')
        states=[ast.literal_eval(line.split('BIV150_NATIVE_W8A8_INSTALL ',1)[1]) for line in log.splitlines() if 'BIV150_NATIVE_W8A8_INSTALL ' in line]
        native=states[-1] if states else {}
        markers={name:name in log for name in ['BIV150_NATIVE_W8A8_FIRST_WEIGHT','BIV150_COMPUTE_ORDER_FIRST_SELECTED','BIV150_Q_FRAGMENT_SELECTED','BIV150_Q_FRAGMENT_FALLBACK','BIV150_COMPUTE_ORDER_SCOPE_REJECTED']}
        after_ready=log.rsplit('Application startup complete.',1)[1] if 'Application startup complete.' in log else ''
        selected=[json.loads(line.split('BIV150_COMPUTE_ORDER_FIRST_SELECTED ',1)[1]) for line in after_ready.splitlines() if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' in line]
        p_actual=any(item.get('original_model_forward_returned') is True and item.get('runtime_mode')=='NONE' and item.get('outside',0)>0 and item.get('inverse_logits_order')=='original_request_rows' and item.get('sampler_rows')==item.get('N') for item in selected)
        results=list((run/'context-16k/results').glob('*.json'));assert len(results)==1
        result=json.loads(results[0].read_text());kv=re.search(r'GPU KV cache size: ([0-9,]+) tokens',log)
        coverage=bool(native.get('installed') is True and native.get('compressed_only') is True and native.get('gate_operator')=='gate_silu_auto'
                      and markers['BIV150_NATIVE_W8A8_FIRST_WEIGHT'] and p_actual and markers['BIV150_Q_FRAGMENT_SELECTED']
                      and not markers['BIV150_Q_FRAGMENT_FALLBACK'] and not markers['BIV150_COMPUTE_ORDER_SCOPE_REJECTED'])
        save(control/'summary.json',dict(kind='PR24移植短验，非官方成绩或单项收益',coverage=coverage,native_install=native,markers=markers,p_after_ready=selected,
             kv_tokens=int(kv.group(1).replace(',','')) if kv else None,result={k:result.get(k) for k in ['completed','failed','total_token_throughput','mean_ttft_ms','mean_tpot_ms']},
             source_commit=PIN,source_tree=manifest['tree'],library_sha256=sha(library),database_before_sha256=original,
             limits=['native数值检查与压缩权重挂载已验证；未单独采集服务逐请求GPU trace','该短测不重做或替代队友的105题准确率验证']))
        if result.get('completed')!=32 or result.get('failed')!=0: raise RuntimeError('requests incomplete')
        if not coverage: raise RuntimeError('coverage incomplete; inspect before any wider test')
        success=True
    except BaseException as error:
        state['error']=repr(error);(control/'failure.txt').write_text(traceback.format_exc());raise
    finally:
        cleanup_ok=True
        try:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            state['gpu_final']=idle()
            shutil.copy2(DB,control/'database-after.sqlite');shutil.copy2(backup,DB)
            state['database_restored']=sha(DB)==original
            if not state['database_restored']: raise RuntimeError('database restore verification failed')
        except Exception as error:
            cleanup_ok=False;state['cleanup_error']=repr(error);state['database_backup']=str(backup)
        try: verify(source,manifest);state['source_unchanged']=True
        except Exception as error: cleanup_ok=False;state['source_error']=repr(error)
        state.update(completed=success and cleanup_ok,finished_utc=utc())
        save(control/'state.json',state)
        (control/'exit-code').write_text('0\n' if success and cleanup_ok else '1\n')
        lock.close()
        if not cleanup_ok: raise RuntimeError('cleanup incomplete; see state.json and preserved database backup')

if __name__=='__main__': main()
