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
    marker='    if IS_3D:\n        tiles_per_segment = cdiv_fn(seq_len, NUM_SEGMENTS_PER_SEQ * TILE_SIZE)'
    reversal='    # 同一序列内先发较长causal query块；不改变请求/采样或K归约顺序。\n    if not IS_3D and USE_CAUSAL and not USE_PER_SEQ_CAUSAL and not USE_MM_PREFIX and not USE_SINKS and not USE_ALIBI_SLOPES and not USE_QQ_BIAS and not USE_SOFTCAP and not SLIDING_WINDOW and CHUNK_LOOKBACK < 0 and KV_QUANT_MODE == 0 and not USE_TD and not USE_TD_QO and num_query_heads == 16 and num_queries_per_kv == 8 and HEAD_SIZE == 128 and BLOCK_M == 128 and BLOCK_Q == 16 and TILE_SIZE == 64:\n        q_block_local_idx = tl.cdiv(cur_batch_query_len, BLOCK_Q) - 1 - q_block_local_idx\n\n'
    assert source.count(marker)==1
    candidate=source.replace(marker,reversal+marker,1)
    assert candidate.replace(reversal+marker,marker,1)==source
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
