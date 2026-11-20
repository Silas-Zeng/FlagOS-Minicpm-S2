"""M2048/2030 wide256真实42层权重工作集；完整开销与数值结果独立保存。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import traceback
from reused_helpers import timed_batch


def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def worker(run,model):
    result=dict(status='started',scope='42个真实O projection权重、M2048/2030、wide256 GEMM；不是模型或官方分数',cases=[],timings=[],
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',limitations=[
            '随机激活及真实权重；没有重放真实模型中间激活。',
            'Graph计时包含完整输出写回；不含Python分配、整个模型及其它算子交织。',
            '不从这组测试承诺所有输入逐位相同，warp布局改变，不能先承诺任意输入逐位。'])
    try:
        import torch
        import candidate
        from safetensors import safe_open
        torch.set_num_threads(4)
        import importlib,inspect,triton
        import triton.language as tl
        module=importlib.import_module('flag_gems.runtime.backend._iluvatar.ops.mm')
        source=Path(inspect.getsourcefile(module.mm));expected='4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
        jit=module.mm_kernel
        while not isinstance(jit,triton.runtime.JITFunction):jit=jit.fn
        (run/'source/installed-mm.py').write_bytes(source.read_bytes())
        result['baseline_source']=dict(path=str(source),sha256=expected)
        index=json.loads((model/'model.safetensors.index.json').read_bytes());weights=[];identities=[]
        for layer in range(42):
            name=f'model.layers.{layer}.self_attn.o_proj.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:w=f.get_tensor(name).contiguous()
            assert w.dtype==torch.bfloat16 and tuple(w.shape)==(2048,2048)
            identities.append(dict(layer=layer,name=name,sha256=hashlib.sha256(w.view(torch.uint8).numpy().tobytes()).hexdigest()))
            weights.append(w.cuda())
        result['weights']=identities;result['weight_bytes']=sum(w.numel()*w.element_size() for w in weights)
        gen=torch.Generator().manual_seed(20261026);cpu=torch.randn((2048,2048),generator=gen,dtype=torch.bfloat16)*.125
        x=cpu.cuda();a=torch.empty((2048,2048),dtype=torch.bfloat16,device='cuda');b=torch.empty_like(a)
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def baseline(xx,w,out):
            return jit[(triton.cdiv(xx.shape[0],256)*16,1)](xx,w.T,out,xx.shape[0],2048,2048,
                2048,1,1,2048,2048,1,acc_dtype=tl.float32,input_precision=None,
                fp8_fast_accum=True,AB_DTYPE=tl.bfloat16,BLOCK_M=256,BLOCK_N=128,BLOCK_K=32,
                GROUP_M=8,SPLIT_K=1,EVEN_K=True,UPGRADE=False,UPGRADE_A_OFFS=False,
                UPGRADE_B_OFFS=False,UPGRADE_C_OFFS=False,num_warps=8,num_stages=2)
        cols=torch.tensor([0,1,17,63,127,255,511,1023,1535,2047],device='cuda')
        def check(m,layer):
            xx=x[:m];aa=a[:m];bb=b[:m];w=weights[layer]
            baseline(xx,w,aa);candidate.launch(xx,w,bb,'wide256');torch.cuda.synchronize()
            rows=torch.tensor([0,1,7,31,63,127,255,511,1023,m-1],device='cuda')
            ref=xx[rows].cpu().double()@w[cols].cpu().double().T
            actual=bb[rows[:,None],cols[None,:]].cpu().double()
            finite=bool(torch.isfinite(aa).all() and torch.isfinite(bb).all())
            passed=finite and bool(torch.allclose(aa,bb,rtol=.01,atol=.001)) and bool(torch.allclose(actual,ref.to(torch.bfloat16).double(),rtol=.01,atol=.001))
            v=dict(layer=layer,rows=m,passed=passed,finite=finite,max_abs_between=float((aa.float()-bb.float()).abs().max()),max_abs_vs_fp64=float((actual-ref).abs().max()),bitwise_equal=bool(torch.equal(aa,bb)))
            result['cases'].append(v);assert passed,'42层数值门失败，停止计时'
        for m in (2048,2030):
            for i in range(42):check(m,i)
        # Capture a whole42-weight sweep; owned scratch lifetime is captured by the graph pool.
        callbacks={}
        for arm in ('A','B'):
            g=torch.cuda.CUDAGraph();torch.cuda.synchronize()
            with torch.cuda.graph(g):
                for w in weights:
                    if arm=='A':baseline(x,w,a)
                    else:candidate.launch(x,w,b,'wide256')
            callbacks[arm]=g
        # Replay with changed same-address input and poisoned output.
        x.copy_(-x.flip(0));a.fill_(float('nan'));b.fill_(float('nan'))
        for g in callbacks.values():g.replay()
        torch.cuda.synchronize();assert torch.isfinite(a).all() and torch.isfinite(b).all() and torch.allclose(a,b,rtol=.01,atol=.001)
        result['changed_graph_last_layer_bitwise']=bool(torch.equal(a,b))
        # A side-stream changed-input case checks changed-input stream ordering.
        stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            baseline(x,weights[0],a);candidate.launch(x,weights[0],b,'wide256')
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
        assert torch.isfinite(b).all() and torch.allclose(a,b,rtol=.01,atol=.001)
        result['side_stream_passed']=True
        for arm in 'ABBA':
            for _ in range(3):callbacks[arm].replay()
            pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
            v=timed_batch(torch,callbacks[arm].replay,pair,16);v['arm']=arm;v['gemms_per_replay']=42
            v['event_per_gemm_ms']=v['event_per_call_ms']/42;v['wall_per_gemm_ms']=v['wall_per_call_ms']/42;result['timings'].append(v)
        result['event_mean_sweep_ms']={arm:statistics.mean(v['event_per_call_ms'] for v in result['timings'] if v['arm']==arm) for arm in 'AB'}
        result['wall_mean_sweep_ms']={arm:statistics.mean(v['wall_per_call_ms'] for v in result['timings'] if v['arm']==arm) for arm in 'AB'}
        assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        result['rng_unchanged']=True;result['status']='completed'
    except BaseException:
        result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    finally:write(run/'result.json',result)
    return 0 if result['status']=='completed' else 1
