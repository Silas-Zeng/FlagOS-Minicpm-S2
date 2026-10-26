"""标准库准备独立组件；不导入Torch/Triton，不连接远端或运行GPU。"""
from __future__ import annotations
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import tarfile
import prototype

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = ROOT / 'tmp/prefill-lpt-component-20261026'
sha = lambda data: hashlib.sha256(data).hexdigest()


def put(name, source):
    (HERE / name).write_bytes(source.encode('utf-8'))


def once(source, old, new):
    assert source.count(old) == 1, old[:120]
    return source.replace(old, new, 1)


# 直接从main6971源包生成stride baseline；不读取LPT候选内核或叠加调序。
archive = ROOT / 'tmp/prefill-stride-main34942-model-20261026/source.tar'
identity = json.loads(archive.with_name('source-manifest.json').read_bytes())
assert identity['tree'] == 'aa43ea2c30b76915d4f83fc383c7102946e0c10b'
with tarfile.open(archive) as tf:
    name = 'vllm_fl/patches/biv150_prefill_normalized.py'
    member = next(m for m in tf if m.name.removeprefix('./') == name)
    data = tf.extractfile(member).read()
    assert sha(data) == identity['files'][name]['sha256']
    normalized = data.decode('utf-8')
attention_path = ROOT / ('tmp/experiment-pr24-phase-20261024/experiments/framework/'
    '20261026T044032Z-main6971-qkv-wide-four-rounds/source/installed/'
    'vllm/v1/attention/ops/triton_unified_attention.py')
attention = attention_path.read_bytes()
assert sha(attention) == '54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f'
fn = next(n for n in ast.parse(attention).body if isinstance(n, ast.FunctionDef)
          and n.name == 'kernel_unified_attention')
kernel = ast.get_source_segment(attention.decode('utf-8'), fn)
kernel = once(kernel, 'L = tl.full([BLOCK_M], 1.0, dtype=tl.float32)',
              'L = tl.zeros([BLOCK_M], dtype=tl.float32)')
kernel = once(kernel, 'def kernel_unified_attention(', 'def kernel_biv150_prefill_normalized(')
nodes = [n for n in ast.parse(normalized).body if (isinstance(n, ast.FunctionDef)
         and n.name == '_specialize_strides') or (isinstance(n, ast.Assign)
         and any(isinstance(t, ast.Name) and t.id == '_STRIDES' for t in n.targets))]
ns = {'ast': ast, 're': re}
exec(compile(ast.Module(body=nodes, type_ignores=[]), '<stdlib-stride-transform>', 'exec'), ns)
current = prototype.canonical(ns['_specialize_strides'](kernel))
assert sha(current.encode()) == prototype.BASELINE_KERNEL_SHA
candidate = prototype.transform(current)
assert 'q_block_local_idx = tl.cdiv' not in candidate
put('current.kernel.py', current)
put('candidate.kernel.py', candidate)
put('kernel.diff', ''.join(difflib.unified_diff(current.splitlines(True), candidate.splitlines(True),
    fromfile='main6971-stride/current.kernel.py', tofile='fresh-kv/candidate.kernel.py')))

# 所有者/身份/真实Builder/FP64等原件复用；只在新目录生成自己的worker和run名。
assets = ('base-source-manifest.json', 'base-source-sha256.json', 'source_identity.py',
    'dispatch_bootstrap.py', 'distributed_bootstrap.py', 'legacy_gate.py', 'monitor_gpu.sh',
    'validate_block_table_candidate.py', 'validate_hidden_row_gather.py', 'validate_mixed_decode.py', 'seal.py')
for name in assets:
    (HERE / name).write_bytes((OLD / name).read_bytes())
entry = (OLD / 'entry.py').read_text(encoding='utf-8')
owner = once(entry, '"-prefill-lpt-"', '"-prefill-fresh-kv-"')
put('entry.py', owner)
put('owner.diff', ''.join(difflib.unified_diff(entry.splitlines(True), owner.splitlines(True),
    fromfile='受测main618组件/entry.py', tofile='fresh-kv/entry.py')))
old = (OLD / 'worker.py').read_text(encoding='utf-8')
w = once(old, 'import alternate_stride\n', '')
w = w.replace('"stride"', '"fresh_kv"').replace('raw_stride', 'raw_fresh').replace('source_stride', 'source_fresh')
w = once(w, 'stride=lambda:', 'fresh_kv=lambda:')
w = w.replace('ir-stride', 'ir-fresh-kv').replace('实际候选不是固定CTA变换', '实际候选不是固定fresh-KV loader变换')
w = w.replace('换值后CTA调序出现数值差异', '换值后fresh/cache同值却出现跨臂差异')
w = w.replace('真实 M2047/KV16K normalized+Q-hoist 对 stride 同形状组件。',
              '真实main6971 stride+Q-hoist对fresh-KV两场景组件，未注册生产。')
w = once(w, 'candidate="当前stride+Q-hoist仅反转序列内query block的CTA枚举；每个query的K顺序不变",',
    'candidate="当前stride+Q-hoist保持绝对T64顺序；本轮新KV直读post-RoPE张量，历史仍paged",')
