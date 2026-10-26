"""待GPU组件入口：复用root现有owner调用worker，不可单独占卡。"""
import hashlib
import json
import os
from pathlib import Path
import statistics
import time
import traceback

from reference import quantize_group, dequantized_dot, output_error


def worker(run, model, activations=None):
    """run须是既有唯一设备owner创建的run；无激活时仅合成组件，不给模型资格。"""
    run, model = Path(run), Path(model)
    manifest = json.loads((run/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('owner_pid') != os.getppid():
        raise RuntimeError('必须通过持唯一设备锁、已核GPU/9031的项目owner启动')
    result = dict(status='started',kind='独立K256分组W8A8组件，不是官方成绩',
                  production_changed=False,cases=[],timings=[],resources=[],
                  real_activations=activations is not None,
                  limitations=['仅layer20实际权重，未覆盖42层及模型真实算子交织。',
                    '保留BF16权重便于对照；本组件不能声称显存/KV收益。',
                    '工程误差淘汰线不能代替官方105题或原BF16逐位合同。'])
    try:
        import torch
        import triton
        import flag_gems
        import candidate
        from safetensors import safe_open
        props = torch.cuda.get_device_properties(torch.cuda.current_device())
        target = triton.runtime.driver.active.get_current_target()
        if ('BI-V150' not in props.name or props.multi_processor_count != 16
                or target.arch != 71 or target.warp_size != 64):
            raise RuntimeError('仅BI-V150/16SM/CoreX71/warp64组件')
        result['target']=str(target)
        result['pid']=os.getpid()
        result['command']=__import__('sys').argv
        index=json.loads((model/'model.safetensors.index.json').read_bytes())
        name='model.layers.20.mlp.down_proj.weight'
        with safe_open(str(model/index['weight_map'][name]),framework='pt',device='cpu') as handle:
            wc=handle.get_tensor(name).contiguous()
        assert tuple(wc.shape)==(2048,6144) and wc.dtype==torch.bfloat16
        result['weight']=dict(name=name,sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest())
        if activations is None:
            generator=torch.Generator().manual_seed(20261026)
            xc=(torch.randn((2048,6144),generator=generator,dtype=torch.float32)*.125).bfloat16()
            result['activation_kind']='合成；不能证明真实SwiGLU误差或模型正确性'
        else:
            ap=Path(activations)
            xc=torch.load(ap,map_location='cpu',weights_only=True)
            assert isinstance(xc,torch.Tensor) and tuple(xc.shape)==(2048,6144) and xc.dtype==torch.bfloat16
            xc=xc.contiguous()
            result['activation_kind']=dict(path=str(ap),sha256=hashlib.sha256(ap.read_bytes()).hexdigest())
        assert bool(torch.isfinite(xc).all() and torch.isfinite(wc).all())
        cpu_rng=torch.get_rng_state().clone();gpu_rng=torch.cuda.get_rng_state().clone()
        w=wc.cuda();x=xc.cuda()
        start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
        start.record();wq,ws=candidate.pack_weight(w);end.record();end.synchronize()
        result['weight_pack_once_ms']=start.elapsed_time(end)
        result['packed_bytes']=wq.numel()+ws.numel()*4
        qwc=wq.cpu();swc=ws.cpu()
        for col in (0,1,1024,2047):
            for group in (0,1,23):
                q,s=quantize_group(wc[col,group*256:(group+1)*256].float().tolist())
                assert qwc[col,group*256:(group+1)*256].tolist()==q
                assert swc[col,group].item()==s
        for m in (2030,2048):
            xx=x[:m];aq=torch.empty((m,6144),device=x.device,dtype=torch.int8)
            sa=torch.empty((m,24),device=x.device,dtype=torch.float32)
            y=torch.empty((m,2048),device=x.device,dtype=torch.bfloat16);base=torch.empty_like(y)
            compiled=candidate.launch_into(xx,wq,ws,y,aq,sa)
            torch.cuda.synchronize()
            for kernel in compiled:
                md=kernel.metadata
                result['resources'].append(dict(rows=m,name=kernel.name,shared=getattr(md,'shared',None),
                    num_warps=getattr(md,'num_warps',None),n_regs=getattr(kernel,'n_regs',None),
                    n_spills=getattr(kernel,'n_spills',None)))
                for kind in ('ttgir','llir','asm','ptx'):
                    source=kernel.asm.get(kind)
                    if isinstance(source,str):(run/f'{m}-{kernel.name}.{kind}').write_text(source,encoding='utf-8')
            qac=aq.cpu();sac=sa.cpu()
            for row in (0,1,m//2,m-1):
                for group in range(24):
                    q,s=quantize_group(xc[row,group*256:(group+1)*256].float().tolist())
                    assert qac[row,group*256:(group+1)*256].tolist()==q
                    assert sac[row,group].item()==s
            # 每组独立CPU INT64参考：验证编译器INT8 dot及布局，绝不按性能改框架。
            partial=torch.empty((32,64),device=x.device,dtype=torch.int32)
            for group in range(24):
                candidate.group_integer_probe[(1,)](aq,wq,partial,M=32,N=2048,K=6144,GROUP=group,
                    num_warps=4,num_stages=1,enable_fp_fusion=False)
                expected=qac[:32,group*256:(group+1)*256].long() @ qwc[:64,group*256:(group+1)*256].long().T
                assert torch.equal(partial.cpu().long(),expected), 'INT8 dot ABI/布局失败，精确否决'
            rows=[0,1,m//2,m-1];cols=[0,1,17,63,127,255,511,1023,1535,2047]
            target=xc[rows].double()@wc[cols].double().T
            # 量化格式的独立FP64数学参考，不用同一GPU核互证。
            aq_ref=qac[rows].reshape(4,24,256).double()*sac[rows,:,None].double()
            wq_ref=qwc[cols].reshape(10,24,256).double()*swc[cols,:,None].double()
            quant_ref=aq_ref.reshape(4,6144)@wq_ref.reshape(10,6144).T
            actual=y[rows][:,cols].cpu().double()
            # 禁FMA的24组scale/累加拓扑也做独立FP32逐步舍入，再BF16。
            rounded=[]
            for row in rows:
                row_result=[]
                ag=[qac[row,g*256:(g+1)*256].tolist() for g in range(24)]
                asc=sac[row].tolist()
                for col in cols:
                    wg=[qwc[col,g*256:(g+1)*256].tolist() for g in range(24)]
                    row_result.append(dequantized_dot(ag,asc,wg,swc[col].tolist()))
                rounded.append(row_result)
            exact_format=torch.tensor(rounded,dtype=torch.bfloat16).double()
            assert torch.equal(actual,exact_format), '分组FP32缩放/加和或BF16舍入与独立参考不一致'
            approximation=output_error(actual.flatten().tolist(),target.flatten().tolist())
            implementation=output_error(actual.flatten().tolist(),quant_ref.flatten().tolist())
            case=dict(rows=m,integer_groups_passed=24,fp32_grouped_reference_bitwise=True,approximation=approximation,
                      implementation_vs_quant_fp64=implementation,finite=bool(torch.isfinite(y).all()))
            result['cases'].append(case)
            assert case['finite'] and approximation['passed'] and implementation['passed'], '预声明误差门失败，停止计时'
            # 完整两kernel捕获；权重pack只在加载期发生，激活量化每次都计入。
            graphs={}
            with flag_gems.use_gems():
                for arm in 'AB':
                    for _ in range(2):
                        if arm=='A':torch.mm(xx,w.T,out=base)
                        else:candidate.launch_into(xx,wq,ws,y,aq,sa)
                    torch.cuda.synchronize()
                    graph=torch.cuda.CUDAGraph()
                    with torch.cuda.graph(graph):
                        if arm=='A':torch.mm(xx,w.T,out=base)
                        else:candidate.launch_into(xx,wq,ws,y,aq,sa)
                    graphs[arm]=graph
            # 同址全零/换值Graph：防止使用旧量化缓存，且输出必须被全覆盖。
            xx.zero_();y.fill_(float('nan'));graphs['B'].replay();torch.cuda.synchronize()
            assert torch.equal(y,torch.zeros_like(y))
            xx.copy_(-xc[:m].cuda());y.fill_(float('nan'));graphs['B'].replay();torch.cuda.synchronize()
            assert bool(torch.isfinite(y).all())
            direct=torch.empty_like(y);candidate.launch_into(xx,wq,ws,direct,aq,sa)
            torch.cuda.synchronize();assert torch.equal(y,direct)
            stream=torch.cuda.Stream();stream.wait_stream(torch.cuda.current_stream())
            with torch.cuda.stream(stream):candidate.launch_into(xx,wq,ws,direct,aq,sa)
            torch.cuda.current_stream().wait_stream(stream);torch.cuda.synchronize();assert torch.equal(y,direct)
            case['graph_changed_zero_and_side_stream']=True
            xx.copy_(xc[:m].cuda())
            for arm in 'ABBA':
                for _ in range(3):graphs[arm].replay()
                torch.cuda.synchronize();t=time.perf_counter();start.record()
                for _ in range(8):graphs[arm].replay()
                end.record();end.synchronize()
                result['timings'].append(dict(rows=m,arm=arm,event_ms=start.elapsed_time(end)/8,
                    wall_ms=(time.perf_counter()-t)*1000/8))
        result['means']={str(m):{arm:statistics.mean(v['event_ms'] for v in result['timings']
            if v['rows']==m and v['arm']==arm) for arm in 'AB'} for m in (2030,2048)}
        assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        result.update(status='completed',rng_unchanged=True,official_accuracy_qualified=False)
    except BaseException:
        result.update(status='failed',error=traceback.format_exc())
    (run/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    return 0 if result['status']=='completed' else 1


if __name__=='__main__':
    raise SystemExit('只提供worker(run,model,activations=None)，须经现有唯一设备owner调用；当前文件不自行启动GPU。')
