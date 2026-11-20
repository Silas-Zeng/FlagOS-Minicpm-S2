"""只复用同源 affine 模型初筛成功记录；不发送新请求。"""
from pathlib import Path
import cache_gate as gate
import qualification as q

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
TREE = '41449b98509c49a370c8878187054514e1a1b069'


def normalize_graph(raw, model_sha, receipt_sha):
    nested = raw['graph']
    return dict(valid=raw['valid'], source_count=raw['source_count'], tree=raw['tree'],
        fingerprint=raw['fingerprint'], graph=nested['native'],
        graph_sha256=nested['graph_sha256'], directory=nested['directory'],
        compiled_handles=nested['compiled_handles'], cache_metadata_sha256=nested['metadata_sha256'],
        aot_files=[dict(path=p, sha256=h) for p,h in sorted(raw['aot_files'].items())],
        model_config_sha256=model_sha, native_library_sha256=q.SO, receipt_sha256=receipt_sha)


def qualify(control, life):
    control = Path(control)
    q.require(not control.is_symlink(), '模型验证control不能为symlink')
    control = control.resolve(strict=True)
    q.require(control.is_relative_to(ROOT/'framework') and control.name.endswith('-control'), '非本实例模型门')
    state = q.read(control/'state.json')
    q.require(all(state.get(k) is True for k in ('completed','validation_completed','database_restored',
                  'source_unchanged','native_unchanged')) and not state.get('cleanup_errors')
        and not state.get('error') and (control/'exit-code').read_text().strip() == '0'
        and state.get('tree') == TREE and state.get('source_count') == 527
        and state.get('base_commit') == q.COMMIT and Path(state['control']) == control,
        '同源 affine 模型门未成功收尾')
    run = Path(state['run'])
    q.require(run == control.with_name(control.name[:-8]) and not run.is_symlink()
        and q.read(run/'result.json') == state and (run/'exit-code').read_text().strip() == '0', '模型门run/result未闭合')
    for name,pin in q.read(HERE/'verification-asset-pins.json').items():
        q.require(q.sha(control/name) == pin, '模型门入口变化: '+name)
    rows = q.read(run/'requests.json')
    expected = [('add',85),('multiply',323),('divide',12),('long-prefill',95)]
    q.require(state.get('semantic_requests') == rows and len(rows) == 4
        and [(r.get('name'),r.get('expected')) for r in rows] == expected
        and all(r.get('correct') is True for r in rows)
        and rows[-1]['usage'].get('prompt_tokens',0) >= 4096, '原四题资格不完整')
    for row in rows:
        response = q.read(run/(row['name']+'-response.json'))
        q.require(gate.final_answer(response['choices'][0]['message']['content'],row['expected']) == row['visible']
            and response['usage'] == row['usage'], '四题与原响应不符')
    manifest = q.read(HERE/'source-manifest.json')
    q.require(manifest['tree'] == TREE and manifest['source_count'] == 527
        and manifest['base_commit'] == q.COMMIT and manifest['base_tree'] == q.TREE, '冻结527来源变化')
    blobs = {p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in manifest['files'].items()}
    hashes = {p:v['sha256'] for p,v in manifest['files'].items()}
    origin = Path(state['source'])
    q.require(not origin.is_symlink() and origin.resolve(strict=True).is_relative_to(ROOT/'code'), '候选源根错误')
    origin = origin.resolve(strict=True)
    q.require(q.read(control/'source-git-blobs.json') == blobs and q.read(control/'source-sha256.json') == hashes
        and all(life.source_maps(p) == (blobs,hashes) for p in (origin,control/'plugin-source')), '已测源发生变化')
    selection = q.read(run/'affine-evidence.json')
    q.require(state.get('affine_evidence') == selection and selection.get('valid') is True
        and selection.get('tree') == TREE and selection.get('runtime_source_sha256')
        == hashes['vllm_fl/patches/biv150_attention_affine_pages.py'], '实际选中资格不符')
    q.require(selection['selected'] and all(all(r.get(k) is True for k in
        ('actual_requests','q_hoisted','cpu_descriptor_verified','device_binding_verified'))
        and r.get('graph_mode') == 'NONE' and r.get('epoch',0) > 0 for r in selection['selected']), '设备绑定原件不符')
    for name,pin in selection['evidence_files'].items():
        path = (run/name).resolve(strict=True)
        q.require(path.is_relative_to(run/'affine-binding') and q.sha(path) == pin, '设备绑定原件变化')
    raw = q.read(run/'model-path/evidence.json')
    graph = raw['graph']
    fx = run/'model-path/backbone/computation_graph.py'
    q.require(state.get('model_path') == raw and raw.get('valid') is True and raw.get('tree') == TREE
        and raw.get('source_count') == 527 and graph['graph_sha256'] == q.sha(fx)
        and graph['native'] == gate.native_graph(fx.read_text(encoding='utf-8'))
        and graph['native']['layers'] == list(range(4,38)) and raw['fingerprint']['native_enabled'] is True,
        '本服务实际native34/FP/backbone资格不符')
    for name,pin in graph['metadata_sha256'].items():
        q.require(Path(name).name == name and q.sha(run/'model-path/backbone'/name) == pin, '缓存原件变化')
    q.require(len(raw['aot_files']) == 1, '真实AOT非唯一')
    for name,pin in raw['aot_files'].items():
        path = Path(name).resolve(strict=True)
        q.require(path.is_relative_to(q.CACHE_ROOT/'torch_compile_cache/torch_aot_compile') and q.sha(path) == pin,
            '实际AOT变化')
    build = q.read(control/'native/build-manifest.original.json')
    receipt = q.read(control/'native/runtime-receipt.json')
    library,log = control/'native/biv150_native_w8a8.so', control/'native/build.log'
    q.require(build.get('exit_code') == 0 and build['library_sha256'] == q.SO and q.sha(library) == q.SO
        and q.sha(log) == build['build_log_sha256'] and receipt == dict(build,runtime_library=str(library))
        and all(hashes[p] == h for p,h in build['source_sha256'].items()), '实际native来源变化')
    reference = q.read(control/'qualification-reference.json')
    q.check_reference(reference)
    model_sha = reference['graph']['model_config_sha256']
    q.require(q.sha(q.MODEL) == model_sha, '模型config变化')
    return origin,blobs,hashes,manifest,normalize_graph(raw,model_sha,q.sha(control/'native/runtime-receipt.json')),build,library,log
