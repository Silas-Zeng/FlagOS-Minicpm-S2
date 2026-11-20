"""实际opaque F.linear对照单一无损BF16 packed down；固定格式、不扫tile。"""
import hashlib
import json
from pathlib import Path
import statistics
import traceback
from reused_helpers import timed_batch
from ir_contract import b_sme2_contract


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path,obj):
    Path(path).write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def worker(run,model):
    run,model=Path(run),Path(model)
    result=dict(status='started',identity=[],cases=[],timings=[],resources=[],weights=[],
        scope='真实layer0 down [2048,6144]，M2030/2048；实际输出buffer按各调用捕获，计时完整GEMM Graph replay；正才3权重环',
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',official_qualified=False,
        layout='P[N/256,K/128,256,128]；仅BF16位重排，加载一次',
        limitations=['组件保留原W与packed两份，各24MiB/层，不算KV容量收益。',
                    '合成激活、最多3真实层权重环；未包含Attention/KV交织，不是模型收益。',
                    '候选只用真实opaque选中配置；不符合唯一格式就停止，不自动改tile。',
                    'Graph replay不重新执行Python/allocator；Event不含每调用eager CPU输出分配或pack加载。该M生产可能图外，不外推官方。'])
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
        xc=(torch.randn((2048,6144),generator=generator,dtype=torch.float32)*.125).bfloat16()
        x=xc.cuda()
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def preserve(name,compiled,m):
            md=getattr(compiled,'metadata',None)
            text=getattr(compiled,'asm',{}).get('ttgir','')
            assembly=getattr(compiled,'asm',{}).get('asm','')
            b_contract=b_sme2_contract(text)
            resource=dict(rows=m,name=name,shared=getattr(md,'shared',None),n_regs=getattr(compiled,'n_regs',None),
                n_spills=getattr(compiled,'n_spills',None),async_copy_ops=text.count('async_copy_global_to_local'),
                B_dot_useSme2=b_contract['passed'],B_SME_contract=b_contract,
                asm_sme_load='sl_sme_load_' in assembly)
            result['resources'].append(resource)
            for kind,value in getattr(compiled,'asm',{}).items():
                if isinstance(value,(str,bytes)):
                    (run/f'{m}-{name}.{kind}').write_bytes(value.encode() if isinstance(value,str) else value)
            return resource
        def oracle(xx,wc,a,b,label):
            rows=[0,1,31,127,1023,xx.shape[0]-1];cols=[0,1,63,127,511,1023,2047]
            reference=(xx[rows].cpu().double()@wc[cols].double().T).bfloat16().double()
            stats={}
            for arm,val in (('A',a),('B',b)):
                sample=val[rows][:,cols].cpu().double()
                stats[arm]=dict(passed=bool(torch.allclose(sample,reference,rtol=.01,atol=.001)),max_abs=float((sample-reference).abs().max()))
            result['cases'].append(dict(label=label,rows=xx.shape[0],kind='independent_fp64',criteria='固定rtol=.01/atol=.001；跨臂全输出另用零容差',arms=stats))
            torch.save(dict(reference=reference,A=a[rows][:,cols].cpu(),B=b[rows][:,cols].cpu()),run/(label+'-fp64.pt'))
            assert all(v['passed'] for v in stats.values()), '独立FP64门失败'
        configs={}
        for m in (2030,2048):
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
                    resource=preserve('packed_linear',ck,m)
                    save(run/'resources-before-timing.json',result['resources'])
                    assert resource['async_copy_ops']>=2 and resource['B_dot_useSme2'] and resource['asm_sme_load'], '编译未保留B SME流水；停止，不用普通load替换凑过'
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
            for arm in 'ABBA':
                for _ in range(3):graphs[arm].replay()
                pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
                result['timings'].append(dict(rows=m,arm=arm,mode='完整GEMM Graph replay；输出buffer捕获，不含eager CPU分配/加载pack',**timed_batch(torch,graphs[arm].replay,pair,16)))
            means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['rows']==m and t['arm']==arm) for arm in 'AB'}
            result.setdefault('means',{})[str(m)]=means
            if means['B']>=means['A']:
                result.update(status='stopped_negative',decision=f'M{m}完整生产对照不正，停止后shape/权重环/模型')
                break
            xx.copy_(xc[:m].cuda())
        else:
            # 只在两M均正之后，最小三层真实权重环；不是42层或Attention交织。
            for layer in (20,41):load_layer(layer)
            m=2030;xx=x[:m];config=configs[m];ring={};ring_graphs={};ring_refs={}
            def ring_call(arm):
                outputs=[]
                for layer in (0,20,41):
                    cpu_weight,original,packed_weight=weights[layer]
                    if arm=='A':out=torch.ops.biv150_stable_small_o.linear(xx,original)
                    else:
                        out=torch.empty((m,2048),dtype=torch.bfloat16,device='cuda')
                        candidate.launch_into(xx,packed_weight,out,config)
                    outputs.append(out)
                ring[arm]=outputs
            ring_call('A');ring_call('B');torch.cuda.synchronize()
            for i,layer in enumerate((0,20,41)):
                assert bits(ring['A'][i],ring['B'][i]) and bool(torch.isfinite(ring['B'][i]).all())
                oracle(xx,weights[layer][0],ring['A'][i],ring['B'][i],f'ring-layer{layer}')
            for arm in 'AB':
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=stream):ring_call(arm)
                ring_graphs[arm]=graph;ring_refs[arm]=ring[arm]
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
            for arm in 'ABBA':
                for _ in range(3):ring_graphs[arm].replay()
                pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
                result['timings'].append(dict(rows=m,arm=arm,mode='三真实权重环0/20/41',**timed_batch(torch,ring_graphs[arm].replay,pair,8)))
            ring_means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['mode']=='三真实权重环0/20/41' and t['arm']==arm) for arm in 'AB'}
            result['ring_means']=ring_means
            result.update(status='component_positive' if ring_means['B']<ring_means['A'] else 'stopped_negative_ring',
                decision='只保留组件信号，未生产/官方资格；三权重环不正则停止')
        result['rng_unchanged']=bits(cpu_rng,torch.get_rng_state()) and bits(gpu_rng,torch.cuda.get_rng_state())
        assert result['rng_unchanged']
    except BaseException:
        result.update(status='failed',error=traceback.format_exc())
    finally:
        if linear_module is not None and original_linear is not None:linear_module.linear_kernel=original_linear
    save(run/'result.json',result)
    return 0 if result['status'] in ('component_positive','stopped_negative','stopped_negative_ring') else 1
