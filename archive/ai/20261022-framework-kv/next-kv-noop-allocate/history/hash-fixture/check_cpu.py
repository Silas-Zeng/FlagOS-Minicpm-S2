"""最短CPU判别：封存原类/原方法的完整no-op链；不导入框架/Tensor或执行新页分配。"""
from __future__ import annotations
from abc import ABC, abstractmethod
import ast
from collections import defaultdict, deque
from collections.abc import Sequence
from dataclasses import dataclass
import enum
import hashlib
import itertools
import json
from pathlib import Path
import runpy
import statistics
import sys
from time import perf_counter_ns, thread_time_ns
from types import ModuleType, SimpleNamespace
from typing import NamedTuple, overload

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).parent
policy = runpy.run_path(str(HERE/'biv150_noop_allocate.py'))
SOURCES = {
    'vllm.v1.core.kv_cache_manager': ROOT/'analysis/source/growth-admission/kv_cache_manager.py',
    'vllm.v1.core.kv_cache_coordinator': ROOT/'analysis/source/growth-admission/kv_cache_coordinator.py',
    'vllm.v1.core.single_type_kv_cache_manager': ROOT/'analysis/source/growth-admission/single_type_kv_cache_manager.py',
    'vllm.v1.core.block_pool': ROOT/'analysis/source/growth-admission/block_pool.py',
    'vllm.v1.request': ROOT/'experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/request.py',
}
SELECT = {
    'vllm.v1.request': ('Request', 'RequestStatus'),
    'vllm.v1.core.single_type_kv_cache_manager': ('SingleTypeKVCacheManager', 'FullAttentionManager', 'CrossAttentionManager'),
    'vllm.v1.core.kv_cache_coordinator': ('KVCacheCoordinator', 'UnitaryKVCacheCoordinator'),
    'vllm.v1.core.block_pool': ('BlockPool',),
    'vllm.v1.core.kv_cache_manager': ('KVCacheBlocks', 'KVCacheManager'),
}


