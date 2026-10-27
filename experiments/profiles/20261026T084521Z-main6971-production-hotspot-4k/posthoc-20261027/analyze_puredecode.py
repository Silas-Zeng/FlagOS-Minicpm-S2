"""只读已封存main6971实际ixsys，唯一64步normal decode段；不跑GPU。"""
from pathlib import Path
from collections import defaultdict,Counter
from bisect import bisect_left
import csv,hashlib,json,sqlite3,statistics

P=Path(__file__).resolve().parent;ROOT=P.parents[2]
receipt=json.loads((P/'receipt.json').read_bytes());trace=P/'baseline.ixsys'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
assert trace.stat().st_size==receipt['bytes'] and sha(trace)==receipt['sha256']=='f96d26feceeaa2aaee32ff65c44b9d537065df2164b3f0f29385c406c561875a'
metadata_path=ROOT/'archive/hotspot-layout-20261026/batch-091200/profiles/20261026T084521Z-main6971-production-hotspot-4k/observations/worker-361793-window-1.json'
assert sha(metadata_path)=='81557093227361cb07cfc4d1a0c307172d1756e62e910e64494fb04e130860cb'
metadata=json.loads(metadata_path.read_bytes());chosen=metadata['scheduled_steps'][2603:2668]
assert [s['step'] for s in chosen]==list(range(2604,2669))
prompts={r['req_id']:r['prompt_token_count'] for s in metadata['scheduled_steps'] for r in s['new_requests']}
for s in chosen:
    assert s['total_num_scheduled_tokens']==64 and all(n==1 for n in s['num_scheduled_tokens'].values())
    cached={r['req_id']:r for r in s['cached_requests']}
    assert all(req in cached and (cached[req]['num_output_tokens']>0 or cached[req]['num_computed_tokens']>=prompts[req]) for req in s['num_scheduled_tokens'])
def merge(v):
    out=[]
    for a,b in sorted(v):
        if b<=a:continue
        if out and a<=out[-1][1]:out[-1]=(out[-1][0],max(out[-1][1],b))
        else:out.append((a,b))
    return out
def length(v):return sum(b-a for a,b in merge(v))
def overlap(v,a,b):return length([(max(l,a),min(r,b)) for l,r in v if l<b and r>a])
def stats(v):return dict(count=len(v),median_ms=statistics.median(v)/1e6,mean_ms=statistics.mean(v)/1e6,min_ms=min(v)/1e6,max_ms=max(v)/1e6)
c=sqlite3.connect(trace.resolve().as_uri()+'?mode=ro&immutable=1',uri=True);c.execute('PRAGMA query_only=ON')
names=dict(c.execute('SELECT id,name FROM function_name_map'))
snap=c.execute("SELECT ts,clock_value FROM clock_snapshot WHERE clock_name='MONOTONIC' ORDER BY ts").fetchall()
assert max(t-m for t,m in snap)-min(t-m for t,m in snap)<1000000
def clock(t):
    ts,m=min(snap,key=lambda x:abs(x[1]-t));return t+ts-m
all_exec=c.execute("SELECT ts,dur FROM cuda_nvtx WHERE process_id=361793 AND name='worker.execute_model' ORDER BY ts").fetchall()
assert len(all_exec)==4243
execs=[]
for s in chosen:
    t,d=all_exec[s['step']-1];assert t<=clock(s['monotonic_ns'])<=t+d
    execs.append((t,t+d))
left,right=execs[0][0],execs[-1][0]
gpu=[]
for kind,table in [('kernel','cuda_kernel_data'),('graph','cuda_graph_data'),('copy','cuda_memcpy_data'),('memset','cuda_memset_data')]:
    cols=[x[1] for x in c.execute('PRAGMA table_info('+table+')')]
    for values in c.execute('SELECT * FROM '+table+' WHERE ts<? AND ts+dur>? AND dur>0',(right,left)):
        r=dict(zip(cols,values));r.update(kind=kind,end=r['ts']+r['dur'],name=names.get(r.get('name_id'),str(r.get('name_id'))))
        gpu.append(r)
apis=[];cols=[x[1] for x in c.execute('PRAGMA table_info(cuda_api_data)')]
for values in c.execute('SELECT * FROM cuda_api_data WHERE processId=361793 AND ts<? AND ts+dur>? AND dur>0',(right,left-1000000000)):
    r=dict(zip(cols,values));r.update(end=r['ts']+r['dur'],name=names.get(r.get('name_id'),str(r.get('name_id'))));apis.append(r)
