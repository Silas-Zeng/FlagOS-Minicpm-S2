"""一个真实 M2047/KV16K 分页 Attention 三臂组件；只由设备 owner 启动。"""
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

ORIGINAL_SHA = "eef0202e6c0ed08bef8098adede1a603c63354c54b54a19414e210b675157265"
M, KV, D = 2047, 16384, 128
ARMS = ("current", "flaggems_original", "page16_rows_n64")
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


def fg_arguments(torch, q, k, v, out, common):
    # 与原 flash_api.py:mha_varlen_fwd 的实际 paged 分支逐项对应。
    return dict(q_ptr=q, k_ptr=k.view(k.shape[0], 16, -1), v_ptr=v.view(v.shape[0], 16, -1),
        o_ptr=out[:M], p_ptr=torch.empty((), device="cuda"),
        softmax_lse_ptr=torch.empty((16, M), dtype=torch.float32, device="cuda"),
        q_row_stride=q.stride(0), k_row_stride=k.stride(1), v_row_stride=v.stride(1),
        q_head_stride=q.stride(1), k_head_stride=k.stride(2), v_head_stride=v.stride(2),
        o_row_stride=out.stride(0), o_head_stride=out.stride(1),
        q_batch_stride=0, k_batch_stride=0, v_batch_stride=0, o_batch_stride=0,
        is_cu_seqlens_q=True, cu_seqlens_q_ptr=common.query_start_loc,
        is_cu_seqlens_k=False, cu_seqlens_k_ptr=None,
        is_seqused_k=True, seqused_k_ptr=common.seq_lens,
        b=1, bk=1, h=16, hk=2, h_hk_ratio=8,
        seqlen_q=M, seqlen_k=KV, seqlen_q_rounded=2048, seqlen_k_rounded=KV,
        d=D, d_rounded=D, is_softcap=False, softcap=0.0,
        scale_softmax=D ** -0.5, scale_softmax_log2=(D ** -0.5) * 1.4426950408889634074,
        is_dropout=False, p_dropout=1.0, rp_dropout=1.0, p_dropout_in_uint8_t=255,
        philox_args=torch.empty((2,), dtype=torch.int64, device="cuda"), return_softmax=False,
        is_causal=True, is_local=False, window_size_left=-1, window_size_right=0,
        seqlenq_ngroups_swapped=False, is_paged=True, is_alibi=False,
        alibi_slopes_ptr=None, alibi_slopes_batch_stride=0, total_q=M,
        page_table_ptr=common.block_table_tensor, page_table_batch_stride=8192,
        block_size=16, k_page_stride=k.stride(0))


