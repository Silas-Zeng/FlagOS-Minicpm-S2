"""仅给冻结QGQA414/finite415追加共同启动标量观察器；receipt在源树之外。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path('/workspace/experiments/minicpm-s2')
INIT = 'vllm_fl/__init__.py'
RUNNER = 'vllm_fl/worker/model_runner.py'
HELPER = 'vllm_fl/patches/biv150_kv_memory_observer.py'
OBSERVER_SHA = '9d43de58bfe587e3f80cbc8aeed2174f03755172858817fb7c90769374aef119'
RUNNER_SHA = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
VARIANTS = {
    'baseline': ('q-gqa-service-candidate-20261022T184141Z', 414,
        'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392',
        'e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff'),
    'finite': ('finite-growth-candidate-20261022T194634Z', 415,
        '7ad1f1acd9188b617a879f7e5de97c883fddf5ccc7981cbb27e0e474f92043c7',
        'c9a2da565f519ea6ebd5edb9b2456ccc4f077141af0fbc00e907f1ecb34df363'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping(folder):
    # 复用已审finite preparer的完整文件map规则。
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc', '.pyo'):
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
    parser.add_argument('--variant', choices=VARIANTS, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    name, count, map_sha, init_sha = VARIANTS[args.variant]
    base = (ROOT / 'code' / name).resolve(strict=True)
    output = args.output_dir.resolve()
    receipt = output.with_name(output.name + '-preparation.json')
    if (output.parent != ROOT / 'code' or output.exists() or output.is_symlink()
            or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output)):
        raise ValueError('输出须为ROOT/code全新直接子目录，不与基点交叠')
    assets = Path(__file__).parent
    raw_map = (assets / (args.variant + '-source-sha256.json')).read_bytes()
    if sha(raw_map) != map_sha:
        raise ValueError('完整参考map变化')
    expected_base = json.loads(raw_map)
    before = mapping(base)
    if (before != expected_base or len(before) != count or before[INIT] != init_sha
            or before[RUNNER] != RUNNER_SHA or HELPER in before):
        raise ValueError('完整冻结基点变化或已有观察器')
    raw = (assets / 'biv150_kv_memory_observer.py').read_bytes()
    if sha(raw) != OBSERVER_SHA:
        raise ValueError('共同observer变化')
    constants = {n.targets[0].id: ast.literal_eval(n.value) for n in ast.parse(raw).body
        if isinstance(n, ast.Assign) and len(n.targets) == 1
        and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id in ('INIT_FOOTER', 'EXPECTED_INIT_PREFIXES')}
    if init_sha not in constants['EXPECTED_INIT_PREFIXES'].values():
        raise ValueError('observer不允许该完整init')
    original = (base / INIT).read_bytes()
    changed = original + constants['INIT_FOOTER']
    compile(changed, INIT, 'exec')
    compile(raw, HELPER, 'exec')
    expected = dict(before)
    expected.update({INIT: sha(changed), HELPER: OBSERVER_SHA})
    assert len(expected) == count + 1
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output / INIT).write_bytes(changed)
    (output / HELPER).write_bytes(raw)
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError('出现未声明源变更')
    info = {'kind': '当前QGQA/finite共同启动标量观察；非容量控制或性能pair',
        'variant': args.variant, 'argv': sys.argv, 'base': str(base), 'source': str(output),
        'base_source_sha256': before, 'source_sha256': expected, 'base_map_sha256': map_sha,
        'changed_paths': [INIT, HELPER], 'observer_sha256': OBSERVER_SHA,
        'preparer_sha256': sha(Path(__file__).read_bytes()), 'runner_unchanged': True,
        'init_before_sha256': init_sha, 'init_after_sha256': expected[INIT],
        'required_evidence': ['same Engine DETERMINE_RETURN/profile1',
            'same Engine PARENT_RETURN original list; all three hooks restored',
            'no REJECTED/NOT_ACTIVATED/OBSERVATION_INCOMPLETE'],
        'limits': ['不增加设备采样/改变原容量；未复现即停止，不追启动样本。',
            '只解释本轮分项，不能回填历史或证明具体分配来源。']}
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'source_count': len(expected)}))


if __name__ == '__main__':
    main()
