"""用无GPU假对象执行实际方法克隆，检验完整调用/kwargs/pending生命周期。"""
import ast
import copy
import json
from pathlib import Path
from types import SimpleNamespace

import factory

ROOT = Path(__file__).resolve().parents[2]
INSTALLED = ROOT / "archive/hotspot-layout-20261026/installed-sampler-20261027"
HIST = ROOT / "tmp/team-main-2412207/source/vllm_fl/patches/biv150_top_p_triton.py"
EVENTS = []


class Tensor:
    def __init__(self, shape=(64, 130560), dtype="bf16"):
        self.shape, self.dtype, self.device, self.ndim = tuple(shape), dtype, "cuda:0", len(shape)
    def stride(self, index=None):
        strides = (self.shape[1], 1) if self.ndim == 2 else (1,)
        return strides if index is None else strides[index]
    def is_contiguous(self): return True
    def to(self, dtype):
        EVENTS.append("to_" + dtype)
        return Tensor(self.shape, dtype)
    def div_(self, other): EVENTS.append("temperature_div"); return self
    def unsqueeze(self, dim): return Tensor((*self.shape, 1), self.dtype)
    def softmax(self, **kwargs): EVENTS.append("original_softmax"); return Tensor(self.shape, "f32")
    def long(self): return Tensor(self.shape, "i64")
    def zero_(self): EVENTS.append("hist_zero"); return self


class Module:
    def __call__(self, *args, **kwargs): return self.forward(*args, **kwargs)


class Kernel:
    def __init__(self, name): self.name = name
    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            EVENTS.append(self.name)
            return SimpleNamespace()
        return launch


def classes(path, name, env):
    tree = ast.parse(path.read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(path), "exec"), env)
    return env[name]


