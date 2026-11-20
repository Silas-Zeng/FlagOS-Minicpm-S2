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


def capture_original(run, source, env):
    state = read_state(run, source, env)
    dirs = state.pop('directories')
    q.require(len(dirs) == 1 and next(iter(dirs)).name == 'backbone' and len(state['aot']) == 1
        and not state['selected'], 'ready时必须只有原profile图，尚无真实选行')
    graph = record_graph(next(iter(dirs)), run/'model-path/backbone')
    result = dict(valid=True, source_count=527, tree=state['manifest']['tree'],
        fingerprint=state['fingerprint'], graph=graph, aot_files=state['aot'],
        limitation='ready后、首个请求前保存原backbone，未据此认定语义或新入口通过')
    gate.save(run/'model-path/original-evidence.json', result)
    return result


def check_selected(events, required_classes, stage):
    allowed = {'S1', 'S_GE_2', 'S1_AFTER_S_GE_2'}
    q.require(events and len(events) <= 3 and required_classes <= allowed, '选择事件缺失/过量')
    classes = [x.get('sample_class') for x in events]
    q.require(len(set(classes)) == len(classes) and set(classes) <= allowed
        and required_classes <= set(classes), '实际选择类别未闭合')
    q.require(classes[0] == 'S1' and events[0]['M'] == 2048
        and events[0]['selection_ordinal'] == 1, '首编未实际走长prefill M2048/S1')
    if stage == 's1-first':
        q.require(classes == ['S1'], '前三串行请求意外出现多请求选择')
    ordinals = []
    for item in events:
        s, m = item['S'], item['M']
        lens = item.get('scheduled_query_lens')
        q.require(item.get('runtime_mode') == 'NONE' and item.get('backend_prefix') == TAG
            and 1 <= s <= 64 and s < m <= 2048 and item.get('original_gpu_indices') is True
            and item.get('original_runner_gather') is True and item.get('o_proj_pruned') is True
            and item.get('unbacked_samples') is True, '真实unbacked选择边界不符')
        q.require(isinstance(lens, list) and len(lens) == s and all(type(x) is int and x > 0 for x in lens)
            and sum(lens) == m, '选择事件CPU qlens不闭合')
        q.require(item.get('scheduled_mode') == ('mixed' if min(lens) == 1 else 'prefill'), 'prefill/mixed记录不符')
        q.require((s == 1) == (item['sample_class'] != 'S_GE_2'), '事件类别与S不符')
        ordinal = item.get('selection_ordinal')
        q.require(type(ordinal) is int and ordinal >= 1, '选择序号无效')
        ordinals.append(ordinal)
    q.require(ordinals == sorted(set(ordinals)), '实际选择事件无序/重复')
    if 'S1_AFTER_S_GE_2' in classes:
        q.require('S_GE_2' in classes and classes.index('S1_AFTER_S_GE_2') > classes.index('S_GE_2'),
            '缺真实S1→S>=2→S1顺序')
    return classes


def same_selected_graph(previous, graph, aot):
    old = previous['selected_graph']
    q.require(old['directory'] == graph['directory'] and old['graph_sha256'] == graph['graph_sha256'],
        '跨S生成新FX/换prefix')
    q.require(gate.relative_handles(old['compiled_handles'], old['directory']) ==
        gate.relative_handles(graph['compiled_handles'], graph['directory']), '跨S编译handles变化')
    q.require(previous['aot_files'] == aot, '跨S新增/改变AOT')


def capture(run, source, env, before, *, stage, required_classes, previous=None):
    q.require(stage in ('s1-first', 's-ge-2', 's1-revisit'), '未知阶段')
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
    classes = check_selected(state['selected'], required_classes, stage)
    graph = record_graph(next(p for p in dirs if p.name == TAG), run/'model-path'/stage/TAG, new=True)
    if previous is not None:
        same_selected_graph(previous, graph, state['aot'])
    result = dict(valid=True, source_count=527, tree=state['manifest']['tree'], fingerprint=state['fingerprint'],
        original=before, selected_graph=graph, selected=state['selected'], aot_files=state['aot'], selected_aot_files=new_aot,
        installed=state['installs'], receipt_sha256=state['receipt_sha256'], model_config_sha256=state['model_config_sha256'],
        native_library_sha256=q.SO,
        stage=stage, observed_classes=classes, same_graph_across_samples=previous is not None,
        aot_restart_validated=False,
        q_proof='原GPU索引直接传入；正q/sum与S<M资格允许prefill或mixed，无GPU回读',
        revisit_proof='S1_AFTER_S_GE_2只记新module实际成功回访，可来自并发请求后段；最终除法另核语义与图稳定性',
        limitation='仅同服务六请求与实际双图/跨S门；未验证AOT重启、105准确率或端到端收益')
    gate.save(run/'model-path'/stage/'evidence.json', result)
    gate.save(run/'model-path/evidence.json', result)
    return result
