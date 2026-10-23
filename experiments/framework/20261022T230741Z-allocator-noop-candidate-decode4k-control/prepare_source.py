"""固定422仅追加init/footer和无状态allocator helper；不修改runner/协议/算子。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

BASE = Path('/workspace/experiments/minicpm-s2/code/q-gqa-kv-swap-20261022T213134Z')
PINS = {
    'base-source-sha256.json': '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
    'expected-source-sha256.json': 'beb748fc30842d2ba378bcb0e526dfff0ba6e02f9ec4acf8986d8f2e7421ac5d',
    'biv150_noop_allocate.py': '7393aa23cbef2c795faed23e32504a028ad1a867226089c45ad5c43026a9f3e9',
    'init-footer.py': '14a55c38704415d1a5bb99074e605ddf78b854bf41540f6fc397ec37b2354f6d',
    'cpu-tested-core.py': 'fc410a4a02f93694402480a91a4a027ce16e5c6beaf90efc59d141cf0c5de2b3',
    'cpu-check.json': 'e876f792614c0cbbd7e1a2222fddf233cbe6adc8dd3ac94355be6e2e010be23b',
}
sha = lambda data: hashlib.sha256(data).hexdigest()


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(x in ('.git','__pycache__') for x in rel.parts) or path.suffix in ('.pyc','.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise ValueError('拒绝外部/目录链接')
        if path.is_file(): result[rel.as_posix()] = sha(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',required=True,type=Path)
    args = parser.parse_args()
    output = args.output_dir.resolve(); receipt = output.with_name(output.name+'-preparation.json')
    if (output.exists() or receipt.exists() or output.is_relative_to(BASE)
            or BASE.is_relative_to(output) or output.parent != BASE.parent):
        raise ValueError('必须在code下新建独立源，不覆盖/交叠')
    assets = Path(__file__).parent
    raw = {}
    for name,pin in PINS.items():
        path = assets/name
        if path.is_symlink() or not path.is_file() or sha(path.read_bytes())!=pin:
            raise ValueError('接线素材变化: '+name)
        raw[name] = path.read_bytes()
    reference=json.loads(raw['base-source-sha256.json']); expected=json.loads(raw['expected-source-sha256.json'])
    before=mapping(BASE)
    if before!=reference or len(before)!=422:
        raise ValueError('完整原213134422源不符')
    check=json.loads(raw['cpu-check.json'])
    if (check.get('cpu_fragment_go') is not True or check['policy_sha256']!=PINS['cpu-tested-core.py']
            or not raw['biv150_noop_allocate.py'].startswith(raw['cpu-tested-core.py'])):
        raise ValueError('CPU净省证据或受测完整热核前缀不符')
    changed=dict(reference)
    init=(BASE/'vllm_fl/__init__.py').read_bytes()+raw['init-footer.py']
    changed['vllm_fl/__init__.py']=sha(init)
    helper='vllm_fl/patches/biv150_noop_allocate.py'
    if helper in reference: raise ValueError('不能覆盖原helper路径')
    changed[helper]=PINS['biv150_noop_allocate.py']
    if changed!=expected or len(expected)!=423:
        raise ValueError('只允许init精确append和helper新增')
    compile(init,'vllm_fl/__init__.py','exec')
    compile(raw['biv150_noop_allocate.py'],helper,'exec')
    shutil.copytree(BASE,output,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    (output/'vllm_fl/__init__.py').write_bytes(init)
    (output/helper).write_bytes(raw['biv150_noop_allocate.py'])
    if mapping(BASE)!=before or mapping(output)!=expected:
        raise ValueError('原源或副本存在未声明改动')
    data={'kind':'已验CPU无状态allocator快返的423短服务候选，非新增算子/参数',
        'argv':sys.argv,'base':str(BASE),'source':str(output),'source_count':423,
        'base_source_sha256':before,'source_sha256':expected,
        'changed_paths':['vllm_fl/__init__.py',helper], 'pins':PINS,
        'preparer_sha256':sha(Path(__file__).read_bytes()),
        'actual_evidence_required':'同Engine ARMED与多请求FIRST_SELECTED，原服务64/0、QGQA、DB四端/KV可比',
        'limits':['CPU片段含guard净省不等服务收益；一次短pair不证明稳定性或新组合accuracy',
                  '原422 COPY/FULL/q0external保持原方法；短4K无FULL事务不是失败','不叠425或97f H2D候选']}
    with receipt.open('x',encoding='utf-8') as file:
        json.dump(data,file,ensure_ascii=False,indent=2);file.write('\n')
    print(json.dumps({'source':str(output),'receipt':str(receipt),'source_count':423}))


if __name__=='__main__': main()