def writer_exact(torch, key, value, k, v, slots):
    import numpy as np
    slot = slots.detach().cpu().numpy().astype(np.int64)
    def bits(x):
        return x.detach().cpu().view(torch.int16).numpy()
    return dict(key=bool(np.array_equal(bits(k)[slot // 16, slot % 16], bits(key[:M]))),
                value=bool(np.array_equal(bits(v)[slot // 16, slot % 16], bits(value[:M]))))


def worker(run, model):
    run = Path(run)
    result = dict(status="started", kind="真实三臂 kernel 组件；无模型权重/官方性能结论",
        shape=dict(M=M, KV=KV, Q_heads=16, KV_heads=2, D=D, page=16, page_table_stride=8192),
        candidate="FlagGems head-major：新 page16 行式 load＋N64；两个变化合并计为一个方法",
        limitations=["只有一个合成形状；不是实际模型输出或完整官方基线。",
            "原库/候选逆序分块与当前归约顺序不同，BF16 不要求跨臂逐位相同。",
            "计时包括各臂实际 launch wrapper 与 LSE 写出；固定共同写KV/metadata成本未计入差额。",
            "全臂同一输入缓存/进程；不声称省了8倍KV，M2047均约256 CTA。"],
        timings=[], ir={})
    manager = capture = None
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
        original = importlib.import_module("flag_gems.ops.flash_kernel")
        require(digest(Path(original.__file__)) == ORIGINAL_SHA, "安装版原 FlagGems kernel 不是固定 v5.3.5 原件")
        result["flaggems_original"] = dict(path=original.__file__, sha256=ORIGINAL_SHA,
            upstream="https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/ops/flash_kernel.py",
            git_blob="134075b148126a010734e49effedc554da801b68")
        spec = importlib.util.spec_from_file_location("head_major_candidate", Path(__file__).with_name("flash_kernel_candidate.py"))
        candidate = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = candidate
        spec.loader.exec_module(candidate)
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
        require(tuple(k.shape) == (1024, 16, 2, 128) and k.shape == v.shape, "实际 KV shape 不符")
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
        kw_b = fg_arguments(torch, q, k, v, outputs["flaggems_original"], common)
        kw_c = fg_arguments(torch, q, k, v, outputs["page16_rows_n64"], common)
        # 固定原库 heuristic 身份，不选择或调优另一个已有 backend。
        cfg = original.runtime.get_heuristic_config("mha_block_128")
        actual_cfg = {name: cfg[name](()) for name in ("BLOCK_M", "BLOCK_N", "num_warps", "num_stages")}
        require(actual_cfg == dict(BLOCK_M=128, BLOCK_N=32, num_warps=4, num_stages=3), "原库配置已变化")
        kw_b.update(actual_cfg, BLOCK_K=128)
        kw_c.update(actual_cfg, BLOCK_K=128)
        kw_c["BLOCK_N"] = 64
        fg_grid = (math.ceil(M / 128), 1, 16)
        calls = dict(current=lambda: manager.wrapper[grid](**kw_a),
            flaggems_original=lambda: original.flash_varlen_fwd_kernel[fg_grid](**kw_b),
            page16_rows_n64=lambda: candidate.flash_varlen_fwd_kernel[fg_grid](**kw_c))
        result["configs"] = dict(current=dict(BLOCK_M=128, BLOCK_Q=16, TILE_SIZE=64, num_warps=8, num_stages=1),
            flaggems_original={**actual_cfg, "BLOCK_K": 128},
            page16_rows_n64={**actual_cfg, "BLOCK_K": 128, "BLOCK_N": 64})
        result["ir"]["current"] = preserve(current_compiled, run / "ir-current", qmod)
        # 原库若有已预见的编译限制，保存原异常，不修改原件或制造修复臂。
        # 仅编译错误可继续独立候选；设备运行错误仍立刻停止。
        from triton.compiler.errors import CompilationError
        active_arms = list(ARMS)
        for name in ("flaggems_original", "page16_rows_n64"):
            result["compiling_arm"] = name
            write(run / "results.json", result)
            try:
                compiled = calls[name]()
            except CompilationError:
                if name != "flaggems_original":
                    raise
                result["original_unmeasurable"] = dict(status="upstream_compile_error", error=traceback.format_exc(),
                    conclusion="仅原库臂不可测；不得声称相对原FlagGems收益，不改其原件")
                (run / "flaggems-original-compile-error.txt").write_text(traceback.format_exc(), encoding="utf-8")
                active_arms.remove(name)
                del outputs[name]
                continue
            result["ir"][name] = preserve(compiled, run / ("ir-" + name), qmod)
        calls["current"]()
        torch.cuda.synchronize()
        result.pop("compiling_arm", None)
        result["active_arms"] = active_arms
        require(torch.equal(cache_before.view(torch.int16), cache.view(torch.int16))
                and torch.equal(q_before.view(torch.int16), query.view(torch.int16))
                and torch.equal(key_before.view(torch.int16), key.view(torch.int16))
                and torch.equal(value_before.view(torch.int16), value.view(torch.int16)), "首次编译/读取修改输入")
        result["initial_oracle"] = sampled_oracle(torch, run, "initial", query, k, v, common.block_table_tensor, outputs)
        torch.save({name: out.cpu() for name, out in outputs.items()}, run / "outputs-initial.pt")
        result["initial_sanity"] = {name: dict(finite=bool(torch.isfinite(out[:M]).all()),
            guard=bool((out[M:] == -17).all())) for name, out in outputs.items()}
        require(all(all(check.values()) for check in result["initial_sanity"].values()), "初始输出 finite/guard 未通过")
        require(all(x["passed"] for x in result["initial_oracle"]["arms"].values()), "初始独立 FP64 门未通过")
        initial = {name: out.clone() for name, out in outputs.items()}
        graphs = {}
        for name in active_arms:
            calls[name](); calls[name]()
            torch.cuda.synchronize()
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                calls[name]()
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
        require(all(x["passed"] for x in result["changed_oracle"]["arms"].values()), "换值独立 FP64 门未通过")
        result["read_only_checks"] = dict(kv=torch.equal(cache_before.view(torch.int16), cache.view(torch.int16)),
            query=torch.equal(q_before.view(torch.int16), query.view(torch.int16)),
            key=torch.equal(key_before.view(torch.int16), key.view(torch.int16)),
            value=torch.equal(value_before.view(torch.int16), value.view(torch.int16)),
            rng=torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state()),
            guards=all(bool((x[M:] == -17).all()) for x in outputs.values()))
        require(all(result["read_only_checks"].values()), "读取改变输入/RNG或越过输出guard")
        # 原始N32/current、候选N64/current分别ABBA；无拷贝/转置大tensor的隐藏步骤。
        groups = [("candidate", "page16_rows_n64")]
        if "flaggems_original" in active_arms:
            groups.insert(0, ("original", "flaggems_original"))
        order = [(group, name) for group, arm in groups for name in ("current", arm, arm, "current")]
        pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in order]
        for start, end in pairs:
            start.record(); end.record()
        torch.cuda.synchronize()
        database = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
        db_before = digest(database)
        for (group, name), pair in zip(order, pairs):
            rec = timed_batch(torch, calls[name], pair, 16)
            rec.update(arm=name, pair=group)
            result["timings"].append(rec)
            write(run / "results.json", result)
        result["database_unchanged_during_ABBA"] = digest(database) == db_before
        require(result["database_unchanged_during_ABBA"], "三臂计时期间共同DB变化")
        result["summary"] = {}
        for group, arm in groups:
            result["summary"][group] = {}
            rows = [r for r in result["timings"] if r["pair"] == group]
            for metric in ("event", "wall"):
                a = statistics.median(r[metric + "_per_call_ms"] for r in rows if r["arm"] == "current")
                b = statistics.median(r[metric + "_per_call_ms"] for r in rows if r["arm"] == arm)
                result["summary"][group][metric] = dict(current_ms=a, other_ms=b, fraction_saved=1-b/a)
        result.update(status="component_only_passed", decision="组件信号；是否进入模型集成由root按数值、资源、原库与当前双重差额决定")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if capture is not None and manager is not None:
            manager.holder[manager.kernel_key] = manager.wrapper
        write(run / "results.json", result)
    return 0 if result["status"] == "component_only_passed" else 1
