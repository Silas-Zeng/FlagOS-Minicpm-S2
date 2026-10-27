"""固定R64完整原Sampler成本；只融合确定性转换/温度/首遍stats。"""
from pathlib import Path
from types import SimpleNamespace
import hashlib
import importlib
import inspect
import json
import statistics
import traceback


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def worker(run, model):
    run, model = Path(run), Path(model)
    result = dict(status="started", cases=[], timings=[], kind="sampler_preprocess_stats_component",
                  rows=64, vocab=130560, source_main="241220723a09061c182764f8f738e5ec01190367",
                  new_persistent_weight_bytes=0, precision_qualified=False, official_qualified=False,
                  scope="完整eager Sampler.forward；新确定性前缀另测换值Graph，随机数原函数/原归属",
                  limitations=["仅固定R64、BF16head/真实词表、无processor的top-p路径，不外推其它R或模型吞吐。",
                               "完整eager Event和wall包含每调用实际分配/依赖；Graph只验证新增确定性数据流，不授予完整随机Sampler Graph资格。",
                               "准备身份和逐位门不是稳定收益/105/官方资格；表述不会把原head计入已测Sampler收益。"])
    try:
        import torch
        import triton
        import flag_gems
        import factory
        import candidate
        from reused_helpers import timed_batch
        from safetensors import safe_open
        from torch.utils._python_dispatch import TorchDispatchMode

        torch.set_num_threads(4)
        props = torch.cuda.get_device_properties(0)
        target = triton.runtime.driver.active.get_current_target()
        assert "BI-V150" in props.name and props.multi_processor_count == 16 and target.warp_size == 64
        for key in ("VLLM_FL_FLAGOS_WHITELIST", "VLLM_FL_FLAGOS_BLACKLIST", "VLLM_FL_FLAGOS_BLACKLIST_APPEND"):
            import os
            assert not os.environ.get(key), "非默认FlagGems配置：" + key
        # Same default worker registrar; do not install attention or a service.
        from vllm_fl.utils import get_flag_gems_whitelist_blacklist
        whitelist, blacklist = get_flag_gems_whitelist_blacklist()
        assert not whitelist and not blacklist
        flag_gems.enable(record=True, once=True, path=str(run / "flaggems-oplist.txt"))
        from vllm_fl.dispatch.backends.vendor.iluvatar.iluvatar import patch_sampler_compile_for_iluvatar
        patch_sampler_compile_for_iluvatar()
        from vllm_fl.patches import biv150_runtime
        biv150_runtime._patch_top_p_sampler()
        sampler_module = importlib.import_module("vllm.v1.sample.sampler")
        top = importlib.import_module("vllm.v1.sample.ops.topk_topp_sampler")
        hist = importlib.import_module("vllm_fl.patches.biv150_top_p_triton")
        from vllm.v1.sample.metadata import SamplingMetadata
        from vllm.model_executor.layers.linear import UnquantizedLinearMethod
        from vllm.platforms import current_platform
        assert current_platform.vendor_name == "iluvatar", "不是实际Iluvatar平台，停止不换采样后端"

        # Current installation pins are verified BEFORE invoking the real head/Sampler.
        receipt = json.loads((Path(__file__).parent / "installed-manifest.json").read_text())
        sources = {}
        for relative, info in receipt["files"].items():
            source = Path(info["source"])
            assert hashlib.sha256(source.read_bytes()).hexdigest() == info["sha256"], relative
            sources[relative] = info["sha256"]
        assert hashlib.sha256(Path(inspect.getsourcefile(hist)).read_bytes()).hexdigest() == "da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9"
        assert getattr(top.apply_top_k_top_p_triton, "_biv150_top_p_dispatch", False)
        assert not hasattr(top.compiled_random_sample, "__wrapped__"), "原Iluvatar compiled_random_sample未unwrap"
        registrations = []
        for op in ("_to_copy", "div_.Tensor", "linear"):
            entries = [x for x in flag_gems.current_work_registrar.config if x[0] == op]
            assert len(entries) == 1, (op, entries)
            function = inspect.unwrap(entries[0][1])
            registrations.append(dict(op=op, module=function.__module__, function=function.__qualname__))
            table = torch._C._dispatch_dump_table("aten::" + op)
            (run / ("dispatch-" + op.replace(".", "-") + ".txt")).write_text(table)
            assert any(line.startswith("CUDA:") and "flag_gems/" in line.replace("\\", "/") for line in table.splitlines()), op
        result["identity"] = dict(installed_sources=sources, registrar=registrations, target=str(target),
                                  platform_vendor=current_platform.vendor_name,
                                  random_sample_code_file=top.random_sample.__code__.co_filename,
                                  sample_noise_code_file=top.sample_with_exponential_noise.__code__.co_filename,
                                  random_sample_unmodified=True, true_div_func="x / y; not div_rn")
        seen = []

        class ObserveOps(TorchDispatchMode):
            def __torch_dispatch__(self, func, types, args=(), kwargs=None):
                kwargs = kwargs or {}
                name = str(func)
                if name in ("aten._to_copy.default", "aten.div_.Tensor", "aten.linear.default", "aten.mm.default"):
                    seen.append(dict(op=name, tensors=[dict(shape=list(x.shape), stride=list(x.stride()), dtype=str(x.dtype))
                                                     for x in args if isinstance(x, torch.Tensor)]))
                return func(*args, **kwargs)

        # One actual current default Unquantized head call. No alternate provider or timing claim.
        index = json.loads((model / "model.safetensors.index.json").read_text())
        name = "lm_head.weight"
        with safe_open(str(model / index["weight_map"][name]), framework="pt", device="cpu") as f:
            wc = f.get_tensor(name).contiguous()
        assert tuple(wc.shape) == (130560, 2048) and wc.dtype == torch.bfloat16
        g = torch.Generator().manual_seed(20261027)
        hidden = (torch.randn((64, 2048), generator=g) * .125).bfloat16().cuda()
        w = wc.cuda()
        layer = SimpleNamespace(weight=w, prefix="lm_head")
        with ObserveOps():
            logits = UnquantizedLinearMethod().apply(layer, hidden, bias=None)
        torch.cuda.synchronize()
        assert logits.dtype == torch.bfloat16 and tuple(logits.shape) == (64, 130560) and logits.is_contiguous()
        assert bool(torch.isfinite(logits).all())
        provider = UnquantizedLinearMethod.apply.__globals__["dispatch_unquantized_gemm"]()
        path = Path(inspect.getsourcefile(provider))
        (run / "source" / "actual-head-provider.py").write_bytes(path.read_bytes())
        result["head"] = dict(weight_name=name, weight_shape=list(w.shape), weight_bytes=w.numel() * 2,
                              weight_sha256=hashlib.sha256(wc.view(torch.uint8).numpy().tobytes()).hexdigest(),
                              provider_module=provider.__module__, provider_name=provider.__qualname__,
                              provider_source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                              output_dtype=str(logits.dtype), output_shape=list(logits.shape), output_stride=list(logits.stride()),
                              timed=False, synthetic_hidden=True, source_callback="actual UnquantizedLinearMethod.apply")
        del w, wc, hidden
        torch.cuda.empty_cache()
        origin = logits.clone()
        temperature = torch.ones(64, dtype=torch.float32, device="cuda")
        p = torch.full((64,), .95, dtype=torch.float32, device="cuda")
        zeros = torch.zeros(64, dtype=torch.float32, device="cuda")
        metadata = SamplingMetadata(temperature=temperature, all_greedy=False, all_random=True,
                                    top_p=p, top_k=None, generators={}, max_num_logprobs=None,
                                    no_penalties=True, prompt_token_ids=None, frequency_penalties=zeros,
                                    presence_penalties=zeros, repetition_penalties=torch.ones_like(zeros),
                                    output_token_ids=[[] for _ in range(64)], allowed_token_ids_mask=None,
                                    bad_words_token_ids={}, logitsprocs=SimpleNamespace(argmax_invariant=[], non_argmax_invariant=[]))
        baseline = sampler_module.Sampler()
        changed = factory.ComponentSampler(sampler_module.Sampler(), hist, candidate._fused_cast_temperature_stats, torch)
        save(run / "clone-contract.json", changed.receipts)
        assert baseline.topk_topp_sampler.logprobs_mode == "raw_logprobs"
        def bits(a, b):
            return a.dtype == b.dtype and torch.equal(a.contiguous().view(torch.uint8), b.contiguous().view(torch.uint8))
        def snapshot_generators():
            return dict(default=torch.cuda.get_rng_state().clone(), cpu=torch.get_rng_state().clone(),
                        request={i: gen.get_state().clone() for i, gen in metadata.generators.items()})
        def restore_rng(state):
            torch.cuda.set_rng_state(state["default"]); torch.set_rng_state(state["cpu"])
            for i, value in state["request"].items():
                metadata.generators[i].set_state(value)
        def equal_rng(a, b):
            return (bits(a["default"], b["default"]) and bits(a["cpu"], b["cpu"])
                    and a["request"].keys() == b["request"].keys()
                    and all(bits(a["request"][i], b["request"][i]) for i in a["request"]))
        def observe(target):
            def record(stage, value, ws):
                target[stage] = value.clone()
                if stage == "filtered":
                    target["stats"] = {key: getattr(ws, key).clone() for key in
                                       ("max_part", "sum_part", "max_row", "z_row", "tau", "prefix_mass", "lo", "hi")}
            return record
        def run_baseline_observed(target):
            # Only correctness probes wrap readonly observation. Timing restores all original entries.
            apply_temp, apply_filter = baseline.apply_temperature, top.apply_top_k_top_p
            def temp_observer(*args):
                out = apply_temp(*args); observe(target)("scaled", out, None); return out
            def filter_observer(value, k, pp):
                out = apply_filter(value, k, pp)
                observe(target)("filtered", out, hist._get_workspace(64, 130560, logits.device))
                return out
            baseline.apply_temperature = temp_observer
            top.apply_top_k_top_p = filter_observer
            try:
                return baseline(logits, metadata)
            finally:
                del baseline.apply_temperature
                top.apply_top_k_top_p = apply_filter
        def check(label, dispatch=False):
            input_before = logits.clone(); temp_before = temperature.clone(); p_before = p.clone()
            initial = snapshot_generators(); aa, bb = {}, {}
            if dispatch:
                with ObserveOps():
                    a = run_baseline_observed(aa)
            else:
                a = run_baseline_observed(aa)
            after_a = snapshot_generators()
            restore_rng(initial)
            changed.observer = observe(bb)
            try:
                b = changed(logits, metadata)
            finally:
                changed.observer = None
            after_b = snapshot_generators()
            torch.cuda.synchronize()
            case = dict(label=label, scaled_bitwise=bits(aa["scaled"], bb["scaled"]),
                        filtered_bitwise=bits(aa["filtered"], bb["filtered"]),
                        stats_bitwise=all(bits(aa["stats"][k], bb["stats"][k]) for k in aa["stats"]),
                        sampled_ids_bitwise=bits(a.sampled_token_ids, b.sampled_token_ids), rng_equal=equal_rng(after_a, after_b),
                        no_nan=not bool(torch.isnan(aa["filtered"]).any() or torch.isnan(bb["filtered"]).any()),
                        scaled_finite=bool(torch.isfinite(aa["scaled"]).all() and torch.isfinite(bb["scaled"]).all()),
                        stats_finite=all(bool(torch.isfinite(value).all()) for values in (aa["stats"], bb["stats"]) for value in values.values()),
                        ids_valid=bool(((a.sampled_token_ids >= 0) & (a.sampled_token_ids < 130560)).all()
                                       and ((b.sampled_token_ids >= 0) & (b.sampled_token_ids < 130560)).all()),
                        inputs_unchanged=bits(logits, input_before) and bits(temperature, temp_before) and bits(p, p_before))
            if label == "real_head":
                # Original temperature=1: BF16-to-double-to-float is an exact independent conversion/division oracle.
                reference = input_before.cpu().double().div(1.0).float()
                case["independent_cpu_fp64_scaled_exact"] = bits(aa["scaled"].cpu(), reference) and bits(bb["scaled"].cpu(), reference)
            result["cases"].append(case)
            save(run / "result.json", result)
            if not all(v for k, v in case.items() if k != "label"):
                raise AssertionError("完整Sampler逐位/原RNG/独立参考门失败，停止，不改容差")
        check("real_head", dispatch=True)
        assert any(x["op"] == "aten._to_copy.default" and x["tensors"][0]["dtype"] == "torch.bfloat16"
                   and x["tensors"][0]["shape"] == [64, 130560] for x in seen), "未见实际原BF16转换"
        assert any(x["op"] == "aten.div_.Tensor" and x["tensors"][0]["dtype"] == "torch.float32"
                   and x["tensors"][0]["shape"] == [64, 130560] for x in seen), "未见实际原FP32温度除法"
        result["actual_dispatch_calls"] = seen
        for label, scale, temp, pp in (("changed_temperature", -.5, .8, .95), ("zero_ties", 0., 1., .95),
                                       ("top_p_one", 1., 2., 1.), ("top_p_zero", 1., 1., 0.)):
            logits.copy_(origin * scale); temperature.fill_(temp); p.fill_(pp); check(label)
        logits.copy_(origin); temperature.fill_(1.); p.fill_(.95)
        metadata.generators = {0: torch.Generator(device="cuda").manual_seed(19), 63: torch.Generator(device="cuda").manual_seed(37)}
        check("mixed_request_generators")
        metadata.generators = {}
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            check("side_stream")
        torch.cuda.current_stream().wait_stream(stream)
        torch.cuda.synchronize()
        # Deterministic changed-input Graph checks cover exactly the newly changed data flow.
        # Random sampling remains outside this check and has already been compared above with full RNG state.
        def prefix_a():
            value = logits.to(torch.float32)
            value = baseline.apply_temperature(value, temperature, True)
            return hist.apply_top_p_hist_triton(value, p)
        def prefix_b():
            value = changed.materialize_stats(logits, temperature, True)
            return changed.filter_after_stats(value, None, p)
        prefix_a(); prefix_b(); torch.cuda.synchronize()
        graphs, outputs = {}, {}
        for arm, callback in (("A", prefix_a), ("B", prefix_b)):
            graphs[arm] = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graphs[arm]):
                outputs[arm] = callback()
        for label, scale, temp, pp in (("graph_changed", -.75, .5, .9), ("graph_back", 1., 1., .95)):
            logits.copy_(origin * scale); temperature.fill_(temp); p.fill_(pp)
            outputs["A"].fill_(float("nan")); outputs["B"].fill_(float("nan"))
            graphs["A"].replay(); graphs["B"].replay(); torch.cuda.synchronize()
            eager = prefix_a()
            case = dict(label=label, bitwise=bits(outputs["A"], outputs["B"]) and bits(eager, outputs["B"]),
                        no_nan=not bool(torch.isnan(outputs["B"]).any()), scope="仅新增确定性前缀Graph；不称完整随机Sampler Graph资格")
            result["cases"].append(case)
            assert case["bitwise"] and case["no_nan"], "换值/poisoned前缀Graph失败"
        del graphs, outputs, eager
        logits.copy_(origin); temperature.fill_(1.); p.fill_(.95)
        assert changed.pending is None and changed.observer is None and "apply_temperature" not in baseline.__dict__
        assert top.apply_top_k_top_p.__module__ == top.__name__
        compiled = changed.records[0]
        result["candidate_resource"] = dict(hash=getattr(compiled.metadata, "hash", None), shared=getattr(compiled.metadata, "shared", None),
                                            n_regs=getattr(compiled, "n_regs", None), n_spills=getattr(compiled, "n_spills", None))
        for kind, data in compiled.asm.items():
            if isinstance(data, (str, bytes)):
                (run / ("candidate." + kind)).write_bytes(data.encode() if isinstance(data, str) else data)
        for _ in range(3):
            baseline(logits, metadata); changed(logits, metadata)
        torch.cuda.synchronize()
        pair = (torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True))
        for arm in "ABBA":
            callback = (lambda: baseline(logits, metadata)) if arm == "A" else (lambda: changed(logits, metadata))
            result["timings"].append(dict(arm=arm, **timed_batch(torch, callback, pair, 12)))
        check("after_timing")
        medians = {arm: {metric: statistics.median(x[metric] for x in result["timings"] if x["arm"] == arm)
                         for metric in ("event_per_call_ms", "wall_per_call_ms")} for arm in "AB"}
        result["median"] = medians
        result["cost_includes"] = "每次实际完整eager Sampler.forward，输出分配、hist依赖、原softmax/噪声/除法/argmax及Python提交；不含未变head的预生成"
        result["status"] = "component_one_abba_positive" if all(medians["B"][m] < medians["A"][m] for m in medians["A"]) else "nonpositive_stop"
        result["precision_qualified"] = False
        result["next"] = "仅单组候选信号；需要root决定后继，不自动模型/官方" if result["status"] == "component_one_abba_positive" else "任一完整Event/wall非正，停止，不扫其它R/参数"
        result["actual_scalar_cpu_division_not_assumed_device_rn"] = True
        save(run / "result.json", result)
        return 0
    except BaseException:
        result.update(status="failed_stop", error=traceback.format_exc())
        save(run / "result.json", result)
        traceback.print_exc()
        return 1
