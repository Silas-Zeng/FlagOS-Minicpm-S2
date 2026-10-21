"""纯整数成本模型，不是服务几何/设备测试；仅检验BQ16向下对齐假设。"""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def ceildiv(x, divisor):
    return (x + divisor - 1) // divisor


def count(prompt, decode_count, align):
    context, chunks = 0, []
    while context < prompt:
        query = min(prompt - context, 2048 - decode_count)
        if align and query < prompt - context:
            query = query // 16 * 16
        valid = ceildiv(query, 16)
        # actual59d9 causal/no-window/2D: min(ctx+qblock*BQ+BQ,seq_len), cdiv(T64)
        tile_pairs = sum(ceildiv(min(context + q * 16 + 16, context + query), 64)
                         for q in range(valid))
        chunks.append({"context": context, "query": query, "linear_m": query + decode_count,
                       "valid_query_ctas_per_kv_head": valid,
                       "launched_query_ctas_per_kv_head": query // 16 + 1,
                       "qk_tile_pairs_per_kv_head": tile_pairs,
                       "m_tiles_if_fixed_bm256": ceildiv(query + decode_count, 256)})
        context += query
    return {"chunks": chunks, "forward_count": len(chunks),
            **{key: sum(chunk[key] for chunk in chunks) for key in (
                "valid_query_ctas_per_kv_head", "launched_query_ctas_per_kv_head",
                "qk_tile_pairs_per_kv_head", "m_tiles_if_fixed_bm256")}}


paths = {"attention": ROOT / "experiments/framework/20261021T212106Z-kv-capacity-context16k-long/postflight-sources/triton_unified_attention.py",
         "helpers": HERE / "triton_attention_helpers.actual59d9.py",
         "c3": ROOT / "patches/framework/biv150_mixed_decode.py",
         "runner": ROOT / "experiments/official/20261021T092944Z-sql-mixed-official/source/plugin/vllm_fl/worker/model_runner.py"}
source_hashes = {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in paths.items()}
assert source_hashes == {
    "attention": "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f",
    "helpers": "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1",
    "c3": "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42",
    "runner": "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1"}
rows = []
for decode in (1, 15, 16, 17, 29, 31):
    original, aligned = count(16384, decode, False), count(16384, decode, True)
    rows.append({"synthetic_constant_decode_count": decode, "original": original, "aligned": aligned,
                 "tile_pair_reduction_percent": (1 - aligned["qk_tile_pairs_per_kv_head"] / original["qk_tile_pairs_per_kv_head"]) * 100})
result = {"kind": "整数反证模型，非kernel benchmark/真实batch统计，不导入Torch/Triton",
          "scope": "16K prompt、C3完整decode前缀已拆且仅一prefill suffix、ctx从0起、2D causal BQ16/T64；D恒定只是构造假设",
          "source_sha256": source_hashes, "rows": rows,
          "full_m_original_over_d1_to31": [2048],
          "full_m_aligned_over_d1_to31": sorted({d + (2048 - d) // 16 * 16 for d in range(1, 32)}),
          "limits": ["BM256是固定配置条件模型，不保证新M会命中原MM autotune配置或同DB。",
                     "query CTA计数/causal loop整数不是访存字节、cache命中或延迟。",
                     "不实现调度策略、不改2048预算/FCFS/原source，不是设备验证。"]}
(HERE / "geometry.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps([{"D": row["synthetic_constant_decode_count"],
                   "original_forwards": row["original"]["forward_count"],
                   "aligned_forwards": row["aligned"]["forward_count"],
                   "valid_q": [row[k]["valid_query_ctas_per_kv_head"] for k in ("original", "aligned")],
                   "launch_q": [row[k]["launched_query_ctas_per_kv_head"] for k in ("original", "aligned")],
                   "qk_reduction_percent": row["tile_pair_reduction_percent"],
                   "mm_mtiles": [row[k]["m_tiles_if_fixed_bm256"] for k in ("original", "aligned")]} for row in rows]))
