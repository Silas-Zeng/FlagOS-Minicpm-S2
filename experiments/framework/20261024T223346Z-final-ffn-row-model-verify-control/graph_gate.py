"""先保存原路图，再绑定新增FFN prefix/AOT；全程只静态读取实际缓存。"""
import ast
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

import cache_gate as gate
import ffn_graph
import qualification as q

HERE = Path(__file__).resolve().parent
TAG = 'biv150_final_ffn_rows'
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
    q.require(q.sha(helper) == manifest['files']['vllm_fl/compile_semantics.py']['sha256'], '527 helper变化')
    semantics = q.load(helper, 'ffn_verify_semantics')
    expected = semantics.build_fingerprint(SimpleNamespace(model_config=SimpleNamespace(
        hf_config=SimpleNamespace(**q.read(MODEL)))), 'iluvatar', package_root=source / 'vllm_fl',
        environ=env, abi={'torch': receipt['abi']['torch_version'], 'cxx11_abi': receipt['abi']['cxx11_abi']})
    text = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'server.log').read_text(encoding='utf-8', errors='replace'))
    def markers(name):
        return [json.loads(line.split(name+' ', 1)[1]) for line in text.splitlines() if name+' ' in line]
    fps = markers('BIV150_COMPILE_SEMANTICS')
    q.require(expected and expected['native_enabled'] and fps and all(x == expected for x in fps), '实际527指纹不符')
    installs = markers('BIV150_FINAL_FFN_ROWS_INSTALL')
    q.require(installs and all(x.get('installed') is True and x.get('backend_prefix') == TAG
        and x.get('shared_weights') is True and x.get('dense_output') is True for x in installs), '末层安装不符')
    root = (Path(env.get('XDG_CACHE_HOME', str(Path.home()/'.cache'))) / 'vllm/torch_compile_cache').resolve()
    dirs = {Path(p.strip()).resolve() for p in re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)}
    q.require(dirs and all(p.is_relative_to(root) and p.name in ('backbone', TAG) for p in dirs), '未知/越界实际prefix')
    paths = re.findall(r'Directly load AOT compilation from path (\S+)', text) + re.findall(r'saved AOT compiled function to (\S+)', text)
    aot = {}
    for name in paths:
        path = Path(name).resolve(strict=True)
        q.require(path.is_file() and path.is_relative_to(root/'torch_aot_compile'), 'AOT越界')
        aot[str(path)] = q.sha(path)
    return dict(manifest=manifest, fingerprint=expected, directories=dirs, aot=aot,
        installs=installs, selected=markers('BIV150_FINAL_FFN_ROWS_FIRST_SELECTED'),
        receipt_sha256=q.sha(receipt_path), model_config_sha256=q.sha(MODEL), native_library_sha256=q.SO)


def record_graph(directory, output, new=False):
    directory = Path(directory)
    graph = directory/'computation_graph.py'
    text = graph.read_text(encoding='utf-8')
    native = gate.native_graph(text)
    sparse = ffn_graph.inspect_graph(text) if new else None
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
    return dict(directory=str(directory), graph_sha256=q.sha(graph), native=native, ffn=sparse,
        compiled_handles=handles, metadata_sha256={p.name:q.sha(p) for p in output.iterdir() if p.is_file()})


def capture_fallback(run, source, env):
    state = read_state(run, source, env)
    dirs = state.pop('directories')
    q.require(len(dirs) == 1 and next(iter(dirs)).name == 'backbone' and len(state['aot']) == 1
        and not state['selected'], '串行S1请求不应提前命中末层路径')
    graph = record_graph(next(iter(dirs)), run/'model-path/backbone')
    result = dict(valid=True, source_count=527, tree=state['manifest']['tree'],
        fingerprint=state['fingerprint'], graph=graph, aot_files=state['aot'],
        limitation='四串行语义仅覆盖原路')
    gate.save(run/'model-path/fallback-evidence.json', result)
    return result


def capture(run, source, env, before):
    state = read_state(run, source, env)
    dirs = state.pop('directories')
    q.require(len(dirs) == 2 and {p.name for p in dirs} == {'backbone',TAG}, '未形成两个实际prefix')
    q.require(before['fingerprint'] == state['fingerprint'] and before['tree'] == state['manifest']['tree'], '同服务身份变化')
    original = Path(before['graph']['directory'])
    q.require(original in dirs and q.sha(original/'computation_graph.py') == before['graph']['graph_sha256'], '原路图改变')
    entries = ast.literal_eval((original/'vllm_compile_cache.py').read_text(encoding='utf-8'))
    current_handles = [dict(cache_key=x['cache_key'],graph_handle=list(x['graph_handle'])) for x in entries.values()]
    q.require(gate.relative_handles(current_handles,original) == gate.relative_handles(before['graph']['compiled_handles'],original), '原路handles变化')
    q.require(len(state['aot']) == 2 and all(state['aot'].get(p) == sha for p,sha in before['aot_files'].items()), '双AOT未闭合')
    new_aot = {p:sha for p,sha in state['aot'].items() if p not in before['aot_files']}
    q.require(len(new_aot) == 1, '新增prefix没有唯一新增实际AOT')
    q.require(state['selected'] and all(x.get('runtime_mode') == 'NONE' and x.get('backend_prefix') == TAG
        and 2 <= x['S'] <= 64 and x['S'] < x['M'] <= 2048 and x.get('original_gpu_indices') is True
        and x.get('original_runner_gather') is True and x.get('o_proj_pruned') is False for x in state['selected']), '缺少真实mixed选中证据')
    graph = record_graph(next(p for p in dirs if p.name == TAG), run/'model-path'/TAG, new=True)
    result = dict(valid=True, source_count=527, tree=state['manifest']['tree'], fingerprint=state['fingerprint'],
        original=before, selected_graph=graph, selected=state['selected'], aot_files=state['aot'], selected_aot_files=new_aot,
        installed=state['installs'], receipt_sha256=state['receipt_sha256'], model_config_sha256=state['model_config_sha256'],
        native_library_sha256=q.SO,
        mixed_q_proof='固定生产_cpu_plan要求min(q)=1、max(q)>1；原GPU索引直接传入，不读回',
        limitation='仅同服务最短语义及真实双图门，不是105准确率/性能成绩；额外workspace与dense回填仍需模型实测')
    gate.save(run/'model-path/evidence.json', result)
    return result
