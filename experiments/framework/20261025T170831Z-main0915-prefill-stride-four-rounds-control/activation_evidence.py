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


EXPECTED_KERNEL = 'fa6ddc420a95102d116714fcbea41bc81aa9c09379d68518af65755c015b8744'
STRIDES = ('block_table_stride','query_stride_0','query_stride_1','output_stride_0','output_stride_1',
           'stride_k_cache_0','stride_k_cache_1','stride_k_cache_2',
           'stride_v_cache_0','stride_v_cache_1','stride_v_cache_2')


def capture(run,control,source,env):
    log = run/'server.log'
    text = re.sub(r'\x1b\[[0-9;]*m','',log.read_text(errors='replace'))
    stack = stack_evidence(log)
    installed, errors = [], []
    for number,line in enumerate(text.splitlines(),1):
        marker = 'BIV150_PREFILL_NORMALIZATION_INSTALL '
        if marker not in line: continue
        try:
            value = ast.literal_eval(line.split(marker,1)[1])
            if not isinstance(value,dict): raise ValueError('回执不是dict')
            installed.append(dict(line=number,value=value,raw=line))
        except (ValueError,SyntaxError) as error:
            errors.append(dict(line=number,error=repr(error),raw=line))
    selected = []
    for record in stack['records']['q_fragment_selected']:
        item = record['value']
        if item.get('mode')!='selected' or item.get('mechanism',{}).get('mechanism_pass') is not True:
            continue
        try:
            signature = item['abi'][0]
            if signature[0]!='dict': raise ValueError('实际ABI签名不是dict')
            types = {key[1]:value[1] for key,value in signature[1]
                     if key[0]=='str' and value[0]=='str'}
            types = {name:types.get(name) for name in STRIDES}
            candidate_hash = item.get('candidate_hash')
            compiled = item.get('candidate_resources',{})
            valid = (all(value=='constexpr' for value in types.values()) and bool(candidate_hash)
                     and compiled.get('hash')==candidate_hash and bool(compiled.get('asm_sha256')))
            selected.append(dict(line=record['line'],valid=valid,stride_types=types,
                normal_hash=item.get('normal_hash'),candidate_hash=candidate_hash,
                candidate_resources=compiled,normal_resources=item.get('normal_resources')))
        except (ValueError,KeyError,IndexError,TypeError) as error:
            errors.append(dict(line=record['line'],error=repr(error)))
    graph = [line for line in text.splitlines() if 'Capturing CUDA graph' in line or 'Graph capturing finished' in line]
    installed_ok = bool(installed) and all(item['value'].get('installed') is True
        and item['value'].get('kernel_sha256')==EXPECTED_KERNEL for item in installed)
    result = dict(valid=bool(installed_ok and selected and all(item['valid'] for item in selected)
                            and graph and stack['valid'] and not errors),
        expected_generated_kernel_sha256=EXPECTED_KERNEL,normalization_install=installed,
        selected_compiled_abi=selected,graph_capture_log=graph,stack=stack,parse_errors=errors,
        source=str(source),q_hoist_artifacts=str(control/'q-hoist-artifacts'),
        limitation='原源码安装回执、首次实际Q-hoist编译选中的ABI/资源和compute-order回执；不是逐请求kernel轨迹。',
        missing_policy='启动期缺首次回执仅待确认；完整负载后缺项不冒称闭合，保留原始绝对成绩。')
    (control/'prefill-activation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
