"""只验证新增生产路由与scratch生命周期，复用已测336例内核数值。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import traceback

def worker(run,model):
    result=dict(status='started',checks=[],scope='新增生产opaque路由/Graph/side-stream；不重跑336例')
    try:
        import torch
        import candidate
        from safetensors import safe_open
        torch.set_num_threads(4)
        path=Path('/workspace/experiments/minicpm-s2/code/main34942f7-prefill-stride-aa43ea2c/vllm_fl/patches/biv150_stable_small_o.py')
        assert hashlib.sha256(path.read_bytes()).hexdigest()=='c5a2dd6c69c514531fee4145621e51bd4e41c0d784f4d4e086fe48aad98104ba'
        spec=importlib.util.spec_from_file_location('original_small',path);original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)
        assert 'BI-V150' in torch.cuda.get_device_name() and torch.cuda.get_device_properties(0).multi_processor_count==16
        candidate._DOWN_SPLIT8_ENABLED=True;candidate._register()
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        gen=torch.Generator().manual_seed(20261026)
        for projection in ['mlp.down_proj','self_attn.o_proj','self_attn.qkv_proj','mlp.gate_up_proj']:
            if projection=='self_attn.qkv_proj':
                values=[]
                for p in ['q','k','v']:
                    name=f'model.layers.0.self_attn.{p}_proj.weight'
                    with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:values.append(f.get_tensor(name))
                w=torch.cat(values).contiguous().cuda()
            else:
                name=f'model.layers.0.{projection}.weight'
                with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:w=f.get_tensor(name).contiguous().cuda()
            for m in ([1,2,8,9] if projection=='mlp.down_proj' else [1,8]):
                x=(torch.randn((m,w.shape[1]),generator=gen,dtype=torch.bfloat16)*.125).cuda()
                a=original._linear(x,w);b=torch.ops.biv150_stable_small_o.linear(x,w)
                torch.cuda.synchronize()
                assert torch.isfinite(b).all() and torch.allclose(a,b,rtol=.01,atol=.001)
                split=projection=='mlp.down_proj' and m<=8
                if split:
                    s=torch.cuda.Stream();s.wait_stream(torch.cuda.current_stream())
                    with torch.cuda.stream(s):b=torch.ops.biv150_stable_small_o.linear(x,w)
                    torch.cuda.current_stream().wait_stream(s)
                    graph=torch.cuda.CUDAGraph()
                    with torch.cuda.graph(graph):out=torch.ops.biv150_stable_small_o.linear(x,w)
                    x.neg_();out.fill_(float('nan'));graph.replay();torch.cuda.synchronize()
                    a=original._linear(x,w)
                    assert torch.isfinite(out).all() and torch.allclose(a,out,rtol=.01,atol=.001)
                    # 非连续步长必须保留原PR51实现，不能进无stride内核。
                    padded=torch.empty((m,w.shape[1]+16),dtype=x.dtype,device=x.device);padded[:,:w.shape[1]].copy_(x)
                    view=padded[:,:w.shape[1]]
                    assert not view.is_contiguous() or m==1
                    p=original._linear(view,w);q=torch.ops.biv150_stable_small_o.linear(view,w)
                    assert torch.allclose(p,q,rtol=.01,atol=.001)
                result['checks'].append(dict(projection=projection,rows=m,split=split,passed=True))
        result.update(status='completed',new_routing_graph_side_stream_passed=True)
    except BaseException:
        result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    (run/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return 0 if result['status']=='completed' else 1
