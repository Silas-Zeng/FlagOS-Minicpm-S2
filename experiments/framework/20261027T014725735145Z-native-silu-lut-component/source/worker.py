"""M2048真实中间层：实际14f完整native gate 对只替尾部的私有LUT。"""
from pathlib import Path
import ast,hashlib,json,statistics,traceback
from reused_helpers import timed_batch
HERE=Path(__file__).resolve().parent
SO=Path('/workspace/experiments/minicpm-s2/official/20261026T184110Z-main241-control-16k-four-rounds-control/native/biv150_native_w8a8.so')
SO_SHA='14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
def save(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def worker(run,model):
    run,model=Path(run),Path(model);result=dict(status='started',scope='M2048/layer20真实权重，合成激活，仅完整gate单组ABBA',cases=[],timings=[],permanent_table_bytes=262144,official_qualified=False)
    try:
        import numpy as np,torch
        from safetensors import safe_open
        from torch.utils.cpp_extension import load
        torch.set_num_threads(4);prop=torch.cuda.get_device_properties(0)
        assert 'BI-V150' in prop.name and prop.multi_processor_count==16
        assert hashlib.sha256(SO.read_bytes()).hexdigest()==SO_SHA
        torch.ops.load_library(str(SO));result['baseline_library_sha256']=SO_SHA
        import flag_gems
        flag_gems.enable(record=True,once=True,path=str(run/'flaggems-oplist.txt'))
        (run/'int-mm-dispatch.txt').write_text(torch._C._dispatch_dump_table('aten::_int_mm'))
        build=run/'build';build.mkdir()
        library=load(name='biv150_silu_lut_component',sources=[str(HERE/'native_w8a8.cpp'),str(HERE/'native_w8a8.cu')],build_directory=str(build),extra_cflags=['-O3'],extra_cuda_cflags=['-O3','-x','ivcore'],is_python_module=False,verbose=True)
        result['candidate_library']=dict(path=str(library),sha256=hashlib.sha256(Path(library).read_bytes()).hexdigest(),torch=torch.__version__,cxx11_abi=bool(torch._C._GLIBCXX_USE_CXX11_ABI),flags=['-O3','-x','ivcore'])
        op=torch.ops.biv150_silu_lut_component
        table=op.make_lut(torch.empty((),device='cuda'));torch.cuda.synchronize();table_before=table.cpu().view(torch.uint8).clone()
        result['table']=dict(bytes=table.numel()*table.element_size(),sha256=hashlib.sha256(table_before.numpy().tobytes()).hexdigest(),initialization='当前device/同expf表达式，一次构造，不在计时内；生产若接线须在KV sizing前诚实计入')
        ups=torch.tensor([0.,-0.,1.,-1.,.5,-.5,2.,-2.,2.**-126,-2.**-126,2.**100,-2.**100],device='cuda',dtype=torch.float32)
        da,db=op.domain(table,ups);a=da.cpu().view(torch.uint16).numpy();b=db.cpu().view(torch.uint16).numpy()
        finite=(np.arange(65536,dtype=np.uint32)&0x7f80)!=0x7f80
        domain_equal=bool(np.array_equal(a[:,finite],b[:,finite]));result['finite_domain']=dict(bitwise=domain_equal,finite_gate_patterns=int(finite.sum()),up_patterns=ups.numel(),nonfinite_gate_patterns_diagnostic_only=True)
        assert domain_equal,'完整有限BF16 gate域出现差异，不放宽/改数学'
        del da,db,a,b
        index=json.loads((model/'model.safetensors.index.json').read_bytes());parts=[];identities=[]
        for p in ('gate_proj','up_proj'):
            name='model.layers.20.mlp.'+p+'.weight'
            with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as f:value=f.get_tensor(name).contiguous()
            assert tuple(value.shape)==(6144,2048) and value.dtype==torch.bfloat16
            parts.append(value);identities.append(dict(name=name,sha256=hashlib.sha256(value.view(torch.uint8).numpy().tobytes()).hexdigest()))
        weights=torch.cat(parts).cuda();py=ast.parse((HERE/'production-native.py').read_bytes());quant=next(n for n in py.body if isinstance(n,ast.FunctionDef) and n.name=='quantize_weight');scope={'torch':torch}
        exec(compile(ast.Module(body=[quant],type_ignores=[]),'actual-production-weight-quantizer','exec'),scope)
        wq,scales=scope['quantize_weight'](weights);del weights,parts
        result['weights']=identities;g=torch.Generator().manual_seed(20261027);xc=(torch.randn((2048,2048),generator=g)*.125).bfloat16();x=xc.cuda()
        marker=torch.zeros((),device='cuda',dtype=torch.bfloat16).expand(12288,2048)
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        def equal(label,a,b):
            ac=a.cpu().view(torch.uint8);bc=b.cpu().view(torch.uint8)
            good=torch.equal(ac,bc);finite=bool(torch.isfinite(a).all() and torch.isfinite(b).all())
            result['cases'].append(dict(label=label,bitwise=good,finite=finite));save(run/'result.json',result)
            assert good and finite,'真实完整gate逐位/finite失败，停止'
        callbacks={'A':lambda:torch.ops.biv150_native.gate_silu_auto(x,wq,scales,marker,17),'B':lambda:op.gate_lut(x,wq,scales,marker,table)}
        for label,source in [('normal',xc),('zero',torch.zeros_like(xc)),('changed',-xc.flip(0)),('finite_extreme',xc*64)]:
            x.copy_(source.cuda());equal(label,callbacks['A'](),callbacks['B']())
        # Independent integer samples for the same current input/production quantizer.
        aq,sa=torch.ops.biv150_native.quantize_rows_probe(x,256);acc=torch._int_mm(aq,wq)
        rr=[0,1,31,1023,2047];cc=[0,1,6143,6144,12287]
        qc=aq.cpu().numpy()[rr].astype(np.int64);wc=wq.cpu().numpy()[:,cc].astype(np.int64)
        ref=qc@wc;actual=acc.cpu().numpy()[np.ix_(rr,cc)]
        result['independent_INT64']=dict(passed=bool(np.array_equal(ref,actual)),rows=rr,cols=cc);assert result['independent_INT64']['passed']
        del aq,sa,acc,qc,wc,ref,actual
        x.copy_(xc.cuda());graphs={};stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
        for arm,callback in callbacks.items():
            callback();torch.cuda.synchronize();graph=torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph,stream=stream):output=callback()
            graphs[arm]=(graph,output)
        torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize()
        for version in range(2):
            x.copy_((xc if version==0 else -xc.flip(0)).cuda())
            for arm in 'AB':graphs[arm][1].fill_(float('nan'));graphs[arm][0].replay()
            torch.cuda.synchronize();equal('changed_poisoned_graph_'+str(version),graphs['A'][1],graphs['B'][1])
            equal('graph_A_vs_fresh_'+str(version),graphs['A'][1],callbacks['A']());equal('graph_B_vs_fresh_'+str(version),graphs['B'][1],callbacks['B']())
        side=torch.cuda.Stream();side.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(side):a=callbacks['A']();b=callbacks['B']()
        torch.cuda.current_stream().wait_stream(side);torch.cuda.synchronize();equal('side_stream',a,b)
        x.copy_(xc.cuda());snapshots=[t.cpu().view(torch.uint8).clone() for t in (x,wq,scales,table)]
        for arm in 'ABBA':
            for _ in range(3):graphs[arm][0].replay()
            pair=(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True))
            result['timings'].append(dict(arm=arm,**timed_batch(torch,graphs[arm][0].replay,pair,16)))
        means={arm:statistics.mean(t['event_per_call_ms'] for t in result['timings'] if t['arm']==arm) for arm in 'AB'};result['means']=means
        equal('after_timing',graphs['A'][1],graphs['B'][1])
        result['inputs_unchanged']=all(torch.equal(t.cpu().view(torch.uint8),s) for t,s in zip((x,wq,scales,table),snapshots))
        result['table_unchanged']=torch.equal(table.cpu().view(torch.uint8),table_before)
        result['rng_unchanged']=torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        assert result['inputs_unchanged'] and result['table_unchanged'] and result['rng_unchanged']
        result['status']='component_positive' if means['B']<means['A'] else 'stopped_negative'
        result['decision']='单组完整native gate信号；无其它M/34层/官方资格，非正停止，不扫参数'
    except BaseException:result.update(status='failed',error=traceback.format_exc());traceback.print_exc()
    finally:save(run/'result.json',result)
    return 0 if result['status'] in ('component_positive','stopped_negative') else 1
