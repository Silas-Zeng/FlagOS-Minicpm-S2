"""只回收官方原启动/Graph日志和已有JIT产物，不挂钩/修改模型调用。"""
import hashlib
import json
from pathlib import Path
import re
import shutil


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
    result=dict(valid=bool(first and graph and saved and all(x['cg_load_count']>0 for x in saved)),
        first_width=first,graph_capture_log=graph,source=str(source),cache_root=str(cache),artifacts=saved,
        limitation='原入口选中日志＋本源码编译/Graph保存链；无额外模型调用或profiler，不声称逐请求逐kernel轨迹。',
        missing_policy='若Triton跨目录复用旧等价binary导致无本路径产物，保留官方成绩并记激活证据待补，不能伪称已闭合。')
    (out/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result
