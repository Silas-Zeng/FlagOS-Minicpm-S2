"""真实 M2047/KV16K normalized+Q-hoist 对 stride 同形状组件。"""
from __future__ import annotations
import importlib
import importlib.util
import math
from pathlib import Path
import re
import statistics
import sys
import traceback
from types import SimpleNamespace as NS

from legacy_gate import timed_batch
from validate_hidden_row_gather import digest, write
from validate_mixed_decode import make_data

import prototype
import alternate_stride
M, KV, D = 2047, 16384, 128
ARMS = ("current", "stride")
SAMPLE_ROWS = (0, 15, 16, 127, 128, 1023, 2046)
SAMPLE_HEADS = (0, 7, 8, 15)


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


class Capture:
    def __init__(self, original):
        self.original, self.records = original, []

    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            compiled = self.original[grid](*args, **kwargs)
            if kwargs.get("IS_3D") is False:
                require(not args, "当前真实 Attention 不是 keyword ABI")
                self.records.append((grid, dict(kwargs), compiled))
            return compiled
        return launch


def preserve(compiled, folder, qmod):
    if isinstance(compiled, tuple):
        compiled = compiled[0]  # 原 FlagGems LibEntry 返回 (kernel, constexprs)。
    folder.mkdir(exist_ok=False)
    for name, value in compiled.asm.items():
        if isinstance(value, (str, bytes)):
            (folder / (name + (".txt" if isinstance(value, str) else ".bin"))).write_bytes(
                value.encode() if isinstance(value, str) else value)
    assembly = compiled.asm.get("asm", "")
    private = re.search(r"workitem_private_segment_byte_size\s*=\s*(\d+)", assembly)
    return dict(resources=qmod._resources(compiled),
                private_bytes=None if private is None else int(private[1]))


