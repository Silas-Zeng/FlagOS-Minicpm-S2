"""导入已封存的原官方包；只核传输和清单，不重跑实验或改CSV。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import sys
import tarfile

name, size, expected_digest, count = sys.argv[1:]
assert name == '20261022T231746Z-q-gqa-kv-swap-official'
root = Path.cwd()
if os.name == 'nt' and not str(root).startswith('\\\\?\\'):
    root = Path('\\\\?\\' + str(root))
parent = root / 'experiments/official'
archive = parent / (name + '.tgz')
digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
assert archive.stat().st_size == int(size) and digest(archive) == expected_digest
assert not (parent / name).exists() and not (parent / (name + '-control')).exists()
with tarfile.open(archive) as bundle:
    seen = set()
    for member in bundle.getmembers():
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] in (name, name + '-control')
        assert member.isdir() or member.isfile()
        assert member.name not in seen
        seen.add(member.name)
    bundle.extractall(parent, filter='data')
seal_path = parent / (name + '-control') / 'evidence-seal.json'
seal = json.loads(seal_path.read_text(encoding='utf-8'))
assert len(seal['files']) == int(count)
actual = {p.relative_to(parent).as_posix(): digest(p)
          for directory in (parent / name, parent / (name + '-control'))
          for p in directory.rglob('*') if p.is_file() and p != seal_path}
assert actual == seal['files'], '原件清单或字节不一致'
run = parent / name
result = json.loads((run / 'result.json').read_text(encoding='utf-8'))
assert (run / 'exit-code').read_text().strip() == '0'
assert result['status'] == 'official_benchmark_completed' and result['exit_code'] == 0
print(json.dumps({'run': name, 'sealed_files': len(actual),
                  'original_validation': result['validation']}, ensure_ascii=False))
