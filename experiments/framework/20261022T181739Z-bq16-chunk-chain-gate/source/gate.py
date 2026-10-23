#!/usr/bin/env python3
"""One actual-backend seven-chunk Attention chain; BQ16 scheduling geometry only.

No weights, serving, profiler, graph capture, sweep or official score. The
controller imports no accelerator runtime; only its owned child uses CUDA.
"""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
from pathlib import Path
import shlex
import signal
import statistics
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace as NS

from validate_hidden_row_gather import digest, load, utc, write


EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"
EXPECTED_WRITER = "f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb"
TIMING_METHOD = "7-chunk chain ABBA, 32 chains/window; prerecord events; wall includes record/submit/final sync; CPU submit clocks exclude final sync; v1 cpu.stat outside window"


def cpu_snapshot():
    names = {"stat": "/sys/fs/cgroup/cpu/cpu.stat",
             "quota": "/sys/fs/cgroup/cpu/cpu.cfs_quota_us",
             "period": "/sys/fs/cgroup/cpu/cpu.cfs_period_us"}
    raw = {name: Path(path).read_text(encoding="utf-8").strip() for name, path in names.items()}
    counters = {line.split()[0]: int(line.split()[1]) for line in raw["stat"].splitlines()}
    if (not {"nr_periods", "nr_throttled", "throttled_time"} <= counters.keys()
            or int(raw["quota"]) != 600000 or int(raw["period"]) != 100000):
        raise RuntimeError("expected the actual unchanged v1 six-CPU quota")
    return {"paths": names, "raw": raw, "counters": counters}


def timed_batch(torch, callback, pair, loops):
    torch.cuda.synchronize()
    before_cpu = cpu_snapshot()
    start, end = pair
    begin = time.perf_counter_ns()
    start.record()
    thread_begin, process_begin = time.thread_time_ns(), time.process_time_ns()
    for _ in range(loops):
        callback()
    submit_thread_ns = time.thread_time_ns() - thread_begin
    submit_process_ns = time.process_time_ns() - process_begin
    end.record()
    torch.cuda.synchronize()
    wall = (time.perf_counter_ns() - begin) / 1e6
    after_cpu = cpu_snapshot()
    event = start.elapsed_time(end)
    if not math.isfinite(event) or event <= 0:
        raise RuntimeError("invalid timing Event elapsed time")
    return {"calls": loops, "wall_total_ms": wall, "wall_per_call_ms": wall / loops,
            "event_total_ms": event, "event_per_call_ms": event / loops,
            "submit_thread_cpu_ns": submit_thread_ns, "submit_process_cpu_ns": submit_process_ns,
            "cpu_stat_before": before_cpu, "cpu_stat_after": after_cpu,
            "cpu_stat_delta": {name: after_cpu["counters"][name] - before_cpu["counters"][name]
                               for name in before_cpu["counters"]}}


def delta(after, before, name):
    return after[name] - before[name]



START, END, DECODE, STEPS = 2944, 16704, 29, 7
CHUNKS = {"baseline": [2019] * 6 + [1646], "aligned": [2016] * 6 + [1664]}


