#!/usr/bin/env python3
"""实验记录增量 PR 发布器：默认仅计划，显式 --publish-pr 才建新分支/PR。

只处理指定私有实验库；不更新 main、不强制更新 ref、不自动合并。
以最近一次发布的本地 commit 计算增量，再叠在远端最新 main。
同路径两边不同改动或文件/目录冲突即停止，不自动选择本地覆盖。
"""
from __future__ import annotations

import argparse
import base64
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from urllib.parse import quote

REPOSITORY = "Silas-Zeng/FlagOS-Minicpm-S2"
REPOSITORY_ID = 1427279927
MAINTENANCE_PATHS = frozenset({"AGENTS.md", "README.md", "CURRENT_WORK.md",
                              "docs/pr-collaboration-plan.md", "docs/current-version-composition.md",
                              "archive/github/20261022-framework-merge.json"})
SECRET_PATTERNS = [rb"-----BEGIN (?:OPENSSH |RSA |EC |DSA |ENCRYPTED )?PRIVATE KEY-----",
                   rb"\bgh[pousr]_[A-Za-z0-9]{30,}\b", rb"\bgithub_pat_[A-Za-z0-9_]{30,}\b",
                   rb"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{32,}\b"]
SHA = re.compile(r"[0-9a-f]{40}\Z")


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if path.is_symlink() or temporary.is_symlink():
        raise ValueError("拒绝状态文件链接")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def valid_path(path):
    if (not isinstance(path, str) or "\\" in path or "\0" in path
            or any(x in ("", ".", "..", ".git") for x in path.split("/"))):
        raise ValueError("不支持的 Git 路径")


def git(local, *args):
    return subprocess.check_output(["git", "-c", "safe.directory=" + local.as_posix(),
                                    "-C", str(local), *args])


def git_map(local, revision):
    result = {}
    for raw in git(local, "ls-tree", "-rz", revision).split(b"\0"):
        if not raw:
            continue
        header, path = raw.split(b"\t", 1)
        mode, kind, oid = header.decode().split()
        path = path.decode("utf-8")
        valid_path(path)
        if path in result or not SHA.fullmatch(oid):
            raise ValueError("重复路径或非 SHA1 Git 对象")
        result[path] = {"mode": mode, "type": kind, "sha": oid}
    return result


def tree_oid(entries):
    """从叶子路径精确计算 Git tree SHA；同时拒绝文件/目录碰撞。"""
    root = {}
    for path, entry in entries.items():
        valid_path(path)
        if ((entry["type"], entry["mode"]) not in (("blob", "100644"), ("blob", "100755"),
                                                   ("blob", "120000"), ("commit", "160000"))
                or not SHA.fullmatch(entry["sha"])):
            raise ValueError("不支持的 Git 叶子模式")
        node = root
        parts = path.split("/")
        for part in parts[:-1]:
            child = node.setdefault(part, {})
            if not isinstance(child, dict):
                raise ValueError("文件/目录冲突: " + path)
            node = child
        if parts[-1] in node:
            raise ValueError("文件/目录冲突: " + path)
        node[parts[-1]] = (entry["mode"], entry["type"], entry["sha"])

    def digest(node):
        rows = []
        for name, entry in node.items():
            directory = isinstance(entry, dict)
            mode, oid = ("40000", digest(entry)) if directory else (entry[0], entry[2])
            rows.append((name.encode("utf-8") + (b"/" if directory else b""),
                         mode.encode() + b" " + name.encode("utf-8") + b"\0" + bytes.fromhex(oid)))
        data = b"".join(row for _, row in sorted(rows))
        return hashlib.sha1(b"tree " + str(len(data)).encode() + b"\0" + data).hexdigest()
    return digest(root)


