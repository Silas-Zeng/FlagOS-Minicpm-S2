"""唯一新增合同：固定六维护路径的显式中间基点；纯离线。"""
from pathlib import Path
import hashlib
import json
import runpy
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
module = HERE / "publish_experiment_pr.py"
ns = runpy.run_path(str(module))
delta = ns["local_delta"](ROOT, ROOT / "tmp/publish-team-rebuild-final-20261022.json",
                          "ed86941", "8af67cc", "ed86941")
accepted = delta["accepted_maintenance"]
assert accepted["local_revision"] == "ed8694129aae10e181433cbc3c1ac26593a70473"
assert set(accepted["paths"]) == ns["MAINTENANCE_PATHS"]


def leaf(text):
    data = text.encode()
    return {"type": "blob", "mode": "100644",
            "sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}


def snapshot(rows):
    tree = ns["tree_oid"](rows)
    return {"metadata": {"id": ns["REPOSITORY_ID"], "full_name": ns["REPOSITORY"],
                          "private": True, "default_branch": "main"},
            "ref": {"ref": "refs/heads/main", "object": {"sha": "1" * 40}},
            "commit": {"sha": "1" * 40, "tree": {"sha": tree}},
            "tree": {"sha": tree, "truncated": False,
                     "tree": [{"path": path, **entry} for path, entry in rows.items()]}}


current_row, = [row for row in delta["changes"] if row["path"] == "CURRENT_WORK.md"]
next_value, teammate = leaf("阶段末 CURRENT"), leaf("队友的新内容")
minimal = {**delta, "changes": [{**current_row, "after": next_value}]}
remote = {"CURRENT_WORK.md": accepted["paths"]["CURRENT_WORK.md"], "team/c500.md": teammate}
plan = ns["merge_plan"](minimal, snapshot(remote), "codex/stage")
assert plan["status"] == "ready" and plan["intermediate_accepted_paths"] == ["CURRENT_WORK.md"]
assert plan["edits"][0]["remote_before"] == accepted["paths"]["CURRENT_WORK.md"]
assert plan["expected_merged_tree"] == ns["tree_oid"]({**remote, "CURRENT_WORK.md": next_value})
assert ns["merge_plan"](minimal, snapshot({**remote, "CURRENT_WORK.md": next_value}), "codex/stage")["status"] == "no_changes"
assert ns["merge_plan"](minimal, snapshot({**remote, "CURRENT_WORK.md": teammate}), "codex/stage")["status"] == "conflicts_stop"
# 指明已接受维护后，这六路径不能退回接受任意旧基点/远端chmod。
assert ns["merge_plan"](minimal, snapshot({**remote, "CURRENT_WORK.md": current_row["before"]}), "codex/stage")["status"] == "conflicts_stop"
assert ns["merge_plan"](minimal, snapshot({**remote, "CURRENT_WORK.md": {**accepted["paths"]["CURRENT_WORK.md"], "mode": "100755"}}), "codex/stage")["status"] == "conflicts_stop"
unlisted = {**delta, "changes": [{"path": "other.md", "before": None, "after": next_value}]}
assert ns["merge_plan"](unlisted, snapshot({**remote, "other.md": teammate}), "codex/stage")["status"] == "conflicts_stop"
try:
    ns["local_delta"](ROOT, ROOT / "tmp/publish-team-rebuild-final-20261022.json", "8af67cc", "8af67cc", "ed86941")
except subprocess.CalledProcessError:
    pass
else:
    raise AssertionError("维护基点不在base→target区间也被接受")

result = {"status": "offline_accepted_maintenance_contract_passed_no_network",
          "script_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
          "check_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          "accepted_local": accepted["local_revision"], "accepted_paths": sorted(ns["MAINTENANCE_PATHS"]),
          "checks": ["actual_ancestor_range", "exact_six_path_blob_and_mode_only",
                     "accepted_CURRENT_to_new_target", "same_target_skipped", "teammate_changes_still_stop",
                     "old_base_and_chmod_not_accepted", "outside_whitelist_still_conflicts"],
          "limitations": ["No live main read, GitHub write or async upload test."]}
(HERE / "maintenance-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
