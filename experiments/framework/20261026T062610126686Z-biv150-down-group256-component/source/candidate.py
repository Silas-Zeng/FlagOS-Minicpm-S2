"""独立down K256分组W8A8原型；只能由root的设备owner启动组件。"""
import torch
import triton
import triton.language as tl

K = 6144
N = 2048
GROUP = 256
GROUPS = 24
CONFIG = dict(BM=32, BN=64, BK=256, num_warps=4, num_stages=2,
              enable_fp_fusion=False)


@triton.jit
def quantize_groups(X, Q, S, ROWS: tl.constexpr, K: tl.constexpr,
                    G: tl.constexpr, GROUPS: tl.constexpr):
    row = tl.program_id(0)
    group = tl.program_id(1)
    j = tl.arange(0, G)
    x = tl.load(X + row * K + group * G + j).to(tl.float32)
    peak = tl.maximum(tl.max(tl.abs(x), 0), 1.0e-6)
    scale = tl.div_rn(peak, 127.0)
    u = tl.div_rn(x, scale)
    # 明确定义half-away-from-zero，与CPU整数参考一致。
    r = tl.floor(tl.abs(u) + 0.5)
    r = tl.where(u < 0, -r, r)
    q = tl.minimum(127.0, tl.maximum(-127.0, r)).to(tl.int8)
    tl.store(Q + row * K + group * G + j, q)
    tl.store(S + row * GROUPS + group, scale)


@triton.jit
def down_group256(A, AS, W, WS, Y, M: tl.constexpr, N: tl.constexpr,
                  K: tl.constexpr, GROUPS: tl.constexpr,
                  BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    pid = tl.program_id(0)
    r = pid // (N // BN) * BM + tl.arange(0, BM)
    c = pid % (N // BN) * BN + tl.arange(0, BN)
    j = tl.arange(0, BK)
    acc = tl.zeros((BM, BN), tl.float32)
    for group in range(GROUPS):
        kk = group * BK + j
        a = tl.load(A + r[:, None] * K + kk[None, :],
                    mask=r[:, None] < M, other=0)
        w = tl.load(W + c[None, :] * K + kk[:, None])
        part = tl.dot(a, w, out_dtype=tl.int32)
        sa = tl.load(AS + r * GROUPS + group, mask=r < M, other=0.)
        sw = tl.load(WS + c * GROUPS + group)
        scale = sa[:, None] * sw[None, :]
        acc = acc + part.to(tl.float32) * scale
    tl.store(Y + r[:, None] * N + c[None, :], acc.to(tl.bfloat16),
             mask=r[:, None] < M)


@triton.jit(do_not_specialize=['GROUP'])
def group_integer_probe(A, W, OUT, M: tl.constexpr, N: tl.constexpr,
                        K: tl.constexpr, GROUP):
    # 只输出某组前min(M,32)行×前64列，验证INT8 dot ABI；不是性能路径。
    r = tl.arange(0, 32)
    c = tl.arange(0, 64)
    k = GROUP * 256 + tl.arange(0, 256)
    a = tl.load(A + r[:, None] * K + k[None, :], mask=r[:, None] < M, other=0)
    w = tl.load(W + c[None, :] * K + k[:, None])
    value = tl.dot(a, w, out_dtype=tl.int32)
    tl.store(OUT + r[:, None] * 64 + c[None, :], value,
             mask=r[:, None] < M)


def _tensor(t, shape, dtype):
    if tuple(t.shape) != shape or t.dtype != dtype or not t.is_contiguous() or not t.is_cuda:
        raise ValueError('不支持的shape/dtype/layout/device')


def quantize_into(x, q, scales):
    _tensor(x, (x.shape[0], K), torch.bfloat16)
    _tensor(q, tuple(x.shape), torch.int8)
    _tensor(scales, (x.shape[0], GROUPS), torch.float32)
    if x.device != q.device or x.device != scales.device:
        raise ValueError('设备不一致')
    with torch.cuda.device(x.device):
        return quantize_groups[(x.shape[0], GROUPS)](
            x, q, scales, ROWS=x.shape[0], K=K, G=GROUP, GROUPS=GROUPS,
            num_warps=4, num_stages=1, enable_fp_fusion=False)


def pack_weight(weight):
    _tensor(weight, (N, K), torch.bfloat16)
    q = torch.empty((N, K), device=weight.device, dtype=torch.int8)
    scales = torch.empty((N, GROUPS), device=weight.device, dtype=torch.float32)
    quantize_into(weight, q, scales)
    # q原存储就是[N,24,256]，无额外运行时transpose或第二份pack。
    return q, scales


def launch_into(x, wq, ws, out, aq, a_scales):
    m = x.shape[0]
    if not 1 <= m <= 2048:
        raise ValueError('组件仅支持1..2048行；首验2030/2048')
    _tensor(x, (m, K), torch.bfloat16)
    _tensor(wq, (N, K), torch.int8)
    _tensor(ws, (N, GROUPS), torch.float32)
    _tensor(out, (m, N), torch.bfloat16)
    if any(t.device != x.device for t in (wq, ws, out, aq, a_scales)):
        raise ValueError('设备不一致')
    with torch.cuda.device(x.device):
        quantized = quantize_into(x, aq, a_scales)
        gemm = down_group256[(triton.cdiv(m, 32) * 32,)](
            aq, a_scales, wq, ws, out, M=m, N=N, K=K,
            GROUPS=GROUPS, **CONFIG)
    return quantized, gemm
