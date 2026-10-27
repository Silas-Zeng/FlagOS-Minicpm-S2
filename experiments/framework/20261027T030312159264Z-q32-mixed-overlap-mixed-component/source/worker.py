"""当前main241真实C3混合层：原串行与原字节93c双流；唯一形状/ABBA。"""
from pathlib import Path
from types import SimpleNamespace as NS
import importlib, statistics, traceback
from validate_hidden_row_gather import digest, write
from validate_mixed_decode import make_data
from legacy_gate import timed_batch
from overlap import MixedAttentionOverlap

D,P,L=63,1985,4096
TOTAL=D+P

def require(value,message):
    if not value: raise RuntimeError(message)

class Capture:
    def __init__(self,raw): self.raw,self.records=raw,[]
    def __getitem__(self,grid):
        def call(*args,**kwargs):
            require(not args,'实际kernel必须keyword ABI')
            compiled=self.raw[grid](**kwargs)
            self.records.append((grid,dict(kwargs),compiled))
            return compiled
        return call

def preserve(kernel,folder,qfragment):
    folder.mkdir(exist_ok=False)
    for name,value in kernel.asm.items():
        if isinstance(value,(bytes,str)):
            (folder/(name+('.txt' if isinstance(value,str) else '.bin'))).write_bytes(value.encode() if isinstance(value,str) else value)
    return qfragment._resources(kernel)

