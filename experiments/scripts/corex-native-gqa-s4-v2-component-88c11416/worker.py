"""N32/S4/KV16384同步原生producer＋原reducer；合成输入，无官方或模型资格。"""
from __future__ import annotations
import importlib
import json
from pathlib import Path
import os
import subprocess
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
class NativeProducer:
    def __init__(self, torch): self.torch=torch
    def __getitem__(self, grid):
        if tuple(grid)!=(32,2,4): raise RuntimeError('只启用本次N32/S4组件')
        def launch(*args, **kw):
            if args: raise RuntimeError('只接受原实际keyword ABI')
            required={'queries_per_kv':8,'ROWS':8,'HEAD_SIZE':128,'PAGE_SIZE':16,'SEGMENTS':4,'k_stride_block':8192,'k_stride_slot':256,'k_stride_head':128,'v_stride_block':8192,'v_stride_slot':256,'v_stride_head':128,'num_warps':1,'num_stages':1}
            if any(kw[k]!=v for k,v in required.items()): raise RuntimeError('原GQA几何/配置变化')
            self.torch.ops.corex_native_gqa_s4_probe.produce(kw['query_ptr'],kw['key_cache_ptr'],kw['value_cache_ptr'],kw['seq_lens_ptr'],kw['block_table_ptr'],kw['segm_output_ptr'],kw['segm_max_ptr'],kw['segm_expsum_ptr'],kw['softmax_scale_log2e'])
        return launch