nvtx=c.execute('SELECT id,ts,dur,name,thread_id FROM cuda_nvtx WHERE process_id=361793 AND ts<? AND ts+dur>? AND dur>0',(right,left-1000000000)).fetchall()
assert not any(n.startswith('biv150_diag') and t+d>left for _,t,d,n,tid in nvtx),'选择段混入重复插桩'
api_by_corr=defaultdict(list)
for a in apis:api_by_corr[a['correlationId']].append(a)
busy=merge([(max(left,r['ts']),min(right,r['end'])) for r in gpu])
gaps=[];cursor=left
for a,b in busy+[(right,right)]:
    if a>cursor:
        nxt=[r for r in gpu if r['ts']==a]
        link=[x for r in nxt for x in api_by_corr[r['correlationId']]]
        phase=defaultdict(list)
        for _,t,d,n,tid in nvtx:
            if t<a and t+d>cursor:phase[n].append((max(t,cursor),min(t+d,a)))
        api=defaultdict(list)
        for r in apis:
            if r['ts']<a and r['end']>cursor:api[r['name']].append((max(r['ts'],cursor),min(r['end'],a)))
        gaps.append(dict(start_ns=cursor,end_ns=a,ms=(a-cursor)/1e6,
            next_names=[r['name'] for r in nxt],next_kinds=[r['kind'] for r in nxt],
            unique_next_api=len(link)==1,
            next_api=None if len(link)!=1 else dict(name=link[0]['name'],start_ns=link[0]['ts'],end_ns=link[0]['end'],
                enqueued_before_gap=link[0]['end']<=cursor,launch_start_after_previous_device_end_ms=(link[0]['ts']-cursor)/1e6),
            phases={n:length(v)/1e6 for n,v in phase.items()},apis={n:length(v)/1e6 for n,v in api.items()}))
    cursor=max(cursor,b)
rows=[]
for i in range(len(execs)-1):
    a,b=execs[i][0],execs[i+1][0]
    gs=[r for r in gpu if r['kind']=='graph' and a<=r['ts']<b]
    rows.append(dict(step=chosen[i]['step'],span_ms=(b-a)/1e6,device_activity_span_union_ms=overlap(busy,a,b)/1e6,
        gpu_uncovered_ms=((b-a)-overlap(busy,a,b))/1e6,graph_count=len(gs),graph_ms=sum(r['dur'] for r in gs)/1e6))
phase_gap=defaultdict(list);api_gap=defaultdict(list)
for g in gaps:
    for n,v in g['phases'].items():phase_gap[n].append(v)
    for n,v in g['apis'].items():api_gap[n].append(v)
graph_rows=[r for r in gpu if r['kind']=='graph']
next_api_classes=Counter(('unlinked_or_ambiguous' if not g['unique_next_api'] else 'already_enqueued' if g['next_api']['enqueued_before_gap'] else 'launch_after_gap_start') for g in gaps)
groups=defaultdict(list)
for r in gpu:groups[(r['kind'],r['name'])].append(r)
activities=[]
for (kind,name),rr in groups.items():
    duration=overlap([(r['ts'],r['end']) for r in rr],left,right)/1e6
    activities.append(dict(kind=kind,name=name,calls=len(rr),clipped_union_ms=duration,mean_full_ms=statistics.mean(r['dur'] for r in rr)/1e6))
activities.sort(key=lambda x:-x['clipped_union_ms'])
ids={r['id'] for r in gpu};flow_links={}
for out_id,in_id in c.execute('SELECT slice_out,slice_in FROM flow'):
    if in_id in ids:flow_links[in_id]=out_id
api_ids={r['id']:r for r in apis}
link_counts=Counter();stages=Counter();stage_activity=defaultdict(list)
for r in gpu:
    match=api_by_corr[r['correlationId']]
    if len(match)==1:
        api=match[0];link_counts['unique_correlation']+=1
        if flow_links.get(r['id'])==api['id']:link_counts['flow_confirms_same_API']+=1
        elif r['id'] not in flow_links:link_counts['flow_absent']+=1
        else:link_counts['flow_disagrees']+=1
        ss=[(d,n) for _,t,d,n,tid in nvtx if t<=api['ts']<t+d and n.startswith('gpu_model_runner:')]
        phase=min(ss)[1] if ss else 'no_specific_runner_scope'
    else:phase='no_unique_API';link_counts['no_unique_API']+=1
    stages[phase]+=1;stage_activity[phase].append((r['ts'],r['end']))
