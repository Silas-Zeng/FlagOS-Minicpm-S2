"""将已导入摘要登记一次；不重测、不重算官方均值。"""
import csv
import json
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'experiments/registry.csv').is_file())
RUN = '20261023T144620Z-current-main-compute-order-official'
summary = json.loads((ROOT/'analysis/compute-order-current-main-official.json').read_text(encoding='utf-8'))
manifest = json.loads((ROOT/'experiments/official'/RUN/'manifest.json').read_text(encoding='utf-8'))
assert summary['完成']['exit_code'] == 0 and summary['完成']['raw_rows'] == 8
assert summary['完成']['summary_rows'] == 2 and summary['方法覆盖']['actual_p_observed']
registry = ROOT/'experiments/registry.csv'
with registry.open(encoding='utf-8-sig', newline='') as stream:
    reader = csv.DictReader(stream)
    fields, rows = reader.fieldnames, list(reader)
assert RUN not in {row['run_id'] for row in rows}
item = dict.fromkeys(fields, '')
item.update(run_id=RUN, local_date='2026-10-23', utc_start=manifest['started_utc'],
    profile_id='compute_order', phase='current_main_official_throughput', device='Iluvatar BI-V150',
    vllm_commit=summary['源码']['base_commit'], flaggems_commit=manifest['flaggems_revision'],
    input_len='4096/16384', output_len='1024', concurrency='64', num_prompts='256/128 x4',
    profiler='false', status='official_complete_absolute_results_no_causal_gain', artifacts=f'experiments/official/{RUN}',
    conclusion='原官方两case各4轮全部SUCCESS，1536请求成功，原第2–4轮均值：4K5116.68、16K3436.04 total tok/s；TTFT4580.19/152082.85ms，TPOT57.74/130.38ms。446源码tree5c77与103/105准确率相同；官方P实际N62/M2048/outside59，准确率评测P0，不能证明P分支完整精度。单臂gain=null，不与旧版本或队友PR16归因比较。725原件逐项核、726导入，DB567/20986→569/21053；68MiB/0、9031双栈关闭、服务/Engine/benchmark退出。保留Draft方法候选，不自动集成；详analysis/compute-order-current-main-official.json。')
with registry.open('a', encoding='utf-8', newline='') as stream:
    csv.DictWriter(stream, fieldnames=fields, lineterminator='\n').writerow(item)
print(json.dumps(dict(registry_rows=len(rows)+1, unique_runs=len({row['run_id'] for row in rows}|{RUN})), ensure_ascii=False))
