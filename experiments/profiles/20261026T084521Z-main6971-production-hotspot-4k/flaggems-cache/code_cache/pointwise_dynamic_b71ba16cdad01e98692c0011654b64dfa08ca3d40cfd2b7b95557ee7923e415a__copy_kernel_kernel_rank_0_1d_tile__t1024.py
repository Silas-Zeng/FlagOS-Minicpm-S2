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


def _copy_kernel_wrapper_rank_0(in0: Union[torch.Tensor, StridedBuffer], /, *, out0: Union[torch.Tensor, StridedBuffer]): 
    """Generated wrapper function with Pointwise: StridedBuffer, StridedBuffer(a1!) -> StridedBuffer(a1!)"""
    assert in0.shape == out0.shape, 'operand shapes mismatch'
    # task partitioning
    num_warps = 1
    num_ctas = 1
    grid = (num_ctas, 1, 1)
    # kernel launch
    in0_strides = in0.stride()
    out0_strides = out0.stride()
    with torch_device_fn.device(in0.device.index):
        _copy_kernel_kernel_rank_0[grid](
            in0, out0,
            num_warps=num_warps,
        )
    return out0

@triton.jit
def _copy_kernel(src):
    return src

@libentry()
@triton.jit
def _copy_kernel_kernel_rank_0(
    in0_ptr: tl.tensor, # of tl.pointer_type
    out0_ptr: tl.tensor, # of tl.pointer_type
):
    # loads
    in0 = tl.load(in0_ptr).to(in0_ptr.type.element_ty) # workaround the bug on bool, we should use the pointer's dtype)

    # compute
    out0 = _copy_kernel(in0)

    # stores
    tl.store(out0_ptr, out0.to(out0_ptr.type.element_ty))

