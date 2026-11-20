"""只读Q32真实返回后的selected与同hash编译机制/资源，不发模型调用。"""
import ast,json,re
from pathlib import Path

def capture(log_path):
    text=re.sub(r'\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={k:[] for k in ('installed','selected','q_fragment')};errors=[];fallback=[]
    markers=[('installed','BIV150_PREFILL_Q32_INSTALL ',ast.literal_eval),
             ('selected','BIV150_PREFILL_Q32_SELECTED ',ast.literal_eval),
             ('q_fragment','BIV150_Q_FRAGMENT_SELECTED ',json.loads)]
    for line_number,line in enumerate(text.splitlines(),1):
        if 'BIV150_PREFILL_Q32_FALLBACK ' in line:fallback.append(dict(line=line_number,raw=line))
        for kind,marker,parse in markers:
            if marker not in line:continue
            try:
                value=parse(line.split(marker,1)[1])
                if not isinstance(value,dict):raise ValueError('回执不是dict')
                records[kind].append(dict(line=line_number,value=value))
            except (ValueError,SyntaxError) as error:errors.append(dict(line=line_number,error=repr(error)))
    geometry=dict(block_m=256,block_q=32,num_warps=16,num_stages=1,tile_size=64)
    installed=bool(records['installed']) and all(x['value'].get('installed') is True for x in records['installed'])
    installed=bool(installed and any(all(x['value'].get(k)==v for k,v in geometry.items())
        and x['value'].get('minimum_query_rows')==1024 and x['value'].get('num_sequences')==1 for x in records['installed']))
    selected=[]
    for item in records['selected']:
        value=item['value'];digest=value.get('hash');linked=[]
        for proof in records['q_fragment']:
            p=proof['value'];resource=p.get('candidate_resources',{});meta=resource.get('metadata',{})
            if (p.get('mode')=='selected' and p.get('candidate_hash')==digest==resource.get('hash')
                and p.get('mechanism',{}).get('mechanism_pass') is True
                and meta.get('num_warps')==16 and meta.get('num_stages')==1 and resource.get('asm_sha256')):
                linked.append(proof['line'])
        valid=(isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) is not None
            and type(value.get('rows')) is int and value['rows']>=1024 and value.get('num_sequences')==1
            and all(value.get(k)==v for k,v in geometry.items()) and bool(linked))
        selected.append(dict(line=item['line'],value=value,valid=valid,linked_Q_fragment_lines=linked))
    valid=bool(installed and selected and all(x['valid'] for x in selected) and not errors)
    return dict(valid=valid,installed_valid=installed,selected=selected,records=records,parse_errors=errors,fallback_records=fallback,
        limitation='Q32/w16的首次真实wrapper返回回执＋同hash Q-hoist机制/机器码哈希与编译资源；仅install不合格，不证明逐请求覆盖率。fallback单独保留，不伪装整轮全覆盖。')
