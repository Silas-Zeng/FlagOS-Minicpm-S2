"""独立long组件：原2D数学按4个绝对K panel分段，split-major partial。

不安装生产，不改变已有IS_3D路由；单panel内原body逐字不动。
"""
from __future__ import annotations
import ast
import hashlib
import inspect
import linecache
import re

STRIDES = ('block_table_stride', 'query_stride_0', 'query_stride_1',
    'output_stride_0', 'output_stride_1', 'stride_k_cache_0', 'stride_k_cache_1',
    'stride_k_cache_2', 'stride_v_cache_0', 'stride_v_cache_1', 'stride_v_cache_2')

HEADER = '    Q_IS_FP8: tl.constexpr = False,\n):\n'
NEW_HEADER = '''    Q_IS_FP8: tl.constexpr = False,
    panel_output_ptr=None,
    panel_max_ptr=None,
    panel_expsum_ptr=None,
    PANEL_TOKENS: tl.constexpr = 0,
    PANEL_COUNT: tl.constexpr = 4,
):
'''
LOOP_MARKER = '    # iterate through tiles (now limited to the sliding window range)\n'
PANEL_BOUNDS = '''    # New implementation: split-major cache panels, not generic IS_3D routing.
    tl.static_assert(not IS_3D)
    tl.static_assert(PANEL_COUNT == 4 and PANEL_TOKENS > 0)
    panel_idx = tl.program_id(2)
    panel_tiles = tl.cdiv(seq_len, PANEL_COUNT * TILE_SIZE)
    loop_lo = tl.maximum(loop_lo, panel_idx * panel_tiles)
    loop_hi = tl.minimum(loop_hi, (panel_idx + 1) * panel_tiles)

'''
EPILOGUE = '    # ---- Epilogue ---------------------------------------------------------\n'
PANEL_EPILOGUE = '''    # Four FP32 partials. No visits: M=-inf; fully masked visits may M=0.
    # Both empty cases write L=0 and acc=0; reducer validity is defined by L>0.
    panel_scalar_offset = ((panel_idx * PANEL_TOKENS + query_offset_0.to(tl.int64))
                           * num_query_heads + query_offset_1)
    panel_offsets = panel_scalar_offset[:, None] * HEAD_SIZE_PADDED + offs_d[None, :]
    panel_valid = query_mask_0 & query_mask_1
    tl.store(panel_output_ptr + panel_offsets, acc,
             mask=panel_valid[:, None] & dim_mask[None, :])
    tl.store(panel_max_ptr + panel_scalar_offset, M, mask=panel_valid)
    tl.store(panel_expsum_ptr + panel_scalar_offset, L, mask=panel_valid)
'''


def transform(source):
    assert source.count(HEADER) == source.count(LOOP_MARKER) == source.count(EPILOGUE) == 1
    assert 'L = tl.zeros([BLOCK_M], dtype=tl.float32)' in source
    assert source.count('def kernel_biv150_prefill_stride(') == 1
    front, old_epilogue = source.split(EPILOGUE)
    assert old_epilogue.lstrip().startswith('if IS_3D:')
    candidate = front.replace(HEADER, NEW_HEADER, 1).replace(LOOP_MARKER, PANEL_BOUNDS + LOOP_MARKER, 1)
    candidate += EPILOGUE + PANEL_EPILOGUE
    restored = candidate.split(EPILOGUE)[0].replace(NEW_HEADER, HEADER, 1).replace(PANEL_BOUNDS + LOOP_MARKER, LOOP_MARKER, 1)
    assert restored + EPILOGUE + old_epilogue == source
    # The original hot body, including every float expression, is byte-identical.
    old_body = source.split(LOOP_MARKER, 1)[1].split(EPILOGUE, 1)[0]
    assert candidate.split(LOOP_MARKER, 1)[1].split(EPILOGUE, 1)[0] == old_body
    ast.parse(candidate)
    return candidate


def build(attention, manager, helpers):
    source = transform(inspect.getsource(manager.raw.fn))
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = '<prefill-panel4-' + digest + '.py>'
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
    # Original Q transform/guards, no new IR editor or qualification inheritance.
    return qmod.Manager(attention, backend, {'kernel': raw}, 'kernel', raw, cloned).install()


def machine_summary(compiled):
    assembly = compiled.asm.get('asm', '')
    def number(key):
        match = re.search(r'\b' + key + r'\s*[:=]\s*(\d+)', assembly)
        return int(match[1]) if match else None
    return dict(sgpr=number('warp_sgpr_count'), vgpr=number('workitem_vgpr_count'),
        sgpr_spill=number('sgpr_spill_count'), vgpr_spill=number('vgpr_spill_count'),
        limits='实际资源只作诊断，不证明occupancy/cache命中或收益')
