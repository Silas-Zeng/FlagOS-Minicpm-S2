"""独立诊断：原writer返回后只读真实请求的BF16位，不改原计算。"""
from pathlib import Path
import hashlib
import json
import os

BACKEND_SHA='1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605'
NAMES=['model.layers.'+str(i)+'.self_attn.attn' for i in range(42)]
_installed=False


def save(path, data):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)


def token_sha(ids):
    return hashlib.sha256(json.dumps(list(ids),separators=(',',':')).encode()).hexdigest()


def registry(runner):
    ctx=runner.compilation_config.static_forward_context
    if set(ctx)!=set(NAMES) or len({id(ctx[n]) for n in NAMES})!=42:
        raise ValueError('static_forward_context不是精确42层，不能猜layer身份')
    return {id(ctx[n]):(i,n,ctx[n]) for i,n in enumerate(NAMES)}


def request_identity(runner, arm):
    if runner.input_batch.num_reqs!=1:
        raise ValueError('arm后不是唯一真实请求')
    ids=runner.input_batch.req_ids
    if len(ids)!=1 or not isinstance(ids[0],str) or not ids[0]:
        raise ValueError('真实request_id不唯一')
    request=runner.requests[ids[0]]
    tokens=request.prompt_token_ids
    if tokens is None or len(tokens)!=arm['prompt_tokens'] or token_sha(tokens)!=arm['prompt_ids_sha256']:
        raise ValueError('engine真实prompt IDs与原/tokenize回复不相同')
    return ids[0]


def sample_indices(slots, positions, limit):
    import numpy as np
    if slots.ndim!=1 or positions.ndim!=1 or len(positions)<len(slots):
        raise ValueError('slot/position shape不符')
    rows=np.flatnonzero(slots>=0)[:128]
    if not len(rows):raise ValueError('没有真实有效slot；禁止采dummy')
    chosen=slots[rows]
    pos=positions[rows]
    if len(set(map(int,chosen)))!=len(chosen) or np.any(chosen>=limit):
        raise ValueError('slot重复或越界')
    return rows,chosen,pos


