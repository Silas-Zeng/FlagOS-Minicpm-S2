"""完整603源码与旧native资格复用；仅允许原四行GQA.cg和三条strict hash闭合。"""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('cg_prior_qualification',HERE/'base_qualification.py')
base=importlib.util.module_from_spec(spec); spec.loader.exec_module(base)
ROOT,MODEL,SO=base.ROOT,base.MODEL,base.SO
COMMIT='0915f01d5efc2b31af65182ddb87e2d2f62bab0c'
REL='vllm_fl/patches/biv150_gqa_decode.py'
read,sha,require,load,assets,check_reference=base.read,base.sha,base.require,base.load,base.assets,base.check_reference


def qualify(control,lifecycle,origin):
    old_identity,native,reference=base.qualify(control,lifecycle)
    main=read(HERE/'team-source-manifest.json'); candidate=read(HERE/'source-manifest.json')
    require(main['commit']==COMMIT and candidate['base_commit']==COMMIT and candidate['source_count']==603,
            '不是冻结0915候选')
    expected = {'vllm_fl/patches/biv150_gqa_decode.py': '1043497f0bb0049ba42ae4a01d78bebf88cf632bbfada700c400b6d1db86c44c', 'vllm_fl/patches/biv150_q_fragment_service.py': '70c51d8ac14b82d8a39d9ec6b40902f22b67755fd41c6bc807d677425e73fa8e', 'vllm_fl/patches/biv150_compute_order.py': '55bd9cdd9e57d6dc0ee329aa03ba1415ae3bb987b448408dcff87f1f1e889482'}
    changed=sorted(p for p in main['files'].keys()|candidate['files'].keys() if main['files'].get(p)!=candidate['files'].get(p))
    require(changed==sorted(expected) and all(candidate['files'][p]['sha256']==v for p,v in expected.items()),
            '只能改已测cg四行及Q-hoist/compute-order三条hash闭合')
    origin=Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(),'要求实际绝对源码目录')
    origin=origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin!=ROOT/'code','源码越界')
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in candidate['files'].items()}
    hashes={p:v['sha256'] for p,v in candidate['files'].items()}
    require(lifecycle.source_maps(origin)==(blobs,hashes),'完整候选源码身份不符')
    _,old_blobs,_,_=old_identity
    main_blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in main['files'].items()}
    require(all(p.startswith(('docs/','tools/')) for p in old_blobs.keys()|main_blobs.keys()
                if old_blobs.get(p)!=main_blobs.get(p)), '0915相对原native来源存在未声明生产变化')
    for name in ('source-manifest.json','team-source-manifest.json'):
        reference['files'][str(HERE/name)]=sha(HERE/name)
    reference.update(candidate_tree=candidate['tree'],base_commit=COMMIT,candidate_commit=None,
                     source_count=603,candidate_changed_files=changed,accuracy_inherited=False)
    return (origin,blobs,hashes,candidate['tree']),native,reference


def check_environment(source,env,build,graph):
    require(sha(MODEL)==graph['model_config_sha256'],'模型config变化')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE')=='0' and
            not any(k in env for k in ('VLLM_CACHE_ROOT','TORCHINDUCTOR_CACHE_DIR')),'默认缓存策略变化')
    require(not any(k.startswith('VLLM_FL_BIV150_') for k in env),'不能以环境覆盖生产默认行为')
    helper=source/'vllm_fl/compile_semantics.py'
    require(sha(helper)==base.SEMANTICS,'编译语义helper未复用原件')
    semantics=load(helper,'cg_semantics')
    config=SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected=semantics.build_fingerprint(config,'iluvatar',package_root=source/'vllm_fl',environ=env,
        abi={'torch':build['abi']['torch_version'],'cxx11_abi':build['abi']['cxx11_abi']})
    require(expected and expected['native_enabled'] and expected!=graph['fingerprint'],
            '新GQA源码未进入新的native-on编译身份')
    return expected
