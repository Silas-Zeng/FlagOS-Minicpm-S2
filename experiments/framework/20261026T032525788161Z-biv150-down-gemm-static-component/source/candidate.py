"""BI-V150 BF16 down projection的两项固定形状候选；不修改已安装算子。"""
import triton
import triton.language as tl


@triton.jit
def down_gemm(X, W, Y, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr,
              BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    # Shape-specific contiguous X[M,6144], W[2048,6144], Y[M,2048].
    # Keep output tile mapping row-major; do not repeat the old GROUP_M test.
    pid = tl.program_id(0)
    pm = pid // (N // BN)
    pn = pid % (N // BN)
    rows = pm * BM + tl.arange(0, BM)
    cols = pn * BN + tl.arange(0, BN)
    inner = tl.arange(0, BK)
    accumulator = tl.zeros((BM, BN), tl.float32)
    for block in range(K // BK):
        k = block * BK + inner
        x = tl.load(X + rows[:, None] * K + k[None, :],
                    mask=rows[:, None] < M, other=0)
        w = tl.load(W + cols[None, :] * K + k[:, None])
        accumulator = tl.dot(x, w, accumulator)
    tl.store(Y + rows[:, None] * N + cols[None, :],
             accumulator.to(tl.bfloat16), mask=rows[:, None] < M)


CONFIGS = {
    'same_tile_static': dict(BM=256, BN=128, BK=32, num_warps=8, num_stages=2),
    'wide_n_static': dict(BM=128, BN=256, BK=32, num_warps=8, num_stages=2),
}


def launch(x, weight, out, variant):
    assert x.dtype == weight.dtype == out.dtype == __import__('torch').bfloat16
    assert x.is_contiguous() and weight.is_contiguous() and out.is_contiguous()
    assert tuple(weight.shape) == (2048, 6144) and x.shape[1] == 6144
    assert tuple(out.shape) == (x.shape[0], 2048) and 0 < x.shape[0] <= 2048
    c = CONFIGS[variant]
    return down_gemm[(triton.cdiv(x.shape[0], c['BM']) * (2048 // c['BN']),)](
        x, weight, out, M=x.shape[0], N=2048, K=6144, **c)
