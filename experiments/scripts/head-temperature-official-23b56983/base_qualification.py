"""只接受已成功161030 main526；不读取或继承KV候选的VERIFY资格。"""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMIT = '0bf9d2efeaa10144dd7f0ff4597298df029f9328'
TREE = '8671e2ec040601981d1533d6a09beb20b9e507db'
RUN = '20261024T161030Z-main0bf9-main-official-four-rounds'
SO = '14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
SEMANTICS = 'bca233bbfdfd3477d12e0a47216e5dfb504af5d43ab78f3dd79fe503e3ff729a'
MODEL = Path('/workspace/MiniCPM5-2B/config.json')
CACHE_ROOT = Path('/root/.cache/vllm')
read = lambda p: json.loads(Path(p).read_bytes())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def assets():
    for name, digest in read(HERE / 'asset-pins.json').items():
        require(sha(HERE / name) == digest, '入口资产变化: ' + name)


def qualify(control, lifecycle):
    control = Path(control)
    require(not control.is_symlink(), 'performance control不可为symlink')
    control = control.resolve(strict=True)
    require(control == ROOT / 'official' / (RUN + '-control'), '只接受161030 main526正式四轮')
    state = read(control / 'state.json')
    require(all(state.get(k) is True for k in ('completed', 'database_restored', 'source_unchanged', 'native_unchanged'))
            and state.get('driver_exit_code') == 0 and not state.get('cleanup_error')
            and (control / 'exit-code').read_text().strip() == '0'
            and state.get('role') == 'main' and state.get('source_count') == 526
            and state.get('base_commit') == COMMIT and state.get('tree') == TREE
            and Path(state['control']) == control, 'main526性能来源未成功闭合')
    run = Path(state['run'])
    require(run == control.with_name(RUN) and not run.is_symlink(), 'run/control不对应')
    result = read(run / 'result.json')
    require(state['result'] == result and result.get('benchmark_completed') is True
            and result.get('exit_code') == 0 and not result.get('cleanup_errors')
            and (run / 'exit-code').read_text().strip() == '0', '原四轮driver未成功收尾')
    validation = result['validation']
    require(validation.get('complete') is True and validation.get('raw_rows') == 8
            and validation.get('summary_rows') == 2 and validation.get('runs_per_case') == 4
            and validation.get('skip_first') == 1 and validation.get('summary_means_verified') is True,
            '来源不是完整原官方四轮')
    files = [control / 'state.json', control / 'source-sha256.json', control / 'source-git-blobs.json',
             run / 'result.json', run / 'model-path/evidence.json', run / 'model-path/computation_graph.py']
    for relative, digest in validation['sha256'].items():
        path = (run / relative).resolve(strict=True)
        require(path.is_relative_to(run) and sha(path) == digest, '原四轮CSV身份变化')
        files.append(path)
    manifest = read(HERE / 'base-source-manifest.json')
    require(manifest['commit'] == COMMIT and manifest['tree'] == TREE and manifest['source_count'] == 526,
            '冻结main manifest不符')
    blobs = {p: dict(mode=v['mode'], sha=v['git_sha']) for p, v in manifest['files'].items()}
    hashes = {p: v['sha256'] for p, v in manifest['files'].items()}
    origin = Path(state['source'])
    require(len(blobs) == 526 and origin.is_absolute() and not origin.is_symlink()
            and origin.resolve(strict=True).is_relative_to(ROOT / 'code'), 'main源路径不符')
    origin = origin.resolve(strict=True)
    require(read(control / 'source-git-blobs.json') == blobs and read(control / 'source-sha256.json') == hashes,
            '来源登记并非完整526')
    for path in (origin, control / 'plugin-source'):
        require(lifecycle.source_maps(path) == (blobs, hashes), '已测526源码变化: ' + str(path))
    graph = read(run / 'model-path/evidence.json')
    gate = load(HERE / 'cache_gate.py', 'baseline_native_graph')
    actual = gate.native_graph((run / 'model-path/computation_graph.py').read_text(encoding='utf-8'))
    require(state['model_path'] == graph and graph.get('valid') is True and graph.get('role') == 'main'
            and graph['graph'] == actual and actual['layers'] == list(range(4, 38))
            and graph['graph_sha256'] == sha(run / 'model-path/computation_graph.py')
            and graph['fingerprint']['native_enabled'] is True and graph['native_library_sha256'] == SO
            and len(graph['aot_files']) == 1, 'main526实际34层FX/AOT资格缺失')
    for item in graph['aot_files']:
        path = Path(item['path']).resolve(strict=True)
        require(path.is_relative_to(CACHE_ROOT / 'torch_compile_cache/torch_aot_compile')
                and sha(path) == item['sha256'], 'main526实际AOT变化')
    build = read(control / 'native/build-manifest.original.json')
    receipt = read(control / 'native/runtime-receipt.json')
    library = control / 'native/biv150_native_w8a8.so'
    log = control / 'native/build.log'
    require(build.get('exit_code') == 0 and build['source_commit'] == '7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93'
            and build['source_tree'] == 'b37543afc3250b4bd9361a505eb9f932286667e6'
            and build['library_sha256'] == SO and not library.is_symlink()
            and sha(library) == SO and library.read_bytes()[:4] == b'\x7fELF'
            and sha(log) == build['build_log_sha256']
            and build['abi'] == {'torch_version': '2.10.0', 'cxx11_abi': False}, '原native构建/库/ABI不符')
    require(receipt == dict(build, runtime_library=str(library)), '已测native runtime receipt不符')
    require(all(hashes[p] == digest for p, digest in build['source_sha256'].items()), 'native构建源码与526不同')
    files += [control / 'native/build-manifest.original.json', control / 'native/runtime-receipt.json', log]
    reference = dict(control=str(control), run=str(run), files={str(p): sha(p) for p in files},
                     graph=graph, source_count=526, tree=TREE, commit=COMMIT)
    return (origin, blobs, hashes, TREE), (build, library, log), reference


def check_environment(source, env, build, graph):
    require(sha(MODEL) == graph['model_config_sha256'], '模型config变化')
    path = source / 'vllm_fl/compile_semantics.py'
    require(sha(path) == SEMANTICS, '缓存语义helper变化')
    semantics = load(path, 'accuracy_semantics')
    config = SimpleNamespace(model_config=SimpleNamespace(hf_config=SimpleNamespace(**read(MODEL))))
    expected = semantics.build_fingerprint(config, 'iluvatar', package_root=source / 'vllm_fl', environ=env,
        abi={'torch': build['abi']['torch_version'], 'cxx11_abi': build['abi']['cxx11_abi']})
    require(expected == graph['fingerprint'], '本次环境/源码/SO指纹与已测main526不符')


def check_reference(reference):
    require(all(sha(Path(p)) == digest for p, digest in reference['files'].items()), '性能资格原件在运行期间变化')
