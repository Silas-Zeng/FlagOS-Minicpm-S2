"""当前528同服务的真实FX/AOT；首启不借用旧图，重用时核相同内容。"""
import ast
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

import cache_gate as gate
import qualification as q
import rope_graph

HERE = Path(__file__).resolve().parent
MODEL = Path('/workspace/MiniCPM5-2B/config.json')


def capture(run, source, env, prior_control=None):
    manifest = q.read(HERE / 'source-manifest.json')
    q.require(env.get('VLLM_DISABLE_COMPILE_CACHE') == '0'
              and not any(k in env for k in ('VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR')),
              '必须使用默认共享编译缓存')
    receipt_path = Path(env['BIV150_RESUME_NATIVE_RECEIPT'])
    q.require(q.sha(receipt_path) == env['BIV150_RESUME_NATIVE_RECEIPT_SHA256'], 'native receipt变化')
    receipt = q.read(receipt_path)
    library = Path(env['BIV150_NATIVE_W8A8_LIBRARY']).resolve(strict=True)
    q.require(library == Path(receipt['runtime_library']).resolve(strict=True)
              and q.sha(library) == receipt['library_sha256'] == q.SO, 'native实际库身份不符')
    helper = source / 'vllm_fl/compile_semantics.py'
    q.require(q.sha(helper) == manifest['files']['vllm_fl/compile_semantics.py']['sha256'], '528缓存helper变化')
    semantics = q.load(helper, 'rope_verify_semantics')
    config = SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**q.read(MODEL))))
    expected = semantics.build_fingerprint(config, 'iluvatar', package_root=source / 'vllm_fl', environ=env,
        abi={'torch': receipt['abi']['torch_version'], 'cxx11_abi': receipt['abi']['cxx11_abi']})
    q.require(expected and expected['native_enabled'] is True, '当前指纹未启用native')
    text = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'server.log').read_text(encoding='utf-8', errors='replace'))
    fingerprints = [json.loads(line.split('BIV150_COMPILE_SEMANTICS ', 1)[1])
                    for line in text.splitlines() if 'BIV150_COMPILE_SEMANTICS ' in line]
    q.require(fingerprints and all(x == expected for x in fingerprints), '真实服务指纹不等于528源码/SO/ABI')
    warmed = text.find('BIV150_ROPE_KV_WARMED ')
    installed = text.find('BIV150_ROPE_KV_INSTALL ')
    q.require(0 <= warmed < installed, '缺少安装前真实kernel预热证据')
    installs = [json.loads(line.split('BIV150_ROPE_KV_INSTALL ', 1)[1])
                for line in text.splitlines() if 'BIV150_ROPE_KV_INSTALL ' in line]
    q.require(installs and all(x.get('installed') is True and x.get('layers') == 42
              and x.get('kernel_warmed') is True for x in installs), '42层安装未闭合')
    cache_root = (Path(env.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))).expanduser() / 'vllm').resolve()
    paths = {Path(p.strip()).resolve() for p in re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)}
    q.require(len(paths) == 1, '服务未声明唯一真实模型图目录')
    directory = paths.pop()
    q.require(directory.is_relative_to(cache_root / 'torch_compile_cache'), '实际图越出默认缓存')
    graph_path = directory / 'computation_graph.py'
    graph_text = graph_path.read_text(encoding='utf-8')
    native = gate.native_graph(graph_text)
    fused = rope_graph.inspect_graph(graph_text)
    entries = ast.literal_eval((directory / 'vllm_compile_cache.py').read_text(encoding='utf-8'))
    q.require(isinstance(entries, dict) and entries, '实际编译entry为空')
    handles = []
    for value in entries.values():
        handle = value['graph_handle']
        q.require(isinstance(handle, (tuple, list)) and len(handle) == 2, '实际编译handle格式不符')
        artifact = Path(handle[1]).resolve(strict=True)
        q.require(artifact.is_file() and artifact.is_relative_to(directory), '实际artifact不在本图目录')
        handles.append({'cache_key': value['cache_key'], 'graph_handle': list(handle)})
    loaded = re.findall(r'Directly load AOT compilation from path (\S+)', text)
    saved = re.findall(r'saved AOT compiled function to (\S+)', text)
    aot = []
    for name in sorted(set(loaded + saved)):
        path = Path(name).resolve(strict=True)
        q.require(path.is_file() and path.is_relative_to(cache_root / 'torch_compile_cache/torch_aot_compile'),
                  '实际AOT不属于默认缓存')
        aot.append({'path': str(path), 'sha256': q.sha(path)})
    q.require(len(aot) == 1, '缺少唯一实际保存或加载AOT证据')
    evidence = dict(valid=True, source_count=manifest['source_count'], tree=manifest['tree'],
        graph_sha256=q.sha(graph_path), graph=native, rope_graph=fused, fingerprint=expected,
        directory=str(directory), graph_path=str(graph_path), compiled_handles=handles,
        aot_files=aot, aot_loaded_paths=loaded, aot_saved_paths=saved,
        native_library_sha256=q.SO, model_config_sha256=q.sha(MODEL), receipt_sha256=q.sha(receipt_path),
        installed=installs, warmed_before_install=True,
        bound_lines=[line for line in text.splitlines() if 'BIV150_ROPE_KV_BOUND ' in line],
        limitation='真实FX证明路径接线；四语义不替代完整105准确率或性能测量')
    if prior_control is not None:
        prior_control = Path(prior_control).resolve(strict=True)
        state = q.read(prior_control / 'state.json')
        q.require(state.get('completed') is True and state.get('database_restored') is True
                  and state.get('source_unchanged') is True and state.get('native_unchanged') is True
                  and state.get('tree') == manifest['tree'] and state.get('source_count') == 528,
                  '重用前置不是成功的相同528来源')
        prior = q.read(Path(state['run']) / 'model-path/evidence.json')
        q.require(state['model_path'] == prior and prior['valid'] is True
                  and prior['fingerprint'] == expected and prior['graph_sha256'] == evidence['graph_sha256']
                  and prior['aot_files'] == aot and bool(loaded)
                  and gate.relative_handles(prior['compiled_handles'], prior['directory'])
                  == gate.relative_handles(handles, directory), '重用未加载已验相同图/FP/AOT/handles')
        evidence['prior_control'] = str(prior_control)
    output = run / 'model-path'
    output.mkdir()
    for name in ('computation_graph.py', 'vllm_compile_cache.py', 'cache_key_factors.json'):
        shutil.copyfile(directory / name, output / name)
    evidence['cache_metadata_sha256'] = {name: q.sha(output / name)
        for name in ('computation_graph.py', 'vllm_compile_cache.py', 'cache_key_factors.json')}
    gate.save(output / 'evidence.json', evidence)
    return evidence
