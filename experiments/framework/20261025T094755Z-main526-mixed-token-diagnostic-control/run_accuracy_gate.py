#!/usr/bin/env python3
"""Own one official Math500 Level 3 run; retain evidence, never infer a pass.

Run on the instance only after the device is idle. This driver imports no
torch/vLLM/FlagGems modules and provides no profiler or sampling overrides.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import socket
import subprocess
import sys
import time
import traceback
import urllib.request


ROOT = Path('/workspace/experiments/minicpm-s2')
IXSMI = '/usr/local/corex-4.5.0/bin/ixsmi'
SITE = Path('/usr/local/lib/python3.12/site-packages')
OFFICIAL_SCRIPT_SHA256 = '6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4'
SERVER = [
    'vllm', 'serve', '/workspace/MiniCPM5-2B', '--port', '9031',
    '--compilation-config', '{"cudagraph_mode": "FULL_DECODE_ONLY"}',
    '--served-model-name', 'minicpm', '--gpu-memory-utilization', '0.85',
    '--max-model-len', '131072',
]


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + '\n', encoding='utf-8')


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpu_state():
    paths = Path('/sys/fs/cgroup/cpu,cpuacct')
    return {name: (paths / name).read_text() for name in
            ['cpu.cfs_quota_us', 'cpu.cfs_period_us', 'cpu.stat'] if (paths / name).exists()}


def preflight():
    # No CUDA context; the common device lock must already be held.
    for family, address in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        try:
            with socket.socket(family) as sock:
                sock.settimeout(1)
                if sock.connect_ex((address, 9031)) == 0:
                    raise RuntimeError('port 9031 occupied')
        except OSError:
            if family == socket.AF_INET:
                raise
    output = subprocess.check_output(
        [IXSMI, '--query-gpu=memory.free', '--format=csv,noheader,nounits'],
        text=True, timeout=10)
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or not lines[0].isdigit() or int(lines[0]) < 30000:
        raise RuntimeError('expected one idle accelerator, free MiB >=30000: ' + repr(lines))
    return {'checked_utc': utc(), 'port_9031': 'free', 'free_mib': int(lines[0])}


def child_environment(source):
    env = os.environ.copy()
    forbidden = [
        'VLLM_FL_ILUVATAR_MAX_NUM_BATCHED_TOKENS',
        'VLLM_FL_ILUVATAR_DISABLE_PREFIX_CACHE', 'VLLM_FL_ILUVATAR_BLOCK_SIZE',
        'VLLM_FL_USE_FLAGGEMS_ATTN', 'VLLM_FL_ILUVATAR_COMPILE_SAMPLER',
        'MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR',
        'FLAGGEMS_DB_URL', 'FLAGGEMS_CACHE_DIR',
    ]
    for name in forbidden:
        if name in env:
            raise RuntimeError('unexpected diagnostic/cache override: ' + name)
    env.update(VLLM_PLUGINS='fl', PYTHONPATH=str(source), PYTHONUNBUFFERED='1')
    return env


def stop_owned_group(process, timeout=45):
    """Signal only a group created by this driver, including its pipeline."""
    if process is None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=10)


def archive_sources(run, source):
    archive = run / 'source'
    archive.mkdir()
    scripts = Path(__file__).resolve().parent
    official = scripts / 'run_math500_level3.sh'
    if sha256(official) != OFFICIAL_SCRIPT_SHA256:
        raise RuntimeError('official accuracy script hash mismatch')
    for name in ['run_accuracy_gate.py', 'run_math500_level3.sh', 'monitor_gpu.sh',
                 'snapshot_tuning_db.py']:
        shutil.copyfile(scripts / name, archive / name)
    plugin = archive / 'plugin'
    plugin.mkdir()
    shutil.copytree(source / 'vllm_fl', plugin / 'vllm_fl',
                    ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    for name in ['pyproject.toml', 'setup.py', 'setup.cfg', 'README.md', 'LICENSE', 'base-revision.txt']:
        if (source / name).is_file():
            shutil.copyfile(source / name, plugin / name)
    installed = [
        SITE / 'vllm/v1/worker/block_table.py',
        SITE / 'vllm/v1/attention/backends/triton_attn.py',
        SITE / 'vllm/v1/attention/ops/triton_unified_attention.py',
        SITE / 'vllm/v1/attention/ops/triton_attention_helpers.py',
        SITE / 'flag_gems/runtime/backend/_iluvatar/ops/mm.py',
        SITE / 'flag_gems/utils/models/sql.py',
        SITE / 'triton/__init__.py',
    ]
    for path in installed:
        target = archive / 'installed' / path.relative_to(SITE)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)
    for name in ['config.json', 'generation_config.json']:
        shutil.copyfile(Path('/workspace/MiniCPM5-2B') / name, archive / name)
    dataset = archive / 'dataset'
    dataset.mkdir()
    for name in ['test.jsonl', 'eval.yaml']:
        shutil.copyfile(Path('/workspace/evalscope-datasets/math_500') / name, dataset / name)
    return {str(path.relative_to(archive)): sha256(path)
            for path in sorted(archive.rglob('*')) if path.is_file()}


def snapshot_database(run, database, phase):
    command = [sys.executable, str(run / 'source/snapshot_tuning_db.py'),
               '--database', str(database), '--output', str(run / ('database-' + phase))]
    write_json(run / ('database-' + phase + '-command.json'), command)
    with (run / ('database-' + phase + '.log')).open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=120)


def wait_ready(server, log_marker, run):
    deadline = time.monotonic() + 600
    while True:
        if server.poll() is not None:
            raise RuntimeError('server exited before ready')
        try:
            with urllib.request.urlopen('http://127.0.0.1:9031/v1/models', timeout=3) as response:
                models = json.load(response)
            if not any(item.get('id') == 'minicpm' for item in models.get('data', [])):
                raise ValueError('served model minicpm absent')
            break
        except (OSError, ValueError):
            if time.monotonic() > deadline:
                raise TimeoutError('service readiness timeout')
            time.sleep(3)
    write_json(run / 'models.json', models)
    if log_marker and log_marker not in (run / 'server.log').read_text(errors='replace'):
        raise RuntimeError('required installation marker absent: ' + log_marker)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path, help='new directory under ROOT/accuracy')
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--require-log-marker')
    parser.add_argument('--database', type=Path, help='explicit existing tuning DB; read-only snapshots')
    args = parser.parse_args(argv)
    run, source = args.run_dir.resolve(), args.source_dir.resolve(strict=True)
    if not run.is_relative_to(ROOT / 'accuracy') or run == ROOT / 'accuracy':
        raise ValueError('accuracy run must be a child of ROOT/accuracy')
    if not source.is_relative_to(ROOT / 'code') or not (source / 'vllm_fl/worker/model_runner.py').is_file():
        raise ValueError('source must be an isolated plugin under ROOT/code')
    database = args.database.resolve(strict=True) if args.database else None
    if database is not None and not database.is_file():
        raise ValueError('database must be an existing file')
    run.mkdir(parents=True, exist_ok=False)
    (run / 'started-at.txt').write_text(utc() + '\n')
    result = {'status': 'started', 'evaluation_completed': False, 'accuracy_gate': 'unassessed',
              'required_manual_checks': ['105 Level 3 samples', 'request/evaluation failures',
                                         'accuracy >= 0.95'], 'cleanup_errors': []}
    manifest = {'kind': 'official Math500 Level 3 accuracy; not performance score',
                'started_utc': utc(), 'source_dir': str(source), 'server_command': SERVER,
                'database': str(database) if database else None,
                'require_log_marker': args.require_log_marker, 'cpu_before': cpu_state(),
                'python': platform.python_version(), 'evaluation_outer_timeout_seconds': 21600}
    lock = server = evaluation = monitor = None
    database_before = False
    status = 1
    previous_handlers = {}
    try:
        # Defer POSIX import so the command/evidence contract can be CPU-tested on Windows.
        import fcntl
        lock = (ROOT / 'framework-device.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, lambda number, frame: (_ for _ in ()).throw(
                KeyboardInterrupt('received signal ' + str(number))))
        manifest['preflight'] = preflight()
        env = child_environment(source)
        manifest['sha256'] = archive_sources(run, source)
        manifest['packages'] = {}
        for name in ['vllm', 'vllm-plugin-fl', 'torch', 'transformers', 'flag-gems', 'sqlalchemy', 'evalscope']:
            manifest['packages'][name] = importlib.metadata.version(name)
        # The instance's Triton has no distribution metadata; record its source version.
        triton_source = (SITE / 'triton/__init__.py').read_text()
        match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)', triton_source, re.MULTILINE)
        manifest['triton_source_version'] = match.group(1) if match else 'not found'
        for label, checkout in [('plugin', source), ('flaggems', Path('/workspace/FlagGems'))]:
            if (checkout / '.git').exists():
                manifest[label + '_revision'] = subprocess.check_output(
                    ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
                manifest[label + '_status'] = subprocess.check_output(
                    ['git', '-C', str(checkout), 'status', '--short'], text=True)
        if (source / 'base-revision.txt').exists():
            manifest['plugin_base_revision'] = (source / 'base-revision.txt').read_text().strip()
        write_json(run / 'manifest.json', manifest)
        if database is not None:
            snapshot_database(run, database, 'before')
            database_before = True
        with (run / 'server.log').open('w') as log:
            server = subprocess.Popen(SERVER, cwd='/workspace', env=env, stdout=log,
                                      stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                      start_new_session=True)
        (run / 'server.pid').write_text(str(server.pid) + '\n')
        with (run / 'monitor.log').open('w') as log:
            monitor = subprocess.Popen(
                ['bash', str(run / 'source/monitor_gpu.sh'), str(server.pid), str(run / 'gpu.csv')],
                stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        wait_ready(server, args.require_log_marker, run)
        command = ['bash', str(run / 'source/run_math500_level3.sh'), str(run / 'math500-level3')]
        write_json(run / 'evaluation-command.json', command)
        result['evaluation_started_utc'] = utc()
        with (run / 'evaluation-launcher.log').open('w') as log:
            evaluation = subprocess.Popen(command, cwd='/workspace', env=env, stdout=log,
                                          stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                          start_new_session=True)
        (run / 'evaluation.pid').write_text(str(evaluation.pid) + '\n')
        result['evaluation_exit_code'] = evaluation.wait(timeout=21600)
        result['evaluation_finished_utc'] = utc()
        if result['evaluation_exit_code'] != 0:
            raise RuntimeError('official evaluation command failed')
        if server.poll() is not None:
            raise RuntimeError('server exited during evaluation')
        result.update(status='evaluation_completed_requires_report_review', evaluation_completed=True)
        status = 0
    except BaseException as error:
        result.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    finally:
        # Preserve failures, and keep the shared lock until all owned jobs stop.
        for label, process in [('evaluation', evaluation), ('server', server), ('monitor', monitor)]:
            try:
                stop_owned_group(process)
                if process is not None:
                    result[label + '_final_returncode'] = process.returncode
            except BaseException as error:
                result['cleanup_errors'].append(label + ': ' + repr(error))
                status = 2
        if database_before:
            try:
                snapshot_database(run, database, 'after')
            except BaseException as error:
                result['cleanup_errors'].append('database-after: ' + repr(error))
                status = 2
        if server is not None:
            try:
                result['postflight'] = preflight()
            except BaseException as error:
                result['cleanup_errors'].append('postflight: ' + repr(error))
                status = 2
        result.update(exit_code=status, finished_utc=utc(), cpu_after=cpu_state())
        write_json(run / 'manifest.json', manifest)
        write_json(run / 'result.json', result)
        (run / 'exit-code').write_text(str(status) + '\n')
        (run / 'finished-at.txt').write_text(result['finished_utc'] + '\n')
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
        if lock is not None:
            lock.close()
    print(json.dumps({'run_dir': str(run), 'exit_code': status,
                      'evaluation_completed': result['evaluation_completed'],
                      'accuracy_gate': 'unassessed'}), flush=True)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
