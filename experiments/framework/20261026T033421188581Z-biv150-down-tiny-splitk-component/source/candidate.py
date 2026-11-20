"""M64 down GEMM固定SplitK4，包含FP32 partial producer与reducer。"""
import torch
import triton
import triton.language as tl

CONFIGS={'split4':dict(BM=16,BN=64,BK=128,S=4,num_warps=4,num_stages=1),
         'split8':dict(BM=16,BN=64,BK=128,S=8,num_warps=4,num_stages=1)}
LAST_REDUCER=None


@triton.jit
def produce(X,W,P,M:tl.constexpr,N:tl.constexpr,K:tl.constexpr,
            BM:tl.constexpr,BN:tl.constexpr,BK:tl.constexpr,S:tl.constexpr):
    pid=tl.program_id(0); split=tl.program_id(1)
    rows=pid//(N//BN)*BM+tl.arange(0,BM)
    cols=pid%(N//BN)*BN+tl.arange(0,BN)
    k=split*(K//S)+tl.arange(0,BK)
    xp=X+(rows%M)[:,None]*K+k[None,:]
    wp=W+cols[None,:]*K+k[:,None]
    acc=tl.zeros((BM,BN),tl.float32)
    for block in range(K//S//BK):
        a=tl.load(xp);b=tl.load(wp)
        acc=tl.dot(a,b,acc)
        xp+=BK;wp+=BK
    tl.store(P+(split*M+rows[:,None])*N+cols[None,:],acc,mask=rows[:,None]<M)


@triton.jit
def reduce(P,Y,M:tl.constexpr,N:tl.constexpr,S:tl.constexpr,B:tl.constexpr):
    i=tl.program_id(0)*B+tl.arange(0,B)
    parts=tl.arange(0,S)
    values=tl.load(P+parts[:,None]*(M*N)+i[None,:],mask=i[None,:]<M*N,other=0.)
    result=tl.sum(values,axis=0)
    tl.store(Y+i,result.to(tl.bfloat16),mask=i<M*N)


def launch(x,w,out,variant):
    global LAST_REDUCER
    assert variant in CONFIGS and x.shape[0] in (1,2) and x.shape[1]==6144
    assert tuple(w.shape)==(2048,6144) and tuple(out.shape)==(x.shape[0],2048)
    assert x.is_contiguous() and w.is_contiguous() and out.is_contiguous()
    assert x.dtype==w.dtype==out.dtype==torch.bfloat16
    c=CONFIGS[variant]
    scratch=torch.empty((c['S'],x.shape[0],2048),device=x.device,dtype=torch.float32)
    compiled=produce[(32,c['S'])](x,w,scratch,M=x.shape[0],N=2048,K=6144,**c)
    LAST_REDUCER=reduce[(triton.cdiv(x.shape[0]*2048,256),)](
        scratch,out,M=x.shape[0],N=2048,S=c['S'],B=256,num_warps=4,num_stages=1)
    return compiled
