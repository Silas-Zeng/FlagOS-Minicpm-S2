"""main594实际callback MM-out与固定M64地址；两臂独立caller out，唯一完整ABBA。"""
from pathlib import Path
import hashlib,json,statistics,traceback,re
from reused_helpers import timed_batch
from ir_contract import b_sme_contract
EXPECTED_CONFIG=dict(BLOCK_M=64,BLOCK_N=64,BLOCK_K=128,SPLIT_K=1,num_warps=16,num_stages=2,num_ctas=1)
EXPECTED_HASH='87fa576ed1c7527759db403f017f02d00299fdf6de6de02f32ce898893df36ed'
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def worker(run,model):
    run,model=Path(run),Path(model);module=original=None
    result=dict(status='started',cases=[],timings=[],resources=[],kind='M64_fixed_address_component',
        source_main='594ae2a9d17aadc4587ad54ade2b34e17f4af990',rows=64,layer=0,config_difference={},
        permanent_extra_weight_bytes=0,pack=False,performance_qualified=False,official_qualified=False,
        scope='原MM64/64/128 w16s2与runtime K；仅消M/N通用grid除余与A/B行列取余，caller-owned独立out',
        limitations=['仅合成M64激活/真实layer0权重；无其它M、42层/模型、105或新基线资格。',
            '只计完整MM Graph replay；两out于capture前独立分配，不含CPU allocator。',
            '实际3rcp减少、SME/资源只诊断；不凭指令数或静态shared假称occupancy或收益。'])
    try:
        import torch,triton,candidate,dispatch_bootstrap
        from safetensors import safe_open
        torch.set_num_threads(4)
        cfg=json.loads((model/'config.json').read_bytes());assert (cfg['hidden_size'],cfg['intermediate_size'],cfg['num_hidden_layers'])==(2048,6144,42)
        props=torch.cuda.get_device_properties(0);target=triton.runtime.driver.active.get_current_target()
        assert 'BI-V150' in props.name and props.multi_processor_count==16 and target.arch==71 and target.warp_size==64
        result['target']=str(target)
        module,callback,result['dispatch']=dispatch_bootstrap.enable_dispatch(torch,run);original=module.mm_kernel
        index=json.loads((model/'model.safetensors.index.json').read_bytes());name='model.layers.0.mlp.down_proj.weight'
        with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:wc=f.get_tensor(name).contiguous()
        assert tuple(wc.shape)==(2048,6144) and wc.dtype==torch.bfloat16
        w=wc.cuda();g=torch.Generator().manual_seed(20261026);xc=(torch.randn((64,6144),generator=g)*.125).bfloat16();x=xc.cuda();origin=x.clone()
        out_a=torch.empty((64,2048),device='cuda',dtype=torch.bfloat16);out_b=torch.empty_like(out_a)
        assert len({t.untyped_storage().data_ptr() for t in (x,w,out_a,out_b)})==4
        result['weight']=dict(name=name,bytes=wc.numel()*2,sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest(),extra_weight_bytes=0)
        bv=w.t();assert tuple(bv.shape)==(6144,2048) and tuple(bv.stride())==(1,6144) and bv.data_ptr()==w.data_ptr()
        result['candidate_B_view']=dict(shape=list(bv.shape),stride=list(bv.stride()),aliases_original_weight=True,
            matches_original_MM_B_view=True)
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def bits(a,b):return torch.equal(a.contiguous().view(torch.uint8),b.contiguous().view(torch.uint8))
        capture=dispatch_bootstrap.Capture(original);module.mm_kernel=capture
        try:ret=callback.small_linear_out(x,w,out=out_a)
        finally:module.mm_kernel=original
        torch.cuda.synchronize();assert ret is out_a and len(capture.records)==1
        record=capture.records[0];kernel_a=record.pop('kernel');assert record['config']==EXPECTED_CONFIG and tuple(record['grid'])==(32,1)
        assert getattr(kernel_a.metadata,'hash',None)==EXPECTED_HASH,'实际新main MM hash不符，停止而不改基线'
        result['identity']=record;result['original_hash']=EXPECTED_HASH
        def preserve(label,kernel):
            md=getattr(kernel,'metadata',None);asm=getattr(kernel,'asm',{});ttgir=asm.get('ttgir','');assembly=asm.get('asm','')
            resource=dict(arm=label,hash=getattr(md,'hash',None),shared=getattr(md,'shared',None),use_sme=getattr(md,'use_sme',None),
                n_regs=getattr(kernel,'n_regs',None),n_spills=getattr(kernel,'n_spills',None),async_copies=ttgir.count('async_copy_global_to_local'),
                B_SME_SSA=b_sme_contract(ttgir),asm_sme_sites=assembly.count('sl_sme_load_'),asm_rcp_count=assembly.count('ml_rcp_f32'),
                runtime_K_in_TTGIR=bool(re.search(r'%K:\s*i32',ttgir)),diagnostic_only=True)
            result['resources'].append(resource)
            for kind,data in asm.items():
                if isinstance(data,(str,bytes)):(run/(label+'.'+kind)).write_bytes(data.encode() if isinstance(data,str) else data)
        preserve('baseline',kernel_a)
        def baseline():
            value=callback.small_linear_out(x,w,out=out_a);assert value is out_a;return value
        def changed():return candidate.launch_into(x,w,out_b)
        def verify(label):
            case=dict(label=label,bitwise=bits(out_a,out_b),finite=bool(torch.isfinite(out_a).all() and torch.isfinite(out_b).all()),
                inputs_unchanged=bits(x,origin) and bits(w.cpu(),wc))
            result['cases'].append(case)
            if not all(case[k] for k in ('bitwise','finite','inputs_unchanged')):
                result['mismatch']=[dict(row=r,column=c,A=float(out_a[r,c]),B=float(out_b[r,c])) for r,c in (out_a!=out_b).nonzero()[:12].cpu().tolist()]
                raise AssertionError('完整逐位/有限性/输入不变失败，停止，不放宽数值门')
        for label,source in (('normal',xc),('zero',torch.zeros_like(xc)),('changed',-xc.flip(0)),('finite_extreme',xc*64)):
            x.copy_(source.cuda());origin.copy_(x);baseline();kernel=changed();torch.cuda.synchronize();verify('eager_'+label)
            if label=='normal':preserve('fixed_address',kernel);save(run/'resources-before-timing.json',result['resources'])
        rows=[0,1,7,15,31,63];cols=[0,1,63,127,511,1023,2047]
        reference=(x[rows].cpu().double()@wc[cols].double().T).bfloat16().double();arms={}
        for arm,value in (('A',out_a),('B',out_b)):
            sample=value[rows][:,cols].cpu().double();arms[arm]=dict(passed=bool(torch.allclose(sample,reference,rtol=.01,atol=.001)),max_abs=float((sample-reference).abs().max()))
        result['cases'].append(dict(label='independent_fp64',kind='independent_fp64',arms=arms,criteria='rtol=.01/atol=.001；全输出跨臂另用逐位'))
        assert all(v['passed'] for v in arms.values()),'独立FP64门失败'
        x.copy_(xc.cuda());origin.copy_(x);graphs={};stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        for arm,cb in (('A',baseline),('B',changed)):
            cb();torch.cuda.synchronize();graph=torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph,stream=stream):cb()
            graphs[arm]=graph
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
        for version in range(2):
            x.copy_((xc if version==0 else -xc.flip(0)).cuda());origin.copy_(x)
            out_a.fill_(float('nan'));out_b.fill_(float('nan'))
            for arm in 'AB':graphs[arm].replay()
            torch.cuda.synchronize();verify('changed_poisoned_graph_'+str(version))
        side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):baseline();changed()
        torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize();verify('side_stream')
        assert len(result['cases'])==8
        for arm in 'ABBA':
            for _ in range(3):graphs[arm].replay()
            pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
            result['timings'].append(dict(arm=arm,rows=64,mode='完整MM Graph replay；两caller-owned out预分配，不含CPU allocator',**timed_batch(torch,graphs[arm].replay,pair,16)))
        means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['arm']==arm) for arm in 'AB'}
        result['means']=means
        result['rng_unchanged']=bits(cpu_rng,torch.get_rng_state()) and bits(gpu_rng,torch.cuda.get_rng_state());assert result['rng_unchanged']
        result.update(status='component_positive' if means['B']<means['A'] else 'stopped_negative',
            decision='仅保留单次M64组件信号，不自动扩大权重环/其它M/模型' if means['B']<means['A'] else '完整组件不正，停止后续/模型，不扫配置')
    except BaseException:result.update(status='failed',error=traceback.format_exc())
    finally:
        if module is not None and original is not None:module.mm_kernel=original
    save(run/'result.json',result);return 0 if result['status'] in ('component_positive','stopped_negative') else 1
