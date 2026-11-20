"""旧467/a42整套版本freshserver原mixed双请求；无性能或新准确率资格。"""
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import signal
import subprocess
import traceback

import cache_gate as gate
import old_identity as old_graph
import diagnostic_requests
import lifecycle as life
import old_identity as q

HERE = Path(__file__).resolve().parent
ROOT = q.ROOT
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--reference-control', required=True, type=Path)
    args = parser.parse_args()
    q.assets()
    q.require(q.sha(gate.COMMON) == gate.COMMON_SHA and q.sha(gate.MONITOR) == gate.MONITOR_SHA,
              '原common/monitor来源变化')
    common = q.load(gate.COMMON, 'final_ffn_verify_common')
    source = args.source_dir.resolve(strict=True)
    q.require(not args.source_dir.is_symlink() and source.is_relative_to(ROOT / 'code'), '旧467来源必须为已测code目录')
    manifest = {'tree': q.TREE}
    (origin, blobs, hashes, _), (build, library, build_log), reference = q.qualify(args.reference_control, life)
    q.require(source == origin, '必须直接使用已验证旧467源码')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'framework' / (stamp + '-pr24-467-native-disabled-mixed-token-diagnostic')
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
    q.identity(source, blobs, hashes, runtime)
    env = common.child_environment(source)
    env = {k:v for k,v in env.items() if not k.startswith(
        ('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
    env.update(BIV150_NATIVE_W8A8_LIBRARY=str(runtime), VLLM_FL_BIV150_NATIVE_W8A8='0', VLLM_DISABLE_COMPILE_CACHE='1',
        VLLM_CACHE_ROOT=str(control/'vllm-cache'), TORCHINDUCTOR_CACHE_DIR=str(control/'inductor-cache'),
        PYTHONDONTWRITEBYTECODE='1', PYTHONUNBUFFERED='1')
    q.require(not (control/'vllm-cache').exists() and not (control/'inductor-cache').exists(), '必须全新隔离缓存')
    gate.save(control / 'environment-overrides.json', {k:v for k,v in sorted(env.items())
        if k in gate.SAFE_ENV or k in ('BIV150_RESUME_NATIVE_RECEIPT', 'BIV150_RESUME_NATIVE_RECEIPT_SHA256',
                                      'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR', 'PYTHONDONTWRITEBYTECODE', 'VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR')})
    shutil.copyfile(gate.COMMON, control / 'run_accuracy_gate.py')
    shutil.copyfile(gate.MONITOR, control / 'monitor_gpu.sh')
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
        source_count=467, tree=manifest['tree'], base_commit=q.COMMIT, completed=False, cleanup_errors=[],
        owned_processes=[], server_command=common.SERVER, started_utc=common.utc(),
        kind='旧467 native-disabled原mixed2；仅隔离正确性，非合规优化/性能/新基线')
    gate.save(control / 'state.json', state)
    processes = []; lock = None; locked = False; original = None; handlers = {}
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
        with (run / 'server.log').open('x') as log:
            server = subprocess.Popen(common.SERVER, cwd='/workspace', env=env, stdout=log,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        processes.append(server)
        state['owned_processes'].append(dict(role='server', pid=server.pid))
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
        common.wait_ready(server, 'BIV150_NATIVE_W8A8_INSTALL', run)
        state['model_path'] = old_graph.capture(run, source, env)
        gate.save(control / 'state.json', state)
        state['diagnostic'] = diagnostic_requests.run(run)
        gate.save(control / 'state.json', state)
        q.require(server.poll() is None, 'token诊断后服务退出')
        state['validation_completed'] = bool(state['diagnostic']['completed'])
        q.require(state['diagnostic']['all_correct'], '原旧467 mixed存在语义失败，详见完整响应/token原件')
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        if locked:
            try:
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
                state['source_unchanged'] = all(q.identity(p, blobs, hashes, runtime)
                    for p in (source, control / 'plugin-source'))
                state['native_unchanged'] = q.sha(runtime) == q.SO and q.sha(library) == q.SO
                q.require(state['source_unchanged'] and state['native_unchanged'], '源码或native后态变化')
                q.check_reference(reference)
                state['cpu_after'] = common.cpu_state()
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
