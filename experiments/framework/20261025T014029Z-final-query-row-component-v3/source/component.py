"""selected-Q 四例真实 backend 数值门；导入不加载 Torch，执行必须由 owner 持卡。"""
import hashlib
import importlib
import importlib.util
import inspect
import itertools
import json
import math
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent
QUERY_SHA = '7d40d8d413537ede15a5f3e25d9d0a5ae408a3f7b0c6bd5d020917267810c746'
INDEX_SHA = '47a7108bcf8424a96651021703f8731f1866a0e2eff88a1ac647e574ccf7e61d'
NAME = 'model.layers.41.self_attn.attn'

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

def cases():
    # 顺序是原请求序；case40/case5 的长请求穿插，P 后才按物理序构造页表。
    q40=[1]*40
    q40[5],q40[23]=1010,1000
    l40=[127 if i%2 else 255 for i in range(40)]
    l40[5],l40[23]=16384,8192
    return [
        dict(name='s32-m2048',q=[1]*31+[2017],length=[127]*31+[16384],scale=1.0),
        dict(name='s40-m2048-p',q=q40,length=l40,scale=1.0),
        dict(name='s64-m2048',q=[1]*63+[1985],length=[255]*63+[16384],scale=1.0),
        dict(name='s5-m141-p',q=[1,7,1,3,129],length=[1,7,127,19,4097],scale=4.0),
    ]

