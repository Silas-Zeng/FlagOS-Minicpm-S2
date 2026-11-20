"""只记录main526当前服务的真实backbone图、34 native和AOT。"""
import ast
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

import cache_gate as gate
import qualification as q

HERE = Path(__file__).resolve().parent
MODEL = Path('/workspace/MiniCPM5-2B/config.json')


def read_state(run, source, env):
    manifest = q.read(HERE / 'source-manifest.json')
    q.require(env.get('VLLM_DISABLE_COMPILE_CACHE') == '0'
        and not any(k in env for k in ('VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR')), '必须使用默认缓存')
    receipt_path = Path(env['BIV150_RESUME_NATIVE_RECEIPT'])
    q.require(q.sha(receipt_path) == env['BIV150_RESUME_NATIVE_RECEIPT_SHA256'], 'receipt变化')
    receipt = q.read(receipt_path)
    library = Path(env['BIV150_NATIVE_W8A8_LIBRARY']).resolve(strict=True)
    q.require(library == Path(receipt['runtime_library']).resolve(strict=True)
        and q.sha(library) == receipt['library_sha256'] == q.SO, '实际native不符')
    helper = source / 'vllm_fl/compile_semantics.py'
    q.require(q.sha(helper) == manifest['files']['vllm_fl/compile_semantics.py']['sha256'], '526 helper变化')
    semantics = q.load(helper, 'ffn_verify_semantics')
    expected = semantics.build_fingerprint(SimpleNamespace(model_config=SimpleNamespace(
        hf_config=SimpleNamespace(**q.read(MODEL)))), 'iluvatar', package_root=source / 'vllm_fl',
        environ=env, abi={'torch': receipt['abi']['torch_version'], 'cxx11_abi': receipt['abi']['cxx11_abi']})
    text = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'server.log').read_text(encoding='utf-8', errors='replace'))
    def markers(name):
        return [json.loads(line.split(name+' ', 1)[1]) for line in text.splitlines() if name+' ' in line]
    fps = markers('BIV150_COMPILE_SEMANTICS')
    q.require(expected and expected['native_enabled'] and fps and all(x == expected for x in fps), '实际526指纹不符')
    root = (Path(env.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'vllm/torch_compile_cache').resolve()
    dirs = {Path(p.strip()).resolve() for p in re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)}
    q.require(dirs and all(p.is_relative_to(root) and p.name == 'backbone' for p in dirs), '未知/越界实际prefix')
    paths = re.findall(r'Directly load AOT compilation from path (\S+)', text) + re.findall(r'saved AOT compiled function to (\S+)', text)
    aot = {}
    for name in paths:
        path = Path(name).resolve(strict=True)
        q.require(path.is_file() and path.is_relative_to(root/'torch_aot_compile'), 'AOT越界')
        aot[str(path)] = q.sha(path)
    return dict(manifest=manifest, fingerprint=expected, directories=dirs, aot=aot,
        receipt_sha256=q.sha(receipt_path), model_config_sha256=q.sha(MODEL), native_library_sha256=q.SO)


def record_graph(directory, output):
    directory = Path(directory)
    graph = directory/'computation_graph.py'
    text = graph.read_text(encoding='utf-8')
    native = gate.native_graph(text)
    entries = ast.literal_eval((directory/'vllm_compile_cache.py').read_text(encoding='utf-8'))
    q.require(isinstance(entries, dict) and entries, '实际compile entries为空')
    handles = []
    for item in entries.values():
        handle = item['graph_handle']
        q.require(isinstance(handle, (tuple,list)) and len(handle) == 2, 'handle格式')
        path = Path(handle[1]).resolve(strict=True)
        q.require(path.is_file() and path.is_relative_to(directory), 'handle越界')
        handles.append(dict(cache_key=item['cache_key'], graph_handle=list(handle)))
    output.mkdir(parents=True, exist_ok=False)
    for name in ('computation_graph.py','vllm_compile_cache.py','cache_key_factors.json'):
        shutil.copyfile(directory/name, output/name)
    return dict(directory=str(directory), graph_sha256=q.sha(graph), native=native,
        compiled_handles=handles, metadata_sha256={p.name:q.sha(p) for p in output.iterdir() if p.is_file()})


def capture(run, source, env, prior_control=None):
    import affine_qualification as aq
    state = read_state(run, source, env)
    dirs = state.pop('directories')
    q.require(len(dirs) == 1 and len(state['aot']) == 1, '必须唯一backbone与AOT')
    graph = record_graph(next(iter(dirs)), run/'model-path/backbone')
    raw = dict(valid=True, source_count=state['manifest']['source_count'], tree=state['manifest']['tree'],
        fingerprint=state['fingerprint'], graph=graph, aot_files=state['aot'])
    evidence = aq.normalize_graph(raw,state['model_config_sha256'],state['receipt_sha256'])
    if prior_control is not None:
        prior_control = Path(prior_control).resolve(strict=True)
        prior_state = q.read(prior_control/'state.json')
        q.require(prior_state.get('completed') is True and prior_state.get('validation_completed') is True
            and prior_state.get('tree') == evidence['tree'] and prior_state.get('source_count') == 527,
            '前置不是成功的同源模型初筛')
        prior_run = Path(prior_state['run'])
        prior_raw = q.read(prior_run/'model-path/evidence.json')
        prior = aq.normalize_graph(prior_raw,state['model_config_sha256'],state['receipt_sha256'])
        text = (run/'server.log').read_text(encoding='utf-8',errors='replace')
        loaded = re.findall(r'Directly load AOT compilation from path (\S+)',text)
        q.require(prior_state['model_path'] == prior_raw and prior['fingerprint'] == evidence['fingerprint']
            and prior['graph_sha256'] == evidence['graph_sha256'] and prior['aot_files'] == evidence['aot_files']
            and loaded and gate.relative_handles(prior['compiled_handles'],prior['directory'])
            == gate.relative_handles(evidence['compiled_handles'],evidence['directory']),
            '本服务未复用已验同源FP/FX/AOT/handles')
        evidence['prior_control'] = str(prior_control)
    evidence['limitation'] = '复用已验同源模型初筛；当前测量与105准确率分别记录，不继承旧105结论'
    gate.save(run/'model-path/evidence.json',evidence)
    return evidence