def sampled_oracle(torch, run, label, query, key_cache, value_cache, table, outputs):
    """独立 NumPy FP64 dense causal 参考；直接按真实页号收集已写入的 KV。"""
    import numpy as np
    pages = table[0, :KV // 16].detach().cpu().numpy().astype(np.int64)
    # CPU numpy 索引与矩阵乘法，不调用任何待测 Attention/softmax/helper。
    q = query[:M].detach().float().cpu().numpy().astype(np.float64)
    k = key_cache.detach().float().cpu().numpy()[pages].reshape(KV, 2, D).astype(np.float64)
    v = value_cache.detach().float().cpu().numpy()[pages].reshape(KV, 2, D).astype(np.float64)
    ref = np.empty((len(SAMPLE_ROWS), len(SAMPLE_HEADS), D), dtype=np.float64)
    for ir, row in enumerate(SAMPLE_ROWS):
        end = KV - M + row + 1
        for ih, head in enumerate(SAMPLE_HEADS):
            scores = (k[:end, head // 8] @ q[row, head]) * D ** -0.5
            weights = np.exp(scores - scores.max())
            weights /= weights.sum()
            ref[ir, ih] = weights @ v[:end, head // 8]
    samples, stats = {}, {}
    for name, out in outputs.items():
        sample = out[:M].detach().float().cpu().numpy()[list(SAMPLE_ROWS)][:, list(SAMPLE_HEADS)]
        samples[name] = sample
        diff = sample.astype(np.float64) - ref
        max_abs = float(np.max(np.abs(diff)))
        relative_l2 = float(np.linalg.norm(diff) / max(np.linalg.norm(ref), 1e-30))
        stats[name] = dict(max_abs=max_abs, rms_abs=float(np.sqrt(np.mean(diff ** 2))),
            relative_l2=relative_l2, finite=bool(np.isfinite(sample).all()),
            passed=bool(np.isfinite(sample).all() and max_abs <= 5e-4 and relative_l2 <= 0.01))
    np.savez(run / (label + "-sampled-fp64.npz"), reference=ref, rows=SAMPLE_ROWS,
             heads=SAMPLE_HEADS, **samples)
    # 固定合成 BF16 组件门，不能代替实际模型正确率；不按观测值放宽。
    return dict(criteria="每臂 finite 且 max_abs≤5e-4、relative_l2≤0.01；仅本合成输入", arms=stats)


def writer_exact(torch, key, value, k, v, slots):
    import numpy as np
    slot = slots.detach().cpu().numpy().astype(np.int64)
    def bits(x):
        return x.detach().cpu().view(torch.int16).numpy()
    return dict(key=bool(np.array_equal(bits(k)[slot // 16, slot % 16], bits(key[:M]))),
                value=bool(np.array_equal(bits(v)[slot // 16, slot % 16], bits(value[:M]))))


def worker(run, model, case="long"):
    global M,KV,SAMPLE_ROWS
    M,KV=(2048,2048) if case=="causal" else (2047,16384)
    SAMPLE_ROWS=(0,15,16,127,128,1023,M-1)
    run = Path(run)
    result = dict(status="started", kind="真实同形状 prefill kernel 组件；无模型权重/官方性能结论",
        shape=dict(M=M, KV=KV, Q_heads=16, KV_heads=2, D=D, page=16, page_table_stride=8192),
        candidate="当前stride+Q-hoist仅反转序列内query block的CTA枚举；每个query的K顺序不变",
        limitations=["只有一个合成形状；不是实际模型输出或完整官方基线。",
            "仅stride特化；原浮点表达式不变，独立FP64及每臂Graph门复用。",
            "计时两臂直接已暖 Q-hoist 私有 JIT 的完整2D输出；共同writer/metadata不计差额。",
            "两臂同输入缓存/进程/ABI，既无affine/next-K，也不扩大tile或减少KV字节。"],
        timings=[], ir={})
    manager = capture = candidate_manager = None
    try:
        import torch
        import vllm_fl
        from vllm.config import CompilationConfig, CUDAGraphMode, set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        config = EngineArgs(model=str(model), served_model_name=["minicpm"],
            gpu_memory_utilization=0.85, max_model_len=131072,
            compilation_config=CompilationConfig(cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        text = config.model_config.hf_text_config
        require((text.hidden_size, text.intermediate_size, text.num_hidden_layers,
                 text.num_attention_heads, text.num_key_value_heads) == (2048, 6144, 42, 16, 2),
                "不是固定 MiniCPM5-2B dense GQA 结构")
        require(config.model_config.dtype == torch.bfloat16 and model.name == "MiniCPM5-2B", "模型/dtype 不符")
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
        require(result["native_install"].get("installed"), "共同受测 main526 安装链不符")
        attention = importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        qmod = importlib.import_module("vllm_fl.patches.biv150_q_fragment_service")
        manager = qmod._MANAGER
        require(manager is not None and manager.active, "当前 main Q-hoist 未自然安装")
        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        raw_stride, source_stride = prototype.build(attention, manager, helpers)
        original_source=__import__('inspect').getsource(manager.raw.fn)
        require(source_stride==prototype.transform(original_source),"实际候选不是固定CTA变换")
        candidate_manager = prototype.private_manager(raw_stride, attention, backend, qmod)
        (run / "candidate.kernel.py").write_text(source_stride, encoding="utf-8")
        import inspect
        (run / "current.kernel.py").write_text(inspect.getsource(manager.raw.fn), encoding="utf-8")
        require(torch.cuda.device_count() == 1, "非单卡")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        require("BI-V150" in props.name and props.multi_processor_count == 16, "不是 BI-V150 16 SM")
        result["device"] = str(props)
        torch.manual_seed(721502)
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=D, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=D, scale=D ** -0.5,
            num_kv_heads=2, alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
            attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        common, query, key, value, cache = make_data(torch, [M], KV)
        query[M:] = float("nan")
        page_ids = list(range(KV // 16))
        page_ids[:8] = reversed(page_ids[:8])
        table_cpu = torch.full((1, 8192), -1, dtype=torch.int32)
        table_cpu[0, :KV // 16] = torch.tensor(page_ids, dtype=torch.int32)
        common.block_table_tensor = table_cpu.cuda()
        common.slot_mapping.copy_(torch.tensor([page_ids[pos // 16] * 16 + pos % 16
            for pos in range(KV - M, KV)], dtype=torch.int64, device="cuda"))
        metadata = builder.build(0, common)
        impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
        cache_before, q_before = cache.clone(), query.clone()
        key_before, value_before = key.clone(), value.clone()
        rng_cpu, rng_gpu = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
        capture = Capture(manager.wrapper)
        manager.holder[manager.kernel_key] = capture
        initial_output = torch.full_like(query, -17)
        impl.forward(layer, query, key, value, cache, metadata, initial_output)
        manager.holder[manager.kernel_key] = manager.wrapper
        observer, capture = capture, None
        require(len(observer.records) == 1, "未捕获唯一真实 M2047 2D ABI")
        grid, current_kwargs, current_compiled = observer.records[0]
        require(current_kwargs["query_ptr"].shape == (M, 16, D) and qmod._eligible(current_kwargs),
                "实际 kernel 不是当前 normalized＋Q-fragment BM128/T64/w8s1")
        k, v = current_kwargs["key_cache_ptr"], current_kwargs["value_cache_ptr"]
        q = current_kwargs["query_ptr"]
        require(tuple(k.shape) == (KV//16, 16, 2, 128) and k.shape == v.shape, "实际 KV shape 不符")
        require(k.stride() == v.stride() == (8192, 256, 128, 1), "实际 packed NHD KV stride 不符")
        require(k.data_ptr() == cache.data_ptr() and v.data_ptr() == cache.data_ptr() + 4096 * 2,
                "K/V 地址不是实际交错缓存的两个 view")
        require(current_kwargs["block_table_stride"] == 8192, "当前实际页表 stride 不符")
        result["initial_writer_exact"] = writer_exact(torch, key, value, k, v, common.slot_mapping)
        require(all(result["initial_writer_exact"].values()), "原 writer 未完整写入 M2047 个 KV 行")
        result["actual_abi"] = {name: dict(shape=list(x.shape), stride=list(x.stride()),
            dtype=str(x.dtype), data_ptr=x.data_ptr(), storage_offset=x.storage_offset())
            for name, x in (("q", q), ("k", k), ("v", v), ("table", common.block_table_tensor))}
        # 保存确切输入/槽位/写后cache，所有下述核共享这一份内存。
        torch.save(dict(query=query.cpu(), key=key.cpu(), value=value.cpu(), cache=cache.cpu(),
            page_table=common.block_table_tensor.cpu(), slots=common.slot_mapping.cpu()), run / "inputs-initial.pt")
        outputs = {name: torch.full_like(query, -17) for name in ARMS}
        kw_a = dict(current_kwargs, output_ptr=outputs["current"][:M])
        kw_b = dict(current_kwargs, output_ptr=outputs["stride"][:M])
        require(qmod._eligible(kw_a) and qmod._eligible(kw_b), "不属于已限定普通causal/BF16无sink等scope")
        # 先由原私有编译链生成并证明两臂Q-hoist，再直接调用同一已暖JIT；
        # Graph capture不经外层wrapper的保守fallback，避免回放另一套内核。
        compiled_a = manager.wrapper[grid](**kw_a)
        compiled_b = candidate_manager.wrapper[grid](**kw_b)
        require(compiled_a.hash in manager.optimized and compiled_b.hash in candidate_manager.optimized,
                "两臂必须真实命中Q-hoist；不能带fallback进入对照")
        calls = dict(current=lambda: manager.candidate[grid](**kw_a),
                     stride=lambda: candidate_manager.candidate[grid](**kw_b))
        result["configs"] = {name: dict(BLOCK_M=128, BLOCK_Q=16, TILE_SIZE=64,
            num_warps=8, num_stages=1) for name in ARMS}
        result["ir"]["current"] = preserve(compiled_a, run / "ir-current", qmod)
        result["ir"]["stride"] = preserve(compiled_b, run / "ir-stride", qmod)
        result["q_hoist"] = {"current": manager.optimized[compiled_a.hash]["mechanism"],
            "stride": candidate_manager.optimized[compiled_b.hash]["mechanism"]}
        result["machine_diagnostic"] = {"current": prototype.machine_summary(compiled_a),
            "stride": prototype.machine_summary(compiled_b)}
        active_arms = list(ARMS)
        expected_hashes = {"current": compiled_a.hash, "stride": compiled_b.hash}
        for name in active_arms:
            require(calls[name]().hash == expected_hashes[name], "直接JIT没有复用已核编译产物")
        torch.cuda.synchronize()
        result["active_arms"] = active_arms
        result["specialized_stride_values"] = {name: current_kwargs[name] for name in prototype.STRIDES}
        require(torch.equal(cache_before.view(torch.int16), cache.view(torch.int16))
                and torch.equal(q_before.view(torch.int16), query.view(torch.int16))
                and torch.equal(key_before.view(torch.int16), key.view(torch.int16))
                and torch.equal(value_before.view(torch.int16), value.view(torch.int16)), "首次编译/读取修改输入")
        result["initial_oracle"] = sampled_oracle(torch, run, "initial", query, k, v, common.block_table_tensor, outputs)
        torch.save({name: out.cpu() for name, out in outputs.items()}, run / "outputs-initial.pt")
        result["initial_sanity"] = {name: dict(finite=bool(torch.isfinite(out[:M]).all()),
            guard=bool((out[M:] == -17).all())) for name, out in outputs.items()}
        require(all(all(check.values()) for check in result["initial_sanity"].values()), "初始输出 finite/guard 未通过")
        if case=="causal":
            # short causal首几行V可为O(1)，BF16输出舍入步长本就可能大于旧long-only的5e-4。
            # CTA映射只允许逐位等于已验证原生产核；不放宽/重写原FP64诊断中的passed。
            require(torch.equal(outputs["current"].view(torch.int16),outputs["stride"].view(torch.int16)),"causal调序未逐位保持原输出")
            result["initial_oracle_applicability"]={"contract":"exact production BF16 bits; original FP64 thresholds unchanged and diagnostic only for this short shape","fp64_pass_inherited":False,"baseline_and_candidate_max_abs":{k:v["max_abs"] for k,v in result["initial_oracle"]["arms"].items()}}
        else:
            require(all(x["passed"] for x in result["initial_oracle"]["arms"].values()), "初始独立 FP64 门未通过")
        require(torch.equal(initial_output[:M].view(torch.int16), outputs["current"][:M].view(torch.int16)),
                "新直接基准调用与原生产forward结果不一致")
        result["initial_cross_arm"] = dict(bitwise=torch.equal(outputs["current"][:M].view(torch.int16), outputs["stride"][:M].view(torch.int16)),
            max_abs=float((outputs["current"][:M].float()-outputs["stride"][:M].float()).abs().max()), diagnostic_only=True)
        require(result["initial_cross_arm"]["bitwise"],"CTA调序不应改变每个query的数值")
        initial = {name: out.clone() for name, out in outputs.items()}
        graphs = {}
        for name in active_arms:
            calls[name](); calls[name]()
            torch.cuda.synchronize()
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                captured = calls[name]()
            require(captured.hash == expected_hashes[name], "Graph capture使用了非指定Q-hoist产物")
            graphs[name] = graph
        torch.cuda.synchronize()
        require(torch.equal(cache_before.view(torch.int16), cache.view(torch.int16))
                and torch.equal(q_before.view(torch.int16), query.view(torch.int16)), "初始读取/Graph capture 改了输入")
        # 同地址变值：历史KV、当前Q/K/V及页表值都更新；仍用原 writer 写新KV。
        query[:M].mul_(-1)
        key.mul_(0.5)
        value.mul_(-1)
        cache.mul_(-0.5)
        page_ids[0], page_ids[2] = page_ids[2], page_ids[0]
        common.block_table_tensor[0, :KV // 16].copy_(torch.tensor(page_ids, dtype=torch.int32))
        impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
        result["changed_writer_exact"] = writer_exact(torch, key, value, k, v, common.slot_mapping)
        require(all(result["changed_writer_exact"].values()), "原 writer 换值后写槽不符")
        cache_before, q_before = cache.clone(), query.clone()
        key_before, value_before = key.clone(), value.clone()
        graph_checks = {}
        for name in active_arms:
            outputs[name].fill_(-17)
            graphs[name].replay()
            torch.cuda.synchronize()
            replay = outputs[name].clone()
            outputs[name].fill_(-17)
            calls[name]()
            torch.cuda.synchronize()
            graph_checks[name] = dict(replay_eager_bits=torch.equal(replay.view(torch.int16), outputs[name].view(torch.int16)),
                changed=not torch.equal(initial[name][:M].view(torch.int16), replay[:M].view(torch.int16)),
                finite=bool(torch.isfinite(replay[:M]).all()), guard=bool((replay[M:] == -17).all()))
        result["changed_input_graph"] = graph_checks
        require(all(all(x.values()) for x in graph_checks.values()), "换值 Graph/guard/finite 未通过")
        result["changed_oracle"] = sampled_oracle(torch, run, "changed", query, k, v, common.block_table_tensor, outputs)
        torch.save(dict(query=query.cpu(), key=key.cpu(), value=value.cpu(), cache=cache.cpu(),
            page_table=common.block_table_tensor.cpu(), slots=common.slot_mapping.cpu(),
            outputs={name: out.cpu() for name, out in outputs.items()}), run / "changed-inputs-outputs.pt")
        if case=="causal":
            # short causal首几行V可为O(1)，BF16输出舍入步长本就可能大于旧long-only的5e-4。
            # CTA映射只允许逐位等于已验证原生产核；不放宽/重写原FP64诊断中的passed。
            require(torch.equal(outputs["current"].view(torch.int16),outputs["stride"].view(torch.int16)),"causal调序未逐位保持原输出")
            result["changed_oracle_applicability"]={"contract":"exact production BF16 bits; original FP64 thresholds unchanged and diagnostic only for this short shape","fp64_pass_inherited":False,"baseline_and_candidate_max_abs":{k:v["max_abs"] for k,v in result["changed_oracle"]["arms"].items()}}
        else:
            require(all(x["passed"] for x in result["changed_oracle"]["arms"].values()), "换值独立 FP64 门未通过")
        result["changed_cross_arm"] = dict(bitwise=torch.equal(outputs["current"][:M].view(torch.int16), outputs["stride"][:M].view(torch.int16)),
            max_abs=float((outputs["current"][:M].float()-outputs["stride"][:M].float()).abs().max()), diagnostic_only=True)
        require(result["changed_cross_arm"]["bitwise"],"换值后CTA调序出现数值差异")
        result["read_only_checks"] = dict(kv=torch.equal(cache_before.view(torch.int16), cache.view(torch.int16)),
            query=torch.equal(q_before.view(torch.int16), query.view(torch.int16)),
            key=torch.equal(key_before.view(torch.int16), key.view(torch.int16)),
            value=torch.equal(value_before.view(torch.int16), value.view(torch.int16)),
            rng=torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state()),
            guards=all(bool((x[M:] == -17).all()) for x in outputs.values()))
        require(all(result["read_only_checks"].values()), "读取改变输入/RNG或越过输出guard")
        # 原同形状完整producer单ABBA；无独有的输入变换或计时外计算。
        groups = [("candidate", "stride")]
        order = [(group, name) for group, arm in groups for name in ("current", arm, arm, "current")]
        pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in order]
        for start, end in pairs:
            start.record(); end.record()
        torch.cuda.synchronize()
        database = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
        db_before = digest(database)
        for (group, name), pair in zip(order, pairs):
            rec = timed_batch(torch, graphs[name].replay, pair, 32)
            rec.update(arm=name, pair=group)
            result["timings"].append(rec)
            write(run / "results.json", result)
        result["database_unchanged_during_ABBA"] = digest(database) == db_before
        require(result["database_unchanged_during_ABBA"], "两臂计时期间共同DB变化")
        result["summary"] = {}
        for group, arm in groups:
            result["summary"][group] = {}
            rows = [r for r in result["timings"] if r["pair"] == group]
            for metric in ("event", "wall"):
                a = statistics.median(r[metric + "_per_call_ms"] for r in rows if r["arm"] == "current")
                b = statistics.median(r[metric + "_per_call_ms"] for r in rows if r["arm"] == arm)
                result["summary"][group][metric] = dict(current_ms=a, other_ms=b, fraction_saved=1-b/a)
        result["timing_scope"]="已构建完整Attention CUDA Graph replay ABBA；含device执行，不含Python JIT提交"
        result.update(status="component_only_passed", decision="组件信号；实际机器码仅诊断，净正才由root决定模型后继；负则收口")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if capture is not None and manager is not None:
            manager.holder[manager.kernel_key] = manager.wrapper
        if candidate_manager is not None:
            result["candidate_manager"] = candidate_manager.snapshot()
            candidate_manager.restore()
        write(run / "results.json", result)
    return 0 if result["status"] == "component_only_passed" else 1
