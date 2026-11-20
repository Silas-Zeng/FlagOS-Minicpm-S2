"""只读当前热点SQLite；复用既有解码/分类，按真实时钟映射窗口并算区间并集。"""
import argparse
from bisect import bisect_left
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import statistics

HERE=Path(__file__).resolve().parent
READER_SHA='25c5ae091cbf289e80ff9dea979b6756fd31ee832cc75ae79b55046fd060a162'
CLASSIFIER_SHA='cb65e1dfc2f745c461bf721b563e7b2d8ac4959a2741064bf5c84bf9bf628b91'
TABLES={'kernel':'cuda_kernel_data','copy':'cuda_memcpy_data','memset':'cuda_memset_data','graph':'cuda_graph_data','api':'cuda_api_data'}
sha=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path,pin,name):
    assert sha(path)==pin,(path,'既有分析源变化')
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

def merge(intervals):
    result=[]
    for left,right in sorted(intervals):
        if right<=left:continue
        if result and left<=result[-1][1]:result[-1]=(result[-1][0],max(right,result[-1][1]))
        else:result.append((left,right))
    return result
def measure(intervals):return sum(b-a for a,b in merge(intervals))
def overlap(intervals,other):
    left=merge(intervals);right=merge(other);i=j=0;result=[]
    while i<len(left) and j<len(right):
        a,b=left[i];c,d=right[j]
        if min(b,d)>max(a,c):result.append((max(a,c),min(b,d)))
        if b<d:i+=1
        else:j+=1
    return result
def clips(rows,left,right):
    return [dict(row,ts=max(row['ts'],left),end=min(row['end'],right),clipped=row['ts']<left or row['end']>right)
            for row in rows if row['end']>left and row['ts']<right]
def intervals(rows):return [(r['ts'],r['end']) for r in rows]
def aggregate(rows,key):
    groups=defaultdict(list)
    for row in rows:groups[key(row)].append(row)
    result=[]
    for name,items in groups.items():
        result.append(dict(name=name,calls=len(items),sum_ms=sum(x['end']-x['ts'] for x in items)/1e6,
            union_ms=measure(intervals(items))/1e6,bytes=sum(x.get('bytes',0) or 0 for x in items),
            kernels=sorted({x['name'] for x in items})))
    return sorted(result,key=lambda x:-x['sum_ms'])

def read_rows(database,reader,schema,table):
    if table not in schema:return [],dict(absent=True)
    query,resolution,columns=reader.event_query(database,schema,table)
    names=reader.lookup(database,schema,('function_name_map',),('id',),('name',))
    sizes=reader.lookup(database,schema,('function_size_map',),('id',),('name',))
    result=[];invalid=0
    for values in database.execute(query):
        row=dict(zip(columns,values))
        if not isinstance(row.get('ts'),int) or not isinstance(row.get('dur'),int) or row['dur']<=0:
            invalid+=1;continue
        name=row.get('name',names.get(row.get('name_id')))
        result.append(dict(row,name=str(name) if name is not None else 'unresolved:'+str(row.get('name_id')),
                           end=row['ts']+row['dur'],grid=row.get('grid',sizes.get(row.get('grid_id')))))
    return result,dict(resolution=resolution,rows=len(result),nonpositive_or_missing=invalid)

def clocks(database,schema):
    if 'clock_snapshot' not in schema:return dict(valid=False,reason='无clock_snapshot')
    rows=database.execute("SELECT ts,clock_value,snapshot_id FROM clock_snapshot WHERE clock_name='MONOTONIC' ORDER BY ts").fetchall()
    if len(rows)<2:return dict(valid=False,reason='MONOTONIC快照不足',snapshots=rows)
    offsets=[ts-value for ts,value,_ in rows]
    spread=max(offsets)-min(offsets)
    return dict(valid=spread<=1000000,offset_spread_ns=spread,median_offset_ns=statistics.median(offsets),
        snapshots=[dict(trace_ns=ts,monotonic_ns=value,offset_ns=ts-value,snapshot_id=sid) for ts,value,sid in rows],
        method='实际MONOTONIC clock_snapshot对应trace ts；使用最近快照偏移，要求全程偏移跨度<=1ms',
        limitation='映射误差以本次快照偏移跨度报告；不是额外硬件校时')
