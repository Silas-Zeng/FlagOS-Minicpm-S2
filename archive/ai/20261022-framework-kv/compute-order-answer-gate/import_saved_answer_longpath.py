"""核对封包后补齐原件；支持Windows长路径，拒绝覆盖已有不同字节。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import sys
import tarfile

name, expected_size, expected_sha, count = sys.argv[1:5]
controller_seal = sys.argv[5:] == ['--controller-seal']
assert not sys.argv[5:] or controller_seal
root = Path(__file__).resolve().parents[1]
if os.name == 'nt' and not str(root).startswith('\\\\?\\'):
    root = Path('\\\\?\\' + str(root))
parent = root / 'experiments/framework'
archive = parent / (name + '.tgz')
sha = lambda raw: hashlib.sha256(raw).hexdigest()
assert archive.stat().st_size == int(expected_size)
assert sha(archive.read_bytes()) == expected_sha
seal_rel = name + ('-control/seal.json' if controller_seal else '-control/evidence-seal.json')
with tarfile.open(archive) as bundle:
    members = bundle.getmembers()
    names = set()
    for member in members:
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert '\\' not in member.name and ':' not in member.name
        assert path.parts[0] in (name, name + '-control')
        assert member.isdir() or member.isfile()
        assert member.name not in names
        names.add(member.name)
    seal = json.loads(bundle.extractfile(seal_rel).read())
    assert len(seal['files']) == int(count)
    original_files = seal['files']
    if controller_seal:
        seal['files'] = {rel: info['sha256'] for rel, info in original_files.items()}
    file_names = {m.name for m in members if m.isfile()}
    assert file_names == set(seal['files']) | {seal_rel}
    added = existing = 0
    for member in members:
        target = parent.joinpath(*PurePosixPath(member.name).parts)
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        data = bundle.extractfile(member).read()
        if member.name != seal_rel:
            assert sha(data) == seal['files'][member.name], member.name
            if controller_seal:
                assert len(data) == original_files[member.name]['bytes'], member.name
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == data, '保留已有不同字节，拒绝覆盖：' + member.name
            existing += 1
        else:
            with target.open('xb') as output:
                output.write(data)
            added += 1
    actual = {p.relative_to(parent).as_posix(): sha(p.read_bytes())
              for folder in (parent / name, parent / (name + '-control'))
              for p in folder.rglob('*') if p.is_file() and p != parent / seal_rel}
    assert actual == seal['files'], '本地完整原件集合/字节不一致'
run = parent / name
results = [run/'context-16k/answer-summary.json']
assert len(results) == 1
result = json.loads(results[0].read_text(encoding='utf-8'))
print(json.dumps({'run': name, 'sealed_files': len(actual), 'added': added,
                  'matched_existing': existing, 'exit_code': (run/'exit-code').read_text().strip(),
                  'result': result}, ensure_ascii=False))
