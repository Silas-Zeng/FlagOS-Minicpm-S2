"""一项device-read参考，不能替代HBM计数器或KV读上限。"""
import hashlib,json,statistics,time,traceback
from pathlib import Path

def worker(run, model, shape="hotspot"):
    result=dict(status="started",diagnostic_only=True,official_score=False,
        operation="BF16 contiguous read + per-block FP32 checksum",
        limitations=["逻辑读取率，非HBM counter；checksum归约有成本", "连续布局与GQA散页不同，不能当严格KV读带宽上限",
                     "未导入模型/native；owner的source/native pin仅固定共同环境", "copy仅一次正确性校验，不测或混同copy带宽"])
    def save():
        (Path(run)/"results.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    try:
        import torch
        import triton
        from reader import stream_read_checksum
        if torch.cuda.device_count()!=1: raise RuntimeError("必须单设备")
        torch.cuda.set_device(0)
        props=torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count!=16: raise RuntimeError("设备不符")
        size=512*1024*1024
        elements=size//2
        block=8192
        programs=triton.cdiv(elements,block)
        source=torch.empty(elements,dtype=torch.bfloat16,device="cuda")
        output=torch.empty(programs,dtype=torch.float32,device="cuda")
        def call(): return stream_read_checksum[(programs,)](source,output,elements,block,num_warps=4,num_stages=1)
        checks=[]
        for value in (1.0,-0.5):
            source.fill_(value)
            compiled=call()
            torch.cuda.synchronize()
            passed=bool(torch.equal(output,torch.full_like(output,block*value)))
            checks.append(dict(value=value,checksum_passed=passed))
            if not passed: raise RuntimeError("流读checksum不符")
        source.fill_(1.0)
        destination=torch.empty_like(source)
        destination.copy_(source)
        copy_equal=bool(torch.equal(source,destination))
        if not copy_equal: raise RuntimeError("一次device copy校验失败")
        del destination
        stream=torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for _ in range(3): call()
        torch.cuda.synchronize()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph,stream=stream): call()
        torch.cuda.synchronize()
        pairs=[(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)) for _ in range(3)]
        for start,end in pairs: start.record();end.record()
        torch.cuda.synchronize()
        timings=[]
        for start,end in pairs:
            torch.cuda.synchronize()
            begin=time.perf_counter_ns()
            start.record()
            for _ in range(16): graph.replay()
            end.record();end.synchronize()
            event_ms=start.elapsed_time(end)/16
            wall_ms=(time.perf_counter_ns()-begin)/1e6/16
            if not (event_ms>0): raise RuntimeError("计时Event无效")
            timings.append(dict(calls=16,event_ms=event_ms,wall_ms=wall_ms,
                logical_read_GBps=size/event_ms/1e6))
        if not bool(torch.equal(output,torch.full_like(output,block))): raise RuntimeError("计时后checksum失败")
        ir=Path(run)/"ir";ir.mkdir()
        for stage,data in compiled.asm.items():
            if isinstance(data,str): (ir/(stage+".txt")).write_text(data)
            elif isinstance(data,bytes): (ir/(stage+".bin")).write_bytes(data)
        result.update(status="reference_only",device=str(props),dtype="bfloat16",source_bytes=size,
            logical_read_bytes_per_call=size,logical_output_write_bytes_per_call=programs*4,
            logical_total_bytes_per_call=size+programs*4,checksum_elements_per_CTA=block,
            num_warps=4,num_stages=1,grid=programs,checks=checks,copy_equal=copy_equal,
            timings=timings,event_median_ms=statistics.median(x["event_ms"] for x in timings),
            logical_read_GBps_median=statistics.median(x["logical_read_GBps"] for x in timings),
            compiled_hash=getattr(compiled,"hash",None),profiler=False,parameter_sweep=False)
    except BaseException:
        result.update(status="failed",error=traceback.format_exc());traceback.print_exc()
    finally: save()
    return 0 if result["status"]=="reference_only" else 1
