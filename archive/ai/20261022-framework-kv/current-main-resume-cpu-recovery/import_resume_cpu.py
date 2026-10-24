"""447 CPU诊断原件导入；复用唯一symlink材料化与全部seal门，允许exit1/未覆盖。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import re
from datetime import datetime
import sys
import tarfile

RUN = None  # root取得实际run ID后可仅锁此项。
LINK = 'vllm_fl/configs/moe/E=256,N=512,device_name=nvidia.json'
LINKNAME = 'E=256,N=512,device_name=nvidia,model=Qwen3.6-35B-A3B-H100.json'
LINK_BLOB = 'e0f0558233316d08efb00d75dce9ff2fd1a1f530'


def main():
    name, expected_size, expected_sha, count = sys.argv[1:5]
    controller_seal = sys.argv[5:] == ['--controller-seal']
    match = re.fullmatch(r'(\d{8}T\d{6}Z)-current-main-resume-cpu-context16k-long', name)
    assert match and (RUN is None or name == RUN) and not sys.argv[5:] and not controller_seal
    datetime.strptime(match.group(1), '%Y%m%dT%H%M%SZ')
    roots = [p for p in Path(__file__).resolve().parents
             if (p / 'experiments/registry.csv').is_file() and (p / 'AGENTS.md').is_file()]
    assert len(roots) == 1, '须唯一仓库根，拒绝猜测导入位置'
    root = roots[0]
    if os.name == 'nt' and not str(root).startswith('\\\\?\\'):
        root = Path('\\\\?\\' + str(root))
    parent = root / 'experiments/framework'
    archive = parent / (name + '.tgz')
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    assert archive.stat().st_size == int(expected_size)
    assert sha(archive.read_bytes()) == expected_sha
    seal_rel = name + ('-control/seal.json' if controller_seal else '-control/evidence-seal.json')
    source = PurePosixPath(name + '-control/plugin-source')
    link_rel = (source / LINK).as_posix()
    target_rel = (source / PurePosixPath(LINK).parent / LINKNAME).as_posix()
    git_rel = name + '-control/source-git-blobs.json'
    with tarfile.open(archive) as bundle:
        members, names = bundle.getmembers(), set()
        for member in members:
            path = PurePosixPath(member.name)
            assert not path.is_absolute() and '..' not in path.parts
            assert '\\' not in member.name and ':' not in member.name
            assert path.parts[0] in (name, name + '-control')
            assert path.as_posix() == member.name.rstrip('/')
            assert member.isdir() or member.isfile() or (member.issym() and member.name == link_rel)
            assert member.name not in names
            names.add(member.name)
        by_name = {m.name: m for m in members}
        assert by_name[seal_rel].isfile() and by_name[git_rel].isfile()
        seal = json.loads(bundle.extractfile(seal_rel).read())
        assert len(seal['files']) == int(count)
        original_files = seal['files']
        if controller_seal:
            seal['files'] = {rel: info['sha256'] for rel, info in original_files.items()}
        file_names = {m.name for m in members if m.isfile() or m.issym()}
        assert file_names == set(seal['files']) | {seal_rel}
        git_raw = bundle.extractfile(git_rel).read()
        assert sha(git_raw) == seal['files'][git_rel]
        git_map = json.loads(git_raw)
        assert len(git_map) == 447 and git_map[LINK] == {'mode': '120000', 'sha': LINK_BLOB}
        assert [rel for rel, item in git_map.items() if item['mode'] == '120000'] == [LINK]
        link, target_member = by_name[link_rel], by_name[target_rel]
        assert link.issym() and link.linkname == LINKNAME and target_member.isfile()
        assert not target_member.issym() and not target_member.islnk()
        text = link.linkname.encode('utf-8')
        assert hashlib.sha1(b'blob ' + str(len(text)).encode() + b'\0' + text).hexdigest() == LINK_BLOB
        # 唯一链接文字已精确锁为同目录文件名，无路径分隔符/绝对路径/递归链接。
        assert PurePosixPath(target_rel).is_relative_to(source)
        materialized = bundle.extractfile(target_member).read()
        target_git = git_map[(PurePosixPath(LINK).parent / LINKNAME).as_posix()]
        assert target_git['mode'] in ('100644', '100755')
        assert hashlib.sha1(b'blob ' + str(len(materialized)).encode() + b'\0' + materialized).hexdigest() == target_git['sha']
        assert sha(materialized) == seal['files'][target_rel] == seal['files'][link_rel]
        added = existing = 0
        for member in members:
            destination = parent.joinpath(*PurePosixPath(member.name).parts)
            assert destination.resolve(strict=False).is_relative_to(parent.resolve())
            assert not destination.is_symlink()
            if member.isdir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            data = materialized if member.issym() else bundle.extractfile(member).read()
            if member.name != seal_rel:
                assert sha(data) == seal['files'][member.name], member.name
                if controller_seal:
                    assert len(data) == original_files[member.name]['bytes'], member.name
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                assert destination.read_bytes() == data, '保留已有不同字节，拒绝覆盖：' + member.name
                existing += 1
            else:
                with destination.open('xb') as output:
                    output.write(data)
                added += 1
        actual = {p.relative_to(parent).as_posix(): sha(p.read_bytes())
                  for folder in (parent / name, parent / (name + '-control'))
                  for p in folder.rglob('*') if p.is_file() and p != parent / seal_rel}
        assert actual == seal['files'], '本地完整原件集合/字节不一致'
    run = parent / name
    pattern = 'context-16k-long/results/*.json'
    result_paths = sorted(run.glob(pattern))
    parsed_results = []
    for path in result_paths:
        try:
            parsed_results.append(json.loads(path.read_text(encoding='utf-8')))
        except (ValueError, UnicodeError) as error:
            parsed_results.append(dict(path=str(path.relative_to(run)), parse_error=type(error).__name__,
                note='负结果可含半写JSON；原字节已通过seal并完整保存，不推定负载成功'))
    result = dict(background_result_glob=pattern, paths=[str(p.relative_to(run)) for p in result_paths],
        results=parsed_results)
    print(json.dumps(dict(run=name, sealed_files=len(actual), added=added,
        matched_existing=existing, original_tgz_sha256=expected_sha,
        materialized_symlinks=[dict(path=link_rel, linkname=LINKNAME, git_blob=LINK_BLOB,
            target=target_rel, materialized_sha256=sha(materialized))],
        exit_code=(run / 'exit-code').read_text().strip(), result=result,
        cpu_events=json.loads((run / 'resume-cpu-events.json').read_text(encoding='utf-8')),
        owner_process_group=json.loads((run / 'owner-process-group.json').read_text(encoding='utf-8'))), ensure_ascii=True))


if __name__ == '__main__':
    main()
