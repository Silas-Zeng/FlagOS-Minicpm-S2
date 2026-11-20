"""干净团队main34942f7原官方四轮；不改原服务和评测参数。"""
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
HERE = Path(__file__).resolve().parent
QUALIFICATION = HERE / 'qualification.py'
COMMON = ROOT / 'scripts/run_accuracy_gate.py'
DRIVER = ROOT / 'scripts/run_official_gate.py'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
DRIVER_SHA = '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def model_path_evidence(run, control, reference, source, env):
    import graph_gate
    import activation_evidence
    evidence = graph_gate.capture(run, source, env)
    evidence['main_activation'] = activation_evidence.capture(run, control, source, env)
    evidence['valid'] = evidence['valid'] and evidence['main_activation']['valid']
    save(control / 'model-path-evidence.json', evidence)
    return evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--performance-control', required=True, type=Path)
    parser.add_argument('--source-dir', required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('main_accuracy_qualification', QUALIFICATION)
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    q.assets()
    if sha(DRIVER) != DRIVER_SHA or sha(COMMON) != COMMON_SHA:
        raise ValueError('原官方driver或35d common变化')
    spec = importlib.util.spec_from_file_location('main_accuracy_lifecycle', HERE / 'lifecycle.py')
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    source_identity, native, reference = q.qualify(args.performance_control, u, args.source_dir)
    performance_control = Path(reference['control'])
    origin, blobs, hashes, tree = source_identity
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'official' / (stamp + '-main34942f7-official-baseline-four-rounds')
    control = run.with_name(run.name + '-control')
    source = ROOT / 'code' / (stamp + '-main34942f7-official-baseline')
    control.mkdir(exist_ok=False)
    shutil.copytree(origin, source, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if u.source_maps(source) != (blobs, hashes):
        raise ValueError('源码复制不符')
    save(control / 'source-git-blobs.json', blobs)
    save(control / 'source-sha256.json', hashes)
    shutil.copyfile(__file__, control / 'official_owner.py')
    for name in q.read(HERE / 'asset-pins.json'):
        shutil.copyfile(HERE / name, control / name)
    shutil.copyfile(HERE / 'asset-pins.json', control / 'asset-pins.json')
    save(control / 'qualification-references.json', reference)
    build, library, build_log = native
    (control / 'native').mkdir()
    runtime = control / 'native/biv150_native_w8a8.so'
    shutil.copyfile(library, runtime)
    shutil.copyfile(build_log, control / 'native/build.log')
    save(control / 'native/build-manifest.json', build)
    if sha(runtime) != build['library_sha256']:
        raise ValueError('native复制不符')
    receipt = control / 'native/runtime-receipt.json'
    save(receipt, dict(build, runtime_library=str(runtime)))
    env = {k:v for k,v in os.environ.items() if not k.startswith(('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
    env.pop('VLLM_CACHE_ROOT', None)
    env.pop('TORCHINDUCTOR_CACHE_DIR', None)
    env.update(BIV150_NATIVE_W8A8_LIBRARY=str(runtime),
               BIV150_RESUME_NATIVE_RECEIPT=str(receipt), BIV150_RESUME_NATIVE_RECEIPT_SHA256=sha(receipt),
               VLLM_DISABLE_COMPILE_CACHE='0', PYTHONUNBUFFERED='1')
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    save(control / 'environment-overrides.json', {k:v for k,v in env.items()
         if k.startswith(('BIV150_', 'VLLM_FL_BIV150_')) or k in ('VLLM_DISABLE_COMPILE_CACHE', 'PYTHONUNBUFFERED')})
    q.check_environment(source, env, build, reference['graph'])
    command = [sys.executable, str(DRIVER), str(run), '--source-dir', str(source),
               '--require-log-marker', 'BIV150_NATIVE_W8A8_INSTALL', '--database', str(DB)]
    save(control / 'command.json', command)
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
                 commit=q.COMMIT, base_commit=q.COMMIT, tree=tree, source_count=len(blobs), completed=False,
                 performance_control=str(performance_control),
                 qualification='干净main34942f7完整618；PR51默认修复保留，原native14f/官方参数；旧control仅原件来源，不继承其成绩')
    lock = (ROOT / 'framework-device.lock').open('a')
    process = None
    original = None
    handlers = {}
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt(str(number))))
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state['preflight'] = u.idle()
        shutil.copyfile(DB, control / 'database-original.sqlite')
        original = sha(control / 'database-original.sqlite')
        state['database_before_sha256'] = original
        fcntl.flock(lock, fcntl.LOCK_UN)
        with (control / 'driver.log').open('x') as log:
            process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state.update(driver_pid=process.pid, stage='running')
        save(control / 'state.json', state)
        print(json.dumps(state), flush=True)
        state['driver_exit_code'] = process.wait()
        result = json.loads((run / 'result.json').read_text())
        state['result'] = result
        if (process.returncode != 0 or not result.get('benchmark_completed') or result.get('cleanup_errors')
                or 'monitor_final_returncode' not in result or (run / 'exit-code').read_text().strip() != '0'):
            raise RuntimeError('原官方吞吐驱动未完成，保留原件')
        state['model_path'] = model_path_evidence(run, control, reference, source, env)
        q.require(state['model_path']['valid'], '完整官方负载后的实际优化栈未闭合；成绩与原件保留')
        q.check_reference(reference)
        state['benchmark_completed'] = True
        state['accuracy_gate'] = 'not_inherited_from_component_or_parent_main' 
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc())
    finally:
        try:
            if process is not None and process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=120)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            pids = set()
            if process is not None:
                pids.add(process.pid)
            for path in [run / 'server.pid', run / 'benchmark.pid']:
                if path.exists():
                    pid = int(path.read_text().strip())
                    if pid <= 1:
                        raise ValueError('pid格式不符')
                    pids.add(pid)
            groups = [u.owned_group(pid) for pid in sorted(pids)]
            deadline = time.monotonic() + 6
            while (not any(g['errors'] for g in groups) and
                   any(m['state'] != 'Z' for g in groups for m in g['members']) and time.monotonic() < deadline):
                time.sleep(.2)
                groups = [u.owned_group(pid) for pid in sorted(pids)]
            save(control / 'owner-process-groups.json', groups)
            if any(g['errors'] for g in groups) or any(m['state'] != 'Z' for g in groups for m in g['members']):
                raise RuntimeError('所属进程未退出；不恢复DB')
            state['postflight'] = u.idle()
            if original is not None:
                shutil.copyfile(DB, control / 'database-after.sqlite')
                state['database_after_sha256'] = sha(control / 'database-after.sqlite')
                shutil.copyfile(control / 'database-original.sqlite', DB)
                state['database_restored'] = sha(DB) == original
                if not state['database_restored']:
                    raise RuntimeError('DB恢复失败')
            state['source_unchanged'] = all(u.source_maps(path) == (blobs, hashes) for path in (origin, source))
            state['native_unchanged'] = sha(runtime) == build['library_sha256']
            if not state['source_unchanged'] or not state['native_unchanged']:
                raise RuntimeError('源码或native变化')
            state['completed'] = state.get('benchmark_completed', False)
        except BaseException as error:
            state['cleanup_error'] = repr(error)
        # 收尾后读取原日志；负筛主动停止亦留回执，不在启动期要求FIRST_SELECTED。
        if (run / 'server.log').exists():
            try:
                import activation_evidence
                state['stack_activation'] = activation_evidence.stack_evidence(run / 'server.log')
                save(control / 'stack-activation.json', state['stack_activation'])
                state['stable_small_o_activation'] = activation_evidence.stable_small_o_evidence(run / 'server.log')
                save(control / 'stable-small-bf16-activation.json', state['stable_small_o_activation'])
            except Exception as error:
                state['stack_activation_error'] = repr(error)
        state['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save(control / 'state.json', state)
        (control / 'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return 0 if state['completed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
