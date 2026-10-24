"""原门两函数逐行提取；只准备数据，不加载候选。"""
import itertools
from types import SimpleNamespace

def make_data(torch, lengths, kv_len):
    n, total = len(lengths), sum(lengths)
    blocks = (kv_len + 15) // 16
    offsets = [0, *itertools.accumulate(lengths)]
    cu_cpu = torch.tensor(offsets, dtype=torch.int32)
    # Cache and new K/V are realistic layouts; update once before all reads.
    cache = torch.randn((n * blocks, 2, 16, 2, 128), dtype=torch.bfloat16, device="cuda")
    query = torch.randn((total + 3, 16, 128), dtype=torch.bfloat16, device="cuda")
    key = torch.randn((total + 3, 2, 128), dtype=torch.bfloat16, device="cuda")
    value = torch.randn_like(key)
    slots = [row * blocks * 16 + kv_len - length + token
             for row, length in enumerate(lengths) for token in range(length)]
    common = SimpleNamespace(
        num_reqs=n, num_actual_tokens=total, max_query_len=max(lengths), max_seq_len=kv_len,
        query_start_loc_cpu=cu_cpu, query_start_loc=cu_cpu.to("cuda"),
        seq_lens=torch.full((n,), kv_len, dtype=torch.int32, device="cuda"),
        block_table_tensor=torch.arange(n * blocks, dtype=torch.int32, device="cuda").reshape(n, blocks),
        slot_mapping=torch.tensor(slots, dtype=torch.int64, device="cuda"),
        causal=True, mm_req_doc_ranges=None,
    )
    return common, query, key, value, cache

def prepare_pages(torch, common, key, value, kv_len):
    """Noncontiguous physical pages and real reused cached-prefix blocks.

    Input setup may copy page numbers to CPU; the runtime candidate never
    reads metadata values on the host. New-token slots follow the same map.
    """
    rows, blocks = common.block_table_tensor.shape
    table = torch.randperm(rows * blocks, device="cuda", dtype=torch.int64).to(torch.int32).reshape(rows, blocks)
    if rows > 1:
        # Only old KV is shared: all new tokens start beyond position 256.
        table[-1, :16] = table[0, :16]
    common.block_table_tensor = table
    pages = table.cpu().tolist()
    lengths = (common.query_start_loc_cpu[1:] - common.query_start_loc_cpu[:-1]).tolist()
    slots = []
    for row, length in enumerate(lengths):
        for position in range(kv_len - length, kv_len):
            slots.append(pages[row][position // 16] * 16 + position % 16)
    total = common.num_actual_tokens
    common.slot_mapping = torch.tensor(slots + [-1] * 3, dtype=torch.int64, device="cuda")
    key[total:] = float("nan")
    value[total:] = float("nan")
