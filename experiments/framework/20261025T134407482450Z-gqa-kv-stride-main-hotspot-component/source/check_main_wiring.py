"""复用既有特化/变stride审核，只验证原生产对照的新增接线。"""
import ast
import hashlib
import json
from pathlib import Path
from stride_evidence import inspect_asm, specialization_evidence

P = Path(__file__).resolve().parent
OLD = P.parent / "gqa-kv-stride-constexpr-20261025"
checks = []
def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)

base = (P / "baseline.py").read_text(encoding="utf8")
candidate = (P / "candidate.py").read_text(encoding="utf8")
check("base_exact_team_production", (P / "baseline.py").read_bytes() ==
      (P.parent / "team-main-0915/source/vllm_fl/patches/biv150_gqa_decode.py").read_bytes())
old = ast.parse((OLD / "candidate.py").read_text(encoding="utf8"))
removed = 0
for node in ast.walk(old):
    if isinstance(node, ast.Call):
        for kw in list(node.keywords):
            if kw.arg == "cache_modifier":
                assert isinstance(kw.value, ast.Constant) and kw.value.value == ".cg"
                node.keywords.remove(kw)
                removed += 1
check("only_cg_removed_from_reviewed_stride_candidate", removed == 4 and ast.dump(old) == ast.dump(ast.parse(candidate)))
check("alternate_stride_review_reused_unchanged", (P / "alternate_stride.py").read_bytes() == (OLD / "alternate_stride.py").read_bytes())
check("owner_only_unique_run_name", (P / "entry.py").read_text(encoding="utf8").replace(
    '"-gqa-kv-stride-main-"', '"-gqa-kv-stride-constexpr-"') == (OLD / "entry.py").read_text(encoding="utf8"))
newworker = (P / "worker.py").read_text(encoding="utf8")
oldworker = (OLD / "worker.py").read_text(encoding="utf8")
expected = oldworker.replace("1043497f0bb0049ba42ae4a01d78bebf88cf632bbfada700c400b6d1db86c44c", "2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1")
expected = expected.replace("gqa_cg_stride_control", "gqa_stride_control").replace("gqa_cg_stride_candidate", "gqa_stride_candidate")
expected = expected.replace("双臂共同 cg，只度量新增 stride 特化", "双臂共同原生产无 cg，只度量新增 stride 特化")
check("worker_only_baseline_binding_changes", newworker == expected)
a = "ml_lsa_blkload_x1 v1, s[2:5], noreg, noreg, #0, ca\n" + "".join(
    f".loc 1 {line} 19\nsl_mul_u64_u32 s[2:3], s4, s5\nsl_mull_u32 s6, s7, s8\n"
    for line in inspect_asm("", base)["page_source_lines"])
b = "ml_lsa_blkload_x1 v1, s[2:5], noreg, noreg, #0, ca\n"
check("normal_ca_and_mul_contract", specialization_evidence(a, b, base, candidate)["integer_multiply_reduced"])
try:
    specialization_evidence(a, b.replace(", ca", ", cg"), base, candidate)
except RuntimeError:
    checks.append("unexpected_cg_rejected")
else:
    raise AssertionError("unexpected cg")
for f in P.glob("*.py"):
    ast.parse(f.read_text(encoding="utf8"))
check("all_source_AST_valid", True)
result = dict(status="CPU_NEW_WIRING_PASS", checks=checks, gpu_run=False,
              previous_cpu_receipt_sha256=hashlib.sha256((OLD / "cpu-check.json").read_bytes()).hexdigest(),
              previous_package_sha256=hashlib.sha256((OLD / "entry.tar.gz").read_bytes()).hexdigest(),
              baseline_sha256=hashlib.sha256(base.encode()).hexdigest(),
              candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
              reused="原24项CPU特化/变stride/Graph接线审据复用，本次未重跑旧套件")
(P / "main-wiring-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps(result, ensure_ascii=False))
