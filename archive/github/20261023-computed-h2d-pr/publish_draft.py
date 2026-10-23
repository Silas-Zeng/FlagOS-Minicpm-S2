"""只将冻结的一个文件发布为独立Draft；不更新main、不合并。"""
import base64, hashlib, importlib.util, json, re, subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REPO='Silas-Zeng/FlagOS-S2-vllm-plugin-FL'
BRANCH='codex/skip-computed-h2d'
GH='C:/Program Files/GitHub CLI/gh.exe'
STATE=HERE/'publication.json'
meta=json.loads((HERE/'manifest.json').read_text(encoding='utf-8'))
assert meta['repository']==REPO and meta['base_commit']=='9a43eb1e883a1ba986a4ae8052f1d00d8fd7aa5f'
assert len(meta['files'])==1
item=meta['files'][0]; data=(HERE/item['package_path']).read_bytes()
assert hashlib.sha256(data).hexdigest()==item['target_sha256']
assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==item['target_blob']
publisher=ROOT/'scripts/publish_experiment_pr.py'
assert hashlib.sha256(publisher.read_bytes()).hexdigest()=='f8e8819654ab87c7772d325304a95bb3a3c8cb918eba922f5e2954c66470ef08'
spec=importlib.util.spec_from_file_location('publisher',publisher); old=importlib.util.module_from_spec(spec); spec.loader.exec_module(old)
assert len(data)<99_000_000 and not any(re.search(p,data) for p in old.SECRET_PATTERNS)
state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'repository':REPO,'branch':BRANCH,'base_commit':meta['base_commit'],'target_blob':item['target_blob']}
assert all(state[k]==v for k,v in {'repository':REPO,'branch':BRANCH,'base_commit':meta['base_commit'],'target_blob':item['target_blob']}.items())
def save():
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def api(method,path='',body=None,missing=False):
    if method!='GET':
        assert method=='POST' and path in {'git/blobs','git/trees','git/commits','git/refs','pulls'}
        if path=='git/refs':assert body['ref']=='refs/heads/'+BRANCH
        if path=='pulls':assert body['head']==BRANCH and body['base']=='main' and body['draft'] is True
    args=[GH,'api','-X',method,'repos/'+REPO+('/'+path if path else '')]
    if body is not None:
        request=HERE/'request.json';request.write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8');args+=['--input',str(request)]
    r=subprocess.run(args,capture_output=True,timeout=120)
    if r.returncode:
        if missing and b'HTTP 404' in r.stderr:return None
        raise RuntimeError(f'GitHub {method} {path} failed, exit={r.returncode}')
    return json.loads(r.stdout)
def guard():
    repo=api('GET');assert repo['id']==1428598271 and repo['full_name']==REPO and repo['private'] and repo['default_branch']=='main'
    assert api('GET','git/ref/heads/main')['object']['sha']==meta['base_commit']
guard()
tree=json.loads((HERE/'main-tree.json').read_text(encoding='utf-8'))
assert tree['sha']==meta['base_tree'] and tree['truncated'] is False
entries={x['path']:{k:x[k] for k in ('mode','type','sha')} for x in tree['tree'] if x['type']!='tree'}
assert old.tree_oid(entries)==meta['base_tree']
assert entries[item['path']]['sha']==item['base_blob']
entries[item['path']]={'mode':'100644','type':'blob','sha':item['target_blob']}
target_tree=old.tree_oid(entries)
branch=api('GET','git/ref/heads/'+BRANCH,missing=True)
if branch is not None:assert state.get('commit')==branch['object']['sha']
if not state.get('blob_created'):
    assert api('POST','git/blobs',{'encoding':'base64','content':base64.b64encode(data).decode()})['sha']==item['target_blob']
    state['blob_created']=True;save()
if not state.get('tree'):
    reply=api('POST','git/trees',{'base_tree':meta['base_tree'],'tree':[{'path':item['path'],**entries[item['path']]}]})
    assert reply['sha']==target_tree;state['tree']=reply['sha'];save()
assert state['tree']==target_tree
guard()
if not state.get('commit'):
    reply=api('POST','git/commits',{'message':'省去CPU metadata成功分支的冗余computed H2D','tree':target_tree,'parents':[meta['base_commit']]})
    state['commit']=reply['sha'];save()
commit=api('GET','git/commits/'+state['commit'])
assert commit['tree']['sha']==target_tree and [x['sha'] for x in commit['parents']]==[meta['base_commit']]
if branch is None:
    guard();api('POST','git/refs',{'ref':'refs/heads/'+BRANCH,'sha':state['commit']})
assert api('GET','git/ref/heads/'+BRANCH)['object']['sha']==state['commit']
prs=api('GET','pulls?state=all&head=Silas-Zeng:'+BRANCH)
assert len(prs)<=1
body=(HERE/'PR.md').read_text(encoding='utf-8')
pr=prs[0] if prs else api('POST','pulls',{'title':'省去 CPU metadata 成功分支的冗余 computed H2D','body':body,'head':BRANCH,'base':'main','draft':True})
assert pr['state']=='open' and pr['head']['sha']==state['commit'] and pr['base']['ref']=='main' and pr['draft']
guard()
state.update(status='draft_PR_created_main_unchanged',pr_number=pr['number'],pr_url=pr['html_url'],tree=target_tree,body_sha256=hashlib.sha256(body.encode()).hexdigest(),files_changed=1)
save();print(json.dumps(state,ensure_ascii=False))
