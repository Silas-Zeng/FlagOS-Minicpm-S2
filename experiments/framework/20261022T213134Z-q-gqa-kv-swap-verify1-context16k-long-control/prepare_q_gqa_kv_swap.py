"""固定QGQA414上累加已验FULL/pitched-SAVE；只重定两个runner身份锁。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

BASE = '/workspace/experiments/minicpm-s2/code/q-gqa-service-candidate-20261022T184141Z'
BASE_MAP = 'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'
OUTPUT_MAP = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
ASSETS = {
    'biv150_kv_worker.py': '2de7802d7b07d6f11c8e8f304df36d5503c1189cee9d4ad60f3fbc80fbb98a52',
    'biv150_kv_protocol.py': '91185a23dd56cc7b1d882e9b4b3ccbfdb0d491dce060e658b183ee563d04d3ab',
    'biv150_kv_transaction.py': '84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883',
    'biv150_kv_page_copy.py': 'c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c',
    'biv150_kv_completion_probe.py': 'a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6',
    'biv150_kv_pitched_copy.py': '818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd',
    'biv150_kv_pitched_bridge.cpp': '0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44',
    'biv150_kv_pitched_bridge.so': '9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0',
}
FOOTER = (b'\n    # _biv150_kv_protocol_v1\n'
          b'    from vllm_fl.patches.biv150_kv_protocol import install as _install_kv_protocol\n'
          b'    _install_kv_protocol(enabled=True)\n')


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', type=Path, default=Path(BASE))
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name+'-preparation.json')
    if (base != Path(BASE) or output.exists() or receipt.exists()
            or output.is_relative_to(base) or base.is_relative_to(output)):
        raise ValueError('仅固定184141基点；输出必须新建且不交叠')
    assets = Path(__file__).parent
    raw_base = (assets/'base-source-sha256.json').read_bytes()
    raw_expected = (assets/'expected-source-sha256.json').read_bytes()
    if sha(raw_base) != BASE_MAP or sha(raw_expected) != OUTPUT_MAP:
        raise ValueError('完整输入/输出map变化')
    reference, expected = json.loads(raw_base), json.loads(raw_expected)
    before = mapping(base)
    if before != reference or len(before) != 414 or before['vllm_fl/worker/model_runner.py'] != RUNNER:
        raise ValueError('完整QGQA414基点不符')
    declared = dict(reference)
    init = (base/'vllm_fl/__init__.py').read_bytes() + FOOTER
    declared['vllm_fl/__init__.py'] = sha(init)
    for name, pin in ASSETS.items():
        asset = assets/name
        if asset.is_symlink() or not asset.is_file() or sha(asset.read_bytes()) != pin:
            raise ValueError('KV资产身份不符: '+name)
        rel = 'vllm_fl/patches/'+name
        if rel in declared:
            raise ValueError('不能覆盖基点已有KV资产')
        declared[rel] = pin
    if declared != expected or len(expected) != 422:
        raise ValueError('只允许init追加及8个已审KV文件')
    # 只拷字节；不import协议/Torch/框架、不编译或加载SO。
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output/'vllm_fl/__init__.py').write_bytes(init)
    for name in ASSETS:
        shutil.copyfile(assets/name, output/'vllm_fl/patches'/name)
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError('基点或产物出现未声明改动')
    data = {'kind':'QGQA+既有FULL/pitched-SAVE VERIFY1组合诊断，非吞吐/新accuracy',
        'argv':sys.argv, 'base':str(base), 'source':str(output), 'source_count':422,
        'base_source_sha256':before, 'source_sha256':expected, 'asset_sha256':ASSETS,
        'changed_paths':['vllm_fl/__init__.py', *['vllm_fl/patches/'+n for n in ASSETS]],
        'runner_unchanged_sha256':RUNNER, 'input_map_sha256':BASE_MAP,
        'output_map_sha256':OUTPUT_MAP, 'preparer_sha256':sha(Path(__file__).read_bytes()),
        'required_evidence':['同事务SAVE源42字节与FULL目的42字节通过，0ZERO',
            '实际安全R/页/bytes、pending队列、runner六checks、原consumer及host释放',
            '真实Q/GQA路径与32成功0失败；完整源、DB前后、KV及严格idle'],
        'limits':['仅两处runner SHA显式重定；旧错误消息文本e155未作额外改写',
            'VERIFY1诊断时间不得作净收益；不继承新组合accuracy',
            '不叠finite/selector/RESTORE新pitch/单H2D候选，不自动启动VERIFY0 pair']}
    with receipt.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'source':str(output), 'receipt':str(receipt), 'source_count':422}))


if __name__ == '__main__':
    main()
