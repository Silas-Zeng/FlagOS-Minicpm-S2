"""只读复核两次mapped原始单层门；不导入框架、不改raw。"""
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[3]
RUNS = ("20261021T184809Z-mapped-decode-sme-fix-gate", "20261021T185023Z-mapped-decode-sme-fix-timing")
EXPECTED = {"gate.py": "ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f",
            "policy.py": "d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b",
            "transform.py": "919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316",
            "candidate_attention.py": "72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


out = {"scope": "BI-V150四形状synthetic单层门；非服务/accuracy/official", "runs": []}
for name in RUNS:
    directory = ROOT / "experiments/framework" / name
    result = json.loads((directory / "results.json").read_text(encoding="utf-8"))
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["exit_code"] == 0 and (directory / "exit-code").read_text().strip() == "0"
    assert result["status"] == "correctness_passed_single_layer_only"
    assert len(result["cases"]) == 4
    for relative, expected in result["source_sha256"].items():
        assert sha(directory / "source" / relative) == expected, (name, relative)
    for relative, expected in EXPECTED.items():
        assert result["source_sha256"][relative] == expected
    for case in result["cases"]:
        assert all(value is True for value in case["correctness"].values())
        assert all(value is True for value in case["next_decode"].values())
        assert all(value["passed"] is True for value in case["fp32_reference"])
        for optional in ("cross_stream", "capture_fallback"):
            if optional in case:
                assert all(value is True for value in case[optional].values())
    assert result["runtime_stats"]["real_forward_selected"] == 0
    assert manifest["postflight"]["port_9031"] == "free"
    assert manifest["postflight"]["free_mib"] == 32700
    assert "No running processes found" in (directory / "postflight-ixsmi.txt").read_text(encoding="utf-8")
    row = {"run": name, "exit": 0, "source_count_verified": len(result["source_sha256"]),
           "result_sha256": sha(directory / "results.json"), "manifest_sha256": sha(directory / "manifest.json"),
           "all_four_correctness_and_next_decode": True, "cross_stream_and_capture": True,
           "real_forward_selected": 0, "stats": result["runtime_stats"],
           "max_difference_from_original_2d": max(c["original_2d_max_abs_difference"] for c in result["cases"]),
           "max_fp32_row_abs_difference": max(x["max_abs_diff"] for c in result["cases"] for x in c["fp32_reference"]),
           "postflight_idle": True, "timing": result["timing"]}
    if result["timing"]:
        rows = result["timings"]
        assert [x["policy"] for x in rows] == ["baseline", "candidate", "candidate", "baseline"]
        assert all(x["calls"] == 32 for x in rows)
        row["timing_recomputed"] = {}
        for kind in ("wall", "event"):
            baseline = statistics.median(x[kind + "_per_call_ms"] for x in rows if x["policy"] == "baseline")
            candidate = statistics.median(x[kind + "_per_call_ms"] for x in rows if x["policy"] == "candidate")
            saved = 1 - candidate / baseline
            expected = result["summary"][kind]
            assert all(math.isclose(value, expected[key], rel_tol=1e-12) for key, value in (
                ("baseline_ms", baseline), ("candidate_ms", candidate), ("fraction_saved", saved)))
            row["timing_recomputed"][kind] = {"baseline_ms": baseline, "candidate_ms": candidate,
                                               "fraction_saved": saved}
    out["runs"].append(row)
out["conclusion"] = "新dummy修复已通过四形状设备门；D29单层含metadata/mapH2D正信号，服务/整模型accuracy仍待。"
out["limits"] = ["原C2 compact oracle逐位一致；新singleton3D与原2D可有小归约差异。",
                 "只有一个synthetic计时形状/一轮ABBA，不能外推E2E或稳定因果收益。",
                 "real_forward_selected0是无runner门预期；服务必须另核real_execute=1。"]
destination = Path(__file__).with_name("device-gates-review.json")
destination.write_text(json.dumps(out, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, ensure_ascii=True, indent=2))
