"""薄派生已受测log2组件；共同基准不带log2，旧资格/计时不重测。"""
import ast
import difflib
import json
from pathlib import Path
import prototype

HERE=Path(__file__).resolve().parent
OLD=HERE.with_name('prefill-log2-20261025')
def put(name,text): (HERE/name).write_bytes(text.encode())
def once(text,old,new):
    assert text.count(old)==1,old[:100]
    return text.replace(old,new,1)
assets=['base-source-manifest.json','base-source-sha256.json','dispatch_bootstrap.py',
    'distributed_bootstrap.py','legacy_gate.py','monitor_gpu.sh','source_identity.py',
    'validate_block_table_candidate.py','validate_hidden_row_gather.py','validate_mixed_decode.py','seal.py']
for name in assets: (HERE/name).write_bytes((OLD/name).read_bytes())
old=(OLD/'entry.py').read_text(encoding='utf-8')
owner=old.replace('prefill-log2-component','prefill-stride-constexpr-component')
put('entry.py',owner)
put('owner.diff',''.join(difflib.unified_diff(old.splitlines(True),owner.splitlines(True),fromfile='受测log2/entry.py',tofile='prefill-stride/entry.py')))
old=(OLD/'worker.py').read_text(encoding='utf-8')
w=old.replace('log2','stride')
w=once(w,'import prototype\n','import prototype\nimport alternate_stride\n')
w=once(w,'candidate="原 normalized+Q-hoist 的 score/M 改 stride 域并直接 exp2；tile/地址/页序不变",',
    'candidate="原normalized+Q-hoist只将11项runtime stride特化constexpr并保持int64地址；数学不变",')
w=once(w,'"换底改变 FP32 舍入，跨臂不要求逐位；BF16 P转换与原归约拓扑保留。",',
    '"仅stride特化；原浮点表达式不变，独立FP64及每臂Graph门复用。",')
w=once(w,'        result["active_arms"] = active_arms\n',
    '''        result["active_arms"] = active_arms
        result["specialized_stride_values"] = {name: current_kwargs[name] for name in prototype.STRIDES}
''')
for label, anchor in [('initial','        initial = {name: out.clone() for name, out in outputs.items()}'),
                      ('changed','        result["read_only_checks"] = dict(kv=torch.equal(cache_before.view(torch.int16), cache.view(torch.int16)),')]:
    w=once(w,anchor,
        '        result["'+label+'_cross_arm"] = dict(bitwise=torch.equal(outputs["current"][:M].view(torch.int16), outputs["stride"][:M].view(torch.int16)),\n'
        '            max_abs=float((outputs["current"][:M].float()-outputs["stride"][:M].float()).abs().max()), diagnostic_only=True)\n'+anchor)
w=once(w,'        # 原同形状完整producer单ABBA；无独有的输入变换或计时外计算。',
    '''        result["alternate_stride"] = alternate_stride.check(torch, run, query, cache, common,
            {"current": kw_a, "stride": kw_b}, {"current": manager, "stride": candidate_manager},
            outputs, graphs, grid, expected_hashes, qmod, preserve)
        # 原同形状完整producer单ABBA；无独有的输入变换或计时外计算。''')
put('worker.py',w)
put('worker.diff',''.join(difflib.unified_diff(old.splitlines(True),w.splitlines(True),fromfile='受测log2/worker.py',tofile='prefill-stride/worker.py')))
kernel=(OLD/'current.kernel.py').read_text(encoding='utf-8')
candidate=prototype.transform(kernel)
put('current.kernel.py',kernel)
put('candidate.kernel.py',candidate)
put('kernel.diff',''.join(difflib.unified_diff(kernel.splitlines(True),candidate.splitlines(True),fromfile='原normalized/current.kernel.py',tofile='stride-constexpr/candidate.kernel.py')))
for name in ('prototype.py','worker.py','entry.py','alternate_stride.py','prepare.py'):
    ast.parse((HERE/name).read_text(encoding='utf-8'),filename=name)
def fn(text,name):
    return next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef) and n.name==name)
for name in ('sampled_oracle','writer_exact','preserve'):
    assert ast.dump(fn(old,name),include_attributes=False)==ast.dump(fn(w,name),include_attributes=False)
assert ast.dump(fn((OLD/'prototype.py').read_text(encoding='utf-8'),'private_manager'),include_attributes=False)==ast.dump(fn((HERE/'prototype.py').read_text(encoding='utf-8'),'private_manager'),include_attributes=False)
ka,ca=fn(kernel,'kernel_biv150_prefill_normalized'),fn(candidate,'kernel_biv150_prefill_stride')
assert len(ca.body)==len(ka.body)+11
assert candidate.count('tl.full((),')==11
assert 'softmax_step(S, M, L)' in candidate and 'tl.exp2(' not in candidate
assert owner.replace('prefill-stride-constexpr-component','prefill-log2-component')==(OLD/'entry.py').read_text(encoding='utf-8')
put('cpu-results.json',json.dumps(dict(status='仅新增CPU通过，未GPU',checks=['11签名/11int64别名及逐字逆回','5模块AST','原FP64/writer/preserve与私有Manager AST复用','原owner仅run名','原数学无log2/新tile','alternate只变eligible允许5项并finally恢复'],
    scope='BM128/T64/w8s1/Q-hoist保持；不重旧资格或GPU门'),ensure_ascii=False,indent=2)+'\n')
print('prefill stride component prepared')
