"""真实 N33/bucket40/S16 热点及原 B32/S4；每次独立组件，无模型激活或官方成绩。"""
from __future__ import annotations
import importlib
import json
from pathlib import Path
import re
import statistics
import traceback
from types import SimpleNamespace as NS

from legacy_gate import timed_batch
from validate_hidden_row_gather import digest, load, write
from validate_mixed_decode import make_data

SOURCE_SHA = "2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1"
HERE = Path(__file__).resolve().parent


class Capture:
    def __init__(self, original):
        self.original, self.records = original, []

    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            if args:
                raise RuntimeError("要求真实 keyword ABI")
            compiled = self.original[grid](**kwargs)
            self.records.append((grid, dict(kwargs), compiled))
            return compiled
        return launch


def dump(compiled, folder):
    folder.mkdir(exist_ok=False)
    for name, value in compiled.asm.items():
        if isinstance(value, (str, bytes)):
            (folder / (name + (".txt" if isinstance(value, str) else ".bin"))).write_bytes(
                value.encode() if isinstance(value, str) else value)
    assembly = compiled.asm.get("asm", "")
    fields = {}
    for name in ("sgpr_count", "sgpr_spill_count", "vgpr_count", "vgpr_spill_count", "private_segment_fixed_size"):
        found = re.findall(r"\." + name + r":\s*(\d+)", assembly)
        fields[name] = int(found[0]) if len(found) == 1 else None
    meta = compiled.metadata
    fields.update(shared=meta.get("shared") if isinstance(meta, dict) else meta.shared,
                  compiled_hash=getattr(compiled, "hash", None),
                  actual_occupancy_proven=False)
    return fields


from cache_policy import cache_evidence


