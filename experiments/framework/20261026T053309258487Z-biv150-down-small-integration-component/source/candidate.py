"""Opt-in BF16 small-row MiniCPM projections; original linear above8 rows."""
import os

import torch
import triton
import triton.language as tl

_DEFINITION = None
_IMPLEMENTATION = None
_INSTALLED = False
_OBSERVED_ROWS = set()
_DOWN_SPLIT8_ENABLED = False
_DOWN_SPLIT8_OBSERVED = set()


@triton.jit(do_not_specialize=['M'])
def _small_o_kernel(X, W, Y, M, K: tl.constexpr, XS0: tl.constexpr, XS1: tl.constexpr,
                    WS0: tl.constexpr, WS1: tl.constexpr,
                    YS0: tl.constexpr, YS1: tl.constexpr):
    # All accepted output widths are multiples of64; only M needs masking.
    row = tl.arange(0,16)
    col = tl.program_id(0)*64 + tl.arange(0,64)
    inner = tl.arange(0,128)
    accumulator = tl.zeros((16,64),tl.float32)
    for block in range(K // 128):
        k = block*128 + inner
        a = tl.load(X + row[:,None]*XS0 + k[None,:]*XS1,
                    mask=row[:,None]<M,other=0)
        b = tl.load(W + col[None,:]*WS0 + k[:,None]*WS1)
        accumulator = tl.dot(a,b,accumulator)
    tl.store(Y + row[:,None]*YS0 + col[None,:]*YS1,
             accumulator.to(tl.bfloat16),mask=row[:,None]<M)


def _small_o_into(x, weight, output):
    _small_o_kernel[(weight.shape[0] // 64,)](x,weight,output,x.shape[0],K=x.shape[1],
                           XS0=x.stride(0),XS1=x.stride(1),
                           WS0=weight.stride(0),WS1=weight.stride(1),
                           YS0=output.stride(0),YS1=output.stride(1),
                           num_warps=4,num_stages=1)
    return output


@triton.jit
def _down_split8_produce(X,W,P,M:tl.constexpr,N:tl.constexpr,K:tl.constexpr,
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
def _down_split8_reduce(P,Y,M:tl.constexpr,N:tl.constexpr,S:tl.constexpr,B:tl.constexpr):
    i=tl.program_id(0)*B+tl.arange(0,B)
    parts=tl.arange(0,S)
    values=tl.load(P+parts[:,None]*(M*N)+i[None,:],mask=i[None,:]<M*N,other=0.)
    result=tl.sum(values,axis=0)
    tl.store(Y+i,result.to(tl.bfloat16),mask=i<M*N)



def _linear(x, weight):
    if not (x.ndim==weight.ndim==2 and x.shape[1]==weight.shape[1]
            and tuple(weight.shape) in ((2048,2048),(12288,2048),(2560,2048),(2048,6144))
            and x.dtype==weight.dtype==torch.bfloat16
            and x.device==weight.device and x.device.type=='cuda'
            and 0<x.shape[0]<=8 and x.stride(1)==weight.stride(1)==1
            and x.stride(0)>=x.shape[1] and weight.stride(0)>=weight.shape[1]):
        # On the supported CUDA platform the original framework dispatch is
        # default_unquantized_gemm -> F.linear. Preserve that exact route.
        return torch.nn.functional.linear(x,weight)
    with torch.cuda.device(x.device):
        key=(x.shape[0],weight.shape[0],weight.shape[1])
        if key not in _OBSERVED_ROWS and not torch.cuda.is_current_stream_capturing():
            _OBSERVED_ROWS.add(key)
            print('BIV150_STABLE_SMALL_O_SELECTED', {
                'rows': x.shape[0], 'output_columns': weight.shape[0], 'input_columns': weight.shape[1], 'input_stride': tuple(x.stride()),
                'weight_stride': tuple(weight.stride()), 'warps': 4, 'stages': 1,
            }, flush=True)
        output=torch.empty((x.shape[0],weight.shape[0]),device=x.device,dtype=x.dtype)
        if (_DOWN_SPLIT8_ENABLED and tuple(weight.shape)==(2048,6144)
                and x.is_contiguous() and weight.is_contiguous()):
            scratch=torch.empty((8,x.shape[0],2048),device=x.device,dtype=torch.float32)
            _down_split8_produce[(32,8)](x,weight,scratch,M=x.shape[0],N=2048,K=6144,
                BM=16,BN=64,BK=128,S=8,num_warps=4,num_stages=1)
            _down_split8_reduce[(triton.cdiv(x.shape[0]*2048,256),)](
                scratch,output,M=x.shape[0],N=2048,S=8,B=256,num_warps=4,num_stages=1)
            if x.shape[0] not in _DOWN_SPLIT8_OBSERVED and not torch.cuda.is_current_stream_capturing():
                _DOWN_SPLIT8_OBSERVED.add(x.shape[0])
                print('BIV150_DOWN_SPLIT8_SELECTED', {
                    'rows':x.shape[0],'N':2048,'K':6144,'S':8,'BM':16,'BN':64,'BK':128,
                    'warps':4,'stages':1,'scratch_bytes':8*x.shape[0]*2048*4,
                    'input_stride':tuple(x.stride()),'weight_stride':tuple(weight.stride()),
                },flush=True)
            return output
        return _small_o_into(x,weight,output)


def _register():
    global _DEFINITION,_IMPLEMENTATION
    if _DEFINITION is not None:return
    definition=torch.library.Library('biv150_stable_small_o','DEF')
    definition.define('linear(Tensor input, Tensor weight) -> Tensor')
    implementation=torch.library.Library('biv150_stable_small_o','IMPL','CUDA')
    implementation.impl('linear',_linear)
    @torch.library.register_fake('biv150_stable_small_o::linear')
    def fake(x,weight):
        return torch.empty((x.shape[0],weight.shape[0]),dtype=x.dtype,device=x.device)
    _DEFINITION,_IMPLEMENTATION=definition,implementation


def install():
    global _INSTALLED, _DOWN_SPLIT8_ENABLED
    if os.environ.get('VLLM_FL_BIV150_STABLE_SMALL_O','1')!='1':
        return {'installed':False,'reason':'disabled'}
    if _INSTALLED:return {'installed':True,'reason':'already installed'}
    from vllm_fl.patches.biv150_native_w8a8 import _eligible_model
    if not _eligible_model():return {'installed':False,'reason':'unsupported model'}
    from vllm.distributed import get_tensor_model_parallel_world_size
    if get_tensor_model_parallel_world_size()!=1:
        return {'installed':False,'reason':'TP1 required'}
    from vllm import envs
    from vllm.model_executor.layers.utils import dispatch_unquantized_gemm, default_unquantized_gemm
    if envs.VLLM_BATCH_INVARIANT or dispatch_unquantized_gemm() is not default_unquantized_gemm:
        return {'installed':False,'reason':'unsupported original GEMM dispatch'}
    from vllm.model_executor.layers.linear import UnquantizedLinearMethod
    _DOWN_SPLIT8_ENABLED = ('BI-V150' in torch.cuda.get_device_name()
        and torch.cuda.get_device_properties(torch.cuda.current_device()).multi_processor_count == 16)
    _register()
    previous=UnquantizedLinearMethod.apply
    def apply(self,layer,x,bias=None):
        projection=(layer.prefix.endswith('.self_attn.o_proj') and tuple(layer.weight.shape)==(2048,2048)
                    or layer.prefix.endswith('.mlp.gate_up_proj') and tuple(layer.weight.shape)==(12288,2048)
                    or layer.prefix.endswith('.self_attn.qkv_proj') and tuple(layer.weight.shape)==(2560,2048)
                    or layer.prefix.endswith('.mlp.down_proj') and tuple(layer.weight.shape)==(2048,6144))
        if (bias is not None or not projection or hasattr(layer,'_biv150_native_wq')
                or layer.weight.dtype!=torch.bfloat16):
            return previous(self,layer,x,bias)
        # M dispatch is inside the opaque CUDA implementation, keeping vLLM's
        # dynamic row dimension out of Python/Dynamo shape branches.
        output=torch.ops.biv150_stable_small_o.linear(x.reshape(-1,layer.weight.shape[1]),layer.weight)
        return output.reshape(*x.shape[:-1],layer.weight.shape[0])
    UnquantizedLinearMethod.apply=apply
    _INSTALLED=True
    print('BIV150_DOWN_SPLIT8_INSTALL', {'installed':_DOWN_SPLIT8_ENABLED,
        'scope':'BI-V150 16SM BF16 contiguous down M1-8 N2048 K6144'},flush=True)
    return {'installed':True,'scope':'BF16 TP1 QKV/O/down and uncompressed edge-gate projections M1-8',
            'block_m':16,'block_n':64,'block_k':128,'warps':4,'stages':1,
            'larger_rows':'original default_unquantized_gemm F.linear route inside the opaque operation'}
