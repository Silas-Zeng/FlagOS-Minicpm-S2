"""MiniCPM 真实 2D Attention 组件；不加载模型权重、不证明模型资格。"""
from __future__ import annotations
import importlib
import json
from pathlib import Path
import re
import statistics
import time
import traceback
from types import SimpleNamespace as NS

import prototype
import next_k
from legacy_gate import timed_batch
from validate_hidden_row_gather import digest, write
from validate_mixed_decode import make_data


class Capture:
    def __init__(self, original):
        self.original, self.records = original, []

    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            result = self.original[grid](*args, **kwargs)
            if kwargs.get("IS_3D") is False:
                if args:
                    raise RuntimeError("组件要求实际 keyword ABI")
                self.records.append((grid, dict(kwargs), result))
            return result
        return launch


def dump(compiled, folder):
    folder.mkdir(exist_ok=True)
    for name, value in compiled.asm.items():
        if isinstance(value, (str, bytes)):
            path = folder / (name + (".txt" if isinstance(value, str) else ".bin"))
            raw = value.encode() if isinstance(value, str) else value
            if path.exists():
                if path.read_bytes() != raw:
                    raise RuntimeError("同轮编译原件发生变化")
            else:
                path.write_bytes(raw)


def preserve(compiled, folder, qmod, kernel, attention):
    dump(compiled, folder)
    proof = qmod.lowered_proof(compiled.asm["ttgir"], compiled.asm["llir"],
        qmod._q_debug_lines(kernel.fn) | qmod._q_debug_lines(attention.__file__))
    resources = qmod._resources(compiled)
    assembly = compiled.asm.get("asm", "")
    # 资源变化记录成本；Q-hoist 仍须真实保留，不能用静态资源替代净计时。
    private = re.search(r"workitem_private_segment_byte_size\s*=\s*(\d+)", assembly)
    if not proof["mechanism_pass"]:
        raise RuntimeError("Q-hoist 机器码门未通过")
    return dict(q_hoist=proof, resources=resources,
                private_bytes=int(private[1]) if private is not None else None,
                runtime_spills=getattr(compiled, "n_spills", None))


def conditional_lookup(ttgir):
    """确认实际生成的 scf.if 一臂不读页表、另一臂读取；机器码另存供审阅。"""
    lines = ttgir.splitlines()
    loop = next(i for i, line in enumerate(lines) if "= scf.for " in line)
    for start in range(loop + 1, len(lines)):
        line = lines[start]
        if "scf.if " not in line:
            continue
        indent = len(line) - len(line.lstrip())
        middle = end = None
        for pos in range(start + 1, len(lines)):
            text = lines[pos]
            if len(text) - len(text.lstrip()) != indent:
                continue
            if text.strip().startswith("} else {"):
                middle = pos
            elif middle is not None and text.strip().startswith("}"):
                end = pos
                break
        if middle is not None and end is not None:
            left, right = "\n".join(lines[start:middle]), "\n".join(lines[middle:end])
            if "tt.load" not in left and "tt.load" in right and "i32" in right:
                return dict(pass_=True, line=start + 1, region="\n".join(lines[start:end + 1]))
    raise RuntimeError("实际 TTGIR 未保留无页表 load 的 affine 分支，停止计时")


