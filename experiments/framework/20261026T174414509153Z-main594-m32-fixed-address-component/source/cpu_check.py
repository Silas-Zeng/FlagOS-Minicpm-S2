from pathlib import Path
import ast,copy,hashlib,json
import numpy as np
HERE=Path(__file__).resolve().parent
def main():
    t=ast.parse((HERE/'candidate.py').read_bytes());fn=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='fixed_address_mm')
    karg=next(a for a in fn.args.args if a.arg=='K');assert karg.annotation is None
    loop=next(n for n in ast.walk(fn) if isinstance(n,ast.For));assert ast.unparse(loop.iter)=='range(0, tl.cdiv(K, BLOCK_K))'
    assert not any(isinstance(n,(ast.If,ast.IfExp)) for n in ast.walk(loop))
    dot=next(n for n in ast.walk(loop) if isinstance(n,ast.Call) and ast.unparse(n.func)=='tl.dot')
    assert ast.unparse(dot)=='tl.dot(a, b, acc, out_dtype=tl.float32, input_precision=None)'
    assert any(isinstance(n,ast.Assign) and len(n.targets)==1 and ast.unparse(n.targets[0])=='acc' and n.value is dot for n in ast.walk(loop))
    original=ast.parse((HERE/'original-installed-mm.py').read_bytes())
    old=next(n for n in ast.walk(original) if isinstance(n,ast.Call) and ast.unparse(n.func)=='tl.dot' and len(n.args)==3)
    old=copy.deepcopy(old)
    for kw in old.keywords:
        if kw.arg=='out_dtype':kw.value=ast.Attribute(value=ast.Name(id='tl',ctx=ast.Load()),attr='float32',ctx=ast.Load())
        if kw.arg=='input_precision':kw.value=ast.Constant(value=None)
    assert ast.dump(old,include_attributes=False)==ast.dump(dot,include_attributes=False)
    cfg=next(n for n in t.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='CONFIG')
    config={k.arg:ast.literal_eval(k.value) for k in cfg.value.keywords}
    assert config==dict(BLOCK_M=32,BLOCK_N=64,BLOCK_K=128,SPLIT_K=1,num_warps=8,num_stages=2,num_ctas=1)
    M,N,K,BM,BN,BK=32,2048,6144,32,64,128;coverage=np.zeros((M,N),np.uint8);tiles=0
    for pid in range(32):
        original_gn=(N+BN-1)//BN;pm=pid//original_gn;pn=pid%original_gn
        rm=pm*BM+np.arange(BM,dtype=np.int64);rn=pn*BN+np.arange(BN,dtype=np.int64)
        assert np.array_equal(rm%M,rm) and np.array_equal(rn%N,rn) and pm==pid//32 and pn==pid%32
        ap=rm[:,None]*K+np.arange(BK,dtype=np.int64)[None,:]
        bp=np.arange(BK,dtype=np.int64)[:,None]+rn[None,:]*K
        for block in range(K//BK):
            ks=block*BK+np.arange(BK,dtype=np.int64)
            assert np.array_equal(ap,(rm%M)[:,None]*K+ks[None,:])
            assert np.array_equal(bp,ks[:,None]+(rn%N)[None,:]*K)
            assert ap.min()>=0 and ap.max()<M*K and bp.min()>=0 and bp.max()<N*K
            ap+=BK;bp+=BK;tiles+=1
        coverage[rm[:,None],rn[None,:]]+=1
    assert np.all(coverage==1)
    jit_call=next(n for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Subscript) and ast.unparse(n.func.value)=='fixed_address_mm')
    assert ast.unparse(jit_call.args[1])=='weight.t()'
    weight=np.empty((N,K),dtype=np.uint16);view=weight.T
    assert view.shape==(K,N) and tuple(v//view.itemsize for v in view.strides)==(1,K) and np.shares_memory(weight,view)
    launch=next(n for n in t.body if isinstance(n,ast.FunctionDef) and n.name=='launch_into')
    assert any(isinstance(n,ast.Compare) and ast.unparse(n).startswith('tuple(x.shape) != (32, 6144)') for n in ast.walk(launch))
    for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
    w=(HERE/'worker.py').read_text();assert "assert len(result['cases'])==8" in w and "for arm in 'ABBA':" in w and 'M31' not in w
    result=dict(status='CPU_ONLY_NOT_GPU_QUALIFIED',fixed_config=config,runtime_K_not_constexpr=True,original_dot_with_acc_AST=True,
        tile_address_cases=tiles,output_exactly_once=True,M32_only=True,tail_qualification=False,pack=False,extra_weight_bytes=0,
        B_JIT_argument='weight.t()',B_view_shape=[K,N],B_view_stride=[1,K],B_aliases_original_weight=True,
        candidate_sha256=hashlib.sha256((HERE/'candidate.py').read_bytes()).hexdigest(),
        compiler_rcp_SME_resources_and_performance_unverified=True)
    (HERE/'cpu-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,ensure_ascii=False))
if __name__=='__main__':main()
