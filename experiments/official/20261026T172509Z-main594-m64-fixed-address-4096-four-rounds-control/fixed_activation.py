"""只读实际M64固定地址的首次编译选中回执，不增加模型调用。"""
import ast
from pathlib import Path
import re

def capture(log_path):
    records={'installed':[],'selected':[]};errors=[]
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    for number,line in enumerate(text.splitlines(),1):
        for kind,marker in [('installed','BIV150_SMALL_OUT_LOWERING_INSTALL '),('selected','BIV150_M64_FIXED_ADDRESS_SELECTED ')]:
            if marker not in line:continue
            try:
                value=ast.literal_eval(line.split(marker,1)[1])
                if not isinstance(value,dict):raise ValueError('回执不是dict')
                records[kind].append(dict(line=number,value=value))
            except (ValueError,SyntaxError) as error:errors.append(dict(line=number,error=repr(error)))
    installed=bool(records['installed']) and all(x['value'].get('installed') is True and x['value'].get('m64_fixed_address') is True for x in records['installed'])
    def valid_selected(x):
        v=x['value']
        return (v.get('rows')==64 and v.get('N')==2048 and v.get('K')==6144
            and v.get('allocation')=='original caller-owned out' and v.get('extra_weight_bytes')==0
            and v.get('runtime_K') is True and isinstance(v.get('kernel_hash'),str)
            and re.fullmatch('[0-9a-f]{64}',v['kernel_hash']) is not None)
    valid=bool(installed and records['selected'] and all(valid_selected(x) for x in records['selected']) and not errors)
    return dict(valid=valid,records=records,parse_errors=errors,
        limitation='首次非capture调用的实际compiled hash与固定M64范围；不声称逐请求覆盖率。源码身份另由691/3差分门绑定，不强认组件路径相关hash。')
