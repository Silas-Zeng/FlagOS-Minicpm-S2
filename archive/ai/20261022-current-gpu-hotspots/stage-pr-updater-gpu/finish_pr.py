from pathlib import Path
import json,subprocess,hashlib
base=Path(__file__).parent
gh='C:/Program Files/GitHub CLI/gh.exe'
repo='Silas-Zeng/FlagOS-Minicpm-S2'
state=json.loads((base/'update-state.json').read_text())
assert state['status']=='existing_PR_updated_main_not_written'
def api(method,path,body=None):
    args=[gh,'api','-X',method,'repos/'+repo+'/'+path]
    if body is not None:
        request=base/'pr-update-request.json'
        request.write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8')
        args+=['--input',str(request)]
    r=subprocess.run(args,capture_output=True,timeout=35,check=True)
    return json.loads(r.stdout)
p=api('GET','pulls/2')
assert p['state']=='open' and p['head']['sha']==state['commit'] and p['head']['ref']==state['branch']
assert p['base']['ref']=='main' and p['head']['repo']['id']==1427279927 and p['head']['repo']['private'] is True
marker='<!-- gpu-hotspots-stage-9b451d8 -->'
append=(base/'pr-body-zh.md').read_text(encoding='utf-8')
append=append.replace('最终目标提交与新增记录数待本阶段冻结后补入。',
    '本阶段来源提交 `9b451d8ab3d590e0496b6abbdf806595a3c0510c`，新增8轮；总表144条登记、141个独立run。')
append+='\n\n125135长基线同样32成功/0失败，219.996秒、2532.119 tok/s，但KV521840/DB527表19702行；122216为KV521936/DB527表19608行。两轮不能配对算收益或自然波动。\n'
append+='\nK lookahead仅完成CPU草稿，收益复审后未上卡：不减少访存或计算，没有已证实的并行度提升，新增carry开销可能抵消预取。保留草稿和同SHA真实IR，未登记成已运行实验。\n'
title='补充框架实验、GPU热点与硬件分析证据'
body=p['body'] or ''
if marker not in body:
    body=body.rstrip()+'\n\n'+marker+'\n\n'+append.strip()+'\n'
    latest=api('GET','pulls/2')
    assert latest['head']['sha']==state['commit'] and latest['body']==p['body'], 'PR changed; preserve and stop'
    api('PATCH','pulls/2',{'title':title,'body':body})
verified=api('GET','pulls/2')
assert verified['head']['sha']==state['commit'] and verified['body']==body and verified['title']==title
receipt={k:state[k] for k in ('repository','branch','pr_number','status','commit','verified_tree','local_target','pr_url','finished_utc')}
receipt.update(title=title,body_sha256=hashlib.sha256(body.encode()).hexdigest(),
    raw_state_sha256=hashlib.sha256((base/'update-state.json').read_bytes()).hexdigest(),
    registry_records=144,unique_runs=141,new_runs=8,updates_main=False)
out=Path('archive/github/20261022-gpu-hotspots-pr2-update.json')
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(base/'pr-body-published-zh.md').write_text(body,encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
