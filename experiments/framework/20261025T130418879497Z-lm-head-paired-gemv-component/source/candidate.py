"""仅供 M2 LM-head 组件对照；无全局注册、无模型接线。"""
import triton
import triton.language as tl


@triton.jit
def paired_gemv_kernel(X, W, Y, N: tl.constexpr, K: tl.constexpr,
                       BN: tl.constexpr, BK: tl.constexpr):
    rows = tl.program_id(0) * BN + tl.arange(0, BN)
    lanes = tl.arange(0, BK)
    acc0 = tl.zeros((BN, BK), tl.float32)
    acc1 = tl.zeros((BN, BK), tl.float32)
    for block in range(K // BK):
        k = block * BK + lanes
        # 一份 BF16 权重载荷同时服务两行，避免两个 mv 重读全词表权重。
        w = tl.load(W + rows[:, None] * K + k[None, :],
                    mask=rows[:, None] < N, other=0).to(tl.float32)
        x0 = tl.load(X + k).to(tl.float32)
        x1 = tl.load(X + K + k).to(tl.float32)
        acc0 = acc0 + w * x0[None, :]
        acc1 = acc1 + w * x1[None, :]
    y0 = tl.sum(acc0, axis=1)
    y1 = tl.sum(acc1, axis=1)
    tl.store(Y + rows, y0, mask=rows < N)
    tl.store(Y + N + rows, y1, mask=rows < N)


def launch(x, weight, output):
    import torch
    if not (x.shape == (2, 2048) and weight.shape == (130560, 2048)
            and output.shape == (2, 130560)
            and x.dtype == weight.dtype == output.dtype == torch.bfloat16
            and x.is_cuda and x.device == weight.device == output.device
            and x.stride() == (2048, 1) and weight.stride() == (2048, 1)
            and output.stride() == (130560, 1)):
        raise ValueError('只接受固定 M2/N130560/K2048、连续 BF16 输入输出')
    return paired_gemv_kernel[(4080,)](x, weight, output, 130560, 2048,
        BN=32, BK=256, num_warps=8, num_stages=1, enable_fp_fusion=False)
