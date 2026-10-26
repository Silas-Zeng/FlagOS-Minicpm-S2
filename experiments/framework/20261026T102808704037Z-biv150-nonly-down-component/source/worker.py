"""真实M64 opaque F.linear对照单一无损N128 down布局；不扫tile。"""
import hashlib
import json
from pathlib import Path
import statistics
import traceback
from reused_helpers import timed_batch
from ir_contract import b_sme_contract


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def worker(run,model):
    run,model=Path(run),Path(model)
    result=dict(status='started',identity=[],cases=[],timings=[],resources=[],weights=[],
        scope='真实layer0 down [2048,6144]，M64及尾M63；实际输出buffer按各调用捕获，只计唯一M64完整GEMM Graph replay ABBA',
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',official_qualified=False,
        layout='P[N/128,K,128]；仅BF16位重排，保留三维descriptor、加载一次',
        limitations=['组件保留原W与packed两份，各24MiB/层，不算KV容量收益。',
                    '合成M64激活、单真实layer0权重；未包含42层/Attention/KV交织，不是模型收益。',
                    '候选只用真实opaque选中配置；不符合唯一格式就停止，不自动改tile。',
                    'Graph replay不重新执行Python/allocator；Event不含每调用eager CPU输出分配或pack加载。该M来自已捕获生产Graph；组件仍不外推官方。'])
    linear_module=original_linear=None
    try:
        import torch,triton
        from safetensors import safe_open
        import candidate,dispatch_bootstrap
        torch.set_num_threads(4)
        cfg=json.loads((model/'config.json').read_bytes())
        assert (cfg['hidden_size'],cfg['intermediate_size'],cfg['num_hidden_layers'])==(2048,6144,42)
        prop=torch.cuda.get_device_properties(0)
        target=triton.runtime.driver.active.get_current_target()
        assert 'BI-V150' in prop.name and prop.multi_processor_count==16 and target.arch==71 and target.warp_size==64
        result['target']=str(target);result['config_sha256']=sha(model/'config.json')
        linear_module,result['dispatch']=dispatch_bootstrap.enable_dispatch(torch,run)
        original_linear=linear_module.linear_kernel
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        weights={}
        def bits(a,b):return torch.equal(a.contiguous().view(torch.uint8),b.contiguous().view(torch.uint8))
        def load_layer(layer):
            if layer in weights:return weights[layer]
            name=f'model.layers.{layer}.mlp.down_proj.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:
                wc=f.get_tensor(name).contiguous()
            assert tuple(wc.shape)==(2048,6144) and wc.dtype==torch.bfloat16
            pc=candidate.pack_cpu(wc)
            assert tuple(pc.shape)==(16,6144,128) and pc.is_contiguous()
            assert bits(candidate.unpack_cpu(pc),wc), '真实权重pack/unpack位级失败'
            result['weights'].append(dict(layer=layer,name=name,original_bytes=wc.numel()*2,packed_bytes=pc.numel()*2,
                original_sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest(),
                packed_sha256=hashlib.sha256(pc.view(torch.uint8).numpy().tobytes()).hexdigest(),
                pack_unpack_bitwise=True,pack_location='CPU加载一次；pack和传输成本不计暖态GEMM，非每token'))
            weights[layer]=(wc,wc.cuda(),pc.cuda())
            return weights[layer]
        wc,w,p=load_layer(0)
        w_copy=w.clone();p_copy=p.clone()
        generator=torch.Generator().manual_seed(20261026)
        xc=(torch.randn((64,6144),generator=generator,dtype=torch.float32)*.125).bfloat16()
        x=xc.cuda()
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def preserve(name,compiled,m):
            md=getattr(compiled,'metadata',None)
            text=getattr(compiled,'asm',{}).get('ttgir','')
            assembly=getattr(compiled,'asm',{}).get('asm','')
            b_contract=b_sme_contract(text)
            resource=dict(rows=m,name=name,use_sme=getattr(md,'use_sme',None),shared=getattr(md,'shared',None),n_regs=getattr(compiled,'n_regs',None),
                n_spills=getattr(compiled,'n_spills',None),async_copy_ops=text.count('async_copy_global_to_local'),
                B_dot_useSme_nonzero=b_contract['passed'],B_SME_contract=b_contract,
                asm_sme_load='sl_sme_load_' in assembly)
            result['resources'].append(resource)
            for kind,value in getattr(compiled,'asm',{}).items():
                if isinstance(value,(str,bytes)):
                    (run/f'{m}-{name}.{kind}').write_bytes(value.encode() if isinstance(value,str) else value)
            return resource
        def oracle(xx,wc,a,b,label):
            rows=[0,1,7,15,31,xx.shape[0]-1];cols=[0,1,63,127,511,1023,2047]
            reference=(xx[rows].cpu().double()@wc[cols].double().T).bfloat16().double()
            stats={}
            for arm,val in (('A',a),('B',b)):
                sample=val[rows][:,cols].cpu().double()
                stats[arm]=dict(passed=bool(torch.allclose(sample,reference,rtol=.01,atol=.001)),max_abs=float((sample-reference).abs().max()))
            result['cases'].append(dict(label=label,rows=xx.shape[0],kind='independent_fp64',criteria='固定rtol=.01/atol=.001；跨臂全输出另用零容差',arms=stats))
            torch.save(dict(reference=reference,A=a[rows][:,cols].cpu(),B=b[rows][:,cols].cpu()),run/(label+'-fp64.pt'))
            assert all(v['passed'] for v in stats.values()), '独立FP64门失败'
        configs={}
        for m in (64,):
            xx=x[:m];origin=xx.clone();holders={}
            capture=dispatch_bootstrap.Capture(original_linear)
            linear_module.linear_kernel=capture
            try:identity_out=torch.ops.biv150_stable_small_o.linear(xx,w)
            finally:linear_module.linear_kernel=original_linear
            torch.cuda.synchronize()
            assert len(capture.records)==1
            rec=capture.records[0]
            assert rec['rows']==m and tuple(identity_out.shape)==(m,2048)
            configs[m]=config=rec['config']
            assert config==candidate.CONFIG, '生产真实配置不符，停止而不改tile/格式'
            assert tuple(rec['grid'])==(16,1), '原M64 down实际grid不符'
            result['observed_graph_kernel_hash']='15ef15aa299d507601ce6980ee4bd56928142529471fbb7e63ea9470df04af6f'
            result['runtime_kernel_hash']=getattr(rec['kernel'].metadata,'hash',None)
            result['runtime_hash_matches_observed_graph']=result['runtime_kernel_hash']==result['observed_graph_kernel_hash']
            result['identity'].append({k:v for k,v in rec.items() if k!='kernel'})
            preserve('original_linear',rec['kernel'],m)
            save(run/'identity.json',result['identity'])
            def baseline():
                holders['A']=torch.ops.biv150_stable_small_o.linear(xx,w)
                return holders['A']
            def packed():
                out=torch.empty((m,2048),dtype=torch.bfloat16,device='cuda')
                ck=candidate.launch_into(xx,p,out,config)
                holders['B']=out
                return ck
            def verify(label):
                a,b=holders['A'],holders['B']
                case=dict(rows=m,label=label,bitwise=bits(a,b),finite=bool(torch.isfinite(a).all() and torch.isfinite(b).all()),
                    inputs_unchanged=bits(xx,origin) and bits(w,w_copy) and bits(p,p_copy))
                result['cases'].append(case)
                if not all(case[k] for k in ('bitwise','finite','inputs_unchanged')):
                    result['mismatch']=[dict(row=r,column=c,A=float(a[r,c]),B=float(b[r,c])) for r,c in (a!=b).nonzero()[:12].cpu().tolist()]
                    raise AssertionError('packed完整逐位/有限性/输入不变门失败；停止，不放宽或改框架')
            for label,source in (('normal',xc[:m]),('zero',torch.zeros_like(xc[:m])),('changed',-xc[:m].flip(0)),('finite_extreme',xc[:m]*64)):
                xx.copy_(source.cuda());origin.copy_(xx)
                baseline();ck=packed();torch.cuda.synchronize();verify('eager_'+label)
                if label=='normal':
                    resource=preserve('nonly_linear',ck,m)
                    save(run/'resources-before-timing.json',result['resources'])
                    result.setdefault('SME_mechanism',{})[str(m)]=dict(preserved=resource['async_copy_ops']>=2 and resource['B_dot_useSme_nonzero'] and resource['asm_sme_load'], diagnostic_only=True, note='两种B方向useSme均只诊断；保存实际B SSA关联/ASM，不把mask当生效；完整8门及尾M通过后只计唯一ABBA')
            oracle(xx,wc,holders['A'],holders['B'],str(m))
            xx.copy_(xc[:m].cuda());origin.copy_(xx)
            graphs={};refs={};stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
            for arm,callback in (('A',baseline),('B',packed)):
                callback();torch.cuda.synchronize()
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=stream):callback()
                graphs[arm]=graph;refs[arm]=holders[arm]
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
            for version in range(2):
                xx.copy_((xc[:m] if version==0 else -xc[:m].flip(0)).cuda());origin.copy_(xx)
                for arm in 'AB':refs[arm].fill_(float('nan'));graphs[arm].replay()
                torch.cuda.synchronize();verify('changed_graph_'+str(version))
            side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(side):baseline();packed()
            torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize();verify('side_stream')
            # 原BM64的尾M63：保持同一配置与K序，不增加计时组。
            tail_x=xx[:63];tail_before=tail_x.clone()
            tail_a=torch.ops.biv150_stable_small_o.linear(tail_x,w)
            tail_b=torch.empty((63,2048),dtype=torch.bfloat16,device='cuda')
            candidate.launch_into(tail_x,p,tail_b,config)
            torch.cuda.synchronize()
            tail_case=dict(rows=63,label='tail_M63',bitwise=bits(tail_a,tail_b),
                finite=bool(torch.isfinite(tail_a).all() and torch.isfinite(tail_b).all()),
                inputs_unchanged=bits(tail_x,tail_before) and bits(w,w_copy) and bits(p,p_copy))
            result['cases'].append(tail_case)
            assert all(tail_case[k] for k in ('bitwise','finite','inputs_unchanged')), '尾M63逐位/有限性/输入不变门失败'
            for arm in 'ABBA':
                for _ in range(3):graphs[arm].replay()
                pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
                result['timings'].append(dict(rows=m,arm=arm,mode='完整GEMM Graph replay；输出buffer捕获，不含eager CPU分配/加载pack',**timed_batch(torch,graphs[arm].replay,pair,16)))
            means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['rows']==m and t['arm']==arm) for arm in 'AB'}
            result.setdefault('means',{})[str(m)]=means
            if means['B']>=means['A']:
                result.update(status='stopped_negative',decision=f'M{m}完整生产对照不正，停止后续/权重环/模型')
                break
            xx.copy_(xc[:m].cuda())
        else:
            result.update(status='component_positive',decision='只保留M64单层组件信号；没有权重环/模型/官方资格，不自动后继')
        result['rng_unchanged']=bits(cpu_rng,torch.get_rng_state()) and bits(gpu_rng,torch.cuda.get_rng_state())
        assert result['rng_unchanged']
    except BaseException:
        result.update(status='failed',error=traceback.format_exc())
    finally:
        if linear_module is not None and original_linear is not None:linear_module.linear_kernel=original_linear
    save(run/'result.json',result)
    return 0 if result['status'] in ('component_positive','stopped_negative','stopped_negative_ring') else 1
