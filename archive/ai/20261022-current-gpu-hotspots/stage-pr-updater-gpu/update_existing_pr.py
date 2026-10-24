#!/usr/bin/env python3
"""仅向现有实验 PR #2 分支追加一个普通提交；默认只生成计划。"""
from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
PUBLISHER = ROOT / "scripts/publish_experiment_pr.py"
PUBLISHER_SHA256 = "f8e8819654ab87c7772d325304a95bb3a3c8cb918eba922f5e2954c66470ef08"
if hashlib.sha256(PUBLISHER.read_bytes()).hexdigest() != PUBLISHER_SHA256:
    raise ValueError("已审发布器身份变化，先审核后更新 pin")
spec = importlib.util.spec_from_file_location("reviewed_experiment_publisher", PUBLISHER)
old = importlib.util.module_from_spec(spec)
spec.loader.exec_module(old)

REPO, REPO_ID = old.REPOSITORY, old.REPOSITORY_ID
BRANCH = "codex/framework-experiments-20261022"
PR = 2
ORIGINAL_HEAD = "6028156d916970d1c7a1ab000038beccaa0e0a48"
ORIGINAL_TREE = "0f998af29fd09f2f52348a9035228b5c7d218de6"
LOCAL_BASE = "4760863e954778469433dc732327f69ae1699615"
PREVIOUS_STATE = ROOT / "tmp/stage-pr-updater/update-state.json"
PREVIOUS_STATE_SHA256 = "3044f1036a7d52203143ba46d47ba49e0e7b9b6befea56ea14f2ddf8728c49ed"
REF_GET = "git/ref/heads/" + quote(BRANCH, safe="/")
REF_PATCH = "git/refs/heads/" + quote(BRANCH, safe="/")


def identity(metadata, pr):
    if (metadata.get("id") != REPO_ID or metadata.get("full_name") != REPO
            or metadata.get("private") is not True or metadata.get("default_branch") != "main"
            or pr.get("number") != PR or pr.get("state") != "open" or pr.get("merged_at") is not None
            or pr["head"]["ref"] != BRANCH or pr["base"]["ref"] != "main"
            or any(pr[side]["repo"].get("id") != REPO_ID
                   or pr[side]["repo"].get("full_name") != REPO for side in ("head", "base"))):
        raise ValueError("必须是固定私有实验库中的现有开放 PR #2")


def tree_map(tree):
    if tree.get("truncated") is not False:
        raise ValueError("远端 tree 被截断")
    result = {}
    for row in tree["tree"]:
        if row["type"] == "tree":
            continue
        old.valid_path(row["path"])
        if row["path"] in result:
            raise ValueError("远端重复路径")
        result[row["path"]] = {k: row[k] for k in ("mode", "type", "sha")}
    if old.tree_oid(result) != tree["sha"]:
        raise ValueError("远端 tree 不能由完整叶子重建")
    return result


def delta(local, target):
    raw_state = PREVIOUS_STATE.read_bytes()
    if hashlib.sha256(raw_state).hexdigest() != PREVIOUS_STATE_SHA256:
        raise ValueError("上一阶段已验发布回执变化，先核身份")
    initial = json.loads(raw_state)
    if any(initial.get(k) != v for k, v in {
            "repository": REPO, "branch": BRANCH, "commit": ORIGINAL_HEAD,
            "tree": ORIGINAL_TREE, "verified_tree": ORIGINAL_TREE, "pr_number": PR,
            "local_target": LOCAL_BASE, "status": "existing_PR_updated_main_not_written"}.items()):
        raise ValueError("旧 PR 已验状态身份变化")
    target = old.git(local, "rev-parse", target + "^{commit}").decode().strip()
    old.git(local, "merge-base", "--is-ancestor", LOCAL_BASE, target)
    before, after = old.git_map(local, LOCAL_BASE), old.git_map(local, target)
    if old.tree_oid(before) != ORIGINAL_TREE:
        raise ValueError("旧 PR 本地来源不等于已发布 tree")
    changes = [{"path": p, "before": before.get(p), "after": after.get(p)}
               for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]
    if any(e and e["type"] != "blob" for row in changes for e in (row["before"], row["after"])):
        raise ValueError("本轮不新增或改变 gitlink")
    return {"local_base": LOCAL_BASE, "local_target": target, "local_target_tree": old.tree_oid(after),
            "changes": changes}