def worker(run, model):
    result = {"status": "started", "kind": "synthetic actual Attention seven-chunk chain, not E2E",
              "chunks": CHUNKS, "target_absolute_range": [START, END], "timing_loops": 32,
              "limitations": ["Target geometry comes from 165525; decode starts at constructed 16384, not observed exact lengths.",
                  "Only existing C2/C3 and existing kernels; no scheduler/runtime/operator modification.",
                  "Input packing, allocation and slot construction excluded; timed callback includes builder, original writer and forward for all seven chunks.",
                  "No GEMM/model/sampling/accuracy evidence; unchanged BF16 strict bits is required before timing."]}
    torch = backend = old_unified = None
    hold = []
    try:
        import importlib
        import itertools
        import torch
        import validate_mixed_decode as previous
        from vllm.config import CompilationConfig, CUDAGraphMode
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
            max_model_len=131072, compilation_config=CompilationConfig(
                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        text = config.model_config.hf_text_config
        if (Path(str(config.model_config.model).rstrip("/\\")).name != "MiniCPM5-2B"
            or config.model_config.dtype != torch.bfloat16
            or (text.hidden_size,text.num_hidden_layers,text.num_attention_heads,text.num_key_value_heads)!=(2048,42,16,2)):
            raise RuntimeError("requires original MiniCPM5-2B BF16")
        backend=importlib.import_module("vllm.v1.attention.backends.triton_attn")
        attention=importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        helpers=importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        writer=importlib.import_module("vllm.v1.attention.ops.triton_reshape_and_cache_flash")
        if digest(Path(writer.__file__))!=EXPECTED_WRITER or backend.triton_reshape_and_cache_flash is not writer.triton_reshape_and_cache_flash:
            raise RuntimeError("unknown actual KV writer")
        c2=load("bq16_chain_c2",run/"source/runtime.py")
        c3=load("bq16_chain_c3",run/"source/mixed.py")
        result["c2_install"],result["c3_install"]=c2.install(),c3.install()
        for name,module in (("backend.py",backend),("attention.py",attention),("helpers.py",helpers),("writer.py",writer)):
            (run/"source"/name).write_bytes(Path(module.__file__).read_bytes())
        (run/"source/model-config.json").write_bytes((model/"config.json").read_bytes())
        if torch.cuda.device_count()!=1:raise RuntimeError("one accelerator required")
        torch.cuda.set_device(0);torch.manual_seed(721502)
        result["device"]=str(torch.cuda.get_device_properties(0));result["torch_num_threads"]=torch.get_num_threads()
        spec=FullAttentionSpec(block_size=16,num_kv_heads=2,head_size=128,dtype=torch.bfloat16)
        builder=backend.TritonAttentionMetadataBuilder(spec,["synthetic.attn"],config,torch.device("cuda:0"))
        impl=backend.TritonAttentionImpl(num_heads=16,head_size=128,scale=128**-0.5,num_kv_heads=2,
             alibi_slopes=None,sliding_window=None,kv_cache_dtype="auto",attn_type=backend.AttentionType.DECODER)
        layer=NS(_q_scale=torch.full((),0.75,device="cuda"),_k_scale=torch.full((),1.25,device="cuda"),_v_scale=torch.full((),0.5,device="cuda"))
        scale_values=tuple(x.clone() for x in (layer._q_scale,layer._k_scale,layer._v_scale))
        common,unusedq,unusedk,unusedv,initial=previous.make_data(torch,[1]*DECODE+[2019],END)
        blocks=(END+15)//16
        table=torch.randperm((DECODE+1)*blocks,device="cuda",dtype=torch.int64).to(torch.int32).reshape(DECODE+1,blocks)
        table[-1,:16]=table[0,:16] # only immutable past positions are shared
        pages=table.cpu().tolist()
        for page in pages[-1][START//16:]:
            initial.narrow(0,page,1).fill_(float("nan"))
        tq=torch.randn((END-START,16,128),device="cuda",dtype=torch.bfloat16)
        tk=torch.randn((END-START,2,128),device="cuda",dtype=torch.bfloat16);tv=torch.randn_like(tk)
        dq=torch.randn((STEPS,DECODE,16,128),device="cuda",dtype=torch.bfloat16)
        dk=torch.randn((STEPS,DECODE,2,128),device="cuda",dtype=torch.bfloat16);dv=torch.randn_like(dk)
        fixtures={}; all_inputs=[]
        for name,chunks in CHUNKS.items():
            rows=[];position=START;logical_slots=[]
            for step,qsize in enumerate(chunks):
                offset=position-START;lengths=[1]*DECODE+[qsize];total=DECODE+qsize
                cu=torch.tensor([0,*itertools.accumulate(lengths)],dtype=torch.int32)
                seq=[16384+step+1]*DECODE+[position+qsize]
                slots=[pages[r][(16384+step)//16]*16+(16384+step)%16 for r in range(DECODE)]
                slots += [pages[-1][absolute//16]*16+absolute%16 for absolute in range(position,position+qsize)]
                logical_slots.extend(slots[DECODE:])
                common=NS(num_reqs=DECODE+1,num_actual_tokens=total,max_query_len=qsize,max_seq_len=max(seq),
                    query_start_loc_cpu=cu,query_start_loc=cu.to("cuda"),seq_lens=torch.tensor(seq,dtype=torch.int32,device="cuda"),
                    block_table_tensor=table,slot_mapping=torch.tensor(slots+[-1]*3,dtype=torch.int64,device="cuda"),causal=True,mm_req_doc_ranges=None)
                q=torch.cat((dq[step],tq[offset:offset+qsize],torch.full((3,16,128),float("nan"),device="cuda",dtype=torch.bfloat16)))
                k=torch.cat((dk[step],tk[offset:offset+qsize],torch.full((3,2,128),float("nan"),device="cuda",dtype=torch.bfloat16)))
                v=torch.cat((dv[step],tv[offset:offset+qsize],torch.full((3,2,128),float("nan"),device="cuda",dtype=torch.bfloat16)))
                out=torch.full_like(q,-17)
                rows.append((common,q,k,v,out));all_inputs.extend((q,k,v));position+=qsize
            if position!=END:raise RuntimeError("target absolute coverage incomplete")
            fixtures[name]={"rows":rows,"cache":initial.clone(),"logical_slots":logical_slots}
        if fixtures["baseline"]["logical_slots"]!=fixtures["aligned"]["logical_slots"]:
            raise RuntimeError("target absolute physical slots differ")
        snapshots=[x.clone() for x in all_inputs]
        old_unified=backend.unified_attention;observed=[]
        def observe(*args,**kwargs):
            observed.append({"q":int(kwargs["q"].shape[0]),"max_q":int(kwargs["max_seqlen_q"]),
                             "seqs":int(kwargs["seqused_k"].shape[0])})
            return old_unified(*args,**kwargs)
        def chain(name,rows=None):
            fixture=fixtures[name];rows=fixture["rows"] if rows is None else rows
            for common,q,k,v,out in rows:
                metadata=builder.build(0,common)
                plan=getattr(metadata,c3._PLAN,None)
                if plan is None or plan.prefix_tokens!=DECODE or plan.total_tokens!=common.num_actual_tokens:
                    raise RuntimeError("original C3 failed to split the planned geometry")
                impl.do_kv_cache_update(layer,k,v,fixture["cache"],common.slot_mapping)
                impl.forward(layer,q,k,v,fixture["cache"],metadata,out)
        def assembled(rows):
            return (torch.stack([row[4][:DECODE] for row in rows]),
                    torch.cat([row[4][DECODE:row[0].num_actual_tokens] for row in rows]))
        def equal_bits(a,b):return torch.equal(a.view(torch.int16),b.view(torch.int16))
        cpu_rng,gpu_rng=torch.get_rng_state().clone(),torch.cuda.get_rng_state().clone()
        backend.unified_attention=observe
        chain("baseline");chain("aligned");torch.cuda.synchronize()
        backend.unified_attention=old_unified
        a,b=assembled(fixtures["baseline"]["rows"]),assembled(fixtures["aligned"]["rows"])
        checks={"target_absolute_slots_equal":True,"absolute_target_output_bits_equal":equal_bits(a[1],b[1]),
            "decode_step_output_bits_equal":equal_bits(a[0],b[0]),"entire_final_kv_bits_equal":equal_bits(fixtures["baseline"]["cache"],fixtures["aligned"]["cache"]),
            "valid_outputs_finite":all(bool(torch.isfinite(x).all()) for x in (*a,*b)),
            "padding_untouched":all(bool((row[4][row[0].num_actual_tokens:]==-17).all()) for f in fixtures.values() for row in f["rows"]),
            "inputs_unchanged":all(equal_bits(x,y) for x,y in zip(all_inputs,snapshots)),
            "rng_unchanged":torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state()),
            "actual_c3_decode_calls":sum(x["max_q"]==1 and x["q"]==DECODE and x["seqs"]==DECODE for x in observed)==14,
            "actual_c3_prefill_calls":sum(x["max_q"]>1 and x["seqs"]==1 for x in observed)==14,
            "scale_values_unchanged":all(torch.equal(x,y) for x,y in zip((layer._q_scale,layer._k_scale,layer._v_scale),scale_values))}
        result["checks"]=checks;result["observed_unified_calls"]=observed
        result["max_abs_target_diff"]=float((a[1].float()-b[1].float()).abs().max())
        result["allclose_001_record_only"]=bool(torch.allclose(a[1],b[1],atol=0.01,rtol=0.01))
        if not all(checks.values()):raise RuntimeError("strict chain bits/KV/RNG gate failed; no timing")
        # Changed Q pointers and values, one non-default stream, original producer→consumer boundary.
        side=torch.cuda.Stream();producer=torch.cuda.Event();done=torch.cuda.Event();new_rows={}
        for name,fixture in fixtures.items():
            fixture["cache"].copy_(initial)
            new_rows[name]=[(c,q.clone().mul_(0.5),k,v,torch.full_like(out,-17)) for c,q,k,v,out in fixture["rows"]]
        producer.record()
        with torch.cuda.stream(side):
            side.wait_event(producer)
            chain("baseline",new_rows["baseline"]);chain("aligned",new_rows["aligned"])
            aa,bb=assembled(new_rows["baseline"]),assembled(new_rows["aligned"])
            side_same=(aa[0].view(torch.int16)==bb[0].view(torch.int16)).all() & (aa[1].view(torch.int16)==bb[1].view(torch.int16)).all()
            side_finite=torch.stack([torch.isfinite(x).all() for x in (*aa,*bb)]).all()
            side_padding=torch.stack([(row[4][row[0].num_actual_tokens:]==-17).all() for rows in new_rows.values() for row in rows]).all()
            done.record()
        done.synchronize()
        checks.update({"nondefault_stream":int(side.cuda_stream)!=int(torch.cuda.default_stream().cuda_stream),
            "new_q_pointers":all(new_rows[name][i][1].data_ptr()!=fixtures[name]["rows"][i][1].data_ptr() for name in fixtures for i in range(STEPS)),
            "new_output_pointers":all(new_rows[name][i][4].data_ptr()!=fixtures[name]["rows"][i][4].data_ptr() for name in fixtures for i in range(STEPS)),
            "side_consumer_bits_equal":bool(side_same.item()),
            "side_valid_outputs_finite":bool(side_finite.item()),"side_padding_untouched":bool(side_padding.item()),
            "side_final_kv_bits_equal":equal_bits(fixtures["baseline"]["cache"],fixtures["aligned"]["cache"]),
            "side_rng_unchanged":torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())})
        if not all(checks.values()):raise RuntimeError("non-default-stream gate failed")
        # No pool comparisons or CPU pattern generation between timing windows.
        pairs=[(torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)) for _ in range(4)]
        for pair in pairs:
            for event in pair:event.record()
        torch.cuda.synchronize()
        windows=[]
        for name,pair in zip(("baseline","aligned","aligned","baseline"),pairs):
            item=timed_batch(torch,lambda n=name:chain(n),pair,32);item["variant"]=name;windows.append(item)
        result["timing_windows"]=windows
        result["timing_summary"]={name:{"wall_ms_per_chain":statistics.median(x["wall_per_call_ms"] for x in windows if x["variant"]==name),
             "event_ms_per_chain":statistics.median(x["event_per_call_ms"] for x in windows if x["variant"]==name)} for name in fixtures}
        checks["after_timing_final_kv_equal"]=equal_bits(fixtures["baseline"]["cache"],fixtures["aligned"]["cache"])
        final_a,final_b=assembled(fixtures["baseline"]["rows"]),assembled(fixtures["aligned"]["rows"])
        checks["after_timing_output_bits_equal"]=all(equal_bits(x,y) for x,y in zip(final_a,final_b))
        checks["after_timing_outputs_finite"]=all(bool(torch.isfinite(x).all()) for x in (*final_a,*final_b))
        checks["after_timing_padding_untouched"]=all(bool((row[4][row[0].num_actual_tokens:]==-17).all()) for f in fixtures.values() for row in f["rows"])
        checks["after_timing_inputs_unchanged"]=all(equal_bits(x,y) for x,y in zip(all_inputs,snapshots))
        checks["after_timing_rng_unchanged"]=torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        if not all(checks.values()):raise RuntimeError("post-timing checks failed")
        result["status"]="pass"
    except BaseException:
        result["status"]="fail";result["error"]=traceback.format_exc();traceback.print_exc()
    finally:
        if backend is not None and old_unified is not None:backend.unified_attention=old_unified
        if torch is not None:
            try:torch.cuda.synchronize();result["settled"]=True
            except BaseException:result["settled"]=False;result["settle_error"]=traceback.format_exc()
        result["finished_utc"]=utc();write(run/"results.json",result)
    return 0 if result["status"]=="pass" else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--runtime-path", type=Path)
    parser.add_argument("--mixed-path", type=Path)
    parser.add_argument("--model", type=Path, default=Path("/workspace/MiniCPM5-2B"))
    parser.add_argument("--ixsmi", default="/usr/local/corex-4.5.0/bin/ixsmi")
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir, args.model)
    if any(path is None for path in (args.runtime_path, args.mixed_path)):
        parser.error("controller requires original C2 and C3 paths")
    import fcntl
    import validate_block_table_candidate as owner
    import validate_hidden_row_gather as utilities
    import validate_mixed_decode as previous
    import bench_attention_dispatch as shared

    root, run = owner.ROOT.resolve(), args.run_dir.resolve()
    if not run.is_relative_to(root) or run == root:
        raise ValueError("run must be a new child of experiment root")
    run.mkdir(parents=True, exist_ok=False)
    manifest = {"started_utc": utc(), "pid": os.getpid(), "command": [sys.executable, *sys.argv],
                "command_shell": shlex.join([sys.executable, *sys.argv]),
                "kind": "one actual-layer 7-chunk BQ16 geometry chain, original kernels, 32 ABBA, no weights/service/score",
                "timing_loops": 32, "timing_method": TIMING_METHOD,
                "environment": {name: os.environ[name] for name in (
                    "VLLM_PLUGINS", "PYTHONPATH", "CUDA_VISIBLE_DEVICES", "IX_VISIBLE_DEVICES",
                    "COREX_VISIBLE_DEVICES", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "TRITON_CACHE_DIR") if name in os.environ}}
    lock, child, monitor, monitor_log, status = None, None, None, None, 1
    def interrupted(signum, frame):
        raise SystemExit(f"controller interrupted by signal {signum}")
    signal.signal(signal.SIGTERM, interrupted)
    try:
        lock = (root / "framework-device.lock").open("a")
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        base_path = os.environ["PYTHONPATH"].split(os.pathsep)[0]
        if not base_path:
            raise RuntimeError("PYTHONPATH must begin with the clean base source directory")
        base_runner = Path(base_path) / "vllm_fl/worker/model_runner.py"
        manifest["base_runner_sha256"] = digest(base_runner)
        if manifest["base_runner_sha256"] != "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141":
            raise RuntimeError("gate requires the clean combined 6f runner")
        manifest["preflight"] = owner.preflight(args.ixsmi)
        gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
        (run / "preflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
        if "No running processes found" not in gpu:
            raise RuntimeError("accelerator process already active")
        source = run / "source"
        source.mkdir()
        for name, path in (("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),
                           ("mixed.py", args.mixed_path),
                           ("validate_hidden_row_gather.py", Path(utilities.__file__)),
                           ("validate_mixed_decode.py", Path(previous.__file__)),
                           ("bench_attention_dispatch.py", Path(shared.__file__)),
                           ("validate_block_table_candidate.py", Path(owner.__file__)),
                           ("monitor_gpu.sh", root / "scripts/monitor_gpu.sh")):
            (source / name).write_bytes(path.read_bytes())
        for name, expected in (("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3)):
            if expected is None or digest(source / name) != expected:
                raise RuntimeError("unaudited original chain gate asset: " + name)
        manifest["source_sha256"] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest["packages"] = {}
        for package in ("torch", "vllm", "FlagGems", "SQLAlchemy"):
            try:
                manifest["packages"][package] = importlib.metadata.version(package)
            except importlib.metadata.PackageNotFoundError:
                manifest["packages"][package] = "unavailable"
        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run),
                                      "--model", str(args.model)]
        write(run / "manifest.json", manifest)
        with (run / "worker.log").open("x") as log:
            child = subprocess.Popen(manifest["worker_command"], stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            manifest["worker_pid"] = child.pid
            monitor_log = (run / "monitor.log").open("x")
            monitor = subprocess.Popen(["bash", str(source / "monitor_gpu.sh"), str(child.pid), str(run / "gpu.csv")],
                                       stdout=monitor_log, stderr=subprocess.STDOUT, start_new_session=True)
            write(run / "manifest.json", manifest)
            status = child.wait(timeout=300)
    except BaseException:
        manifest["controller_error"] = traceback.format_exc()
        traceback.print_exc()
    finally:
        for process in (child, monitor):
            if process is not None and process.poll() is None:
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=10)
                except ProcessLookupError:
                    process.wait(timeout=10)
                except BaseException:
                    manifest["cleanup_error"], status = traceback.format_exc(), 1
        if monitor_log is not None:
            monitor_log.close()
        if child is not None and child.poll() is not None:
            try:
                manifest["postflight"] = owner.preflight(args.ixsmi)
                gpu = subprocess.check_output([args.ixsmi], text=True, timeout=10)
                (run / "postflight-ixsmi.txt").write_text(gpu, encoding="utf-8")
                if "No running processes found" not in gpu:
                    raise RuntimeError("accelerator process remains after owned worker exit")
            except BaseException:
                manifest["postflight_error"], status = traceback.format_exc(), 1
        manifest.update(finished_utc=utc(), exit_code=status)
        write(run / "manifest.json", manifest)
        (run / "exit-code").write_text(str(status) + "\n", encoding="utf-8")
        (run / "finished-at.txt").write_text(manifest["finished_utc"] + "\n", encoding="utf-8")
        if lock is not None:
            lock.close()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