def worker(run, model, shape="hotspot"):
    result = dict(status="started", kind="生产 kernel+reducer 的随机输入组件", checks=[], timings=[],
                  limitations=["没有模型权重或实际激活采样；不是模型资格或官方收益",
                               "默认 N33/bucket40/S16，可显式选择原 B32/S4；split 由实际生产路由选择",
                               "性能仅关闭 profiler 的同输入 CUDA Graph ABBA"])
    gqa = producer_capture = reducer_capture = None
    original_producer = original_reducer = None
    try:
        import torch
        import vllm_fl
        from vllm.config import CompilationConfig, CUDAGraphMode, set_current_vllm_config
        from vllm.engine.arg_utils import EngineArgs
        from vllm.v1.kv_cache_interface import FullAttentionSpec
        config = EngineArgs(model=str(model), served_model_name=["minicpm"], gpu_memory_utilization=0.85,
            max_model_len=131072, compilation_config=CompilationConfig(
                cudagraph_mode=CUDAGraphMode.FULL_DECODE_ONLY)).create_engine_config()
        text = config.model_config.hf_text_config
        if (text.hidden_size, text.intermediate_size, text.num_hidden_layers,
                text.num_attention_heads, text.num_key_value_heads) != (2048, 6144, 42, 16, 2):
            raise RuntimeError("不是固定 MiniCPM5-2B dense GQA")
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
            raise RuntimeError("共同 native 安装链不符")
        gqa = importlib.import_module("vllm_fl.patches.biv150_gqa_decode")
        if digest(Path(gqa.__file__)) != SOURCE_SHA or digest(HERE / "baseline.py") != SOURCE_SHA:
            raise RuntimeError("实际 GQA 不是冻结 main526 原件")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        candidate = load("gqa_kv_cg_candidate", HERE / "candidate.py")
        if torch.cuda.device_count() != 1:
            raise RuntimeError("非单卡")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("不是 BI-V150 16 SM")
        result["device"] = str(props)
        result["source_sha256"] = dict(baseline=SOURCE_SHA, candidate=digest(HERE / "candidate.py"))
        torch.manual_seed(725013)
        if shape == "hotspot":
            B, active, segments = 40, 33, 16
        elif shape == "b32":
            B, active, segments = 32, 32, 4
        else:
            raise ValueError("未知 shape")
        L = 16384
        common, query, key, value, cache = make_data(torch, [1] * B, L)
        query[B:] = -17
        table = torch.zeros((B, 8192), dtype=torch.int32)
        table[:, :L // 16] = torch.arange(B * (L // 16), dtype=torch.int32).reshape(B, -1)
        common.block_table_tensor = table.cuda()
        if active < B:
            # Actual runner: query_start_loc tail=last real token, lengths=0,
            # null block=0 (reserved), slot=-1, padded request/token counts=B.
            cache = torch.cat((torch.zeros_like(cache[:1]), cache), dim=0)
            common.block_table_tensor[:active, :L // 16].add_(1)
            common.block_table_tensor[active:].zero_()
            common.seq_lens[active:].zero_()
            common.query_start_loc_cpu.clamp_(max=active)
            common.query_start_loc.copy_(common.query_start_loc_cpu)
            common.slot_mapping[:active].add_(16)
            common.slot_mapping[active:].fill_(-1)
        spec = FullAttentionSpec(block_size=16, num_kv_heads=2, head_size=128, dtype=torch.bfloat16)
        builder = backend.TritonAttentionMetadataBuilder(spec, ["synthetic.attn"], config, torch.device("cuda:0"))
        impl = backend.TritonAttentionImpl(num_heads=16, head_size=128, scale=128 ** -0.5,
            num_kv_heads=2, alibi_slopes=None, sliding_window=None, kv_cache_dtype="auto",
            attn_type=backend.AttentionType.DECODER)
        layer = NS(_q_scale=torch.ones((), device="cuda"), _k_scale=torch.ones((), device="cuda"),
                   _v_scale=torch.ones((), device="cuda"))
        metadata = builder.build(0, common)
        impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
        if active < B and not bool((cache[0] == 0).all()):
            raise RuntimeError("padded slot=-1 或 null block 保留语义失配")
        original_producer, original_reducer = gqa._gqa_decode_attention, gqa._reduce_partials
        producer_capture, reducer_capture = Capture(original_producer), Capture(original_reducer)
        gqa._gqa_decode_attention, gqa._reduce_partials = producer_capture, reducer_capture
        production_output = torch.full_like(query, -17)
        try:
            impl.forward(layer, query, key, value, cache, metadata, production_output)
        finally:
            gqa._gqa_decode_attention, gqa._reduce_partials = original_producer, original_reducer
        if len(producer_capture.records) != 1 or len(reducer_capture.records) != 1:
            raise RuntimeError("没有捕获唯一真实生产 GQA+reducer，禁止替代路由")
        grid, kwargs, production_compiled = producer_capture.records[0]
        rgrid, rkwargs, reducer_compiled = reducer_capture.records[0]
        if (tuple(grid), tuple(rgrid), kwargs["ROWS"], kwargs["SEGMENTS"], kwargs["HEAD_SIZE"],
                kwargs["PAGE_SIZE"], kwargs["block_table_stride"], kwargs["num_warps"], kwargs["num_stages"]) != (
                    (B, 2, segments), (B, 16), 8, segments, 128, 16, 8192, 1, 1):
            raise RuntimeError("实际生产 ABI 未自然选中该 bucket 的 split/page16/w1s1")
        result["abi"] = dict(shape=shape, active_requests=active, padded_bucket=B,
            grid=grid, reducer_grid=rgrid, builder_segments=metadata.num_par_softmax_segments,
            source_q_shape=list(kwargs["query_ptr"].shape), source_k_shape=list(kwargs["key_cache_ptr"].shape),
            source_k_stride=list(kwargs["key_cache_ptr"].stride()), block_table_stride=8192,
            rows=8, segments=segments, head_size=128, page_size=16, num_warps=1, num_stages=1,
            query_start_loc=common.query_start_loc_cpu.tolist(), seq_lens=common.seq_lens.cpu().tolist(),
            padded_slot_values=common.slot_mapping[active:].cpu().tolist())
        original_inputs = (query.clone(), cache.clone(), common.seq_lens.clone(), common.block_table_tensor.clone())
        arms = {}
        for name, kernel in (("baseline", original_producer), ("candidate", candidate._gqa_decode_attention)):
            out = torch.full_like(query, -17)
            partial = torch.full_like(metadata.softmax_segm_output, -17)
            maxima = torch.full_like(metadata.softmax_segm_max, -17)
            sums = torch.full_like(metadata.softmax_segm_expsum, -17)
            pk = dict(kwargs, segm_output_ptr=partial.narrow(2, 0, segments), segm_max_ptr=maxima.narrow(2, 0, segments),
                      segm_expsum_ptr=sums.narrow(2, 0, segments))
            rk = dict(rkwargs, output_ptr=out[:B], segm_output_ptr=pk["segm_output_ptr"],
                      segm_max_ptr=pk["segm_max_ptr"], segm_expsum_ptr=pk["segm_expsum_ptr"])
            def call(kernel=kernel, pk=pk, rk=rk):
                compiled = kernel[grid](**pk)
                original_reducer[rgrid](**rk)
                return compiled
            arms[name] = NS(call=call, out=out, partial=partial, maxima=maxima, sums=sums,
                            tensors=(out, partial, maxima, sums))
        first = {name: arm.call() for name, arm in arms.items()}
        torch.cuda.synchronize()
        result["resources"] = {name: dump(compiled, run / ("ir-" + name)) for name, compiled in first.items()}
        result["resources"]["production"] = dump(production_compiled, run / "ir-production")
        result["resources"]["reducer"] = dump(reducer_compiled, run / "ir-reducer")
        write(run / "results.json", result)
        same_bits = lambda a, b: torch.equal(a.view(torch.int16 if a.element_size() == 2 else torch.int32),
                                            b.view(torch.int16 if b.element_size() == 2 else torch.int32))
        if not same_bits(production_output, arms["baseline"].out):
            raise RuntimeError("捕获 ABI 重放不同于实际 backend 输出")
        # 只确认 .cg 落到机器访存指令；提示被忽略时不做计时。
        # 寄存器/shared 仅记录，不另增资源阈值。
        result["cache_policy"] = cache_evidence(first["baseline"].asm["asm"], first["candidate"].asm["asm"])
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            for arm in arms.values():
                arm.call()
        torch.cuda.current_stream().wait_stream(stream)
        for arm in arms.values():
            arm.graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(arm.graph, stream=stream):
                arm.call()
        torch.cuda.synchronize()

        def check(label, finite=True, changed=False):
            # 整份 KV/输入逐位和 RNG 门在计时外；失败也先保存响应与 partial。
            before = tuple(x.clone() for x in (query, cache, common.seq_lens, common.block_table_tensor))
            rng_cpu, rng_gpu = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
            for arm in arms.values():
                for tensor in arm.tensors:
                    tensor.fill_(-17)
                arm.call()
            torch.cuda.synchronize()
            a, b = arms["baseline"], arms["candidate"]
            expected = tuple(t.clone() for t in a.tensors)
            checks = dict(eager_bits=all(same_bits(x, y) for x, y in zip(a.tensors, b.tensors)),
                finite=(bool(torch.isfinite(b.out[:B]).all()) if finite else True),
                guard=bool((a.out[B:] == -17).all() and (b.out[B:] == -17).all()))
            if active < B:
                checks["padded_output_zero"] = all(bool((arm.out[active:B] == 0).all()) for arm in arms.values())
                checks["padded_partials_untouched"] = all(bool((t[active:B] == -17).all())
                    for arm in arms.values() for t in (arm.partial, arm.maxima, arm.sums))
            else:
                checks["padded_output_zero"] = True
                checks["padded_partials_untouched"] = True
            failed_eager = [t.cpu() for t in b.tensors] if not checks["eager_bits"] else None
            for arm in arms.values():
                for tensor in arm.tensors:
                    tensor.fill_(-17)
                arm.graph.replay()
            torch.cuda.synchronize()
            checks["graph_fresh_bits"] = all(same_bits(x, y) for arm in arms.values()
                for x, y in zip(expected, arm.tensors))
            checks["inputs_unchanged"] = all(same_bits(x, y) for x, y in zip(
                before, (query, cache, common.seq_lens, common.block_table_tensor)))
            checks["rng_unchanged"] = torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state())
            if changed:
                checks["output_changed"] = not same_bits(initial_output[:B], expected[0][:B])
            record = dict(case=label, checks=checks, nonfinite_diagnostic=not finite,
                          baseline_nan=int(torch.isnan(a.out[:B]).sum().item()),
                          candidate_nan=int(torch.isnan(b.out[:B]).sum().item()))
            result["checks"].append(record)
            torch.save({"baseline": [x.cpu() for x in expected], "candidate": [x.cpu() for x in b.tensors],
                        "failed_eager_candidate": failed_eager,
                        "seq_lens": common.seq_lens.cpu(), "query": query.cpu(),
                        "block_table": common.block_table_tensor.cpu()}, run / (label + ".pt"))
            write(run / "results.json", result)
            if not all(checks.values()):
                torch.save(cache.cpu(), run / (label + "-failed-kv.pt"))
                raise RuntimeError("新增数值/Graph 边界失败：" + label + repr(checks))
            return expected[0]

        initial_output = check("dense-random")
        query[:B].neg_()
        # row15 remains long in the ragged pattern; mutate pages it actually reads.
        changed_row = 15
        changed_page = changed_row * (L // 16) + (1 if active < B else 0)
        cache[changed_page, 1].add_(0.5)
        common.block_table_tensor[changed_row, :2].copy_(common.block_table_tensor[changed_row, :2].flip(0))
        ragged_pattern = [0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65, 4095, 4096, 4097, 16383, 16384]
        ragged = [ragged_pattern[i % len(ragged_pattern)] for i in range(active)] + [0] * (B - active)
        common.seq_lens.copy_(torch.tensor(ragged, dtype=torch.int32, device="cuda"))
        check("graph-changed-q-kv-pages-ragged-zero-tail", changed=True)
        # 按既定 split 造首页/三页/尾页边界，S16 也覆盖多个完整页与尾页。
        # B32/S4 的模式仍为原来的 0/1/15/16/17/64/160/163。
        boundary = [0, 1, 15, 16, 17, segments * 16, segments * 48 - 32, segments * 48 - 29]
        common.seq_lens.copy_(torch.tensor([boundary[i % 8] for i in range(active)] + [0] * (B - active),
                                           dtype=torch.int32, device="cuda"))
        query[:B].zero_()
        cache.zero_()
        cache[:, 1].fill_(-0.0)
        check("finite-equal-max-negative-zero-v")
        tiny = torch.tensor([2.0 ** -133, -(2.0 ** -133), 2.0 ** -126, -(2.0 ** -126)],
                            dtype=torch.bfloat16, device="cuda")
        cache[:, 1].copy_(tiny.repeat(32).reshape(1, 1, 1, 128).expand_as(cache[:, 1]))
        check("finite-equal-max-subnormal-cancellation-v")
        cache[:, 1].fill_(float("nan"))
        cache[:, 1, :, :, 0].fill_(float("inf"))
        cache[:, 1, :, :, 1].fill_(float("-inf"))
        check("finite-max-nonfinite-accumulator", finite=False)
        cache[:, 1].fill_(1.0)
        query[:B].fill_(1.0)
        cache[:, 0].fill_(float("-inf"))
        check("negative-infinity-max-original-path", finite=False)
        cache[:, 0].fill_(float("inf"))
        check("positive-infinity-max-original-path", finite=False)

        for target, saved in zip((query, cache, common.seq_lens, common.block_table_tensor), original_inputs):
            target.copy_(saved)
        check("restored-dense-before-ABBA")
        for arm in arms.values():
            arm.graph.replay()
        pairs = [(torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)) for _ in range(4)]
        for start, end in pairs:
            start.record(); end.record()
        torch.cuda.synchronize()
        database = Path("/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db")
        database_before = digest(database)
        for name, events in zip(("baseline", "candidate", "candidate", "baseline"), pairs):
            timing = timed_batch(torch, arms[name].graph.replay, events, 16)
            timing["arm"] = name
            result["timings"].append(timing)
            write(run / "results.json", result)
        result["database_unchanged_during_ABBA"] = digest(database) == database_before
        if not result["database_unchanged_during_ABBA"]:
            raise RuntimeError("共同 DB 在计时期间变化")
        result["summary"] = {}
        for metric in ("event", "wall"):
            a = statistics.median(x[metric + "_per_call_ms"] for x in result["timings"] if x["arm"] == "baseline")
            b = statistics.median(x[metric + "_per_call_ms"] for x in result["timings"] if x["arm"] == "candidate")
            result["summary"][metric] = dict(baseline_ms=a, candidate_ms=b, fraction_saved=1 - b / a)
        result.update(status="component_signal_only", decision="仅一组组件信号；不自动扩形状或模型，先由 root 判断真实收益")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if gqa is not None and original_producer is not None:
            gqa._gqa_decode_attention, gqa._reduce_partials = original_producer, original_reducer
        write(run / "results.json", result)
    return 0 if result["status"] == "component_signal_only" else 1
