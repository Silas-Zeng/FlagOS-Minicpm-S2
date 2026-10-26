"""真实down权重组件；原JIT配置、FP64抽样、完整输出/Graph/guard及ABBA。"""
import hashlib
import importlib
import inspect
import json
from pathlib import Path
import statistics
import traceback
from reused_helpers import timed_batch

MM_SHA = '4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090'
BASE_CONFIG = dict(BLOCK_M=256, BLOCK_N=128, BLOCK_K=32, SPLIT_K=1,
    GROUP_M=8, EVEN_K=True, UPGRADE=False,
    UPGRADE_A_OFFS=False, UPGRADE_B_OFFS=False, UPGRADE_C_OFFS=False,
    num_warps=8, num_stages=2)


def write(p, v):
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2, allow_nan=False)+'\n')


def dump(compiled, path):
    path.mkdir()
    for k,v in compiled.asm.items():
        if isinstance(v,(str,bytes)):
            (path/(k+('.bin' if isinstance(v,bytes) else '.txt'))).write_bytes(v if isinstance(v,bytes) else v.encode())
    return dict(hash=compiled.hash, n_regs=getattr(compiled,'n_regs',None),
        n_spills=getattr(compiled,'n_spills',None),metadata=str(compiled.metadata))


def worker(run, model):
    result=dict(status='started',shape=[2048,2048,6144],baseline=BASE_CONFIG,
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',seed=20261026,cases=[],
        scope='独立BF16 down GEMM组件；原模型权重，非整模型或官方性能资格',
        limitations=['BM256/BN256/BK32/w16/s2，同原BK/loop/无mask读取，扩大N复用A tile；理论panel请求减少，实际shared增加至64KiB。',
            'warm单权重组件不代表42层工作集；组件正向后才测试完整工作集。',
            'CPU FP64仅抽样，完整输出同时对原JIT比较；无新量化、split-K或库路由。'])
    try:
        import torch
        import triton
        import triton.language as tl
        import candidate
        from safetensors import safe_open
        torch.set_num_threads(4)
        props=torch.cuda.get_device_properties(0)
        assert 'BI-V150' in props.name
        result['environment']=dict(torch=torch.__version__,triton=triton.__version__,
            gpu=props.name,sm=props.multi_processor_count,properties=str(props),cpu_threads=4)
        module=importlib.import_module('flag_gems.runtime.backend._iluvatar.ops.mm')
        source=Path(inspect.getsourcefile(module.mm));assert hashlib.sha256(source.read_bytes()).hexdigest()==MM_SHA
        (run/'source/installed-mm.py').write_bytes(source.read_bytes())
        jit=module.mm_kernel
        while not isinstance(jit,triton.runtime.JITFunction):jit=jit.fn
        result['candidate_configs']=candidate.CONFIGS
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        name='model.layers.0.mlp.down_proj.weight';shard=model/index['weight_map'][name]
        with safe_open(str(shard),framework='pt',device='cpu') as f:wc=f.get_tensor(name).contiguous()
        assert tuple(wc.shape)==(2048,6144) and wc.dtype==torch.bfloat16
        result['weight']=dict(name=name,shard=shard.name,sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest())
        gen=torch.Generator().manual_seed(result['seed'])
        xc=torch.randn((2048,6144),generator=gen,dtype=torch.bfloat16)*.125
        w=wc.cuda();x=xc.cuda();x2=xc.flip(0).contiguous().cuda();w2=wc.flip(0).contiguous().cuda()
        buffers=[torch.full((2048*2048+64,),123.,device='cuda',dtype=torch.bfloat16) for _ in range(1+len(candidate.CONFIGS))]
        outputs=[v[32:-32].view(2048,2048) for v in buffers]
        a=outputs[0]
        def baseline(inp,weight,out):
            return jit[(triton.cdiv(inp.shape[0],256)*16,1)](inp,weight.T,out,
                inp.shape[0],2048,6144,6144,1,1,6144,2048,1,
                acc_dtype=tl.float32, AB_DTYPE=tl.bfloat16,
                input_precision=None,fp8_fast_accum=True,**BASE_CONFIG)
        compiled={'baseline':baseline(x,w,a)}
        for label,out in zip(candidate.CONFIGS,outputs[1:]):compiled[label]=candidate.launch(x,w,out,label)
        torch.cuda.synchronize()
        result['resources']={label:dump(v,run/('ir-'+label)) for label,v in compiled.items()}
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        row_ids=torch.tensor([0,1,7,31,63,127,255,511,1023,2029,2047]);col_ids=torch.tensor([0,1,17,63,127,255,511,1023,1535,2047])
        def check(inp,weight,out,refbase,m,label):
            rows=row_ids[row_ids<m];ref=inp.cpu()[rows].double()@weight.cpu()[col_ids].double().T
            actual=out[rows.cuda()[:,None],col_ids.cuda()[None,:]].cpu().double()
            err=(actual-ref).abs();finite=bool(torch.isfinite(out).all())
            max_between=float((out.float()-refbase.float()).abs().max())
            rel=float((out.float()-refbase.float()).norm()/refbase.float().norm())
            passed=finite and bool(torch.allclose(actual,ref.to(torch.bfloat16).double(),rtol=.01,atol=.001)) and bool(torch.allclose(out,refbase,rtol=.01,atol=.001))
            return dict(label=label,rows=m,finite=finite,max_abs_vs_fp64=float(err.max()),
                max_abs_vs_baseline=max_between,relative_l2_vs_baseline=rel,passed=passed)
        # Natural tail2030, exact2048, changed pointers/content, and same-address Graph replay.
        for case,inp,weight in [('original',x,w),('changed-pointers',x2,w2)]:
            for m in (2048,2030):
                xx=inp[:m];base=a[:m];baseline(xx,weight,base)
                for label,out in zip(candidate.CONFIGS,outputs[1:]):
                    oo=out[:m];candidate.launch(xx,weight,oo,label);torch.cuda.synchronize()
                    v=check(xx,weight,oo,base,m,label);v['case']=case;result['cases'].append(v);write(run/'result.json',result)
                    assert v['passed'], '数值失败，不进行性能计时'
        baseline(x,w,a)
        graphs={}
        for label,out in zip(candidate.CONFIGS,outputs[1:]):
            g=torch.cuda.CUDAGraph()
            with torch.cuda.graph(g):candidate.launch(x,w,out,label)
            graphs[label]=g
        x.copy_(x2);w.copy_(w2);baseline(x,w,a)
        for label,out in zip(candidate.CONFIGS,outputs[1:]):
            out.fill_(float('nan'));graphs[label].replay();torch.cuda.synchronize()
            v=check(x,w,out,a,2048,label);v['case']='same-address-changed-poisoned-graph';result['cases'].append(v);assert v['passed']
        assert all(bool((v[:32]==123).all() and (v[-32:]==123).all()) for v in buffers)
        assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        result['rng_unchanged']=True;result['guards_unchanged']=True
        # Graph windows contain8 complete GEMMs; all outputs are materialized.
        callbacks={'baseline':lambda:baseline(x,w,a)}
        callbacks.update({label:(lambda l=label,o=out:candidate.launch(x,w,o,l)) for label,out in zip(candidate.CONFIGS,outputs[1:])})
        gcallbacks={}
        for label,callback in callbacks.items():
            callback();torch.cuda.synchronize();g=torch.cuda.CUDAGraph()
            with torch.cuda.graph(g):
                for _ in range(8):callback()
            gcallbacks[label]=g.replay
        result['timings']=[]
        order=['baseline','wide256','wide256','baseline']
        for label in order:
            for _ in range(1+len(candidate.CONFIGS)):gcallbacks[label]()
            pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
            r=timed_batch(torch,gcallbacks[label],pair,8);r.update(arm=label,gemms_per_replay=8)
            r['event_per_gemm_ms']=r['event_per_call_ms']/8;r['wall_per_gemm_ms']=r['wall_per_call_ms']/8
            result['timings'].append(r)
        result['event_mean_ms']={l:statistics.mean(v['event_per_gemm_ms'] for v in result['timings'] if v['arm']==l) for l in callbacks}
        result['wall_mean_ms']={l:statistics.mean(v['wall_per_gemm_ms'] for v in result['timings'] if v['arm']==l) for l in callbacks}
        result['post_timing_finite']=all(bool(torch.isfinite(o).all()) for o in outputs)
        assert result['post_timing_finite']
        result['post_timing_checks']=[check(x,w,out,a,2048,label) for label,out in zip(candidate.CONFIGS,outputs[1:])]
        assert all(v['passed'] for v in result['post_timing_checks'])
        assert all(bool((v[:32]==123).all() and (v[-32:]==123).all()) for v in buffers)
        result['status']='completed'
    except BaseException:
        result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    finally:write(run/'result.json',result)
    return 0 if result['status']=='completed' else 1
