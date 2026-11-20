#!/usr/bin/env python3
"""Compare original and candidate storage/bounds helpers on real CPU tensors."""
from __future__ import annotations
import argparse, importlib.util, json, statistics, time
from pathlib import Path

HERE=Path(__file__).resolve().parent

def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    if spec is None or spec.loader is None: raise RuntimeError("cannot load helper source")
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

def outcome(fn,*args):
    try:return ("ok",fn(*args))
    except Exception as exc:return (type(exc).__name__,str(exc))

def validate_storage_checks(mod,tensors,cache=None):
    q,k,scale,v,lens,table,partial,maximum,summation=tensors
    for t in tensors: mod.bounds(t,cache) if cache is not None else mod.bounds(t)
    for src in (q,lens,table):
        overlap=mod.overlaps(src,k,cache) if cache is not None else mod.overlaps(src,k)
        if overlap: raise RuntimeError('source/live-cache backing alias')
    for i,out in enumerate((partial,maximum,summation)):
        for src in (q,k,scale,v,lens,table):
            overlap=mod.overlaps(out,src,cache) if cache is not None else mod.overlaps(out,src)
            if overlap: raise RuntimeError('scratch/source backing alias')
        for other in (partial,maximum,summation)[:i]:
            overlap=mod.overlaps(out,other,cache) if cache is not None else mod.overlaps(out,other)
            if overlap: raise RuntimeError('scratch backing alias')

def make_validate_tensors(torch):
    q=torch.empty_strided((1,16,128),(2048,128,1),dtype=torch.bfloat16)
    key=torch.empty((8,16,128),dtype=torch.bfloat16)
    scale=key.view(torch.int8).as_strided((8,16,1),(4096,256,1))
    value=key.as_strided((8,16,128),(2048,128,1))
    lens=torch.empty((1,),dtype=torch.int32)
    table=torch.empty((1,8),dtype=torch.int32)
    partial=torch.empty((1,16,8,128),dtype=torch.float32)
    maximum=torch.empty((1,16,8),dtype=torch.float32)
    summation=torch.empty((1,16,8),dtype=torch.float32)
    return [q,key,scale,value,lens,table,partial,maximum,summation]

def benchmark(torch,old,new,iterations=400):
    tensors=make_validate_tensors(torch)
    # Correctness gates run before any timing and use actual CPU tensors.
    validate_storage_checks(old,tensors)
    validate_storage_checks(new,tensors,{})
    old_alias=[old.overlaps(tensors[a],tensors[b]) for a,b in
        [(0,1),(1,2),(1,3),(6,7),(7,8),(0,4),(2,5)]]
    new_alias=[new.overlaps(tensors[a],tensors[b],{}) for a,b in
        [(0,1),(1,2),(1,3),(6,7),(7,8),(0,4),(2,5)]]
    if old_alias!=new_alias: raise AssertionError('benchmark alias precheck mismatch')
    # A/BAB/BAAB order counters warmed code only; each timed window runs the
    # exact same 9 bounds + 24 overlap relations, with a new B cache per call.
    sequence=['A','B','B','A','B','A','A','B']
    samples=[]
    funcs={'A':lambda:validate_storage_checks(old,tensors),
           'B':lambda:validate_storage_checks(new,tensors,{})}
    for arm in ('A','B'): funcs[arm]()
    for index,arm in enumerate(sequence):
        t0=time.perf_counter_ns()
        for _ in range(iterations): funcs[arm]()
        elapsed=time.perf_counter_ns()-t0
        samples.append({'window':index,'arm':arm,'iterations':iterations,
                        'elapsed_ns':elapsed,'per_call_ns':elapsed/iterations})
    medians={arm:statistics.median(x['per_call_ns'] for x in samples if x['arm']==arm)
             for arm in ('A','B')}
    return {'order':'ABBA BAAB','windows':samples,'median_per_call_ns':medians,
            'scope':'9个真实CPU Tensor上的bounds+24个overlap关系；不是Adapter完整调用或端到端吞吐。',
            'storage_aliases':{'key_scale_value_share_storage':True,
                               'three_scratch_storages_independent':True}}