def install(worker):
    global _installed
    if _installed:raise ValueError('同一worker重复安装采样器')
    import numpy as np
    import torch
    import importlib
    backend=importlib.import_module('vllm.v1.attention.backends.triton_attn')
    if hashlib.sha256(Path(backend.__file__).read_bytes()).hexdigest()!=BACKEND_SHA:
        raise ValueError('原backend源码变化')
    folder=Path(os.environ['MINICPM_REAL_KV_SAMPLE_DIR']).resolve(strict=True)
    runner=worker.model_runner
    text=worker.vllm_config.model_config.hf_text_config
    if tuple(getattr(text,k) for k in ('hidden_size','intermediate_size','num_hidden_layers','num_attention_heads','num_key_value_heads'))!=(2048,6144,42,16,2):
        raise ValueError('非固定MiniCPM5-2B结构')
    layers=registry(runner)
    original=backend.TritonAttentionImpl.do_kv_cache_update
    if original.__module__!=backend.__name__ or original.__qualname__!='TritonAttentionImpl.do_kv_cache_update':
        raise ValueError('原writer方法已被包装')
    records={};samples={};binding=None
    def wrapped(self,layer,key,value,kv_cache,slot_mapping):
        nonlocal binding
        result=original(self,layer,key,value,kv_cache,slot_mapping)
        # 未arm和capture期间没有数据读取/D2H；启动暖图/dummy不会进入采样。
        if not (folder/'arm.json').is_file() or (folder/'complete.json').exists():return result
        if torch.cuda.is_current_stream_capturing():return result
        try:
            arm=json.loads((folder/'arm.json').read_bytes())
            rid=request_identity(runner,arm)
            if id(layer) not in layers:raise ValueError('writer layer不在真实42层registry')
            index,name,registered=layers[id(layer)]
            if registered is not layer:raise ValueError('layer对象身份不一致')
            if index in records:return result
            bound=layer.kv_cache
            if isinstance(bound,(list,tuple)):
                if len(bound)!=1:raise ValueError('多virtual engine cache不在诊断范围')
                bound=bound[0]
            if not isinstance(bound,torch.Tensor) or bound.data_ptr()!=kv_cache.data_ptr() or bound.shape!=kv_cache.shape or bound.stride()!=kv_cache.stride():
                raise ValueError('实际writer cache与layer绑定不一致')
            if key.dtype!=torch.bfloat16 or value.dtype!=torch.bfloat16 or kv_cache.dtype!=torch.bfloat16:
                raise ValueError('不是原BF16缓存')
            if key.ndim!=3 or tuple(key.shape[1:])!=(2,128) or key.shape!=value.shape:
                raise ValueError('真实K/V shape变化')
            if kv_cache.ndim!=5 or tuple(kv_cache.shape[1:])!=(2,16,2,128) or kv_cache.stride()!=(8192,4096,256,128,1):
                raise ValueError('缓存不是原normal NHD；不猜packing/shared路径')
            slots=slot_mapping.detach().cpu().numpy().astype(np.int64)
            positions=runner.positions[:len(slots)].detach().cpu().numpy().astype(np.int64)
            rows,chosen,pos=sample_indices(slots,positions,kv_cache.shape[0]*16)
            if rows[-1]>=key.shape[0] or np.any(pos<0) or np.any(pos>=arm['prompt_tokens']):
                raise ValueError('采样不属于真实prompt位置')
            if binding is None:binding=(rid,chosen.tolist(),pos.tolist())
            if binding!=(rid,chosen.tolist(),pos.tolist()):raise ValueError('42层请求/slot/position不一致')
            row_gpu=torch.tensor(rows,device=key.device,dtype=torch.int64)
            slot_gpu=torch.tensor(chosen,device=key.device,dtype=torch.int64)
            def bits(x):return x.detach().contiguous().cpu().view(torch.int16).numpy().view(np.uint16)
            k=bits(key.index_select(0,row_gpu));v=bits(value.index_select(0,row_gpu))
            kc=bits(kv_cache[slot_gpu//16,0,slot_gpu%16]);vc=bits(kv_cache[slot_gpu//16,1,slot_gpu%16])
            if not np.array_equal(k,kc) or not np.array_equal(v,vc):raise ValueError('原writer源/目标KV位型不相同')
            np.savez(folder/('layer-%02d.npz'%index),k_bits=k,v_bits=v)
            records[index]=dict(index=index,layer_name=name,request_id=rid,slots=chosen.tolist(),positions=pos.tolist(),
                source_rows=rows.tolist(),cache_data_ptr=kv_cache.data_ptr(),cache_shape=list(kv_cache.shape),
                cache_stride=list(kv_cache.stride()),key_cache_equal=True,value_cache_equal=True,
                sample_sha256=hashlib.sha256((folder/('layer-%02d.npz'%index)).read_bytes()).hexdigest())
            samples[index]=(k,v)
            save(folder/'progress.json',dict(layers=len(records),records=[records[i] for i in sorted(records)]))
            if len(records)==42:
                k_all=np.stack([samples[i][0] for i in range(42)])
                v_all=np.stack([samples[i][1] for i in range(42)])
                if k_all.nbytes+v_all.nbytes>5505024:raise ValueError('超过5.25MiB位样本预算')
                np.savez(folder/'real-kv.npz',k_bits=k_all,v_bits=v_all)
                meta=dict(model='MiniCPM5-2B',real_model_activations=True,
                    kind='单条原数学题prompt KV诊断；非准确率/性能/16K代表性',
                    npz_sha256=hashlib.sha256((folder/'real-kv.npz').read_bytes()).hexdigest(),
                    arm=arm,request_id=rid,layers=[records[i] for i in range(42)],sample_bytes=k_all.nbytes+v_all.nbytes)
                save(folder/'real-kv.json',meta)
                save(folder/'complete.json',dict(status='sampled_42_real_layers',sample_bytes=meta['sample_bytes'],
                    npz_sha256=meta['npz_sha256'],all_writer_cache_bits_equal=True))
        except BaseException as error:
            save(folder/'sample-error.json',dict(error=repr(error)))
            raise
        return result
    backend.TritonAttentionImpl.do_kv_cache_update=wrapped
    _installed=True
    save(folder/'installed.json',dict(pid=os.getpid(),backend_sha256=BACKEND_SHA,
        layers=[x[1] for x in sorted(layers.values())],runner_source_sha256=hashlib.sha256(Path(importlib.import_module(type(runner).__module__).__file__).read_bytes()).hexdigest()))
