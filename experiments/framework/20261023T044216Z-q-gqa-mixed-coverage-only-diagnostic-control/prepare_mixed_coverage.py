"""只从固定422生成init+独立helper诊断副本；原runner/protocol不改。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
RUNNER_SHA = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
POLICY_SHA = '8c5b1e2d34d223b068dfd468e2015572871a286cdaf8c19d61ddc63a4e8ae02e'
FOOTER_SHA = '75f4394406f0607e6e7254440bf738075bdb6f6d2134f4341b473caca819696b'
INIT = 'vllm_fl/__init__.py'
HELPER = 'vllm_fl/patches/biv150_puredecode_native.py'


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + '-preparation.json')
    if (base != Path('/workspace/experiments/minicpm-s2/code/q-gqa-kv-swap-20261022T213134Z')
            or output.exists() or receipt.exists() or output.is_relative_to(base)
            or base.is_relative_to(output) or output.parent != base.parent):
        raise RuntimeError('固定422基点及同code父目录的新独立副本')
    before = mapping(base)
    assets = Path(__file__).parent
    map_raw = (assets / 'base-source-sha256.json').read_bytes()
    if sha(map_raw) != MAP_SHA or before != json.loads(map_raw) or len(before) != 422:
        raise RuntimeError('完整固定422源不符')
    if before['vllm_fl/worker/model_runner.py'] != RUNNER_SHA or HELPER in before:
        raise RuntimeError('原runner身份/新增路径不符')
    policy = (assets / 'biv150_puredecode_native.py').read_bytes()
    footer = (assets / 'init-footer.py').read_bytes()
    if sha(policy) != POLICY_SHA or sha(footer) != FOOTER_SHA:
        raise RuntimeError('冻结诊断资产变化')
    changed = (base / INIT).read_bytes() + footer
    compile(changed, INIT, 'exec')
    compile(policy, HELPER, 'exec')
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output / INIT).write_bytes(changed)
    (output / HELPER).write_bytes(policy)
    expected = dict(before, **{INIT: sha(changed), HELPER: sha(policy)})
    if mapping(base) != before or mapping(output) != expected:
        raise RuntimeError('未声明的源改动')
    receipt.write_text(json.dumps(dict(kind='当前422 mixed metadata CPU计数；无profiler，不是性能测量',
        source=str(output), base_source_map_sha256=MAP_SHA, base_source_count=422,
        source_count=423, base_source_sha256=before, source_sha256=expected,
        changed_paths=[INIT, HELPER], base_runner_sha256=RUNNER_SHA,
        policy_sha256=POLICY_SHA, footer_sha256=FOOTER_SHA), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'source_count': 423}))


if __name__ == '__main__':
    main()
