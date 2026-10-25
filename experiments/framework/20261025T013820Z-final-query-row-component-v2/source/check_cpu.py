"""只核新增case几何/P合同和接线；不导入Torch，不重跑原owner/模型suite。"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace as NS
import numpy as np

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('selected_query_cpu_component',ROOT/'component.py')
component=importlib.util.module_from_spec(spec);spec.loader.exec_module(component)
checks=[]
def check(label,value):
    assert value,label
    checks.append(label)

candidate_ast=ast.parse((ROOT/'query_candidate.py').read_bytes())
candidate_nodes={n.name:n for n in candidate_ast.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
p_ast=ast.parse((ROOT.parent/'framework-cache-fix-20261024/vllm_fl/patches/biv150_compute_order.py').read_bytes())
plan=next(n for n in p_ast.body if isinstance(n,ast.ClassDef) and n.name=='Plan')
plan=copy.deepcopy(plan)
plan.body=[n for n in plan.body if isinstance(n,ast.FunctionDef) and n.name=='__init__']
function=copy.deepcopy(candidate_nodes['_cpu_plan'])
class StripImports(ast.NodeTransformer):
    def visit_ImportFrom(self,node):return None
function=StripImports().visit(function)
env=dict(np=np)
exec(compile(ast.fix_missing_locations(ast.Module(body=[plan],type_ignores=[])),'<actual-plan-init>','exec'),env)
env['p']=NS(Plan=env['Plan'])
exec(compile(ast.fix_missing_locations(ast.Module(body=[function],type_ignores=[])),'<actual-cpu-contract>','exec'),env)
geometry_receipts=[]
for number,case in enumerate(component.cases()):
    g=component.geometry(case,20261025+number)
    m,s=sum(case['q']),len(case['q'])
    assert (s,m) in ((32,2048),(40,2048),(64,2048),(5,141))
    reqs=[str(i) for i in range(s)]
    runner=NS(max_num_tokens=2048,input_batch=NS(num_reqs=s,req_ids=reqs,req_id_to_index={r:i for i,r in enumerate(reqs)}))
    output=NS(total_num_scheduled_tokens=m,num_scheduled_tokens=dict(zip(reqs,case['q'])),scheduled_spec_decode_tokens={},scheduled_encoder_inputs={})
    p=env['Plan']({},g['permutation'],g['inverse'],g['physical_q'],g['original_indices']+1,m,0,0)
    actual=None if np.array_equal(g['permutation'],np.arange(s)) else p
    proof=env['_cpu_plan'](runner,output,np.asarray(case['q'],dtype=np.int32),actual)
    assert proof and proof['M']==m and proof['S']==s
    assert set(g['slots']).isdisjoint(g['guards']) and len(g['slots'])==len(set(g['slots']))==m
    assert len(set(x for row in g['pages'] for x in row))==g['cache_blocks']-2
    written=dict(zip(g['slots'],range(m)))
    for row,length in enumerate(g['physical_lens']):
        last_slot=g['pages'][row][(length-1)//16]*16+(length-1)%16
        assert written[last_slot]==int(g['ends'][row])
    assert np.array_equal(g['original_indices'][g['permutation']],g['ends'])
    scattered=np.zeros(m,dtype=np.int32)
    original_values=np.arange(s,dtype=np.int32)+101
    scattered[g['ends']]=original_values[g['permutation']]
    assert np.array_equal(scattered[g['original_indices']],original_values)
    geometry_receipts.append(dict(name=case['name'],M=m,S=s,p_reordered=actual is not None,
        cache_bytes=g['cache_blocks']*2*16*2*128*2,guard_count=len(g['guards']),unique_slots=m))
check('4 exact cases: actual CPU Plan contract, full slots and request order',len(geometry_receipts)==4)
check('P and no-P covered', {x['p_reordered'] for x in geometry_receipts}=={True,False})
check('no full repeated long cache allocation',all(x['cache_bytes']<48*1024**2 for x in geometry_receipts))
check('frozen selected-Q production helper copied byte-exact',component.sha(ROOT/'query_candidate.py')==component.QUERY_SHA)
tree=ast.parse((ROOT/'component.py').read_bytes())
top_imports=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
check('CPU import contains no Torch/Triton/vLLM',not any('torch' in ast.unparse(n) or 'vllm' in ast.unparse(n) or 'triton' in ast.unparse(n) for n in top_imports))
text=(ROOT/'component.py').read_text()
check('two arms use full original K/V and context M slots',text.count('impl.do_kv_cache_update(layer,key,value,cache,ctx.slot_mapping[NAME])')==1
    and "for role in ('mixed','selected_q'):" in text and 'key[:s]' not in text and 'value[:s]' not in text)
check('new numeric route uses actual selected_context and observed GQA calls',
    'candidate._selected_context(original_context,buffers,proof,runner.device)' in text
    and "stats_after['gqa']['calls']-stats_before['gqa']['calls']==1" in text
    and "partial.fill_(float('nan'))" in text)
check('FP32 reference is CPU and no performance gain is calculated',
    'CPU NumPy float32' in text and 'numerical_acceptance=\'unassessed' in text
    and 'end_to_end_gain_claimed=False' in text and 'np.exp(scores)' in text)
for path in ROOT.glob('*.py'):ast.parse(path.read_bytes())
out=dict(passed=len(checks),checks=checks,geometry=geometry_receipts,
    component_sha256=component.sha(ROOT/'component.py'),owner_sha256=component.sha(ROOT/'run_component.py'),
    query_candidate_sha256=component.sha(ROOT/'query_candidate.py'),gpu_executed=False,old_f72_lifecycle_reused=True)
(ROOT/'cpu-check.json').write_bytes((json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps(out,ensure_ascii=False,indent=2))