cycles=[];ordered=sorted(graph_rows,key=lambda r:r['ts'])
for prev,nxt in zip(ordered,ordered[1:]):
    a,b=prev['ts'],nxt['ts']
    if a<left or b>right:continue
    between=[r for r in gpu if r['kind']!='graph' and a<=r['ts']<b]
    cycles.append(dict(graph_correlation=prev['correlationId'],cycle_ms=(b-a)/1e6,graph_ms=prev['dur']/1e6,
        after_graph_until_next_ms=(b-prev['end'])/1e6,
        post_graph_GPU_covered_ms=overlap([(r['ts'],r['end']) for r in between],prev['end'],b)/1e6,
        post_graph_names=[r['name'] for r in sorted(between,key=lambda r:r['ts'])]))
res=dict(historical_source='main6971/native14f; not main241/main56 budget',trace_sha256=receipt['sha256'],trace_bytes=trace.stat().st_size,
    scheduler_metadata_sha256=sha(metadata_path),verified_puredecode_by_prompt_computed_and_output_counts=True,
    selected_steps=[chosen[0]['step'],chosen[-2]['step']],normal_steps=64,excluded_diag_samples=[162,258,642,1053],
    no_diag_NVTX_in_selected_segment=True,span_ms=(right-left)/1e6,device_activity_span_union_ms=length(busy)/1e6,
    gpu_uncovered_ms=((right-left)-length(busy))/1e6,gpu_uncovered_fraction=1-length(busy)/(right-left),
    all_device_process_ids=sorted({r['processId'] for r in gpu}),clock_offset_spread_ns=max(t-m for t,m in snap)-min(t-m for t,m in snap),
    graph_stats=stats([r['dur'] for r in graph_rows]),counts_by_kind=dict(Counter(r['kind'] for r in gpu)),
    gaps_by_next_launch_status=dict(next_api_classes),
    gaps_ms_by_next_launch_status={key:sum(g['ms'] for g in gaps if ('unlinked_or_ambiguous' if not g['unique_next_api'] else 'already_enqueued' if g['next_api']['enqueued_before_gap'] else 'launch_after_gap_start')==key) for key in next_api_classes},
    activity_rankings=activities,
    explicit_flow_checks=dict(link_counts),
    launch_phase_activity_union_ms={k:overlap(v,left,right)/1e6 for k,v in stage_activity.items()},
    graph_to_next_graph=dict(cycles=len(cycles),cycle=stats([x['cycle_ms']*1e6 for x in cycles]),
        graph=stats([x['graph_ms']*1e6 for x in cycles]),
        after_graph_until_next=stats([x['after_graph_until_next_ms']*1e6 for x in cycles]),
        post_graph_GPU_covered=stats([x['post_graph_GPU_covered_ms']*1e6 for x in cycles]),first_cycle=cycles[0]),
    gap_NVTX_overlap_ms=sorted([(n,sum(v)) for n,v in phase_gap.items()],key=lambda x:-x[1]),
    gap_API_overlap_ms=sorted([(n,sum(v)) for n,v in api_gap.items()],key=lambda x:-x[1]),
    top_gaps=sorted(gaps,key=lambda g:-g['ms'])[:20],
    limits=['profiler运行原件，不是关闭profiler后的净收益；未给优化成绩。','cuda_graph_data整段是device Graph span，不能证明图内每一瞬间计算或访存饱和；此分析只排除大额跨步host提交空洞。','NVTX父子范围重叠，phase/API overlap不能相加作CPU耗时。','Event/stream等待可能在等GPU；API期间与设备空隙相交不自动等于可删除CPU工作。'])
(P/'puredecode-summary.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (P/'puredecode-steps.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(P/'puredecode-gaps.json').write_text(json.dumps(gaps,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in res.items() if k not in ('top_gaps','gap_NVTX_overlap_ms','gap_API_overlap_ms','limits','activity_rankings')},ensure_ascii=False,indent=2))
print('ACTIVITY_TOP',json.dumps(activities[:10],ensure_ascii=False))
print('GAP_PHASE',res['gap_NVTX_overlap_ms'][:12]);print('GAP_API',res['gap_API_overlap_ms'][:12]);print('TOP_GAPS',json.dumps(res['top_gaps'][:3],ensure_ascii=False))
