"""与原GQA相同tl.exp2原语；只验证FP32 P及BF16舍入边界。"""
import triton
import triton.language as tl

@triton.jit
def probability_reference(score, probability, pbf16):
    row=tl.program_id(0)
    column=tl.arange(0,16)
    s=tl.load(score+row*16+column)
    p=tl.exp2(s-tl.max(s,0))
    tl.store(probability+row*16+column,p)
    tl.store(pbf16+row*16+column,p.to(tl.bfloat16))
