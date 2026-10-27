"""明确只调用原run_once两次；不修改benchmark文件或RUNS/SKIP_FIRST。"""
import csv,hashlib,importlib.util,json,math
from datetime import datetime
from pathlib import Path
BENCHMARK=Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py')
BENCHMARK_SHA='0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
CASE=(4096,1024,64,256)

def load_original(path=BENCHMARK):
    path=Path(path)
    if hashlib.sha256(path.read_bytes()).hexdigest()!=BENCHMARK_SHA:raise ValueError('原benchmark源变化')
    spec=importlib.util.spec_from_file_location('unchanged_official_benchmark_two_calls',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    if (module.RUNS,module.SKIP_FIRST)!=(4,1):raise ValueError('原benchmark常量变化')
    return module

def execute(original,args,directory=Path('.')):
    if args.test_cases!=[CASE] or args.enable_all:raise ValueError('仅原4K case')
    common_args=original.build_common_args(args.model,args.port,args.served_model_name)
    output=Path(directory)/'benchmark_results';output.mkdir(exist_ok=True)
    if list(output.iterdir()):raise ValueError('诊断结果目录必须为空，不能覆盖旧记录')
    stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
    raw=output/('raw_runs_diagnostic_'+stamp+'.csv');record=output/('diagnostic_'+stamp+'.json')
    evidence=dict(protocol='two-round-diagnostic',official_qualified=False,official_four_round_complete=False,
        original_benchmark_sha256=BENCHMARK_SHA,original_source_RUNS=original.RUNS,original_source_SKIP_FIRST=original.SKIP_FIRST,
        actual_max_calls=2,completed_calls=0,case=list(CASE),common_args=common_args,calls=[],complete=False,
        limitation='两次原run_once/原参数，无四轮summary；第1轮冷、第2轮首暖，不能估计稳定均值。')
    try:
        for run_id in (1,2):
            # 不调用run_test_case四轮外层，不修改原函数/源码/常量或服务参数。
            metrics=original.run_once(CASE,run_id,common_args)
            row=original.format_result(CASE,metrics,include_successful_requests=True)
            row['Run Status']='SUCCESS' if metrics.get('successful_requests')==CASE[3] else 'FAILED'
            original.append_csv(row,str(raw),original.RAW_CSV_COLUMNS)
            evidence['calls'].append(dict(run_id=run_id,metrics=metrics));evidence['completed_calls']+=1
            if (row['Run Status']!='SUCCESS' or metrics.get('total_input_tokens')!=CASE[0]*CASE[3]
                or metrics.get('total_output_tokens')!=CASE[1]*CASE[3]):raise ValueError('原benchmark请求/输入输出数量失败')
        evidence['complete']=True
    finally:record.write_text(json.dumps(evidence,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    return 0

def validate_outputs(run,original=None):
    original=load_original() if original is None else original
    output=Path(run)/'benchmark_results';files=list(output.glob('raw_runs_diagnostic_*.csv'));records=list(output.glob('diagnostic_*.json'))
    if len(files)!=1 or len(records)!=1 or list(output.glob('summary_*.csv')):raise ValueError('两轮诊断不应生成四轮summary')
    with files[0].open(newline='',encoding='utf-8-sig') as handle:rows=list(csv.DictReader(handle))
    record=json.loads(records[0].read_bytes())
    if (len(rows)!=2 or record.get('protocol')!='two-round-diagnostic' or record.get('completed_calls')!=2
        or record.get('complete') is not True or record.get('official_qualified') is not False):raise ValueError('诊断两调用未完整')
    for row in rows:
        case=tuple(int(row[k]) for k in ('Prefill','Decode','Conc','Num Prompts'))
        if (case!=CASE or row['Run Status']!='SUCCESS' or float(row['Successful Requests'])!=256
            or float(row['Total Input Tokens'])!=4096*256 or float(row['Total Output Tokens'])!=1024*256):raise ValueError('两轮请求/长度错误')
        for key in original.RAW_CSV_COLUMNS[6:]:
            value=float(row[key])
            if not math.isfinite(value) or value<=0:raise ValueError('诊断指标非有效正数：'+key)
    return dict(complete=True,diagnostic_complete=True,official_complete=False,protocol='two-round-diagnostic',raw_rows=2,
        summary_rows=0,runs_per_case=2,skip_first=1,successful_requests=512,cold_toks=float(rows[0]['Total tok/s']),
        first_warm_toks=float(rows[1]['Total tok/s']),summary_means_verified=False,summary_rewritten=False,
        sha256={str(p.relative_to(run)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files+records},
        limitation='完成的是两轮诊断，原外围driver的benchmark_completed只表示这两调用完成；非四轮官方资格/稳定均值。')

def main():
    original=load_original();args=original.parse_args()
    return execute(original,args)
if __name__=='__main__':raise SystemExit(main())
