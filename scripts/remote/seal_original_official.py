#!/usr/bin/env python3
"""结束后的只读核验与证据补全；不导入框架、不运行模型、不终止进程。"""
import datetime
import hashlib
import json
import pathlib
import shutil
import socket
import subprocess

ROOT = pathlib.Path('/workspace/experiments/minicpm-s2')
RUN = ROOT / 'official/20261021T122607Z-original-baseline'
CONTROL = pathlib.Path(str(RUN) + '-control')
SITE = pathlib.Path('/usr/local/lib/python3.12/site-packages')
ATTENTION = 'installed/vllm/v1/attention/ops/triton_unified_attention.py'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    if path.exists():
        raise FileExistsError('保留既有封存文件，禁止覆盖：' + str(path))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def main():
    result = json.loads((RUN / 'result.json').read_text())
    assert (RUN / 'exit-code').read_text().strip() == '0'
    assert result['exit_code'] == 0 and result['status'] == 'official_benchmark_completed'
    assert result['benchmark_completed'] and result['benchmark_exit_code'] == 0
    assert result['cleanup_errors'] == []
    manifest = json.loads((RUN / 'manifest.json').read_text())
    source = pathlib.Path(manifest['source_dir'])
    assert source == ROOT / 'code/official-base-20261021T091033Z'
    utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    archive_failures, live_failures, live_hashes = [], [], {}
    for name, expected in manifest['sha256'].items():
        archived = RUN / 'source' / name
        if not archived.is_file() or sha(archived) != expected:
            archive_failures.append(name)
        if name.startswith('plugin/'):
            live = source / name.removeprefix('plugin/')
        elif name.startswith('installed/'):
            live = SITE / name.removeprefix('installed/')
        elif name.startswith('dataset/'):
            live = pathlib.Path('/workspace/evalscope-datasets/math_500') / name.removeprefix('dataset/')
        elif name in ('config.json', 'generation_config.json'):
            live = pathlib.Path('/workspace/MiniCPM5-2B') / name
        elif name == 'benchmark_throughput_serve.py':
            live = pathlib.Path('/workspace/vllm-plugin-FL/benchmarks') / name
        else:
            live = ROOT / 'scripts' / name
        actual = sha(live) if live.is_file() else None
        live_hashes[name] = {'path': str(live), 'sha256': actual}
        if actual != expected:
            live_failures.append(name)
    text = [p.read_bytes() for p in (source / 'vllm_fl').rglob('*.py')]
    no_module = not (source / 'vllm_fl/patches/biv150_runtime.py').exists()
    no_hook = not any(b'biv150_runtime' in t for t in text)
    no_marker = not any(b'_biv150_minicpm_attention_patched_v2' in t for t in text)
    target = RUN / 'postflight-sources/triton_unified_attention.py'
    target.parent.mkdir(exist_ok=True)
    assert not target.exists()
    shutil.copyfile(SITE / ATTENTION.removeprefix('installed/'), target)
    review = {'utc': utc, 'stage': 'after_driver_cleanup',
              'manifest_sha256': sha(RUN / 'manifest.json'), 'source_dir': str(source),
              'archive_source_count': len(manifest['sha256']),
              'archive_source_failures': archive_failures, 'live_source_failures': live_failures,
              'live_sources': live_hashes, 'no_retained_module': no_module,
              'no_retained_hook': no_hook, 'no_retained_marker': no_marker,
              'installed_attention_sha256': live_hashes[ATTENTION]['sha256'],
              'archived_attention_sha256': sha(RUN / 'source' / ATTENTION),
              'postflight_attention_copy_sha256': sha(target)}
    save(RUN / 'source-review.json', review)
    save(CONTROL / 'final-source-review.json', review)
    ports = {}
    for family, host in [(socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')]:
        try:
            with socket.socket(family, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                ports[host] = sock.connect_ex((host, 9031)) != 0
        except OSError as error:
            ports[host] = str(error)
    query_command = ['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits']
    query = subprocess.check_output(query_command, text=True)
    rows = [line for line in query.splitlines() if line.strip()]
    assert len(rows) == 1
    memory, usage = [int(v.strip()) for v in rows[0].split(',')]
    process_checks = {}
    for label, path in [('runner', CONTROL / 'runner.pid'), ('server', RUN / 'server.pid'),
                        ('benchmark', RUN / 'benchmark.pid')]:
        pid = int(path.read_text().strip())
        process_checks[label] = {'pid': pid, 'exists': pathlib.Path('/proc/' + str(pid)).exists()}
    process_checks['EngineCore'] = {'pid': 166820, 'exists': pathlib.Path('/proc/166820').exists()}
    table = subprocess.check_output(['ixsmi'], text=True)
    post = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'port_9031_closed': all(value is True for value in ports.values()), 'ports': ports,
            'memory_used_mib': memory, 'gpu_utilization_percent': usage,
            'query_command': query_command, 'query': query, 'ixsmi': table,
            'no_running_device_processes': 'No running processes found' in table,
            'monitor_final_returncode': result['monitor_final_returncode'],
            'owned_processes': process_checks}
    save(RUN / 'postflight-full.json', post)
    assert not archive_failures and not live_failures and no_module and no_hook and no_marker, review
    assert sha(target) == 'bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0'
    assert post['port_9031_closed'] and memory <= 68 and usage == 0
    assert post['no_running_device_processes'], table
    assert all(not item['exists'] for item in process_checks.values()), process_checks
    print(json.dumps({'status': 'sealed', 'source_count': len(manifest['sha256']),
                      'postflight': post}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
