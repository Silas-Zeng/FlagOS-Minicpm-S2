"""后继只复用成功的同源528服务资格；不重新发送语义或组件请求。"""
from pathlib import Path
import cache_gate as gate
import qualification as q
import rope_graph

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
TREE = '4e2f52ce47382fe4d1ef13317c3e171ab922cd27'


def qualify(control, life):
    control = Path(control)
    q.require(not control.is_symlink(), 'RoPE验证control不能为symlink')
    control = control.resolve(strict=True)
    q.require(control.is_relative_to(ROOT / 'framework') and control.name.endswith('-control'),
              '只接受本实例framework RoPE验证control')
    state = q.read(control / 'state.json')
    q.require(all(state.get(k) is True for k in ('completed', 'validation_completed', 'database_restored',
                                               'source_unchanged', 'native_unchanged'))
              and not state.get('cleanup_errors') and not state.get('cleanup_error')
              and (control / 'exit-code').read_text().strip() == '0'
              and state.get('source_count') == 528 and state.get('tree') == TREE
              and state.get('base_commit') == q.COMMIT and Path(state['control']) == control,
              '同源528服务验证尚未成功收尾')
    run = Path(state['run'])
    q.require(run == control.with_name(control.name[:-8]) and not run.is_symlink()
              and q.read(run / 'result.json') == state and (run / 'exit-code').read_text().strip() == '0',
              '验证run/control/result未闭合')
    for name, pin in q.read(HERE / 'verification-asset-pins.json').items():
        q.require(q.sha(control / name) == pin, '验证入口来源变化: ' + name)
    requests = q.read(run / 'requests.json')
    expected = [('add', 85), ('multiply', 323), ('divide', 12), ('long-prefill', 95)]
    q.require(state.get('semantic_requests') == requests and len(requests) == 4
              and [(r.get('name'), r.get('expected')) for r in requests] == expected
              and all(r.get('correct') is True for r in requests)
              and requests[-1].get('usage', {}).get('prompt_tokens', 0) >= 4096,
              '四语义/长prefill原件不完整')
    for row in requests:
        response = q.read(run / (row['name'] + '-response.json'))
        q.require(gate.final_answer(response['choices'][0]['message']['content'], row['expected']) == row['visible']
                  and response.get('usage', {}) == row['usage'], '语义记录与原响应不一致')
    manifest = q.read(HERE / 'source-manifest.json')
    q.require(manifest['source_count'] == 528 and manifest['tree'] == TREE
              and manifest['base_commit'] == q.COMMIT and manifest['base_tree'] == q.TREE,
              '冻结528来源不符')
    blobs = {p: dict(mode=x['mode'], sha=x['git_sha']) for p, x in manifest['files'].items()}
    hashes = {p: x['sha256'] for p, x in manifest['files'].items()}
    q.require(len(blobs) == 528 and q.read(control / 'source-git-blobs.json') == blobs
              and q.read(control / 'source-sha256.json') == hashes, '528源码登记变化')
    origin = Path(state['source'])
    q.require(not origin.is_symlink() and origin.resolve(strict=True).is_relative_to(ROOT / 'code'), '528源码根错误')
    origin = origin.resolve(strict=True)
    q.require(all(life.source_maps(p) == (blobs, hashes) for p in (origin, control / 'plugin-source')),
              '验证后528源码发生变化')
    graph = q.read(run / 'model-path/evidence.json')
    fx = run / 'model-path/computation_graph.py'
    text = fx.read_text(encoding='utf-8')
    q.require(state.get('model_path') == graph and graph.get('valid') is True
              and graph.get('tree') == TREE and graph.get('source_count') == 528
              and graph['graph_sha256'] == q.sha(fx) and graph['graph'] == gate.native_graph(text)
              and graph['rope_graph'] == rope_graph.inspect_graph(text)
              and graph['fingerprint']['native_enabled'] is True and graph['native_library_sha256'] == q.SO,
              '528真实34native/42fusion/0旧KV/dep图资格不符')
    for name, digest in graph['cache_metadata_sha256'].items():
        q.require(Path(name).name == name and q.sha(run / 'model-path' / name) == digest, '验证缓存元数据变化')
    q.require(len(graph['aot_files']) == 1, '验证AOT非唯一')
    for item in graph['aot_files']:
        path = Path(item['path']).resolve(strict=True)
        q.require(path.is_relative_to(q.CACHE_ROOT / 'torch_compile_cache/torch_aot_compile')
                  and q.sha(path) == item['sha256'], '验证实际AOT发生变化')
    build = q.read(control / 'native/build-manifest.original.json')
    receipt = q.read(control / 'native/runtime-receipt.json')
    library, log = control / 'native/biv150_native_w8a8.so', control / 'native/build.log'
    q.require(build.get('exit_code') == 0 and build['library_sha256'] == q.SO
              and q.sha(library) == q.SO and q.sha(log) == build['build_log_sha256']
              and receipt == dict(build, runtime_library=str(library))
              and graph['receipt_sha256'] == q.sha(control / 'native/runtime-receipt.json')
              and all(hashes[p] == digest for p, digest in build['source_sha256'].items()),
              '已验native来源或实际SO变化')
    return origin, blobs, hashes, manifest, graph, build, library, log
