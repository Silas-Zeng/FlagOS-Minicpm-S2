"""M1/2 SplitK8真实42层权重工作集；完整开销与数值结果独立保存。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import traceback
from reused_helpers import timed_batch


def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n')


def worker(run,model):
    result=dict(status='started',scope='42个真实down权重、M1/2、SplitK8含scratch/归约；不是模型或官方分数',cases=[],timings=[],
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',limitations=[
            '随机激活及真实权重；没有重放真实模型中间激活。',
            'Graph计时包含producer与reducer，不含Python分配、整个模型及其它算子交织。',
            '不从这组测试承诺所有输入逐位相同，FP32分段归约改变计算分组。'])
    try:
        import torch
        import candidate
        from safetensors import safe_open
        torch.set_num_threads(4)
        source=Path('/workspace/experiments/minicpm-s2/code/main34942f7-prefill-stride-aa43ea2c/vllm_fl/patches/biv150_stable_small_o.py')
        expected='c5a2dd6c69c514531fee4145621e51bd4e41c0d784f4d4e086fe48aad98104ba'
        assert hashlib.sha256(source.read_bytes()).hexdigest()==expected
        spec=importlib.util.spec_from_file_location('stable_original',source);original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
        (run/'source/original-stable-small-o.py').write_bytes(source.read_bytes())
        result['baseline_source']=dict(path=str(source),sha256=expected)
        index=json.loads((model/'model.safetensors.index.json').read_bytes());weights=[];identities=[]
        for layer in range(42):
            name=f'model.layers.{layer}.mlp.down_proj.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:w=f.get_tensor(name).contiguous()
            assert w.dtype==torch.bfloat16 and tuple(w.shape)==(2048,6144)
            identities.append(dict(name=name,sha256=hashlib.sha256(w.view(torch.uint8).numpy().tobytes()).hexdigest()))
            weights.append(w.cuda())
        result['weights']=identities;result['weight_bytes']=sum(w.numel()*w.element_size() for w in weights)
        gen=torch.Generator().manual_seed(20261026);cpu=torch.randn((2,6144),generator=gen,dtype=torch.bfloat16)*.125
        x=cpu.cuda();a=torch.empty((2,2048),dtype=torch.bfloat16,device='cuda');b=torch.empty_like(a)
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def baseline(xx,w,out):
            return original._small_o_kernel[(32,)](xx,w,out,xx.shape[0],K=6144,
                XS0=6144,XS1=1,WS0=6144,WS1=1,YS0=2048,YS1=1,num_warps=4,num_stages=1)
        cols=torch.tensor([0,1,17,63,127,255,511,1023,1535,2047],device='cuda')
        def check(m,layer):
            xx=x[:m];aa=a[:m];bb=b[:m];w=weights[layer]
            baseline(xx,w,aa);candidate.launch(xx,w,bb,'split8');torch.cuda.synchronize()
            ref=xx.cpu().double()@w[cols].cpu().double().T
            actual=bb[:,cols].cpu().double()
            finite=bool(torch.isfinite(aa).all() and torch.isfinite(bb).all())
            passed=finite and bool(torch.allclose(aa,bb,rtol=.01,atol=.001)) and bool(torch.allclose(actual,ref.to(torch.bfloat16).double(),rtol=.01,atol=.001))
            v=dict(layer=layer,rows=m,passed=passed,finite=finite,max_abs_between=float((aa.float()-bb.float()).abs().max()),max_abs_vs_fp64=float((actual-ref).abs().max()),bitwise_equal=bool(torch.equal(aa,bb)))
            result['cases'].append(v);assert passed,'42层数值门失败，停止计时'
        for m in (2,1):
            for i in range(42):check(m,i)
        # Capture a whole42-weight sweep; owned scratch lifetime is captured by the graph pool.
        callbacks={}
        for arm in ('A','B'):
            g=torch.cuda.CUDAGraph();torch.cuda.synchronize()
            with torch.cuda.graph(g):
                for w in weights:
                    if arm=='A':baseline(x,w,a)
                    else:candidate.launch(x,w,b,'split8')
            callbacks[arm]=g
        # Replay with changed same-address input and poisoned output.
        x.copy_(-x.flip(0));a.fill_(float('nan'));b.fill_(float('nan'))
        for g in callbacks.values():g.replay()
        torch.cuda.synchronize();assert torch.isfinite(a).all() and torch.isfinite(b).all() and torch.allclose(a,b,rtol=.01,atol=.001)
        result['changed_graph_last_layer_bitwise']=bool(torch.equal(a,b))
        # A side-stream changed-input case checks the two-kernel scratch dependency.
        stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            baseline(x,weights[0],a);candidate.launch(x,weights[0],b,'split8')
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
