"""单一BF16无损微块格式，独立down消费者；不安装到生产。"""
import torch
import triton
import triton.language as tl

PACK_N, PACK_K = 256, 128


def pack_cpu(weight):
    """加载时一次纯重排：P[N/256,K/128,256,128]，不做浮点运算。"""
    if (weight.device.type != 'cpu' or weight.dtype != torch.bfloat16
            or tuple(weight.shape) != (2048,6144) or not weight.is_contiguous()):
        raise ValueError('仅CPU原contiguous BF16 down权重[2048,6144]')
    return weight.reshape(8,256,48,128).permute(0,2,1,3).contiguous().flatten()


def unpack_cpu(packed):
    if packed.device.type != 'cpu' or packed.dtype != torch.bfloat16 or packed.numel()!=2048*6144:
        raise ValueError('不是固定down packed buffer')
    return packed.reshape(8,48,256,128).permute(0,2,1,3).contiguous().reshape(2048,6144)


@triton.jit
def packed_linear(X,P,Y,M,N,K,XS0,YS0,BM:tl.constexpr,BN:tl.constexpr,BK:tl.constexpr):
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
    # BN须整除PACK_N，故整个CTA的N都落同一256列微块。
    group_n=(pn*BN)//256
    local_n=(pn*BN)%256+tl.arange(0,BN)
    wp=P+group_n*(K*256)+local_n[None,:]*128+rk[:,None]
    acc=tl.zeros((BM,BN),tl.float32)
    for block in range(0,tl.cdiv(K,BK)):
        a=tl.load(xp);b=tl.load(wp)
        acc+=tl.dot(a,b,allow_tf32=False)
        xp+=BK
        if BK==128:
            wp+=256*128
        else:
            # 原K遍历不变；只在固定128跨度边界跳过微块其它N行。
            wp+=tl.where((block+1)%(128//BK)==0,256*128-128+BK,BK)
    mask=(rm[:,None]<M)&(rn[None,:]<N)
    tl.store(Y+rm[:,None]*YS0+rn[None,:],acc.to(tl.bfloat16),mask)


def launch_into(x,packed,output,config):
    m=x.shape[0]
    tensors=(x,packed,output)
    if (m not in (2030,2048) or tuple(x.shape)!=(m,6144)
            or tuple(packed.shape)!=(2048*6144,) or tuple(output.shape)!=(m,2048)
            or any(t.dtype!=torch.bfloat16 or not t.is_cuda or t.device!=x.device
                   or not t.is_contiguous() for t in tensors)
            or len({t.untyped_storage().data_ptr() for t in tensors})!=3):
        raise ValueError('固定BI-V150 down组件，输入/packed/output须独立contiguous storage')
    required=('BLOCK_M','BLOCK_N','BLOCK_K','num_warps','num_stages','num_ctas')
    if (any(type(config.get(k)) is not int for k in required)
            or config.get('SPLIT_K',1)!=1 or config['num_ctas']!=1
            or config['BLOCK_N'] not in (32,64,128,256)
            or config['BLOCK_K'] not in (32,64,128)
            or any(config[k]<=0 for k in required)):
        raise ValueError('只消费原实际linear被选配置；唯一pack格式不兼容就停，不改tile')
    with torch.cuda.device(x.device):
        prop=torch.cuda.get_device_properties(x.device)
        if 'BI-V150' not in prop.name or prop.multi_processor_count!=16:
            raise ValueError('仅BI-V150 16SM')
        bm,bn,bk=(config[k] for k in ('BLOCK_M','BLOCK_N','BLOCK_K'))
        return packed_linear[(triton.cdiv(m,bm)*triton.cdiv(2048,bn),)](
            x,packed,output,m,2048,6144,6144,2048,BM=bm,BN=bn,BK=bk,
            num_warps=config['num_warps'],num_stages=config['num_stages'],
            num_ctas=1,enable_fp_fusion=True)
