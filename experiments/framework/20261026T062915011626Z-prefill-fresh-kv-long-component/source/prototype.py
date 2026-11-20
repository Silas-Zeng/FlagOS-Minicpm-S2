"""独立 fresh-KV loader 原型；只由组件构建，不注册生产。"""
from __future__ import annotations
import ast
import hashlib
import inspect
import linecache
import re

BASELINE_KERNEL_SHA = 'b6703eef9828e4497b446a5bd96d0c00c84049d1a092bf5fc0077f44dd5e7a63'
FRESH_STRIDES = ('fresh_k_stride_0', 'fresh_k_stride_1', 'fresh_k_stride_2',
                 'fresh_v_stride_0', 'fresh_v_stride_1', 'fresh_v_stride_2')


def _once(source, before, after):
    if source.count(before) != 1:
        raise ValueError('找不到唯一源码锚点: ' + before[:90])
    return source.replace(before, after, 1)


def canonical(source):
    node = next(x for x in ast.parse(source).body
                if isinstance(x, ast.FunctionDef))
    return ast.get_source_segment(source, node).rstrip() + '\n'


def transform(source):
    """只变loader/新增显式参数；原绝对K tile与全部浮点语句不动。"""
    source = canonical(source)
    digest = hashlib.sha256(source.encode()).hexdigest()
    if digest != BASELINE_KERNEL_SHA:
        raise ValueError('不是已冻结 main6971 stride 核: ' + digest)
    candidate = _once(source, 'def kernel_biv150_prefill_stride(',
                      'def kernel_biv150_prefill_fresh_kv(')
    extra = ('    fresh_key_ptr,\n    fresh_value_ptr,\n' +
             ''.join('    ' + name + ': tl.constexpr,\n' for name in FRESH_STRIDES))
    candidate = _once(candidate, '\n    value_cache_ptr,\n', '\n    value_cache_ptr,\n' + extra)
    aliases = ''.join('    ' + name + '_i64 = tl.full((), ' + name + ', tl.int64)\n'
                      for name in FRESH_STRIDES)
    scope = '''    tl.static_assert(not IS_3D and USE_CAUSAL and not USE_PER_SEQ_CAUSAL)
    tl.static_assert(not USE_MM_PREFIX and not USE_SINKS and not USE_ALIBI_SLOPES)
    tl.static_assert(not USE_ALIBI_SQRT and not USE_QQ_BIAS and not USE_SOFTCAP)
    tl.static_assert(not SLIDING_WINDOW and CHUNK_LOOKBACK < 0)
    tl.static_assert(KV_QUANT_MODE == 0 and not USE_FP8 and not Q_IS_FP8)
    tl.static_assert(not USE_TD and not USE_TD_QO)
    tl.static_assert(num_query_heads == 16 and num_queries_per_kv == 8)
    tl.static_assert(HEAD_SIZE == 128 and HEAD_SIZE_PADDED == 128)
    tl.static_assert(BLOCK_SIZE == 16 and TILE_SIZE == 64)
    tl.static_assert(BLOCK_M == 128 and BLOCK_Q == 16)
    tl.static_assert(fresh_key_ptr.dtype.element_ty == tl.bfloat16)
    tl.static_assert(fresh_value_ptr.dtype.element_ty == tl.bfloat16)
'''
    candidate = _once(candidate, '    block_table_stride_i64 =',
                      aliases + scope + '    block_table_stride_i64 =')
    start = candidate.index('        physical_block_idx = tl.load(')
    end = candidate.index('        K = _cast_kv_tile', start)
    old = candidate[start:end]
    loader = '''        # 原绝对T64 tile不重分组；只在ctx边界选择数据来源。
        valid_key = tile_mask & (seq_offset < seq_len)
        fresh_lane = valid_key & (seq_offset >= context_len)
        history_lane = valid_key & (seq_offset < context_len)
        physical_block_idx = tl.load(
            block_tables_ptr + block_table_offset + seq_offset // BLOCK_SIZE,
            mask=history_lane, other=0,
        ).to(tl.int64)
        # 被mask的历史lane不形成负raw行；不会解引用未知raw地址。
        fresh_row = cur_batch_in_all_start_index.to(tl.int64) + tl.maximum(
            seq_offset - context_len, 0).to(tl.int64)
        k_offset = (
            physical_block_idx[None, :] * stride_k_cache_0_i64
            + kv_head_idx * stride_k_cache_2_i64
            + offs_d[:, None] * stride_k_cache_3
            + (seq_offset % BLOCK_SIZE)[None, :] * stride_k_cache_1_i64
        )
        v_offset = (
            physical_block_idx[:, None] * stride_v_cache_0_i64
            + kv_head_idx * stride_v_cache_2_i64
            + offs_d[None, :] * stride_v_cache_3
            + (seq_offset % BLOCK_SIZE)[:, None] * stride_v_cache_1_i64
        )
        fresh_k_offset = (fresh_row[None, :] * fresh_k_stride_0_i64
            + kv_head_idx * fresh_k_stride_1_i64
            + offs_d[:, None] * fresh_k_stride_2_i64)
        fresh_v_offset = (fresh_row[:, None] * fresh_v_stride_0_i64
            + kv_head_idx * fresh_v_stride_1_i64
            + offs_d[None, :] * fresh_v_stride_2_i64)
        # 同dtype pointer select后每个K/V元素各读一次，非两次读后求和。
        k_ptr = tl.where(fresh_lane[None, :], fresh_key_ptr + fresh_k_offset,
                         key_cache_ptr + k_offset)
        v_ptr = tl.where(fresh_lane[:, None], fresh_value_ptr + fresh_v_offset,
                         value_cache_ptr + v_offset)
        K_load = tl.load(k_ptr,
            mask=dim_mask[:, None] & valid_key[None, :], other=0.0)
        V_load = tl.load(v_ptr,
            mask=dim_mask[None, :] & valid_key[:, None], other=0.0)
'''
    candidate = candidate[:start] + loader + candidate[end:]
    # 准确逆变换核验：变更限定于签名、scope/aliases和loader。
    restored = candidate.replace(loader, old, 1).replace(aliases + scope, '', 1)
    restored = restored.replace(extra, '', 1).replace(
        'def kernel_biv150_prefill_fresh_kv(', 'def kernel_biv150_prefill_stride(', 1)
    if restored != source:
        raise AssertionError('不能精确逆回原stride核')
    ast.parse(candidate)
    return candidate


