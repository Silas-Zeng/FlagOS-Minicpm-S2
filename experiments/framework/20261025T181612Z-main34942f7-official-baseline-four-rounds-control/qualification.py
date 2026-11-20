"""完整618源码与旧native资格复用；接受干净团队34942f7，不包含本方候选。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('simt_prior_qualification',HERE/'base_qualification.py')
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
ROOT,MODEL,SO=base.ROOT,base.MODEL,base.SO
COMMIT='34942f7e28da5c954ab05878dec75807da9d7a93'
REL='vllm_fl/patches/biv150_gqa_decode.py'
TEAM_PRODUCTION = {'vllm_fl/compile_semantics.py': '66cfa4a34a4040f2334fc5c05dba782e773fa9c09a0d2750a90b56ef46cf0ef1', 'vllm_fl/patches/biv150_compute_order.py': '35bfd13a7ff214d7a9e0aa7b162dd287980dded074e1eb37900095ed3f522053', 'vllm_fl/patches/biv150_stable_small_o.py': 'c5a2dd6c69c514531fee4145621e51bd4e41c0d784f4d4e086fe48aad98104ba', 'vllm_fl/worker/model_runner.py': 'cbbbabcea66663b033f2209febc55e75a9e14ac72d1693173d9d4aad1be7fac6'}
read,sha,require,load,assets,check_reference=base.read,base.sha,base.require,base.load,base.assets,base.check_reference


def qualify(control,lifecycle,origin):
    old_identity,native,reference=base.qualify(control,lifecycle)
    main=read(HERE/'team-source-manifest.json'); candidate=read(HERE/'source-manifest.json')
    require(main['commit']==COMMIT and candidate['commit']==COMMIT and candidate['source_count']==618,
            '不是冻结34942f7候选')
    expected = {}
    changed=sorted(p for p in main['files'].keys()|candidate['files'].keys() if main['files'].get(p)!=candidate['files'].get(p))
    require(changed==sorted(expected) and all(candidate['files'][p]['sha256']==v for p,v in expected.items()),
            '必须与完整干净34942f7团队源码完全一致')
    origin=Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(),'要求实际绝对源码目录')
    origin=origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin!=ROOT/'code','源码越界')
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in candidate['files'].items()}
    hashes={p:v['sha256'] for p,v in candidate['files'].items()}
    require(lifecycle.source_maps(origin)==(blobs,hashes),'完整候选源码身份不符')
    _,old_blobs,_,_=old_identity
    main_blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in main['files'].items()}
    production_delta=sorted(p for p in old_blobs.keys()|main_blobs.keys()
        if old_blobs.get(p)!=main_blobs.get(p) and not p.startswith(('docs/','tools/')))
    require(production_delta==sorted(TEAM_PRODUCTION) and
        all(main['files'][p]['sha256']==digest for p,digest in TEAM_PRODUCTION.items()),
        '团队34942f7只能增加已合入PR51的四项精确生产变化')
    for name in ('source-manifest.json','team-source-manifest.json'):
        reference['files'][str(HERE/name)]=sha(HERE/name)
    reference.update(candidate_tree=candidate['tree'],base_commit=COMMIT,candidate_commit=COMMIT,
                     source_count=618,candidate_changed_files=changed,accuracy_inherited=False,
                     old_control_scope='仅原native/环境与生命周期来源，不继承34942f7性能或准确率',
                     team_production_delta=production_delta)
    return (origin,blobs,hashes,candidate['tree']),native,reference


def check_environment(source,env,build,graph):
    require(sha(MODEL)==graph['model_config_sha256'],'模型config变化')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE')=='0' and
            not any(k in env for k in ('VLLM_CACHE_ROOT','TORCHINDUCTOR_CACHE_DIR')),'默认缓存策略变化')
    require(not any(k.startswith('VLLM_FL_BIV150_') for k in env),'不能以环境覆盖生产默认行为')
    helper=source/'vllm_fl/compile_semantics.py'
    require(sha(helper)==TEAM_PRODUCTION['vllm_fl/compile_semantics.py'],'未保留团队新compile语义')
    semantics=load(helper,'simt_semantics')
    config=SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected=semantics.build_fingerprint(config,'iluvatar',package_root=source/'vllm_fl',environ=env,
        abi={'torch':build['abi']['torch_version'],'cxx11_abi':build['abi']['cxx11_abi']})
    require(expected and expected['native_enabled'] and expected!=graph['fingerprint'],
            '新团队源码未进入新的native-on编译身份')
    return expected