def to_trace(clock,value):
    entries=clock['snapshots'];entry=min(entries,key=lambda x:abs(x['monotonic_ns']-value))
    assert entries[0]['monotonic_ns']<=value<=entries[-1]['monotonic_ns'],'事件未被clock快照包围'
    return value+entry['offset_ns']

def classify(name,grid,helper):
    lower=name.lower()
    if '_gqa_decode_attention' in lower:return 'GQA-decode'
    if '_reduce_partials' in lower:return 'GQA-reduce'
    if any(x in lower for x in ('quantize_cached_rows','quantize_residual_rows','quantize_rows')):return 'Native-row-quantize'
    if any(x in lower for x in ('residual_silu_epilogue','silu_epilogue')):return 'Native-SiLU-epilogue'
    return helper.category(name.replace('kernel_biv150_prefill_normalized','kernel_unified_attention'),{'grid':grid})

def per_step(rows,steps,clock,helper):
    """按同PID/correlationId把设备活动归到实际launch API所在主机步；不按GPU时间切错异步归属。"""
    api=defaultdict(list)
    for row in rows['api']:api[(row.get('processId'),row.get('correlationId'))].append(row)
    bounds=[(to_trace(clock,s['execute_start_ns']),to_trace(clock,s['sample_return_ns'])) for s in steps]
    parts=[{k:[] for k in ('kernel','copy','memset','graph')} for _ in steps]
    unknown=[]
    for kind in parts[0]:
        for row in rows[kind]:
            matches=api[(row.get('processId'),row.get('correlationId'))]
            hits=[i for i,(a,b) in enumerate(bounds) if len(matches)==1 and a<=matches[0]['ts']<b]
            if len(hits)==1:parts[hits[0]][kind].append(row)
            else:unknown.append(dict(kind=kind,name=row['name'],correlation=row.get('correlationId'),api_matches=len(matches),step_matches=hits))
    result=[]
    for i,part in enumerate(parts):
        gpu=[p for rows2 in part.values() for p in intervals(rows2)]
        result.append(dict(index=i,group='boundary_first_two' if i<2 else 'interior',N=steps[i]['N'],M=steps[i]['M'],
            gpu_union_ms=measure(gpu)/1e6,
            kernel_categories=aggregate(part['kernel'],lambda r:classify(r['name'],r.get('grid'),helper)),
            graph=aggregate(part['graph'],lambda r:r['name']),
            copy=aggregate(part['copy'],lambda r:str(r.get('srcKind'))+' -> '+str(r.get('dstKind')))))
    return dict(method='同PID/correlationId唯一API匹配，API启动时刻在execute_start..sample_return内',
        steps=result,unassigned=unknown,limitation='每步GPU可能异步重叠；步并集不能直接相加作窗口延迟。')

