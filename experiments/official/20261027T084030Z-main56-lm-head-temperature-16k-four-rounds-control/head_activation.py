"""只读真实head首次kernel和原Sampler消费回执，缺覆盖与运行错误分别记录。"""
import ast
from pathlib import Path
import re

def capture(log_path):
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={name:[] for name in ('ready','selected','sampled','rejected','raw_fallback')};errors=[]
    markers={name:'BIV150_HEAD_TEMPERATURE_'+name.upper()+' ' for name in records}
    for number,line in enumerate(text.splitlines(),1):
        for name,marker in markers.items():
            if marker not in line:continue
            raw=line.split(marker,1)[1]
            item=dict(line=number,raw=raw)
            if name=='selected':
                try:
                    item['value']=ast.literal_eval(raw)
                    if not isinstance(item['value'],dict):raise ValueError('selected非dict')
                except (ValueError,SyntaxError) as error:errors.append(dict(line=number,error=repr(error)))
            records[name].append(item)
    selected=[]
    for item in records['selected']:
        value=item.get('value',{});digest=value.get('hash')
        selected.append(value.get('rows')==64 and value.get('grid')==[510,1]
            and isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) is not None)
    abnormal=bool(errors or records['rejected'] or records['raw_fallback'])
    covered=bool(records['ready'] and records['selected'] and records['sampled'] and all(selected))
    return dict(valid=bool(covered and not abnormal),covered=covered,abnormal=abnormal,
        status='abnormal' if abnormal else 'selected_and_sampled' if covered else 'coverage_missing',
        records=records,parse_errors=errors,
        limitation='首次实际kernel选择及原Sampler消费，非逐步计数或真实选中占比；缺覆盖不等于官方请求/数学失败。精确源码由独立809文件身份门核对。')

def kv_tokens(log_path):
    text=Path(log_path).read_text(errors='replace')
    values=[int(v.replace(',','')) for v in re.findall(r'GPU KV cache size:\s*([\d,]+)\s*tokens',text)]
    if not values or len(set(values))!=1:raise ValueError('实际KV容量缺失或不唯一')
    return values[0]


def optional_scope_valid(evidence):
    """16K可合法未命中R64；出现selection/sample则仍须原完整闭合。"""
    observed = bool(evidence['records']['selected'] or evidence['records']['sampled'])
    return bool(not evidence['abnormal'] and (not observed or evidence['valid']))