def worker(run,model,case='mixed'):
    run=Path(run)
    result=dict(status='started',shape=dict(decode=D,prefill=P,kv_len=L),timings=[],
        limitations=['一个main241真实backend合成混合层，不是官方吞吐/模型准确率。',
            '同数学/同producer+reducer；完整成本含原writer与每call fork/join/event/record_stream/collect。',
            '不是CUDA Graph性能；不强制共驻，不证明硬件并发，不自动接入服务。'])
    overlap=manager=gqa=None
    saved_wrapper=saved_gqa=saved_reduce=None
    try:
        require(case=='mixed','只运行D63/P1985/KV4K，不自动扩形状')
        import torch
        import vllm_fl
        from vllm.config import CompilationConfig,CUDAGraphMode,set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        config=EngineArgs(model=str(model),served_model_name=['minicpm'],gpu_memory_utilization=.85,
            max_model_len=131072,compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        text=config.model_config.hf_text_config
        require((text.hidden_size,text.intermediate_size,text.num_hidden_layers,text.num_attention_heads,text.num_key_value_heads)==(2048,6144,42,16,2),'固定模型结构不符')
        with set_current_vllm_config(config):
            import distributed_bootstrap
            distributed_bootstrap.initialize(config,run)
            from vllm_fl.ops.custom_ops import register_oot_ops
            from dispatch_bootstrap import enable_dispatch
            register_oot_ops();result['dispatch']=enable_dispatch(torch,run)
            importlib.import_module('vllm_fl.worker.model_runner')
            native=importlib.import_module('vllm_fl.patches.biv150_native_w8a8')
            result['native_install']=native.install()
        require(result['native_install'].get('installed'),'main241原安装链不符')
        backend=importlib.import_module('vllm.v1.attention.backends.triton_attn')
        qfragment=importlib.import_module('vllm_fl.patches.biv150_q_fragment_service')
        q32=importlib.import_module('vllm_fl.patches.biv150_prefill_q32')
        mixed=importlib.import_module('vllm_fl.patches.biv150_mixed_decode')
        gqa=importlib.import_module('vllm_fl.patches.biv150_gqa_decode')
        manager=q32._MANAGER;base=qfragment._MANAGER
        require(manager is not None and manager.active and base is not None,'main241 Q32没有自然安装')
        policy=base.holder[base.kernel_key]
        require(type(policy) is q32._Policy and policy.manager is manager and policy.base is base.wrapper and not policy.disabled,'实际Q32 Policy绑定失败')
        require(torch.cuda.device_count()==1,'只允许本站单卡')
        torch.cuda.set_device(0);props=torch.cuda.get_device_properties(0)
        require('BI-V150' in props.name and props.multi_processor_count==16,'设备不符')
        result['device']=str(props)
        torch.manual_seed(721507)
        spec=FullAttentionSpec(block_size=16,num_kv_heads=2,head_size=128,dtype=torch.bfloat16)
        builder=backend.TritonAttentionMetadataBuilder(spec,['synthetic.attn'],config,torch.device('cuda:0'))
        impl=backend.TritonAttentionImpl(num_heads=16,head_size=128,scale=128**-.5,num_kv_heads=2,
            alibi_slopes=None,sliding_window=None,kv_cache_dtype='auto',attn_type=backend.AttentionType.DECODER)
        layer=NS(_q_scale=torch.ones((),device='cuda'),_k_scale=torch.ones((),device='cuda'),_v_scale=torch.ones((),device='cuda'))
        common,q,k,v,cache=make_data(torch,[1]*D+[P],L)
        table=torch.full((D+1,8192),-1,dtype=torch.int32,device='cuda')
        table[:,:L//16].copy_(common.block_table_tensor)
        common.block_table_tensor=table
        metadata=builder.build(0,common)
        plan=getattr(metadata,mixed._PLAN,None)
        require(plan is not None and plan.prefix_tokens==D and plan.total_tokens==TOTAL,'真实C3没有自然切分')
        overlap=MixedAttentionOverlap(backend,mixed,torch,torch.device('cuda:0'))
        # 观察实际生产调用后立刻还原；计时不留observer。
        saved_wrapper=manager.wrapper;saved_gqa=gqa._gqa_decode_attention;saved_reduce=gqa._reduce_partials
        qp,gp,rp=Capture(saved_wrapper),Capture(saved_gqa),Capture(saved_reduce)
        manager.wrapper=qp;gqa._gqa_decode_attention=gp;gqa._reduce_partials=rp
        probe=torch.full_like(q,-17)
        impl.do_kv_cache_update(layer,k[:TOTAL],v[:TOTAL],cache,common.slot_mapping)
        overlap.serial(impl,layer,q,k,v,cache,metadata,probe)
        manager.wrapper=saved_wrapper;gqa._gqa_decode_attention=saved_gqa;gqa._reduce_partials=saved_reduce
        require(len(qp.records)==len(gp.records)==len(rp.records)==1,'没有捕获唯一Q32/GQA/reducer')
        qgrid,qkw,qkern=qp.records[0];ggrid,gkw,gkern=gp.records[0];rgrid,rkw,rkern=rp.records[0]
        require(tuple(qgrid)==(P//32+1,2) and qkw['query_ptr'].shape[0]==P and qkw['num_seqs']==1
            and (qkw['BLOCK_M'],qkw['BLOCK_Q'],qkw['num_warps'],qkw['num_stages'],qkw['TILE_SIZE'])==(256,32,16,1,64)
            and qkern.hash in manager.optimized and not policy.disabled,'实际没有选择原Q32/原Qhoist')
        segments=gqa._pick_segments(D,2,metadata.num_par_softmax_segments)
        require(segments==4 and tuple(ggrid)==(D,2,4) and tuple(rgrid)==(D,16),'真实D63 GQA必须自然S4，不能假用N64/S2')
        result['production_binding']=dict(q32_grid=list(qgrid),q32_hash=qkern.hash,gqa_grid=list(ggrid),gqa_hash=gkern.hash,
            reducer_grid=list(rgrid),reducer_hash=rkern.hash,segments=segments,
            q32=preserve(qkern,run/'ir-q32',qfragment),gqa=preserve(gkern,run/'ir-gqa',qfragment),reducer=preserve(rkern,run/'ir-reducer',qfragment))
        consumed=[]
        for query in (q.clone(),-q):
            a,b=torch.full_like(q,-17),torch.full_like(q,-17)
            # 不在两次换Q之间host同步；原stream立即消费整输出，检验join和scratch复用。
            impl.do_kv_cache_update(layer,k[:TOTAL],v[:TOTAL],cache,common.slot_mapping)
            overlap.serial(impl,layer,query,k,v,cache,metadata,a)
            overlap.forward(impl,layer,query,k,v,cache,metadata,b)
            consumed.append((a.clone(),b.clone()))
        cache_before=cache.clone();inputs=[x.clone() for x in (q,k,v,common.seq_lens,common.block_table_tensor,common.slot_mapping)]
        rng=(torch.get_rng_state().clone(),torch.cuda.get_rng_state().clone())
        torch.cuda.synchronize();overlap.collect_completed()
        same=lambda a,b:bool(torch.equal(a.view(torch.int16),b.view(torch.int16)))
        checks=dict(all_output_bitwise=all(same(a,b) for a,b in consumed),
            finite=all(bool(torch.isfinite(b[:TOTAL]).all()) for _,b in consumed),
            padding_untouched=all(bool((b[TOTAL:]==-17).all()) for _,b in consumed),pending_after_correctness=len(overlap.pending)==0)
        require(all(checks.values()),'两次换Q/主stream消费/位型门失败')
        dummy=torch.full_like(q,-19)
        before=overlap.selected_calls
        overlap.forward(impl,layer,q,k,v,cache,None,dummy)
        torch.cuda.synchronize()
        checks['no_plan_fallback']=overlap.selected_calls==before and overlap.fallback_calls==1
        require(checks['no_plan_fallback'],'无plan未回原serial fallback')
        aout,bout=torch.full_like(q,-17),torch.full_like(q,-17)
        def serial_call():
            impl.do_kv_cache_update(layer,k[:TOTAL],v[:TOTAL],cache,common.slot_mapping)
            return overlap.serial(impl,layer,q,k,v,cache,metadata,aout)
        def overlap_call():
            impl.do_kv_cache_update(layer,k[:TOTAL],v[:TOTAL],cache,common.slot_mapping)
            return overlap.forward(impl,layer,q,k,v,cache,metadata,bout)
        for callback in (serial_call,overlap_call):callback();callback();torch.cuda.synchronize();overlap.collect_completed()
        checks.update(cache_unchanged=same(cache,cache_before),inputs_unchanged=all(same(a,b) for a,b in zip(inputs,(q,k,v,common.seq_lens,common.block_table_tensor,common.slot_mapping))),
            rng_unchanged=bool(torch.equal(rng[0],torch.get_rng_state()) and torch.equal(rng[1],torch.cuda.get_rng_state())),warm_cross_arm_bitwise=same(aout,bout))
        require(all(checks.values()),'原writer/输入/KV/RNG门失败')
        result['checks']=checks
        pairs=[(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)) for _ in range(4)]
        for start,end in pairs:start.record();end.record()
        torch.cuda.synchronize()
        for arm,events in zip(('serial','overlap','overlap','serial'),pairs):
            row=timed_batch(torch,serial_call if arm=='serial' else overlap_call,events,32)
            row['arm']=arm;result['timings'].append(row);write(run/'results.json',result)
            overlap.collect_completed()
        result['summary']={}
        for metric in ('event','wall'):
            a=statistics.median(x[metric+'_per_call_ms'] for x in result['timings'] if x['arm']=='serial')
            b=statistics.median(x[metric+'_per_call_ms'] for x in result['timings'] if x['arm']=='overlap')
            result['summary'][metric]=dict(serial_ms=a,overlap_ms=b,fraction_saved=1-b/a)
        require(same(cache,cache_before),'计时后KV变更')
        result.update(status='component_signal_only',selected_calls=overlap.selected_calls,fallback_calls=overlap.fallback_calls,
            peak_pending_frames=overlap.peak_pending,decision='一次完整混合层；无一致净正信号即停，不自动生产')
    except BaseException:
        result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    finally:
        if manager is not None and saved_wrapper is not None:manager.wrapper=saved_wrapper
        if gqa is not None and saved_gqa is not None:gqa._gqa_decode_attention,gqa._reduce_partials=saved_gqa,saved_reduce
        if overlap is not None:
            try:
                overlap.torch.cuda.synchronize();overlap.collect_completed()
                result['pending_after_sync']=len(overlap.pending)
                require(not overlap.pending,'同步后仍有pending帧')
            except BaseException:result.update(status='failed',shutdown_error=traceback.format_exc())
        write(run/'results.json',result)
    return 0 if result['status']=='component_signal_only' else 1
