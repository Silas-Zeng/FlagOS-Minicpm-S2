"""仅从完整PASS单层H2D门锁实际SO，构建当前422上的FULL-only 425源；不加载库。"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys

ROOT = Path('/workspace/experiments/minicpm-s2')
BASE = ROOT / 'code/q-gqa-kv-swap-20261022T213134Z'
BASE_MAP = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
DRAFT = '9f178a70b48cf19e97d32f7b9bea26195f7e447b593be9784659916d36120475'
WORKER = 'vllm_fl/patches/biv150_kv_worker.py'
RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
CONTROLLER = 'ed7331a693719a5db950527812eac3072432d8bc4e6db2da1cd32fcbed6f4862'
CUDART = 'd39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527'
GATE_SOURCE = {
    'gate.py': '10e5ec18ea1a1ddc125362a9bf21063f59c6a196214a0873a455c1c8ed3d6df9',
    'biv150_kv_pitched_copy.py': '818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd',
    'biv150_kv_pitched_restore.py': 'a7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c',
    'bridge.cpp': '48295ffde897cce988d3a8460904ab4451669e1de2fbe2bd5257d3f75e35ab20',
    'biv150_kv_page_copy.py': 'c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c',
    'pitched-save-gate.py': 'c8c0f64e7293634a28949f4338800298b43d32daa7cbd866e64dcd59833d7dc6',
    'restore-page-evidence.json': '55c383db7601041cbc9a0d464e2395f30b36637d22ffb65231414d17444ae308',
    'memcpy2d-abi.json': 'f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576',
}
CHECKS = {
    'native_submit_counts_and_not_ACK', 'same_stream_consumer_all_selected_bytes',
    'consumer_host_guards', 'host_and_destination_nonzero_storage_offsets',
    'pinned_host_source_and_both_guards_unchanged',
    'candidate_all_selected_gap_and_guards_match_CPU_oracle',
    'candidate_positive_basic_guard_reads',
    'baseline_c95f_all_selected_gap_and_guards_match_same_oracle',
    'baseline_c95f_submit', 'host_source_and_both_guards_still_unchanged',
}
ADDED = {
    'biv150_kv_pitched_restore.py': 'biv150_kv_pitched_restore.py',
    'biv150_kv_pitched_restore_bridge.cpp': 'bridge.cpp',
    'biv150_kv_pitched_restore_bridge.so': 'bridge.so',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('要求regular file: ' + str(path))
    return json.loads(path.read_text(encoding='utf-8'))


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise ValueError('拒绝外部/目录链接: ' + str(path))
        if path.is_file():
            result[rel.as_posix()] = file_sha(path)
    return result


def passed_gate(gate):
    """只读原完整seal及PASS；SO不能由CLI指定或从未测编译产物取代。"""
    if (gate.is_symlink() or gate.resolve(strict=True) != gate or gate.parent != ROOT / 'framework'
            or not gate.name.endswith('-kv-pitched-restore-gate')):
        raise ValueError('要求原ROOT/framework直系H2D gate绝对目录')
    control = gate.with_name(gate.name + '-control')
    if control.is_symlink() or not control.is_dir():
        raise ValueError('缺真实control目录')
    seal = read(control / 'seal.json')
    if (seal.get('exit_code') != 0 or seal.get('run') != str(gate)
            or seal.get('control') != str(control) or not seal.get('files')):
        raise ValueError('原gate seal未完整成功')
    actual = {}
    for directory in (gate, control):
        for path in directory.rglob('*'):
            if path.is_symlink():
                raise ValueError('gate封存禁止链接')
            if path.is_file() and path != control / 'seal.json':
                actual[path.relative_to(gate.parent).as_posix()] = path
    if set(actual) != set(seal['files']):
        raise ValueError('gate实际完整文件集合与原seal不同，不接受未封存SO/结果')
    for name, expected in seal['files'].items():
        rel = PurePosixPath(name)
        if (rel.is_absolute() or '..' in rel.parts or '\\' in name
                or rel.parts[0] not in (gate.name, control.name)):
            raise ValueError('seal路径不合法')
        path = actual[name]
        if expected != {'sha256': file_sha(path), 'bytes': path.stat().st_size}:
            raise ValueError('gate seal字节不符: ' + name)
    manifest, result = read(gate / 'manifest.json'), read(gate / 'results.json')
    if ((gate / 'failed.json').exists() or (gate / 'exit-code').read_text().strip() != '0'
            or manifest.get('exit_code') != 0 or manifest.get('worker_exit_code') != 0
            or manifest.get('controller_sha256') != CONTROLLER
            or manifest.get('source_unchanged') is not True or result.get('status') != 'pass'
            or any(k in manifest for k in ('controller_error', 'cleanup_errors', 'source_post_error',
                                          'db_after_error', 'postflight_error', 'environment_after_error'))):
        raise ValueError('gate worker/controller/source未PASS')
    if file_sha(control / 'launch_kv_pitched_restore_gate.py') != CONTROLLER:
        raise ValueError('gate controller身份变化')
    source = gate / 'source'
    bridge = file_sha(source / 'bridge.so')
    expected_source = {**GATE_SOURCE, 'bridge.so': bridge}
    if (mapping(source) != expected_source or read(control / 'source-sha256.json') != expected_source
            or read(control / 'source-post-sha256.json') != expected_source
            or result.get('source_sha256') != expected_source
            or manifest.get('bridge_sha256') != bridge or result.get('bridge_sha256') != bridge):
        raise ValueError('实际SO与门前/门后/结果/归档资产不一致')
    checks = result.get('case', {}).get('checks', {})
    loaded = result.get('actual_loaded_libcudart', {})
    post = manifest.get('postflight', {})
    if (set(checks) != CHECKS or any(value is not True for value in checks.values())
            or result.get('RNG_unchanged') != {'CPU': True, 'GPU': True}
            or type(result.get('explicit_nondefault_stream_handle')) is not int
            or result['explicit_nondefault_stream_handle'] <= 0
            or len(loaded) != 1 or next(iter(loaded.values())).get('sha256') != CUDART
            or post.get('query', '').strip() != '68, 0'
            or 'No running processes found' not in post.get('ixsmi', '')
            or len(post.get('sockets', [])) != 2
            or any(row.get('connect_ex', 0) == 0 for row in post['sockets'])):
        raise ValueError('单层字节/流/guard/RNG或结束idle门未全过')
    return source, bridge, {
        'run': str(gate), 'control': str(control), 'seal_sha256': file_sha(control / 'seal.json'),
        'seal_files': len(seal['files']), 'results_sha256': file_sha(gate / 'results.json'),
        'manifest_sha256': file_sha(gate / 'manifest.json'), 'bridge_sha256': bridge,
        'source_sha256': expected_source,
        'scope': '独立单层H2D正确性；不替代新425的42层事务/服务/accuracy',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--gate-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    assets = Path(__file__).resolve().parent
    output = args.output_dir.absolute()
    receipt = output.with_name(output.name + '-preparation.json')
    if (output.parent != ROOT / 'code' or not output.name.startswith('q-gqa-kv-restore-pitched-')
            or output.exists() or output.is_symlink() or receipt.exists()
            or output.resolve() != output or output == BASE):
        raise ValueError('输出必须是ROOT/code下全新独立restore-pitched源')
    raw_map = (assets / 'base-source-sha256.json').read_bytes()
    raw_worker = (assets / 'biv150_kv_pitched_restore_worker.py').read_bytes()
    if sha(raw_map) != BASE_MAP or sha(raw_worker) != DRAFT:
        raise ValueError('固定422完整map或已审worker草稿变化')
    before = mapping(BASE)
    if (before != json.loads(raw_map) or len(before) != 422
            or before.get('vllm_fl/worker/model_runner.py') != RUNNER):
        raise ValueError('当前213134完整422基点不符')
    gate_source, bridge, gate_receipt = passed_gate(args.gate_dir)
    anchor = b'RESTORE_BRIDGE = None\n'
    replacement = ('RESTORE_BRIDGE = ' + repr(bridge) + '\n').encode('ascii')
    if raw_worker.count(anchor) != 1:
        raise ValueError('必须只锁唯一RESTORE_BRIDGE None')
    worker = raw_worker.replace(anchor, replacement)
    if worker.replace(replacement, anchor) != raw_worker:
        raise ValueError('SO pin单点变换不可精确逆回')
    compile(worker, 'vllm_fl/patches/biv150_kv_worker.py', 'exec')
    expected = dict(before)
    expected[WORKER] = sha(worker)
    for target, origin in ADDED.items():
        rel = 'vllm_fl/patches/' + target
        if rel in expected:
            raise ValueError('禁止覆盖既有新增路径: ' + rel)
        expected[rel] = file_sha(gate_source / origin)
    if len(expected) != 425:
        raise ValueError('只允许worker替换及三个restore文件')
    # 不编译CPP/不import候选或Torch/不加载任何SO；只复制已测字节。
    shutil.copytree(BASE, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output / WORKER).write_bytes(worker)
    for target, origin in ADDED.items():
        shutil.copyfile(gate_source / origin, output / 'vllm_fl/patches' / target)
    if mapping(BASE) != before or mapping(output) != expected:
        raise ValueError('基点或425产物有未声明变更')
    # 从验证到复制不接受gate输入变化，包括动态SO。
    if mapping(gate_source) != gate_receipt['source_sha256']:
        raise ValueError('gate归档源在准备中发生变化')
    data = {
        'kind': 'QGQA+原swap仅FULL H2D pitched的VERIFY1兼容诊断，非性能或accuracy',
        'argv': sys.argv, 'base': str(BASE), 'source': str(output), 'source_count': 425,
        'input_map_sha256': BASE_MAP, 'base_source_sha256': before, 'source_sha256': expected,
        'output_map_sha256': sha((json.dumps(expected, indent=2) + '\n').encode()),
        'changed_paths': [WORKER, *['vllm_fl/patches/' + n for n in ADDED]],
        'worker_draft_sha256': DRAFT, 'worker_sha256': sha(worker),
        'worker_change': '相对已审9f草稿仅RESTORE_BRIDGE None单点锁实际PASS门SO；逆回精确',
        'runner_unchanged_sha256': RUNNER, 'passed_H2D_gate': gate_receipt,
        'preparer_sha256': file_sha(Path(__file__)),
        'required_evidence': ['新FULL实际实现及动态几何、同事务两组42字节、0ZERO',
            '原SAVE/协议/runner消费/QGQA路径及32-0；DB/源/idle完整',
            'VERIFY1时间不作收益；VERIFY0配对与新accuracy由root后续另定'],
        'limits': ['不混finite/selector/RESTORE旧路重试/H2D小候选',
            '单层PASS不证明42层事务、恢复资格、净益或accuracy；原422证据不能继承为425'],
    }
    with receipt.open('x', encoding='utf-8', newline='\n') as file:
        json.dump(data, file, ensure_ascii=False, indent=2); file.write('\n')
    print(json.dumps({'source': str(output), 'receipt': str(receipt), 'source_count': 425}))


if __name__ == '__main__':
    main()
