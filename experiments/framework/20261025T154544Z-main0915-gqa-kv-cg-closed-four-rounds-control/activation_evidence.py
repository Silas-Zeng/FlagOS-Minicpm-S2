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


def capture(run,control,source,env):
    text=re.sub(r'\x1b\[[0-9;]*m','',(run/'server.log').read_text(errors='replace'))
    first=[line for line in text.splitlines() if 'BIV150_GQA_DECODE_FIRST_WIDTH ' in line]
    graph=[line for line in text.splitlines() if 'Capturing CUDA graph' in line or 'Graph capturing finished' in line]
    cache=Path(env.get('TRITON_CACHE_DIR','/root/.triton/cache')).resolve()
    expected=(source/'vllm_fl/patches/biv150_gqa_decode.py').as_posix()
    saved=[]
    out=control/'gqa-jit'; out.mkdir()
    for origin in cache.glob('*/_gqa_decode_attention.source'):
        ir=origin.read_text(errors='replace')
        if expected not in ir: continue
        folder=origin.parent
        assembly=folder/'_gqa_decode_attention.asm'
        metadata=folder/'_gqa_decode_attention.json'
        if not assembly.is_file() or not metadata.is_file(): continue
        asm=assembly.read_text(errors='replace')
        loads=[line.strip() for line in asm.splitlines() if re.search(r'\b(?:ml|sl)_lsa_(?:blkload|load)_.*[,]\s*cg\s*(?:;.*)?$',line)]
        target=out/folder.name; target.mkdir()
        hashes={}
        for file in folder.glob('_gqa_decode_attention.*'):
            if file.is_file():
                shutil.copyfile(file,target/file.name)
                hashes[file.name]=hashlib.sha256(file.read_bytes()).hexdigest()
        saved.append(dict(directory=str(folder),cg_load_count=len(loads),cg_loads=loads,
                          metadata=json.loads(metadata.read_text()),files=hashes))
    stack=stack_evidence(run/'server.log')
    result=dict(valid=bool(first and graph and saved and all(x['cg_load_count']>0 for x in saved) and stack['valid']),
        first_width=first,graph_capture_log=graph,source=str(source),cache_root=str(cache),artifacts=saved,
        stack=stack,
        limitation='原入口选中日志＋本源码编译/Graph保存链；无额外模型调用或profiler，不声称逐请求逐kernel轨迹。',
        missing_policy='若Triton跨目录复用旧等价binary导致无本路径产物，保留官方成绩并记激活证据待补，不能伪称已闭合。')
    (out/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
