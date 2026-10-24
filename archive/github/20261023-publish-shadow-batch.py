"""将已保存的两轮诊断追加到现有实验 PR；普通 push，禁止覆盖远端推进。"""
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
REPO = 'Silas-Zeng/FlagOS-Minicpm-S2'
BRANCH = 'codex/framework-experiments-20261022'
PARENT = 'efdd6ca7a26e9057ba865a974b678268124c81f4'
MAIN = 'f75b549a44a0f3cf35da3923766a2cc6b69ae6ee'
BASE = '404718ab207fcd4106663a22b659c5abb4b4ed6e'
GH = 'C:/Program Files/GitHub CLI/gh.exe'
source = ROOT / 'scripts/publish_experiment_pr.py'
assert hashlib.sha256(source.read_bytes()).hexdigest() == 'f8e8819654ab87c7772d325304a95bb3a3c8cb918eba922f5e2954c66470ef08'
spec = importlib.util.spec_from_file_location('reuse_publisher', source)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
def git(*args, **kw):
    return subprocess.check_output(['git', '-c', 'core.longpaths=true', '-C', str(ROOT), *args], **kw)
def api(endpoint, *args):
    return json.loads(subprocess.check_output([GH, 'api', endpoint, *args]))
def current():
    repo = api('repos/' + REPO)
    assert repo['id'] == 1427279927 and repo['private'] and repo['full_name'] == REPO
    pr = api('repos/' + REPO + '/pulls/2')
    assert pr['state'] == 'open' and pr['head']['ref'] == BRANCH and pr['base']['ref'] == 'main'
    assert api('repos/' + REPO + '/git/ref/heads/main')['object']['sha'] == MAIN
    return pr

target = git('rev-parse', '88a10fa^{commit}').decode().strip()
before = mod.git_map(ROOT, BASE)
after = mod.git_map(ROOT, target)
assert mod.tree_oid(before) == '917ca7336c52305780444cee287d287ffb39ea5f'
edits = [dict(path=k, after=after.get(k)) for k in sorted(set(before) | set(after)) if before.get(k) != after.get(k)]
blobs = mod.changed_blobs(ROOT, dict(edits=edits))
tree = mod.tree_oid(after)
assert git('rev-parse', target + '^{tree}').decode().strip() == tree
assert current()['head']['sha'] == PARENT
assert api('repos/' + REPO + '/git/commits/' + PARENT)['tree']['sha'] == mod.tree_oid(before)
commit = git('commit-tree', tree, '-p', PARENT,
             input='补充辅助门失败与计算顺序数值诊断原件\n'.encode()).decode().strip()
record = dict(repository=REPO, pr_number=2, pr_url='https://github.com/'+REPO+'/pull/2',
    branch=BRANCH, local_base=BASE, local_target=target, parent=PARENT,
    published_commit=commit, verified_tree=tree, main_unchanged=MAIN, private=True,
    registry_rows=193, unique_runs=190, changed_paths=len(edits), scanned_blobs=len(blobs),
    status='prepared_no_remote_write')
(HERE / 'shadow-batch-plan.json').write_text(json.dumps(record, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
assert current()['head']['sha'] == PARENT
env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
subprocess.run(['git', '-c', 'core.longpaths=true', '-c', 'credential.helper=',
    '-c', 'credential.helper=!gh auth git-credential', '-c', 'http.version=HTTP/1.1',
    '-c', 'http.lowSpeedLimit=1000', '-c', 'http.lowSpeedTime=45',
    'push', '--quiet', 'https://github.com/'+REPO+'.git', commit+':refs/heads/'+BRANCH],
    cwd=ROOT, env=env, check=True)
assert current()['head']['sha'] == commit
remote = api('repos/' + REPO + '/git/commits/' + commit)
assert remote['tree']['sha'] == tree and [p['sha'] for p in remote['parents']] == [PARENT]
body = (HERE / 'body.md').read_text(encoding='utf-8')
body_path = HERE / 'shadow-batch-pr-body.json'
body_path.write_text(json.dumps(dict(body=body), ensure_ascii=False), encoding='utf-8')
updated = api('repos/'+REPO+'/pulls/2', '--method', 'PATCH', '--input', str(body_path))
assert updated['head']['sha'] == commit and updated['body'] == body
record.update(status='existing_PR_updated_main_not_written', transport='ordinary_nonforce_git_push',
    body_sha256=hashlib.sha256(body.encode()).hexdigest(), verified_utc=datetime.now(timezone.utc).isoformat())
receipt = ROOT / 'archive/github/20261023-compute-order-shadow-pr2-update.json'
with receipt.open('x', encoding='utf-8') as handle:
    json.dump(record, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps(record, ensure_ascii=False))
