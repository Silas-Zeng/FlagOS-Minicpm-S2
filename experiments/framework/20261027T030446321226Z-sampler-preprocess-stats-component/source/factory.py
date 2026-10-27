"""CPU可读的窄源码变换；不替换随机数或现有top-p数学。"""
import ast
import copy
import inspect
import textwrap
import types


def dump(node):
    return ast.dump(node, include_attributes=False)


def one(tree, name):
    found = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name]
    if len(found) != 1:
        raise RuntimeError("源码函数数量变化：" + name)
    return found[0]


def replace_once(source, old, new):
    if source.count(old) != 1:
        raise RuntimeError("源码窄变换不唯一：" + old[:70])
    return source.replace(old, new, 1)


def kernel_source(histogram_source):
    tree = ast.parse(histogram_source)
    old = one(tree, "_row_stats_partial")
    source = ast.get_source_segment(histogram_source, old)
    new = replace_once(source, "def _row_stats_partial(\n    LOGITS,", "def _fused_cast_temperature_stats(\n    INPUT,\n    TEMPERATURE,\n    stride_input,\n    LOGITS,")
    new = replace_once(new, "    row_sum = 0.0\n", "    row_sum = 0.0\n    temperature = tl.load(TEMPERATURE + row)\n")
    new = replace_once(new, "            LOGITS + row * stride_row + idx,", "            INPUT + row * stride_input + idx,")
    new = replace_once(new, "        tile_max = tl.max(values, axis=0)", "        values = values.to(tl.float32) / temperature\n        tl.store(LOGITS + row * stride_row + idx, values, mask=idx < VOCAB_SIZE)\n        tile_max = tl.max(values, axis=0)")
    inverse = new
    inverse = replace_once(inverse, "def _fused_cast_temperature_stats(\n    INPUT,\n    TEMPERATURE,\n    stride_input,\n    LOGITS,", "def _row_stats_partial(\n    LOGITS,")
    inverse = replace_once(inverse, "    temperature = tl.load(TEMPERATURE + row)\n", "")
    inverse = replace_once(inverse, "            INPUT + row * stride_input + idx,", "            LOGITS + row * stride_row + idx,")
    inverse = replace_once(inverse, "        values = values.to(tl.float32) / temperature\n        tl.store(LOGITS + row * stride_row + idx, values, mask=idx < VOCAB_SIZE)\n", "")
    if inverse != source:
        raise RuntimeError("首遍kernel不能逐字逆回")
    # Original dot/exp/FMA/max/sum expressions are deliberately not transformed.
    return "from vllm.triton_utils import tl, triton\n\n@triton.jit\n" + new + "\n"


def clone_method(function, transform, namespace_extra):
    original = textwrap.dedent(inspect.getsource(function))
    original_tree = ast.parse(original)
    transformed = copy.deepcopy(original_tree)
    transformed, receipt = transform(transformed)
    transformed = ast.fix_missing_locations(transformed)
    namespace = dict(function.__globals__)
    namespace.update(namespace_extra)
    exec(compile(transformed, "<sampler-component-private-clone>", "exec"), namespace)
    result = namespace[function.__name__]
    return result, dict(original_ast=dump(original_tree), candidate_ast=dump(transformed), **receipt)


def forward_transform(tree):
    target = ast.parse("logits = logits.to(torch.float32)").body[0]
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and dump(n) == dump(target)]
    if len(matches) != 1:
        raise RuntimeError("原forward FP32转换不唯一")
    matches[0].value = ast.Name(id="logits", ctx=ast.Load())
    inverse = copy.deepcopy(tree)
    restored = 0
    for n in ast.walk(inverse):
        if isinstance(n, ast.Assign) and dump(n) == dump(ast.parse("logits = logits").body[0]):
            n.value = copy.deepcopy(target.value)
            restored += 1
    if restored != 1:
        raise RuntimeError("forward逆变换不唯一")
    return tree, dict(change="仅延迟原FP32转换至sample首遍；前置processor必须全为空", inverse_ast=dump(inverse))


def sample_transform(tree):
    matches = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
               and dump(n.func) == dump(ast.parse("self.apply_temperature", mode="eval").body)]
    if len(matches) != 1:
        raise RuntimeError("sample温度调用不唯一")
    call = matches[0]
    original = copy.deepcopy(call)
    expected = ast.parse("self.apply_temperature(logits, sampling_metadata.temperature, sampling_metadata.all_random)", mode="eval").body
    if dump(call) != dump(expected):
        raise RuntimeError("原温度参数/次序变化")
    call.func = ast.Name(id="_component_materialize_stats", ctx=ast.Load())
    inverse = copy.deepcopy(tree)
    found = [n for n in ast.walk(inverse) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "_component_materialize_stats"]
    if len(found) != 1:
        raise RuntimeError("sample逆变换不唯一")
    found[0].func = original.func
    return tree, dict(change="仅原apply_temperature替为转换/除法/首遍stats", inverse_ast=dump(inverse))