def worker(run, model):
    result = dict(status="started", kind="真实 kernel 组件，非服务/模型准确率资格", cases=[],
                  model_gate="仅 affine+Q 与 affine+nextK+Q 组件对照，不继承服务/准确率资格")
    manager = affine_manager = baseline_manager = capture = None
    try:
        import torch
        import vllm_fl  # 先完成实际插件的 Torch dtype 兼容。
        from vllm.config import CompilationConfig, CUDAGraphMode, set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        config = EngineArgs(model=str(model), served_model_name=["minicpm"],
            gpu_memory_utilization=0.85, max_model_len=131072,
            compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        text = config.model_config.hf_text_config
        if (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
                text.num_attention_heads, text.num_key_value_heads) != (2048, 6144, 42, 16, 2):
            raise RuntimeError("不是固定 MiniCPM5-2B dense GQA 结构")
        if config.model_config.dtype != torch.bfloat16 or model.name != "MiniCPM5-2B":
            raise RuntimeError("模型/dtype 不符")
        with set_current_vllm_config(config):
            import distributed_bootstrap
            distributed_bootstrap.initialize(config, run)
            from vllm_fl.ops.custom_ops import register_oot_ops
            from dispatch_bootstrap import enable_dispatch
            register_oot_ops()
            result["dispatch"] = enable_dispatch(torch, run)
            importlib.import_module("vllm_fl.worker.model_runner")
            native = importlib.import_module("vllm_fl.patches.biv150_native_w8a8")
            result["native_install"] = native.install()
        if not result["native_install"].get("installed"):
            raise RuntimeError("两臂共同 native 安装链不符")
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        qmod = importlib.import_module("vllm_fl.patches.biv150_q_fragment_service")
        baseline_manager = qmod._MANAGER
        if baseline_manager is None or not baseline_manager.active:
            raise RuntimeError("当前 main Q-hoist 未自然安装")
        flaggems = importlib.import_module("flag_gems")
        result["flaggems"] = dict(path=str(flaggems.__file__), sha256=digest(Path(flaggems.__file__)))
        if torch.cuda.device_count() != 1:
            raise RuntimeError("非单卡")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("不是 BI-V150 16 SM")
        result["device"] = str(props)
        torch.manual_seed(721502)
        _, affine_source = prototype.sources(attention.__file__)
        source = next_k.transform(affine_source)
        jit = importlib.import_module("triton.runtime.jit")
        def private_manager(kernel_source):
            raw = prototype.instantiate(attention, kernel_source)
            cloned = jit.JITFunction(raw.fn, version=raw.version,
                do_not_specialize=list(raw.do_not_specialize),
                do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
                debug=raw.debug, noinline=raw.noinline, repr=raw._repr, launch_metadata=raw.launch_metadata)
            holder = {"kernel": raw}
            return qmod.Manager(attention, backend, holder, "kernel", raw, cloned).install()
        affine_manager = private_manager(affine_source)
        manager = private_manager(source)
        (run / "baseline.kernel.py").write_text(affine_source)
        (run / "candidate.kernel.py").write_text(source)
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5,
            num_kv_heads=2, alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
            attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        lengths = [1] * 29 + [2019]
        baseline_launch = baseline_manager.wrapper
        for kv_len in (16384,):
            common, query, key, value, cache = make_data(torch, lengths, kv_len)
            query[2048:] = float("nan")
            pages = kv_len // 16
            rows = [list(range(i * pages, (i + 1) * pages)) for i in range(30)]
            # 真实 page16，保留官方模型最大长度对应的页表容量和 stride。
            table_cpu = torch.zeros((30, 8192), dtype=torch.int32)
            table_cpu[:, :pages] = torch.tensor(rows, dtype=torch.int32)
            common.block_table_tensor = table_cpu.cuda()
            metadata = builder.build(0, common)
            impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
            observer = capture = Capture(baseline_launch)
            baseline_manager.holder[baseline_manager.kernel_key] = capture
            output = torch.full_like(query, -17)
            impl.forward(layer, query, key, value, cache, metadata, output)
            baseline_manager.holder[baseline_manager.kernel_key] = baseline_launch
            capture = None
            if len(observer.records) != 1:
                raise RuntimeError("没有捕获唯一 P2019 真实 2D ABI")
            grid, kwargs, compiled_a = observer.records[0]
            if kwargs["query_ptr"].shape != (2019, 16, 128) or not qmod._eligible(kwargs):
                raise RuntimeError("捕获的不是 main 当前受控 P2019/BM128/T64/w8s1")
            if kwargs["block_table_stride"] != 8192:
                raise RuntimeError("实际页表 stride 不是 8192")
            # main 原核只用于捕获真实 C3 ABI；计时基准是已受测 affine+Q。
            arm_info = {}
            desc_cpu = torch.empty((1, 3), dtype=torch.int32, pin_memory=True)
            desc_gpu = torch.empty_like(desc_cpu, device="cuda")
            out_a = torch.full((2022, 16, 128), -17, dtype=torch.bfloat16, device="cuda")
            out_b = torch.full_like(out_a, -17)
            kw_a = dict(kwargs, output_ptr=out_a[:2019], affine_pages_ptr=desc_gpu)
            kw_b = dict(kwargs, output_ptr=out_b[:2019], affine_pages_ptr=desc_gpu)
            call_a = lambda: affine_manager.wrapper[grid](**kw_a)
            call_b = lambda: manager.wrapper[grid](**kw_b)
            for layout in ("continuous",):
                row = list(rows[-1])
                if layout != "continuous":
                    row[:8] = row[:8][::-1]
                    row[-8:] = row[-8:][::-1]
                rows[-1] = row
                common.block_table_tensor[-1, :pages].copy_(torch.tensor(row, dtype=torch.int32))
                slots = [rows[r][pos // 16] * 16 + pos % 16
                    for r, length in enumerate(lengths) for pos in range(kv_len - length, kv_len)]
                common.slot_mapping.copy_(torch.tensor(slots, dtype=torch.int64, device="cuda"))
                impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
                plan_args = (["prefill"], [2019], [kv_len], [row], 1)
                bound = prototype.plan(*plan_args)
                desc_cpu.copy_(torch.tensor(bound.descriptors, dtype=torch.int32))
                desc_gpu.copy_(desc_cpu, non_blocking=True)
                cache_before = cache.clone()
                rng_cpu, rng_gpu = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
                a_before, b_before = affine_manager.selected_calls, manager.selected_calls
                compiled_a = call_a(); compiled_b = call_b()
                dump(compiled_a, run / f"ir-{kv_len}-baseline")
                dump(compiled_b, run / f"ir-{kv_len}-candidate")
                torch.cuda.synchronize()
                checks = dict(bits=torch.equal(out_a.view(torch.int16), out_b.view(torch.int16)),
                    finite=bool(torch.isfinite(out_b[:2019]).all()),
                    guard=bool((out_b[2019:] == -17).all()),
                    kv_unchanged=torch.equal(cache_before.view(torch.int16), cache.view(torch.int16)),
                    rng_unchanged=torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state()),
                    both_q_hoisted=affine_manager.selected_calls == a_before + 1 and manager.selected_calls == b_before + 1)
                case = dict(kv_len=kv_len, P=2019, M=2048, layout=layout, descriptor=bound.descriptors,
                            checks=checks, timings=[], candidate_resources=qmod._resources(compiled_b))
                result["cases"].append(case)
                if not all(checks.values()):
                    raise RuntimeError("组件数值或 scope 失败：" + repr(checks))
                if layout == "continuous":
                    arm_info["baseline"] = preserve(compiled_a, run / f"ir-{kv_len}-baseline", qmod,
                                                    affine_manager.candidate, attention)
                    arm_info["candidate"] = preserve(compiled_b, run / f"ir-{kv_len}-candidate", qmod,
                                                     manager.candidate, attention)
                    arm_info["conditional_lookup"] = conditional_lookup(compiled_b.asm["ttgir"])
                    case["ir"] = arm_info
                    # 在编译后 gate 可能拒绝前保存两臂真实资源和原件，不丢失败。
                    arm_info["machine_resources"] = {
                        "baseline": next_k.resource_fields(compiled_a),
                        "candidate": next_k.resource_fields(compiled_b)}
                    write(run / "results.json", result)
                    machine = arm_info["machine_resources"]
                    ares, bres = machine["baseline"], machine["candidate"]
                    cost_fields = ("shared", "private_segment_fixed_size", "vgpr_count",
                                   "vgpr_spill_count", "sgpr_count", "sgpr_spill_count")
                    arm_info["resource_cost"] = dict(
                        delta={name: bres[name] - ares[name] for name in cost_fields},
                        static_resources_are_not_performance_gate=True,
                        actual_occupancy_proven=False)
                    arm_info["next_k"] = next_k.mechanism(compiled_b.asm["ttgir"], compiled_b.asm["asm"], source)
                case["ir"] = arm_info
                # 同一已编译 JIT 及同一 GPU 页表指针，改当前旧 KV 页号后重建 descriptor。
                # 这验证重新提交，不声称 CUDA Graph replay 生命周期已通过。
                old_output = out_a.clone()
                changed_row = row.copy()
                changed_row[0], changed_row[2] = changed_row[2], changed_row[0]
                if bound.matches(["prefill"], [2019], [kv_len], [changed_row], 2):
                    raise RuntimeError("旧 CPU 计划误接受换页")
                common.block_table_tensor[-1, :pages].copy_(torch.tensor(changed_row, dtype=torch.int32))
                replay_plan = prototype.plan(["prefill"], [2019], [kv_len], [changed_row], 2)
                desc_cpu.copy_(torch.tensor(replay_plan.descriptors, dtype=torch.int32))
                desc_gpu.copy_(desc_cpu, non_blocking=True)
                call_a(); call_b(); torch.cuda.synchronize()
                case["changed_page_resubmit"] = dict(bits=torch.equal(out_a.view(torch.int16), out_b.view(torch.int16)),
                    data_changed=not torch.equal(old_output[:2019].view(torch.int16), out_a[:2019].view(torch.int16)),
                    kv_unchanged=torch.equal(cache_before.view(torch.int16), cache.view(torch.int16)),
                    guard=bool((out_b[2019:] == -17).all()))
                if not all(case["changed_page_resubmit"].values()):
                    raise RuntimeError("换页重新提交未通过")
                common.block_table_tensor[-1, :pages].copy_(torch.tensor(row, dtype=torch.int32))
                desc_cpu.copy_(torch.tensor(bound.descriptors, dtype=torch.int32))
                desc_gpu.copy_(desc_cpu, non_blocking=True)
                call_a(); call_b(); torch.cuda.synchronize()
                cpu_samples = []
                for _ in range(16):
                    begin = time.perf_counter_ns()
                    plan_now = prototype.plan(*plan_args)
                    desc_cpu.copy_(torch.tensor(plan_now.descriptors, dtype=torch.int32))
                    cpu_samples.append((time.perf_counter_ns() - begin) / 1e6)
                pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(5)]
                for start, end in pairs:
                    start.record(); end.record()
                torch.cuda.synchronize()
                h2d = timed_batch(torch, lambda: desc_gpu.copy_(desc_cpu, non_blocking=True), pairs[0], 32)
                database = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
                database_before = digest(database)
                for arm, events in zip(("baseline", "candidate", "candidate", "baseline"), pairs[1:]):
                    record = timed_batch(torch, call_a if arm == "baseline" else call_b, events, 16)
                    record["arm"] = arm
                    case["timings"].append(record)
                    write(run / "results.json", result)
                case["database_unchanged_during_ABBA"] = digest(database) == database_before
                if not case["database_unchanged_during_ABBA"]:
                    raise RuntimeError("计时期间共同 FlagGems DB 变化")
                case["descriptor_cost"] = dict(cpu_plan_and_pinned_fill_ms=cpu_samples,
                    h2d=h2d, scope="一次/批，42层共享；H2D单独串行测量，不声称生产能完全重叠")
                summary = {}
                for metric in ("event", "wall"):
                    a = statistics.median(x[metric + "_per_call_ms"] for x in case["timings"] if x["arm"] == "baseline")
                    b = statistics.median(x[metric + "_per_call_ms"] for x in case["timings"] if x["arm"] == "candidate")
                    cost = 0  # 两臂同一 descriptor；此成本是共同项，无 next-K 增量。
                    summary[metric] = dict(baseline_ms=a, candidate_ms=b, fraction_saved=1 - b / a,
                                          amortized_42_layer_net_ms=42 * (a - b) - cost)
                case["summary"] = summary
                write(run / "results.json", result)
                if layout == "continuous" and summary["event"]["amortized_42_layer_net_ms"] <= 0:
                    result.update(status="component_signal_only", decision="最有利连续页 next-K 无正信号，停止；不接服务")
                    return 0
                del cache_before
            del cache, query, key, value
        result.update(status="component_signal_only", decision="仅 next-K 组件信号；真实驻留/其他形状/模型正确性未验证，不自动接服务")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if capture is not None and baseline_manager is not None:
            baseline_manager.holder[baseline_manager.kernel_key] = baseline_manager.wrapper
        if manager is not None:
            result["candidate_manager"] = manager.snapshot()
            manager.restore()
        if affine_manager is not None:
            result["affine_baseline_manager"] = affine_manager.snapshot()
            affine_manager.restore()
        write(run / "results.json", result)
    return 0 if result["status"] == "component_signal_only" else 1
