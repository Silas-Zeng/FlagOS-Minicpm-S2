"""单一BF16无损N分块格式；真实M64 down配置，不安装到生产。"""
import torch
import triton
import triton.language as tl

PACK_N = 128
CONFIG = dict(BLOCK_M=64, BLOCK_N=128, BLOCK_K=64,
              num_warps=8, num_stages=2, num_ctas=1, SPLIT_K=1)


def pack_cpu(weight):
    """加载时一次位重排，保留三维descriptor：[16,6144,128]。"""
    if (weight.device.type != 'cpu' or weight.dtype != torch.bfloat16
            or tuple(weight.shape) != (2048,6144) or not weight.is_contiguous()):
        raise ValueError('仅CPU原contiguous BF16 down权重[2048,6144]')
    return weight.reshape(16,128,6144).permute(0,2,1).contiguous()


def unpack_cpu(packed):
    if (packed.device.type != 'cpu' or packed.dtype != torch.bfloat16
            or tuple(packed.shape)!=(16,6144,128) or not packed.is_contiguous()):
        raise ValueError('不是固定N128 down packed buffer')
    return packed.permute(0,2,1).contiguous().reshape(2048,6144)


@triton.jit
def nonly_linear(X,P,Y,M,N,K,XS0,YS0,BM:tl.constexpr,BN:tl.constexpr,BK:tl.constexpr):
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
    # 本run固定BN=PACK_N=128：每CTA完整消费一个N分块。
    wp=P+pn*(K*128)+rk[:,None]*128+tl.arange(0,BN)[None,:]
    acc=tl.zeros((BM,BN),tl.float32)
    for block in range(0,tl.cdiv(K,BK)):
        a=tl.load(xp);b=tl.load(wp)
        acc+=tl.dot(a,b,allow_tf32=False)
        xp+=BK
        wp+=BK*128
    mask=(rm[:,None]<M)&(rn[None,:]<N)
    tl.store(Y+rm[:,None]*YS0+rn[None,:],acc.to(tl.bfloat16),mask)


def launch_into(x,packed,output,config):
    m=x.shape[0]
    tensors=(x,packed,output)
    if (m not in (63,64) or tuple(x.shape)!=(m,6144)
            or tuple(packed.shape)!=(16,6144,128) or tuple(output.shape)!=(m,2048)
            or any(t.dtype!=torch.bfloat16 or not t.is_cuda or t.device!=x.device
                   or not t.is_contiguous() for t in tensors)
            or len({t.untyped_storage().data_ptr() for t in tensors})!=3):
        raise ValueError('固定BI-V150 M64/尾M63 down组件，须独立contiguous storage')
    if any(type(config.get(k)) is not int or config[k]!=v for k,v in CONFIG.items()):
        raise ValueError('只接受真实Graph观察配置64/128/64 w8/s2/SPLIT1；不匹配就停')
    with torch.cuda.device(x.device):
        prop=torch.cuda.get_device_properties(x.device)
        if 'BI-V150' not in prop.name or prop.multi_processor_count!=16:
            raise ValueError('仅BI-V150 16SM')
        return nonly_linear[(triton.cdiv(m,64)*16,)](
            x,packed,output,m,2048,6144,6144,2048,BM=64,BN=128,BK=64,
            num_warps=8,num_stages=2,num_ctas=1,enable_fp_fusion=True)
