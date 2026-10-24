"""核对整包、每个原件，并汇总原 smoke 输出；不修改原始证据。"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys
import tarfile

name, size, digest, count = sys.argv[1:]
parent = Path(__file__).resolve().parents[2] / 'experiments/framework'
archive = parent / (name + '.tgz')
assert archive.stat().st_size == int(size)
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest
assert not (parent / name).exists() and not (parent / (name + '-control')).exists()
with tarfile.open(archive) as bundle:
    for member in bundle.getmembers():
        path = PurePosixPath(member.name)
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] in (name, name + '-control')
        assert member.isdir() or member.isfile()
    bundle.extractall(parent, filter='data')
seal = json.loads((parent / (name + '-control') / 'evidence-seal.json').read_text())
assert len(seal['files']) == int(count)
for rel, expected in seal['files'].items():
    assert hashlib.sha256((parent / rel).read_bytes()).hexdigest() == expected, rel
run = parent / name
assert (run / 'exit-code').read_text().strip() == '0'
smoke = json.loads((run / 'smoke.json').read_text())
events = []
for line in (run / 'server.log').read_text(errors='replace').splitlines():
    marker = 'BIV150_KV_MEMORY_OBSERVER '
    if marker in line:
        events.append(json.loads(line.split(marker, 1)[1]))
print(json.dumps({'run': name, 'sealed_files': len(seal['files']),
                 'smoke_choices': len(smoke['choices']), 'observer_events': events}, ensure_ascii=False))