def local_delta(local, published_state, revision, base_local, accepted_maintenance_local=None):
    state = json.loads(Path(published_state).read_text(encoding="utf-8"))
    if state["repository"] != REPOSITORY or not state.get("published_commit"):
        raise ValueError("必须使用本实验库已完成发布的 state")
    base = state["local_revision"]
    explicit_base = git(local, "rev-parse", base_local + "^{commit}").decode().strip()
    if explicit_base != base:
        raise ValueError("--base-local 不等于上次已完成发布的本地来源")
    target = git(local, "rev-parse", revision + "^{commit}").decode().strip()
    subprocess.run(["git", "-c", "safe.directory=" + local.as_posix(), "-C", str(local),
                    "merge-base", "--is-ancestor", base, target], check=True, capture_output=True)
    before, after = git_map(local, base), git_map(local, target)
    if (tree_oid(before) != state["expected_tree"]
            or state.get("verified_tree") != state["expected_tree"]
            or tree_oid(after) != git(local, "rev-parse", target + "^{tree}").decode().strip()):
        raise ValueError("本地基点/目标 tree 身份不符")
    accepted = None
    if accepted_maintenance_local is not None:
        middle = git(local, "rev-parse", accepted_maintenance_local + "^{commit}").decode().strip()
        for older, newer in ((base, middle), (middle, target)):
            subprocess.run(["git", "-c", "safe.directory=" + local.as_posix(), "-C", str(local),
                            "merge-base", "--is-ancestor", older, newer], check=True, capture_output=True)
        if middle == base:
            raise ValueError("维护中间基点必须晚于原发布本地基点")
        middle_map = git_map(local, middle)
        if any(path not in middle_map or middle_map[path]["type"] != "blob" for path in MAINTENANCE_PATHS):
            raise ValueError("维护中间基点缺少固定六个文档 blob")
        accepted = {"local_revision": middle, "paths": {path: middle_map[path] for path in sorted(MAINTENANCE_PATHS)}}
    changed = [{"path": path, "before": before.get(path), "after": after.get(path)}
               for path in sorted(before.keys() | after.keys() | (MAINTENANCE_PATHS if accepted else set()))
               if (before.get(path) != after.get(path)
                   or (accepted and path in MAINTENANCE_PATHS and accepted["paths"][path] != after.get(path)))]
    if any(entry and entry["type"] != "blob" for row in changed for entry in (row["before"], row["after"])):
        raise ValueError("本轮不发布新增或变化的 gitlink")
    return {"repository": REPOSITORY, "local_base": base, "local_target": target,
            "last_published_remote_commit": state["published_commit"],
            "base_tree": state["expected_tree"], "target_tree": tree_oid(after), "changes": changed,
            "accepted_maintenance": accepted}


def merge_plan(delta, snapshot, branch):
    metadata = snapshot["metadata"]
    if (metadata["id"] != REPOSITORY_ID or metadata["full_name"] != REPOSITORY
            or metadata["private"] is not True or metadata["default_branch"] != "main"
            or snapshot["ref"]["ref"] != "refs/heads/main"):
        raise ValueError("远端仓库/默认分支身份不符")
    head = snapshot["ref"]["object"]["sha"]
    commit, tree = snapshot["commit"], snapshot["tree"]
    if (commit["sha"] != head or tree.get("truncated") is not False
            or commit["tree"]["sha"] != tree["sha"]):
        raise ValueError("远端完整 main tree 不符")
    remote = {}
    for row in tree["tree"]:
        if row["type"] == "tree":
            continue
        valid_path(row["path"])
        if row["path"] in remote:
            raise ValueError("远端重复路径")
        remote[row["path"]] = {k: row[k] for k in ("mode", "type", "sha")}
    if tree_oid(remote) != tree["sha"]:
        raise ValueError("远端叶子不能重建 tree（可能有空 tree 或未知模式）；不猜测处理")
    accepted = delta.get("accepted_maintenance")
    if accepted is not None and set(accepted["paths"]) != MAINTENANCE_PATHS:
        raise ValueError("维护中间基点只能包含固定六路径")
    merged, edits, conflicts, already, intermediate = dict(remote), [], [], [], []
    for row in delta["changes"]:
        path, before, after = row["path"], row["before"], row["after"]
        actual = remote.get(path)
        expected_before = accepted["paths"][path] if accepted and path in MAINTENANCE_PATHS else before
        if actual == after:
            already.append(path)
        elif actual != expected_before:
            conflicts.append({"path": path, "published_local_base": before,
                              "accepted_maintenance_before": expected_before if accepted and path in MAINTENANCE_PATHS else None,
                              "remote_main": actual, "local_target": after})
        else:
            edits.append({**row, "remote_before": actual})
            if actual != before:
                intermediate.append(path)
            if after is None:
                merged.pop(path, None)
            else:
                merged[path] = after
    # 同路径无冲突还不足以允许 a → a/b，必须同时核全远端文件/目录集合。
    merged_tree = None
    if not conflicts:
        try:
            merged_tree = tree_oid(merged)
        except ValueError as exc:
            conflicts.append({"kind": "file_directory_or_mode_conflict", "reason": str(exc)})
    plan = {**delta, "kind": "incremental_experiment_evidence_PR_only",
            "branch": branch, "remote_main": head, "remote_base_tree": tree["sha"],
            "expected_merged_tree": merged_tree, "remote_entries": len(remote),
            "expected_merged_entries": len(merged), "edits": edits,
            "already_applied": already, "conflicts": conflicts,
            "intermediate_accepted_paths": intermediate,
            "reuse_remote_blobs": sorted({row["after"]["sha"] for row in edits if row["after"] is not None}
                                         & {entry["sha"] for entry in remote.values() if entry["type"] == "blob"}),
            "status": "conflicts_stop" if conflicts else ("ready" if edits else "no_changes"),
            "preserves_untouched_remote_paths": True, "updates_main": False}
    plan["fingerprint"] = hashlib.sha256(canonical(plan)).hexdigest()
    return plan


