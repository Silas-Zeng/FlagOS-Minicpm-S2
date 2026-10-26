"""只读新候选安装/加载/编译选中回执；不发请求、不改测量。"""
import ast,re
from pathlib import Path
CONFIG=dict(BLOCK_M=64,BLOCK_N=128,BLOCK_K=64,num_warps=8,num_stages=2,num_ctas=1,SPLIT_K=1)
def capture(log_path,require_selected=True):
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={k:[] for k in ('installed','weight','selected')};errors=[]
    markers={'installed':'BIV150_NONLY_DOWN_INSTALL','weight':'BIV150_NONLY_DOWN_WEIGHT','selected':'BIV150_NONLY_DOWN_SELECTED'}
    for number,line in enumerate(text.splitlines(),1):
        for kind,marker in markers.items():
            if marker+' ' not in line:continue
            try:
                v=ast.literal_eval(line.split(marker+' ',1)[1])
                if not isinstance(v,dict):raise ValueError('回执非dict')
                records[kind].append(dict(line=number,value=v))
            except (ValueError,SyntaxError) as e:errors.append(dict(line=number,error=repr(e)))
    installed=bool(records['installed']) and all(x['value'].get('installed') is True for x in records['installed'])
    complete_weights=[x for x in records['weight'] if x['value'].get('layers')==42
        and x['value'].get('packed_bytes')==1056964608 and x['value'].get('keeps_original_weight') is True
        and x['value'].get('allocation')=='process_weights_after_loading, before KV memory profiling']
    selected=bool(records['selected']) and all(x['value'].get('rows')==64
        and x['value'].get('input_columns')==6144 and x['value'].get('output_columns')==2048
        and tuple(x['value'].get('packed_shape',()))==(16,6144,128) and x['value'].get('config')==CONFIG
        and isinstance(x['value'].get('kernel_hash'),str) and len(x['value']['kernel_hash'])==64
        for x in records['selected'])
    kv=[int(x.replace(',','')) for x in re.findall(r'GPU KV cache size: ([0-9,]+) tokens',text)]
    return dict(valid=bool(installed and complete_weights and (selected or (not require_selected and not records['selected'])) and not errors),
        records=records,parse_errors=errors,packed_42_layers=bool(complete_weights),selected=selected,
        selected_scope='first noncapture call; can be warmup, not per-request coverage',kv_capacity_tokens=kv,
        baseline_KV_tokens=548336,expected_extra_weight_bytes=1056964608,
        limitation='42个新opaque另由本run真实FX证明；M64的完整官方负载与独立GPU接线门承担实际覆盖，不把安装/暖up次数称请求命中率。')