def build(attention, manager, helpers=None):
    source = transform(inspect.getsource(manager.raw.fn))
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = '<prefill-fresh-kv-' + digest + '.py>'
    full = '@triton.jit\n' + source
    linecache.cache[filename] = (len(full), None, full.splitlines(True), filename)
    namespace = dict(vars(attention))
    exec(compile(full, filename, 'exec'), namespace)
    return namespace['kernel_biv150_prefill_fresh_kv'], source


def private_manager(raw, attention, backend, qmod):
    from triton.runtime.jit import JITFunction
    cloned = JITFunction(raw.fn, version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug, noinline=raw.noinline, repr=raw._repr,
        launch_metadata=raw.launch_metadata)
    return qmod.Manager(attention, backend, {'kernel': raw}, 'kernel', raw, cloned).install()


def add_fresh_kwargs(kwargs, key, value):
    """仅组件显式增参；不安装生产wrapper，不制造contiguous副本。"""
    q = kwargs['query_ptr']
    for tensor in (key, value):
        if (str(tensor.dtype) != 'torch.bfloat16' or tensor.device != q.device
            or tensor.ndim != 3 or tensor.shape != (q.shape[0], 2, 128)
            or tensor.stride(-1) != 1 or any(s <= 0 for s in tensor.stride())):
            raise ValueError('fresh KV descriptor不符')
        if tensor.untyped_storage().data_ptr() == kwargs['output_ptr'].untyped_storage().data_ptr():
            raise ValueError('fresh KV与output别名')
    extra = dict(fresh_key_ptr=key, fresh_value_ptr=value)
    extra.update({name: stride for name, stride in zip(FRESH_STRIDES, (*key.stride(), *value.stride()))})
    return dict(kwargs, **extra)


def machine_summary(compiled):
    assembly = compiled.asm.get('asm', '')
    def number(key):
        match = re.search(r'\b' + key + r'\s*[:=]\s*(\d+)', assembly)
        return int(match[1]) if match else None
    return {key: number(key) for key in ('warp_sgpr_count', 'workitem_vgpr_count',
        'sgpr_spill_count', 'vgpr_spill_count', 'workitem_private_segment_byte_size')}
