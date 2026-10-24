"""只摘录已封存并导入的144620官方终态；不重算均值、判卷或运行模型。"""
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath

RUN = '20261023T144620Z-current-main-compute-order-official'
ACCURACY = '20261023T142019Z-current-main-compute-order'
TREE = '5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
CASES = ((4096, 1024, 64, 256), (16384, 1024, 64, 128))
CASE_KEYS = ('Prefill', 'Decode', 'Conc', 'Num Prompts')
METRICS = ('Total tok/s', 'Output tok/s', 'Mean TTFT (ms)',
           'Mean TPOT (ms)', 'Benchmark Duration (s)')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def project_root():
    roots = [p for p in Path(__file__).resolve().parents
             if (p / 'AGENTS.md').is_file() and (p / 'experiments/registry.csv').is_file()]
    require(len(roots) == 1, '项目根不唯一')
    root = roots[0]
    return Path('\\\\?\\' + str(root)) if os.name == 'nt' and not str(root).startswith('\\\\?\\') else root


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sealed_read(path, parent, seal):
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == seal['files'].get(path.relative_to(parent).as_posix()),
            '摘要所用原件与已有seal不一致：' + path.name)
    return json.loads(raw)


def summarize(root, receipt_path):
    parent = root / 'experiments/official'
    run, control = parent / RUN, parent / (RUN + '-control')
    seal = read(control / 'evidence-seal.json')
    receipt = read(receipt_path)
    require(receipt['run'] == RUN and receipt['exit_code'] == '0'
            and receipt['sealed_files'] == len(seal['files'])
            and receipt['added'] + receipt['matched_existing'] == len(seal['files']) + 1,
            '缺少本轮完整导入成功回执')
    load = lambda path: sealed_read(path, parent, seal)
    result, manifest = load(run / 'result.json'), load(run / 'manifest.json')
    post, sealed_review = load(run / 'postflight-full.json'), load(run / 'official-seal-review.json')
    coverage, purpose = load(run / 'method-coverage.json'), load(control / 'purpose.json')
    validation = result['validation']
    require((run / 'exit-code').read_text().strip() == '0' and result['exit_code'] == 0
            and result['status'] == 'official_benchmark_completed' and result['benchmark_completed'] is True
            and result['benchmark_exit_code'] == 0 and result['cleanup_errors'] == [], '原任务尚未完整结束')
    require(sealed_review['status'] == 'sealed_existing_completed_official'
            and sealed_review['validation_reexecuted'] is False
            and validation == sealed_review['original_validation'] == seal['original_validation'] == receipt['original_validation']
            and coverage == receipt['method_coverage'], '原验证/封存/导入身份不一致')
    require(all(validation.get(k) is True for k in ('complete', 'retained_raw_metrics_checked', 'summary_means_verified'))
            and validation['summary_rewritten'] is False
            and (validation['raw_rows'], validation['summary_rows'], validation['runs_per_case'], validation['skip_first']) == (8, 2, 4, 1),
            '原八行/两摘要/第2至4轮验证未完整')
    require([v['case'] for v in validation['verified_cases']] == [list(c) for c in CASES]
            and all(v['retained_runs'] == [2, 3, 4] for v in validation['verified_cases']), '不是原两负载')
    require(manifest['profiler'] is False and manifest['smoke_requests'] == 0
            and manifest['repetitions'] == {'RUNS': 4, 'SKIP_FIRST': 1}
            and purpose['source_count'] == post['source_count'] == coverage['source_count'] == 446
            and purpose['tree'] == TREE and purpose['source'] == manifest['source_dir'], '本轮源码/测法身份不符')
    require(not post['source_failures'] and not post['archived_source_failures']
            and post['query'].strip() == '68, 0' and all(post['ports_closed'].values())
            and all(s is None or '\nState:\tZ ' in s for s in post['owned_process_status'].values()), '清理或源码后态未通过')
    csv_rows = {}
    for relative, digest in validation['sha256'].items():
        path = PurePosixPath(relative)
        require(not path.is_absolute() and '..' not in path.parts and len(path.parts) == 2
                and path.parts[0] == 'benchmark_results' and path.suffix == '.csv', '未知CSV路径')
        raw = run.joinpath(*path.parts).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == digest == seal['files'].get(RUN + '/' + relative), '原CSV验证字节变化')
        kind = 'raw' if path.name.startswith('raw_runs_') else 'summary' if path.name.startswith('summary_') else None
        require(kind is not None and kind not in csv_rows, 'CSV种类不唯一')
        csv_rows[kind] = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
    require(set(csv_rows) == {'raw', 'summary'} and len(csv_rows['raw']) == 8 and len(csv_rows['summary']) == 2, 'CSV缺行')
    key = lambda row: tuple(int(row[k]) for k in CASE_KEYS)
    require([key(row) for row in csv_rows['summary']] == list(CASES)
            and all(key(row) in CASES for row in csv_rows['raw']), 'CSV负载不符')
    cases = []
    for summary in csv_rows['summary']:
        case = key(summary)
        rows = [row for row in csv_rows['raw'] if key(row) == case]
        require(len(rows) == 4 and all(row['Run Status'] == 'SUCCESS'
                and float(row['Successful Requests']) == case[3] for row in rows), '八轮并非全部成功')
        cases.append(dict(负载=dict(zip(CASE_KEYS, case)), 保留轮次=[2, 3, 4],
            原summary数值={k: float(summary[k]) for k in METRICS},
            原始四轮=[dict(轮次=i, 是否warmup=i == 1, 状态=row['Run Status'],
                成功请求=int(float(row['Successful Requests'])), 数值={k: float(row[k]) for k in METRICS})
                for i, row in enumerate(rows, 1)]))
    db_keys = ('table_count', 'row_count', 'snapshot_sha256', 'schema_sha256', 'logical_content_sha256')
    database = {}
    for phase in ('before', 'after'):
        item = load(run / ('database-' + phase) / 'manifest.json')
        require(item['status'] == 'complete', 'DB快照不完整')
        database[phase] = {k: item[k] for k in db_keys}
    accuracy_parent = root / 'experiments/accuracy'
    accuracy_run = accuracy_parent / ACCURACY
    accuracy_seal_path = accuracy_parent / (ACCURACY + '-control/evidence-seal.json')
    accuracy_seal = read(accuracy_seal_path)
    reference = load(control / 'accuracy-reference.json')
    require(reference == purpose['accuracy_reference'] == sealed_review['accuracy']
            and reference['run'] == ACCURACY and reference['tree'] == TREE and reference['source_count'] == 446
            and reference['seal_sha256'] == hashlib.sha256(accuracy_seal_path.read_bytes()).hexdigest(), '准确率附证身份不符')
    accuracy = sealed_read(accuracy_run / 'accuracy-review.json', accuracy_parent, accuracy_seal)
    accuracy_coverage = sealed_read(accuracy_run / 'method-coverage.json', accuracy_parent, accuracy_seal)
    require(reference['report_sha256'] == hashlib.sha256((accuracy_run / 'accuracy-review.json').read_bytes()).hexdigest()
            and accuracy['validity'] == 'valid' and accuracy['samples'] == accuracy['expected_samples'] == 105
            and (accuracy['correct'], accuracy['accuracy_gate']) == (reference['correct'], reference['accuracy_gate']), '原完整105题附证不完整')
    return dict(状态='已完成官方绝对结果摘要', run_id=RUN, 平台='Iluvatar BI-V150', gain=None,
        源码=dict(source=manifest['source_dir'], files=446, tree=TREE, base_commit=purpose['base_commit']),
        完成=dict(status=result['status'], exit_code=result['exit_code'], raw_rows=8, summary_rows=2,
            benchmark_started_utc=result['benchmark_started_utc'], benchmark_finished_utc=result['benchmark_finished_utc'],
            cleanup_errors=result['cleanup_errors'], gpu=post['query'].strip(), ports_closed=post['ports_closed']),
        官方两负载=cases, 方法覆盖=coverage,
        准确率=dict(run_id=ACCURACY, 原报告={k: accuracy[k] for k in ('correct', 'samples', 'exact_accuracy', 'accuracy_gate')},
            诊断=accuracy['diagnostics'], 方法覆盖=accuracy_coverage,
            限制='完整105题与P覆盖分别记录；P零命中时不能据完整评测声称新P分支完整准确率通过'),
        数据库=database, DB前后相同=database['before'] == database['after'],
        验证复用=dict(original_validation=validation, summary_recomputed=False, benchmark_or_accuracy_rerun=False,
            importer_receipt=str(receipt_path), original_tgz_sha256=receipt['original_tgz_sha256'], sealed_files=receipt['sealed_files']),
        原件=dict(run='experiments/official/' + RUN, result='experiments/official/' + RUN + '/result.json',
            csv=['experiments/official/' + RUN + '/' + p for p in validation['sha256']],
            accuracy='experiments/accuracy/' + ACCURACY + '/accuracy-review.json'),
        限制=['直接引用原第2至4轮summary；未重算均值、评分或重复完整文件验收。',
            '140324/141159短pair KV521840/521936不同，gain=null；本轮单臂不与旧423或队友PR16计算收益。',
            '方法首命中不代表全程或每个请求；BI-V150结果不能外推C500。'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--import-receipt', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = project_root()
    output = args.output if args.output.is_absolute() else root / args.output
    receipt = args.import_receipt if args.import_receipt.is_absolute() else root / args.import_receipt
    if output.exists():
        raise FileExistsError('保留已有摘要，拒绝覆盖：' + str(output))
    try:
        summary = summarize(root, receipt)
    except FileNotFoundError as error:
        print(json.dumps(dict(status='pending', 原因='原件或完整导入回执尚未齐，不写摘要', missing=str(error.filename)), ensure_ascii=False))
        return
    with output.open('x', encoding='utf-8') as stream:
        json.dump(summary, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(status='written', output=str(output), run_id=RUN, gain=None), ensure_ascii=False))


if __name__ == '__main__':
    main()
