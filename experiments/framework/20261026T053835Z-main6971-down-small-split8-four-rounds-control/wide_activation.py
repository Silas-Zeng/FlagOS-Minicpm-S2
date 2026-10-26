"""只读取实际调用后的回执；不修改模型、不发合成请求。"""
import ast
from pathlib import Path
import re

def capture(log_path):
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={'installed':[],'selected':[]};errors=[]
    for number,line in enumerate(text.splitlines(),1):
        for kind,marker in (('installed','BIV150_DOWN_SPLIT8_INSTALL'),('selected','BIV150_DOWN_SPLIT8_SELECTED')):
            if marker+' ' not in line:continue
            try:
                v=ast.literal_eval(line.split(marker+' ',1)[1])
                if not isinstance(v,dict):raise ValueError('回执不是dict')
                records[kind].append(dict(line=number,value=v))
            except (ValueError,SyntaxError) as e:errors.append(dict(line=number,error=repr(e)))
    installed=bool(records['installed']) and all(x['value'].get('installed') is True for x in records['installed'])
    selected=bool(records['selected']) and all(x['value'].get('rows') in range(1,9)
        and x['value'].get('N')==2048 and x['value'].get('K')==6144
        and x['value'].get('BM')==16 and x['value'].get('BN')==64
        and x['value'].get('BK')==128 and x['value'].get('S')==8 and x['value'].get('warps')==4 and x['value'].get('stages')==1
        and tuple(x['value'].get('input_stride',()))==(6144,1)
        and tuple(x['value'].get('weight_stride',()))==(6144,1) for x in records['selected'])
    return dict(valid=bool(installed and selected and not errors),records=records,parse_errors=errors,
        limitation='自然模型调用后首次日志证明路由实际执行，不代表逐kernel覆盖；同源官方承担实际选中，105单独判准确率。')
