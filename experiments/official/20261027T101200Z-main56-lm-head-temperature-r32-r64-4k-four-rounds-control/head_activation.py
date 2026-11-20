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
            if name in ('selected','sampled'):
                try:
                    item['value']=ast.literal_eval(raw)
                    if not isinstance(item['value'],dict):raise ValueError('head回执非dict')
                except (ValueError,SyntaxError) as error:errors.append(dict(line=number,error=repr(error)))
            records[name].append(item)
    grids={32:[2040,1],64:[510,1]};selected=[];selected_rows=set();sampled_rows=set()
    for item in records['selected']:
        value=item.get('value',{});digest=value.get('hash');row=value.get('rows')
        good=(type(row) is int and row in grids and value.get('grid')==grids[row]
            and isinstance(digest,str) and re.fullmatch('[0-9a-f]{64}',digest) is not None)
        selected.append(good)
        if good:selected_rows.add(row)
    sampled=[]
    for item in records['sampled']:
        value=item.get('value',{});row=value.get('rows')
        good=(type(row) is int and row in grids and value.get('chain')=='original stats/top-p/softmax/noise; temperature consumed once')
        sampled.append(good)
        if good:sampled_rows.add(row)
    abnormal=bool(errors or records['rejected'] or records['raw_fallback'])
    covered=bool(records['ready'] and records['selected'] and records['sampled'] and all(selected)
        and all(sampled) and selected_rows==sampled_rows)
    return dict(valid=bool(covered and not abnormal),covered=covered,abnormal=abnormal,
        status='abnormal' if abnormal else 'selected_and_sampled' if covered else 'coverage_missing',
        records=records,parse_errors=errors,selected_rows=sorted(selected_rows),sampled_rows=sorted(sampled_rows),
        limitation='首次实际kernel选择及原Sampler消费，非逐步计数或真实选中占比；缺覆盖不等于官方请求/数学失败。精确源码由独立809文件身份门核对。')

def kv_tokens(log_path):
    text=Path(log_path).read_text(errors='replace')
    values=[int(v.replace(',','')) for v in re.findall(r'GPU KV cache size:\s*([\d,]+)\s*tokens',text)]
    if not values or len(set(values))!=1:raise ValueError('实际KV容量缺失或不唯一')
    return values[0]


def optional_scope_valid(evidence):
    """16K可合法未命中R32/R64；出现selection/sample则仍须原完整闭合。"""
    observed = bool(evidence['records']['selected'] or evidence['records']['sampled'])
    return bool(not evidence['abnormal'] and (not observed or evidence['valid']))


def compare_kv(log_path,baseline_tokens):
    """容量解析仍严格；匹配与否独立记录，绝不伪称严格因果收益。"""
    actual=kv_tokens(log_path)
    if actual<=0:raise ValueError('实际KV容量须为正数')
    return dict(valid=True,compare_kv_match=actual==baseline_tokens,baseline=baseline_tokens,candidate=actual,
        limitation='KV容量不一致时仍记录官方观测和首暖筛选，但不能声称相同显存条件下的严格因果收益。')
