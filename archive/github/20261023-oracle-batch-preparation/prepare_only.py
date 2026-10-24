"""仅准备本地增量与中文正文，不创建提交、不修改任何GitHub对象。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / 'archive/github/20261023-oracle-batch-preparation'
out.mkdir(exist_ok=True)
source = root / 'scripts/publish_experiment_pr.py'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'f8e8819654ab87c7772d325304a95bb3a3c8cb918eba922f5e2954c66470ef08'
spec = importlib.util.spec_from_file_location('reuse_publisher',source)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
base='88a10fab4097dd80fc6e2f2d10ac814eea02e2da'
target='82a6b44cabdce061cabc4b8dddc7d718342ca1ed'
parent='be606b1c61e6e1033c8f3bdfe6f2630d5c3982ab'
before, after = mod.git_map(root,base), mod.git_map(root,target)
assert mod.tree_oid(before) == 'd31971c239530214026cdb10d5e4dba700821c19'
edits = [dict(path=k,after=after.get(k)) for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)]
blobs = mod.changed_blobs(root,dict(edits=edits))
assert subprocess.check_output(['git','rev-parse',parent+'^{tree}'],cwd=root,text=True).strip()==mod.tree_oid(before)
record=dict(status='prepared_locally_no_GitHub_write',repository='Silas-Zeng/FlagOS-Minicpm-S2',pr_number=2,
    local_base=base,local_target=target,remote_parent=parent,remote_parent_tree=mod.tree_oid(before),
    target_tree=mod.tree_oid(after),registry_rows=195,unique_runs=192,
    changed_paths=len(edits),scanned_blobs=len(blobs),
    new_runs=['20261023T082246Z-compute-order-first-layer-context16k','20261023T085500Z-compute-order-oracle-context16k'],
    limits='现有仓库只读的最新用户AGENTS消息与既有维护指示冲突；本包没有远端写入。若授权继续用实验专用库，发布前再核head/main，普通追加，不force。')
(out/'plan.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
