"""从本轮冻结Q+GQA414源创建观察副本；只更改init并新增一个helper。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

MAP_SHA = 'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'
INIT = 'vllm_fl/__init__.py'
RUNNER = 'vllm_fl/worker/model_runner.py'
HELPER = 'vllm_fl/patches/biv150_admission_observer.py'
INIT_SHA = 'e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff'
RUNNER_SHA = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
ASSETS = {'biv150_admission_observer.py': '916e842e838763731d5a1ffa4588c2c5a14baabd592813afa74b23d60a7aed4b',
          'observer_init_footer.py': '5127841cab8b5c805702b0bea041b66600c9f10a7dd9f198a42799b1f1665606'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc','.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise ValueError('拒绝外部/目录链接')
        if path.is_file():
            result[rel.as_posix()] = sha(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + '-preparation.json')
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError('输出须全新且不与基点交叠')
    assets = Path(__file__).parent
    raw_map = (assets / 'base-source-sha256.json').read_bytes()
    if sha(raw_map) != MAP_SHA:
        raise ValueError('非184141冻结414 map')
    expected_base = json.loads(raw_map)
    before = mapping(base)
    if before != expected_base or len(before) != 414 or before[INIT] != INIT_SHA or before[RUNNER] != RUNNER_SHA or HELPER in before:
        raise ValueError('完整Q+GQA414基点不符')
    data = {name: (assets / name).read_bytes() for name in ASSETS}
    if any(sha(data[name]) != pin for name, pin in ASSETS.items()):
        raise ValueError('观察资产未冻结/变化')
    changed = (base / INIT).read_bytes() + data['observer_init_footer.py']
    compile(changed, 'admission-observer-init', 'exec')
    compile(data['biv150_admission_observer.py'], HELPER, 'exec')
    expected = dict(before)
    expected.update({INIT: sha(changed), HELPER: ASSETS['biv150_admission_observer.py']})
    assert len(expected) == 415
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    (output / INIT).write_bytes(changed)
    (output / HELPER).write_bytes(data['biv150_admission_observer.py'])
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError('出现未声明源变更')
    info = {'kind': '固定QGQA414的稀疏CPU准入诊断；不改变调度结果、不计性能', 'argv': sys.argv,
        'base': str(base), 'source': str(output), 'base_source_sha256': before, 'source_sha256': expected,
        'changed_paths': [INIT, HELPER], 'runner_unchanged': expected[RUNNER] == before[RUNNER],
        'base_map_sha256': MAP_SHA, 'assets_sha256': ASSETS, 'preparer_sha256': sha(Path(__file__).read_bytes())}
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'source_count': len(expected)}))


if __name__ == '__main__':
    main()
