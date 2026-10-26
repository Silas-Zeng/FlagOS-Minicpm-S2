"""实际Graph N64/B64/S2热点；每次独立组件，无模型激活或官方成绩。"""
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
                  use_sme=meta.get("use_sme") if isinstance(meta, dict) else getattr(meta, "use_sme", None),
                  num_warps=meta.get("num_warps") if isinstance(meta, dict) else getattr(meta, "num_warps", None),
                  num_stages=meta.get("num_stages") if isinstance(meta, dict) else getattr(meta, "num_stages", None),
                  actual_occupancy_proven=False)
    return fields


from fp_reference import sampled_reference
from descriptor import prepare_launch_kwargs


def worker(run, model, shape="hotspot"):
    result = dict(status="started", kind="生产 kernel+reducer 的随机输入组件", checks=[], timings=[],
                  limitations=["没有模型权重或实际激活采样；不是模型资格或官方收益",
                               "仅N64/B64/S2；观测长度多重集、合成激活；page16/split/FP顺序保持，仅标量页基址拆分+原while/span",
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
            raise RuntimeError("实际 GQA 不是冻结 main6971/618 原件")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        candidate = load("gqa_scalar_page_base_candidate", HERE / "candidate.py")
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
            B, active, segments = 64, 64, 2
        else:
            raise ValueError("未知 shape")
        L = 16384
        common, query, key, value, cache = make_data(torch, [1] * B, L)
        query[B:] = -17
        table = torch.zeros((B, 8192), dtype=torch.int32)
        table[:, :L // 16] = torch.arange(B * (L // 16), dtype=torch.int32).reshape(B, -1)
        table[:, :L // 16] = table[:, :L // 16].reshape(B, -1, 4).flip(-1).reshape(B, -1)
        common.slot_mapping[:B] = table[:, L // 16 - 1].to("cuda", dtype=torch.int64) * 16 + 15
        common.block_table_tensor = table.cuda()
        timing_shape = json.loads((HERE / "timing-shape.json").read_text(encoding="utf-8"))
        timing_lengths = timing_shape["seq_lens"]
        if len(timing_lengths) != B or any(not (1 <= n <= L) for n in timing_lengths):
            raise RuntimeError("诊断长度多重集越界")
        common.seq_lens.copy_(torch.tensor(timing_lengths, dtype=torch.int32, device="cuda"))
        common.max_seq_len = max(timing_lengths)
        common.slot_mapping[:B] = torch.tensor([
            int(table[row, (length - 1) // 16]) * 16 + (length - 1) % 16
            for row, length in enumerate(timing_lengths)], dtype=torch.int64, device="cuda")
        result["timing_shape"] = timing_shape
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
            rows=8, segments=segments, head_size=128, page_size=16, candidate_compute_tile=16, num_warps=1, num_stages=1,
            query_start_loc=common.query_start_loc_cpu.tolist(), seq_lens=common.seq_lens.cpu().tolist(),
            padded_slot_values=common.slot_mapping[active:].cpu().tolist())
        original_inputs = (query.clone(), cache.clone(), common.seq_lens.clone(), common.block_table_tensor.clone())
        result["span_views"] = []
        arms = {}
        for name, kernel in (("baseline", original_producer), ("candidate", candidate._gqa_decode_attention_scalar_page_base)):
            out = torch.full_like(query, -17)
            partial = torch.full_like(metadata.softmax_segm_output, -17)
            maxima = torch.full_like(metadata.softmax_segm_max, -17)
            sums = torch.full_like(metadata.softmax_segm_expsum, -17)
            pk = dict(kwargs, segm_output_ptr=partial.narrow(2, 0, segments), segm_max_ptr=maxima.narrow(2, 0, segments),
                      segm_expsum_ptr=sums.narrow(2, 0, segments))
            keepalive = []
            if name == "candidate":
                pk, keepalive = prepare_launch_kwargs(pk)
                for pointer, view in zip(("key_cache_ptr", "value_cache_ptr"), keepalive):
                    logical = kwargs[pointer]
                    view_record = dict(pointer=pointer, original_shape=list(logical.shape),
                        original_stride=list(logical.stride()), backing_shape=list(view.shape),
                        storage_offset=logical.storage_offset(), span_elements=view.numel(),
                        storage_elements=logical.untyped_storage().nbytes() // logical.element_size(),
                        same_data_ptr=view.data_ptr() == logical.data_ptr(),
                        same_storage=view.untyped_storage().data_ptr() == logical.untyped_storage().data_ptr(),
                        contiguous=view.is_contiguous(),
                        within_storage=logical.storage_offset() + view.numel() <= logical.untyped_storage().nbytes() // logical.element_size())
                    if not all(view_record[k] for k in ("same_data_ptr", "same_storage", "contiguous", "within_storage")):
                        raise RuntimeError("非法backing view别名或storage尾界")
                    result["span_views"].append(view_record)
            rk = dict(rkwargs, output_ptr=out[:B], segm_output_ptr=pk["segm_output_ptr"],
                      segm_max_ptr=pk["segm_max_ptr"], segm_expsum_ptr=pk["segm_expsum_ptr"])
            def call(kernel=kernel, pk=pk, rk=rk, keepalive=keepalive):
                compiled = kernel[grid](**pk)
                original_reducer[rgrid](**rk)
                return compiled
            arms[name] = NS(call=call, out=out, partial=partial, maxima=maxima, sums=sums,
                            tensors=(out, partial, maxima, sums), keepalive=keepalive, pk_views=keepalive)
        first = {name: arm.call() for name, arm in arms.items()}
        torch.cuda.synchronize()
        result["resources"] = {name: dump(compiled, run / ("ir-" + name)) for name, compiled in first.items()}
        result["resources"]["production"] = dump(production_compiled, run / "ir-production")
        result["resources"]["reducer"] = dump(reducer_compiled, run / "ir-reducer")
        # Selection is diagnostic: a frontend mask is not proof of an SME copy.
        patterns = {"sme_transport": r"sme|g2s|global_to_shared|global.*shared|cp\.async",
                    "wait": r"waitcnt|wait_group|async_wait|wait_all|waitcnt_",
                    "barrier": r"barrier|s_barrier|syncthreads",
                    "shared_fragment": r"local_load|local_alloc|s2r|shared"}
        selection = dict(diagnostic_only=True, no_asm_selection_claim=True,
            expected_mask_delta_hex="0x30", masks={}, evidence={},
            note="生产N64/S2窄scratch预期14->62；mask不等于实际SME。须核scalar page-base是否保留、实际KV copy/wait与资源。")
        for arm_name, compiled in first.items():
            selection["masks"][arm_name] = result["resources"][arm_name]["use_sme"]
            selection["evidence"][arm_name] = {}
            for stage, raw in compiled.asm.items():
                if not isinstance(raw, (str, bytes)):
                    continue
                if isinstance(raw, bytes):
                    try:
                        raw = raw.decode("utf-8")
                    except UnicodeDecodeError:
                        continue
                lines = raw.splitlines()
                selection["evidence"][arm_name][stage] = {
                    kind: [dict(line=i + 1, text=line[:1000]) for i, line in enumerate(lines)
                           if re.search(pattern, line, re.IGNORECASE)][:256]
                    for kind, pattern in patterns.items()}
        a_mask, b_mask = (selection["masks"][name] for name in ("baseline", "candidate"))
        selection["mask_delta_matches"] = (a_mask ^ b_mask == 0x30) if isinstance(a_mask, int) and isinstance(b_mask, int) else None
        result["selection_diagnostic"] = selection
        write(run / "sme-selection-diagnostic.json", selection)
        write(run / "results.json", result)
        same_bits = lambda a, b: torch.equal(a.view(torch.int16 if a.element_size() == 2 else torch.int32),
                                            b.view(torch.int16 if b.element_size() == 2 else torch.int32))
        if not same_bits(production_output, arms["baseline"].out):
            raise RuntimeError("捕获 ABI 重放不同于实际 backend 输出")
        result["numerical_contract"] = dict(source="scripts/remote/validate_mapped_decode.py:70-92",
            atol=0.03, rtol=0.03, relative_l2_limit=0.01,
            description="独立CPU FP64抽样；同输入族原Attention 3e-2合同，附固定relative_l2界；不是模型准确率")
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
            expected = {name: tuple(t.clone() for t in arm.tensors) for name, arm in arms.items()}
            oracle = sampled_reference(torch, run, label, query, cache, common.seq_lens,
                common.block_table_tensor, {name: arm.out for name, arm in arms.items()}, active) if finite else None
            checks = dict(eager_numerics=(all(row["passed"] for row in oracle["arms"].values()) if finite else
                bool(torch.equal(torch.isnan(a.out[:B]), torch.isnan(b.out[:B])) and
                     torch.equal(torch.isposinf(a.out[:B]), torch.isposinf(b.out[:B])) and
                     torch.equal(torch.isneginf(a.out[:B]), torch.isneginf(b.out[:B])))),
                finite=(all(bool(torch.isfinite(arm.out[:B]).all()) for arm in arms.values()) if finite else True),
                guard=bool((a.out[B:] == -17).all() and (b.out[B:] == -17).all()))
            if active < B:
                checks["padded_output_zero"] = all(bool((arm.out[active:B] == 0).all()) for arm in arms.values())
                checks["padded_partials_untouched"] = all(bool((t[active:B] == -17).all())
                    for arm in arms.values() for t in (arm.partial, arm.maxima, arm.sums))
            else:
                checks["padded_output_zero"] = True
                checks["padded_partials_untouched"] = True
            failed_eager = [t.cpu() for t in b.tensors] if not checks["eager_numerics"] else None
            for arm in arms.values():
                for tensor in arm.tensors:
                    tensor.fill_(-17)
                arm.graph.replay()
            torch.cuda.synchronize()
            checks["graph_fresh_bits"] = all(same_bits(x, y) for name, arm in arms.items()
                for x, y in zip(expected[name], arm.tensors))
            checks["inputs_unchanged"] = all(same_bits(x, y) for x, y in zip(
                before, (query, cache, common.seq_lens, common.block_table_tensor)))
            checks["rng_unchanged"] = torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state())
            if changed:
                checks["output_changed"] = not same_bits(initial_output[:B], expected["baseline"][0][:B])
            span_alias = all(arms["candidate"].pk_views[i].data_ptr() == kwargs[pointer].data_ptr()
                for i, pointer in enumerate(("key_cache_ptr", "value_cache_ptr")))
            checks["span_views_still_alias_original_kv"] = span_alias
            record = dict(case=label, checks=checks, independent_reference=oracle, nonfinite_diagnostic=not finite,
                          baseline_nan=int(torch.isnan(a.out[:B]).sum().item()),
                          candidate_nan=int(torch.isnan(b.out[:B]).sum().item()))
            record["cross_arm_bitwise_diagnostic"] = same_bits(a.out[:B], b.out[:B])
            result["checks"].append(record)
            torch.save({"baseline": [x.cpu() for x in expected["baseline"]], "candidate": [x.cpu() for x in b.tensors],
                        "failed_eager_candidate": failed_eager,
                        "seq_lens": common.seq_lens.cpu(), "query": query.cpu(),
                        "block_table": common.block_table_tensor.cpu()}, run / (label + ".pt"))
            write(run / "results.json", result)
            if not all(checks.values()):
                torch.save(cache.cpu(), run / (label + "-failed-kv.pt"))
                raise RuntimeError("新增数值/Graph 边界失败：" + label + repr(checks))
            return expected["baseline"][0]

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
        # 保原page16分段，覆盖整页、尾页、空段及零长Graph行。
        boundary = [0, 1, 15, 16, 17, segments * 16, segments * 80 - 32, segments * 80 - 29]
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
        result.update(status="component_signal_only", decision="仅实际N64/S2标量页基址+原while/span一组组件；实际SMEcopy/wait由root审，不自动扩形状或模型")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if gqa is not None and original_producer is not None:
            gqa._gqa_decode_attention, gqa._reduce_partials = original_producer, original_reducer
        write(run / "results.json", result)
    return 0 if result["status"] == "component_signal_only" else 1