def worker(run, model, shape="hotspot"):
    result = dict(status="started", kind="生产 kernel+reducer 的随机输入组件", checks=[], timings=[],
                  limitations=["没有模型权重或实际激活采样；不是模型资格或官方收益",
                               "仅N32/B32/S4；timing真实长度统一16384，cache最大容量16384；合成激活不是官方16K成绩或模型资格；同步8KiB原生SME＋原page16/FP/split",
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
            raise RuntimeError("实际 GQA 不是冻结main56原件（与PR84 GQA相同）")
        backend = importlib.import_module("vllm.v1.attention.backends.triton_attn")
        # Same target/macros as the reviewed CPU compiler artifact; never fast-math.
        from torch.utils.cpp_extension import load as build
        os.environ['MAX_JOBS']='1';os.environ['TORCH_CUDA_ARCH_LIST']='7.1'
        builddir=run/'native-build';builddir.mkdir()
        flags=['-O3','-std=c++17','-D__ILUVATAR__','-D__MR__','-DCOREX_NATIVE_GQA_V_OVERLAP=0','-x','ivcore','--cuda-gpu-arch=ivcore11','--cuda-path=/usr/local/corex']
        library=build(name='corex_native_gqa_s4_probe',sources=[str(HERE/'bridge.cpp'),str(HERE/'gqa_s4_draft.cu')],build_directory=str(builddir),extra_cflags=['-O3','-std=c++17'],extra_cuda_cflags=flags,is_python_module=False,verbose=True)
        commands=subprocess.check_output(['ninja','-t','commands'],cwd=builddir,text=True)
        (run/'native-build-commands.txt').write_text(commands)
        actual=[line for line in commands.splitlines() if str(HERE/'gqa_s4_draft.cu') in line]
        if len(actual)!=1 or any(flag not in actual[0] for flag in flags) or any(flag in actual[0] for flag in ['-ffast-math','--use_fast_math']): raise RuntimeError('extension命令未保持已审target/宏/同步variant')
        result['native_build']=dict(library_sha256=digest(Path(library)),actual_cuda_command=actual[0],flags=flags)
        candidate=NativeProducer(torch)
        if torch.cuda.device_count() != 1:
            raise RuntimeError("非单卡")
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        if "BI-V150" not in props.name or props.multi_processor_count != 16:
            raise RuntimeError("不是 BI-V150 16 SM")
        result["device"] = str(props)
        result["source_sha256"] = dict(baseline=SOURCE_SHA, candidate=digest(HERE / "gqa_s4_draft.cu"))
        torch.manual_seed(725013)
        if shape == "hotspot":
            B, active, segments = 32, 32, 4
        else:
            raise ValueError("未知 shape")
        L = 16384
        common, query, key, value, cache = make_data(torch, [1] * B, L)
        query_backing = torch.full((B + 3, 2560), -23, dtype=torch.bfloat16, device="cuda")
        strided_query = query_backing[:, :2048].view(B + 3, 16, 128)
        strided_query.copy_(query)
        query = strided_query
        query[B:] = -17
        table = torch.zeros((B, 8192), dtype=torch.int32)
        table[:, :L // 16] = torch.arange(B * (L // 16), dtype=torch.int32).reshape(B, -1)
        table[:, :L // 16] = table[:, :L // 16].reshape(B, -1, 4).flip(-1).reshape(B, -1)
        common.slot_mapping[:B] = table[:, L // 16 - 1].to("cuda", dtype=torch.int64) * 16 + 15
        common.block_table_tensor = table.cuda()
        timing_lengths=[16384]*B
        timing_shape=dict(seq_lens=timing_lengths,N=32,S=4,actual_KV=16384,cache_capacity=16384,origin='固定16K组件完整producer+reducer判别；合成输入，非官方成绩')
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
            source_q_shape=list(kwargs["query_ptr"].shape), source_q_stride=list(kwargs["query_ptr"].stride()), source_k_shape=list(kwargs["key_cache_ptr"].shape),
            source_k_stride=list(kwargs["key_cache_ptr"].stride()), block_table_stride=8192,
            rows=8, segments=segments, head_size=128, page_size=16, candidate_compute_tile=16, num_warps=1, num_stages=1,
            query_start_loc=common.query_start_loc_cpu.tolist(), seq_lens=common.seq_lens.cpu().tolist(),
            padded_slot_values=common.slot_mapping[active:].cpu().tolist())
        if tuple(kwargs["query_ptr"].stride()) != (2560,128,1) or tuple(rkwargs["output_ptr"].stride()) != (2048,128,1):
            raise RuntimeError("本次实际QKV切片query/out stride未命中2560/2048")
        original_inputs = (query.clone(), cache.clone(), common.seq_lens.clone(), common.block_table_tensor.clone())
        arms = {}
        for name, kernel in (("baseline", original_producer), ("candidate", candidate)):
            out = torch.full_like(query, -17)
            partial = torch.full_like(metadata.softmax_segm_output, -17)
            maxima = torch.full_like(metadata.softmax_segm_max, -17)
            sums = torch.full_like(metadata.softmax_segm_expsum, -17)
            pk = dict(kwargs, segm_output_ptr=partial.narrow(2, 0, segments), segm_max_ptr=maxima.narrow(2, 0, segments),
                      segm_expsum_ptr=sums.narrow(2, 0, segments))
            # Native uses tensor strides; A/reducer use the captured ABI. They
            # must describe the same actual prefix storage, including holes.
            for pointer,dim,keyname in (
                ('query_ptr',0,'query_stride_token'),('query_ptr',1,'query_stride_head'),
                ('block_table_ptr',0,'block_table_stride'),
                ('segm_output_ptr',0,'segment_stride_token'),('segm_output_ptr',1,'segment_stride_head'),('segm_output_ptr',2,'segment_stride_segment'),
                ('segm_max_ptr',0,'max_stride_token'),('segm_max_ptr',1,'max_stride_head'),
                ('segm_expsum_ptr',0,'max_stride_token'),('segm_expsum_ptr',1,'max_stride_head')):
                if pk[pointer].stride(dim)!=pk[keyname]:raise RuntimeError('实际prefix tensor stride与原ABI不等: '+pointer+'/'+keyname)
            rk = dict(rkwargs, output_ptr=out[:B], segm_output_ptr=pk["segm_output_ptr"],
                      segm_max_ptr=pk["segm_max_ptr"], segm_expsum_ptr=pk["segm_expsum_ptr"])
            def call(kernel=kernel, pk=pk, rk=rk):
                compiled = kernel[grid](**pk)
                original_reducer[rgrid](**rk)
                return compiled
            arms[name] = NS(call=call, out=out, partial=partial, maxima=maxima, sums=sums,
                            tensors=(out, partial, maxima, sums), pk=pk)
        first = {name: arm.call() for name, arm in arms.items()}
        torch.cuda.synchronize()
        result["resources"] = {"baseline":dump(first['baseline'], run / 'ir-baseline')}
        result['resources']['candidate_cpu_probe']=json.loads((run/'compile-proof/compile-check.json').read_text())
        result['native_build']['resources_scope']='此处candidate资源只读独立CPU probe；实际extension仅保存命令与二进制SHA，未反汇编.so，不迁移资源精确身份'
        result['actual_baseline_identity']=dict(production_hash=production_compiled.hash,direct_baseline_hash=first['baseline'].hash,matched=production_compiled.hash==first['baseline'].hash)
        if not result['actual_baseline_identity']['matched']:raise RuntimeError('A不是本次真实生产编译产物')
        result["resources"]["production"] = dump(production_compiled, run / "ir-production")
        result["resources"]["reducer"] = dump(reducer_compiled, run / "ir-reducer")
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
            # Whole backing CPU snapshot distinguishes fixture corruption before any attention call.
            query_backing_before_cpu = query_backing.cpu().clone()
            query_backing_guard_before = bool((query_backing_before_cpu[:, 2048:] == -23).all())
            if not query_backing_guard_before:
                torch.save(query_backing_before_cpu.view(torch.int16), run / (label + "-bad-query-backing-before.pt"))
                result["checks"].append(dict(case=label, checks=dict(query_backing_guard_before=False), attention_not_called=True))
                write(run / "results.json", result)
                raise RuntimeError("fixture guard已在Attention执行前改变：" + label)
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
            checks["query_backing_guard_before"] = query_backing_guard_before
            if finite:
                checks["cross_arm_bitwise"] = same_bits(a.out[:B], b.out[:B])
                checks['all_partial_state_cross_arm_bitwise']=all(same_bits(x,y) for x,y in zip((a.partial,a.maxima,a.sums),(b.partial,b.maxima,b.sums)))
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
            checks["QKV_extra512_guard_unchanged"] = bool((query_backing[:, 2048:] == -23).all())
            checks["rng_unchanged"] = torch.equal(rng_cpu, torch.get_rng_state()) and torch.equal(rng_gpu, torch.cuda.get_rng_state())
            if changed:
                checks["output_changed"] = not same_bits(initial_output[:B], expected["baseline"][0][:B])
            record = dict(case=label, checks=checks, independent_reference=oracle, nonfinite_diagnostic=not finite,
                          baseline_nan=int(torch.isnan(a.out[:B]).sum().item()),
                          candidate_nan=int(torch.isnan(b.out[:B]).sum().item()))
            record["cross_arm_bitwise_diagnostic"] = same_bits(a.out[:B], b.out[:B])
            result["checks"].append(record)
            torch.save({"baseline": [x.cpu() for x in expected["baseline"]], "candidate": [x.cpu() for x in b.tensors],
                        "failed_eager_candidate": failed_eager,
                        "query_backing_before_cpu_bits": query_backing_before_cpu.view(torch.int16),
                        "query_backing_after_cpu_bits": query_backing.cpu().view(torch.int16),
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
        ragged_output=check("graph-changed-q-kv-pages-ragged-zero-tail", changed=True)
        # New native-specific boundary: legal tail page may contain NaN in unused
        # K and V slots. Original masked-load semantics must survive the SME read.
        for row,length in enumerate(ragged):
            if length>0 and length%16:
                page=int(common.block_table_tensor[row,(length-1)//16].cpu())
                cache[page,:,length%16:].fill_(float('nan'))
        tail_output=check('tail-unused-KV-NaN-masked')
        if not same_bits(ragged_output,tail_output):raise RuntimeError('尾槽poison改变了有效输出')
        # 保原page16分段，覆盖整页、尾页、空段及零长Graph行。
        boundary = [0, 1, 15, 16, 17, segments * 16, segments * 80 - 32, segments * 80 - 29]
        common.seq_lens.copy_(torch.tensor([boundary[i % 8] for i in range(active)] + [0] * (B - active),
                                           dtype=torch.int32, device="cuda"))
        # Same exact +0 BF16 Q, constructed on CPU: registered CUDA zero_ ignores this view stride.
        query[:B].copy_(torch.zeros((B, 16, 128), dtype=torch.bfloat16, device="cpu").to(query.device))
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
        result.update(status="component_signal_only", decision="仅N32/S4/KV16384同步原生producer＋原reducer一组；合成KV16384不是官方16K成绩；无模型/准确率/生产资格")
    except BaseException:
        result.update(status="failed", error=traceback.format_exc())
        traceback.print_exc()
    finally:
        if gqa is not None and original_producer is not None:
            gqa._gqa_decode_attention, gqa._reduce_partials = original_producer, original_reducer
        write(run / "results.json", result)
    return 0 if result["status"] == "component_signal_only" else 1