def make_plan(change, snapshot):
    identity(snapshot["metadata"], snapshot["pr"])
    head = snapshot["ref"]["object"]["sha"]
    if (snapshot["ref"]["ref"] != "refs/heads/" + BRANCH
            or snapshot["pr"]["head"]["sha"] != head or snapshot["commit"]["sha"] != head
            or snapshot["commit"]["tree"]["sha"] != snapshot["tree"]["sha"]
            or snapshot["ancestry"] not in ("ahead", "identical")):
        raise ValueError("远端 PR 分支身份/原提交祖先关系不符")
    remote = tree_map(snapshot["tree"])
    merged, edits, conflicts, already = dict(remote), [], [], []
    for row in change["changes"]:
        path, before, after = row["path"], row["before"], row["after"]
        actual = remote.get(path)
        if actual == after:
            already.append(path)
        elif actual != before:
            conflicts.append({"path": path, "previous_PR": before, "current_branch": actual, "local_target": after})
        else:
            edits.append({**row, "remote_before": actual})
            if after is None:
                merged.pop(path, None)
            else:
                merged[path] = after
    expected = None
    if not conflicts:
        try:
            expected = old.tree_oid(merged)
        except ValueError as exc:
            conflicts.append({"kind": "file_directory_or_mode_conflict", "reason": str(exc)})
    plan = {**change, "repository": REPO, "branch": BRANCH, "pr_number": PR,
            "kind": "append_commit_to_existing_experiment_PR_only", "original_head": ORIGINAL_HEAD,
            "remote_head": head, "remote_tree": snapshot["tree"]["sha"],
            "observed_main": snapshot["main_head"], "expected_tree": expected,
            "expected_entries": len(merged), "edits": edits, "already_applied": already,
            "conflicts": conflicts, "updates_main": False, "creates_PR": False, "force": False,
            "reuse_remote_blobs": sorted({row["after"]["sha"] for row in edits if row["after"]}
                                         & {x["sha"] for x in remote.values() if x["type"] == "blob"}),
            "status": "conflicts_stop" if conflicts else ("ready" if edits else "no_changes")}
    plan["fingerprint"] = hashlib.sha256(old.canonical(plan)).hexdigest()
    return plan


class API:
    def __init__(self, gh, state_path, writes=False):
        self.gh, self.state_path, self.writes = gh, state_path, writes

    def guard(self, method, path, body):
        if method == "GET":
            return
        allowed = ((method == "POST" and path in {"git/blobs", "git/trees", "git/commits"})
                   or (method == "PATCH" and path == REF_PATCH and body.get("force") is False
                       and set(body) == {"sha", "force"} and old.SHA.fullmatch(body["sha"])))
        if not self.writes or not allowed:
            raise ValueError("禁止此写入口；只能追加普通对象并非强制更新固定 PR 分支")

    def call(self, method, path="", body=None):
        self.guard(method, path, body)
        cmd = [self.gh, "api", "-X", method, "repos/" + REPO + ("/" + path if path else "")]
        if body is not None:
            request = self.state_path.with_name(self.state_path.name + ".request.json")
            old.save(request, body)
            cmd += ["--input", str(request)]
        result = subprocess.run(cmd, capture_output=True, timeout=180)
        if result.returncode:
            # 不打印 gh 的原始 stderr/凭据，也不调用 auth token 等命令。
            code = re.search(rb"HTTP (\d{3})", result.stderr)
            raise RuntimeError("GitHub API 未成功: " + method + " " + path
                               + (" HTTP " + code[1].decode() if code else "；查看受控日志"))
        return json.loads(result.stdout)

    def snapshot(self):
        metadata, pr = self.call("GET"), self.call("GET", "pulls/2")
        identity(metadata, pr)
        ref = self.call("GET", REF_GET)
        head = ref["object"]["sha"]
        main_head = self.call("GET", "git/ref/heads/main")["object"]["sha"]
        commit = self.call("GET", "git/commits/" + head)
        tree = self.call("GET", "git/trees/" + commit["tree"]["sha"] + "?recursive=1")
        ancestry = "identical" if head == ORIGINAL_HEAD else self.call(
            "GET", "compare/" + ORIGINAL_HEAD + "..." + head)["status"]
        if (self.call("GET", REF_GET)["object"]["sha"] != head
                or self.call("GET", "git/ref/heads/main")["object"]["sha"] != main_head):
            raise RuntimeError("读取期间分支/main 变化，重新计划")
        return dict(metadata=metadata, pr=pr, ref=ref, main_head=main_head,
                    commit=commit, tree=tree, ancestry=ancestry)


