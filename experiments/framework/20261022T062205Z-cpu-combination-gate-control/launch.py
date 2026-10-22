#!/usr/bin/env python3
"""组合方法门薄层：固定输入、DB与封存；设备锁/worker/清理由原gate独占。"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import signal
import socket
import subprocess
import sys
import traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
DB = '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db'
BASE = ROOT / 'code/sql-mixed-20261021T080656Z/vllm_fl/worker/model_runner.py'
INPUTS = {
    'validate_cpu_combination.py': 'abfc7981a8d5a20ff32b80f42dd30148bbeb5d680c649bf892e2b3924ead0bad',
    'biv150_cpu_metadata.py': '0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f',
    'biv150_async_token_update.py': '1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc',
    'cpu-combination-model_runner.py': '6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141',
    'validate_block_table_candidate.py': '6072137cfb178dd77ebf4fbf9dd5ffc46534a56bbc07cbbc03f603d8ac1cb3b1',
    'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a',
    'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
BASE_SHA = 'e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1'


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    with path.open('x', encoding='utf-8', newline='\n') as file:
        json.dump(value, file, ensure_ascii=False, indent=2)
        file.write('\n')


def command(control, label, argv):
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, capture_output=True, timeout=30)
    (control / (label + '.stdout')).write_bytes(result.stdout)
    (control / (label + '.stderr')).write_bytes(result.stderr)
    write(control / (label + '-command.json'), {'argv': argv, 'shell': shlex.join(argv),
                                              'returncode': result.returncode, 'utc': utc()})
    if result.returncode:
        raise RuntimeError(label + ' failed: ' + str(result.returncode))
    return result.stdout.decode('utf-8', errors='replace')


def idle(control, label):
    query = command(control, label + '-query', ['ixsmi', '--query-gpu=memory.used,utilization.gpu',
                                               '--format=csv,noheader,nounits'])
    table = command(control, label + '-table', ['ixsmi'])
    ports = {}
    for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            ports[host] = sock.connect_ex((host, 9031)) != 0
    data = {'utc': utc(), 'query': query, 'ixsmi': table, 'ports_closed': ports}
    write(control / (label + '.json'), data)
    if (query.strip() != '68, 0' or 'No running processes found' not in table
            or 'BI-V150' not in table or '32768MiB' not in table or not all(ports.values())):
        raise RuntimeError(label + ': device/ports are not idle')
    return data


def snapshot(control, label):
    command(control, label, [sys.executable, str(control / 'snapshot_tuning_db.py'),
                            '--database', DB, '--output', str(control / label)])
    folder = control / label
    data = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if data.get('status') != 'complete' or sha(folder / 'snapshot.sqlite') != data.get('snapshot_sha256'):
        raise RuntimeError(label + ': incomplete snapshot')
    return {key: data[key] for key in ('snapshot_sha256', 'schema_sha256',
                                      'logical_content_sha256', 'table_count', 'row_count')}


def environment():
    packages = {}
    for name in ('torch', 'numpy', 'vllm', 'vllm-plugin-fl', 'flag-gems', 'flagtree', 'triton', 'sqlalchemy'):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = None
    cgroup = {}
    for part in ('cpu,cpuacct/cpu.cfs_quota_us', 'cpu,cpuacct/cpu.cfs_period_us',
                 'cpu,cpuacct/cpu.stat', 'memory/memory.limit_in_bytes', 'memory/memory.usage_in_bytes'):
        path = Path('/sys/fs/cgroup') / part
        if path.is_file():
            cgroup[str(path)] = path.read_text()
    return {'utc': utc(), 'python': sys.version, 'platform': platform.platform(), 'packages': packages,
            'env': {key: os.environ.get(key) for key in ('PATH', 'PYTHONPATH', 'LD_LIBRARY_PATH',
                    'VLLM_PLUGINS', 'COREX_VISIBLE_DEVICES', 'CUDA_VISIBLE_DEVICES',
                    'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'TRITON_CACHE_DIR')}, 'cgroup': cgroup}


def main():
    argparse.ArgumentParser(description=__doc__).parse_args()
    name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-cpu-combination-gate'
    run = ROOT / 'framework' / name
    control = run.with_name(name + '-control')
    if run.exists():
        raise FileExistsError(run)
    control.mkdir(exist_ok=False)
    shutil.copyfile(Path(__file__), control / 'launch.py')
    result = {'kind': '真实方法组合正确性；无权重/服务/性能/准确率成绩', 'started_utc': utc(),
              'launcher_pid': os.getpid(), 'run': str(run), 'control': str(control),
              'device_owner': 'validate_cpu_combination.py controller only',
              'db_snapshot_lock_scope': 'outside controller lock; root-exclusive serial dispatch required'}
    child = None
    checked = False
    status = 1
    print('RUN=' + str(run) + '\nCONTROL=' + str(control) + '\nLAUNCHER_PID=' + str(os.getpid()), flush=True)

    def interrupted(signum, frame):
        # Only notify the unique owner; never kill its GPU worker from this layer.
        if child is not None and child.poll() is None:
            child.send_signal(signum)
        raise InterruptedError('launcher signal ' + str(signum))

    signal.signal(signal.SIGTERM, interrupted)
    signal.signal(signal.SIGINT, interrupted)
    try:
        paths = {str(ROOT / 'scripts' / key): value for key, value in INPUTS.items()}
        paths[str(BASE)] = BASE_SHA
        for name_, expected in paths.items():
            path = Path(name_)
            if len(expected) != 64 or not path.is_file() or path.is_symlink() or sha(path) != expected:
                raise RuntimeError('unreviewed or changed input: ' + name_)
        checked = True
        write(control / 'input-sha256.json', paths)
        shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py', control / 'snapshot_tuning_db.py')
        write(control / 'environment-before.json', environment())
        result['preflight'] = idle(control, 'preflight')
        result['db_before'] = snapshot(control, 'db-before')
        argv = [sys.executable, str(ROOT / 'scripts/validate_cpu_combination.py'), '--run-dir', str(run),
                '--runtime-path', str(ROOT / 'scripts/biv150_cpu_metadata.py'),
                '--async-runtime-path', str(ROOT / 'scripts/biv150_async_token_update.py'),
                '--runner-path', str(BASE),
                '--candidate-runner-path', str(ROOT / 'scripts/cpu-combination-model_runner.py')]
        write(control / 'command.json', {'argv': argv, 'shell': shlex.join(argv)})
        env = os.environ.copy()
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        with (control / 'controller.log').open('xb') as log:
            child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                                     env=env, start_new_session=True)
            (control / 'controller.pid').write_text(str(child.pid) + '\n', encoding='utf-8')
            result['controller_pid'] = child.pid
            status = child.wait()
        result['controller_exit_code'] = status
        if status == 0:
            manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
            outcome = json.loads((run / 'results.json').read_text(encoding='utf-8'))
            if manifest.get('exit_code') != 0 or outcome.get('status') != 'pass':
                raise RuntimeError('controller/worker result inconsistent')
    except BaseException:
        status = 1
        result['error'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        if child is not None and child.poll() is None:
            # The owner receives SIGTERM and performs its original finally cleanup.
            child.terminate()
            child.wait()
        if checked:
            try:
                result['db_after'] = snapshot(control, 'db-after')
                result['db_unchanged'] = result.get('db_before') == result['db_after']
                write(control / 'environment-after.json', environment())
                result['postflight'] = idle(control, 'postflight')
                source = run / 'source'
                actual = {p.name: sha(p) for p in sorted(source.iterdir()) if p.is_file() and not p.is_symlink()}
                write(control / 'source-after.json', actual)
                manifest = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
                if actual != manifest['source_sha256']:
                    raise RuntimeError('archived source changed')
            except BaseException:
                status = 1
                result['postflight_error'] = traceback.format_exc()
        result.update(finished_utc=utc(), exit_code=status)
        write(control / 'result.json', result)
        (control / 'exit-code').write_text(str(status) + '\n', encoding='utf-8')
        (control / 'finished-at.txt').write_text(result['finished_utc'] + '\n', encoding='utf-8')
        sys.stdout.flush()
        sys.stderr.flush()
        files = {str(p.relative_to(ROOT / 'framework')): sha(p)
                 for folder in (run, control) if folder.is_dir()
                 for p in sorted(folder.rglob('*')) if p.is_file() and not p.is_symlink()}
        write(control / 'seal.json', {'status': 'pass' if status == 0 else 'failed',
                                     'utc': utc(), 'files_sha256': files})
    return status


if __name__ == '__main__':
    raise SystemExit(main())