def actual_classes():
    shared = dict(ABC=ABC, abstractmethod=abstractmethod, defaultdict=defaultdict, deque=deque,
        dataclass=dataclass, enum=enum, itertools=itertools, Sequence=Sequence,
        NamedTuple=NamedTuple, overload=overload,
        # CPU片段唯一数学依赖：本合同仅非负整数/正16的原cdiv语义。
        cdiv=lambda a,b:(a+b-1)//b)
    modules = {}
    for name, selected in SELECT.items():
        path = SOURCES[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == policy['EXPECTED'][name]
        tree = ast.parse(path.read_bytes())
        classes = [n for n in tree.body if isinstance(n,ast.ClassDef) and n.name in selected]
        assert len(classes)==len(selected)
        # 类及方法AST完整；只隔离未使用的import/构造器依赖，不伪造Tensor/框架模块。
        module = ModuleType(name); module.__file__ = str(path)
        module.__dict__.update(shared); sys.modules[name]=module
        # 直接保留完整ClassDef节点（包括decorators/原line），不能用不含decorator的source_segment。
        future=ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0)
        exact=ast.fix_missing_locations(ast.Module(body=[future,*classes],type_ignores=[]))
        exec(compile(exact,str(path),'exec'),module.__dict__)
        modules[name]=module
        shared.update({n:getattr(module,n) for n in selected})
    return modules


MODULES = actual_classes()
km, co, st, bp, rq = (MODULES[n] for n in policy['EXPECTED'])


def fixture(n=1, *, computed=16653, known=16653, cached=None, owned=None, free=4096):
    pool=object.__new__(bp.BlockPool); pool.free_block_queue=SimpleNamespace(num_free_blocks=free)
    single=object.__new__(st.FullAttentionManager)
    single.block_size=single.scheduler_block_size=16
    single._max_admission_blocks_per_request=None; single.block_pool=pool
    single.use_eagle=False; single.enable_caching=True; single.new_block_ids=[]
    single.req_to_blocks=defaultdict(list); single.num_cached_block={}; single.kv_cache_spec=None
    coordinator=object.__new__(co.UnitaryKVCacheCoordinator)
    coordinator.single_type_managers=(single,); coordinator.retention_interval=None
    manager=object.__new__(km.KVCacheManager)
    manager.coordinator=coordinator; manager.block_pool=pool; manager.max_model_len=131072
    manager.enable_caching=True; manager.use_eagle=False; manager.watermark_blocks=0
    manager.empty_kv_cache_blocks=km.KVCacheBlocks(((),))
    requests={}
    for i in range(n):
        r=object.__new__(rq.Request); r.request_id=str(i); r.status=rq.RequestStatus.RUNNING
        r._all_token_ids=[0]*known; r._output_token_ids=[0]*(known-16384)
        r.num_prompt_tokens=16384; r.num_computed_tokens=computed
        r.num_output_placeholders=max(0,computed-known+1)
        r.stop_reason=None; r.resumable=False; r.spec_token_ids=[]; r.mm_features=[]
        r.prompt_embeds=None; r.pooling_params=None; r.structured_output_request=None
        r.async_tokens_to_discard=0; r.max_tokens=1024
        requests[r.request_id]=r
        single.req_to_blocks[r.request_id]=[object()] * (owned if owned is not None else (computed+16)//16)
        single.num_cached_block[r.request_id]=known//16 if cached is None else cached
    handle=policy['create'](manager,modules=MODULES,requests=requests)
    return manager,single,pool,requests,handle


def state(f):
    manager,single,pool,requests,_=f
    return (dict(single.num_cached_block), tuple((k,id(v),tuple(map(id,v))) for k,v in single.req_to_blocks.items()),
        tuple(single.new_block_ids), pool.free_block_queue.num_free_blocks,
        tuple((r.status,r.num_computed_tokens,r.num_output_placeholders,r.num_tokens,r.num_output_tokens) for r in requests.values()),
        id(manager.empty_kv_cache_blocks), manager.empty_kv_cache_blocks.blocks)


def checks():
    result={}
    for label,c,k in (('normal_q1',16653,16653),('queued_optimistic_known_cap',16656,16655)):
        f=fixture(computed=c,known=k); r=next(iter(f[3].values())); h=f[-1]; before=state(f)
        baseline=h['original'](r,1,num_lookahead_tokens=0)
        candidate=h['call'](r,1,num_lookahead_tokens=0)
        assert baseline is candidate is h['empty'] and state(f)==before
        assert h['counts']=={'selected':1,'fallback':0}
        result[label]='same original empty object; all tracked allocator/request state unchanged'
    # 两个真实边界执行原方法直到确实进入原pool写入口；不伪造该写操作成功。
    for label,options,method in (('new_page_boundary',{'computed':16656,'known':16656,'owned':1041},'get_new_blocks'),
                                 ('new_hash_boundary',{'computed':16655,'known':16656,'owned':1042,'cached':1040},'cache_full_blocks')):
        f=fixture(**options); r=next(iter(f[3].values())); h=f[-1]; before=state(f); calls=[]
        error=RuntimeError('CPU boundary stops before real pool mutation')
        def stop(*args,**kwargs):
            calls.append(method); raise error
        setattr(f[2],method,stop)
        for function in (h['original'],h['call']):
            try: function(r,1,num_lookahead_tokens=0)
            except RuntimeError as observed: assert observed is error and observed.__context__ is None
            else: raise AssertionError('boundary did not reach original pool')
        assert calls==[method,method] and state(f)==before and h['counts']=={'selected':0,'fallback':1}
        result[label]='both reached same original pool mutation entry; actual mutation deliberately not run'
    for status in (rq.RequestStatus.PREEMPTED,rq.RequestStatus.FINISHED_ABORTED,rq.RequestStatus.FINISHED_STOPPED):
        f=fixture(); r=next(iter(f[3].values())); r.status=status; before=state(f); h=f[-1]
        assert h['call'](r,1) is h['original'](r,1) is h['empty']
        assert state(f)==before and h['counts']['fallback']==1 and h['counts']['selected']==0
        result[status.name]='original fallback'
    f=fixture(free=0); r=next(iter(f[3].values())); h=f[-1]; before=state(f)
    assert h['call'](r,1,reserved_blocks=1) is h['original'](r,1,reserved_blocks=1) is None
    assert state(f)==before and h['counts']['fallback']==1
    result['reserved_blocks_zero_demand_can_still_fail']='original None preserved'
    return result


def timing(n):
    f=fixture(n); h=f[-1]; requests=list(f[3].values()); before=state(f)
    for r in requests: h['original'](r,1,num_lookahead_tokens=0); h['call'](r,1,num_lookahead_tokens=0)
    windows=[]; batches=2048
    for arm in ('baseline','candidate','candidate','baseline'):
        function=h['original'] if arm=='baseline' else h['call']
        count_before=dict(h['counts']); wall=perf_counter_ns(); cpu=thread_time_ns()
        for _ in range(batches):
            for r in requests: function(r,1,num_lookahead_tokens=0)
        cpu=thread_time_ns()-cpu; wall=perf_counter_ns()-wall
        if arm=='candidate': assert h['counts']['selected']-count_before['selected']==batches*n
        windows.append({'arm':arm,'batches':batches,'requests_per_batch':n,'thread_cpu_ns_per_batch':cpu/batches,'wall_ns_per_batch':wall/batches})
    assert state(f)==before
    a=statistics.median(w['wall_ns_per_batch'] for w in windows if w['arm']=='baseline')
    b=statistics.median(w['wall_ns_per_batch'] for w in windows if w['arm']=='candidate')
    return {'N':n,'windows':windows,'median_wall_ns_baseline':a,'median_wall_ns_candidate':b,
            'wall_ns_saved_per_batch':a-b,'local_fragment_only_not_E2E':True}


if __name__=='__main__':
    output=HERE/'cpu-check.json'
    if output.exists(): raise FileExistsError('不覆盖旧结果')
    result={'kind':'actual原类/原方法CPU无状态链片段；非生产scope/分配写入/GPU结果',
        'source_sha256':{k:hashlib.sha256(v.read_bytes()).hexdigest() for k,v in SOURCES.items()},
        'policy_sha256':hashlib.sha256((HERE/'biv150_noop_allocate.py').read_bytes()).hexdigest(),
        'checks':checks(),'timing':[timing(n) for n in (30,31,64)],
        'limits':['隔离原类定义/未执行构造器；只填本no-op路径所需原字段，opaque owned refs没有读页内容',
            '新页/hash边界只到原pool写入口即停止，不伪造pool操作成功；无Tensor/无GPU/无整框架mock',
            'CPU cdiv仅非负整数正除数的等价表达；原source方法体不改',
            '局部Windows perf_counter wall配对中位数为净省判据；thread_time仅诊断（可能15.625ms量化），非实际6CPU服务；每步完整guard/kwargs/计数计入，来源验证一次在窗口外',
            '无生产安装入口；有CPU省才准备严格422模型scope/薄服务，queue2可遮盖CPU节省']}
    result['cpu_fragment_go']=all(x['wall_ns_saved_per_batch']>0 for x in result['timing'])
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'cpu_fragment_go':result['cpu_fragment_go'],'timing':result['timing'],'output':str(output)},ensure_ascii=False))
