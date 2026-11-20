"""默认native关闭候选的完整105准确率；原35d驱动/题目/参数不变。"""
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
DRIVER = ROOT / 'scripts/run_accuracy_gate.py'
DRIVER_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', required=True, type=Path)
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location('main_accuracy_qualification', QUALIFICATION)
    q = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(q)
    q.assets()
    if sha(DRIVER) != DRIVER_SHA:
        raise ValueError('原35d准确率驱动变化')
    spec = importlib.util.spec_from_file_location('main_accuracy_lifecycle', HERE / 'lifecycle.py')
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    source_identity, reference = q.qualify(args.source_dir, u)
    origin, blobs, hashes, tree = source_identity
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'accuracy' / (stamp + '-native-safe-default-math500')
    control = run.with_name(run.name + '-control')
    source = ROOT / 'code' / (stamp + '-native-safe-default-accuracy')
    control.mkdir(exist_ok=False)
    shutil.copytree(origin, source, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if u.source_maps(source) != (blobs, hashes):
        raise ValueError('源码复制不符')
    save(control / 'source-git-blobs.json', blobs)
    save(control / 'source-sha256.json', hashes)
    shutil.copyfile(__file__, control / 'accuracy_owner.py')
    for name in q.read(HERE / 'asset-pins.json'):
        shutil.copyfile(HERE / name, control / name)
    shutil.copyfile(HERE / 'asset-pins.json', control / 'asset-pins.json')
    save(control / 'qualification-references.json', reference)
    env = {k:v for k,v in os.environ.items() if not k.startswith(('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
    env.pop('VLLM_CACHE_ROOT', None)
    env.pop('TORCHINDUCTOR_CACHE_DIR', None)
    env.update(VLLM_DISABLE_COMPILE_CACHE='0', PYTHONUNBUFFERED='1')
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    save(control / 'environment-overrides.json', {k:v for k,v in env.items()
         if k.startswith(('BIV150_', 'VLLM_FL_BIV150_')) or k in ('VLLM_DISABLE_COMPILE_CACHE', 'PYTHONUNBUFFERED')})
    expected_fingerprint = q.check_environment(source, env)
    save(control / 'expected-fingerprint.json', expected_fingerprint)
    command = [sys.executable, str(DRIVER), str(run), '--source-dir', str(source),
               '--require-log-marker', 'BIV150_NATIVE_W8A8_INSTALL', '--database', str(DB)]
    save(control / 'command.json', command)
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
                 commit=reference['commit'], tree=tree, source_count=len(blobs), completed=False,
                 source_manifest_sha256=sha(HERE / 'source-manifest.json'),
                 qualification='候选完整manifest；无native环境覆盖、默认cache0、实际FX0native；105结果需原review脚本判断')
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
        if (process.returncode != 0 or not result.get('evaluation_completed') or result.get('cleanup_errors')
                or 'monitor_final_returncode' not in result or (run / 'exit-code').read_text().strip() != '0'):
            raise RuntimeError('准确率驱动未完成，保留原件')
        state['model_path'] = q.model_path_evidence(run, control, expected_fingerprint)
        q.check_reference(reference)
        state['evaluation_completed'] = True
        state['accuracy_gate'] = 'unassessed_requires_original_105_prediction_and_report_review' 
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
            for path in [run / 'server.pid', run / 'evaluation.pid']:
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
            if not state['source_unchanged']:
                raise RuntimeError('源码变化')
            state['completed'] = state.get('evaluation_completed', False)
        except BaseException as error:
            state['cleanup_error'] = repr(error)
        state['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save(control / 'state.json', state)
        (control / 'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return 0 if state['completed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
