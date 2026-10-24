#!/usr/bin/env python3
"""One owned server and two serial, bounded diagnostic loads (not a score)."""

import argparse
import fcntl
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import signal
import shlex
import socket
import sqlite3
import subprocess
import time
import urllib.request
from datetime import datetime, timezone


ROOT = Path('/workspace/experiments/minicpm-s2')
IXSMI = '/usr/local/corex-4.5.0/bin/ixsmi'
SERVER = [
    'vllm', 'serve', '/workspace/MiniCPM5-2B', '--port', '9031',
    '--compilation-config', '{"cudagraph_mode": "FULL_DECODE_ONLY"}',
    '--served-model-name', 'minicpm', '--gpu-memory-utilization', '0.85',
    '--max-model-len', '131072',
]


def utc():
    return datetime.now(timezone.utc).isoformat()


def cpu_state():
    result = {}
    for name in ['cpu.cfs_quota_us', 'cpu.cfs_period_us', 'cpu.stat']:
        path = Path('/sys/fs/cgroup/cpu,cpuacct') / name
        if path.exists():
            result[name] = path.read_text()
    return result


def request(path, payload=None, timeout=3):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        'http://127.0.0.1:9031' + path, data=data,
        headers={'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.load(response)


def snapshot_metrics(run, label):
    # Outside the measured client load, preserve original counter samples so
    # a scheduling candidate can be judged against actual preemption deltas.
    with urllib.request.urlopen('http://127.0.0.1:9031/metrics', timeout=5) as response:
        (run / f'metrics-{label}.prom').write_bytes(response.read())
    (run / f'metrics-{label}-utc.txt').write_text(utc() + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=721001)
    parser.add_argument('--smoke-only', action='store_true')
    parser.add_argument('--smoke-repeats', type=int, choices=range(1, 5), default=1)
    parser.add_argument('--native-profile', action='store_true')
    parser.add_argument('--host-profile', action='store_true', help='Diagnostic-only bounded CPU/walltime window')
    parser.add_argument('--decode-screen', action='store_true', help='One short load with sustained decode concurrency')
    parser.add_argument('--context-screen', action='store_true', help='One 16K load: 32 requests, 128 output tokens, concurrency64')
    parser.add_argument('--context-long-screen', action='store_true', help='One 16K load: 32 requests, 1024 output tokens, concurrency64')
    parser.add_argument('--require-log-marker', help='Fail before loads if installation evidence is absent')
    parser.add_argument('--answer-requests', required=True, type=Path)
    parser.add_argument('--answer-variant', required=True, choices=('baseline', 'candidate'))
    args = parser.parse_args()
    if not args.context_screen or args.native_profile or args.host_profile or args.smoke_only or args.decode_screen or args.context_long_screen:
        parser.error('辅助答案门只接受原context-screen形状，不启profiler')
    answer_client = Path(__file__).with_name('run_answer_load.py')
    if hashlib.sha256(answer_client.read_bytes()).hexdigest() != '6dafbfbee4e3f91343ce28ecfefd55a48202e701d718184d8036556dff722c12':
        raise ValueError('辅助client身份变化')
    if args.context_long_screen and (args.context_screen or args.native_profile or args.host_profile or args.smoke_only or args.decode_screen):
        parser.error('--context-long-screen requires a standalone unprofiled load')
    if args.context_screen and (args.native_profile or args.host_profile or args.smoke_only or args.decode_screen):
        parser.error('--context-screen requires a standalone unprofiled load')
    if args.native_profile and args.smoke_only:
        parser.error('--native-profile requires its decode load, not --smoke-only')
    if args.decode_screen and (args.native_profile or args.smoke_only):
        parser.error('--decode-screen cannot be combined with native-profile or smoke-only')
    if args.host_profile and (args.native_profile or args.smoke_only):
        parser.error('--host-profile cannot be combined with native-profile or smoke-only')
    run = args.run_dir.resolve()
    source = args.source_dir.resolve()
    if not run.is_relative_to(ROOT) or not source.is_relative_to(ROOT / 'code'):
        raise ValueError('run/source directory outside experiment workspace')
    run.mkdir(parents=True, exist_ok=True)
    # Never overwrite a previous attempt, including a failed one.
    with (run / 'started-at.txt').open('x') as handle:
        handle.write(utc() + '\n')
    (run / 'screen-driver.py').write_bytes(Path(__file__).read_bytes())
    lock = (ROOT / 'framework-device.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    with socket.socket() as sock:
        sock.settimeout(1)
        if sock.connect_ex(('127.0.0.1', 9031)) == 0:
            raise RuntimeError('port 9031 occupied')
    free = subprocess.check_output(
        [IXSMI, '--query-gpu=memory.free', '--format=csv,noheader,nounits'], text=True,
    ).splitlines()[0].strip()
    if int(free) < 30000:
        raise RuntimeError('device occupied: free MiB=' + free)
    env = os.environ.copy()
    for name in [
        'VLLM_FL_ILUVATAR_MAX_NUM_BATCHED_TOKENS',
        'VLLM_FL_ILUVATAR_DISABLE_PREFIX_CACHE', 'VLLM_FL_ILUVATAR_BLOCK_SIZE',
        'VLLM_FL_USE_FLAGGEMS_ATTN', 'VLLM_FL_ILUVATAR_COMPILE_SAMPLER',
    ]:
        if name in env:
            raise RuntimeError('unexpected diagnostic override: ' + name)
    env.update(VLLM_PLUGINS='fl', PYTHONPATH=str(source), PYTHONUNBUFFERED='1')
    if args.native_profile:
        env['MINICPM_NATIVE_PROFILE_EVENTS'] = str(run / 'native-events.jsonl')
    if args.host_profile:
        env['MINICPM_DECODE_GAP_RUN_DIR'] = str(run)
    paths = [
        source / 'vllm_fl/__init__.py',
        source / 'vllm_fl/worker/model_runner.py',
        source / 'vllm_fl/patches/biv150_runtime.py',
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/worker/block_table.py'),
        Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_attention_helpers.py'),
        Path('/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops/mm.py'),
        Path('/usr/local/lib/python3.12/site-packages/flag_gems/utils/models/sql.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/sched/scheduler.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/sched/async_scheduler.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/kv_cache_manager.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/kv_cache_coordinator.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/single_type_kv_cache_manager.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/core/block_pool.py'),
        Path('/workspace/MiniCPM5-2B/config.json'),
        Path('/workspace/MiniCPM5-2B/generation_config.json'),
    ]
    paths.extend(sorted((source / 'vllm_fl/patches').glob('biv150*py')))
    if args.host_profile:
        for name in ['index.py', '../utils/libentry.py', '../utils/pointwise_dynamic.py']:
            paths.append((Path('/usr/local/lib/python3.12/site-packages/flag_gems/ops') / name).resolve())
        snapshot = run / 'source'
        snapshot.mkdir()
        for path in [source / 'vllm_fl/worker/model_runner.py', *paths[-3:]]:
            (snapshot / path.name).write_bytes(path.read_bytes())
    manifest = {
        'kind': ('bounded host profile; not performance comparison or official score'
                 if args.host_profile else 'short serial diagnostic; not official performance'),
        'started_utc': utc(), 'server_command': SERVER, 'source_dir': str(source),
        'seed': args.seed, 'cpu_before': cpu_state(),
        'smoke_only': args.smoke_only, 'smoke_repeats': args.smoke_repeats,
        'native_profile': args.native_profile,
        'host_profile': args.host_profile,
        'decode_screen': args.decode_screen,
        'context_screen': args.context_screen,
        'context_long_screen': args.context_long_screen,
        'require_log_marker': args.require_log_marker,
        'packages': {name: importlib.metadata.version(name) for name in
                     ['vllm', 'vllm-plugin-fl', 'torch', 'transformers', 'flag-gems', 'sqlalchemy']},
        'sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    }
    for label, checkout in [('plugin', source), ('flaggems', Path('/workspace/FlagGems'))]:
        if (checkout / '.git').exists():
            manifest[label + '_revision'] = subprocess.check_output(
                ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True,
            ).strip()
            manifest[label + '_status'] = subprocess.check_output(
                ['git', '-C', str(checkout), 'status', '--short'], text=True,
            )
    if (source / 'base-revision.txt').exists():
        manifest['plugin_base_revision'] = (source / 'base-revision.txt').read_text().strip()
    (run / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    server = monitor = None
    service_pid = None
    status = 1
    try:
        with (run / 'server.log').open('w') as log:
            launch = SERVER
            if args.native_profile:
                entry = run / 'server-entry.sh'
                entry.write_text('#!/usr/bin/env bash\nexec ' + shlex.join(SERVER) + '\n')
                launch = ['/usr/local/corex-4.5.0/bin/ixsys', '-t', 'cuda',
                          '--profile-from-start', 'off', '--print-kernel-args',
                          '-o', str(run / 'native-trace.json'), 'bash', str(entry)]
            (run / 'launch-command.json').write_text(json.dumps(launch, indent=2))
            server = subprocess.Popen(launch, cwd='/workspace', env=env,
                                      stdout=log, stderr=subprocess.STDOUT,
                                      stdin=subprocess.DEVNULL, start_new_session=True)
        (run / 'server.pid').write_text(str(server.pid) + '\n')
        monitor = subprocess.Popen(
            ['bash', str(ROOT / 'scripts/monitor_gpu.sh'), str(server.pid), str(run / 'gpu.csv')],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        deadline = time.monotonic() + 600
        while True:
            if server.poll() is not None:
                raise RuntimeError('server exited before ready')
            try:
                models = request('/v1/models')
                break
            except (OSError, ValueError):
                if time.monotonic() > deadline:
                    raise TimeoutError('service readiness timeout')
                time.sleep(3)
        (run / 'models.json').write_text(json.dumps(models, indent=2))
        if args.require_log_marker and args.require_log_marker not in (run / 'server.log').read_text():
            raise RuntimeError('required installation marker absent: ' + args.require_log_marker)
        if args.native_profile:
            # Stop only this launch's vLLM child so ixsys can flush and exit.
            pending = [server.pid]
            while pending:
                pid = pending.pop()
                try:
                    proc = Path('/proc') / str(pid)
                    argv = (proc / 'cmdline').read_bytes().split(b'\0')
                    if any(Path(value.decode()).name == 'vllm'
                           for value in argv[:2]):
                        service_pid = pid
                        break
                    children = (proc / f'task/{pid}/children').read_text().split()
                    pending.extend(map(int, children))
                except (OSError, ValueError):
                    continue
            if service_pid is None:
                raise RuntimeError('cannot identify owned vLLM child under ixsys')
            (run / 'service.pid').write_text(str(service_pid) + '\n')
        smoke_payload = {
            'model': 'minicpm', 'prompt': 'Explain what an inference engine does.',
            'temperature': 0, 'seed': 71, 'max_tokens': 32,
        }
        if args.smoke_only:
            smoke_payload.update(logprobs=2, return_token_ids=True)
        (run / 'smoke-request.json').write_text(json.dumps(smoke_payload, indent=2))
        for repeat in range(args.smoke_repeats):
            smoke = request('/v1/completions', smoke_payload, timeout=120)
            if not smoke.get('choices'):
                raise RuntimeError('invalid smoke response')
            name = 'smoke.json' if repeat == 0 else f'smoke-r{repeat + 1}.json'
            (run / name).write_text(json.dumps(smoke, indent=2))
        if args.smoke_only:
            status = 0
            return status
        commands = []
        # Separate cases: no overlapping clients or profiler. The decode lengths
        # cross at least one 16-token KV block boundary.
        cases = [
            ('4k', 4096, 32, 16, 16), ('16k', 16384, 16, 8, 8),
        ]
        if args.context_long_screen:
            cases = [('context-16k-long', 16384, 1024, 64, 32)]
        elif args.context_screen:
            cases = [('context-16k', 16384, 128, 64, 32)]
        elif args.native_profile:
            # 32 output tokens can finish most requests before prefill admission
            # drains, leaving no >=16-request pure-decode window to capture.
            cases = [('native-4k', 4096, 128, 64, 64)]
        elif args.decode_screen or args.host_profile:
            cases = [('decode-4k', 4096, 128, 64, 64)]
        for offset, (label, length, output, concurrency, prompts) in enumerate(cases):
            command = ['python3', str(answer_client), '--requests', str(args.answer_requests.resolve()),
                       '--run-dir', str(run / label), '--variant', args.answer_variant,
                       '--server-log', str(run / 'server.log')]
            commands.append(command)
            (run / 'load-commands.json').write_text(json.dumps(commands, indent=2))
            (run / f'cpu-before-{label}.json').write_text(json.dumps(cpu_state()))
            snapshot_metrics(run, 'before-' + label)
            subprocess.run(command, env=env, cwd='/workspace', check=True,
                           timeout=900 if args.context_long_screen else 240)
            snapshot_metrics(run, 'after-' + label)
            (run / f'cpu-after-{label}.json').write_text(json.dumps(cpu_state()))
        status = 0
    finally:
        if server is not None and server.poll() is None:
            if service_pid is not None:
                try:
                    os.kill(service_pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
            else:
                os.killpg(server.pid, signal.SIGTERM)
            try:
                server.wait(timeout=45)
            except subprocess.TimeoutExpired:
                os.killpg(server.pid, signal.SIGKILL)
                server.wait(timeout=10)
        if monitor is not None:
            monitor.terminate()
            monitor.wait(timeout=10)
        if args.native_profile:
            validation = {'valid': False}
            try:
                events = [json.loads(line) for line in
                          (run / 'native-events.jsonl').read_text().splitlines()]
                stops = [event for event in events if event['event'] == 'stop']
                with sqlite3.connect('file:' + str(run / 'native-trace.json') +
                                     '?mode=ro', uri=True) as trace:
                    validation['kernel_rows'] = trace.execute(
                        'SELECT COUNT(*) FROM cuda_kernel_data').fetchone()[0]
                validation['stops'] = stops
                validation['valid'] = bool(
                    len(stops) == 1 and stops[0]['result'] == 0 and
                    len(stops[0]['executed_shapes']) == 5 and
                    all(n >= 16 and n == total and maximum == 1 for
                        n, total, maximum in stops[0]['executed_shapes']) and
                    validation['kernel_rows'] > 0)
            except (OSError, ValueError, KeyError, sqlite3.Error) as error:
                validation['error'] = repr(error)
            (run / 'native-validation.json').write_text(json.dumps(validation, indent=2))
            if not validation['valid'] and status == 0:
                status = 2
        if args.host_profile:
            validation = {'valid': False, 'kind': 'diagnostic_only_not_score'}
            try:
                summary = json.loads((run / 'host-window-summary.json').read_text())
                validation.update(
                    complete=summary.get('complete'),
                    profiled_steps=summary.get('profiled_steps'),
                    valid=bool(summary.get('complete') and
                               summary.get('profiled_steps') == 8 and
                               (run / 'host-window.pstats').stat().st_size > 0),
                )
            except (OSError, ValueError) as error:
                validation['error'] = repr(error)
            (run / 'host-validation.json').write_text(json.dumps(validation, indent=2))
            if not validation['valid'] and status == 0:
                status = 2
        (run / 'exit-code').write_text(str(status) + '\n')
        (run / 'finished-at.txt').write_text(utc() + '\n')
        (run / 'cpu-final.json').write_text(json.dumps(cpu_state()))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