def check_new_call_snapshot(torch,new):
    t=torch.empty((8,4),dtype=torch.bfloat16)
    cache_a={};new.bounds(t,cache_a)
    old_storage=t.untyped_storage() # retain backing allocation to prevent address reuse
    old_range=cache_a[id(t)][1]
    replacement=torch.empty((8,4),dtype=torch.bfloat16)
    t.set_(replacement.untyped_storage(),0,(8,4),(4,1))
    cache_b={};new.bounds(t,cache_b)
    new_range=cache_b[id(t)][1]
    if old_range[0]==new_range[0] or old_range[1:]==new_range[1:]:
        raise AssertionError('new validate-call cache did not observe replaced storage')
    return {'status':'pass','operation':'real CPU Tensor.set_ to retained distinct storage',
            'new_call_cache_created':True,'storage_identity_changed':True,
            'old_storage_retained':old_storage is not None}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--baseline',type=Path,default=HERE/'baseline.py')
    ap.add_argument('--candidate',type=Path,default=HERE/'candidate.py')
    ap.add_argument('--benchmark',action='store_true',help='run short CPU-only ABBA/BAAB helper benchmark after correctness checks')
    a=ap.parse_args()
    try: import torch
    except ImportError as exc:
        print(json.dumps({'status':'not_run','reason':'real PyTorch CPU runtime unavailable','detail':str(exc)},ensure_ascii=False))
        return 2
    old=module(a.baseline,'snapshot_baseline_helpers');new=module(a.candidate,'snapshot_candidate_helpers')
    base=torch.arange(512,dtype=torch.bfloat16)
    view=base.as_strided((8,4),(16,2),storage_offset=3)
    sibling=base.as_strided((8,4),(16,2),storage_offset=8)
    independent=torch.empty((8,4),dtype=torch.bfloat16)
    integer=torch.arange(64,dtype=torch.int32)
    bytes_=torch.arange(64,dtype=torch.int8)
    scalar=torch.arange(64,dtype=torch.float32)
    empty=torch.empty_strided((0,4),(8,1),dtype=torch.bfloat16)
    zero_stride=torch.empty((1,4),dtype=torch.bfloat16).expand(8,4)
    unknown=torch.empty((8,4),dtype=torch.float64)
    tensors=[base,view,sibling,independent,integer,bytes_,scalar,empty,zero_stride,unknown]
    cache={};bounds=[]
    for i,t in enumerate(tensors):
        before=outcome(old.bounds,t)
        after=outcome(new.bounds,t,cache)
        if before!=after: raise AssertionError(f'bounds mismatch case {i}: {before!r} != {after!r}')
        if outcome(old.bounds,t)!=outcome(new.bounds,t):
            raise AssertionError(f'uncached bounds behavior changed case {i}')
        if outcome(old.storage,t)!=outcome(new.storage,t):
            raise AssertionError(f'generic storage helper changed case {i}')
        bounds.append({'case':i,'dtype':str(t.dtype),'shape':list(t.shape),'stride':list(t.stride()),
                       'status':before[0],'message':before[1] if before[0]!='ok' else None})
    # Every overlap check remains conservative on backing storage, even when view slices
    # do not intersect logically; independent storages remain non-overlapping.
    pairs=[(base,view),(view,sibling),(view,independent),(integer,bytes_),
           (scalar,empty),(empty,independent),(view,view)]
    alias=[]
    for i,(x,y) in enumerate(pairs):
        before=outcome(old.overlaps,x,y)
        after=outcome(new.overlaps,x,y,cache)
        if before!=after: raise AssertionError(f'overlap mismatch pair {i}: {before!r} != {after!r}')
        if outcome(old.overlaps,x,y)!=outcome(new.overlaps,x,y):
            raise AssertionError(f'uncached overlap behavior changed pair {i}')
        alias.append({'pair':i,'baseline':before[1] if before[0]=='ok' else before,
                      'candidate':after[1] if after[0]=='ok' else after})
    expected_cached={id(t) for t,result in zip(tensors,bounds) if result['status']=='ok'}
    if set(cache)!=expected_cached or any(cache[id(t)][0] is not t for t in tensors if id(t) in cache):
        raise AssertionError('candidate cache is not exact Tensor-object keyed')
    before=len(cache)
    for x,y in pairs: new.overlaps(x,y,cache)
    if len(cache)!=before: raise AssertionError('alias checks created duplicate object snapshots')
    new_call=check_new_call_snapshot(torch,new)
    timed=benchmark(torch,old,new) if a.benchmark else None
    print(json.dumps({'status':'pass','runtime':'real PyTorch CPU tensors','bounds_cases':bounds,
        'alias_cases':alias,'unique_tensor_snapshots':len(cache),
        'view_objects_kept_distinct':id(view)!=id(sibling),'new_call_snapshot':new_call,
        'benchmark':timed,'cuda_or_device_action':False},ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':raise SystemExit(main())
