"""只绑定131603整套467/a42原件；不复用526缓存资格。"""
import ast
import importlib.util
from pathlib import Path
import shutil

import cache_gate as gate
import lifecycle as life

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
SOURCE = ROOT/'code/20261024T131603Z-pr24-isolated-cache'
REFERENCE = ROOT/'accuracy/20261024T131603Z-pr24-isolated-cache-math500-control'
COMMIT = '1ad9a708ee77323372f0fa5975a04a52d294852c'
TREE = 'd1a96e3f56723956a7902cba7e676fd285c83d0c'
SO = 'a42f71e27197c9d6efc0ad72ef1656b0c71abbd5f5d8530cdbdd390eb2470203'
sha = gate.sha
require = gate.require


def read(path):
    import json
    return json.loads(Path(path).read_bytes())


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assets():
    for name, expected in read(HERE/'asset-pins.json').items():
        require(sha(HERE/name) == expected, '入口资产变化: '+name)


def identity(source, blobs, hashes, library):
    # 131603旧清单的SHA跟随链接，Git blob仍核链接文本；不可套526的SHA口径。
    source = Path(source).resolve(strict=True)
    actual_blobs, _ = life.source_maps(source)
    require(actual_blobs == blobs and len(blobs) == 467, '旧467源码Git身份变化')
    require(set(blobs) == set(hashes), '旧源码两份清单不一致')
    for relative, expected in hashes.items():
        path = (source/relative).resolve(strict=True)
        require(path.is_relative_to(source) and sha(path) == expected, '旧源码SHA变化: '+relative)
    require(sha(library) == SO, '旧a42 native身份变化')
    return True


def check_reference(reference):
    root = Path(reference['control'])
    require(root == REFERENCE, '旧准确率来源路径不符')
    for name, expected in reference['files'].items():
        require(sha(root/name) == expected, '131603原件变化: '+name)


def qualify(control, unused_life):
    control = Path(control).resolve(strict=True)
    names = ('source-git-blobs.json', 'source-sha256.json', 'state.json',
             'accuracy-review.json', 'native/build-manifest.json')
    reference = dict(control=str(control), files={name: sha(HERE/'reference'/name) for name in names})
    check_reference(reference)
    state, review = read(control/'state.json'), read(control/'accuracy-review.json')
    require(state['commit'] == COMMIT and state['tree'] == TREE and state['source_count'] == 467
            and Path(state['source']) == SOURCE, '131603源码身份不符')
    require(all(state.get(k) is True for k in ('completed', 'source_unchanged', 'native_unchanged', 'database_restored'))
            and review['validity'] == 'valid' and review['accuracy_gate'] == 'pass'
            and review['correct'] == 100 and review['samples'] == 105, '131603原准确率未达标')
    blobs, hashes = read(control/'source-git-blobs.json'), read(control/'source-sha256.json')
    build = read(control/'native/build-manifest.json')
    library, log = control/'native/biv150_native_w8a8.so', control/'native/build.log'
    require(build['source_commit'] == COMMIT and build['source_tree'] == TREE
            and build['library_sha256'] == SO, '131603构建身份不符')
    require(sha(log) == build['build_log_sha256'], '旧native构建日志变化')
    identity(SOURCE, blobs, hashes, library)
    return (SOURCE, blobs, hashes, TREE), (build, library, log), reference


def capture(run, source, env):
    # disable_compile_cache=1不会打印默认缓存目录/AOT；只读取本run全新私有根。
    require(env['VLLM_DISABLE_COMPILE_CACHE'] == '1', '必须保留旧隔离编译策略')
    root = Path(env['VLLM_CACHE_ROOT']).resolve(strict=True)
    require(root == run.with_name(run.name+'-control')/'vllm-cache', '图必须来自本次私有缓存')
    paths = sorted(root.glob('torch_compile_cache/**/computation_graph.py'))
    output = run/'model-path'
    output.mkdir()
    evidence = dict(source=str(source), source_count=467, commit=COMMIT, tree=TREE,
                    native_library_sha256=SO, cache_root=str(root), graphs=[], valid=False)
    for index, graph in enumerate(paths):
        require(graph.resolve().is_relative_to(root), '图路径越界')
        target = output/str(index)
        target.mkdir()
        for name in ('computation_graph.py', 'cache_key_factors.json', 'vllm_compile_cache.py'):
            path = graph.parent/name
            if path.is_file():
                shutil.copyfile(path, target/name)
        evidence['graphs'].append(dict(path=str(graph), sha256=sha(graph), evidence=str(target)))
    gate.save(output/'evidence.json', evidence)
    require(len(paths) == 1 and paths[0].parent.name == 'backbone', '本次未得到唯一实际backbone图')
    tree = ast.parse(paths[0].read_text(encoding='utf-8'))
    calls = [gate.dotted(node.func) for node in ast.walk(tree) if isinstance(node, ast.Call)
             and gate.dotted(node.func).startswith('torch.ops.biv150_native.')]
    marker = 'BIV150_NATIVE_W8A8_INSTALL '
    installations = [ast.literal_eval(line.split(marker, 1)[1].strip())
        for line in (run/'server.log').read_text(encoding='utf-8', errors='replace').splitlines() if marker in line]
    evidence['graphs'][0]['native'] = dict(native_call_count=len(calls), calls=calls)
    evidence['installations'] = installations
    gate.save(output/'evidence.json', evidence)
    require(env.get('VLLM_FL_BIV150_NATIVE_W8A8') == '0'
            and installations and all(item.get('installed') is False for item in installations)
            and not calls, 'native关闭未生效：要求installed=False且实际图0 native调用')
    evidence['valid'] = True
    gate.save(output/'evidence.json', evidence)
    return evidence
