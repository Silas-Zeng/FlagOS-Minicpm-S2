"""真实layer0 edge BF16：生产opaque linear＋原SiLU，对照两阶段partial fusion。"""
import hashlib
import inspect
import json
from pathlib import Path
import sqlite3
import statistics
import traceback

from reused_helpers import timed_batch


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n', encoding='utf-8')


def db_rows(path, m):
    c = sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro', uri=True)
    c.execute('PRAGMA query_only=ON')
    c.row_factory = sqlite3.Row
    result = {}
    try:
        tables = [r[0] for r in c.execute("SELECT name FROM sqlite_schema WHERE type='table'")]
        for table in tables:
            if not table.startswith('linear_kernel_') or 'benchmark' in table:
                continue
            quoted = '"'+table.replace('"','""')+'"'
            result[table] = [dict(r) for r in c.execute('SELECT * FROM '+quoted+
                ' WHERE key_0=? AND key_1=12288 AND key_2=2048', (((m+31)//32)*32,))]
        return result
    finally:
        c.close()


def worker(run, model):
    run, model = Path(run), Path(model)
    result = dict(status='started', cases=[], timings=[], resources=[], identity=[],
        scope='仅layer0实际edge BF16 gate/up，M2030/2048；原生产opaque F.linear＋当前服务实际SiLU，完整两launch对两launch',
        base_commit='6971ef48615af97a1637405c71f96dd89969563e', official_qualified=False,
        limitations=['合成激活、单层，不是8层工作集或官方模型成绩。',
                    '当前服务实际SiLU源码/heuristic原样重编；不声称重用同一机器码或原服务XBLOCK。',
                    '必须原生产linear身份/config门通过，不能使用手工mm替代。'])
    linear_module = original_linear = None
    try:
        import torch, triton
        from safetensors import safe_open
        from torch._C import _cuda_getCurrentRawStream as get_stream
        import candidate
        import baseline_kernel
        import dispatch_bootstrap
        torch.set_num_threads(4)
        config = json.loads((model/'config.json').read_bytes())
        assert (config['hidden_size'], config['intermediate_size'], config['num_hidden_layers']) == (2048,6144,42)
        props = torch.cuda.get_device_properties(0)
        target = triton.runtime.driver.active.get_current_target()
        assert 'BI-V150' in props.name and props.multi_processor_count == 16 and target.arch == 71 and target.warp_size == 64
        result['target'] = str(target)
        result['config_sha256'] = sha(model/'config.json')
        linear_module, result['dispatch'] = dispatch_bootstrap.enable_dispatch(torch, run)
        original_linear = linear_module.linear_kernel
        index = json.loads((model/'model.safetensors.index.json').read_bytes())
        parts, identities = [], []
        for projection in ('gate_proj','up_proj'):
            name = f'model.layers.0.mlp.{projection}.weight'
            with safe_open(str(model/index['weight_map'][name]), framework='pt', device='cpu') as f:
                part = f.get_tensor(name).contiguous()
            assert tuple(part.shape) == (6144,2048) and part.dtype == torch.bfloat16
            identities.append(dict(name=name, sha256=hashlib.sha256(part.view(torch.uint8).numpy().tobytes()).hexdigest()))
            parts.append(part)
        wc = torch.cat(parts).contiguous()
        w = wc.cuda()
        w_original = w.clone()
        result['weights'] = identities
        gen = torch.Generator().manual_seed(20261026)
        xc = (torch.randn((2048,2048), generator=gen, dtype=torch.float32)*.125).bfloat16()
        x = xc.cuda()
        cpu_rng = torch.get_rng_state().clone()
        gpu_rng = torch.cuda.get_rng_state().clone()
        silu = baseline_kernel.triton_poi_fused_linear_mul_silu_slice_1
        result['current_service_silu_sha256']='52c1984c9afd4b2bf748fece3b876cab05b74c493eab14605aab2b6777fc1bf3'

        def bits(a,b):
            return torch.equal(a.contiguous().view(torch.uint8), b.contiguous().view(torch.uint8))

        def preserve(name, compiled, m):
            md = getattr(compiled, 'metadata', None)
            result['resources'].append(dict(rows=m, name=name, shared=getattr(md,'shared',None),
                n_regs=getattr(compiled,'n_regs',None), n_spills=getattr(compiled,'n_spills',None)))
            for kind, text in getattr(compiled,'asm',{}).items():
                if isinstance(text, (str,bytes)):
                    (run/f'{m}-{name}.{kind}').write_bytes(text.encode() if isinstance(text,str) else text)

        for m in (2030,2048):
            xx = x[:m]
            origin_x = xx.clone()
            # 真实opaque调用的LibEntry旁路只做身份观测，不替代调用路径。
            capture = dispatch_bootstrap.Capture(original_linear)
            linear_module.linear_kernel = capture
            try:
                identity_raw = torch.ops.biv150_stable_small_o.linear(xx,w)
            finally:
                linear_module.linear_kernel = original_linear
            torch.cuda.synchronize()
            assert len(capture.records) == 1, '原opaque没有唯一真实linear launch'
            rec = capture.records[0]
            assert rec['rows'] == m and tuple(identity_raw.shape) == (m,12288)
            actual_config = rec['config']
            preserve('original_linear', rec['kernel'],m)
            result['identity'].append({k:v for k,v in rec.items() if k != 'kernel'})
            result['identity'][-1]['db_rows_after_real_opaque'] = db_rows(run/'database-original.sqlite',m)
            result['identity'][-1]['current_db_rows'] = db_rows('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db',m)
            save(run/'identity.json', result['identity'])
            holders = {}

            def baseline():
                raw = torch.ops.biv150_stable_small_o.linear(xx,w)
                out = torch.empty((m,6144), dtype=torch.bfloat16, device='cuda')
                silu.run(raw,out,m*6144,stream=get_stream(0))
                holders['A'] = (raw,out)
                return raw,out

            def fused():
                gate = torch.empty((m,6144), dtype=torch.bfloat16, device='cuda')
                out = torch.empty_like(gate)
                candidate.launch_into(xx,w,gate,out,actual_config)
                holders['B'] = (gate,out)
                return gate,out

            def verify(label):
                raw,a = holders['A'];gate,b = holders['B']
                eq = bits(a,b)
                case = dict(rows=m,label=label,output_bitwise=eq,gate_bitwise=bits(raw[:,:6144],gate),
                    finite=bool(torch.isfinite(a).all() and torch.isfinite(b).all() and torch.isfinite(raw).all() and torch.isfinite(gate).all()),
                    inputs_unchanged=bits(xx,origin_x) and bits(w,w_original))
                result['cases'].append(case)
                if not all(case[k] for k in ('output_bitwise','gate_bitwise','finite','inputs_unchanged')):
                    coords=(a!=b).nonzero()[:12].cpu().tolist()
                    result['mismatch']=[dict(row=r,column=c,baseline=float(a[r,c]),candidate=float(b[r,c]),
                        baseline_gate=float(raw[r,c]),candidate_gate=float(gate[r,c]),baseline_up=float(raw[r,c+6144])) for r,c in coords]
                    result['decision']='逐位/有限性/不变性失败，立即停止，无性能计时；不改原框架或容差'
                    raise AssertionError('完整partial gate数值门失败')

            for label, source in (('normal',xc[:m]), ('zero',torch.zeros_like(xc[:m])),
                                   ('changed',-xc[:m].flip(0)), ('finite_extreme',xc[:m]*64)):
                xx.copy_(source.cuda());origin_x.copy_(xx)
                baseline()
                fused();torch.cuda.synchronize();verify('eager_'+label)
            # 独立FP64：只在CPU做dot；显式投影BF16 round后计算SiLU乘up。
            rows=[0,1,31,127,1023,m-1];cols=[0,1,63,127,1023,3071,6143]
            actual_x=xx[rows].cpu().double()
            projection=(actual_x@wc[cols+[c+6144 for c in cols]].double().T).bfloat16().double()
            gate64,up64=projection[:,:len(cols)],projection[:,len(cols):]
            expected=(gate64*torch.sigmoid(gate64)*up64).bfloat16().double()
            raw,a=holders['A'];gate,b=holders['B']
            samples={name:val[rows][:,cols].cpu().double() for name,val in (('A',a),('B',b),('gate',gate))}
            fp64={name:dict(passed=bool(torch.allclose(v,gate64 if name=='gate' else expected,rtol=.01,atol=.001)),
                max_abs=float((v-(gate64 if name=='gate' else expected)).abs().max())) for name,v in samples.items()}
            result['cases'].append(dict(rows=m,label='independent_fp64',criteria='固定rtol=.01/atol=.001；逐位跨臂门独立且零容差',arms=fp64))
            torch.save(dict(reference=expected,gate_projection=gate64,up_projection=up64,samples=samples),run/f'{m}-fp64-sample.pt')
            assert all(v['passed'] for v in fp64.values()), '独立FP64样本门失败'
            xx.copy_(xc[:m].cuda());origin_x.copy_(xx)
            graphs={};graph_refs={};stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
            for arm, callback in (('A',baseline),('B',fused)):
                callback();torch.cuda.synchronize()
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=stream):refs=callback()
                graphs[arm]=graph;graph_refs[arm]=refs
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
            for version in range(2):
                xx.copy_((xc[:m] if version==0 else -xc[:m].flip(0)).cuda());origin_x.copy_(xx)
                for arm in 'AB':
                    graph_refs[arm][1].fill_(float('nan'))
                    graphs[arm].replay()
                torch.cuda.synchronize();verify('changed_graph_'+str(version))
            side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(side):baseline();fused()
            torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize();verify('side_stream')
            # 保存两种候选编译产物，调用身份与数学相同的私有JIT只为取返回kernel，不计时。
            gate,out=holders['B']
            bm,bn,bk=(actual_config[k] for k in ('BLOCK_M','BLOCK_N','BLOCK_K'))
            for phase in (False,True):
                ck=candidate.half_mm[(triton.cdiv(m,bm)*triton.cdiv(6144,bn),)](xx,w,gate,out,M=m,FUSE_UP=phase,
                    BM=bm,BN=bn,BK=bk,num_warps=actual_config['num_warps'],num_stages=actual_config['num_stages'],
                    num_ctas=actual_config['num_ctas'],enable_fp_fusion=True)
                preserve('partial_up' if phase else 'partial_gate',ck,m)
            torch.cuda.synchronize()
            for arm in 'ABBA':
                for _ in range(3):graphs[arm].replay()
                pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
                result['timings'].append(dict(rows=m,arm=arm,mode='CUDA Graph完整两launch与对应分配捕获',
                    **timed_batch(torch,graphs[arm].replay,pair,16)))
            means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['rows']==m and t['arm']==arm) for arm in 'AB'}
            result.setdefault('means',{})[str(m)]=means
            if means['B']>=means['A']:
                result.update(status='stopped_negative',decision=f'M{m}完整Graph链不优于生产基线，停止后续shape/工作集',rng_unchanged=bits(cpu_rng,torch.get_rng_state()) and bits(gpu_rng,torch.cuda.get_rng_state()))
                break
            xx.copy_(xc[:m].cuda())
        else:
            result.update(status='completed_positive_component_only',decision='仅单层两M正，仍未8层工作集/生产/官方资格')
        result['rng_unchanged']=bits(cpu_rng,torch.get_rng_state()) and bits(gpu_rng,torch.cuda.get_rng_state())
        assert result['rng_unchanged']
        result['silu_launchers']=[str(getattr(f,'config',None)) for f in (getattr(silu,'launchers',None) or [])]
    except BaseException:
        result.update(status='failed',error=traceback.format_exc())
    finally:
        if linear_module is not None and original_linear is not None:
            linear_module.linear_kernel=original_linear
    save(run/'result.json',result)
    return 0 if result['status'] in ('completed_positive_component_only','stopped_negative') else 1
