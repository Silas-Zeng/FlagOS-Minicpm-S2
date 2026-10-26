"""固定512MiB BF16连续流读，输出每block的FP32 checksum；无autotune。"""
import triton
import triton.language as tl
@triton.jit
def stream_read_checksum(X, Y, N: tl.constexpr, BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offset = pid * BLOCK + tl.arange(0, BLOCK)
    values = tl.load(X + offset, mask=offset < N, other=0.0).to(tl.float32)
    checksum = tl.sum(values, 0)
    tl.store(Y + pid, checksum)
