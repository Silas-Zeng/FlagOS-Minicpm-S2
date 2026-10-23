"""只给新建精确QGQA414副本追加native诊断footer；无设备导入或启动。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

BASE_SHA = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
MAP_SHA = 'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'
FOOTER_SHA = 'e13d46137f48f8bc6923676115c3f8b7dbf12e5fd4ec176721fad2b35fe0c26b'
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
    footer = Path(__file__).with_name('resume_native_footer.py').read_bytes()
    if sha(raw) != BASE_SHA or sha(footer) != FOOTER_SHA:
        raise RuntimeError('exact QGQA414/footer required; no admission observer')
    result = raw + b'\n' + footer
    compile(result, 'isolated:resume-native-runner', 'exec')
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
    map_raw = Path(__file__).with_name('base-source-sha256.json').read_bytes()
    if sha(map_raw) != MAP_SHA:
        raise RuntimeError('fixed184141 QGQA source map changed')
    expected_base = json.loads(map_raw)
    if len(expected_base) != 414 or before != expected_base:
        raise RuntimeError('complete QGQA414 source map mismatch')
    raw = (base / RUNNER).read_bytes()
    changed = transform(raw)
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output / RUNNER).write_bytes(changed)
    expected = dict(before, **{RUNNER: sha(changed)})
    if mapping(base) != before or mapping(output) != expected:
        raise RuntimeError('unexpected source delta')
    receipt.write_text(json.dumps(dict(
        kind='current QGQA414 preempted request resume native diagnostic, not performance',
        base_source_map_sha256=MAP_SHA, base_source_count=414,
        base_source_sha256=before, source_sha256=expected, changed_paths=[RUNNER],
        base_runner_sha256=BASE_SHA, footer_sha256=FOOTER_SHA,
        candidate_runner_sha256=sha(changed)), indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'candidate_runner_sha256': sha(changed)}))


if __name__ == '__main__':
    main()
