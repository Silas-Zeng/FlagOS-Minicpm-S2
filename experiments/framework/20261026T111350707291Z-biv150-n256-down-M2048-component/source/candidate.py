"""唯一N256权重格式；M2048优先，原真实tile全部保持，不装生产。"""
import torch
import triton
import triton.language as tl

PACK_N = 256


def pack_cpu(weight):
    """加载时一次位重排，保留三维descriptor：[8,6144,256]。"""
    if (weight.device.type != 'cpu' or weight.dtype != torch.bfloat16
            or tuple(weight.shape) != (2048,6144) or not weight.is_contiguous()):
        raise ValueError('仅CPU原contiguous BF16 down权重[2048,6144]')
    return weight.reshape(8,256,6144).permute(0,2,1).contiguous()


def unpack_cpu(packed):
    if (packed.device.type != 'cpu' or packed.dtype != torch.bfloat16
            or tuple(packed.shape)!=(8,6144,256) or not packed.is_contiguous()):
        raise ValueError('不是固定N256 down packed buffer')
    return packed.permute(0,2,1).contiguous().reshape(2048,6144)


@triton.jit
def n256_linear(X,P,Y,M,N,K,XS0,YS0,BM:tl.constexpr,BN:tl.constexpr,BK:tl.constexpr):
    pid=tl.program_id(0)
    grid_m=tl.cdiv(M,BM);grid_n=tl.cdiv(N,BN)
    width=8*grid_n;group_id=pid//width
    group_size=min(grid_m-group_id*8,8)
    pm=group_id*8+pid%group_size
    pn=(pid%width)//group_size
    rm=pm*BM+tl.arange(0,BM)
    rn=pn*BN+tl.arange(0,BN)
    ram=tl.max_contiguous(tl.multiple_of(rm%M,BM),BM)
    rk=tl.arange(0,BK)
    xp=X+ram[:,None]*XS0+rk[None,:]
    # BN整除256，CTA不跨物理N256分块；支持原BN32/64/128/256。
    start_n=pn*BN
    wp=P+(start_n//256)*(K*256)+rk[:,None]*256+(start_n%256+tl.arange(0,BN)[None,:])
    acc=tl.zeros((BM,BN),tl.float32)
    for block in range(0,tl.cdiv(K,BK)):
        a=tl.load(xp);b=tl.load(wp)
        acc+=tl.dot(a,b,allow_tf32=False)
        xp+=BK
        wp+=BK*256
    mask=(rm[:,None]<M)&(rn[None,:]<N)
    tl.store(Y+rm[:,None]*YS0+rn[None,:],acc.to(tl.bfloat16),mask)


def launch_into(x,packed,output,config):
    m=x.shape[0]
    tensors=(x,packed,output)
    if (m not in (32,64,2048) or tuple(x.shape)!=(m,6144)
            or tuple(packed.shape)!=(8,6144,256) or tuple(output.shape)!=(m,2048)
            or any(t.dtype!=torch.bfloat16 or not t.is_cuda or t.device!=x.device
                   or not t.is_contiguous() for t in tensors)
            or len({t.untyped_storage().data_ptr() for t in tensors})!=3):
        raise ValueError('固定BI-V150 M32/M64/M2048 down组件，须独立contiguous storage')
    required=('BLOCK_M','BLOCK_N','BLOCK_K','num_warps','num_stages','num_ctas','SPLIT_K')
    if (any(type(config.get(k)) is not int or config[k]<=0 for k in required)
            or config['BLOCK_M'] not in (32,64,128,256)
            or config['BLOCK_N'] not in (32,64,128,256)
            or config['BLOCK_K'] not in (32,64,128)
            or config['num_warps'] not in (4,8,16)
            or config['num_stages'] not in (1,2,3,4)
            or config['num_ctas']!=1 or config['SPLIT_K']!=1):
        raise ValueError('只接受原真实BM/BN/BK/warp/stage，BN≤256且整除256；不符就停')
    with torch.cuda.device(x.device):
        prop=torch.cuda.get_device_properties(x.device)
        if 'BI-V150' not in prop.name or prop.multi_processor_count!=16:
            raise ValueError('仅BI-V150 16SM')
        bm,bn,bk=(config[k] for k in ('BLOCK_M','BLOCK_N','BLOCK_K'))
        return n256_linear[(triton.cdiv(m,bm)*triton.cdiv(2048,bn),)](
            x,packed,output,m,2048,6144,6144,2048,BM=bm,BN=bn,BK=bk,
            num_warps=config['num_warps'],num_stages=config['num_stages'],
            num_ctas=1,enable_fp_fusion=True)
