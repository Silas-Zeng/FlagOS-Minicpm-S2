"""只核新源码默认关闭native及本次实际缓存图；不继承旧准确率资格。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
MODEL = Path('/workspace/MiniCPM5-2B/config.json')
CACHE_ROOT = Path('/root/.cache/vllm')
read = lambda p: json.loads(Path(p).read_bytes())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assets():
    for name, digest in read(HERE / 'asset-pins.json').items():
        require(sha(HERE / name) == digest, '入口资产变化: ' + name)


def qualify(origin, lifecycle):
    require(origin.is_absolute() and not origin.is_symlink(), '要求实际绝对源码目录')
    origin = origin.resolve(strict=True)
    require(origin.is_relative_to(ROOT / 'code') and origin != ROOT / 'code', '源码必须在实验code下')
    manifest = read(HERE / 'source-manifest.json')
    require(re.fullmatch('[0-9a-f]{40}', manifest['commit']) and
            re.fullmatch('[0-9a-f]{40}', manifest['tree']), '源码manifest尚未冻结')
    blobs = {p: dict(mode=v['mode'], sha=v['git_sha']) for p, v in manifest['files'].items()}
    hashes = {p: v['sha256'] for p, v in manifest['files'].items()}
    require(len(blobs) == manifest['source_count'] and bool(blobs), '源码数量不符')
    require(lifecycle.source_maps(origin) == (blobs, hashes), '候选完整源码身份不符')
    reference = dict(commit=manifest['commit'], tree=manifest['tree'], source_count=len(blobs),
                     files={str(HERE / 'source-manifest.json'): sha(HERE / 'source-manifest.json'),
                            str(MODEL): sha(MODEL)})
    return (origin, blobs, hashes, manifest['tree']), reference


def check_environment(source, env):
    require(not any(k.startswith(('VLLM_FL_BIV150_NATIVE_', 'BIV150_NATIVE_',
                                  'BIV150_RESUME_NATIVE_', 'MINICPM_NATIVE_')) for k in env),
            '必须测源码默认值，不允许native环境覆盖')
    require(env.get('VLLM_DISABLE_COMPILE_CACHE') == '0' and
            not any(k in env for k in ('VLLM_CACHE_ROOT', 'TORCHINDUCTOR_CACHE_DIR')),
            '必须保留默认共享cache策略0')
    semantics = load(source / 'vllm_fl/compile_semantics.py', 'safe_default_semantics')
    config = SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected = semantics.build_fingerprint(config, 'iluvatar', package_root=source / 'vllm_fl',
        environ=env, abi={'torch': '2.10.0', 'cxx11_abi': False})
    require(expected is not None and expected.get('native_enabled') is False,
            '源码默认fingerprint未关闭native')
    return expected


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return dotted(node.value) + '.' + node.attr
    return ''


def marker_evidence(text, expected):
    fingerprints = [json.loads(line.split('BIV150_COMPILE_SEMANTICS ', 1)[1])
                    for line in text.splitlines() if 'BIV150_COMPILE_SEMANTICS ' in line]
    installations = [ast.literal_eval(line.split('BIV150_NATIVE_W8A8_INSTALL ', 1)[1].strip())
                     for line in text.splitlines() if 'BIV150_NATIVE_W8A8_INSTALL ' in line]
    require(fingerprints and all(x == expected and x.get('native_enabled') is False for x in fingerprints),
            '实际cache指纹没有闭合为本次源码默认native关闭')
    require(installations and all(x.get('installed') is False for x in installations),
            '本服务安装器未关闭native')
    return dict(fingerprint=fingerprints[0], installations=installations)


def native_calls(text):
    return [dotted(node.func) for node in ast.walk(ast.parse(text)) if isinstance(node, ast.Call)
            and dotted(node.func).startswith('torch.ops.biv150_native.')]


def model_path_evidence(run, control, expected):
    # 沿原cache_gate的日志→唯一实际目录→FX/cache handles/AOT读取链；不运行图。
    text = re.sub(r'\x1b\[[0-9;]*m', '', (run / 'server.log').read_text(errors='replace'))
    evidence = dict(valid=False, **marker_evidence(text, expected))
    declared = re.findall(r"Using cache directory: (.+?) for vLLM's torch\.compile", text)
    paths = {Path(path.strip()).resolve() for path in declared}
    require(len(paths) == 1, '日志未给出唯一实际cache目录')
    directory = paths.pop()
    require(directory.is_relative_to(CACHE_ROOT / 'torch_compile_cache'), '实际图不在默认共享cache')
    graph = directory / 'computation_graph.py'
    output = control / 'model-path'
    output.mkdir()
    files = {}
    for name in ('computation_graph.py', 'vllm_compile_cache.py', 'cache_key_factors.json'):
        file = directory / name
        require(file.is_file(), '实际缓存文件缺失: ' + name)
        shutil.copyfile(file, output / name)
        files[name] = sha(file)
    calls = native_calls(graph.read_text())
    evidence.update(directory=str(directory), graph_path=str(graph), graph_sha256=sha(graph),
                    native_call_count=len(calls), native_calls=calls, files=files)
    # 先保存FX身份；后续失败也不丢已回收实际图。
    (output / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    require(not calls, '实际FX仍含native调用')
    entries = ast.literal_eval((directory / 'vllm_compile_cache.py').read_text())
    require(isinstance(entries, dict) and bool(entries), '实际编译cache entry为空')
    handles = []
    for value in entries.values():
        require(isinstance(value, dict) and 'graph_handle' in value and 'cache_key' in value, '编译cache entry非预期')
        handle = value['graph_handle']
        require(isinstance(handle, (list, tuple)) and len(handle) == 2, '编译handle非预期')
        artifact = Path(handle[1]).resolve(strict=True)
        require(artifact.is_relative_to(directory), '编译artifact不属于本次图目录')
        handles.append(dict(cache_key=value['cache_key'], graph_handle=list(handle), sha256=sha(artifact)))
    aot = re.findall(r'Directly load AOT compilation from path (\S+)', text)
    saved_aot = re.findall(r'saved AOT compiled function to (\S+)', text)
    aot_files = []
    for name in sorted(set(aot + saved_aot)):
        path = Path(name).resolve(strict=True)
        require(path.is_relative_to(CACHE_ROOT / 'torch_compile_cache/torch_aot_compile') and path.is_file(),
                '实际AOT不在默认cache')
        aot_files.append(dict(path=str(path), sha256=sha(path)))
    require(len(aot_files) == 1, '本次未闭合唯一实际保存/加载AOT')
    evidence.update(valid=True, compiled_handles=handles, aot_files=aot_files,
                    accuracy_gate='unassessed_requires_original_105_prediction_and_report_review')
    (output / 'evidence.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    return evidence


def check_reference(reference):
    require(all(sha(Path(path)) == digest for path, digest in reference['files'].items()),
            '源码manifest或模型config运行期间变化')
