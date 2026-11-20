"""main594完整690文件原官方控制组；旧control只提供native/环境出处。"""
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
    main=read(HERE/'source-manifest.json')
    require(main['commit']==COMMIT and main['tree']==TREE and main['source_count']==690,'不是冻结main594完整690源码')
    origin=Path(origin)
    require(origin.is_absolute() and not origin.is_symlink(),'要求实际绝对源码目录')
    origin=origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT/'code') and origin!=ROOT/'code','源码越界')
    blobs={p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in main['files'].items()}
    hashes={p:v['sha256'] for p,v in main['files'].items()}
    require(lifecycle.source_maps(origin)==(blobs,hashes),'main594完整源码身份不符')
    build,_,_=native
    require(all(hashes[p]==v for p,v in build['source_sha256'].items()),'新main与原native构建源码不符')
    reference['files'][str(HERE/'source-manifest.json')]=sha(HERE/'source-manifest.json')
    # 只复用中断run的初始DB原件，不继承其completed/16K性能资格。
    previous=ROOT/'official/20261026T154111Z-main594-official-control-four-rounds-control'
    initial=previous/'database-original.sqlite'
    require(sha(initial)==read(previous/'state.json')['database_before_sha256']
        and sha(Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db'))==sha(initial),
        '必须先恢复154111原初始DB；本入口不自行改写或修复DB')
    reference['files'][str(initial)]=sha(initial)
    reference['split_service_protocol']='main594重启后4K两轮诊断；同690源/native14f/初始DB，不继承四轮/稳定均值资格'
    reference.update(main_tree=TREE,base_commit=COMMIT,main_commit=COMMIT,source_count=690,
        accuracy_inherited=False,old_control_scope='仅已核native14f/环境与生命周期来源；不继承旧main性能或准确率，本轮建立本站main594控制组')
    return (origin,blobs,hashes,TREE),native,reference
def check_environment(source,env,build,graph):
    require(sha(MODEL)==graph['model_config_sha256'],'模型config变化')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE')=='0' and not any(k in env for k in ('VLLM_CACHE_ROOT','TORCHINDUCTOR_CACHE_DIR')),'默认缓存策略变化')
    require(not any(k.startswith('VLLM_FL_BIV150_') for k in env),'不能以环境覆盖新main生产默认行为')
    helper=source/'vllm_fl/compile_semantics.py'
    require(sha(helper)=='1626fe91d450a207eda44e8e1238d64dfce21e272c04df779324d0674d3b7727','main594 compile语义变化')
    semantics=load(helper,'main594_semantics')
    config=SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected=semantics.build_fingerprint(config,'iluvatar',package_root=source/'vllm_fl',environ=env,abi={'torch':build['abi']['torch_version'],'cxx11_abi':build['abi']['cxx11_abi']})
    require(expected and expected['native_enabled'] and expected!=graph['fingerprint'],'main594源码未进入native-on新编译身份')
    return expected
