"""main594固定寻址691候选；两档控制证据闭合后才允许分档新服务启动。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prior_native_qualification',HERE/'base_qualification.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
ROOT,MODEL,SO=base.ROOT,base.MODEL,base.SO
COMMIT='594ae2a9d17aadc4587ad54ade2b34e17f4af990'
TREE='5a406f3c5b8d35d4ba9f3d8493270d67a9bd57a7'
read,sha,require,load,assets,check_reference=base.read,base.sha,base.require,base.load,base.assets,base.check_reference
def qualify(control,lifecycle,origin):
    _,native,reference=base.qualify(control,lifecycle)
    from baseline_reference import capture as baseline_capture
    baseline=baseline_capture()
    main=read(HERE/'team-source-manifest.json')
    candidate=read(HERE/'source-manifest.json')
    expected={'vllm_fl/patches/biv150_small_out_lowering.py':'eb78c1bf8d7c2ea6aaa848610bdd1362ec300d00901cba42c505a8484c904772','vllm_fl/compile_semantics.py':'219ef9748c20786fad0fcaf8f09a792d8dc9e0f6d66d0722e4475357dc9aba7d','vllm_fl/patches/biv150_m64_fixed_address.py':'4c5c5bb7af322230a38feeae6ea4eac9aeed6590a49e2e6752b13eb8bb17b3c6'}
    changed=sorted(p for p in main['files'].keys()|candidate['files'].keys() if main['files'].get(p)!=candidate['files'].get(p))
    require(candidate['base_commit']==COMMIT and candidate['source_count']==691 and candidate['tree']=='260f6527a52a5ba51bd3ffe42414440e6f81a13b'
        and changed==sorted(expected) and all(candidate['files'][p]['sha256']==v for p,v in expected.items()),'候选只能有已审691文件/3差分')
    require(main['commit']==COMMIT and main['tree']==TREE and main['source_count']==690,'不是冻结main594完整690源码')
    origin=Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(),'要求实际绝对源码目录')
    origin=origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin!=ROOT/'code','源码越界')
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in candidate['files'].items()}
    hashes={p:v['sha256'] for p,v in candidate['files'].items()}
    require(lifecycle.source_maps(origin)==(blobs,hashes),'main594固定寻址完整691候选源码身份不符')
    build,_,_=native
    require(all(hashes[p]==v for p,v in build['source_sha256'].items()),'新main与原native构建源码不符')
    for name in ('source-manifest.json','team-source-manifest.json'):
        reference['files'][str(HERE/name)]=sha(HERE/name)
    reference['files'].update(baseline['files'])
    reference.update(main_tree=TREE,base_commit=COMMIT,candidate_tree=candidate['tree'],source_count=691,
        candidate_changed_files=changed,accuracy_inherited=False,matched_baseline=baseline,
        old_control_scope='旧526仅native14f来源；4K对154111原有效四轮，16K对164443独立控制，逐档新服务')
    return (origin,blobs,hashes,candidate['tree']),native,reference

def check_environment(source,env,build,graph):
    require(sha(MODEL)==graph['model_config_sha256'],'模型config变化')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE')=='0' and not any(k in env for k in ('VLLM_CACHE_ROOT','TORCHINDUCTOR_CACHE_DIR')),'默认缓存策略变化')
    require(not any(k.startswith('VLLM_FL_BIV150_') for k in env),'不能以环境覆盖新main生产默认行为')
    helper=source/'vllm_fl/compile_semantics.py'
    require(sha(helper)=='219ef9748c20786fad0fcaf8f09a792d8dc9e0f6d66d0722e4475357dc9aba7d','main594 compile语义变化')
    semantics=load(helper,'main594_semantics')
    config=SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected=semantics.build_fingerprint(config,'iluvatar',package_root=source/'vllm_fl',environ=env,abi={'torch':build['abi']['torch_version'],'cxx11_abi':build['abi']['cxx11_abi']})
    require(expected and expected['native_enabled'] and expected!=graph['fingerprint'],'main594源码未进入native-on新编译身份')
    return expected
