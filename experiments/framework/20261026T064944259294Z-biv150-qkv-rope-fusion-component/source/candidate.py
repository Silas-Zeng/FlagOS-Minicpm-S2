"""独立CPU准备原型：原QKV tile后保留BF16舍入再RoPE；未GPU资格。"""
import torch
import triton
import triton.language as tl


@triton.jit
def qkv_rope(X,W,POSITIONS,CACHE,Q,KOUT,VOUT,M:tl.constexpr,CACHE_ROWS:tl.constexpr,
             V_STRIDE:tl.constexpr,BM:tl.constexpr,BN:tl.constexpr,BK:tl.constexpr):
    pid=tl.program_id(0)
    pm=pid//20;pn=pid%20
    rows=pm*BM+tl.arange(0,BM)
    cols=pn*BN+tl.arange(0,BN)
    inner=tl.arange(0,BK)
    rr=rows%M
    xp=X+rr[:,None]*2048+inner[None,:]
    wp=W+cols[None,:]*2048+inner[:,None]
    acc=tl.zeros((BM,BN),tl.float32)
    for block in range(2048//BK):
        x=tl.load(xp);w=tl.load(wp)
        acc=tl.dot(x,w,acc)
        xp+=BK;wp+=BK
    projected=acc.to(tl.bfloat16)
    # BN128每CTA恰有一个完整head，Q16+K2，最后V2不旋转。
    if pn<18:
        lane=tl.arange(0,BN)
        partners=tl.broadcast_to(((lane+64)%128)[None,:],(BM,BN))
        opposite=tl.gather(projected,partners,axis=1).to(tl.float32)
        value=projected.to(tl.float32)
        p=tl.load(POSITIONS+rr)
        p=tl.where(p<0,p+CACHE_ROWS,p)
        tl.device_assert((p>=0)&(p<CACHE_ROWS),'RoPE position超出原cache范围')
        cosine=tl.load(CACHE+p[:,None]*128+(lane%64)[None,:]).to(tl.float32)
        sine=tl.load(CACHE+p[:,None]*128+64+(lane%64)[None,:]).to(tl.float32)
        direct=value*cosine
        crossed=opposite*sine
        rotated=tl.where(lane[None,:]<64,direct-crossed,direct+crossed)
        projected=rotated.to(tl.bfloat16)
    # 沿实际原RoPE返回的独立contiguous Q/K；首门也保留原V的2560行stride。
    if pn<16:
        tl.store(Q+rows[:,None]*2048+cols[None,:],projected,mask=rows[:,None]<M)
    elif pn<18:
        tl.store(KOUT+rows[:,None]*256+(cols-2048)[None,:],projected,mask=rows[:,None]<M)
    else:
        tl.store(VOUT+rows[:,None]*V_STRIDE+(cols-2304)[None,:],projected,mask=rows[:,None]<M)


def launch_into(x,w,positions,cache,query,key,value):
    if (x.shape[0] not in (2030,2048) or tuple(x.shape)!=(x.shape[0],2048)
            or tuple(w.shape)!=(2560,2048) or tuple(query.shape)!=(x.shape[0],2048)
            or tuple(key.shape)!=(x.shape[0],256) or tuple(value.shape)!=(x.shape[0],256)
            or tuple(positions.shape)!=(x.shape[0],) or positions.dtype!=torch.int64
            or cache.ndim!=2 or cache.shape[1]!=128
            or any(t.dtype!=torch.bfloat16 for t in (x,w,cache,query,key,value))
            or any(not t.is_contiguous() for t in (x,w,positions,cache,query,key))
            or value.stride()!=(2560,1)
            or any(t.device!=x.device or not t.is_cuda
                   for t in (x,w,positions,cache,query,key,value))):
        raise ValueError('仅受约束的BI-V150 QKV组件形状；调用者须保证合法positions')
    with torch.cuda.device(x.device):
        props=torch.cuda.get_device_properties(x.device)
        if 'BI-V150' not in props.name or props.multi_processor_count!=16:
            raise ValueError('仅BI-V150 16SM')
        return qkv_rope[(triton.cdiv(x.shape[0],256)*20,)](
            x,w,positions,cache,query,key,value,M=x.shape[0],CACHE_ROWS=cache.shape[0],
            V_STRIDE=2560,BM=256,BN=128,BK=32,num_warps=8,num_stages=2)
