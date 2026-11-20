"""BI-V150 edge8 BF16 gate/up两阶段partial fusion；仅独立组件，未GPU资格。"""
import torch
import triton
import triton.language as tl


@triton.jit
def half_mm(X, W, GATE, OUT, M: tl.constexpr, FUSE_UP: tl.constexpr,
            BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    # 原生产F.linear用GROUP_M8，而不是旧手工mm的Nfast。
    # 半N+两个全局pass仍会改变实际cache次序，不声称完全保留CTA顺序。
    pid = tl.program_id(0)
    gm = tl.cdiv(M, BM)
    gn = tl.cdiv(6144, BN)
    width = 8 * gn
    group_id = pid // width
    group_size = min(gm - group_id * 8, 8)
    pm = group_id * 8 + pid % group_size
    pn = (pid % width) // group_size
    rm = pm * BM + tl.arange(0, BM)
    rn = pn * BN + tl.arange(0, BN)
    ram = tl.max_contiguous(tl.multiple_of(rm % M, BM), BM)
    rbn = tl.max_contiguous(tl.multiple_of(rn % 6144, BN), BN)
    rk = tl.arange(0, BK)
    xp = X + ram[:, None] * 2048 + rk[None, :]
    wp = W + rk[:, None] + rbn[None, :] * 2048
    if FUSE_UP:
        wp += 6144 * 2048
    acc = tl.zeros((BM, BN), tl.float32)
    for k in range(2048 // BK):
        a = tl.load(xp)
        b = tl.load(wp)
        # 与实际安装linear.py相同的分块dot再FP32加法，不用mm的dot(acc)。
        acc += tl.dot(a, b, allow_tf32=False)
        xp += BK
        wp += BK
    projected = acc.to(tl.bfloat16)
    mask = rm[:, None] < M
    offs = rm[:, None] * 6144 + rn[None, :]
    if FUSE_UP:
        # 原wrapper真实SiLU链：投影先BF16；SiLU内部无额外BF16 round。
        tmp0 = tl.load(GATE + offs, mask, other=0).to(tl.float32)
        tmp5 = projected.to(tl.float32)
        tmp1 = tmp0.to(tl.float32)
        tmp2 = tl.sigmoid(tmp1)
        tmp3 = tmp1 * tmp2
        tmp4 = tmp3.to(tl.float32)
        tmp6 = tmp4 * tmp5
        tl.store(OUT + offs, tmp6, mask)
    else:
        tl.store(GATE + offs, projected, mask)


def launch_into(x, merged_weight, gate_scratch, output, config):
    """两launch都计入候选；scratch由调用者持有且禁止任何输入/输出别名。"""
    m = x.shape[0]
    tensors = (x, merged_weight, gate_scratch, output)
    if (m not in (2030, 2048) or tuple(x.shape) != (m, 2048)
            or tuple(merged_weight.shape) != (12288, 2048)
            or tuple(gate_scratch.shape) != (m, 6144)
            or tuple(output.shape) != (m, 6144)
            or any(t.dtype != torch.bfloat16 or not t.is_contiguous()
                   or not t.is_cuda or t.device != x.device for t in tensors)
            or len({t.untyped_storage().data_ptr() for t in tensors}) != 4):
        raise ValueError('仅M2030/2048、原contiguous BF16 edge gate；四个storage须独立')
    with torch.cuda.device(x.device):
        prop = torch.cuda.get_device_properties(x.device)
        if 'BI-V150' not in prop.name or prop.multi_processor_count != 16:
            raise ValueError('仅BI-V150 16SM；没有生产fallback或adapter')
        required = ('BLOCK_M', 'BLOCK_N', 'BLOCK_K', 'num_warps', 'num_stages', 'num_ctas')
        if (any(type(config.get(k)) is not int for k in required)
                or config.get('SPLIT_K', 1) != 1 or config['num_ctas'] != 1
                or 6144 % config['BLOCK_N'] or 2048 % config['BLOCK_K']
                or any(config[k] <= 0 for k in required)):
            raise ValueError('只接受原实际linear选择的整除、非split配置；不自动调参')
        bm, bn, bk = (config[k] for k in ('BLOCK_M', 'BLOCK_N', 'BLOCK_K'))
        grid = (triton.cdiv(m, bm) * triton.cdiv(6144, bn),)
        common = dict(M=m, BM=bm, BN=bn, BK=bk,
                      num_warps=config['num_warps'], num_stages=config['num_stages'],
                      num_ctas=config['num_ctas'], enable_fp_fusion=True)
        half_mm[grid](x, merged_weight, gate_scratch, output, FUSE_UP=False, **common)
        half_mm[grid](x, merged_weight, gate_scratch, output, FUSE_UP=True, **common)
    return output