def main():
    torch = SimpleNamespace(Tensor=Tensor, Generator=type("Generator", (), {}), float32="f32", bfloat16="bf16", int32="i32",
                            empty_strided=lambda shape, stride, **kw: (EVENTS.append("allocate_fp32") or Tensor(shape, kw["dtype"])))
    def original_random(probs, generators, use_fp64):
        assert probs.shape == (64, 130560) and use_fp64 is False
        EVENTS.append(("original_random", tuple(generators.keys()), id(generators)))
        return Tensor((64,), "i64")
    hist_env = dict(torch=torch, _MAX_SPLITS=1, _BLOCK=4096, _ZOOM_ROUNDS=2, _NBINS=256, _LOGIT_RANGE=20.0)
    ws = SimpleNamespace(tiles_per_split=32, **{x: Tensor((64,), "f32") for x in
                         ("max_part", "sum_part", "max_row", "z_row", "prefix_mass", "lo", "hi", "tau", "hist")})
    hist_env["_get_workspace"] = lambda *args: ws
    for name in ("_row_stats_partial", "_row_max_reduce", "_weighted_hist", "_hist_walk", "_apply_mask"):
        hist_env[name] = Kernel(name)
    node = factory.one(ast.parse(HIST.read_text()), "apply_top_p_hist_triton")
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), str(HIST), "exec"), hist_env)
    histogram = SimpleNamespace(**hist_env)
    platform = SimpleNamespace(is_cuda=lambda: False, is_cpu=lambda: False, is_xpu=lambda: False)
    env = dict(__name__="cpu_fake_target", torch=torch, nn=SimpleNamespace(Module=Module), LogprobsMode=str,
               SamplingMetadata=type("SamplingMetadata", (), {}), PIN_MEMORY=False,
               SamplerOutput=lambda **kw: SimpleNamespace(**kw), LogprobsTensors=type("LogprobsTensors", (), {}),
               _SAMPLING_EPS=1e-5, current_platform=platform, rocm_aiter_ops=SimpleNamespace(is_enabled=lambda: False),
               random_sample=original_random, apply_top_k_top_p=lambda value, k, p: histogram.apply_top_p_hist_triton(value, p))
    classes(INSTALLED / "vllm/v1/sample/ops/topk_topp_sampler.py", "TopKTopPSampler", env)
    Sampler = classes(INSTALLED / "vllm/v1/sample/sampler.py", "Sampler", env)
    meta = SimpleNamespace(all_random=True, all_greedy=False, temperature=Tensor((64,), "f32"),
                           top_p=Tensor((64,), "f32"), top_k=None, generators={0: object(), 63: object()},
                           max_num_logprobs=None, no_penalties=True, prompt_token_ids=None,
                           frequency_penalties=None, presence_penalties=None, repetition_penalties=None,
                           output_token_ids=[[] for _ in range(64)], allowed_token_ids_mask=None, bad_words_token_ids={},
                           logitsprocs=SimpleNamespace(argmax_invariant=[], non_argmax_invariant=[]),
                           logprob_token_ids=None, spec_token_ids=None, thinking_budget_state_holder=None)
    logits = Tensor()
    a, b = Sampler(), factory.ComponentSampler(Sampler(), histogram, Kernel("fused_cast_temp_stats"), torch)
    EVENTS.clear(); aa = a(logits, meta); events_a = EVENTS.copy()
    EVENTS.clear(); bb = b(logits, meta); events_b = EVENTS.copy()
    assert aa.sampled_token_ids.shape == bb.sampled_token_ids.shape == (64, 1)
    assert events_a.count("temperature_div") == 1 and "temperature_div" not in events_b
    assert events_a.count("_row_stats_partial") == 1 and "_row_stats_partial" not in events_b
    assert events_b.count("allocate_fp32") == events_b.count("fused_cast_temp_stats") == 1
    random_a = next(x for x in events_a if isinstance(x, tuple))
    random_b = next(x for x in events_b if isinstance(x, tuple))
    assert random_a == random_b
    math_a = [x for x in events_a if isinstance(x, tuple) or x in
              ("_row_max_reduce", "hist_zero", "_weighted_hist", "_hist_walk", "_apply_mask", "original_softmax")]
    math_b = [x for x in events_b if isinstance(x, tuple) or x in
              ("_row_max_reduce", "hist_zero", "_weighted_hist", "_hist_walk", "_apply_mask", "original_softmax")]
    assert math_a == math_b and b.pending is None
    rejected = []
    mutations = dict(all_random=False, all_greedy=True, top_k=Tensor((64,), "i32"), max_num_logprobs=0,
                     no_penalties=False, allowed_token_ids_mask=Tensor(), bad_words_token_ids={1: [[2]]},
                     logprob_token_ids={0: [1]}, spec_token_ids=[[1]], temperature=Tensor((64,), "bf16"),
                     top_p=Tensor((32,), "f32"), thinking_budget_state_holder=SimpleNamespace(has_tracked_requests=lambda: True),
                     logitsprocs=SimpleNamespace(argmax_invariant=[object()], non_argmax_invariant=[]))
    for name, value in mutations.items():
        old = getattr(meta, name); setattr(meta, name, value)
        try:
            try: b(logits, meta)
            except RuntimeError: rejected.append(name)
            else: raise AssertionError("未拒绝" + name)
            assert b.pending is None
        finally: setattr(meta, name, old)
    assert len(rejected) == len(mutations)
    # An exception after materialization must not keep its output alive in pending.
    old_tail = b.tail
    b.tail = lambda *args: (_ for _ in ()).throw(RuntimeError("fake tail failure"))
    try:
        try: b(logits, meta)
        except RuntimeError: pass
        else: raise AssertionError("未传播原异常")
        assert b.pending is None
    finally: b.tail = old_tail
    report = dict(cpu_only=True, imports_torch=False, gpu_qualified=False, actual_source_clone_executed=True,
                  original_same_softmax_noise_arguments=True, original_histogram_tail_order_equal=True,
                  exact_one_new_fp32_allocation=True, pending_consumed_and_exception_cleared=True,
                  eligibility_rejected=rejected, records_scope="仅假对象调用/生命周期，不证明Corex数学/RNG设备输出",
                  events_a=[x if not isinstance(x, tuple) else list(x[:2]) for x in events_a],
                  events_b=[x if not isinstance(x, tuple) else list(x[:2]) for x in events_b])
    (Path(__file__).parent / "cpu-harness-contract.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__": main()
