"""仅 MiniCPM BF16 普通 causal 2D 的 log2 softmax 组件，不注册生产。"""
from __future__ import annotations
import ast
import hashlib
import inspect
import linecache
from pathlib import Path

HELPERS_SHA = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
LOG2E = 1.4426950408889634074


def once(text, old, new):
    if text.count(old) != 1:
        raise ValueError("非唯一源码锚点：" + old[:80])
    return text.replace(old, new, 1)


def transform(kernel_source, helper_source):
    """只改缩放域和指数，归约、负无穷保护及概率 BF16 转换保持。"""
    candidate = once(kernel_source, "def kernel_biv150_prefill_normalized(",
                     "def kernel_biv150_prefill_log2(")
    candidate = once(candidate, "    score_scale = scale\n",
                     "    score_scale = scale * 1.4426950408889634074\n")
    candidate = once(candidate, "M, L, P, alpha = softmax_step(S, M, L)",
                     "M, L, P, alpha = softmax_step_log2(S, M, L)")
    helper = once(helper_source, "def softmax_step(", "def softmax_step_log2(")
    helper = once(helper, "tl.exp(S - m_j[:, None])", "tl.exp2(S - m_j[:, None])")
    helper = once(helper, "tl.exp(M - m_j)", "tl.exp2(M - m_j)")
    restored = once(candidate, "def kernel_biv150_prefill_log2(",
                    "def kernel_biv150_prefill_normalized(")
    restored = once(restored, "    score_scale = scale * 1.4426950408889634074\n",
                    "    score_scale = scale\n")
    restored = once(restored, "M, L, P, alpha = softmax_step_log2(S, M, L)",
                    "M, L, P, alpha = softmax_step(S, M, L)")
    if restored != kernel_source:
        raise AssertionError("内核不能精确逆回当前生产 normalized source")
    original_helper = helper.replace("def softmax_step_log2(", "def softmax_step(", 1)
    original_helper = original_helper.replace("tl.exp2(S - m_j[:, None])", "tl.exp(S - m_j[:, None])", 1)
    original_helper = original_helper.replace("tl.exp2(M - m_j)", "tl.exp(M - m_j)", 1)
    if original_helper != helper_source:
        raise AssertionError("helper 除换底外发生变化")
    source = helper + "\n\n" + candidate
    ast.parse(source)
    return source


def build(attention, manager, helpers):
    if hashlib.sha256(Path(helpers.__file__).read_bytes()).hexdigest() != HELPERS_SHA:
        raise ValueError("未审计的原 softmax helper")
    source = transform(inspect.getsource(manager.raw.fn), inspect.getsource(helpers.softmax_step.fn))
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = "<prefill-log2-component-" + digest + ".py>"
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
    namespace = dict(vars(attention))
    exec(compile(source, filename, "exec"), namespace)
    return namespace["kernel_biv150_prefill_log2"], source


def private_manager(raw, attention, backend, qmod):
    from triton.runtime.jit import JITFunction
    cloned = JITFunction(raw.fn, version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug, noinline=raw.noinline, repr=raw._repr,
        launch_metadata=raw.launch_metadata)
    return qmod.Manager(attention, backend, {"kernel": raw}, "kernel", raw, cloned).install()


def machine_summary(compiled):
    import re
    llvm = compiled.asm.get("llir", "")
    assembly = compiled.asm.get("asm", "")
    return dict(log2e_llvm_mul=len(re.findall(r"fmul[^\n]*0x3FF7154760000000", llvm)),
        log2e_asm_mul=len(re.findall(r"ml_mul_f32[^\n]*0x3fb8aa3b", assembly, re.I)),
        exp_instructions=len(re.findall(r"\bml_exp_f32\b", assembly)),
        limits="静态指令计数仅诊断，不等于动态总成本或收益硬门")
