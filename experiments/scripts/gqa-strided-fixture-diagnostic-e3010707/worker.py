"""仅定位同 FlagGems dispatch 下非连续 Q 夹具的写入范围；无 GQA。"""
from pathlib import Path
import hashlib
import inspect
import json
import traceback


def worker(run, model):
    result = dict(status="started", cases=[], gpu_attention_called=False,
                  scope="仅Q构造操作；不是数值/性能或模型成绩")
    save = lambda: (run / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    try:
        import torch
        import vllm_fl
        from vllm.config import CompilationConfig, CUDAGraphMode, set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs
        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
            max_model_len=131072, compilation_config=CompilationConfig(
                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        with set_current_vllm_config(config):
            from vllm_fl.ops.custom_ops import register_oot_ops
            from dispatch_bootstrap import enable_dispatch
            register_oot_ops()
            result["dispatch"] = enable_dispatch(torch, run)
        props = torch.cuda.get_device_properties(0)
        if torch.cuda.device_count() != 1 or "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("非本站唯一BI-V150")
        result["device"] = str(props)
        import flag_gems
        provider = {}
        zero_fn = inspect.unwrap(flag_gems.zero_)
        zero_path = Path(inspect.getsourcefile(zero_fn))
        zero_data = zero_path.read_bytes()
        (run / "actual-flaggems-zero.py").write_bytes(zero_data)
        result["actual_flaggems_zero"] = dict(source=str(zero_path), function=zero_fn.__name__,
            sha256=hashlib.sha256(zero_data).hexdigest())
        for name in ("zero_", "fill_.Scalar", "copy_", "neg_"):
            table = torch._C._dispatch_dump_table("aten::" + name)
            (run / ("dispatch-" + name.replace(".", "-") + ".txt")).write_text(table)
            provider[name] = dict(dispatch_cuda=[s for s in table.splitlines() if s.startswith("CUDA:")])
        for op, fn, *_ in flag_gems.current_work_registrar.config:
            if op in ("zero_", "fill_.Scalar", "copy_", "neg_"):
                raw = inspect.unwrap(fn)
                path = Path(inspect.getsourcefile(raw))
                data = path.read_bytes()
                target = run / ("provider-" + op.replace(".", "-") + "-" + path.name)
                target.write_bytes(data)
                provider.setdefault(op, {}).update(source=str(path), sha256=hashlib.sha256(data).hexdigest(), function=raw.__name__)
        result["providers"] = provider
        if not any("flag_gems" in s for s in provider["zero_"]["dispatch_cuda"]):
            raise RuntimeError("zero_未注册同FlagGems CUDA dispatch")
        # 每操作独立 backing；初始化及 oracle 在CPU构造，GPU只拷入连续整份 backing。
        for B in (32, 64):
            for op in ("neg", "zero", "fill", "copy"):
                cpu = torch.full((B + 3, 2560), -23, dtype=torch.bfloat16)
                qcpu = cpu[:, :2048].view(B + 3, 16, 128)
                qcpu[:B].copy_((torch.arange(B*2048).remainder(31).reshape(B,16,128)-15).to(torch.bfloat16))
                qcpu[B:] = -17
                expected = cpu.clone()
                eq = expected[:, :2048].view(B + 3, 16, 128)
                values = torch.full((B,16,128), 3, dtype=torch.bfloat16)
                if op == "neg": eq[:B].neg_()
                elif op == "zero": eq[:B].zero_()
                elif op == "fill": eq[:B].fill_(1)
                else: eq[:B].copy_(values)
                backing = cpu.to("cuda")
                q = backing[:, :2048].view(B + 3, 16, 128)
                before = backing.cpu().view(torch.int16).clone()
                if op == "neg": q[:B].neg_()
                elif op == "zero": q[:B].zero_()
                elif op == "fill": q[:B].fill_(1)
                else: q[:B].copy_(values.to("cuda"))
                torch.cuda.synchronize()
                after = backing.cpu().view(torch.int16).clone()
                exp = expected.view(torch.int16)
                bad = after != exp
                changed = before != after
                row = dict(B=B, op=op, q_stride=list(q.stride()),
                    guard_before=bool((before[:,2048:]==cpu.view(torch.int16)[:,2048:]).all()),
                    guard_after=bool((after[:,2048:]==before[:,2048:]).all()),
                    full_expected_bits=bool(torch.equal(after,exp)),
                    active_expected_bits=bool(torch.equal(after[:B,:2048],exp[:B,:2048])),
                    padded_rows_unchanged=bool(torch.equal(after[B:],before[B:])),
                    wrong_elements=int(bad.sum()), guard_changed_elements=int(changed[:,2048:].sum()),
                    first_wrong_coords=bad.nonzero()[:16].tolist())
                torch.save(dict(before=before, after=after, expected=exp), run / (f"B{B}-{op}.pt"))
                result["cases"].append(row)
                save()
        result["status"] = "diagnostic_complete"
        result["all_expected_bits"] = all(x["full_expected_bits"] for x in result["cases"])
        save()
        return 0
    except BaseException:
        result.update(status="failed_stop", error=traceback.format_exc())
        save()
        traceback.print_exc()
        return 1
