"""固定PR15源码包→原35d准确率owner；不改评测、不安装包或修改已有源码。"""
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
COMMIT = '638c4ac0f07ed98e4476a5971c849630d9cdd580'
BASE = '2b59d7612666452f7a1b8cca0f634af0b5e887b8'
TREE = 'd6a9597c34c29d06613562a40a95b91f70eeb70f'
ARCHIVE_SHA = 'a61e717f7d3623d558008d621e4e9b95b7c05f571e2191c79dd31541be44f25a'
MAP_SHA = '411f2a68b9220cc05a53719e1e8dd6c6d90171eb04303bbe7976b4ec7a2c2dcf'
RUNNER = 'vllm_fl/worker/model_runner.py'
RUNNER_SHA = '195cc806a127ab4e43b6838aaee70ef70a4d8b2f02dd38df6f0e815374202b88'
HELPER = 'vllm_fl/patches/biv150_cpu_metadata.py'
HELPER_SHA = '0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f'
SCRIPTS = {
    'run_accuracy_gate.py': '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54',
    'run_math500_level3.sh': '6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4',
    'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}


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
    if len(entries) != 432 or tree_oid(entries) != BASE or entries[RUNNER]['sha'] != 'b5b867ac5ddc0efa7cef1205f603d4c39b34d80e':
        raise ValueError('原main完整Git tree不符')
    entries[RUNNER] = dict(mode='100644', sha='08220acfc4564f68263a5cde31c08cdd42a4e5a2')
    if tree_oid(entries) != TREE:
        raise ValueError('替runner后不是PR15发布tree')
    return entries


def checked_members(archive, entries, source):
    if sha(archive.read_bytes()) != ARCHIVE_SHA:
        raise ValueError('不是冻结的PR15 tarball')
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
        raise ValueError('tar未覆盖完整PR15树')
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
    p.add_argument('--source-dir', type=Path, default=ROOT / 'code/pr15-computed-h2d-638c4ac0')
    p.add_argument('--check-only', action='store_true', help='仅CPU核冻结tar全部blob/tree，不解包、不启动')
    args = p.parse_args()
    source = args.source_dir.resolve()
    entries = expected_tree()
    members = checked_members(args.archive.resolve(strict=True), entries, source)
    if args.check_only:
        print(json.dumps(dict(status='fixed_PR15_tar_tree_verified_CPU_only', commit=COMMIT, tree=TREE, files=len(entries))))
        return
    if source != ROOT / 'code/pr15-computed-h2d-638c4ac0' or source.exists():
        raise ValueError('只允许指定全新独立source目录')
    for name, pin in SCRIPTS.items():
        if sha((ROOT / 'scripts' / name).read_bytes()) != pin:
            raise ValueError('原accuracy owner/官方脚本变化：' + name)
    source.mkdir(parents=True, exist_ok=False)
    with tarfile.open(args.archive, 'r:gz') as tar:
        tar.extractall(source, members=members, filter='data')
    blobs, hashes = source_maps(source)
    if blobs != entries or hashes[RUNNER] != RUNNER_SHA or hashes[HELPER] != HELPER_SHA:
        raise ValueError('解包源码与完整PR15 tree不符')
    run = ROOT / 'accuracy' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-pr15-computed-h2d')
    control = run.with_name(run.name + '-control')
    control.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, control / 'plugin-source', symlinks=True)
    if source_maps(control / 'plugin-source') != (blobs, hashes) or source_maps(source) != (blobs, hashes):
        raise ValueError('原源或control完整归档变化')
    save(control / 'source-sha256.json', hashes)
    save(control / 'source-git-blobs.json', blobs)
    shutil.copyfile(__file__, control / 'launch_pr15_accuracy.py')
    shutil.copyfile(HERE / 'main-tree.json', control / 'main-tree.json')
    save(control / 'purpose.json', dict(kind='PR15实际提交的独立完整准确率，尚未通过',
        source=str(source), source_count=len(hashes), commit=COMMIT, tree=TREE,
        archive_sha256=ARCHIVE_SHA, runner_sha256=RUNNER_SHA, metadata_helper_sha256=HELPER_SHA,
        removed_environment_names=['BIV150_FINITE_GROWTH_ADMISSION', 'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'],
        limits=['复用旧方法/短pair，不继承旧QGQA准确率或性能', 'SQL只作启动门；需同Engine原metadata FIRST_SELECTED和105题原判卷',
                '本轮仅BI-V150，不能代C500准确率；原35d独占/DB/cleanup不变']))
    command = ['python3', str(ROOT / 'scripts/run_accuracy_gate.py'), str(run), '--source-dir', str(source),
        '--require-log-marker', 'BIV150_SQL_REFLECTION_INSTALLED', '--database',
        '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db']
    env = os.environ.copy()
    env.pop('BIV150_FINITE_GROWTH_ADMISSION', None)
    env.pop('BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR', None)
    (control / 'command.txt').write_text(shlex.join(command) + '\n', encoding='utf-8')
    save(control / 'scripts-sha256.json', SCRIPTS)
    with (control / 'runner.log').open('x') as log:
        job = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (control / 'runner.pid').write_text(str(job.pid) + '\n')
    print(json.dumps(dict(run=str(run), control=str(control), source=str(source), runner_pid=job.pid, commit=COMMIT)))


if __name__ == '__main__':
    main()