class API:
    def __init__(self, gh, state_path, branch, writes=False):
        self.gh, self.state_path, self.branch, self.writes = gh, state_path, branch, writes

    def call(self, method, path="", body=None, missing=False):
        if method != "GET":
            if (not self.writes or method != "POST"
                    or path not in {"git/blobs", "git/trees", "git/commits", "git/refs", "pulls"}):
                raise ValueError("禁止的 GitHub 写入口；不允许更新 main/ref/自动合并")
            if path == "git/refs" and body.get("ref") != "refs/heads/" + self.branch:
                raise ValueError("只允许创建指定的新 codex 分支")
            if path == "pulls" and (body.get("base") != "main" or body.get("head") != self.branch):
                raise ValueError("PR base/head 不符")
        command = [self.gh, "api", "-X", method, "repos/" + REPOSITORY + ("/" + path if path else "")]
        if body is not None:
            request = self.state_path.with_name(self.state_path.name + ".request.json")
            save(request, body)
            command += ["--input", str(request)]
        result = subprocess.run(command, capture_output=True, timeout=180)
        if result.returncode:
            if missing and b"(HTTP 404)" in result.stderr:
                return None
            raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
        return json.loads(result.stdout)

    def snapshot(self):
        metadata = self.call("GET")
        ref = self.call("GET", "git/ref/heads/main")
        commit = self.call("GET", "git/commits/" + ref["object"]["sha"])
        tree = self.call("GET", "git/trees/" + commit["tree"]["sha"] + "?recursive=1")
        if self.call("GET", "git/ref/heads/main")["object"]["sha"] != ref["object"]["sha"]:
            raise RuntimeError("读取期间 main 前进，请重新生成计划")
        return {"metadata": metadata, "ref": ref, "commit": commit, "tree": tree}


def changed_blobs(local, plan):
    ids = sorted({row["after"]["sha"] for row in plan["edits"] if row["after"] is not None})
    packed = subprocess.run(["git", "-c", "safe.directory=" + local.as_posix(), "-C", str(local),
                             "cat-file", "--batch"], input=("\n".join(ids) + "\n").encode(),
                            capture_output=True, check=True).stdout if ids else b""
    result, offset = {}, 0
    for oid in ids:
        end = packed.index(b"\n", offset)
        header = packed[offset:end].decode().split()
        if header[:2] != [oid, "blob"]:
            raise ValueError("本地 blob 身份不符")
        size = int(header[2])
        content = packed[end + 1:end + 1 + size]
        if len(content) != size or packed[end + 1 + size:end + 2 + size] != b"\n":
            raise ValueError("本地 blob 读取截断")
        if hashlib.sha1(b"blob " + str(size).encode() + b"\0" + content).hexdigest() != oid:
            raise ValueError("本地 blob 字节 SHA 不符")
        if size > 99_000_000 or any(re.search(pattern, content) for pattern in SECRET_PATTERNS):
            raise ValueError("过大或疑似凭据 blob（不打印内容）: " + oid)
        result[oid] = content
        offset = end + 2 + size
    for row in plan["edits"]:
        if Path(row["path"]).name in {".env", "credentials", "id_rsa", "id_ed25519"}:
            raise ValueError("疑似凭据路径（不发布）")
    return result


