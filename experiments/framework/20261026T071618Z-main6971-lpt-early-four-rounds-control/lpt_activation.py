"""读取新私有LPT Q-hoist实际编译/启用证明；不发合成请求。"""
import ast,json,re
from pathlib import Path
def capture(log_path,require_selected=True):
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={'installed':[],'geometry':[],'selected':[]};errors=[]
    for number,line in enumerate(text.splitlines(),1):
        for kind,marker in [('installed','BIV150_Q_FRAGMENT_INSTALL'),('geometry','BIV150_LPT_PREFILL_SELECTED'),('selected','BIV150_LPT_Q_FRAGMENT_SELECTED')]:
            if marker+' ' not in line:continue
            raw=line.split(marker+' ',1)[1]
            try:
                value=json.loads(raw) if kind=='selected' else ast.literal_eval(raw)
                records[kind].append({'line':number,'value':value})
            except (ValueError,SyntaxError) as e:errors.append({'line':number,'error':repr(e)})
    installed=bool(records['installed']) and all(v['value'].get('installed') is True and v['value'].get('lpt_private_manager') is True for v in records['installed'])
    selected=bool(records['selected']) and all(v['value'].get('mode')=='selected' and v['value'].get('mechanism',{}).get('mechanism_pass') is True and v['value'].get('candidate_hash') for v in records['selected'])
    valid=installed and not errors and 'BIV150_LPT_PREFILL_NOT_READY' not in text and ((selected and bool(records['geometry'])) or (not require_selected and not records['geometry']))
    return dict(valid=bool(valid),status='actual_private_q_hoist_selected' if selected else 'not_observed',records=records,parse_errors=errors,
        limitation='host选择与实际私有Q-hoist证明合取；不能把只安装或未命中几何当收益资格。')