def live_guard(api, plan, allowed_head):
    identity(api.call("GET"), api.call("GET", "pulls/2"))
    if (api.call("GET", REF_GET)["object"]["sha"] != allowed_head
            or api.call("GET", "pulls/2")["head"]["sha"] != allowed_head
            or api.call("GET", "git/ref/heads/main")["object"]["sha"] != plan["observed_main"]):
        raise RuntimeError("PR 分支或 main 已变化；停止，不覆盖，重新计划")


def verify_commit(api, commit, plan):
    record = api.call("GET", "git/commits/" + commit)
    if (record["sha"] != commit or record["tree"]["sha"] != plan["expected_tree"]
            or [x["sha"] for x in record["parents"]] != [plan["remote_head"]]):
        raise ValueError("提交不是以原远端 head 为唯一父的预期 tree")
    tree = api.call("GET", "git/trees/" + plan["expected_tree"] + "?recursive=1")
    if len(tree_map(tree)) != plan["expected_entries"] or tree["sha"] != plan["expected_tree"]:
        raise ValueError("提交的完整 tree 后验失败")


def publish(local, plan, api, state_path):
    if plan["status"] != "ready":
        raise ValueError("无增量或有冲突，不更新分支")
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {
        "repository": REPO, "branch": BRANCH, "pr_number": PR, "fingerprint": plan["fingerprint"],
        "started_utc": old.utc(), "uploaded_blobs": [], "next_edit": 0, "tree": plan["remote_tree"]}
    if any(state.get(k) != plan[k] for k in ("repository", "branch", "pr_number", "fingerprint")):
        raise ValueError("断点状态与计划不一致")
    current = api.call("GET", REF_GET)["object"]["sha"]
    if state.get("commit") and current == state["commit"]:
        # PATCH 成功但客户端断线时，不再次更新 ref，直接验证既有提交。
        live_guard(api, plan, current)
        verify_commit(api, current, plan)
    else:
        live_guard(api, plan, plan["remote_head"])
        blobs = old.changed_blobs(local, plan)
        old.save(state_path, state)
        for oid, content in blobs.items():
            if oid in state["uploaded_blobs"] or oid in plan["reuse_remote_blobs"]:
                continue
            reply = api.call("POST", "git/blobs", {"encoding": "base64", "content": base64.b64encode(content).decode()})
            if reply["sha"] != oid:
                raise RuntimeError("远端 blob 字节身份不符")
            state["uploaded_blobs"].append(oid)
            old.save(state_path, state)
        edits = sorted(plan["edits"], key=lambda row: (row["after"] is not None, row["path"]))
        while state["next_edit"] < len(edits):
            batch = edits[state["next_edit"]:state["next_edit"] + 200]
            entries = [{"path": row["path"], **(row["after"] or row["remote_before"]),
                        "sha": row["after"]["sha"] if row["after"] else None} for row in batch]
            reply = api.call("POST", "git/trees", {"base_tree": state["tree"], "tree": entries})
            state.update(tree=reply["sha"], next_edit=state["next_edit"] + len(batch))
            old.save(state_path, state)
        if state["tree"] != plan["expected_tree"]:
            raise RuntimeError("增量 tree 不符，不创建提交/更新分支")
        full = api.call("GET", "git/trees/" + state["tree"] + "?recursive=1")
        if len(tree_map(full)) != plan["expected_entries"] or full["sha"] != plan["expected_tree"]:
            raise RuntimeError("完整 tree 后验失败")
        live_guard(api, plan, plan["remote_head"])
        if not state.get("commit"):
            reply = api.call("POST", "git/commits", {
                "message": "补充GPU热点实验、硬件属性与失败证据\n\n本地来源: "
                           + plan["local_base"] + " → " + plan["local_target"],
                "tree": plan["expected_tree"], "parents": [plan["remote_head"]]})
            state["commit"] = reply["sha"]
            old.save(state_path, state)
        verify_commit(api, state["commit"], plan)
        live_guard(api, plan, plan["remote_head"])
        api.call("PATCH", REF_PATCH, {"sha": state["commit"], "force": False})
        live_guard(api, plan, state["commit"])
        verify_commit(api, state["commit"], plan)
    state.update(status="existing_PR_updated_main_not_written", finished_utc=old.utc(),
                 verified_tree=plan["expected_tree"], local_target=plan["local_target"],
                 pr_url="https://github.com/" + REPO + "/pull/2")
    old.save(state_path, state)
    return state


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--local", type=Path, default=ROOT)
    p.add_argument("--target-local", required=True, help="根负责人冻结的本阶段完整40位提交，不接受HEAD/分支名")
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--snapshot", type=Path, help="离线只读计划，不能用于直接发布")
    p.add_argument("--apply-plan", type=Path)
    p.add_argument("--state", type=Path)
    p.add_argument("--publish", action="store_true")
    p.add_argument("--gh", default=shutil.which("gh") or "C:/Program Files/GitHub CLI/gh.exe")
    a = p.parse_args()
    if not old.SHA.fullmatch(a.target_local):
        p.error("本阶段必须显式给出冻结后的40位 --target-local")
    if a.publish and (not a.apply_plan or not a.state or a.snapshot):
        p.error("发布须指定现有 --apply-plan 和独立 --state，不能传 --snapshot")
    if a.apply_plan and not a.publish:
        p.error("--apply-plan 只供显式发布")
    protected = {(ROOT / "tmp/stage-pr-publisher/20261022-publish-state.json").resolve(), PUBLISHER.resolve(),
                 PREVIOUS_STATE.resolve(), (ROOT / "tmp/stage-pr-updater/update-result.json").resolve(),
                 (ROOT / "tmp/stage-pr-updater/update_existing_pr.py").resolve()}
    outputs = [a.output.resolve()] + ([a.state.resolve()] if a.state else [])
    if (len(set(outputs)) != len(outputs) or any(x in protected for x in outputs)
            or (a.apply_plan and a.apply_plan.resolve() in outputs)):
        raise ValueError("计划/状态/结果必须分开，不能覆盖原发布状态或代码")
    local = a.local.resolve()
    change = delta(local, a.target_local)
    api = API(a.gh, a.state or a.output, writes=a.publish)
    if a.publish:
        plan = json.loads(a.apply_plan.read_text(encoding="utf-8"))
        check = dict(plan)
        fingerprint = check.pop("fingerprint")
        if (hashlib.sha256(old.canonical(check)).hexdigest() != fingerprint
                or any(plan.get(k) != v for k, v in {"repository": REPO, "branch": BRANCH,
                        "pr_number": PR, "original_head": ORIGINAL_HEAD, "local_base": LOCAL_BASE,
                        "local_target": change["local_target"], "changes": change["changes"]}.items())):
            raise ValueError("计划内容或本地来源变化")
        state = json.loads(a.state.read_text(encoding="utf-8")) if a.state.exists() else {}
        if not state.get("commit") or api.call("GET", REF_GET)["object"]["sha"] != state["commit"]:
            if make_plan(change, api.snapshot())["fingerprint"] != fingerprint:
                raise ValueError("实时远端已不等于审核计划，重新生成计划")
        result = publish(local, plan, api, a.state)
        old.save(a.output, {k: result[k] for k in ("status", "commit", "verified_tree", "pr_url", "local_target")})
        print(json.dumps({"status": result["status"], "pr_url": result["pr_url"]}, ensure_ascii=False))
    else:
        snapshot = json.loads(a.snapshot.read_text(encoding="utf-8")) if a.snapshot else api.snapshot()
        plan = make_plan(change, snapshot)
        old.changed_blobs(local, plan)  # 复用已审身份/大小/凭据扫描，不输出内容。
        old.save(a.output, plan)
        print(json.dumps({"status": plan["status"], "edits": len(plan["edits"]),
                          "conflicts": len(plan["conflicts"]), "reuse_blobs": len(plan["reuse_remote_blobs"]),
                          "remote_head": plan["remote_head"], "expected_tree": plan["expected_tree"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
