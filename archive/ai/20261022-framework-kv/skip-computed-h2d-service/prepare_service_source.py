"""方法门通过后才建立baseline或单H2D服务副本；完整414只允许runner差异。"""
import argparse
import hashlib
import json
from pathlib import Path
import runpy
import shutil
import sys

MAP_SHA = 'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'
EXPECTED_MAP_SHA = '425245ed4b8a0f086dc1ac99807d137f21f0128aaa1ada45a576c19bd639c0dd'
TRANSFORM_SHA = '23d833a1bd3f4155652a2457b19bdaedf29b918de488e18e5b986b2cb5e08427'
BASE_DIR = '/workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z'
RUNNER = 'vllm_fl/worker/model_runner.py'
BASE_RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
CAND_RUNNER = '97f41ac455cad0db7c8ddfd2b9809e77326b6472285cb14e56ce486f2f0f7443'
METHOD = {'gate.py':'461676a0b6517e5c832d315fbcfe18aff059ad0bd23cf14e51da7f34cfe4af42',
    'transform.py':TRANSFORM_SHA, 'runner.py':BASE_RUNNER, 'runner-transformed.py':CAND_RUNNER,
    'runtime.py':'0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f',
    'async-runtime.py':'1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc'}


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
                raise ValueError('拒绝外部/目录链接')
        if path.is_file():
            result[rel.as_posix()] = sha(path.read_bytes())
    return result


def method_gate(folder):
    folder = folder.resolve(strict=True)
    result = json.loads((folder/'results.json').read_text())
    manifest = json.loads((folder/'manifest.json').read_text())
    if (int((folder/'exit-code').read_text()) != 0 or manifest.get('exit_code') != 0
            or result.get('status') != 'pass' or not result.get('consecutive_event_and_fixed_graph_consumer')
            or not result.get('full_method_real_guard_fallback')
            or not all(result['full_method_real_guard_fallback'].values())
            or result.get('rng_unchanged_during_timing') is not True):
        raise ValueError('必须等待已通过的固定方法门；未运行/失败不能部署服务')
    actual = {name:sha((folder/'source'/name).read_bytes()) for name in METHOD}
    if actual != METHOD:
        raise ValueError('不是本次固定helper/runner的461676方法门')
    return {'run':str(folder), 'passed':True, 'source_sha256':actual,
        'results_sha256':sha((folder/'results.json').read_bytes()),
        'manifest_sha256':sha((folder/'manifest.json').read_bytes())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir',required=True,type=Path)
    parser.add_argument('--output-dir',required=True,type=Path)
    parser.add_argument('--method-gate-dir',required=True,type=Path)
    parser.add_argument('--variant',choices=('baseline','candidate'),required=True)
    args = parser.parse_args()
    verified = method_gate(args.method_gate_dir)
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    if base != Path(BASE_DIR):
        raise ValueError('仅接受184141已受测QGQA414源码')
    receipt = output.with_name(output.name+'-preparation.json')
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError('输出必须新建且不与基点交叠')
    assets = Path(__file__).parent
    raw_map = (assets/'base-source-sha256.json').read_bytes()
    raw_expected = (assets/'expected-source-sha256.json').read_bytes()
    transform = assets/'prepare_skip_computed_h2d.py'
    if (sha(raw_map)!=MAP_SHA or sha(raw_expected)!=EXPECTED_MAP_SHA
            or sha(transform.read_bytes())!=TRANSFORM_SHA):
        raise ValueError('固定输入/输出map或transform变化')
    reference = json.loads(raw_map)
    candidate_map = json.loads(raw_expected)
    before = mapping(base)
    if before!=reference or len(before)!=414 or before.get(RUNNER)!=BASE_RUNNER:
        raise ValueError('完整原QGQA414基点变化')
    expected = dict(reference)
    changed = (base/RUNNER).read_bytes()
    if args.variant=='candidate':
        changed = runpy.run_path(str(transform))['transform_source'](changed)
        expected[RUNNER] = CAND_RUNNER
        if expected!=candidate_map:
            raise ValueError('仅允许固定runner差异')
    shutil.copytree(base,output,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    (output/RUNNER).write_bytes(changed)
    if mapping(base)!=before or mapping(output)!=expected:
        raise ValueError('副本或基点出现未声明源变更')
    data = {'kind':'方法门后原QGQA vs单computedH2D候选；未修改服务参数/算子',
        'argv':sys.argv, 'variant':args.variant, 'base':str(base), 'source':str(output),
        'source_count':414, 'base_source_sha256':before, 'source_sha256':expected,
        'changed_paths':[RUNNER] if args.variant=='candidate' else [],
        'method_gate':verified, 'base_map_sha256':MAP_SHA,
        'preparer_sha256':sha(Path(__file__).read_bytes())}
    with receipt.open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'source':str(output),'receipt':str(receipt),'source_count':414}))


if __name__=='__main__':
    main()
