from vllm.triton_utils import tl, triton

@triton.jit
def _fused_cast_temperature_stats(
    INPUT,
    TEMPERATURE,
    stride_input,
    LOGITS,
    MAX_PART,
    SUM_PART,
    stride_row,
    VOCAB_SIZE: tl.constexpr,
    NUM_SPLITS: tl.constexpr,
    MAX_SPLITS: tl.constexpr,
    TILES_PER_SPLIT: tl.constexpr,
    BLOCK: tl.constexpr,
):
    row = tl.program_id(0)
    split = tl.program_id(1)
    offs = tl.arange(0, BLOCK)
    start = split * TILES_PER_SPLIT * BLOCK
    row_max = float("-inf")
    row_sum = 0.0
    temperature = tl.load(TEMPERATURE + row)
    for tile in range(TILES_PER_SPLIT):
        idx = start + tile * BLOCK + offs
        values = tl.load(
            INPUT + row * stride_input + idx,
            mask=idx < VOCAB_SIZE,
            other=float("-inf"),
        )
        values = values.to(tl.float32) / temperature
        tl.store(LOGITS + row * stride_row + idx, values, mask=idx < VOCAB_SIZE)
        tile_max = tl.max(values, axis=0)
        new_max = tl.maximum(row_max, tile_max)
        safe_new_max = tl.where(new_max == float("-inf"), 0.0, new_max)
        old_scale = tl.where(
            row_max == float("-inf"),
            0.0,
            tl.exp(row_max - safe_new_max),
        )
        row_sum = row_sum * old_scale + tl.sum(
            tl.exp(values - safe_new_max), axis=0
        )
        row_max = new_max
    tl.store(MAX_PART + row * MAX_SPLITS + split, row_max)
    tl.store(SUM_PART + row * MAX_SPLITS + split, row_sum)
