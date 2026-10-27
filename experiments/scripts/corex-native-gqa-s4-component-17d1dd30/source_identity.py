"""只读固定 main56 与当前 native 二进制身份。"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
NATIVE_SHA = '14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
COMMIT = '56f1838192abc940b3fb9accef490022ac125000'

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(source, library):
    source, library = Path(source).resolve(strict=True), Path(library).resolve(strict=True)
    manifest = json.loads((HERE/'base-source-manifest.json').read_bytes())
    if manifest['commit'] != COMMIT or manifest['source_count'] != 807 or sha(library) != NATIVE_SHA:
        raise ValueError('main56/native14f身份不符')
    for name, record in manifest['files'].items():
        path = source/name
        raw = path.readlink().as_posix().encode() if record['mode']=='120000' and path.is_symlink() else path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != record['sha256']:
            raise ValueError('固定807文件变化: '+name)
    extras = {}
    for path in source.rglob('*'):
        rel = path.relative_to(source)
        if '.git' in rel.parts or '__pycache__' in rel.parts or not path.is_file():
            continue
        if rel.as_posix() not in manifest['files']:
            extras[rel.as_posix()] = sha(path)
    return dict(commit=COMMIT, tracked_files=807, native_sha256=NATIVE_SHA, extras=extras)