def histogram_tail_source(histogram_source):
    tree = ast.parse(histogram_source)
    old = one(tree, "apply_top_p_hist_triton")
    candidate = copy.deepcopy(old)
    removed = []
    kept = []
    for stmt in candidate.body:
        if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and isinstance(stmt.value.func, ast.Subscript)
                and isinstance(stmt.value.func.value, ast.Name)
                and stmt.value.func.value.id == "_row_stats_partial"):
            removed.append(copy.deepcopy(stmt))
        else:
            kept.append(stmt)
    if len(removed) != 1:
        raise RuntimeError("top-p首遍调用不唯一")
    candidate.body = kept
    inverse = copy.deepcopy(candidate)
    # Insert at the exact position from the original body, not a guessed slot.
    position = next(i for i, n in enumerate(old.body) if dump(n) == dump(removed[0]))
    inverse.body.insert(position, removed[0])
    if dump(inverse) != dump(old):
        raise RuntimeError("histogram尾不能逐AST逆回")
    candidate.name = "_component_histogram_after_stats"
    candidate.decorator_list = []
    module = ast.fix_missing_locations(ast.Module(body=[candidate], type_ignores=[]))
    return module, dict(change="只去已完成的_row_stats_partial调用，workspace共用原缓存", inverse_ast_equal=True)


class ComponentSampler:
    """仅组件的独立实例；不重绑生产类/全局函数，不支持并发同实例。"""

    def __init__(self, sampler, histogram, kernel, torch):
        self.sampler, self.histogram, self.kernel, self.torch = sampler, histogram, kernel, torch
        self.pending = None
        self.records = []
        self.observer = None
        self.receipts = {}
        cls = type(sampler)
        forward, self.receipts["forward"] = clone_method(cls.forward, forward_transform, {})
        sample, self.receipts["sample"] = clone_method(cls.sample, sample_transform,
                                                     {"_component_materialize_stats": self.materialize_stats})
        if self.receipts["forward"]["inverse_ast"] != self.receipts["forward"]["original_ast"]:
            raise RuntimeError("forward除延迟cast外有变化")
        if self.receipts["sample"]["inverse_ast"] != self.receipts["sample"]["original_ast"]:
            raise RuntimeError("sample除融合首遍外有变化")
        sampler.forward = types.MethodType(forward, sampler)
        sampler.sample = types.MethodType(sample, sampler)
        top = sampler.topk_topp_sampler
        original = type(top).forward_native
        if getattr(top.forward, "__func__", None) is not original:
            raise RuntimeError("实际TopKTopPSampler不是原forward_native，停止")
        namespace = dict(original.__globals__)
        namespace["apply_top_k_top_p"] = self.filter_after_stats
        # Reuse the original code object; only deterministic filtering entry changes.
        cloned = types.FunctionType(original.__code__, namespace, original.__name__, original.__defaults__, original.__closure__)
        cloned.__kwdefaults__ = original.__kwdefaults__
        top.forward = types.MethodType(cloned, top)
        source = inspect.getsource(histogram.apply_top_p_hist_triton)
        module, self.receipts["histogram_tail"] = histogram_tail_source(source)
        env = dict(vars(histogram))
        exec(compile(module, "<sampler-component-original-histogram-tail>", "exec"), env)
        self.tail = env["_component_histogram_after_stats"]

    @staticmethod
    def eligible(logits, sm, torch):
        holder = sm.thinking_budget_state_holder
        return (tuple(logits.shape) == (64, 130560) and logits.dtype == torch.bfloat16
                and logits.stride(1) == 1 and logits.is_contiguous()
                and sm.all_random and not sm.all_greedy and sm.temperature is not None
                and sm.temperature.dtype == torch.float32 and tuple(sm.temperature.shape) == (64,)
                and sm.temperature.is_contiguous() and sm.top_k is None and sm.top_p is not None
                and sm.top_p.dtype == torch.float32 and tuple(sm.top_p.shape) == (64,)
                and sm.top_p.is_contiguous() and sm.no_penalties
                and sm.temperature.device == logits.device and sm.top_p.device == logits.device
                and sm.max_num_logprobs is None and not sm.logprob_token_ids
                and sm.allowed_token_ids_mask is None and not sm.bad_words_token_ids
                and not sm.logitsprocs.argmax_invariant and not sm.logitsprocs.non_argmax_invariant
                and sm.spec_token_ids is None
                and (holder is None or not holder.has_tracked_requests()))

    def __call__(self, logits, metadata):
        if self.pending is not None:
            raise RuntimeError("上次调用留有pending或同实例并发")
        if not self.eligible(logits, metadata, self.torch):
            raise RuntimeError("组件固定R64/无processor资格未满足，不改原语义")
        try:
            output = self.sampler(logits, metadata)
            if self.pending is not None:
                raise RuntimeError("实际top-p未消费预计算stats")
            return output
        finally:
            self.pending = None

    def materialize_stats(self, logits, temperature, all_random):
        assert all_random and self.pending is None
        torch, h = self.torch, self.histogram
        out = torch.empty_strided(logits.shape, logits.stride(), dtype=torch.float32, device=logits.device)
        ws = h._get_workspace(64, 130560, logits.device)
        compiled = self.kernel[(64, h._MAX_SPLITS)](
            logits, temperature, logits.stride(0), out, ws.max_part, ws.sum_part, out.stride(0),
            VOCAB_SIZE=130560, NUM_SPLITS=h._MAX_SPLITS, MAX_SPLITS=h._MAX_SPLITS,
            TILES_PER_SPLIT=ws.tiles_per_split, BLOCK=h._BLOCK, num_warps=8)
        if not self.records:
            self.records.append(compiled)
        self.pending = out
        if self.observer:
            self.observer("scaled", out, ws)
        return out

    def filter_after_stats(self, logits, k, p):
        if k is not None or self.pending is not logits:
            raise RuntimeError("top-p输入不对应本次融合首遍")
        self.pending = None
        result = self.tail(logits, p)
        if self.observer:
            self.observer("filtered", result, self.histogram._get_workspace(64, 130560, logits.device))
        return result