def publish(local, plan, api, state_path, title, body):
    if plan["status"] != "ready":
        raise ValueError("计划没有可发布增量或存在冲突")
    if api.call("GET", "git/ref/heads/main")["object"]["sha"] != plan["remote_main"]:
        raise RuntimeError("main 已前进：重新计划，禁止以旧树发布")
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {
        "repository": REPOSITORY, "fingerprint": plan["fingerprint"], "branch": plan["branch"],
        "started_utc": utc(), "uploaded_blobs": [], "next_edit": 0, "tree": plan["remote_base_tree"]}
    if any(state[k] != plan[k] for k in ("repository", "fingerprint", "branch")):
        raise ValueError("state 来源已变化，另建分支/状态文件")
    branch_path = "git/ref/heads/" + quote(plan["branch"], safe="/")
    existing = api.call("GET", branch_path, missing=True)
    if existing is not None and (not state.get("commit") or existing["object"]["sha"] != state["commit"]):
        raise ValueError("codex 分支已存在且非本次已保存的 commit；不覆盖")
    blobs = changed_blobs(local, plan)
    save(state_path, state)
    if existing is None:
        for oid, content in blobs.items():
            if oid in state["uploaded_blobs"] or oid in plan["reuse_remote_blobs"]:
                continue
            response = api.call("POST", "git/blobs", {"encoding": "base64", "content": base64.b64encode(content).decode()})
            if response["sha"] != oid:
                raise RuntimeError("远端 blob SHA 不符")
            state["uploaded_blobs"].append(oid)
            save(state_path, state)
            print("已保存新增 blob " + str(len(state["uploaded_blobs"])), flush=True)
        # 先删除旧叶子再加新叶子，避免文件↔目录变换的顺序歧义。
        edits = sorted(plan["edits"], key=lambda row: (row["after"] is not None, row["path"]))
        while state["next_edit"] < len(edits):
            batch = edits[state["next_edit"]:state["next_edit"] + 200]
            entries = [{"path": row["path"], **(row["after"] or row["remote_before"]),
                        "sha": row["after"]["sha"] if row["after"] else None} for row in batch]
            response = api.call("POST", "git/trees", {"base_tree": state["tree"], "tree": entries})
            state["tree"] = response["sha"]
            state["next_edit"] += len(batch)
            save(state_path, state)
        if state["tree"] != plan["expected_merged_tree"]:
            raise RuntimeError("增量后的完整 tree 不符，不创建 commit/ref/PR")
        actual = api.call("GET", "git/trees/" + state["tree"] + "?recursive=1")
        rows = {row["path"]: {k: row[k] for k in ("mode", "type", "sha")}
                for row in actual["tree"] if row["type"] != "tree"}
        if actual.get("truncated") is not False or tree_oid(rows) != plan["expected_merged_tree"] or len(rows) != plan["expected_merged_entries"]:
            raise RuntimeError("远端完整增量 tree 后验失败")
        if api.call("GET", "git/ref/heads/main")["object"]["sha"] != plan["remote_main"]:
            raise RuntimeError("上传期间 main 前进：不创建分支，重新计划")
        if not state.get("commit"):
            commit = api.call("POST", "git/commits", {"message": title + "\n\n本地增量: " + plan["local_base"] + " → " + plan["local_target"],
                                                       "tree": state["tree"], "parents": [plan["remote_main"]]})
            state["commit"] = commit["sha"]
            save(state_path, state)
        api.call("POST", "git/refs", {"ref": "refs/heads/" + plan["branch"], "sha": state["commit"]})
        state["branch_created"] = True
        save(state_path, state)
    if api.call("GET", branch_path)["object"]["sha"] != state["commit"]:
        raise RuntimeError("新分支身份不符")
    if api.call("GET", "git/ref/heads/main")["object"]["sha"] != plan["remote_main"]:
        raise RuntimeError("main 在建分支后前进：保留未合分支，重新审阅/计划；不自动提PR")
    prs = api.call("GET", "pulls?state=open&base=main&head=" + quote(REPOSITORY.split("/")[0] + ":" + plan["branch"], safe=""))
    if len(prs) > 1:
        raise RuntimeError("同分支出现多个PR，停止")
    pr = prs[0] if prs else api.call("POST", "pulls", {"base": "main", "head": plan["branch"], "title": title,
        "body": body + "\n\n本次仅发布已保存证据；本地来源 `" + plan["local_base"] + "` → `" + plan["local_target"]
                + "`。以远端 `" + plan["remote_main"] + "` 为父，保留未触及的队友路径；不直接更新 main。"})
    if (pr["head"]["sha"] != state["commit"] or pr["head"]["ref"] != plan["branch"]
            or pr["head"]["repo"]["full_name"] != REPOSITORY
            or pr["base"]["ref"] != "main" or pr["base"]["repo"]["full_name"] != REPOSITORY):
        raise RuntimeError("PR身份不符")
    state.update(pr_url=pr["html_url"], pr_number=pr["number"], finished_utc=utc(),
                 verified_tree=state["tree"], status="PR_created_main_not_updated")
    save(state_path, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, required=True)
    parser.add_argument("--published-state", type=Path, required=True)
    parser.add_argument("--base-local", required=True)
    parser.add_argument("--target-local", "--revision", dest="revision", required=True)
    parser.add_argument("--accepted-maintenance-local")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--remote-snapshot", type=Path)
    parser.add_argument("--offline-delta", action="store_true")
    parser.add_argument("--publish-pr", action="store_true")
    parser.add_argument("--state", type=Path)
    parser.add_argument("--title", default="同步本阶段实验记录与原始证据")
    parser.add_argument("--body-file", type=Path)
    parser.add_argument("--gh", default=shutil.which("gh") or "C:/Program Files/GitHub CLI/gh.exe")
    args = parser.parse_args()
    if (not re.fullmatch(r"codex/[a-z0-9][a-z0-9/_-]{0,100}", args.branch)
            or "//" in args.branch or args.branch.endswith("/")):
        raise ValueError("必须使用新的 codex/ 分支名")
    if args.publish_pr and (args.offline_delta or args.remote_snapshot or args.state is None):
        raise ValueError("发布必须实时读取main并指定state，不能采用离线snapshot")
    files = [args.output.resolve(), args.published_state.resolve()]
    if args.state is not None:
        files.append(args.state.resolve())
    if len(set(files)) != len(files):
        raise ValueError("计划、旧发布水位和PR状态不能共用文件")
    local = args.local.resolve()
    delta = local_delta(local, args.published_state, args.revision, args.base_local,
                        args.accepted_maintenance_local)
    if args.offline_delta:
        blobs = changed_blobs(local, {"edits": delta["changes"]})
        known = {entry["sha"] for entry in git_map(local, delta["local_base"]).values() if entry["type"] == "blob"}
        new_ids = set(blobs) - known
        save(args.output, {**delta, "status": "local_delta_only_remote_not_observed",
                           "changed_blob_secret_scan_passed": True, "unique_changed_blobs": len(blobs),
                           "unique_changed_bytes": sum(map(len, blobs.values())),
                           "new_vs_last_published_tree_blobs": len(new_ids),
                           "new_vs_last_published_tree_bytes": sum(len(blobs[oid]) for oid in new_ids)})
        print(json.dumps({"status": "local_delta_only_remote_not_observed", "paths": len(delta["changes"])}))
        return
    api = API(args.gh, args.state or args.output, args.branch, writes=args.publish_pr)
    snapshot = json.loads(args.remote_snapshot.read_text(encoding="utf-8")) if args.remote_snapshot else api.snapshot()
    plan = merge_plan(delta, snapshot, args.branch)
    changed_blobs(local, plan)  # 默认计划也先拒绝新增凭据，不必等实际发布。
    save(args.output, plan)
    if args.publish_pr:
        body = args.body_file.read_text(encoding="utf-8") if args.body_file else "汇总本阶段方法、失败记录和来源，复用已完成的验证。\n\n本发布步骤不重新运行设备实验。"
        result = publish(local, plan, api, args.state, args.title, body)
        print(json.dumps({k: result[k] for k in ("status", "pr_url", "verified_tree")}, ensure_ascii=False))
    else:
        print(json.dumps({"status": plan["status"], "paths": len(plan["edits"]), "already_applied": len(plan["already_applied"]),
                          "conflicts": len(plan["conflicts"]), "remote_main": plan["remote_main"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
