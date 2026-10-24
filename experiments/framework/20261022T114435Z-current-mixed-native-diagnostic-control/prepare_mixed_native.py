"""只给新建精确6f副本追加native诊断footer；无设备导入或启动。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

BASE_SHA = '6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141'
FOOTER_SHA = 'f0f41e303dee92b8e468f16d2c7d63cdc38a7ef24da6c38f731cb55c40b53e75'
RUNNER = 'vllm_fl/worker/model_runner.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise RuntimeError('external/directory link: ' + str(rel))
        if path.is_file():
            result[rel.as_posix()] = sha(path.read_bytes())
    return result


def transform(raw):
    footer = Path(__file__).with_name('mixed_native_footer.py').read_bytes()
    if sha(raw) != BASE_SHA or sha(footer) != FOOTER_SHA:
        raise RuntimeError('exact 6f/footer required; no stacked candidate')
    result = raw + b'\n' + footer
    compile(result, 'isolated:mixed-native-runner', 'exec')
    assert result[:len(raw)] == raw
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + '-preparation.json')
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise RuntimeError('new disjoint output required')
    before = mapping(base)
    raw = (base / RUNNER).read_bytes()
    changed = transform(raw)
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output / RUNNER).write_bytes(changed)
    expected = dict(before, **{RUNNER: sha(changed)})
    if mapping(base) != before or mapping(output) != expected:
        raise RuntimeError('unexpected source delta')
    receipt.write_text(json.dumps(dict(
        kind='current 6f natural mixed native diagnostic, not performance',
        base_source_sha256=before, source_sha256=expected, changed_paths=[RUNNER],
        base_runner_sha256=BASE_SHA, footer_sha256=FOOTER_SHA,
        candidate_runner_sha256=sha(changed)), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'candidate_runner_sha256': sha(changed)}))


if __name__ == '__main__':
    main()
