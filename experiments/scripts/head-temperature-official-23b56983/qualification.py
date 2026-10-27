"""main56完整807文件原官方控制组；旧control只提供native/环境出处。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('prior_native_qualification',HERE/'base_qualification.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
ROOT,MODEL,SO=base.ROOT,base.MODEL,base.SO
COMMIT='56f1838192abc940b3fb9accef490022ac125000'
TREE='1e9af62de05aad53ee61c814054624de8e252dd0'
read,sha,require,load,assets,check_reference=base.read,base.sha,base.require,base.load,base.assets,base.check_reference
def qualify(control,lifecycle,origin):
    _,native,reference=base.qualify(control,lifecycle)
    from baseline_reference import capture as baseline_capture
    baseline=baseline_capture()
    main=read(HERE/'team-source-manifest.json');candidate=read(HERE/'source-manifest.json')
    expected={'vllm_fl/worker/model_runner.py': '42cdf64d8af025ecd2762e586ca592daf3d760a69e204e01ce930729f74f2c6e', 'vllm_fl/compile_semantics.py': '2f7ae86405b35d6ff85e38f3f40f7d3491e4ba15673a4ffdc7d3ba8897a8d5ae', 'vllm_fl/patches/biv150_compute_order.py': '80609b3cc79933d78ed869a21c24c9c800e5423172db27c810964ffff1c444aa', 'vllm_fl/patches/biv150_lm_head_temperature.py': '560fdeaf25b92616fd073db083dee240d5857cc9a062532fbc9c76d053126afa', 'vllm_fl/patches/biv150_lm_head_temperature_kernel.py': '4c800693a2ae134fc580382d4166091b4c48e96dc2b7838ab417da7094cb2537'}
    changed=sorted(p for p in main['files'].keys()|candidate['files'].keys()
        if (main['files'].get(p) or {}).get('sha256')!=(candidate['files'].get(p) or {}).get('sha256'))
    require(candidate['base_commit']==COMMIT and candidate['source_count']==809 and candidate['tree']=='8125c3d9efc83afdd63f7174cea3374de2da24ac'
        and changed==sorted(expected) and all(candidate['files'][p]['sha256']==v for p,v in expected.items()),'候选须为受审809文件/5精确差分')
    require(main['commit']==COMMIT and main['tree']==TREE and main['source_count']==807,'冻结main56控制源不符')
    origin=Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(),'要求实际绝对源码目录')
    origin=origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin!=ROOT/'code','源码越界')
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in candidate['files'].items()}
    hashes={p:v['sha256'] for p,v in candidate['files'].items()}
    require(lifecycle.source_maps(origin)==(blobs,hashes),'head候选完整809源码身份不符')
    build,_,_=native
    require(all(hashes[p]==v for p,v in build['source_sha256'].items()),'新main与原native构建源码不符')
    for name in ('source-manifest.json','team-source-manifest.json'):
        reference['files'][str(HERE/name)]=sha(HERE/name)
    reference['files'].update(baseline['files'])
    reference.update(main_tree=TREE,base_commit=COMMIT,candidate_tree=candidate['tree'],source_count=809,
        candidate_changed_files=changed,accuracy_inherited=False,matched_baseline=baseline,
        old_control_scope='旧526仅native14f来源；性能只对052425 main56/native14f完整4K控制')
    return (origin,blobs,hashes,candidate['tree']),native,reference

def check_environment(source,env,build,graph):
    require(sha(MODEL)==graph['model_config_sha256'],'模型config变化')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE')=='0' and not any(k in env for k in ('VLLM_CACHE_ROOT','TORCHINDUCTOR_CACHE_DIR')),'默认缓存策略变化')
    require(not any(k.startswith('VLLM_FL_BIV150_') for k in env),'不能以环境覆盖新main生产默认行为')
    helper=source/'vllm_fl/compile_semantics.py'
    require(sha(helper)=='2f7ae86405b35d6ff85e38f3f40f7d3491e4ba15673a4ffdc7d3ba8897a8d5ae','main56 compile语义变化')
    semantics=load(helper,'main56_semantics')
    config=SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected=semantics.build_fingerprint(config,'iluvatar',package_root=source/'vllm_fl',environ=env,abi={'torch':build['abi']['torch_version'],'cxx11_abi':build['abi']['cxx11_abi']})
    require(expected and expected['native_enabled'] and expected!=graph['fingerprint'],'main56源码未进入native-on新编译身份')
    return expected
