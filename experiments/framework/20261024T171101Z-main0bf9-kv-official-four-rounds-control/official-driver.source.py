#!/usr/bin/env python3
"""One owned official two-case throughput run; unchanged script and arguments.

Uses the reviewed accuracy driver's ownership/evidence helpers. No profiler,
smoke request, custom load, benchmark rewrite, or replacement averaging.
"""

from __future__ import annotations

import argparse
import ast
import csv
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
from statistics import mean
import subprocess
import traceback

import run_accuracy_gate as common


ROOT = common.ROOT
SERVER = common.SERVER
BENCHMARK = Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py')
BENCHMARK_SHA256 = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
TEST_CASES = '[[4096,1024,64,256],[16384,1024,64,128]]'
OUTER_TIMEOUT = 21600


def benchmark_command():
    return ['python3', BENCHMARK.as_posix(), '--model', '/workspace/MiniCPM5-2B',
            '--served-model-name', 'minicpm', '--port', '9031', '--test-cases', TEST_CASES]


def check_benchmark_source():
    if common.sha256(BENCHMARK) != BENCHMARK_SHA256:
        raise RuntimeError('official benchmark exact source hash mismatch')
    tree = ast.parse(BENCHMARK.read_bytes(), filename=str(BENCHMARK))
    constants = {node.targets[0].id: ast.literal_eval(node.value)
                 for node in tree.body if isinstance(node, ast.Assign)
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id in ('RUNS', 'SKIP_FIRST')}
    if constants != {'RUNS': 4, 'SKIP_FIRST': 1}:
        raise RuntimeError('unexpected official repetition contract: ' + repr(constants))
    return constants


