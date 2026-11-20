"""只接受本次控制闭合后启动；每档仅首暖筛，正后跑满，异常停止。"""
import argparse
import csv
import datetime
import io
import json
import math
import os
from pathlib import Path
import select
import signal
import subprocess
import sys

import baseline_reference

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/experiments/minicpm-s2')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')

def first_round_stack(log_path):
    import activation_evidence
    import fixed_activation
    stack=activation_evidence.stack_evidence(log_path);fixed=fixed_activation.capture(log_path)
    return dict(valid=bool(stack['valid'] and fixed['valid']),stack=stack,fixed_address=fixed,
        scope='首轮后一次只读首次启用检查；完整FX/provider仍由原posthoc负责')

def complete_csv_snapshot(path):
    """benchmark仍在追加；未结束末行或列尚未齐时留到下一次快照。"""
    data=path.read_bytes()
    if not data or not data.endswith(b'\n'):return None
    rows=list(csv.DictReader(io.StringIO(data.decode('utf-8-sig'))))
    if any(None in row or any(value is None for value in row.values()) for row in rows):return None
    return rows

def new_row_decision(rows,seen,reference):
    """仅解析已落CSV；返回错误或各档第2轮首暖，后续暖轮不筛停。"""
    counts={4096:0,16384:0}
    for index,row in enumerate(rows):
        size=int(row['Prefill']);round_number=counts[size];counts[size]+=1
        if index<seen:continue
        expected=(size,1024,64,256 if size==4096 else 128)
        case=tuple(int(row[k]) for k in ('Prefill','Decode','Conc','Num Prompts'))
        if (case!=expected or row.get('Run Status')!='SUCCESS'
                or float(row['Successful Requests'])!=expected[3]):
            return dict(kind='runtime_error',reason='本轮原CSV状态或请求数异常，立即停止并保留原件',prefill=size,round=round_number+1)
        if round_number!=1:continue
        value=float(row['Total tok/s']);base=reference[size]
        if not math.isfinite(value) or not value>0:return dict(kind='runtime_error',reason='首暖吞吐非有效正数',prefill=size,round=2)
        if value<base:
            return dict(kind='performance',reason='本档第2轮首暖低于本次main594同档首暖，停止后续；不是完整官方成绩',
                prefill=size,round=2,candidate=value,baseline=base,delta_percent=(value/base-1)*100)
    return None

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path);parser.add_argument('label')
    parser.add_argument('--prefill',type=int,choices=(4096,16384),required=True)
    args=parser.parse_args();source=args.source;label=args.label
    # 未完成即退出；不预排队、不等设备，不与控制组重叠。
    baseline=baseline_reference.capture()
    import qualification as q
    q.assets()
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    log=HERE/('official-owner-'+stamp+'.log')
    command=['/usr/local/bin/python',str(HERE/'official_owner.py'),'--performance-control',str(ROOT/'official/20261024T161030Z-main0bf9-main-official-four-rounds-control'),'--source-dir',str(source),'--prefill',str(args.prefill)]
    with log.open('x') as out:owner=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
    receipt=dict(supervisor_pid=os.getpid(),owner_pid=owner.pid,label=label,log=str(log),command=command,
        started_utc=stamp,prefill=args.prefill,baseline=baseline,stop_policy='每档仅第2轮首暖筛；正首暖后跑满该档四轮，不因后续波动早停；错误立即停止')
    save(HERE/'supervisor-launch.json',receipt);print(json.dumps(receipt),flush=True)
    fd=os.pidfd_open(owner.pid);poll=select.poll();poll.register(fd,select.POLLIN)
    state=None;seen=0;stopped=False;stack_checked=False;server_position=0;server_pending=''
    try:
        while owner.poll() is None:
            if state is None:
                for line in log.read_text(errors='replace').splitlines():
                    try:value=json.loads(line)
                    except (ValueError,TypeError):continue
                    if isinstance(value,dict) and value.get('owner_pid')==owner.pid and 'control' in value:
                        state=value;receipt.update(run=state['run'],control=state['control']);save(HERE/'supervisor-launch.json',receipt);break
            if state is not None and not stopped:
                server_log=Path(state['run'])/'server.log'
                if server_log.exists():
                    with server_log.open(errors='replace') as server:
                        server.seek(server_position);server_pending+=server.read();server_position=server.tell()
                    lines=server_pending.split('\n');server_pending=lines.pop()
                    rejected=next((line for line in lines if 'BIV150_COMPUTE_ORDER_SCOPE_REJECTED ' in line),None)
                    if rejected:
                        receipt['qualification_stop']=dict(reason='原compute-order明确拒绝，对照无效',raw_marker=rejected)
                files=sorted((Path(state['run'])/'benchmark_results').glob('raw_runs_*.csv'))
                rows=[]
                if files:
                    rows=complete_csv_snapshot(files[-1])
                if rows and rows[0].get('Run Status')=='SUCCESS' and not stack_checked and 'qualification_stop' not in receipt:
                    evidence=first_round_stack(server_log);save(Path(state['control'])/'first-round-stack.json',evidence);stack_checked=True
                    if not evidence['valid']:receipt['qualification_stop']=dict(reason='首轮后新旧优化启用回执未闭合，不作净收益对照')
                decision=new_row_decision(rows,seen,baseline['first_warm']) if rows is not None else None
                if decision:
                    decision.update(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),completed_csv_rows=len(rows),owner_pid=owner.pid)
                    key='stop_decision' if decision['kind']=='performance' else 'runtime_stop'
                    receipt[key]=decision;save(Path(state['control'])/('performance-stop-decision.json' if key=='stop_decision' else 'runtime-stop-decision.json'),decision)
                if rows is not None:seen=len(rows)
                if any(key in receipt for key in ('qualification_stop','runtime_stop','stop_decision')):
                    if 'qualification_stop' in receipt:save(Path(state['control'])/'qualification-stop-decision.json',receipt['qualification_stop'])
                    save(HERE/'supervisor-launch.json',receipt);os.kill(owner.pid,signal.SIGTERM);stopped=True
            if poll.poll(5000):break
    except BaseException as error:
        receipt['supervisor_error']=repr(error)
    finally:
        # 新解析异常也交原owner清理，不能留下占卡任务。
        if owner.poll() is None:os.kill(owner.pid,signal.SIGTERM)
        receipt.update(owner_exit_code=owner.wait(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
        if state is not None:
            final=json.loads((Path(state['control'])/'state.json').read_text())
            receipt['final']={k:final.get(k) for k in ['completed','error','cleanup_error','database_restored','source_unchanged','native_unchanged','finished_utc']}
        save(HERE/'supervisor-final.json',receipt);os.close(fd)
    print(json.dumps(receipt,ensure_ascii=False),flush=True)
    if any(receipt.get(key) for key in ('supervisor_error','qualification_stop','runtime_stop')):return 1
    final=receipt.get('final',{})
    if final.get('cleanup_error') or any(final.get(key) is not True for key in ('database_restored','source_unchanged','native_unchanged')):return 1
    return 0 if receipt.get('stop_decision') or receipt['owner_exit_code']==0 else 1
if __name__=='__main__':raise SystemExit(main())
