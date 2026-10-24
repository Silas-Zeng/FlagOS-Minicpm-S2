"""只构造本地计算序方法分支；隔离Git index，不改现有checkout或远端。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'experiments/registry.csv').is_file() and (p/'AGENTS.md').is_file())
REPO=ROOT/'collaboration/FlagOS-S2-vllm-plugin-FL'
PROFILE=ROOT/'archive/ai/20261022-framework-kv/compute-order-main-profile'
HERE=Path(__file__).resolve().parent
BASE='3283672b92fa30f93f652b242193999836a95f88'
TARGET='5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
BRANCH='refs/heads/codex/biv150-compute-order'
GIT=['git','-c','safe.directory='+REPO.as_posix(),'-C',str(REPO)]

def call(args,*,data=None,env=None):
    return subprocess.check_output(GIT+args,input=data,env=env).decode('utf-8').strip()

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None

def main():
    receipt=HERE/'branch-receipt.json'
    if receipt.exists():raise FileExistsError('本地分支已登记，不重复构造提交')
    manifest=json.loads((PROFILE/'candidate-manifest.json').read_text(encoding='utf-8'))
    assert manifest['base_commit']==BASE and manifest['target_tree']==TARGET
    head=call(['rev-parse','HEAD'])
    branch=call(['symbolic-ref','--short','HEAD'])
    status=call(['--no-optional-locks','status','--porcelain'])
    assert status=='','保留现有未提交改动，拒绝操作'
    gitdir=Path(call(['rev-parse','--absolute-git-dir']))
    index_hash=digest(gitdir/'index')
    probe=subprocess.run(GIT+['show-ref','--verify','--quiet',BRANCH])
    if probe.returncode==0:raise FileExistsError('同名本地方法分支已存在')
    if probe.returncode!=1:raise RuntimeError('分支只读检查失败')
    index=ROOT/'tmp/compute-order-pr-local.index'
    if index.exists():raise FileExistsError('保留旧隔离index，拒绝覆盖')
    env=os.environ.copy();env['GIT_INDEX_FILE']=str(index)
    call(['read-tree',BASE],env=env)
    for name,item in manifest['changed_paths'].items():
        data=(PROFILE/'files'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest()==item['sha256']
        blob=call(['hash-object','-w','--stdin'],data=data)
        assert blob==item['after']['sha']
        call(['update-index','--add','--cacheinfo',item['after']['mode']+','+blob+','+name],env=env)
    tree=call(['write-tree'],env=env)
    assert tree==TARGET,'本地候选tree与受测446源码不同'
    changed=call(['diff','--name-only',BASE,tree]).splitlines()
    assert changed==sorted(manifest['changed_paths'])
    message='BI-V150：分离混合批次计算顺序与请求采样顺序\n\n基于当前normalized main，仅改runner和compute helper；源码tree与141159短测及142019完整准确率相同。'
    commit=call(['commit-tree',tree,'-p',BASE],data=(message+'\n').encode('utf-8'))
    call(['update-ref',BRANCH,commit,'0'*40])
    assert call(['rev-parse','HEAD'])==head and call(['symbolic-ref','--short','HEAD'])==branch
    assert digest(gitdir/'index')==index_hash
    assert call(['--no-optional-locks','status','--porcelain'])==status
    assert call(['rev-parse',BRANCH+'^{tree}'])==TARGET
    result=dict(utc=datetime.now(timezone.utc).isoformat(),repository=str(REPO),branch=BRANCH.removeprefix('refs/heads/'),
        commit=commit,parent=BASE,tree=tree,changed_paths=changed,source_count=446,
        checkout_head_before_and_after=head,checkout_branch_before_and_after=branch,
        original_index_sha256=index_hash,original_index_unchanged=True,checkout_clean=True,
        remote_mutated=False,tests_rerun=False,
        evidence=['analysis/compute-order-current-main-pair.json','analysis/compute-order-current-main-accuracy.json'],
        limits=['本地方法分支已准备，尚未发布GitHub PR','完整105题103正确但P0覆盖；短pair因KV容量失配gain=null','官方144620仍在运行，最终成绩未产生'])
    with receipt.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':main()
