"""唯一一次新main真实small_linear_out M32调用；只有配置/资源，无性能结论。"""
from pathlib import Path
import hashlib,json,traceback
from ir_contract import b_sme_contract
ROWS=32
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def worker(run,model):
    run,model=Path(run),Path(model);module=original=None
    result=dict(status='started',kind='baseline_identity_only',callback_calls=0,timings=[],
        source_main='594ae2a9d17aadc4587ad54ade2b34e17f4af990',rows=ROWS,layer=0,
        performance_qualified=False,model_path_qualified=False,accuracy_qualified=False,
        limitation='仅编译路径原callback单次真实调用；没有完整Inductor/模型、候选数值门或ABBA，不证明新baseline吞吐')
    try:
        import torch,triton,dispatch_bootstrap
        from safetensors import safe_open
        torch.set_num_threads(4)
        cfg=json.loads((model/'config.json').read_bytes());assert (cfg['hidden_size'],cfg['intermediate_size'],cfg['num_hidden_layers'])==(2048,6144,42)
        props=torch.cuda.get_device_properties(0);target=triton.runtime.driver.active.get_current_target()
        assert 'BI-V150' in props.name and props.multi_processor_count==16 and target.arch==71 and target.warp_size==64
        result['device']=str(props);result['target']=str(target)
        module,callback,result['dispatch']=dispatch_bootstrap.enable_dispatch(torch,run)
        original=module.mm_kernel
        index=json.loads((model/'model.safetensors.index.json').read_bytes());name='model.layers.0.mlp.down_proj.weight'
        with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:wc=f.get_tensor(name).contiguous()
        assert tuple(wc.shape)==(2048,6144) and wc.dtype==torch.bfloat16
        g=torch.Generator().manual_seed(20261026);xc=(torch.randn((ROWS,6144),generator=g)*.125).bfloat16()
        w=wc.cuda();x=xc.cuda();out=torch.empty((ROWS,2048),device='cuda',dtype=torch.bfloat16)
        assert len({a.untyped_storage().data_ptr() for a in (x,w,out)})==3
        result['weight']=dict(name=name,bytes=wc.numel()*2,sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest(),extra_weight_bytes=0,pack=False)
        capture=dispatch_bootstrap.Capture(original);module.mm_kernel=capture
        try:
            # 唯一实际callback。库内部若cache miss调优属原机制，不另发探针调用。
            value=callback.small_linear_out(x,w,out=out);result['callback_calls']+=1
        finally:module.mm_kernel=original
        torch.cuda.synchronize();assert value is out and len(capture.records)==1
        record=capture.records[0];kernel=record.pop('kernel');result['actual_mm']=record
        md=getattr(kernel,'metadata',None);asm=getattr(kernel,'asm',{});ttgir=asm.get('ttgir','');assembly=asm.get('asm','')
        result['compiled']=dict(hash=getattr(md,'hash',None),shared=getattr(md,'shared',None),use_sme=getattr(md,'use_sme',None),
            n_regs=getattr(kernel,'n_regs',None),n_spills=getattr(kernel,'n_spills',None),async_copies=ttgir.count('async_copy_global_to_local'),
            B_SME_SSA=b_sme_contract(ttgir),asm_sme_sites=assembly.count('sl_sme_load_'))
        result['fixed_address_decision_inputs']=dict(BLOCK_M=record['config']['BLOCK_M'],BLOCK_N=record['config']['BLOCK_N'],grid=record['grid'],
            candidate_written=False,note='仅真实M32 MM身份；未预设配置或删row modulo，不证明当前16K覆盖')
        for kind,data in asm.items():
            if isinstance(data,(str,bytes)):(run/('actual-mm.'+kind)).write_bytes(data.encode() if isinstance(data,str) else data)
        oc=out.cpu();rows=[0,1,15,31];cols=[0,1,127,1023,2047]
        reference=(xc[rows].double()@wc[cols].double().T).bfloat16().double();sample=oc[rows][:,cols].double()
        result['single_call_sanity']=dict(output_finite=bool(torch.isfinite(oc).all()),sample_fp64_pass=bool(torch.allclose(sample,reference,rtol=.01,atol=.001)),
            sample_max_abs=float((sample-reference).abs().max()),input_unchanged=torch.equal(x.cpu().view(torch.uint8),xc.view(torch.uint8)),
            weight_unchanged=torch.equal(w.cpu().view(torch.uint8),wc.view(torch.uint8)),not_full_correctness_gate=True)
        assert result['single_call_sanity']['output_finite'] and result['single_call_sanity']['sample_fp64_pass']
        assert result['single_call_sanity']['input_unchanged'] and result['single_call_sanity']['weight_unchanged']
        result.update(status='baseline_probe_completed',decision='保存真实MM身份/config/IR资源，未写候选/不计时，不授官方或准确率资格')
    except BaseException:result.update(status='failed',error=traceback.format_exc())
    finally:
        if module is not None and original is not None:module.mm_kernel=original
    save(run/'result.json',result);return 0 if result['status']=='baseline_probe_completed' else 1
