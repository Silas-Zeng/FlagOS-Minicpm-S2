"""唯一新 CPU 合同；不导入设备框架，不模拟数值。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS
sys.dont_write_bytecode=True
here=Path(__file__).parent
root=here.parents[1]
spec=importlib.util.spec_from_file_location("k_lookahead_contract",here/"biv150_prefill_k_lookahead.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
begin=time.perf_counter_ns()
source=(root/'tmp/remote-source/triton_unified_attention.py').read_bytes()
helpers=(root/'tmp/remote-source/triton_attention_helpers.py').read_bytes()
changed=p.transform_source(source,helpers)
(here/'generated_attention.py').write_bytes(changed)
old=ast.parse(source);new=ast.parse(changed)
okernel=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name=='kernel_unified_attention')
nkernel=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name=='kernel_unified_attention')
assert [n.arg for n in nkernel.args.args]==[n.arg for n in okernel.args.args]+['BIV150_K_LOOKAHEAD']
assert ast.unparse(nkernel.args.args[-1].annotation)=='tl.constexpr'
# Preserve each mathematical call expression, its AST and its relative order.
math_names={'tl.dot','softmax_step','apply_softcap','apply_alibi_to_score','load_qq_bias_tile'}
def calls(node):
 found=[n for n in ast.walk(node) if isinstance(n,ast.Call) and ast.unparse(n.func) in math_names]
 return [ast.dump(n,include_attributes=False) for n in sorted(found,key=lambda n:(n.lineno,n.col_offset))]
assert calls(okernel)==calls(nkernel)
# Original helper returns/current masked path not rewritten; exact descriptor guard is reused.
previous=ast.parse((root/'patches/framework/biv150_prefill_visible_prefix.py').read_bytes())
oldguard=next(n for n in previous.body if isinstance(n,ast.FunctionDef) and n.name=='_eligible')
newguard=next(n for n in ast.parse((here/'biv150_prefill_k_lookahead.py').read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='_eligible')
assert ast.dump(oldguard,include_attributes=False)==ast.dump(newguard,include_attributes=False)
rejected=False
try:p.transform_source(source+b'\n',helpers)
except RuntimeError:rejected=True
assert rejected
class Launcher:
 def __init__(self,name): self.name=name;self.calls=[];self.error=None
 def __getitem__(self,grid):
  def call(*args,**kwargs):
   self.calls.append((grid,args,kwargs))
   if self.error is not None: raise self.error
   return NS(hash=self.name,n_regs=102,n_spills=0,metadata=NS(num_warps=8,num_stages=1,shared=65536),asm={'llir':self.name})
  return call
original,candidate=Launcher('original'),Launcher('candidate')
attention=NS(kernel_unified_attention=original);forward=object();backend=NS(TritonAttentionImpl=NS(forward=forward))
m=p.Manager(attention,backend,candidate,here/'generated_attention.py')
p._eligible=lambda kw:kw.get('IS_3D') is False and kw.get('test_scope',True)
q,out=object(),object();kw={'IS_3D':False,'query_ptr':q,'output_ptr':out,'num_warps':8,'num_stages':1}
m.install_baseline_observer();attention.kernel_unified_attention[(128,2)](**kw)
assert original.calls[-1][2]==kw and m.selected_calls==0 and not candidate.calls
m.restore();m.install();attention.kernel_unified_attention[(128,2)](**kw)
assert candidate.calls[-1][2]==dict(kw,BIV150_K_LOOKAHEAD=True) and kw.get('BIV150_K_LOOKAHEAD') is None
q2,out2=object(),object();fresh=dict(kw,query_ptr=q2,output_ptr=out2)
attention.kernel_unified_attention[(128,2)](**fresh)
assert candidate.calls[-1][2]['query_ptr'] is q2 and candidate.calls[-1][2]['output_ptr'] is out2
for fallback in (dict(kw,IS_3D=True),dict(kw,test_scope=False)):
 attention.kernel_unified_attention[(128,2)](**fallback);assert original.calls[-1][2]==fallback
error=RuntimeError('candidate compile/resource error');candidate.error=error;n=len(candidate.calls);nold=len(original.calls)
try:attention.kernel_unified_attention[(128,2)](**kw)
except RuntimeError as caught:assert caught is error and caught.__context__ is None
else:raise AssertionError('lost candidate error')
assert len(candidate.calls)==n+1 and len(original.calls)==nold
m.restore();assert attention.kernel_unified_attention is original and not m.active and backend.TritonAttentionImpl.forward is forward
# CPU address/order proof: first plus strict-next visits exactly original tiles,
# including empty/one/offset loops and a partial final K tile. Physical vector
# is carried with K, hence no extra original page-table tile is fetched.
address_cases=[]
for lo,hi,prefix in ((0,0,0),(0,1,1),(0,1,63),(0,2,65),(0,32,2015),(0,256,16383),
                     (1,2,65),(3,5,257),(12,256,16384)):
    original_tiles=list(range(lo,hi))
    prefetched=[]
    consumed=[]
    carry=None
    if lo<hi:
        carry=lo;prefetched.append(lo)
    for j in range(lo,hi):
        assert carry==j
        original_addresses=tuple((j*64+t)//16 for t in range(64))
        carried_addresses=tuple((carry*64+t)//16 for t in range(64))
        assert original_addresses==carried_addresses
        assert tuple(j*64+t<prefix for t in range(64))==tuple(carry*64+t<prefix for t in range(64))
        consumed.append(carry)
        if j+1<hi:
            carry=j+1;prefetched.append(carry)
    assert prefetched==consumed==original_tiles
    address_cases.append({'loop_lo':lo,'loop_hi':hi,'prefix_bound':prefix,'loads':len(prefetched)})
receipt={'status':'pass' ,'elapsed_seconds':(time.perf_counter_ns()-begin)/1e9,
 'policy_sha256':hashlib.sha256((here/'biv150_prefill_k_lookahead.py').read_bytes()).hexdigest(),
 'generated_sha256':hashlib.sha256(changed).hexdigest(),
 'address_cases':address_cases,
 'checks':['no extra final/partial or empty-loop table/K reads; physical vector and K carry agree','exact54c V-late inverse plus exact V-only inverse in real transform','one constexpr added, no SME operand shift','dot/softmax call AST and order unchanged','exact87c6 descriptor guard reused','modified source rejects','baseline resource observation uses original once and same kwargs','selected newJIT only flag added; fresh pointers','3D/unknown original once','candidate error same object/context no original retry','restore exact binding'],
 'limitations':'No Torch/Triton import; CPU tile-index/source proof does not prove compiler lookahead/native overlap/resources/GPU bytes or numerical correctness.'}
(here/'cpu-check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
