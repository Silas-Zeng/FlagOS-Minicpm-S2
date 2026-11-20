"""官方测量前只读模型路径门；不请求模型、不导入Torch、不改变运行配置。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

HELPER_SHA = '84a67eed8c9db23d9f9085974dd9d2ffe4ebcc66e8a536091659ed363d355bd0'
SEMANTICS_SHA = 'bca233bbfdfd3477d12e0a47216e5dfb504af5d43ab78f3dd79fe503e3ff729a'
BASE_COMMIT = '0bf9d2efeaa10144dd7f0ff4597298df029f9328'
KV_TREE = '98f4688ae0a0edb325e5aac39647486e323b86f7'
MODEL_CONFIG = Path('/workspace/MiniCPM5-2B/config.json')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def module(path, expected, name):
    require(sha(path) == expected, '图门依赖来源变化: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def relative_handles(handles, directory):
    """保留编译key/符号/相对产物身份，只去各自backbone目录前缀。"""
    root = Path(directory).resolve()
    normalized = []
    for value in handles:
        require(isinstance(value, dict), '编译handle记录非dict')
        handle = value.get('graph_handle')
        require(isinstance(handle, (tuple, list)) and len(handle) == 2,
                '编译handle格式不符')
        artifact = Path(handle[1]).resolve()
        require(artifact.is_relative_to(root) and artifact != root,
                '编译artifact不在各自实际图目录内')
        normalized.append({'cache_key': value['cache_key'],
                           'graph_handle': [handle[0], artifact.relative_to(root).as_posix()]})
    return normalized


def capture(run, source, role, verification_control, env):
    """调用方已校验535完整来源；这里绑定本服务日志、实际图及SO内容指纹。"""
    require(role == 'kv', '本入口仅运行535候选')
    run, source = Path(run), Path(source)
    require(env.get('VLLM_DISABLE_COMPILE_CACHE', '0') == '0'
            and not any(k in env for k in ('VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR')),
            '官方队列要求默认共享编译缓存')
    receipt_path = Path(env['BIV150_RESUME_NATIVE_RECEIPT'])
    require(sha(receipt_path) == env['BIV150_RESUME_NATIVE_RECEIPT_SHA256'], 'native凭据变化')
    receipt = read(receipt_path)
    library = Path(env['BIV150_NATIVE_W8A8_LIBRARY']).resolve(strict=True)
    require(library == Path(receipt['runtime_library']).resolve(strict=True)
            and sha(library) == receipt['library_sha256'], '实际native SO与凭据不符')
    abi = receipt['abi']
    require(isinstance(abi['torch_version'], str) and type(abi['cxx11_abi']) is bool, 'native ABI凭据不符')
    semantics = module(source / 'vllm_fl/compile_semantics.py', SEMANTICS_SHA, 'official_semantics_gate')
    model = SimpleNamespace(**read(MODEL_CONFIG))
    config = SimpleNamespace(model_config=SimpleNamespace(hf_config=model))
    expected = semantics.build_fingerprint(config, 'iluvatar', package_root=source / 'vllm_fl',
        environ=env, abi={'torch': abi['torch_version'], 'cxx11_abi': abi['cxx11_abi']})
    require(expected is not None and expected['native_enabled'] is True, '预测当前native指纹失败')
    helper = module(Path(__file__).with_name('cache_gate.py'), HELPER_SHA, 'official_native_graph_gate')
    text = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'server.log').read_text(encoding='utf-8', errors='replace'))
    fingerprints = [json.loads(line.split('BIV150_COMPILE_SEMANTICS ', 1)[1])
                    for line in text.splitlines() if 'BIV150_COMPILE_SEMANTICS ' in line]
    require(fingerprints and all(value == expected for value in fingerprints), '本服务指纹不符当前源码/SO/ABI')
    cache_root = (Path(env.get('XDG_CACHE_HOME', str(Path.home() / '.cache'))).expanduser() / 'vllm').resolve()
    paths = {Path(p.strip()).resolve() for p in re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)}
    require(len(paths) == 1, '本服务未声明唯一模型图目录')
    directory = paths.pop()
    require(directory.is_relative_to(cache_root / 'torch_compile_cache'), '实际模型图越出默认缓存')
    graph_path = directory / 'computation_graph.py'
    graph = helper.native_graph(graph_path.read_text(encoding='utf-8'))
    graph_sha = sha(graph_path)
    entries = ast.literal_eval((directory / 'vllm_compile_cache.py').read_text(encoding='utf-8'))
    require(isinstance(entries, dict) and entries, '模型编译entry为空')
    handles = []
    for value in entries.values():
        handle = value['graph_handle']
        require(isinstance(handle, (tuple, list)) and len(handle) == 2
                and Path(handle[1]).resolve(strict=True).is_relative_to(directory), '编译artifact不属于真实图目录')
        handles.append({'cache_key': value['cache_key'], 'graph_handle': list(handle)})
    loaded = re.findall(r'Directly load AOT compilation from path (\S+)', text)
    saved = re.findall(r'saved AOT compiled function to (\S+)', text)
    aot = []
    for name in sorted(set(loaded + saved)):
        path = Path(name).resolve(strict=True)
        require(path.is_file() and path.is_relative_to(cache_root / 'torch_compile_cache/torch_aot_compile'),
                '实际AOT文件不属于默认缓存')
        aot.append({'path': str(path), 'sha256': sha(path)})
    require(len(aot) == 1, '本服务缺少唯一保存/加载AOT证据')
    evidence = dict(valid=True, role=role, directory=str(directory), graph_path=str(graph_path),
        graph_sha256=graph_sha, graph=graph, fingerprint=expected, aot_files=aot,
        aot_loaded_paths=loaded, aot_saved_paths=saved, compiled_handles=handles,
        native_library_sha256=receipt['library_sha256'], model_config_sha256=sha(MODEL_CONFIG),
        receipt_sha256=sha(receipt_path), provenance='当前源码预测指纹与本服务真实图/AOT，非安装marker推断',
        native_execution_per_request_asserted=False)
    if role == 'kv':
        control = Path(verification_control)
        state = read(control / 'state.json')
        require(state.get('completed') is True and state.get('database_restored') is True
                and state.get('base_commit') == BASE_COMMIT and state.get('tree') == KV_TREE
                and state.get('source_count') == 535, '候选须引用已成功的新535 VERIFY1')
        prior = read(Path(state['run']) / 'model-path/graph-evidence.json')
        require(prior['fingerprint'] == expected
                and prior['graph_sha256'] == graph_sha and prior['graph']['layers'] == list(range(4, 38))
                and relative_handles(prior['compiled_handles'], prior['directory']) == relative_handles(handles, directory)
                and prior['aot_files'] == aot,
                '候选实际模型图/AOT不符新535 VERIFY1')
        require(bool(loaded),
                '候选未实际加载已验535 AOT/编译图')
        evidence['verification_control'] = str(control)
        evidence['verification_directory'] = prior['directory']
        evidence['verification_cache_relocated'] = prior['directory'] != str(directory)
        evidence['verification_graph_sha256'] = sha(Path(state['run']) / 'model-path/graph-evidence.json')
    output = run / 'model-path'
    output.mkdir(exist_ok=False)
    shutil.copyfile(graph_path, output / 'computation_graph.py')
    evidence['cache_metadata_sha256'] = {name: sha(directory / name)
        for name in ('vllm_compile_cache.py', 'cache_key_factors.json')}
    for name in evidence['cache_metadata_sha256']:
        shutil.copyfile(directory / name, output / name)
    (output / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return evidence
