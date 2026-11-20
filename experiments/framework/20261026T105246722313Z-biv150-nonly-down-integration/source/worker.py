"""仅新增42权重GPU helper/opaque接线门；无性能、无完整Llama加载资格。"""
import hashlib,json,traceback
from pathlib import Path

def worker(run,model):
    run,model=Path(run),Path(model)
    result=dict(status='started',scope='42真实down权重：实际GPU after-loading helper与新opaque；完整模型hook链由后继官方验证',
        cases=[],official_qualified=False,performance=False,old_component_not_repeated=True)
    try:
        import torch
        from safetensors import safe_open
        import dispatch_bootstrap
        torch.set_num_threads(4)
        _,result['dispatch']=dispatch_bootstrap.enable_dispatch(torch,run)
        from vllm_fl.patches import biv150_nonly_down as module
        module._register()
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        cfg=json.loads((model/'config.json').read_bytes())
        assert (cfg['hidden_size'],cfg['intermediate_size'],cfg['num_hidden_layers'])==(2048,6144,42)
        def bits(a,b):return torch.equal(a.contiguous().view(torch.uint8),b.contiguous().view(torch.uint8))
        layers=[];cpu_samples=[];weight_ptrs=[]
        cols=[0,1,63,127,511,1023,2047]
        for i in range(42):
            name=f'model.layers.{i}.mlp.down_proj.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:
                cpu=f.get_tensor(name).contiguous()
            assert tuple(cpu.shape)==(2048,6144) and cpu.dtype==torch.bfloat16
            layer=torch.nn.Module();layer.prefix=f'model.layers.{i}.mlp.down_proj'
            layer.weight=torch.nn.Parameter(cpu.cuda(),requires_grad=False)
            original=layer.weight;ptr=layer.weight.data_ptr()
            module._after_loading(layer)
            packed=layer._biv150_nonly_down_weight
            restored=packed.cpu().permute(0,2,1).contiguous().reshape(2048,6144)
            ok=bits(cpu,restored)
            assert ok and layer.weight is original and layer.weight.data_ptr()==ptr
            assert packed.shape==(16,6144,128) and packed.is_contiguous()
            assert '_biv150_nonly_down_weight' in layer._non_persistent_buffers_set
            layers.append(layer);weight_ptrs.append(ptr);cpu_samples.append(cpu[cols].double())
            result['cases'].append(dict(layer=i,pack_roundtrip_bitwise=ok,original_weight_retained=True,nonpersistent=True))
        assert module._STATE==dict(layers=42,packed_bytes=1056964608)
        result['packed_state']=dict(module._STATE)
        generator=torch.Generator().manual_seed(20261026)
        cpu_x=(torch.randn((64,6144),generator=generator,dtype=torch.float32)*.125).bfloat16()
        x=cpu_x.cuda();initial=x.clone();rows=[0,1,7,15,31,63]
        def baseline():return [torch.ops.biv150_stable_small_o.linear(x,l.weight) for l in layers]
        def candidate():return [torch.ops.biv150_nonly_down.linear(x,l.weight,l._biv150_nonly_down_weight) for l in layers]
        a=baseline();b=candidate();torch.cuda.synchronize()
        for i in range(42):
            assert bits(a[i],b[i]) and bool(torch.isfinite(b[i]).all())
            ref=(cpu_x[rows].double()@cpu_samples[i].T).bfloat16().double()
            aa=a[i][rows][:,cols].cpu().double();bb=b[i][rows][:,cols].cpu().double()
            assert torch.allclose(aa,ref,rtol=.01,atol=.001) and torch.allclose(bb,ref,rtol=.01,atol=.001)
            result['cases'][i].update(eager_full_output_bitwise=True,FP64_passed=True,
                FP64_max_abs=max(float((aa-ref).abs().max()),float((bb-ref).abs().max())))
        stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):candidate()
        torch.cuda.synchronize()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph,stream=stream):outputs=candidate()
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
        for version in range(2):
            x.copy_((cpu_x if version==0 else -cpu_x.flip(0)).cuda())
            a=baseline()
            for out in outputs:out.fill_(float('nan'))
            graph.replay();torch.cuda.synchronize()
            assert all(bits(aa,bb) and bool(torch.isfinite(bb).all()) for aa,bb in zip(a,outputs))
            for row in result['cases']:row['graph_changed_'+str(version)+'_bitwise']=True
        # 16K旧窗口的M32路径：新opaque必须真实回原实现，不能误启M64核。
        previous=module.kernel.launch_into
        def forbidden(*args,**kwargs):raise RuntimeError('M32错误进入N-only M64实现')
        module.kernel.launch_into=forbidden
        try:
            x32=x[:32]
            aa=torch.ops.biv150_stable_small_o.linear(x32,layers[0].weight)
            bb=torch.ops.biv150_nonly_down.linear(x32,layers[0].weight,layers[0]._biv150_nonly_down_weight)
            torch.cuda.synchronize()
            assert bits(aa,bb)
        finally:module.kernel.launch_into=previous
        assert [l.weight.data_ptr() for l in layers]==weight_ptrs
        result.update(status='integration_component_pass',graph_layers=42,changed_graph_versions=2,
            M32_original_fallback_bitwise=True,original_weight_pointers_retained=True,
            no_full_model_install_chain_claim=True,no_105_inherited=True)
    except BaseException:
        result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    (run/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if result['status']=='integration_component_pass' else 1
