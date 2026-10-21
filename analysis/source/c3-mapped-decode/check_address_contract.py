"""CPU address/coverage proof for an unimplemented mapped Attention design.

This is a mathematical model of the pinned helper's virtual-CTA address rule,
not a Triton interpreter, GPU kernel, runner patch or performance simulation.
"""
from bisect import bisect_right
import hashlib
from itertools import accumulate
import json
from pathlib import Path
import random


ROOT = Path(__file__).resolve().parents[3]
SOURCES = {
    "experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/ops/triton_unified_attention.py":
        "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f",
    "experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/ops/triton_attention_helpers.py":
        "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1",
}


def plan(lengths, threshold=64, max_tokens=2048):
    if (not lengths or any(type(length) is not int or length <= 0 for length in lengths)
            or sum(lengths) > max_tokens):
        return None
    selected = [request for request, length in enumerate(lengths) if length == 1]
    prefix = next((request for request, length in enumerate(lengths) if length != 1), len(lengths))
    if not selected or len(selected) == len(lengths) or len(selected) > threshold or len(selected) == prefix:
        return None
    return selected


def original_2d_rows(lengths, *, skip_single=False, block_q=16):
    """Pinned resolve_seq_and_query_len/find_seq_idx integer rule only."""
    cu = [0, *accumulate(lengths)]
    virtual_starts = [offset // block_q + request for request, offset in enumerate(cu[:-1])]
    written = []
    for program in range(cu[-1] // block_q + len(lengths)):
        request = bisect_right(virtual_starts, program) - 1
        local = program - virtual_starts[request]
        length = lengths[request]
        if local * block_q >= length or (skip_single and length == 1):
            continue
        written.extend(cu[request] + offset for offset in range(local * block_q, min((local + 1) * block_q, length)))
    assert len(written) == len(set(written)), "2D wrote a token more than once"
    return set(written)


def checked(lengths):
    assert original_2d_rows(lengths) == set(range(sum(lengths)))
    selected = plan(lengths)
    if selected is None:
        return False
    cu = [0, *accumulate(lengths)]
    assert selected == sorted(set(selected))
    # The reducer writes one real output token per selected request, whereas
    # all intermediate buffers use compact ordinal, never cu[request].
    output_rows = {cu[request] for request in selected}
    scratch_rows = set(range(len(selected)))
    assert len(output_rows) == len(selected) and max(scratch_rows) < 64
    assert all(lengths[request] == 1 and 0 <= cu[request] < sum(lengths) for request in selected)
    prefill_rows = original_2d_rows(lengths, skip_single=True)
    assert not prefill_rows & output_rows
    assert prefill_rows | output_rows == set(range(sum(lengths)))
    # BM16/GQA8 has two query positions; only qpos0 may store for query_len1.
    assert {compact + qpos for compact in scratch_rows for qpos in (0, 1) if qpos < 1} == scratch_rows
    return True


def main():
    for relative, expected in SOURCES.items():
        assert hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected, relative
    cases = [[2048], [1] * 62, [1, 1, 7], [7, 1, 1], [1, 2019] + [1] * 28,
             [1, 7, 1, 9, 1], [7, 1, 9, 1, 1], [2] * 190 + [1] * 64 + [3, 4],
             [2] + [1] * 65, [2, 1], [1, 2, 1, 2, 1]]
    selected = sum(checked(case) for case in cases)
    generator = random.Random(721201)
    for _ in range(300):
        lengths = [1 if generator.random() < 0.7 else generator.randint(2, 31)
                   for _ in range(generator.randint(1, 256))]
        selected += checked(lengths)
        selected += checked(list(reversed(lengths)))
    assert plan([2, 1, 1]) == [1, 2]
    assert plan([1, 2, 1]) == [0, 2]
    assert plan([2] + [1] * 65) is None
    assert plan([1, 1, 7]) is None
    print(json.dumps({"status": "CPU_address_contract_pass", "explicit_cases": len(cases),
                      "random_and_reversed_cases": 600, "selected_cases": selected,
                      "kernel_implemented": False, "GPU_executed": False,
                      "limits": "Only integer coverage/address mathematics; no tensor, compiler, FP, stream or timing proof."}, indent=2))


if __name__ == "__main__":
    main()