def summarize_window(start,stop,clock,all_rows,helper):
    left=to_trace(clock,start['monotonic_ns']);right=to_trace(clock,stop['monotonic_ns'])
    assert right>left and start['pid']==stop['pid']
    pid=start['pid'];selected={k:clips([r for r in rows if r.get('processId')==pid],left,right) for k,rows in all_rows.items()}
    gpu=merge([p for k in ('kernel','copy','memset','graph') for p in intervals(selected[k])])
    api=intervals(selected['api'])
    gaps=[];cursor=left
    for a,b in gpu+[(right,right)]:
        if a>cursor:
            active=clips(selected['api'],cursor,a)
            gaps.append(dict(start_relative_ms=(cursor-left)/1e6,duration_ms=(a-cursor)/1e6,
                api_union_ms=measure(intervals(active))/1e6,top_api=aggregate(active,lambda x:x['name'])[:5]))
        cursor=max(cursor,b)
    categories=aggregate(selected['kernel'],lambda x:classify(x['name'],x.get('grid'),helper))
    api_correlation={}
    for row in selected['api']:
        key=(row.get('processId'),row.get('correlationId'))
        api_correlation.setdefault(key,[]).append(row)
    linked=unlinked=ambiguous=0;latencies=[]
    for kind in ('kernel','copy','graph'):
        for row in selected[kind]:
            candidates=api_correlation.get((pid,row.get('correlationId')),[])
            if len(candidates)==1:
                linked+=1
                latencies.append(dict(kind=kind,name=row['name'],api=candidates[0]['name'],
                    device_start_minus_api_start_ms=(row['ts']-candidates[0]['ts'])/1e6))
            elif not candidates:unlinked+=1
            else:ambiguous+=1
    return dict(phase=start['phase'],window_valid=stop.get('valid') is True,pid=pid,
        trace_start_ns=left,trace_end_ns=right,span_ms=(right-left)/1e6,rows=stop.get('rows'),
        gpu_observed_union_ms=measure(gpu)/1e6,gpu_uncovered_ms=((right-left)-measure(gpu))/1e6,
        api_union_ms=measure(api)/1e6,api_overlapping_gpu_union_ms=measure(overlap(api,gpu))/1e6,
        sources={kind:dict(calls=len(rows),sum_ms=sum(r['end']-r['ts'] for r in rows)/1e6,
                    union_ms=measure(intervals(rows))/1e6,by_name=aggregate(rows,lambda x:x['name'])) for kind,rows in selected.items()},
        kernel_categories=categories,copy_directions=aggregate(selected['copy'],lambda x:str(x.get('srcKind'))+' -> '+str(x.get('dstKind'))),
        largest_observed_gpu_gaps=sorted(gaps,key=lambda x:-x['duration_ms'])[:12],
        correlation=dict(unique_links=linked,unlinked=unlinked,ambiguous=ambiguous,
                         largest_observed_launch_offsets=sorted(latencies,key=lambda x:-x['device_start_minus_api_start_ms'])[:12]),
        step_attribution=per_step(selected,stop['rows'],clock,helper),
        graph_internal_breakdown='unproven',gpu_gap_is_cpu_bottleneck=False,
        boundary_sync_perturbs_first_two_steps=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('run',type=Path);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run=args.run.resolve(strict=True);out=args.output.resolve()
    assert not out.exists() and not out.is_relative_to(run),'输出须为原件目录外新文件'
    trace=run/'native-trace.sqlite';events_path=run/'hotspot-events.jsonl'
    reader=load(HERE/'summarize_native_trace.py',READER_SHA,'hotspot_existing_reader')
    helper=load(HERE/'analyze_mixed_native.py',CLASSIFIER_SHA,'hotspot_existing_category')
    events=[json.loads(x) for x in events_path.read_text(encoding='utf-8').splitlines() if x.strip()]
    with sqlite3.connect(trace.as_uri()+'?mode=ro&immutable=1',uri=True) as database:
        database.execute('PRAGMA query_only=ON');schema=reader.schema_of(database)
        rows={};sources={}
        for kind,table in TABLES.items():rows[kind],sources[kind]=read_rows(database,reader,schema,table)
        clock=clocks(database,schema)
        windows=[];errors=[]
        for phase in ('mixed','decode'):
            starts=[x for x in events if x.get('event')=='window_start' and x.get('phase')==phase]
            stops=[x for x in events if x.get('event')=='window_stop' and x.get('phase')==phase]
            if len(starts)==len(stops)==1 and clock['valid']:
                try:windows.append(summarize_window(starts[0],stops[0],clock,rows,helper))
                except Exception as error:errors.append(dict(phase=phase,error=repr(error)))
            else:errors.append(dict(phase=phase,starts=len(starts),stops=len(stops),clock_valid=clock['valid']))
    result=dict(kind='当前main526短窗GPU/API诊断；不是性能成绩',inputs={p.name:sha(p) for p in (trace,events_path,run/'result.json',run/'model-path/evidence.json') if p.exists()},
        reader_sha256=READER_SHA,classifier_sha256=CLASSIFIER_SHA,clock=clock,sources=sources,windows=windows,errors=errors,
        limitations=['kernel与graph/搬运活动求并集，不将重叠时长重复相加；各类别并集仍可彼此重叠。',
                    'API与GPU在同trace时钟内相关；Python时间只经本次clock_snapshot映射。',
                    'FULL内部kernel归属/覆盖未知；可见图外kernel比例不能当整图内部比例。',
                    'GPU未覆盖区间与同期API仅是定位线索；不能自动称CPU瓶颈。',
                    '边界sync、观察元数据与profiler增加开销；前两步不用于预测关闭profiler后的收益。'])
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as stream:json.dump(result,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps(dict(output=str(out),clock_valid=clock['valid'],errors=errors,windows=[{k:w[k] for k in ('phase','window_valid','span_ms','gpu_observed_union_ms','api_union_ms','kernel_categories')} for w in windows]),ensure_ascii=False))
if __name__=='__main__':main()