w = w.replace('CTA调序不应改变每个query的数值', '两来源同BF16值且原分组不变，必须跨臂逐位')
w = once(w, '            "仅stride特化；原浮点表达式不变，独立FP64及每臂Graph门复用。",',
    '            "只改变KV地址来源；原FP64阈值及跨臂逐位不放宽。",')
w = once(w, '        common, query, key, value, cache = make_data(torch, [M], KV)\n',
    '''        common, query, key, value, cache = make_data(torch, [M], KV)
        # 共同模拟QKV投影后K/V视图的非连续token stride，不是候选独有副本。
        raw_backing = torch.full((M + 3, 2560), -19, dtype=torch.bfloat16, device="cuda")
        raw_k = raw_backing[:, 2048:2304].view(M + 3, 2, 128)
        raw_v = raw_backing[:, 2304:2560].view(M + 3, 2, 128)
        raw_k.copy_(key); raw_v.copy_(value)
        key, value = raw_k, raw_v
        raw_backing_before = raw_backing.clone()
''')
w = once(w, '        kw_b = dict(current_kwargs, output_ptr=outputs["fresh_kv"][:M])\n',
    '        kw_b = prototype.add_fresh_kwargs(dict(current_kwargs, output_ptr=outputs["fresh_kv"][:M]), key[:M], value[:M])\n')
w = once(w, '        result["specialized_stride_values"] = {name: current_kwargs[name] for name in prototype.STRIDES}\n',
    '        result["fresh_stride_values"] = {name: kw_b[name] for name in prototype.FRESH_STRIDES}\n')
w = once(w, '        initial = {name: out.clone() for name, out in outputs.items()}\n',
    '''        initial = {name: out.clone() for name, out in outputs.items()}
        # 路由反事实只作机制门：raw与cache暂时不等，不计性能/正确性分数。
        value[:M].mul_(-1)
        calls["current"](); calls["fresh_kv"]()
        torch.cuda.synchronize()
        result["fresh_source_read_proof"] = dict(
            cache_only_unchanged=torch.equal(initial["current"][:M].view(torch.int16),
                                            outputs["current"][:M].view(torch.int16)),
            fresh_arm_changed=not torch.equal(initial["fresh_kv"][:M].view(torch.int16),
                                              outputs["fresh_kv"][:M].view(torch.int16)))
        value.copy_(value_before)
        calls["current"](); calls["fresh_kv"]()
        torch.cuda.synchronize()
        require(all(result["fresh_source_read_proof"].values()), "未证明候选实际读取新KV")
        require(all(torch.equal(initial[name].view(torch.int16), outputs[name].view(torch.int16))
                    for name in ARMS), "raw恢复后没有逐位恢复原输出")
''')
w = once(w, '        page_ids[0], page_ids[2] = page_ids[2], page_ids[0]\n',
    '''        page_ids[0], page_ids[2] = page_ids[2], page_ids[0]
        # 零prefix场景的新KV也覆盖这些页：slot与新页表必须同步重建。
        common.slot_mapping.copy_(torch.tensor([page_ids[pos // 16] * 16 + pos % 16
            for pos in range(KV - M, KV)], dtype=torch.int64, device="cuda"))
''')
assert 'alternate_stride.' not in w
w = once(w, '        require(all(result["read_only_checks"].values()), "读取改变输入/RNG或越过输出guard")\n',
    '''        require(all(result["read_only_checks"].values()), "读取改变输入/RNG或越过输出guard")
        require(torch.equal(raw_backing[:, :2048].view(torch.int16),
                            raw_backing_before[:, :2048].view(torch.int16)), "raw KV相邻QKV区域被修改")
''')
put('worker.py', w)
put('worker.diff', ''.join(difflib.unified_diff(old.splitlines(True), w.splitlines(True),
    fromfile='受测prefill组件/worker.py', tofile='fresh-kv/worker.py')))
for name in ('entry.py', 'worker.py', 'prototype.py'):
    ast.parse((HERE / name).read_text(encoding='utf-8'), filename=name)
worker_tree = ast.parse(w)
calls = next(n for n in ast.walk(worker_tree) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'calls' for t in n.targets))
assert {k.arg for k in calls.value.keywords} == {'current', 'fresh_kv'}
receipt = {'status': 'CPU准备，未GPU编译/数值/性能', 'base_tree': identity['tree'],
    'baseline_kernel_sha256': sha(current.encode()), 'candidate_kernel_sha256': sha(candidate.encode()),
    'normalized_module_sha256': sha(data), 'attention_sha256': sha(attention),
    'source': '直接从main6971源包及原installed54c生成，无LPT段',
    'owner': '原所有者仅run名变化，原锁/预检/DB恢复/进程组清理不变',
    'scenarios': [[2048, 2048], [2047, 16384]],
    'checks': ['syntax', 'loader准确逆变换', 'no_LPT', 'main618身份及owner复用']}
(HERE / 'preparation.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(receipt, ensure_ascii=False))