def geometry(case, seed):
    """纯 CPU 几何；所有页独占，物理页置换，guard不与任何本轮写槽重合。"""
    import numpy as np
    q=np.asarray(case['q'],dtype=np.int32)
    lens=np.asarray(case['length'],dtype=np.int32)
    require(q.shape==lens.shape and len(q) in (5,32,40,64) and np.all(lens>=q) and np.all(q>0),'case长度非法')
    perm=np.concatenate((np.flatnonzero(q==1),np.flatnonzero(q!=1))).astype(np.int64)
    inverse=np.argsort(perm).astype(np.int64)
    physical_q,physical_lens=q[perm],lens[perm]
    offsets=np.array([0,*itertools.accumulate(int(x) for x in physical_q)],dtype=np.int32)
    ends=offsets[1:]-1
    counts=(physical_lens+15)//16
    total_pages=int(counts.sum())
    ids=np.random.default_rng(seed).permutation(np.arange(1,total_pages+1,dtype=np.int32))
    table=np.zeros((len(q),int(counts.max())),dtype=np.int32)
    slots=[];pages=[];cursor=0
    for row,(count,length,scheduled) in enumerate(zip(counts,physical_lens,physical_q)):
        row_pages=ids[cursor:cursor+int(count)]
        cursor+=int(count)
        table[row,:int(count)]=row_pages
        pages.append(row_pages.tolist())
        slots.extend(int(row_pages[p//16])*16+p%16 for p in range(int(length-scheduled),int(length)))
    require(len(slots)==int(q.sum())==len(set(slots)),'本轮slots不唯一')
    writes=set(slots)
    guard=set(range(16))|set(range((total_pages+1)*16,(total_pages+2)*16))
    for row,length in enumerate(physical_lens):
        for logical in (int(length-physical_q[row])-1,int(length)):
            if 0<=logical<len(pages[row])*16:
                slot=pages[row][logical//16]*16+logical%16
                if slot not in writes:guard.add(slot)
    require(not guard&writes,'guard包含本轮有效写槽')
    return dict(q=q,lens=lens,permutation=perm,inverse=inverse,physical_q=physical_q,
                physical_lens=physical_lens,offsets=offsets,ends=ends,original_indices=ends[inverse],
                table=table,pages=pages,slots=slots,guards=sorted(guard),cache_blocks=total_pages+2)

def enable_dispatch(torch, run):
    for key in ('VLLM_FL_FLAGOS_WHITELIST','VLLM_FL_FLAGOS_BLACKLIST','VLLM_FL_FLAGOS_BLACKLIST_APPEND',
                'FLAGGEMS_DB_URL','FLAGGEMS_CACHE_DIR'):
        require(not os.environ.get(key),'不同服务dispatch/cache覆盖: '+key)
    require(os.environ.get('USE_FLAGGEMS','True').lower() in ('true','1'),'FlagGems被关闭')
    import flag_gems
    flag_gems.enable(record=True,once=True,path=str(run/'flaggems-oplist.txt'))
    registrar=flag_gems.current_work_registrar
    entries=[x for x in registrar.config if x[0]=='index.Tensor']
    require(len(entries)==1 and entries[0][1] is flag_gems.index,'真实index绑定不同')
    fn=inspect.unwrap(flag_gems.index)
    path=Path(inspect.getsourcefile(fn)).resolve()
    require(sha(path)==INDEX_SHA,'实际index源不符')
    table=torch._C._dispatch_dump_table('aten::index.Tensor')
    (run/'dispatch-index.txt').write_text(table)
    require(any(x.startswith('CUDA:') and 'flag_gems/' in x.replace('\\','/') for x in table.splitlines()),'CUDA index未指向FlagGems')
    return dict(index_source_sha256=INDEX_SHA,registered=True,exclude_ops=list(registrar.get_unused_ops()))

def install_actual(torch, model, source, run):
    import vllm_fl  # 与实际插件一样先完成 Torch dtype 兼容。
    require(Path(vllm_fl.__file__).resolve().is_relative_to(source),'未导入指定526插件')
    from vllm.config import CompilationConfig,CUDAGraphMode,set_current_vllm_config
    from vllm.engine.arg_utils import EngineArgs
    kwargs=dict(model=str(model),served_model_name=['minicpm'],gpu_memory_utilization=0.85,max_model_len=131072,
                compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY))
    config=EngineArgs(**kwargs).create_engine_config()
    with set_current_vllm_config(config):
        import distributed_bootstrap
        distributed_bootstrap.initialize(config,run)
        from vllm_fl.ops.custom_ops import register_oot_ops
        register_oot_ops()
        dispatch=enable_dispatch(torch,run)
        # 直接执行固定526 runner模块尾部的 C2→C3→GQA→normalization→Q→native 原顺序。
        from vllm_fl.worker import model_runner
        # 只加载类定义/既有编译入口源码，供固定来源验证；不实例化或加载权重。
        from vllm.model_executor.models import llama
        from vllm.compilation import piecewise_backend
    from vllm_fl.patches import biv150_compute_order as p,biv150_gqa_decode as gqa,biv150_q_fragment_service as q,biv150_native_w8a8 as native
    backend=importlib.import_module('vllm.v1.attention.backends.triton_attn')
    candidate=load(HERE/'query_candidate.py','selected_query_frozen_candidate')
    require(sha(HERE/'query_candidate.py')==QUERY_SHA,'冻结selected-Q脚本变更')
    for name,pin in {**p.SOURCES,**candidate._PINS}.items():
        obj=sys.modules.get(name)
        require(obj is not None and sha(obj.__file__)==pin,'实际依赖身份不符: '+name)
    require(Path(model_runner.__file__).resolve().is_relative_to(source),'runner并非指定526')
    p._main_stack(torch)
    require(q._MANAGER is not None and q._MANAGER.active,'Q manager未实际绑定')
    require(native._LOADED,'当前14f native库未由原安装链加载')
    record=dict(server_configuration=dict(model=str(model),served_model_name=['minicpm'],gpu_memory_utilization=0.85,
                max_model_len=131072,compilation_config={'cudagraph_mode':'FULL_DECODE_ONLY'}),
                parsed=dict(dtype=str(config.model_config.dtype),max_num_seqs=config.scheduler_config.max_num_seqs,
                max_num_batched_tokens=config.scheduler_config.max_num_batched_tokens,capture_sizes=config.compilation_config.cudagraph_capture_sizes),
                actual_runner_sha256=sha(model_runner.__file__),dispatch=dispatch,native_loaded=True,native_executed=False,
                model_config_sha256=sha(model/'config.json'),torch_version=str(torch.__version__),
                cpu_threads=torch.get_num_threads(),interop_threads=torch.get_num_interop_threads(),
                source_pins={**p.SOURCES,**candidate._PINS})
    save(run/'runtime.json',record)
    return config,backend,candidate,p,gqa,q

def snapshot(gqa,q):
    return dict(gqa=gqa.stats(),q_fragment={k:v for k,v in q._MANAGER.snapshot().items()
                if k in ('selected_calls','fallback_calls','original_3d_calls','selected_compiles','fallback_compiles')})

def difference(reference,candidate):
    import numpy as np
    require(reference.shape==candidate.shape and np.isfinite(reference).all() and np.isfinite(candidate).all(),'非有限或shape不符')
    x,y=reference.astype(np.float64),candidate.astype(np.float64)
    d=x-y
    return dict(elements=int(x.size),different_elements=int(np.count_nonzero(x!=y)),max_abs=float(np.max(np.abs(d))),
        rms_abs=float(np.sqrt(np.mean(d*d))),relative_l2=float(np.linalg.norm(d)/max(np.linalg.norm(x),1e-20)),
        reference_abs_max=float(np.max(np.abs(x))),both_finite=True,exact_equal=bool(np.array_equal(reference,candidate)))

def run(run_dir, model_path, plugin_source, native_library):
    run=Path(run_dir);source=Path(plugin_source).resolve();model=Path(model_path).resolve()
    from source_identity import check
    before=check(source,native_library)
    require(os.environ.get('BIV150_NATIVE_W8A8_LIBRARY')==str(Path(native_library).resolve()),'native环境与显式身份不一致')
    import numpy as np
    import torch
    require(torch.__version__.split('+')[0]=='2.10.0','Torch版本变化')
    torch.cuda.set_device(0)
    props=torch.cuda.get_device_properties(0)
    require('BI-V150' in props.name and props.multi_processor_count==16 and props.major==7,'非BI-V150 16SM')
    config,backend,candidate,p,gqa,qmanager=install_actual(torch,model,source,run)
    from vllm.config import CUDAGraphMode
    from vllm.forward_context import ForwardContext,override_forward_context
    from vllm.v1.kv_cache_interface import FullAttentionSpec
    spec=FullAttentionSpec(block_size=16,num_kv_heads=2,head_size=128,dtype=torch.bfloat16)
    builder=backend.TritonAttentionMetadataBuilder(spec,[NAME],config,torch.device('cuda:0'))
    impl=backend.TritonAttentionImpl(num_heads=16,head_size=128,scale=128**-0.5,num_kv_heads=2,
        alibi_slopes=None,sliding_window=None,kv_cache_dtype='auto',attn_type=backend.AttentionType.DECODER)
    from vllm_fl.patches import biv150_mixed_decode as mixed
    require(mixed._builder_eligible(builder,backend,torch),'实际配置不符合当前C3条件；禁止人为改配置')
    layer=NS(layer_name=NAME,_q_scale=torch.ones((),device='cuda'),_k_scale=torch.ones((),device='cuda'),_v_scale=torch.ones((),device='cuda'))
    runner=NS(device=torch.device('cuda:0'),max_num_tokens=2048)
    buffers=candidate._QueryBuffers(runner,layer,backend)
    result=dict(completed=False,component_only=True,framework=before,query_candidate_sha256=QUERY_SHA,
        model_accuracy_claimed=False,end_to_end_gain_claimed=False,numerical_acceptance='unassessed; record differences against same-input and FP32 reference',
        cases=[],limitations=['合成BF16 Q/K/V、实际backend，无模型权重；不是模型准确率。',
            '完整M写槽逐字与有限guard核验，不保存或比较整份历史cache。',
            '两臂独立同步且包含首次编译；时间仅诊断，不计算收益。',
            '组件为同一stream，原模型pinned索引重用由已有prepare event保护。'])
    save(run/'results.json',result)
    try:
        for number,case in enumerate(cases()):
            seed=20261025+number
            geo=geometry(case,seed)
            m,s=int(sum(case['q'])),len(case['q'])
            row=dict(name=case['name'],M=m,S=s,seed=seed,q_original=case['q'],seq_lens_original=case['length'],
                permutation=geo['permutation'].tolist(),physical_q=geo['physical_q'].tolist(),
                physical_seq_lens=geo['physical_lens'].tolist(),physical_ends=geo['ends'].tolist(),
                cache_blocks=geo['cache_blocks'],cache_bytes=geo['cache_blocks']*2*16*2*128*2,
                slot_count=len(geo['slots']),guard_count=len(geo['guards']),arms=[])
            result['cases'].append(row);save(run/'results.json',result)
            torch.manual_seed(seed)
            cache=torch.randn((geo['cache_blocks'],2,16,2,128),device='cuda',dtype=torch.bfloat16)
            query=torch.randn((m,16,128),device='cuda',dtype=torch.bfloat16)*case['scale']
            key=torch.randn((m,2,128),device='cuda',dtype=torch.bfloat16)*case['scale']
            value=torch.randn((m,2,128),device='cuda',dtype=torch.bfloat16)*(2.0 if case['scale']>1 else 1.0)
            layer.kv_cache=cache
            common=NS(num_reqs=s,num_actual_tokens=m,max_query_len=int(geo['physical_q'].max()),max_seq_len=int(geo['physical_lens'].max()),
                query_start_loc_cpu=torch.from_numpy(geo['offsets']),query_start_loc=torch.tensor(geo['offsets'],device='cuda',dtype=torch.int32),
                seq_lens=torch.tensor(geo['physical_lens'],device='cuda',dtype=torch.int32),
                block_table_tensor=torch.tensor(geo['table'],device='cuda',dtype=torch.int32),
                slot_mapping=torch.tensor(geo['slots'],device='cuda',dtype=torch.int64),causal=True,mm_req_doc_ranges=None)
            metadata=builder.build(0,common)
            require(hasattr(metadata,mixed._PLAN),'实际mixed构造没有产生C3 plan')
            original_context=ForwardContext(no_compile_layers={NAME:layer},attn_metadata={NAME:metadata},slot_mapping={NAME:common.slot_mapping},cudagraph_runtime_mode=CUDAGraphMode.NONE)
            reqs=[str(i) for i in range(s)]
            runner.input_batch=NS(num_reqs=s,req_ids=reqs,req_id_to_index={r:i for i,r in enumerate(reqs)})
            scheduled=np.asarray(case['q'],dtype=np.int32)
            output=NS(total_num_scheduled_tokens=m,num_scheduled_tokens=dict(zip(reqs,map(int,scheduled))),scheduled_spec_decode_tokens={},scheduled_encoder_inputs={})
            logits_host=torch.empty(geo['original_indices'].shape,dtype=torch.int32,pin_memory=True)
            np.copyto(logits_host.numpy(),geo['original_indices'],casting='no')
            prefix=next((i for i,x in enumerate(case['q']) if x!=1),s)
            plan=p.Plan(dict(logits_cpu=logits_host),geo['permutation'],geo['inverse'],geo['physical_q'],geo['original_indices']+1,m,prefix,int((scheduled==1).sum())-prefix)
            actual_plan=None if np.array_equal(geo['permutation'],np.arange(s)) else plan
            original_indices=plan.logits_indices(runner)
            proof=candidate._cpu_plan(runner,output,scheduled,actual_plan)
            require(proof is not None,'真实CPU唯一性/P合同拒绝fixture')
            physical_ends=torch.tensor(geo['ends'],device='cuda',dtype=torch.int64)
            block_ids=common.slot_mapping//16;slot_ids=common.slot_mapping%16
            guards=torch.tensor(geo['guards'],device='cuda',dtype=torch.int64)
            def bytes_cpu(x):return x.contiguous().view(torch.uint8).cpu().numpy().tobytes()
            expected_k,expected_v=bytes_cpu(key),bytes_cpu(value)
            guard_before=bytes_cpu(cache[guards//16,:,guards%16])
            observations={}
            # 数值门一次原路、一次候选；不以冷编译耗时宣称吞吐。
            for role in ('mixed','selected_q'):
                for partial in (metadata.softmax_segm_output,metadata.softmax_segm_max,metadata.softmax_segm_expsum):partial.fill_(float('nan'))
                torch.cuda.synchronize()
                stats_before=snapshot(gqa,qmanager)
                started=time.perf_counter()
                if role=='selected_q':
                    indices=buffers.physical_indices(runner,original_indices,proof,actual_plan)
                    ctx=candidate._selected_context(original_context,buffers,proof,runner.device)
                    require(ctx is not None and not hasattr(ctx.attn_metadata[NAME],mixed._PLAN),'selected元数据资格/C3隔离失败')
                    q_input=query[indices]
                    require(tuple(q_input.shape)==(s,16,128),'selected Query行数不符')
                    require(bytes_cpu(indices)==bytes_cpu(physical_ends.to(torch.int32)),'P转物理序与独立ends不同')
                    rows=s
                else:
                    ctx=original_context;q_input=query;rows=m
                out=torch.full((rows+3,16,128),8192.,dtype=torch.bfloat16,device='cuda')
                with override_forward_context(ctx):
                    # 显式独立slots来自context，不能用被裁S的假writer。
                    impl.do_kv_cache_update(layer,key,value,cache,ctx.slot_mapping[NAME])
                    impl.forward(layer,q_input,key,value,cache,ctx.attn_metadata[NAME],out)
                finished=torch.cuda.Event();finished.record();finished.synchronize()
                wall=(time.perf_counter()-started)*1000
                stats_after=snapshot(gqa,qmanager)
                require(stats_after['gqa']['calls']-stats_before['gqa']['calls']==1,'本臂未实际命中一次当前GQA')
                if role=='mixed':
                    selected_delta=stats_after['q_fragment']['selected_calls']-stats_before['q_fragment']['selected_calls']
                    fallback_delta=stats_after['q_fragment']['fallback_calls']-stats_before['q_fragment']['fallback_calls']
                    require(selected_delta+fallback_delta==1,'基线prefill未实际经过当前Q manager')
                written_k,written_v=bytes_cpu(cache[block_ids,0,slot_ids]),bytes_cpu(cache[block_ids,1,slot_ids])
                require(written_k==expected_k and written_v==expected_v,'完整M KV写入不是逐字原输入')
                require(bytes_cpu(cache[guards//16,:,guards%16])==guard_before,'历史/未写guard变化')
                require(bool((out[rows:]==8192.).all()),'输出guard被写坏')
                selected=out[physical_ends] if role=='mixed' else out[:s]
                observations[role]=selected.float().cpu().numpy()
                require(np.isfinite(observations[role]).all(),'输出非有限')
                row['arms'].append(dict(role=role,query_rows=rows,writer_rows=m,
                    metadata_num_actual_tokens=ctx.attn_metadata[NAME].num_actual_tokens,
                    max_query_len=ctx.attn_metadata[NAME].max_query_len,
                    whole_kv_bitwise=True,guard_unchanged=True,output_guard=True,
                    k_bytes_sha256=hashlib.sha256(written_k).hexdigest(),v_bytes_sha256=hashlib.sha256(written_v).hexdigest(),
                    stats_before=stats_before,stats_after=stats_after,wall_ms_includes_cold=wall))
                save(run/'results.json',result)
                del out,selected,q_input,ctx
            row['selected_vs_mixed']=difference(observations['mixed'],observations['selected_q'])
            # 物理结果scatter至M，再按原logits_indices采样：CPU证明不改变请求顺序。
            dense=np.zeros((m,16,128),dtype=np.float32)
            dense[geo['ends']]=observations['selected_q']
            request_order=dense[geo['original_indices']]
            require(np.array_equal(request_order,observations['selected_q'][geo['inverse']]),'scatter/原采样顺序错误')
            row['request_order_preserved']=True
            # 独立 CPU FP32 参考；只取一条最长Query历史，不复制全cache或全部M注意力。
            r=int(np.argmax(geo['physical_lens']));length=int(geo['physical_lens'][r])
            page=torch.tensor(geo['pages'][r],device='cuda',dtype=torch.int64)
            keys=cache[page,0].reshape(-1,2,128)[:length].float().cpu().numpy()
            vals=cache[page,1].reshape(-1,2,128)[:length].float().cpu().numpy()
            qlast=query[int(geo['ends'][r])].float().cpu().numpy().reshape(2,8,128)
            ref=np.empty((2,8,128),dtype=np.float32)
            for group in range(2):
                scores=(qlast[group]@keys[:,group].T)*np.float32(128**-0.5)
                scores-=scores.max(axis=1,keepdims=True)
                weights=np.exp(scores)
                weights/=weights.sum(axis=1,keepdims=True,dtype=np.float32)
                ref[group]=weights@vals[:,group]
            ref=ref.reshape(16,128)
            row['fp32_reference']=dict(physical_request=r,seq_len=length,logical_query_position=length-1,
                algorithm='CPU NumPy float32 QK/max-subtracted softmax/PV, KV group8',
                mixed_error=difference(ref,observations['mixed'][r]),selected_error=difference(ref,observations['selected_q'][r]))
            save(run/'results.json',result)
            del cache,query,key,value,common,metadata,original_context,plan,actual_plan,original_indices,logits_host,physical_ends
            del block_ids,slot_ids,guards,observations,dense,request_order,page,keys,vals,qlast,ref,weights,scores
            layer.kv_cache=None
        torch.cuda.synchronize()
        result['framework_after']=check(source,native_library)
        require(result['framework_after']==before,'框架或native来源变化')
        result['q_manager_final']=qmanager._MANAGER.snapshot()
        result['completed']=True
        save(run/'results.json',result)
        return result
    finally:
        torch.cuda.synchronize()
