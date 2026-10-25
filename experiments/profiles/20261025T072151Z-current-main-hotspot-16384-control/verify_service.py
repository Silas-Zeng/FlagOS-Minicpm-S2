"""当前main526真实4K或16K少量请求热点诊断；不作为官方性能或准确率。"""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import signal
import subprocess
import traceback

import cache_gate as gate
import graph_gate
import shlex
import sqlite3
import time
import lifecycle as life
import qualification as q

HERE = Path(__file__).resolve().parent
ROOT = q.ROOT
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
IXSYS = Path('/usr/local/corex-4.5.0/bin/ixsys')
IXSYS_SHA = '7b47fa41f8afb2777fcddd1fb68d9f1e9f221b2f3538f70cd9681b216b277932'

def owned_service(parent):
    pending=[parent]
    while pending:
        pid=pending.pop()
        try:
            proc=Path('/proc')/str(pid)
            argv=(proc/'cmdline').read_bytes().split(b'\0')
            if any(Path(x.decode()).name=='vllm' for x in argv[:2]):return pid
            pending.extend(map(int,(proc/f'task/{pid}/children').read_text().split()))
        except (OSError,ValueError):continue
    raise RuntimeError('ixsys子树未找到所属vLLM服务')


def flush_trace(server,service_pid,state):
    # 正常结束先TERM所属vLLM子进程，等待ixsys写完；失败后仍由原finally清组。
    if server.poll() is None:
        if service_pid is None:
            try:service_pid=owned_service(server.pid)
            except Exception as error:state['ixsys_service_discovery_error']=repr(error)
        if service_pid is not None:
            try:os.kill(service_pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:server.wait(timeout=45)
            except subprocess.TimeoutExpired:state['ixsys_flush_timeout']=True
    state['ixsys_exit_code']=server.poll()
    state['ixsys_flushed']=server.poll() is not None and not state.get('ixsys_flush_timeout')


def validate_trace(run):
    events=[__import__('json').loads(line) for line in (run/'hotspot-events.jsonl').read_text().splitlines()]
    stops=[x for x in events if x['event']=='window_stop']
    path=run/'native-trace.sqlite'
    with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as database:
        rows=database.execute('SELECT COUNT(*) FROM cuda_kernel_data').fetchone()[0]
        tables=[x[0] for x in database.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    result=dict(valid=len(stops)==2 and [x['phase'] for x in stops]==['mixed','decode']
        and all(x['valid'] for x in stops) and rows>0,kernel_rows=rows,tables=tables,
        windows=stops,trace_sha256=q.sha(path),full_internal_nodes_verified=False,
        performance_claimed=False,missing_windows_are_not_retried=True)
    gate.save(run/'trace-validation.json',result)
    return result




def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--performance-control', required=True, type=Path)
    parser.add_argument('--input-len',type=int,choices=(4096,16384),required=True)
    args = parser.parse_args()
    q.assets()
    q.require(q.sha(gate.COMMON) == gate.COMMON_SHA and q.sha(gate.MONITOR) == gate.MONITOR_SHA,
              '原common/monitor来源变化')
    common = q.load(gate.COMMON, 'final_ffn_verify_common')
    source = args.source_dir.resolve(strict=True)
    q.require(not args.source_dir.is_symlink() and source.is_relative_to(ROOT / 'code'), 'main526来源必须为已测code目录')
    manifest = q.read(HERE/'source-manifest.json')
    q.require(q.sha(IXSYS)==IXSYS_SHA,'ixsys binary身份变化')
    (origin, blobs, hashes, _), (build, library, build_log), reference = q.qualify(args.performance_control, life)
    base_blobs,base_hashes=blobs,hashes
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in manifest['files'].items()}
    hashes={p:v['sha256'] for p,v in manifest['files'].items()}
    q.require(source!=origin and len(hashes)==527 and life.source_maps(source)==(blobs,hashes),'诊断527来源不符')
    q.require({p for p in set(hashes)|set(base_hashes) if hashes.get(p)!=base_hashes.get(p)} == {'vllm_fl/__init__.py','vllm_fl/patches/biv150_current_hotspot_observer.py'},'仅允许观察接线与独立helper')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'profiles' / (stamp + '-current-main-hotspot-'+str(args.input_len))
    run.parent.mkdir(exist_ok=True)
    control = run.with_name(run.name + '-control')
    run.mkdir(exist_ok=False)
    control.mkdir(exist_ok=False)
    for name in q.read(HERE / 'asset-pins.json'):
        target = control / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(HERE / name, target)
    shutil.copyfile(HERE / 'asset-pins.json', control / 'asset-pins.json')
    shutil.copytree(source, control / 'plugin-source', symlinks=True,
        ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    gate.save(control / 'source-git-blobs.json', blobs)
    gate.save(control / 'source-sha256.json', hashes)
    gate.save(control / 'qualification-reference.json', reference)
    (control / 'native').mkdir()
    runtime = control / 'native/biv150_native_w8a8.so'
    shutil.copyfile(library, runtime)
    shutil.copyfile(build_log, control / 'native/build.log')
    gate.save(control / 'native/build-manifest.original.json', build)
    receipt = control / 'native/runtime-receipt.json'
    gate.save(receipt, dict(build, runtime_library=str(runtime)))
    gate.identity(source, hashes, runtime, q.SO)
    env = common.child_environment(source)
    env = {k:v for k,v in env.items() if not k.startswith(
        ('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
    for key in ('VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR'):
        env.pop(key, None)
    env.update(BIV150_NATIVE_W8A8_LIBRARY=str(runtime), BIV150_RESUME_NATIVE_RECEIPT=str(receipt),
        BIV150_RESUME_NATIVE_RECEIPT_SHA256=q.sha(receipt), VLLM_DISABLE_COMPILE_CACHE='0', PYTHONDONTWRITEBYTECODE='1')
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    q.check_environment(origin, env, build, reference['graph'])
    env.update(BIV150_CURRENT_HOTSPOT='1',MINICPM_CURRENT_HOTSPOT_EVENTS=str(run/'hotspot-events.jsonl'))
    gate.save(control / 'environment-overrides.json', {k:v for k,v in sorted(env.items())
        if k in gate.SAFE_ENV or k in ('BIV150_RESUME_NATIVE_RECEIPT', 'BIV150_RESUME_NATIVE_RECEIPT_SHA256',
                                      'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR', 'PYTHONDONTWRITEBYTECODE',
                                      'BIV150_CURRENT_HOTSPOT','MINICPM_CURRENT_HOTSPOT_EVENTS')})
    shutil.copyfile(gate.COMMON, control / 'run_accuracy_gate.py')
    shutil.copyfile(gate.MONITOR, control / 'monitor_gpu.sh')
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
        source_count=527, tree=manifest['tree'], base_commit=q.COMMIT, completed=False, cleanup_errors=[],
        owned_processes=[], server_command=common.SERVER, started_utc=common.utc(),
        kind='当前main526独立短窗profiler诊断；不是官方性能/准确率',
        input_length=args.input_len,output_length=1024,concurrency=64,num_prompts=64,seed=721201,
        limitations=['边界sync扰动首两步','逐步CPU元数据及profiler会增加开销','FULL图内节点未证实可见','不比较诊断吞吐作为收益'])
    gate.save(control / 'state.json', state)
    processes = []; lock = None; locked = False; original = None; handlers = {}
    server = None; service_pid = None; driver = None
    try:
        import fcntl
        lock = (ROOT / 'framework-device.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        locked = True
        for sig in (signal.SIGTERM, signal.SIGINT):
            handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt(str(number))))
        state['preflight'] = life.idle()
        state['common_preflight'] = common.preflight()
        state['cpu_before'] = common.cpu_state()
        shutil.copyfile(DB, control / 'database-original.sqlite')
        original = q.sha(control / 'database-original.sqlite')
        state['database_before_sha256'] = original
        entry=control/'server-entry.sh'
        entry.write_text('#!/usr/bin/env bash\nexec '+shlex.join(common.SERVER)+'\n',encoding='utf-8')
        command=[str(IXSYS),'-t','cuda','--profile-from-start','off','--print-kernel-args','-o',str(run/'native-trace.sqlite'),'bash',str(entry)]
        state['profiler_command']=command
        state['profiler_sha256']=q.sha(IXSYS)
        with (run / 'server.log').open('x') as log:
            server = subprocess.Popen(command, cwd='/workspace', env=env, stdout=log,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        processes.append(server)
        state['owned_processes'].append(dict(role='ixsys', pid=server.pid))
        (run / 'server.pid').write_text(str(server.pid)+'\n')
        gate.save(control / 'state.json', state)
        with (run / 'monitor.log').open('x') as log:
            monitor = subprocess.Popen(['bash', str(control / 'monitor_gpu.sh'), str(server.pid), str(run / 'gpu.csv')],
                stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        processes.append(monitor)
        state['owned_processes'].append(dict(role='monitor', pid=monitor.pid))
        (run / 'monitor.pid').write_text(str(monitor.pid)+'\n')
        gate.save(control / 'state.json', state)
        print(__import__('json').dumps(state), flush=True)
        common.wait_ready(server, 'BIV150_CURRENT_HOTSPOT_CORE_HOOKED', run)
        service_pid=owned_service(server.pid)
        state['service_pid']=service_pid
        (run/'service.pid').write_text(str(service_pid)+'\n')
        state['model_path'] = graph_gate.capture(run, source, env)
        gate.save(control / 'state.json', state)
        command=['bash',str(control/'run_diagnostic_load.sh'),str(run/'load'),'hotspot-'+str(args.input_len),str(args.input_len),'1024','64','64','721201']
        state['load_command']=command
        with (run/'load-driver.log').open('x') as log:
            driver=subprocess.Popen(command,cwd='/workspace',env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
        processes.append(driver)
        state['owned_processes'].append(dict(role='load',pid=driver.pid))
        gate.save(control/'state.json',state)
        state['load_exit_code']=driver.wait(timeout=900)
        q.require(state['load_exit_code']==0 and server.poll() is None,'诊断load失败或服务提前退出')
        state['load_completed']=True
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        if locked:
            try:
                if driver is not None and driver.poll() is None:
                    common.stop_owned_group(driver)
                if server is not None:
                    flush_trace(server,service_pid,state)
                if processes:
                    gate.clean_groups(common, processes, control, state)
                q.require(not state['cleanup_errors'], '所属进程未清理，不恢复DB')
                state['postflight'] = life.idle()
                if original is not None:
                    shutil.copyfile(DB, control / 'database-after.sqlite')
                    state['database_after_sha256'] = q.sha(control / 'database-after.sqlite')
                    shutil.copyfile(control / 'database-original.sqlite', DB)
                    state['database_restored'] = q.sha(DB) == original
                    q.require(state['database_restored'], 'DB恢复失败')
                state['source_unchanged'] = all(life.source_maps(p) == (blobs, hashes)
                    for p in (source, control / 'plugin-source'))
                state['native_unchanged'] = q.sha(runtime) == q.SO and q.sha(library) == q.SO
                q.require(life.source_maps(origin)==(base_blobs,base_hashes),'基线原件变化')
                q.require(state['source_unchanged'] and state['native_unchanged'], '源码或native后态变化')
                q.check_reference(reference)
                state['cpu_after'] = common.cpu_state()
                if state.get('load_completed'):
                    state['trace_validation']=validate_trace(run)
                    state['validation_completed']=bool(state.get('ixsys_flushed') and state['trace_validation']['valid'])
            except BaseException as error:
                state['cleanup_errors'].append(repr(error))
        state['completed'] = bool(state.get('validation_completed') and state.get('database_restored')
                                   and not state['cleanup_errors'] and not state.get('error'))
        state['finished_utc'] = common.utc()
        state['exit_code'] = 0 if state['completed'] else 1
        gate.save(control / 'state.json', state)
        gate.save(run / 'result.json', state)
        for path in (run, control):
            (path / 'exit-code').write_text(str(state['exit_code'])+'\n')
        if lock is not None:lock.close()
        for sig, handler in handlers.items():signal.signal(sig, handler)
    return state['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