def validate_outputs(run):
    """Verify original retained rows and means; never rewrite official CSVs."""
    output = run / 'benchmark_results'
    raw_files, summaries = sorted(output.glob('raw_runs_*.csv')), sorted(output.glob('summary_*.csv'))
    if len(raw_files) != 1 or len(summaries) != 1:
        raise RuntimeError('expected one raw CSV and one official summary CSV')
    if raw_files[0].name.removeprefix('raw_runs_') != summaries[0].name.removeprefix('summary_'):
        raise RuntimeError('raw and summary CSV timestamps differ')
    with raw_files[0].open(newline='', encoding='utf-8-sig') as handle:
        raw = list(csv.DictReader(handle))
    with summaries[0].open(newline='', encoding='utf-8-sig') as handle:
        summary = list(csv.DictReader(handle))
    cases = [tuple(case) for case in json.loads(TEST_CASES)]

    def case_of(row):
        return tuple(int(row[key]) for key in ['Prefill', 'Decode', 'Conc', 'Num Prompts'])

    if [case_of(row) for row in raw] != [case for case in cases for _ in range(4)]:
        raise RuntimeError('raw CSV does not contain the original two cases x four runs in order')
    if [case_of(row) for row in summary] != cases:
        raise RuntimeError('official summary missing or has unexpected cases')
    failures = []
    for index, row in enumerate(raw):
        if (row['Run Status'] != 'SUCCESS' or
                float(row['Successful Requests']) != case_of(row)[3]):
            failures.append({'case': list(case_of(row)), 'run': index % 4 + 1,
                             'status': row['Run Status'], 'successful_requests': row['Successful Requests']})
    # Keep the original positions even when warmup failed. Never filter rows
    # before applying SKIP_FIRST, or an extra retained run could be discarded.
    scored_failures = [failure for failure in failures if failure['run'] != 1]
    if scored_failures:
        raise RuntimeError('request failures in official retained repetitions: ' + repr(scored_failures))
    metric_columns = [
        'Benchmark Duration (s)', 'Total Input Tokens', 'Total Output Tokens',
        'Req/s', 'Output tok/s', 'Peak Output tok/s', 'Total tok/s',
        'Mean TTFT (ms)', 'Median TTFT (ms)', 'P99 TTFT (ms)',
        'Mean TPOT (ms)', 'Median TPOT (ms)', 'P99 TPOT (ms)',
        'Mean ITL (ms)', 'Median ITL (ms)', 'P99 ITL (ms)',
    ]

    def numeric(row, key, label):
        try:
            value = float(row[key])
        except (KeyError, TypeError, ValueError) as error:
            raise RuntimeError(f'{label}: missing/invalid {key}') from error
        if not math.isfinite(value) or value <= 0:
            raise RuntimeError(f'{label}: nonfinite/nonpositive {key}')
        return value

    def check_tokens(row, case, label):
        for key, expected in [('Total Input Tokens', case[0] * case[3]),
                              ('Total Output Tokens', case[1] * case[3])]:
            if numeric(row, key, label) != expected:
                raise RuntimeError(f'{label}: {key} must equal {expected}')

    verified_cases = []
    for case_index, case in enumerate(cases):
        # The official format writes parsed CLI floats to raw without rounding,
        # then round(mean(values), 2) to summary. Mirror only that verification.
        retained = raw[case_index * 4 + 1:case_index * 4 + 4]
        for run_number, row in enumerate(retained, 2):
            label = f'case {case} run {run_number}'
            check_tokens(row, case, label)
            for key in metric_columns:
                numeric(row, key, label)
        row = summary[case_index]
        label = f'case {case} official summary'
        check_tokens(row, case, label)
        for key in metric_columns:
            actual = numeric(row, key, label)
            expected = round(mean(float(item[key]) for item in retained), 2)
            if not math.isclose(actual, expected, rel_tol=0, abs_tol=1e-9):
                raise RuntimeError(f'{label}: {key}={actual} differs from '
                                   f'original runs 2-4 mean={expected}')
        verified_cases.append({'case': list(case), 'retained_runs': [2, 3, 4],
                               'expected_input_tokens_per_run': case[0] * case[3],
                               'expected_output_tokens_per_run': case[1] * case[3]})
    return {'complete': True, 'raw_rows': len(raw), 'summary_rows': len(summary),
            'runs_per_case': 4, 'skip_first': 1, 'warmup_failures': failures,
            'retained_raw_metrics_checked': True, 'verified_cases': verified_cases,
            'summary_means_verified': True, 'summary_rewritten': False,
            'sha256': {str(path.relative_to(run)): common.sha256(path) for path in
                       sorted(output.rglob('*')) if path.is_file()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path, help='new child directory of ROOT/official')
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--require-log-marker')
    parser.add_argument('--database', type=Path, required=True, help='actual existing SQLite tuning DB')
    args = parser.parse_args(argv)
    run, source, database = (args.run_dir.resolve(), args.source_dir.resolve(strict=True),
                              args.database.resolve(strict=True))
    if not run.is_relative_to(ROOT / 'official') or run == ROOT / 'official':
        raise ValueError('run must be a new child of ROOT/official')
    if not source.is_relative_to(ROOT / 'code') or not (source / 'vllm_fl/worker/model_runner.py').is_file():
        raise ValueError('source must be an isolated plugin under ROOT/code')
    if not database.is_file():
        raise ValueError('database must be an existing regular file')
    run.mkdir(parents=True, exist_ok=False)
    (run / 'started-at.txt').write_text(common.utc() + '\n')
    result = {'status': 'started', 'benchmark_completed': False, 'accuracy_gate': 'separate',
              'cleanup_errors': [], 'score': 'not computed by driver'}
    manifest = {'kind': 'unmodified official two-case throughput', 'started_utc': common.utc(),
                'source_dir': str(source), 'database': str(database),
                'server_command': SERVER, 'benchmark_command': benchmark_command(),
                'benchmark_cwd': str(run), 'profiler': False, 'smoke_requests': 0,
                'require_log_marker': args.require_log_marker,
                'outer_timeout_seconds': OUTER_TIMEOUT, 'cpu_before': common.cpu_state(),
                'python': platform.python_version()}
    lock = server = benchmark = monitor = None
    previous_handlers = {}
    database_before = False
    status = 1
    try:
        import fcntl
        lock = (ROOT / 'framework-device.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for signum in (signal.SIGTERM, signal.SIGINT):
            previous_handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, lambda number, frame: (_ for _ in ()).throw(
                KeyboardInterrupt('received signal ' + str(number))))
        manifest['preflight'] = common.preflight()
        manifest['repetitions'] = check_benchmark_source()
        env = common.child_environment(source)
        # Reuse the complete reviewed plugin/installed-source/model archive.
        # Its small accuracy dataset archive is provenance only, never executed.
        manifest['sha256'] = common.archive_sources(run, source)
        shutil.copyfile(Path(__file__), run / 'source/run_official_gate.py')
        shutil.copyfile(BENCHMARK, run / 'source/benchmark_throughput_serve.py')
        for name in ['run_official_gate.py', 'benchmark_throughput_serve.py']:
            manifest['sha256'][name] = common.sha256(run / 'source' / name)
        manifest['packages'] = {name: importlib.metadata.version(name) for name in
                                ['vllm', 'vllm-plugin-fl', 'torch', 'transformers', 'flag-gems', 'sqlalchemy']}
        match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]+)',
                          (common.SITE / 'triton/__init__.py').read_text(), re.MULTILINE)
        manifest['triton_source_version'] = match.group(1) if match else 'not found'
        for label, checkout in [('plugin', source), ('flaggems', Path('/workspace/FlagGems'))]:
            if (checkout / '.git').exists():
                manifest[label + '_revision'] = subprocess.check_output(
                    ['git', '-C', str(checkout), 'rev-parse', 'HEAD'], text=True).strip()
                manifest[label + '_status'] = subprocess.check_output(
                    ['git', '-C', str(checkout), 'status', '--short'], text=True)
        if (source / 'base-revision.txt').exists():
            manifest['plugin_base_revision'] = (source / 'base-revision.txt').read_text().strip()
        common.write_json(run / 'manifest.json', manifest)
        common.snapshot_database(run, database, 'before')
        database_before = True
        with (run / 'server.log').open('w') as log:
            server = subprocess.Popen(SERVER, cwd='/workspace', env=env, stdout=log,
                                      stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                      start_new_session=True)
        (run / 'server.pid').write_text(str(server.pid) + '\n')
        with (run / 'monitor.log').open('w') as log:
            monitor = subprocess.Popen(
                ['bash', str(run / 'source/monitor_gpu.sh'), str(server.pid), str(run / 'gpu.csv')],
                stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        common.wait_ready(server, args.require_log_marker, run)
        check_benchmark_source()
        common.write_json(run / 'benchmark-command.json', benchmark_command())
        result['benchmark_started_utc'] = common.utc()
        with (run / 'benchmark.log').open('w') as log:
            benchmark = subprocess.Popen(benchmark_command(), cwd=run, env=env, stdout=log,
                                         stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                         start_new_session=True)
        (run / 'benchmark.pid').write_text(str(benchmark.pid) + '\n')
        result['benchmark_exit_code'] = benchmark.wait(timeout=OUTER_TIMEOUT)
        result['benchmark_finished_utc'] = common.utc()
        if result['benchmark_exit_code'] != 0 or server.poll() is not None:
            raise RuntimeError('official benchmark failed or server exited')
        result['validation'] = validate_outputs(run)
        result.update(status='official_benchmark_completed', benchmark_completed=True)
        status = 0
    except BaseException as error:
        result.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    finally:
        for label, process in [('benchmark', benchmark), ('server', server), ('monitor', monitor)]:
            try:
                common.stop_owned_group(process)
                if process is not None:
                    result[label + '_final_returncode'] = process.returncode
            except BaseException as error:
                result['cleanup_errors'].append(label + ': ' + repr(error))
                status = 2
        if database_before:
            try:
                common.snapshot_database(run, database, 'after')
            except BaseException as error:
                result['cleanup_errors'].append('database-after: ' + repr(error))
                status = 2
        if server is not None:
            for label, action in [('postflight', common.preflight),
                                  ('benchmark_source_after', check_benchmark_source)]:
                try:
                    result[label] = action()
                except BaseException as error:
                    result['cleanup_errors'].append(label + ': ' + repr(error))
                    status = 2
        result.update(exit_code=status, finished_utc=common.utc(), cpu_after=common.cpu_state())
        common.write_json(run / 'manifest.json', manifest)
        common.write_json(run / 'result.json', result)
        (run / 'exit-code').write_text(str(status) + '\n')
        (run / 'finished-at.txt').write_text(result['finished_utc'] + '\n')
        for signum, handler in previous_handlers.items():
            signal.signal(signum, handler)
        if lock is not None:
            lock.close()
    print(json.dumps({'run_dir': str(run), 'exit_code': status,
                      'benchmark_completed': result['benchmark_completed']}), flush=True)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
