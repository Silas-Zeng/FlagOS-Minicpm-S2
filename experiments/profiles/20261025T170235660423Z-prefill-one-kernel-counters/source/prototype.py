"""仅 MiniCPM BF16 普通 causal 2D 的11项stride特化；不注册生产。"""
from __future__ import annotations
import ast
import hashlib
import inspect
import linecache
import re

STRIDES = ('block_table_stride', 'query_stride_0', 'query_stride_1',
    'output_stride_0', 'output_stride_1', 'stride_k_cache_0', 'stride_k_cache_1',
    'stride_k_cache_2', 'stride_v_cache_0', 'stride_v_cache_1', 'stride_v_cache_2')


def transform(source):
    header, body = source.split('\n):\n', 1)
    original_header, original_body = header, body
    for name in STRIDES:
        old = name + ': tl.int64'
        if header.count(old) != 1:
            raise ValueError('未识别唯一stride签名：' + name)
        header = header.replace(old, name + ': tl.constexpr', 1)
        body = re.sub(r'\b' + name + r'\b', name + '_i64', body)
    aliases = ''.join('    ' + name + '_i64 = tl.full((), ' + name + ', tl.int64)\n' for name in STRIDES)
    header = header.replace('def kernel_biv150_prefill_normalized(', 'def kernel_biv150_prefill_stride(', 1)
    candidate = header + '\n):\n' + aliases + body
    restored_header = header.replace('def kernel_biv150_prefill_stride(', 'def kernel_biv150_prefill_normalized(', 1)
    restored_body = body
    for name in STRIDES:
        restored_header = restored_header.replace(name + ': tl.constexpr', name + ': tl.int64', 1)
        restored_body = re.sub(r'\b' + name + r'_i64\b', name, restored_body)
    if (restored_header, restored_body) != (original_header, original_body):
        raise AssertionError('stride变换不能逐字逆回')
    ast.parse(candidate)
    return candidate


def build(attention, manager, helpers):
    source = transform(inspect.getsource(manager.raw.fn))
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = '<prefill-stride-component-' + digest + '.py>'
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
    namespace = dict(vars(attention))
    exec(compile(source, filename, 'exec'), namespace)
    return namespace['kernel_biv150_prefill_stride'], source


def private_manager(raw, attention, backend, qmod):
    from triton.runtime.jit import JITFunction
    cloned = JITFunction(raw.fn, version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug, noinline=raw.noinline, repr=raw._repr,
        launch_metadata=raw.launch_metadata)
    return qmod.Manager(attention, backend, {'kernel': raw}, 'kernel', raw, cloned).install()


def machine_summary(compiled):
    assembly = compiled.asm.get('asm', '')
    def number(key):
        match = re.search(r'\b' + key + r'\s*[:=]\s*(\d+)', assembly)
        return int(match[1]) if match else None
    return dict(sgpr=number('warp_sgpr_count'), vgpr=number('workitem_vgpr_count'),
        sgpr_spill=number('sgpr_spill_count'), vgpr_spill=number('vgpr_spill_count'),
        integer_mul=len(re.findall(r'\b(?:sl|ml)_mul(?:l)?_[ui](?:32|64)(?:_[ui]32)?\b', assembly)),
        limits='实际ASM资源/整数乘法仅诊断，不等于动态总成本或收益硬门')
