"""真实layer0 QKV GEMM＋原526 RoPE combo 对比 head内融合；仅组件。"""
import hashlib
import importlib
import importlib.util
import inspect
import json
from pathlib import Path
import statistics
import struct
import traceback
import types

from reused_helpers import timed_batch

HERE=Path(__file__).resolve().parent
GUARD=64


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def save(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]


def worker(run,model):
    run,model=Path(run),Path(model)
    result=dict(status='started',cases=[],timings=[],resources=[],
        base_commit='6971ef48615af97a1637405c71f96dd89969563e',
        scope='仅layer0实际QKV拼接权重，M2030/2048，完整原GEMM＋原native RoPE combo；不含双方共同KVwriter',
        limitations=['合成激活，原安装API构造表而非live模型cache抓取。',
            '仅单层组件，未复现42层算子交织，不能外推模型收益。',
            '原RoPE heuristic重新编译热身，不宣称复用原服务机器码或原XBLOCK。',
            '没有生产adapter或官方准确率/性能资格。'])
    try:
        import torch,triton
        import triton.language as tl
        import candidate
        import baseline_kernel
        from safetensors import safe_open
        from torch._C import _cuda_getCurrentRawStream as get_stream
        torch.set_num_threads(4)
        config=json.loads((model/'config.json').read_bytes())
        assert (config['hidden_size'],config['num_attention_heads'],config['num_key_value_heads'],
            config['head_dim'],config['rope_theta'],config['max_position_embeddings'])==(2048,16,2,128,5000000,131072)
        assert config.get('rope_scaling') is None
        result['config_sha256']=sha(model/'config.json')
        module=importlib.import_module('flag_gems.runtime.backend._iluvatar.ops.mm')
        mm_path=Path(inspect.getsourcefile(module.mm))
        assert sha(mm_path)=='4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090'
        jit=module.mm_kernel
        while not isinstance(jit,triton.runtime.JITFunction):jit=jit.fn
        (run/'source/installed-mm.py').write_bytes(mm_path.read_bytes())
        rotary=importlib.import_module('vllm.model_executor.layers.rotary_embedding.base')
        assert sha(rotary.__file__)=='c81804498f08f072356a26b41967f211475df2694dabf5da9f488c074d1fdef5'
        (run/'source/installed-rotary-base.py').write_bytes(Path(rotary.__file__).read_bytes())
        props=torch.cuda.get_device_properties(0)
        target=triton.runtime.driver.active.get_current_target()
        assert 'BI-V150' in props.name and props.multi_processor_count==16 and target.arch==71 and target.warp_size==64
        result['target']=str(target)
        # 使用已安装原API本体，未自写sin/cos。只构造其所读的静态属性。
        holder=types.SimpleNamespace(base=config['rope_theta'],rotary_dim=128,max_position_embeddings=131072)
        cls=rotary.RotaryEmbeddingBase
        holder._compute_inv_freq=types.MethodType(cls._compute_inv_freq,holder)
        with torch.device('cuda'):
            table=cls._compute_cos_sin_cache(holder).to(torch.bfloat16).contiguous()
        assert tuple(table.shape)==(131072,128) and table.stride()==(128,1)
        table_cpu=table.cpu();table_original=table.clone()
        result['table']=dict(api='installed RotaryEmbeddingBase._compute_cos_sin_cache',
            source_sha256=sha(rotary.__file__),device_context='cuda',dtype=str(table.dtype),
            shape=list(table.shape),stride=list(table.stride()),live_model_capture=False,
            sha256=hashlib.sha256(table_cpu.view(torch.uint8).numpy().tobytes()).hexdigest())
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        parts=[];identities=[]
        for projection,n in (('q_proj',2048),('k_proj',256),('v_proj',256)):
            name=f'model.layers.0.self_attn.{projection}.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:part=f.get_tensor(name).contiguous()
            assert tuple(part.shape)==(n,2048) and part.dtype==torch.bfloat16
            identities.append(dict(name=name,sha256=hashlib.sha256(part.view(torch.uint8).numpy().tobytes()).hexdigest()))
            parts.append(part)
        wc=torch.cat(parts).contiguous();w=wc.cuda();w_original=w.clone()
        result['weights']=identities
        generator=torch.Generator().manual_seed(20261026)
        xc=(torch.randn((2048,2048),generator=generator,dtype=torch.float32)*.125).bfloat16()
        x=xc.cuda();cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        rope=baseline_kernel.triton_poi_fused_1
        def bits(a,b):return torch.equal(a.contiguous().view(torch.uint8),b.contiguous().view(torch.uint8))
        def guarded(shape):
            count=1
            for size in shape:count*=size
            storage=torch.full((count+2*GUARD,),-7.,dtype=torch.bfloat16,device='cuda')
            return storage,storage[GUARD:-GUARD].view(shape)
        def check_guard(storage):
            return bool((storage[:GUARD]==-7).all() and (storage[-GUARD:]==-7).all())
        def record_kernel(name,kernel,m):
            md=getattr(kernel,'metadata',None)
            result['resources'].append(dict(rows=m,name=name,shared=getattr(md,'shared',None),
                n_regs=getattr(kernel,'n_regs',None),n_spills=getattr(kernel,'n_spills',None)))
            for kind in ('ttgir','llir','asm','ptx'):
                text=getattr(kernel,'asm',{}).get(kind)
                if isinstance(text,str):(run/f'{m}-{name}.{kind}').write_text(text,encoding='utf-8')
        def mm(xx,out):
            return jit[(triton.cdiv(xx.shape[0],256)*20,1)](xx,w.T,out,xx.shape[0],2560,2048,
                2048,1,1,2048,2560,1,acc_dtype=tl.float32,input_precision=None,
                fp8_fast_accum=True,AB_DTYPE=tl.bfloat16,BLOCK_M=256,BLOCK_N=128,BLOCK_K=32,
                GROUP_M=8,SPLIT_K=1,EVEN_K=True,UPGRADE=False,UPGRADE_A_OFFS=False,
                UPGRADE_B_OFFS=False,UPGRADE_C_OFFS=False,num_warps=8,num_stages=2)
        for m in (2030,2048):
            xx=x[:m];original_x=xx.clone()
            raw_storage,raw=guarded((m,2560))
            aqs,aq=guarded((m,2048));aks,ak=guarded((m,256))
            bqs,bq=guarded((m,2048));bks,bk=guarded((m,256))
            bvs,bv_whole=guarded((m,2560));bv=bv_whole[:,:256]
            positions=torch.arange(m,device='cuda',dtype=torch.int64)
            def baseline():
                compiled=mm(xx,raw)
                rope.run(raw,positions,table,ak,aq,m*256,m*2048,stream=get_stream(0))
                return compiled
            def fused():return candidate.launch_into(xx,w,positions,table,bq,bk,bv)
            def verify(label):
                equal=bits(aq,bq) and bits(ak,bk) and bits(raw[:,2304:],bv)
                case=dict(rows=m,label=label,q_bitwise=bits(aq,bq),k_bitwise=bits(ak,bk),
                    v_bitwise=bits(raw[:,2304:],bv),finite=bool(torch.isfinite(bq).all() and torch.isfinite(bk).all() and torch.isfinite(bv).all()))
                result['cases'].append(case)
                if not equal:
                    mismatch=[]
                    for name,aa,bb,base_col in (('q',aq,bq,0),('k',ak,bk,2048),('v',raw[:,2304:],bv,2304)):
                        indices=(aa!=bb).nonzero()[:12].cpu().tolist()
                        for row,col in indices:
                            item=dict(output=name,row=row,column=col,baseline=float(aa[row,col]),candidate=float(bb[row,col]))
                            if name!='v':
                                local=col%128;partner=base_col+(col//128)*128+(local+64)%128
                                a=float(raw[row,base_col+col]);b=float(raw[row,partner])
                                pos=int(positions[row]);pos=pos+131072 if pos<0 else pos
                                c=float(table_cpu[pos,local%64]);s=float(table_cpu[pos,64+local%64])
                                sign=-1 if local<64 else 1
                                item['fp32_diagnostic']=dict(projected_bf16=a,partner_bf16=b,cos=c,sin=s,
                                    separate=f32(f32(a*c)+sign*f32(b*s)),
                                    fuse_direct_approx=f32(a*c+sign*f32(b*s)),
                                    fuse_crossed_approx=f32(f32(a*c)+sign*b*s),
                                    note='FP64模拟单FMA仅诊断，不证明源投影或原机器码的真实融合顺序')
                            mismatch.append(item)
                    result['mismatch_diagnostic']=mismatch
                    result['decision']='完整跨臂不逐位，停止计时；先读原/新IR确认GEMM/舍入/FMA，不放宽门凑过'
                    raise AssertionError('QKV+RoPE完整跨臂逐位门失败')
                assert case['finite'] and all(check_guard(s) for s in (raw_storage,aqs,aks,bqs,bks,bvs))
                assert bool((bv_whole[:,256:]==-7).all()), 'V stride洞被写入'
                assert bits(xx,original_x) and bits(w,w_original) and bits(table,table_original)
            for variant in ('prefill','long_nonmonotonic','repeated_boundary'):
                if variant=='prefill':pc=torch.arange(m,dtype=torch.int64)
                elif variant=='long_nonmonotonic':pc=(torch.arange(m,dtype=torch.int64)*61+16384)%131072
                else:pc=torch.tensor([0,1,4095,16383,16653,131071,-1]*((m+6)//7),dtype=torch.int64)[:m]
                positions.copy_(pc.cuda())
                record_kernel('original_mm',baseline(),m)
                record_kernel('qkv_rope',fused(),m)
                torch.cuda.synchronize();verify('eager_'+variant)
            # 独立FP64抽样：先投影舍入BF16，再旋转；不是将未舍入FP64直接旋转。
            rows=[0,1,31,127,1023,m-1];cols=[0,63,64,127,1023,2047,2048,2303,2304,2559]
            needed=sorted(set(cols+[c//128*128+(c%128+64)%128 for c in cols if c<2304]))
            projected=(xx[rows].cpu().double()@wc[needed].double().T).to(torch.bfloat16).double()
            lookup={c:i for i,c in enumerate(needed)};expected=[]
            for row_idx,row in enumerate(rows):
                p=int(pc[row]);p=p+131072 if p<0 else p;values=[]
                for c in cols:
                    value=projected[row_idx,lookup[c]]
                    if c<2304:
                        other=projected[row_idx,lookup[c//128*128+(c%128+64)%128]]
                        value=value*table_cpu[p,c%64].double()+(-1 if c%128<64 else 1)*other*table_cpu[p,64+c%64].double()
                    values.append(float(value))
                expected.append(values)
            reference=torch.tensor(expected,dtype=torch.float64).bfloat16().double()
            actual=torch.stack([bq[r,c] if c<2048 else bk[r,c-2048] if c<2304 else bv[r,c-2304] for r in rows for c in cols]).cpu().double().reshape(len(rows),len(cols))
            fp64_pass=bool(torch.allclose(actual,reference,rtol=.01,atol=.001))
            result['cases'].append(dict(rows=m,label='independent_fp64_sample',passed=fp64_pass,max_abs=float((actual-reference).abs().max())))
            assert fp64_pass
            graphs={};stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
            for arm,callback in (('A',baseline),('B',fused)):
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=stream):callback()
                graphs[arm]=graph
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
            for version in range(2):
                xx.copy_((xc[:m] if version==0 else -xc[:m].flip(0)).cuda());original_x.copy_(xx)
                positions.copy_(((torch.arange(m,dtype=torch.int64)*(37+version)+8192)%131072).cuda())
                aq.fill_(float('nan'));ak.fill_(float('nan'));bq.fill_(float('nan'));bk.fill_(float('nan'));bv.fill_(float('nan'))
                for graph in graphs.values():graph.replay()
                torch.cuda.synchronize();verify('changed_graph_'+str(version))
            side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(side):baseline();fused()
            torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize();verify('side_stream')
            for arm in 'ABBA':
                for _ in range(3):graphs[arm].replay()
                pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
                entry=timed_batch(torch,graphs[arm].replay,pair,16)
                result['timings'].append(dict(rows=m,arm=arm,**entry))
            result['means']= {str(mm_):{arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['rows']==mm_ and t['arm']==arm) for arm in 'AB'} for mm_ in (2030,2048) if any(t['rows']==mm_ for t in result['timings'])}
            xx.copy_(xc[:m].cuda())
        result['rope_launchers']=[dict(config=str(getattr(f,'config',None)),n_regs=str(getattr(f,'n_regs',None)),n_spills=str(getattr(f,'n_spills',None))) for f in (getattr(rope,'launchers',None) or [])]
        assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        result.update(status='completed',rng_unchanged=True,official_qualified=False)
    except BaseException:
        result.update(status='failed',error=traceback.format_exc())
    save(run/'result.json',result)
    return 0 if result['status']=='completed' else 1
