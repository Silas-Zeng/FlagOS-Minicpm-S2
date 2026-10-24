"""唯一新增 CPU 合同：只核 launch kwargs/计数/还原，不模拟 GPU 数学。"""
import importlib.util
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import time
sys.dont_write_bytecode = True
root=Path(__file__).parent
spec=importlib.util.spec_from_file_location("prefill_w16_cpu",root/"biv150_prefill_w16.py")
p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class Tensor:
    dtype="torch.bfloat16"
    device=NS(type="cuda")
class Original:
    def __init__(self): self.calls=[];self.error=None
    def __getitem__(self,grid):
        def run(*args,**kw):
            self.calls.append((grid,args,kw))
            if self.error is not None: raise self.error
            return NS(hash="synthetic",n_regs=9,n_spills=0,metadata=NS(num_warps=kw.get("num_warps"),num_stages=kw.get("num_stages"),shared=0))
        return run
k=dict(IS_3D=False,HEAD_SIZE=128,HEAD_SIZE_PADDED=128,num_query_heads=16,num_queries_per_kv=8,
       BLOCK_M=128,BLOCK_Q=16,BLOCK_SIZE=16,TILE_SIZE=64,NUM_SEGMENTS_PER_SEQ=1,
       KV_QUANT_MODE=0,SLIDING_WINDOW=0,CHUNK_SIZE=-1,CHUNK_LOOKBACK=-1,num_warps=8,num_stages=1,
       USE_CAUSAL=True,query_ptr=Tensor(),output_ptr=Tensor(),key_cache_ptr=Tensor(),value_cache_ptr=Tensor())
begin=time.perf_counter_ns(); original=Original();attention=NS(kernel_unified_attention=original)
forward=object();backend=NS(TritonAttentionImpl=NS(forward=forward));m=p.Manager(attention,backend)
m.install();attention.kernel_unified_attention[(128,2)](**k)
assert original.calls[-1][2]==dict(k,num_warps=16) and k['num_warps']==8
assert m.snapshot()['compiled_resources']['metadata']['num_warps']==16
fresh=dict(k,query_ptr=Tensor(),output_ptr=Tensor());attention.kernel_unified_attention[(128,2)](**fresh)
assert original.calls[-1][2]['query_ptr'] is fresh['query_ptr']
for name,value in [('IS_3D',True),('num_warps',4),('num_stages',2),('BLOCK_M',256),('TILE_SIZE',128),('USE_SOFTCAP',True),('USE_TD',True),('KV_QUANT_MODE',1)]:
    kw=dict(k);kw[name]=value;attention.kernel_unified_attention[(128,2)](**kw)
    assert original.calls[-1][2]==kw
error=RuntimeError('native compile/resource failure');original.error=error;n=len(original.calls)
try: attention.kernel_unified_attention[(128,2)](**k)
except RuntimeError as caught: assert caught is error and caught.__context__ is None
else: raise AssertionError('lost original error')
assert len(original.calls)==n+1
m.restore();assert not m.active and attention.kernel_unified_attention is original and backend.TritonAttentionImpl.forward is forward
receipt={'status':'pass','elapsed_seconds':(time.perf_counter_ns()-begin)/1e9,'policy_sha256':hashlib.sha256((root/'biv150_prefill_w16.py').read_bytes()).hexdigest(),
         'scope':'CPU launch contract only; fake metadata is not compiled-resource/device/numerical evidence',
         'checks':['only num_warps changes 8 to16','caller kwargs unchanged','current Q/output arguments','3D and seven unknown configs unchanged','compile error same object/context once, no retry','original kernel/forward restore']}
(root/'cpu-check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
