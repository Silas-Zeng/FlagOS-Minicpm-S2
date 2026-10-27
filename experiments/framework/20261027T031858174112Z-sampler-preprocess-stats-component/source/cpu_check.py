"""不导入Torch/Triton的源码/索引合同；不是设备数值通过。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import struct

from factory import dump, one, forward_transform, sample_transform, histogram_tail_source, kernel_source


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sampler-source", type=Path, required=True)
    parser.add_argument("--histogram-source", type=Path, required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    sampler = args.sampler_source.read_text(encoding="utf-8")
    hist = args.histogram_source.read_text(encoding="utf-8")
    tree = ast.parse(sampler)
    sampler_class = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Sampler")
    receipts = {}
    for name, transform in (("forward", forward_transform), ("sample", sample_transform)):
        original = next(n for n in sampler_class.body if isinstance(n, ast.FunctionDef) and n.name == name)
        module = ast.Module(body=[original], type_ignores=[])
        before = dump(module)
        transformed, receipt = transform(module)
        assert receipt["inverse_ast"] == before
        compile(ast.fix_missing_locations(transformed), "<cpu-only-source-check>", "exec")
        receipts[name] = dict(exact_inverse=True, source_ast_sha256=hashlib.sha256(before.encode()).hexdigest())
    tail, tail_receipt = histogram_tail_source(hist)
    compile(tail, "<cpu-only-tail>", "exec")
    source = kernel_source(hist)
    compile(source, "<cpu-only-candidate>", "exec")
    # Exact BF16->FP32 conversion is a zero-extension of the significand bits.
    finite = zeros = 0
    for bits in range(65536):
        fp32_bits = bits << 16
        value = struct.unpack("<f", struct.pack("<I", fp32_bits))[0]
        if (bits & 0x7f80) != 0x7f80:
            assert struct.unpack("<I", struct.pack("<f", value))[0] == fp32_bits
            finite += 1
        if bits in (0, 0x8000):
            assert struct.unpack("<I", struct.pack("<f", value))[0] == fp32_bits
            zeros += 1
    assert finite == 65280 and zeros == 2
    # Same original one-split/32-tile traversal, exact ownership and tail masks.
    rows, vocab, block, tiles = 64, 130560, 4096, 32
    visited = 0
    for row in range(rows):
        expected = 0
        for tile in range(tiles):
            start, stop = tile * block, min(vocab, (tile + 1) * block)
            assert start == expected and stop >= start
            for idx in (start, stop - 1):
                assert row * vocab + idx < rows * vocab
            visited += stop - start
            expected = stop
        assert expected == vocab
    assert visited == rows * vocab
    report = dict(cpu_only=True, gpu_qualified=False, source_contracts=receipts,
                  histogram_tail=tail_receipt, kernel_exact_byte_inverse=True,
                  bf16_finite_values=finite, signed_zero_patterns=zeros,
                  rows=rows, vocab=vocab, block=block, tiles=tiles,
                  full_index_ownership=visited, original_and_candidate_splits=1,
                  fp32_division="原FlagGems true_div_func x/y；CPU不模拟Corex近似除法或证明设备逐位",
                  sampler_sha256=hashlib.sha256(args.sampler_source.read_bytes()).hexdigest(),
                  histogram_sha256=hashlib.sha256(args.histogram_source.read_bytes()).hexdigest(),
                  candidate_sha256=hashlib.sha256(source.encode()).hexdigest())
    if args.out:
        args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
