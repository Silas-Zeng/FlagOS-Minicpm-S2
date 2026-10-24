"""固定当前main完整Git树→原bc51短服务；不改生产源、SERVER或准确率。"""
import argparse
import copy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shlex
import shutil
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMIT = '3283672b92fa30f93f652b242193999836a95f88'
BASE = 'a6e53d5219addc76700718880f86c33ab014b311'
TREE = 'a6e53d5219addc76700718880f86c33ab014b311'
ARCHIVE_SHA = '5cf712a06ae5098240d17e23c4c701615dcb9201a764878e707ffbd9c3e6b0a9'
MAP_SHA = '0f054156787c216c94f24062cf2ef865369a982ff32ff76a9638fa3bfb70e222'
RUNNER = 'vllm_fl/worker/model_runner.py'
RUNNER_SHA = '97c78bde864cb019fe38831804f08d201a950dd2cfafd15ac5ad77b90a93879f'
HELPER = 'vllm_fl/patches/biv150_prefill_normalized.py'
HELPER_SHA = '24a421fa25e0ce7e21b54deb760a5bc893d3899a86ced4849bd3f3bfab50ed42'
SCRIPTS = {'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9', 'run_diagnostic_load.sh': '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378', 'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2', 'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def oid(kind, raw):
    return hashlib.sha1(kind.encode() + b' ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def tree_oid(entries):
    root = {}
    for path, entry in entries.items():
        parts, node = path.split('/'), root
        for part in parts[:-1]:
            node = node.setdefault(part, {})
        node[parts[-1]] = (entry['mode'], entry['sha'])
    def walk(node):
        raw = b''
        for name in sorted(node, key=lambda x: (x + '/' if isinstance(node[x], dict) else x).encode()):
            value = node[name]
            mode, digest = ('40000', walk(value)) if isinstance(value, dict) else value
            raw += mode.encode() + b' ' + name.encode() + b'\0' + bytes.fromhex(digest)
        return oid('tree', raw)
    return walk(root)


def expected_tree():
    raw = (HERE / 'main-tree.json').read_bytes()
    doc = json.loads(raw)
    if sha(raw) != MAP_SHA or doc['sha'] != BASE or doc['truncated'] is not False:
        raise ValueError('原main完整tree身份变化')
    entries = {d['path']: dict(mode=d['mode'], sha=d['sha']) for d in doc['tree'] if d['type'] == 'blob'}
    if len(entries) != 445 or tree_oid(entries) != TREE or entries[RUNNER]['sha'] != '03d86ca175befbb0d9928f3b0b7fcffa9a4f8197':
        raise ValueError('当前main完整Git tree不符')
    return entries


def checked_members(archive, entries, source):
    if sha(archive.read_bytes()) != ARCHIVE_SHA:
        raise ValueError('不是冻结的当前main tarball')
    members, found, prefix = [], {}, None
    with tarfile.open(archive, 'r:gz') as tar:
        for item in tar.getmembers():
            path = PurePosixPath(item.name)
            if path.is_absolute() or '..' in path.parts or '\\' in item.name or not path.parts:
                raise ValueError('不安全tar成员路径')
            prefix = path.parts[0] if prefix is None else prefix
            if path.parts[0] != prefix:
                raise ValueError('tar有多个根目录')
            relative = PurePosixPath(*path.parts[1:])
            if not relative.parts:
                if not item.isdir():
                    raise ValueError('tar根不是目录')
                continue
            if item.isdir():
                if not any(name.startswith(relative.as_posix() + '/') for name in entries):
                    raise ValueError('tar含非Git树目录')
                continue
            name = relative.as_posix()
            if name in found or name not in entries or not (item.isfile() or item.issym()):
                raise ValueError('tar含重复/多余/特殊成员')
            mode = '120000' if item.issym() else ('100755' if item.mode & 0o111 else '100644')
            if item.issym():
                target = PurePosixPath(item.linkname)
                if target.is_absolute() or '\\' in item.linkname or not (source / relative.parent / item.linkname).resolve().is_relative_to(source):
                    raise ValueError('tar symlink越过新source')
                data = item.linkname.encode()
            else:
                with tar.extractfile(item) as stream:
                    data = stream.read()
            found[name] = dict(mode=mode, sha=oid('blob', data))
            if found[name] != entries[name]:
                raise ValueError('tar blob/mode不符：' + name)
            member = copy.copy(item)
            member.name = name
            members.append(member)
    if found != entries:
        raise ValueError('tar未覆盖完整当前main树')
    return members


def source_maps(source):
    blobs, hashes = {}, {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if any(x in ('.git', '__pycache__') for x in relative.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            if not path.resolve(strict=True).is_relative_to(source):
                raise ValueError('source symlink越界')
            data, mode = os.readlink(path).encode(), '120000'
        elif path.is_file():
            data, mode = path.read_bytes(), '100755' if path.stat().st_mode & 0o111 else '100644'
        else:
            continue
        blobs[relative.as_posix()] = dict(mode=mode, sha=oid('blob', data))
        hashes[relative.as_posix()] = sha(path.read_bytes())
    return blobs, hashes


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', required=True, type=Path)
    p.add_argument('--source-dir', type=Path, default=None)
    p.add_argument('--check-only', action='store_true', help='仅CPU核冻结tar全部blob/tree，不解包、不启动')
    args = p.parse_args()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    source = (args.source_dir or ROOT / 'code' / ('current-main-baseline-3283672b-'+stamp)).resolve()
    entries = expected_tree()
    members = checked_members(args.archive.resolve(strict=True), entries, source)
    if args.check_only:
        print(json.dumps(dict(status='fixed_current_main_tar_tree_verified_CPU_only', commit=COMMIT, tree=TREE, files=len(entries))))
        return
    if not source.is_relative_to(ROOT / 'code') or source.exists():
        raise ValueError('只允许指定全新独立source目录')
    for name, pin in SCRIPTS.items():
        if sha((ROOT / 'scripts' / name).read_bytes()) != pin:
            raise ValueError('原accuracy owner/官方脚本变化：' + name)
    source.mkdir(parents=True, exist_ok=False)
    with tarfile.open(args.archive, 'r:gz') as tar:
        tar.extractall(source, members=members, filter='data')
    blobs, hashes = source_maps(source)
    if blobs != entries or hashes[RUNNER] != RUNNER_SHA or hashes[HELPER] != HELPER_SHA:
        raise ValueError('解包源码与完整当前main tree不符')
    run = ROOT / 'framework' / (stamp + '-current-main-baseline-context16k')
    control = run.with_name(run.name + '-control')
    control.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, control / 'plugin-source', symlinks=True)
    if source_maps(control / 'plugin-source') != (blobs, hashes) or source_maps(source) != (blobs, hashes):
        raise ValueError('原源或control完整归档变化')
    save(control / 'source-sha256.json', hashes)
    save(control / 'source-git-blobs.json', blobs)
    shutil.copyfile(__file__, control / 'launch_current_main_baseline.py')
    shutil.copyfile(HERE / 'main-tree.json', control / 'main-tree.json')
    save(control / 'purpose.json', dict(kind='当前main完整代码的独立短服务基线；不是新准确率或优化收益',
        source=str(source), source_count=len(hashes), commit=COMMIT, tree=TREE,
        archive_sha256=ARCHIVE_SHA, runner_sha256=RUNNER_SHA, normalization_helper_sha256=HELPER_SHA,
        accuracy_reused='PR16已有完整105题102/105及原官方4K/16K证据；本轮不重跑',
        limits=['只完整main，不叠PR15或实验Q/KV/P资产', '安装marker不等实际选中，真实NORMALIZATION_SELECTED须本轮后验',
                '原bc51单锁/CPU quota观察/monitor/240s及清理不变；DB-after由原seal_framework_screen收集']))
    command = ['python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(source),
        '--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_PREFILL_NORMALIZATION_INSTALL']
    env = os.environ.copy()
    removed = {name: env.pop(name) for name in list(env) if name.startswith('BIV150_')
        or name in ('MINICPM_NATIVE_PROFILE_EVENTS','MINICPM_DECODE_GAP_RUN_DIR')}
    if env.get('VLLM_FL_BIV150_PREFILL_NORMALIZE','1') != '1':
        raise ValueError('不允许关闭已合入normalization')
    save(control / 'removed-experiment-environment.json', {'removed_names':sorted(removed)})
    quota_root=Path('/sys/fs/cgroup/cpu,cpuacct')
    quota={name:(quota_root/name).read_text() for name in ('cpu.cfs_quota_us','cpu.cfs_period_us','cpu.stat')}
    if int(quota['cpu.cfs_quota_us']) != 6*int(quota['cpu.cfs_period_us']):
        raise ValueError('不是当前6CPU quota，拒绝静默改变条件')
    save(control / 'cpu-before.json', quota)
    import socket
    ports={}
    for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
        with socket.socket(family,socket.SOCK_STREAM) as sock:
            sock.settimeout(2);ports[host]=sock.connect_ex((host,9031)) != 0
    gpu=subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
    gpu_table=subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi'],text=True)
    save(control / 'preflight.json', dict(ports_closed=ports,gpu=gpu,ixsmi=gpu_table,under_device_lock=False))
    if not all(ports.values()) or gpu.strip() != '68, 0' or 'No running processes found' not in gpu_table:
        raise RuntimeError('当前卡/端口非严格空闲；原bc51仍是唯一锁owner')
    shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py',control / 'snapshot_tuning_db.py')
    with (control / 'db-before.log').open('x') as output:
        subprocess.run(['python3',str(control / 'snapshot_tuning_db.py'),'--database',
            '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db','--output',str(control / 'db-before')],
            stdout=output,stderr=subprocess.STDOUT,check=True)
    (control / 'command.txt').write_text(shlex.join(command) + '\n', encoding='utf-8')
    save(control / 'scripts-sha256.json', SCRIPTS)
    with (control / 'runner.log').open('x') as log:
        job = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (control / 'runner.pid').write_text(str(job.pid) + '\n')
    print(json.dumps(dict(run=str(run), control=str(control), source=str(source), runner_pid=job.pid, commit=COMMIT)))


if __name__ == '__main__':
    main()
