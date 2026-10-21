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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('run_dir', type=Path)
    parser.add_argument('--source-dir', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=721001)
    parser.add_argument('--smoke-only', action='store_true')
    parser.add_argument('--smoke-repeats', type=int, choices=range(1, 5), default=1)
    parser.add_argument('--native-profile', action='store_true')
    args = parser.parse_args()
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
    paths = [
        source / 'vllm_fl/worker/model_runner.py',
        source / 'vllm_fl/patches/biv150_runtime.py',
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/worker/block_table.py'),
        Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py'),
        Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_attention_helpers.py'),
        Path('/usr/local/lib/python3.12/site-packages/flag_gems/runtime/backend/_iluvatar/ops/mm.py'),
        Path('/workspace/MiniCPM5-2B/config.json'),
        Path('/workspace/MiniCPM5-2B/generation_config.json'),
    ]
    paths.extend(sorted((source / 'vllm_fl/patches').glob('biv150*py')))
    manifest = {
        'kind': 'short serial diagnostic; not official performance',
        'started_utc': utc(), 'server_command': SERVER, 'source_dir': str(source),
        'seed': args.seed, 'cpu_before': cpu_state(),
        'smoke_only': args.smoke_only, 'smoke_repeats': args.smoke_repeats,
        'native_profile': args.native_profile,
        'packages': {name: importlib.metadata.version(name) for name in
                     ['vllm', 'vllm-plugin-fl', 'torch', 'transformers', 'flag-gems']},
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
        if args.native_profile:
            cases = [('native-4k', 4096, 32, 64, 64)]
        for offset, (label, length, output, concurrency, prompts) in enumerate(cases):
            command = ['bash', str(ROOT / 'scripts/run_diagnostic_load.sh'),
                       str(run / label), label, str(length), str(output),
                       str(concurrency), str(prompts), str(args.seed + offset)]
            commands.append(command)
            (run / 'load-commands.json').write_text(json.dumps(commands, indent=2))
            (run / f'cpu-before-{label}.json').write_text(json.dumps(cpu_state()))
            subprocess.run(command, env=env, cwd='/workspace', check=True, timeout=240)
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
        (run / 'exit-code').write_text(str(status) + '\n')
        (run / 'finished-at.txt').write_text(utc() + '\n')
        (run / 'cpu-final.json').write_text(json.dumps(cpu_state()))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
