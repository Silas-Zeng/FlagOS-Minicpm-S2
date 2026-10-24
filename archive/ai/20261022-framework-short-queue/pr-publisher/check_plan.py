"""唯一离线发布安全合同；不 import 模型、不调用网络、不修改 Git 对象。"""
from pathlib import Path
import hashlib
import json
import runpy
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
module = HERE / "publish_experiment_pr.py"
ns = runpy.run_path(str(module))


def leaf(text, mode="100644"):
    data = text.encode()
    return {"type": "blob", "mode": mode,
            "sha": hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()}


def snapshot(rows):
    tree = ns["tree_oid"](rows)
    return {"metadata": {"id": ns["REPOSITORY_ID"], "full_name": ns["REPOSITORY"],
                          "private": True, "default_branch": "main"},
            "ref": {"ref": "refs/heads/main", "object": {"sha": "1" * 40}},
            "commit": {"sha": "1" * 40, "tree": {"sha": tree}},
            "tree": {"sha": tree, "truncated": False,
                     "tree": [{"path": path, **entry} for path, entry in rows.items()]}}


old, new, other = leaf("旧本地"), leaf("本阶段"), leaf("队友改变")
remote = {"README.md": old, "teammate/c500.md": other, "scripts/run.sh": leaf("exec", "100755"),
          "config/link": leaf("../source.json", "120000"), "metadata/sha": leaf("合法文件名sha")}
delta = {"repository": ns["REPOSITORY"], "local_base": "2" * 40, "local_target": "3" * 40,
         "changes": [{"path": "README.md", "before": old, "after": new},
                     {"path": "experiments/new.json", "before": None, "after": new}]}
plan = ns["merge_plan"](delta, snapshot(remote), "codex/phase")
assert plan["status"] == "ready" and len(plan["edits"]) == 2
assert plan["expected_merged_tree"] == ns["tree_oid"]({**remote, "README.md": new, "experiments/new.json": new})
assert plan["expected_merged_entries"] == 6 and not plan["updates_main"]
already = ns["merge_plan"](delta, snapshot({**remote, "README.md": new}), "codex/phase")
assert already["already_applied"] == ["README.md"] and len(already["edits"]) == 1
conflict = ns["merge_plan"](delta, snapshot({**remote, "README.md": other}), "codex/phase")
assert conflict["status"] == "conflicts_stop" and conflict["expected_merged_tree"] is None
assert conflict["conflicts"][0]["remote_main"] == other
deletion = {**delta, "changes": [{"path": "README.md", "before": old, "after": None}]}
assert ns["merge_plan"](deletion, snapshot(remote), "codex/phase")["status"] == "ready"
assert ns["merge_plan"](deletion, snapshot({**remote, "README.md": other}), "codex/phase")["status"] == "conflicts_stop"
structural = {**delta, "changes": [{"path": "README.md/child", "before": None, "after": new}]}
assert ns["merge_plan"](structural, snapshot(remote), "codex/phase")["status"] == "conflicts_stop"
complete = ns["merge_plan"](delta, snapshot({**remote, "README.md": new, "experiments/new.json": new}), "codex/phase")
assert complete["status"] == "no_changes" and not complete["edits"]

# 写路径拒绝发生在 subprocess 之前；不使用 mock 远端或实际 API。
api = ns["API"]("does-not-exist", HERE / "unused-state", "codex/phase", writes=True)
for method, path, body in (("PATCH", "git/refs/heads/main", {}),
                           ("POST", "git/refs", {"ref": "refs/heads/main"}),
                           ("POST", "pulls", {"base": "main", "head": "other"}),
                           ("POST", "pulls/1/merge", {})):
    try:
        api.call(method, path, body)
    except ValueError:
        pass
    else:
        raise AssertionError("禁止写入口未拒绝")
assert not any(name in sys.modules for name in ("torch", "triton", "vllm"))
result = {"status": "offline_plan_contract_passed_no_network_or_GitHub_write",
          "script_sha256": hashlib.sha256(module.read_bytes()).hexdigest(),
          "check_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          "checks": ["untouched_teammate_paths_preserved", "already_applied_skipped", "same_path_conflict_stops",
                     "modified_delete_conflict_stops", "file_directory_collision_stops", "no_empty_PR",
                     "executable_symlink_modes_preserved", "main_update_force_and_merge_routes_forbidden"],
          "limitations": ["Offline planner/route guards only; live main identity, Git Data API writes/resume/PR creation not executed."]}
(HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
