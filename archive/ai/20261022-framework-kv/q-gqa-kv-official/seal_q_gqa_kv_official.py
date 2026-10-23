#!/usr/bin/env python3
"""封存固定QGQA+原KV422已结束官方任务；不启动模型、不重跑CSV验证或准确率。"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shlex
import socket
import subprocess
import sys
import tarfile

ROOT = Path('/workspace/experiments/minicpm-s2')
MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
DRIVER_SHA = '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
BENCHMARK_SHA = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
LAUNCH_SHA = 'c720998168374ea4b8a96f89b6aad010b3b26a56dc291e8f56324a71c9465f02'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def mapping(folder):
    return {p.relative_to(folder).as_posix(): sha(p) for p in folder.rglob('*')
        if p.is_file() and not any(x in ('.git', '__pycache__') for x in p.relative_to(folder).parts)
        and p.suffix not in ('.pyc', '.pyo')}


def actual_markers(log):
    results = {}
    for name, marker, counter in (
        ('Q', 'BIV150_Q_FRAGMENT_SERVICE_FIRST_ACTUAL_EXECUTE_SELECTED ', 'selected_calls_in_execute'),
        ('GQA', 'BIV150_Q_GQA_FIRST_ACTUAL_EXECUTE_SELECTED ', 'gqa_calls_in_execute')):
        values = []
        for line in log.splitlines():
            if marker not in line:
                continue
            prefix, payload = line.split(marker, 1)
            value = json.loads(payload)
            pid = re.search(r'EngineCore[^\s()]* pid=(\d+)', prefix)
            if not (pid and int(pid.group(1)) == value.get('pid')
                    and value.get('actual_execute') is True
                    and value.get('complete_step_return') is True
                    and value.get('num_requests', 0) >= 2 and value.get('scheduled_tokens', 0) > 0
                    and value.get(counter, 0) > 0
                    and value.get('gqa_python_count_excludes_graph_replay') is True):
                raise RuntimeError('真实成功execute marker不完整: ' + name)
            values.append(value)
        if len(values) != 1:
            raise RuntimeError('需要唯一实际execute marker: ' + name)
        results[name] = values[0]
    if results['Q']['pid'] != results['GQA']['pid']:
        raise RuntimeError('Q/GQA不在同一Engine')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    args = parser.parse_args()
    if args.run_id != '20261022T231746Z-q-gqa-kv-swap-official':
        raise ValueError('只接受固定231746 QGQA+KV official run ID')
    parent = ROOT / 'official'
    run, control = parent / args.run_id, parent / (args.run_id + '-control')
    archive = parent / (args.run_id + '.tgz')
    outputs = [run / 'postflight-full.json', run / 'official-seal-review.json',
        control / 'evidence-seal.json', control / 'seal_q_gqa_kv_official.py',
        control / 'seal-command.json', archive]
    if any(path.exists() for path in outputs):
        raise FileExistsError('已有封存输出；保留原件，不覆盖/重复封包')
    result, manifest = read(run / 'result.json'), read(run / 'manifest.json')
    validation = result['validation']
    if ((run / 'exit-code').read_text(encoding='utf-8').strip() != '0'
            or result.get('exit_code') != 0 or result.get('cleanup_errors') != []
            or result.get('status') != 'official_benchmark_completed'
            or result.get('benchmark_completed') is not True or result.get('benchmark_exit_code') != 0
            or validation.get('complete') is not True or validation.get('raw_rows') != 8
            or validation.get('summary_rows') != 2 or validation.get('runs_per_case') != 4
            or validation.get('skip_first') != 1
            or validation.get('retained_raw_metrics_checked') is not True
            or validation.get('summary_means_verified') is not True
            or validation.get('summary_rewritten') is not False
            or [v.get('case') for v in validation.get('verified_cases', [])]
                != [[4096, 1024, 64, 256], [16384, 1024, 64, 128]]
            or any(v.get('retained_runs') != [2, 3, 4] for v in validation['verified_cases'])):
        raise RuntimeError('仅封存原driver已完成且验证八行/两摘要/第2–4轮均值的任务')
    expected = read(control / 'source-sha256.json')
    if sha(control / 'source-sha256.json') != MAP_SHA or len(expected) != 422:
        raise RuntimeError('不是冻结422完整map')
    source = Path(manifest['source_dir']).resolve(strict=True)
    if source != ROOT / 'code/q-gqa-kv-swap-20261022T213134Z':
        raise ValueError('非本次固定QGQA+KV422 source')
    if (mapping(source) != expected or mapping(control / 'plugin-source') != expected
            or 'vllm_fl/patches/biv150_finite_growth_admission.py' in expected):
        raise RuntimeError('live/control完整源变化或混入finite')
    failures = [k for k, v in manifest['sha256'].items()
        if not (run / 'source' / k).is_file() or sha(run / 'source' / k) != v]
    failures += ['plugin/' + k for k, v in expected.items()
        if (run / 'source/plugin' / k).exists() and sha(run / 'source/plugin' / k) != v]
    # 小时级运行后核对原归档的实际安装文件；只读，不触发导入或额外模型测试。
    installed_live = {k: sha(Path('/usr/local/lib/python3.12/site-packages') / k.removeprefix('installed/'))
        for k in manifest['sha256'] if k.startswith('installed/')}
    if any(value != manifest['sha256'][key] for key, value in installed_live.items()):
        raise RuntimeError('运行期间原installed源码发生变化')
    pins = {'run_official_gate.py': DRIVER_SHA, 'run_accuracy_gate.py': COMMON_SHA,
        'benchmark_throughput_serve.py': BENCHMARK_SHA}
    if failures or any(sha(run / 'source' / k) != v for k, v in pins.items()):
        raise RuntimeError('原driver/benchmark或manifest归档字节变化: ' + repr(failures))
    # 原driver已经验证CSV；此处只确认那份验证覆盖的字节仍在，不再执行validate_outputs。
    if any(not (run / k).is_file() or sha(run / k) != v for k, v in validation['sha256'].items()):
        raise RuntimeError('原CSV验证之后结果文件变化')
    if (manifest.get('profiler') is not False or manifest.get('smoke_requests') != 0
            or manifest.get('repetitions') != {'RUNS': 4, 'SKIP_FIRST': 1}
            or sha(control / 'launch.sh') != LAUNCH_SHA):
        raise RuntimeError('非冻结原official接线')
    command = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION', 'BIV150_KV_VERIFY_RESTORE=0',
        'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=' + str(control / 'q-hoist-artifacts'),
        'python3', str(ROOT / 'scripts/run_official_gate.py'), str(run), '--source-dir', str(source),
        '--database', '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db',
        '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']
    if shlex.split((control / 'command.txt').read_text(encoding='utf-8')) != command:
        raise RuntimeError('官方owner命令/VERIFY0/finite unset/Q ENV变化')
    log = (run / 'server.log').read_text(encoding='utf-8', errors='replace')
    if 'BIV150_FINITE_GROWTH_ADMISSION_' in log:
        raise RuntimeError('出现不应有的finite安装/执行')
    markers = actual_markers(log)
    for phase in ('before', 'after'):
        if read(run / ('database-' + phase) / 'manifest.json').get('status') != 'complete':
            raise RuntimeError('缺少完整原DB快照: ' + phase)
    ports = {}
    for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            ports[host] = sock.connect_ex((host, 9031)) != 0
    query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu',
        '--format=csv,noheader,nounits'], text=True)
    table = subprocess.check_output(['ixsmi'], text=True)
    pids = {int(p.read_text(encoding='utf-8')) for p in
        (control / 'runner.pid', run / 'server.pid', run / 'benchmark.pid')}
    pids.update(map(int, re.findall(r'EngineCore[^\s()]* pid=(\d+)', log)))
    states = {}
    for pid in sorted(pids):
        status = Path('/proc') / str(pid) / 'status'
        states[str(pid)] = status.read_text(encoding='utf-8') if status.exists() else None
    post = {'utc': datetime.now(timezone.utc).isoformat(), 'source_count': len(expected),
        'source_failures': [], 'archived_source_failures': [], 'ports_closed': ports,
        'query': query, 'ixsmi': table, 'owned_process_status': states}
    if (not all(ports.values()) or query.strip() != '68, 0'
            or 'No running processes found' not in table
            or not all(s is None or '\nState:\tZ ' in s for s in states.values())):
        raise RuntimeError('原owner清理后态不通过: ' + json.dumps(post))
    save(run / 'postflight-full.json', post)
    save(run / 'official-seal-review.json', {'status': 'sealed_existing_completed_official',
        'validation_reexecuted': False, 'original_validation': validation, 'actual_markers': markers,
        'installed_live_sha256': installed_live,
        'finite_present': False, 'accuracy': '20261022T215836Z-q-gqa-kv-swap: 103/105 separately recorded; not rerun here',
        'limits': ['Python实际marker不覆盖graph replay，不是额外GPU完成ACK。',
            '本脚本只封存绝对结果，不比较跨容量/DB/源的收益。']})
    save(control / 'seal-command.json', {'argv': sys.argv, 'models_or_tests_started': False})
    with (control / 'seal_q_gqa_kv_official.py').open('xb') as stream:
        stream.write(Path(__file__).read_bytes())
    files = {str(p.relative_to(parent)): sha(p) for d in (run, control)
        for p in sorted(d.rglob('*')) if p.is_file()}
    save(control / 'evidence-seal.json', {'utc': post['utc'], 'exit_code': 0, 'files': files,
        'sealer_sha256': sha(Path(__file__)), 'original_validation': validation})
    with tarfile.open(archive, 'x:gz') as package:
        package.add(run, arcname=run.name)
        package.add(control, arcname=control.name)
    print(json.dumps({'archive': str(archive), 'bytes': archive.stat().st_size,
        'sha256': sha(archive), 'sealed_files': len(files), 'raw_rows': 8, 'summary_rows': 2}))


if __name__ == '__main__':
    main()
