import triton
import triton.language as tl

from flag_gems.utils import libentry, libtuner
from flag_gems import runtime
from flag_gems.utils.shape_utils import volume
from flag_gems.utils import triton_lang_extension as ext


@libentry()
@libtuner(
    configs=[
        triton.Config({'BLOCK_SIZE0': 8, 'BLOCK_SIZE1': 128}, num_warps=4, num_stages=2),
        triton.Config({'BLOCK_SIZE0': 16, 'BLOCK_SIZE1': 128}, num_warps=4, num_stages=2),
    ],
    key=["M"],
    strategy=["align32"],
    warmup=5,
    rep=10,
)
@triton.jit
def _index_linearized_jit_function(
    input_ptr,
    indices0_ptr,
    out_ptr,
    M,
    N,
    BLOCK_SIZE0: tl.constexpr,
    BLOCK_SIZE1: tl.constexpr,
):
    pid_p = tl.program_id(axis=0)
    pid_m = tl.program_id(axis=1)
    pid_n = tl.program_id(axis=2)

    index_offsets = pid_m * BLOCK_SIZE0 + tl.arange(0, BLOCK_SIZE0)
    suffix_offsets = pid_n * BLOCK_SIZE1 + tl.arange(0, BLOCK_SIZE1)
    index_mask = index_offsets < M

    raw0 = tl.load(indices0_ptr + index_offsets, mask=index_mask, other=0)
    idx0 = tl.where(raw0 < 0, raw0 + 56, raw0)

    linear_index = idx0 * 1
    valid_index = (idx0 >= 0) & (idx0 < 56)

    src_offsets = (
        (pid_p * 56 + linear_index[:, None]) * 2048
        + suffix_offsets[None, :]
    )
    out_offsets = (
        (pid_p * M + index_offsets[:, None]) * 2048
        + suffix_offsets[None, :]
    )
    mask = index_mask[:, None] & valid_index[:, None] & (suffix_offsets[None, :] < 2048)

    cur_value = tl.load(input_ptr + src_offsets, mask=mask)
    tl.store(out_ptr + out_offsets, cur_value, mask=mask)


def _index_linearized_wrapper(input, start_dim, indices, out):
    M = indices[0].numel()
    P = 1
    N = 2048

    grid = lambda meta: (
        P,
        triton.cdiv(M, meta['BLOCK_SIZE0']),
        triton.cdiv(N, meta['BLOCK_SIZE1']),
    )

    _index_linearized_jit_function[grid](
        input,
        indices[0],
        out,
        M,
        N,
    )
    return input


