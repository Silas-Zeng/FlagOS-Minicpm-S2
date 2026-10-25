"""仅新增差分与机器指令判读合同，不导入框架或设备。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from cache_policy import cache_evidence

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-v3-20261025"
checks = []
check = lambda name, ok: checks.append(name) if ok else (_ for _ in ()).throw(AssertionError(name))
raw = (HERE / "baseline.py").read_bytes()
check("main_0915_production_source_exact", raw == (HERE.parent / "team-main-0915/source/vllm_fl/patches/biv150_gqa_decode.py").read_bytes())
candidate = ast.parse((HERE / "candidate.py").read_text(encoding="utf-8"))
changed = []
for node in ast.walk(candidate):
    if isinstance(node, ast.Call):
        additions = [k for k in node.keywords if k.arg == "cache_modifier"]
        for key in additions:
            check("exact_cg_value", isinstance(key.value, ast.Constant) and key.value.value == ".cg")
            check("only_K_or_V_load", ast.unparse(node.func) == "tl.load" and ast.unparse(node.args[0]) in
                  ("key_cache_ptr + k_offsets", "value_cache_ptr + v_offsets"))
            changed.append(ast.unparse(node.args[0])); node.keywords.remove(key)
check("four_KV_loads_only", len(changed) == 4 and len(set(changed)) == 2)
check("all_other_AST_unchanged", ast.dump(candidate) == ast.dump(ast.parse(raw.decode())))
from prepare import INHERITED
check("inherited_assets_exact", all((HERE / n).read_bytes() == (BASE / n).read_bytes() for n in INHERITED))
owner_old = (BASE / "entry.py").read_text(encoding="utf-8")
owner_new = (HERE / "entry.py").read_text(encoding="utf-8")
check("owner_only_run_name", owner_new.replace('"-gqa-kv-cg-"', '"-gqa-identity-rescale-v2-"') == owner_old)
a = "\tml_lsa_blkload_x1 v1, s[2:5], noreg, noreg, #0, ca\n"
b = a.replace(", ca", ", cg")
check("actual_machine_cg_accepted", cache_evidence(a, b)["candidate_cg_count"] == 1)
for name, left, right in (("same_code_rejected", a, a), ("debug_only_rejected", a, a + '.file 1 "cg"\n'),
                          ("resource_only_rejected", a, a + '.vgpr_count: 50\n'),
                          ("no_machine_load_rejected", "cg", "cg")):
    try:
        cache_evidence(left, right)
    except RuntimeError:
        checks.append(name)
    else:
        raise AssertionError(name)
worker = (HERE / "worker.py").read_text(encoding="utf-8")
check("cache_machine_gate_before_graph_and_timing", worker.index('result["cache_policy"]') < worker.index("arm.graph =") < worker.index("timed_batch(torch"))
check("negative_candidate_absent", "skip_rescale" not in (HERE / "candidate.py").read_text() and "branch_evidence" not in worker)
for path in HERE.glob("*.py"):
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
probe = subprocess.run([sys.executable, "-B", "-X", "utf8", str(HERE / "entry.py"), "--help"],
                       capture_output=True, text=True, encoding="utf8")
check("entry_help_inert", probe.returncode == 0 and "{hotspot,b32}" in probe.stdout)
result = dict(status="CPU_ONLY_PASS", gpu_run=False, checks=checks,
              baseline_sha256=hashlib.sha256(raw).hexdigest(),
              candidate_sha256=hashlib.sha256((HERE / "candidate.py").read_bytes()).hexdigest(),
              inherited_validation="复用 v3 数值/Graph/实际 metadata/空 padding/owner 生命周期；本次未重新运行旧套件")
(HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
