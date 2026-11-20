"""外层观察原CSV执行负候选早停；不修改官方driver、benchmark和参数。"""
import csv
import datetime
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/experiments/minicpm-s2')
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
    source=Path(sys.argv[1]);label=sys.argv[2]
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    log=HERE/('official-owner-'+stamp+'.log')
    command=['/usr/local/bin/python',str(HERE/'official_owner.py'),'--performance-control',str(ROOT/'official/20261024T161030Z-main0bf9-main-official-four-rounds-control'),'--source-dir',str(source)]
    with log.open('x') as out:owner=subprocess.Popen(command,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True)
    receipt=dict(supervisor_pid=os.getpid(),owner_pid=owner.pid,label=label,log=str(log),command=command,started_utc=stamp,baseline='PR60 official 20261026T013104Z; main6971 same tree',stop_policy='每档仅第2轮首暖筛选；低于同轮基线可停；首暖非负则完成该档4轮，后续单轮波动不早停')
    save(HERE/'supervisor-launch.json',receipt);print(json.dumps(receipt),flush=True)
    fd=os.pidfd_open(owner.pid);poll=select.poll();poll.register(fd,select.POLLIN)
    state=None;seen=0;stopped=False
    # 固定已有原始轮次，不选最低基线，不重复测基线。
    reference={4096:[4913.84,5533.03,5677.28,5760.00],16384:[3806.25,4119.46,4119.07,4119.19]}
    while owner.poll() is None:
        if state is None:
            for line in log.read_text(errors='replace').splitlines():
                try:value=json.loads(line)
                except (ValueError,TypeError):continue
                if isinstance(value,dict) and value.get('owner_pid')==owner.pid and 'control' in value:
                    state=value;receipt.update(run=state['run'],control=state['control']);save(HERE/'supervisor-launch.json',receipt);break
        if state is not None and not stopped:
            files=sorted((Path(state['run'])/'benchmark_results').glob('raw_runs_*.csv'))
            rows=list(csv.DictReader(files[-1].open())) if files else []
            if len(rows)>seen:
                counts={4096:0,16384:0}
                for index,row in enumerate(rows):
                    size=int(row['Prefill']);round_number=counts[size];counts[size]+=1
                    if index<seen or round_number!=1 or row.get('Run Status')!='SUCCESS':continue
                    value=float(row['Total tok/s']);base=reference[size][round_number]
                    if value<base:
                        decision=dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reason='本档第2轮首暖低于可比基线，按当前用户规则停止；不是完整官方成绩',prefill=size,round=round_number+1,candidate=value,baseline=base,delta_percent=(value/base-1)*100,completed_csv_rows=len(rows),owner_pid=owner.pid)
                        save(Path(state['control'])/'performance-stop-decision.json',decision)
                        receipt['stop_decision']=decision;save(HERE/'supervisor-launch.json',receipt)
                        os.kill(owner.pid,signal.SIGTERM);stopped=True;break
                seen=len(rows)
        if poll.poll(5000):break
    receipt.update(owner_exit_code=owner.wait(),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    if state is not None:
        final=json.loads((Path(state['control'])/'state.json').read_text())
        receipt['final']={k:final.get(k) for k in ['completed','error','cleanup_error','database_restored','source_unchanged','native_unchanged','finished_utc']}
    save(HERE/'supervisor-final.json',receipt);os.close(fd)
    print(json.dumps(receipt,ensure_ascii=False),flush=True)
    return 0 if receipt.get('stop_decision') or receipt['owner_exit_code']==0 else 1
if __name__=='__main__':raise SystemExit(main())
