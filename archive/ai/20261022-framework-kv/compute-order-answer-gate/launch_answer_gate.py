"""单侧辅助答案门薄接线；原bc51派生owner持锁和清理，不自动pair。"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import socket
import subprocess

ROOT = Path('/workspace/experiments/minicpm-s2')
OWNER_SHA = '9b6453dff7d77deb88cf164a4f7736a99845239216e8de3a8fdb4f8501420cda'
CLIENT_SHA = '6dafbfbee4e3f91343ce28ecfefd55a48202e701d718184d8036556dff722c12'
CASES = {
    'baseline': ('q-gqa-kv-swap-20261022T213134Z',
        '20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long', 422,
        '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
        'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'),
    'candidate': ('compute-order-20261023T060425Z',
        '20261023T060425Z-compute-order-candidate-context16k', 423,
        '6cf2e1d7e3084d95e0fd8db23ceaa426c5c5ab6ff887dffcd8f036e60b98a7b9',
        'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink() and (not path.resolve().is_file() or not path.resolve().is_relative_to(folder)):
            raise ValueError('外部/目录链接')
        if path.is_file():
            result[rel.as_posix()] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('variant', choices=tuple(CASES))
    parser.add_argument('--requests', type=Path, required=True)
    args = parser.parse_args()
    assets = Path(__file__).resolve().parent
    requests = args.requests.resolve(strict=True)
    if not requests.is_relative_to(ROOT):
        raise ValueError('共享请求必须在实验目录内')
    for path, pin in {
        assets / 'run_answer_gate.py': OWNER_SHA,
        assets / 'run_answer_load.py': CLIENT_SHA,
        ROOT / 'scripts/snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
    }.items():
        if pin is None or sha(path) != pin:
            raise ValueError('未冻结/变化的owner、client或DB快照工具')
    # 只运行client的纯数据校验函数，不发HTTP或加载框架。
    import run_answer_load
    _, requests_sha, request_manifest = run_answer_load.load_requests(requests)
    source_name, reference_name, count, map_sha, runner_sha = CASES[args.variant]
    source = ROOT / 'code' / source_name
    reference = ROOT / 'framework' / (reference_name + '-control') / 'source-sha256.json'
    expected = json.loads(reference.read_text())
    if sha(reference) != map_sha or len(expected) != count or mapping(source) != expected:
        raise ValueError('实际冻结完整源/map变化')
    if expected['vllm_fl/worker/model_runner.py'] != runner_sha:
        raise ValueError('runner不符')
    query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu',
        '--format=csv,noheader,nounits'], text=True)
    table = subprocess.check_output(['ixsmi'], text=True)
    if query.strip() != '68, 0' or 'No running processes found' not in table:
        raise ValueError('设备未清理')
    for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            if sock.connect_ex((host, 9031)) == 0:
                raise ValueError('9031占用')
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'framework' / (stamp + '-compute-order-answer-' + args.variant)
    control = run.with_name(run.name + '-control')
    if run.exists():
        raise ValueError('旧run不得覆盖')
    control.mkdir()
    for name in ('launch_answer_gate.py', 'run_answer_gate.py', 'run_answer_load.py', 'prepare_requests.py'):
        shutil.copyfile(assets / name, control / name)
    shutil.copyfile(reference, control / 'source-sha256.json')
    shutil.copyfile(requests, control / 'requests.jsonl')
    shutil.copyfile(request_manifest, control / 'requests.jsonl.manifest.json')
    shutil.copytree(source, control / 'plugin-source', ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
    if mapping(control / 'plugin-source') != expected or mapping(source) != expected:
        raise ValueError('源归档/原源变化')
    (control / 'purpose.json').write_text(json.dumps(dict(
        kind='真实计算序辅助答案门；非官方accuracy/逐层或RNG逐位证明', variant=args.variant,
        source=str(source), source_count=count, reference=str(reference), requests_sha256=requests_sha,
        fixed_case='32×16384 token IDs/128out/concurrency64/temp1/top_p0.95/ignoreEOS/no request seed',
        limits=['两侧必须共享同一请求SHA；基线自己不过则门无判别力',
                'candidate必须答案负载内实际Dprefix/outside命中，安装/旧marker不足',
                '只核首完整answer tag；不以本门用时作性能收益']), ensure_ascii=False, indent=2) + '\n')
    with (control / 'db-before.log').open('x') as output:
        subprocess.run(['python3', str(ROOT / 'scripts/snapshot_tuning_db.py'), '--database',
            '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db',
            '--output', str(control / 'db-before')], stdout=output, stderr=subprocess.STDOUT, check=True)
    (control / 'q-hoist-artifacts').mkdir()
    command = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION', 'BIV150_KV_VERIFY_RESTORE=0',
        'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR=' + str(control / 'q-hoist-artifacts'),
        'python3', str(assets / 'run_answer_gate.py'), str(run), '--source-dir', str(source),
        '--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED',
        '--answer-requests', str(requests), '--answer-variant', args.variant]
    for name in ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR'):
        if name in os.environ:
            raise ValueError('不得夹带profiler')
    (control / 'command.txt').write_text(shlex.join(command) + '\n')
    with (control / 'runner.log').open('x') as output:
        child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=output,
                                 stderr=subprocess.STDOUT, start_new_session=True)
    (control / 'runner.pid').write_text(str(child.pid) + '\n')
    print(json.dumps(dict(run=str(run), control=str(control), source=str(source),
                         runner_pid=child.pid, variant=args.variant, requests_sha256=requests_sha)))


if __name__ == '__main__':
    main()
