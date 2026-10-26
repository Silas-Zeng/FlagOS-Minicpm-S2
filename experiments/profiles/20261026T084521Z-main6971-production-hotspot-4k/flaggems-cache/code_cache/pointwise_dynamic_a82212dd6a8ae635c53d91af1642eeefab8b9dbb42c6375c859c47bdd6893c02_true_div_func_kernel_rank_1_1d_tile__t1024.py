import math
from typing import Union
import torch
import triton
from triton import language as tl

from flag_gems.utils.shape_utils import (
    heuristics_for_tile_size,
    heuristics_for_num_warps,
    stride_order,
)
from flag_gems.utils.tensor_wrapper import StridedBuffer
from flag_gems.utils.libentry import libentry
from flag_gems.utils import triton_lang_extension as ext
from flag_gems.runtime import torch_device_fn
from flag_gems.utils.triton_lang_extension import div_rn, fmod, trunc


@triton.jit
def _int_floordiv(x, y):
    # TODO: request Triton to add an integer remainder builtin
    # The semantic of Triton floordiv differs from Pytorch/Numpy
    # Triton floordiv equates to
    #     (x - np.fmod(x, y)) / y
    # whereas Pytorch floordiv is
    #     (x - np.remainder(x, y)) y
    # The results show a one off difference when
    #     C1) x and y have opposite signs
    # and C2) x is not multiples of y.
    # Apart from the above, there's an erroneous case x // 0 returns -1
    # whereas in Pytorch x // 0 returns -1 if x >=0 and -2 if x < 0
    # but this special case is coalesced into the c1 and c2 check so
    # there's extra handling.
    r = x % y
    c1 = r != 0
    c2 = (x < 0) ^ (y < 0)
    return tl.where(c1 & c2, x // y - 1, x // y)

@triton.jit
def _float_floordiv(x, y):
    # Cast to float32 for fmod/div_rn which only support fp32/fp64 on CUDA
    orig_dtype = x.dtype
    x_fp32 = x.to(tl.float32)
    y_fp32 = y.to(tl.float32)

    # NOTE: fmod's sign is the same as the dividend
    remainder = fmod(x_fp32, y_fp32)
    imperfect = remainder != 0.0
    different_sign = (x_fp32 < 0) ^ (y_fp32 < 0)

    # NOTE: we have to use div_rn explicitly here
    q = div_rn(x_fp32 - remainder, y_fp32)
    q = tl.where(imperfect & different_sign, q - 1, q)

    floor_q = tl.math.floor(q)
    c = q - floor_q > 0.5
    floor_q = tl.where(c, floor_q + 1.0, floor_q)

    q_is_zeros = q == 0.0
    floor_q = tl.where(q_is_zeros, tl.where(different_sign, -0.0, 0.0), floor_q)

    is_div_by_zero = y_fp32 == 0.0
    float_division = x_fp32 / y_fp32
    out = tl.where(is_div_by_zero, float_division, floor_q)
    return out.to(orig_dtype)

def true_div_func_wrapper_rank_1(in0: Union[torch.Tensor, StridedBuffer], in1: Union[torch.Tensor, StridedBuffer], /, *, out0: Union[torch.Tensor, StridedBuffer]): 
    """Generated wrapper function with Pointwise: StridedBuffer, StridedBuffer, StridedBuffer(a1!) -> StridedBuffer(a1!)"""
    assert in0.shape == in1.shape == out0.shape, 'operand shapes mismatch'
    # task partitioning
    shape = out0.shape
    num_tasks = out0.numel()
    if num_tasks == 0:
        return out0
    tile_sizes = heuristics_for_tile_size(1024, num_tasks)
    tile_size = tile_sizes[0]
    num_tiles = triton.cdiv(num_tasks, tile_size)
    num_ctas = min(65536, num_tiles)
    tiles_per_cta = triton.cdiv(num_tiles, num_ctas)
    num_warps = heuristics_for_num_warps(tile_size)
    one_tile_per_cta = tiles_per_cta==1
    grid = (num_ctas, 1, 1)
    # kernel launch
    in0_strides = in0.stride()
    in1_strides = in1.stride()
    out0_strides = out0.stride()
    with torch_device_fn.device(in0.device.index):
        true_div_func_kernel_rank_1[grid](
            in0, in1, out0,
            in0_strides[0], # stride for in0
            in1_strides[0], # stride for in1
            out0_strides[0], # stride for out0
            shape[0], # task indexing space
            num_tasks, # num tasks
            tiles_per_cta=tiles_per_cta, # tiles_per_cta
            tile_size=tile_size,
            one_tile_per_cta=one_tile_per_cta,
            num_warps=num_warps,
        )
    return out0

@triton.jit
def true_div_func(x, y):
    return x / y

@libentry()
@triton.jit
def true_div_func_kernel_rank_1(
    in0_ptr: tl.tensor, # of tl.pointer_type
    in1_ptr: tl.tensor, # of tl.pointer_type
    out0_ptr: tl.tensor, # of tl.pointer_type
    in0_stride0: int, # strides for in0
    in1_stride0: int, # strides for in1
    out0_stride0: int, # strides for out0
    s0, # task_space
    num_tasks,
    tiles_per_cta: int,
    tile_size: tl.constexpr,
    one_tile_per_cta: tl.constexpr,
):
    pid = ext.program_id(0)
    if one_tile_per_cta: # monolitic kernel style
        tile_id = pid
        tid = tile_id * tile_size + tl.arange(0, tile_size)
        mask = tid < num_tasks
        i0 = tid

        # loads
        in0 = tl.load(in0_ptr + i0 * in0_stride0, mask=mask).to(in0_ptr.type.element_ty)
        in1 = tl.load(in1_ptr + i0 * in1_stride0, mask=mask).to(in1_ptr.type.element_ty)

        # compute
        out0 = true_div_func(in0, in1)

        in0 = tl.store(out0_ptr + i0 * out0_stride0, out0, mask=mask)
    else: # grid-stride-loop style kernel
        num_ctas = ext.num_programs(0)
        for j in range(0, tiles_per_cta):
            tile_id = pid + j * num_ctas
            tid = tile_id * tile_size + tl.arange(0, tile_size)
            mask = tid < num_tasks
            i0 = tid

            # loads
            in0 = tl.load(in0_ptr + i0 * in0_stride0, mask=mask).to(in0_ptr.type.element_ty)
            in1 = tl.load(in1_ptr + i0 * in1_stride0, mask=mask).to(in1_ptr.type.element_ty)

            # compute
            out0 = true_div_func(in0, in1)

            in0 = tl.store(out0_ptr + i0 * out0_stride0, out0, mask=mask)

