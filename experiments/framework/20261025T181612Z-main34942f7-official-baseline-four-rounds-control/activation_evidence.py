"""只回收官方原启动/Graph日志和已有JIT产物，不挂钩/修改模型调用。"""
import ast
import hashlib
import json
from pathlib import Path
import re
import shutil


def stack_evidence(log_path):
    """仅解析原有回执；未经历真实负载时缺FIRST_SELECTED属于待确认。"""
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    markers={
        'q_fragment_install': ('BIV150_Q_FRAGMENT_INSTALL', ast.literal_eval),
        'q_fragment_selected': ('BIV150_Q_FRAGMENT_SELECTED', json.loads),
        'compute_order_selected': ('BIV150_COMPUTE_ORDER_FIRST_SELECTED', json.loads),
        'compute_order_rejected': ('BIV150_COMPUTE_ORDER_SCOPE_REJECTED', json.loads),
    }
    records={name:[] for name in markers}
    errors=[]
    for number,line in enumerate(text.splitlines(),1):
        for name,(marker,parse) in markers.items():
            if marker+' ' not in line: continue
            try:
                value=parse(line.split(marker+' ',1)[1])
                if not isinstance(value,dict): raise ValueError('回执不是dict')
                records[name].append(dict(line=number,value=value,raw=line))
            except (ValueError,SyntaxError) as error:
                errors.append(dict(line=number,marker=marker,error=repr(error),raw=line))
    installed=records['q_fragment_install']
    rejected=bool(errors or records['compute_order_rejected'] or
                  any(x['value'].get('installed') is not True for x in installed))
    q_selected=any(x['value'].get('mode')=='selected' and
                   x['value'].get('mechanism',{}).get('mechanism_pass') is True
                   for x in records['q_fragment_selected'])
    order_selected=any(x['value'].get('original_model_forward_returned') is True
                       for x in records['compute_order_selected'])
    valid=bool(installed and q_selected and order_selected and not rejected)
    return dict(valid=valid,status='selected' if valid else 'rejected' if rejected else 'pending_or_missing',
                server_log=str(log_path),records=records,parse_errors=errors,
                limitation='原服务安装及首次实际选中回执，不证明逐请求逐kernel；启动期缺首次回执仅待确认。')


ORIGINAL_NORMALIZED_KERNEL = '0295ceff7472b60fbab69dda6557725e3bcb7ccb48aa841b1c1a13d8ec9cbb5d'



def stable_small_o_evidence(log_path):
    """读取PR51原回执；不发新调用，未遇小行就明确未观察到选中。"""
    text=re.sub(r'\x1b\[[0-9;]*m','',Path(log_path).read_text(errors='replace'))
    records={'installed':[],'selected':[]};errors=[]
    for number,line in enumerate(text.splitlines(),1):
        for kind,marker in (('installed','BIV150_STABLE_SMALL_O_INSTALL'),
                            ('selected','BIV150_STABLE_SMALL_O_SELECTED')):
            if marker+' ' not in line:continue
            try:
                value=ast.literal_eval(line.split(marker+' ',1)[1])
                if not isinstance(value,dict):raise ValueError('回执不是dict')
                records[kind].append(dict(line=number,value=value,raw=line))
            except (ValueError,SyntaxError) as error:
                errors.append(dict(line=number,marker=marker,error=repr(error),raw=line))
    installed=bool(records['installed']) and all(x['value'].get('installed') is True for x in records['installed'])
    geometries={(2048,2048),(12288,2048),(2560,2048),(2048,6144)}
    selected_valid=all(type(x['value'].get('rows')) is int and 1<=x['value']['rows']<=8
        and (x['value'].get('output_columns'),x['value'].get('input_columns')) in geometries
        and x['value'].get('warps')==4 and x['value'].get('stages')==1 for x in records['selected'])
    valid=bool(installed and selected_valid and not errors)
    status=('selected' if records['selected'] else 'installed_no_small_rows_observed') if valid else 'pending_or_rejected'
    return dict(valid=valid,status=status,records=records,parse_errors=errors,
        limitation='PR51默认安装与自然小行首次选中日志；缺小行记录不证明执行过M1-8，实际Graph绑定另记。')


def capture(run,control,source,env):
    log=run/'server.log'
    text=re.sub(r'\x1b\[[0-9;]*m','',log.read_text(errors='replace'))
    stack=stack_evidence(log)
    stable=stable_small_o_evidence(log)
    installed=[];errors=[]
    for number,line in enumerate(text.splitlines(),1):
        marker='BIV150_PREFILL_NORMALIZATION_INSTALL '
        if marker not in line:continue
        try:
            value=ast.literal_eval(line.split(marker,1)[1])
            if not isinstance(value,dict):raise ValueError('回执不是dict')
            installed.append(dict(line=number,value=value,raw=line))
        except (ValueError,SyntaxError) as error:
            errors.append(dict(line=number,error=repr(error),raw=line))
    norm_ok=bool(installed) and all(x['value'].get('installed') is True
        and x['value'].get('kernel_sha256')==ORIGINAL_NORMALIZED_KERNEL for x in installed)
    first=[line for line in text.splitlines() if 'BIV150_GQA_DECODE_FIRST_WIDTH ' in line]
    graph=[line for line in text.splitlines() if 'Capturing CUDA graph' in line or 'Graph capturing finished' in line]
    result=dict(valid=bool(norm_ok and first and graph and stack['valid'] and stable['valid'] and not errors),
        stack=stack,stable_small_o=stable,normalization_install=installed,parse_errors=errors,
        first_width=first,graph_capture_log=graph,source=str(source),
        limitation='干净34942f7原优化栈/PR51的自然安装与首次选中；不继承旧0915或队友成绩。')
    (control/'main-activation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
