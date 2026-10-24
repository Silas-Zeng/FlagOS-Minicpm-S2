#!/usr/bin/env python3
"""封存当前446组合官方原件；不启动模型，不重跑原CSV验证或准确率。"""
import argparse
import ast
import runpy
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
BLOBS_SHA = '340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e'
MANIFEST_SHA = '0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4'
TREE = '5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
DRIVER_SHA = '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
BENCHMARK_SHA = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
LAUNCH_SHA = '871790d6ef6abee9c0d114be2538be3d9883a6db8b496e59c2c5d9d5ab31f166'


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
    # 方法覆盖独立记录：未命中/拒绝/坏marker不阻止原件封存，也不冒充全程覆盖。
    selected, normalized, rejected, malformed = [], [], [], []
    for line in log.splitlines():
        pid = re.search(r'EngineCore[^\s()]* pid=(\d+)', line)
        for marker, destination in (
            ('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', selected),
            ('BIV150_PREFILL_NORMALIZATION_SELECTED ', normalized),
            ('BIV150_COMPUTE_ORDER_SCOPE_REJECTED ', rejected)):
            if marker not in line:
                continue
            try:
                if destination is normalized:
                    value = ast.literal_eval(line.split(marker, 1)[1])
                    if not pid or not isinstance(value, tuple) or len(value) != 3 or not all(type(v) is int and v > 0 for v in value):
                        raise ValueError('Normalization marker几何/PID不完整')
                    destination.append(dict(pid=int(pid.group(1)), shape=list(value)))
                    continue
                value = json.loads(line.split(marker, 1)[1])
                if not pid or not isinstance(value, dict) or value.get('pid') != int(pid.group(1)):
                    raise ValueError('marker PID不匹配')
                if destination is selected and not (value.get('original_model_forward_returned') is True
                        and value.get('runtime_mode') == 'NONE' and value.get('sampler_rows') == value.get('N')
                        and 0 < value.get('Dprefix', 0) < value.get('Dall', 0)
                        and value.get('outside') == value['Dall'] - value['Dprefix']):
                    raise ValueError('P marker资格不完整')
                destination.append(value)
            except Exception as error:
                malformed.append(dict(marker=marker, error_type=type(error).__name__, line=line))
    p_valid = bool(selected) and all(value['pid'] in {item['pid'] for item in normalized}
        for value in selected) and not (rejected or malformed)
    return dict(source_count=446, p_first_selected=selected, normalization_selected=normalized,
        scope_rejected=rejected, malformed_markers=malformed, actual_p_observed=p_valid,
        p_coverage_status=('actual_P_observed' if p_valid else
            'invalid_or_rejected_marker' if selected or rejected or malformed else 'not_observed'),
        limitations=['FIRST_SELECTED只记首命中，不是完整路径计数、所有题目覆盖或GPU完成ACK。',
                     '覆盖与原官方CSV完成分别记录，缺命中不改写结果或补造成功。'])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    args = parser.parse_args()
    if args.run_id != '20261023T144620Z-current-main-compute-order-official':
        raise ValueError('只接受固定144620的446组合official run ID')
    parent = ROOT / 'official'
    run, control = parent / args.run_id, parent / (args.run_id + '-control')
    archive = parent / (args.run_id + '.tgz')
    outputs = [run / 'postflight-full.json', run / 'official-seal-review.json',
        run / 'method-coverage.json', control / 'evidence-seal.json', control / 'seal_combined_official.py',
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
    launcher = control / 'launch_combined_official.py'
    if (sha(launcher) != LAUNCH_SHA or sha(control / 'candidate-git-blobs.json') != BLOBS_SHA
            or sha(control / 'candidate-manifest.json') != MANIFEST_SHA):
        raise RuntimeError('冻结446官方launcher/Git身份变化')
    namespace = runpy.run_path(str(launcher))  # 仅stdlib/定义；绝不运行main或准确率审阅。
    blobs, candidate, purpose = (read(control / name) for name in
        ('candidate-git-blobs.json', 'candidate-manifest.json', 'purpose.json'))
    source = Path(manifest['source_dir']).resolve(strict=True)
    if (source != namespace['SOURCE'] or source.is_symlink() or len(expected) != 446 or len(blobs) != 446
            or namespace['TREE'] != TREE or candidate['target_tree'] != TREE
            or candidate['target_blob_count'] != 446 or read(control / 'source-git-blobs.json') != blobs
            or purpose['source'] != str(source) or purpose['source_count'] != 446
            or purpose['base_commit'] != namespace['COMMIT'] or purpose['tree'] != TREE
            or namespace['source_maps'](source) != (blobs, expected)
            or namespace['source_maps'](control / 'plugin-source') != (blobs, expected)):
        raise RuntimeError('不是冻结同446完整Git blobs/modes/link及live/control字节')
    accuracy = read(control / 'accuracy-reference.json')
    if (accuracy != purpose['accuracy_reference'] or accuracy['run'] != namespace['ACCURACY_NAME']
            or accuracy['accuracy_gate'] != 'pass' or accuracy['samples'] != 105
            or accuracy['source_count'] != 446 or accuracy['tree'] != TREE):
        raise RuntimeError('非本轮同446已通过105题的启动附证')
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
            or sha(launcher) != LAUNCH_SHA):
        raise RuntimeError('非冻结原official接线')
    command = ['python3', str(ROOT / 'scripts/run_official_gate.py'), str(run),
        '--source-dir', str(source), '--require-log-marker', 'BIV150_PREFILL_NORMALIZATION_INSTALL',
        '--database', '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db']
    if shlex.split((control / 'command.txt').read_text(encoding='utf-8')) != command:
        raise RuntimeError('原官方owner argv或Normalization安装门变化')
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
    save(run / 'method-coverage.json', dict(run_id=args.run_id, **markers))
    save(run / 'postflight-full.json', post)
    save(run / 'official-seal-review.json', {'status': 'sealed_existing_completed_official',
        'validation_reexecuted': False, 'original_validation': validation, 'method_coverage': markers,
        'installed_live_sha256': installed_live,
        'finite_present': False, 'accuracy': accuracy,
        'limits': ['方法覆盖单独记录，不将缺P命中或scope拒绝伪装成已覆盖；不重跑准确率。',
            '本脚本只封存绝对结果，不比较跨容量/DB/源的收益。']})
    save(control / 'seal-command.json', {'argv': sys.argv, 'models_or_tests_started': False})
    with (control / 'seal_combined_official.py').open('xb') as stream:
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
