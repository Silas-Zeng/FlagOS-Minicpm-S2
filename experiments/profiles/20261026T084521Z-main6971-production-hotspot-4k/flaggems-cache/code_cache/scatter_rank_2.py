import torch
import triton
import triton.language as tl

from flag_gems.utils import libentry
from flag_gems import runtime
import flag_gems



def heur_block(args):
    if(flag_gems.vendor_name in ['metax', 'iluvatar']):
        return 256
    return 128


def loop_count(args):
    return 4


@libentry()
@triton.heuristics(
    {
        "BLOCK": heur_block,
        "LOOP": loop_count,
    }
)
@triton.jit(do_not_specialize=['N','stride_dim','inp_size_dim','inp_stride_0','inp_stride_1','index_stride_0','index_stride_1','src_stride_0','src_stride_1','shape_0','shape_1'])
def _scatter_jit_function(
    src_strided,
    index,
    inp,
    out,
    inp_stride_0: int, inp_stride_1: int, # stride for inp
    index_stride_0: int, index_stride_1: int, # stride for index
    src_stride_0: int, src_stride_1: int, # stride for src
    shape_0: int, shape_1: int, # shape
    inp_size_dim,
    stride_dim,
    N,
    IS_ADD: tl.constexpr,
    IS_MUL: tl.constexpr,
    BLOCK: tl.constexpr,
    LOOP: tl.constexpr,
    INT32_OFFSET: tl.constexpr
):
    pid = tl.program_id(0)
    if not INT32_OFFSET:
        pid = pid.to(tl.int64)
    offsets = pid * LOOP * BLOCK + tl.arange(0, BLOCK)
    for loop_iter in tl.static_range(LOOP):
        mask = offsets < N
        cur_idx = offsets
        if INT32_OFFSET:
            inp_offsets = tl.zeros((BLOCK, ), dtype=tl.int32)
            idx_offsets = tl.zeros((BLOCK, ), dtype=tl.int32)
            src_offsets = tl.zeros((BLOCK, ), dtype=tl.int32)
        else:
            inp_offsets = tl.zeros((BLOCK, ), dtype=tl.int64)
            idx_offsets = tl.zeros((BLOCK, ), dtype=tl.int64)
            src_offsets = tl.zeros((BLOCK, ), dtype=tl.int64)
        if INT32_OFFSET:
            shape_1 = shape_1.to(tl.int32)
            inp_stride_1 = inp_stride_1.to(tl.int32)
            index_stride_1 = index_stride_1.to(tl.int32)
            src_stride_1 = src_stride_1.to(tl.int32)
        mod = cur_idx % shape_1
        inp_offsets += mod * inp_stride_1
        idx_offsets += mod * index_stride_1
        src_offsets += mod * src_stride_1
        cur_idx = cur_idx // shape_1
        if INT32_OFFSET:
            shape_0 = shape_0.to(tl.int32)
            inp_stride_0 = inp_stride_0.to(tl.int32)
            index_stride_0 = index_stride_0.to(tl.int32)
            src_stride_0 = src_stride_0.to(tl.int32)
        mod = cur_idx % shape_0
        inp_offsets += mod * inp_stride_0
        idx_offsets += mod * index_stride_0
        src_offsets += mod * src_stride_0
        cur_src = tl.load(src_strided + src_offsets, mask=mask, other=0)
        cur_index = tl.load(index + idx_offsets, mask=mask, other=0)
        if INT32_OFFSET:
            cur_index = cur_index.to(tl.int32)
            stride_dim = stride_dim.to(tl.int32)
        dim_offsets = cur_index * stride_dim
        inp_offsets += dim_offsets

        if IS_ADD: 
            tl.atomic_add(out + inp_offsets, cur_src, mask=mask, sem='relaxed')
        elif IS_MUL: 
            stop = tl.where(mask, 0, 1).to(tl.int1)
            block_stop = False
            while not block_stop:
                cur_inp = tl.load(out + inp_offsets, mask=mask, other=0)
                res = tl.where(stop, cur_inp, cur_inp * cur_src)
                cas_res = tl.atomic_cas(out + inp_offsets, cur_inp, res, sem='relaxed')
                stop |= cur_inp == cas_res
                block_stop = tl.sum(stop.to(tl.int32)) == BLOCK
        else: 
            tl.store(out + inp_offsets, cur_src, mask=mask)
        offsets += BLOCK


def _scatter_wrapper(src_strided, index, inp, out, dim_size, dim_stride, N, reduce: tl.constexpr=None, int32_offset: tl.constexpr=None):
    inp_strides = list(inp.stride())
    index_strides = index.stride()
    src_strides = src_strided.stride()
    index_shapes = list(index.shape)
    inp_size_dim = dim_size
    stride_dim = dim_stride
    IS_ADD = reduce == "add"
    IS_MUL = reduce == "multiply"
    int32_offset = int32_offset or True
    grid = lambda meta: (
        triton.cdiv(N, meta["BLOCK"] * meta["LOOP"]), 
    )
    _scatter_jit_function[grid](
        src_strided, index, inp, out, 
        inp_strides[0], inp_strides[1],
        index_strides[0], index_strides[1],
        src_strides[0], src_strides[1],
        index_shapes[0], index_shapes[1],
        inp_size_dim,
        stride_dim,
        N,
        IS_ADD,
        IS_MUL,
        INT32_OFFSET=int32_offset,
    )
    return out
