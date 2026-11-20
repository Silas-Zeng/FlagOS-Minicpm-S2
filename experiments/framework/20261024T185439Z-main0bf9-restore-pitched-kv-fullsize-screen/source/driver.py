"""完整规模两轮筛选；原官方函数和SERVER不改，不生成官方分数。"""
import argparse
import importlib.util
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
BENCHMARK = Path('/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py')
COMMON = ROOT / 'scripts/run_accuracy_gate.py'
MONITOR = ROOT / 'scripts/monitor_gpu.sh'
BENCHMARK_SHA = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
MONITOR_SHA = 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'
CASES = ((4096, 1024, 64, 256), (16384, 1024, 64, 128))
ROUNDS = 2


def sha(path):
    import hashlib
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def load(path, pin, name):
    if path.is_symlink() or sha(path) != pin:
        raise ValueError('原脚本身份变化: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def official():
    module = load(BENCHMARK, BENCHMARK_SHA, 'original_throughput_benchmark')
    if (module.RUNS, module.SKIP_FIRST) != (4, 1):
        raise ValueError('官方四轮/丢首轮约定变化')
    return module


def validate_metrics(metrics, case):
    counts = {'successful_requests': case[3], 'total_input_tokens': case[0] * case[3],
              'total_output_tokens': case[1] * case[3]}
    if any(type(metrics.get(k)) not in (int, float) or metrics[k] != v for k, v in counts.items()):
        raise ValueError('成功请求或完整token数不符: ' + repr(counts))
    for name in ('benchmark_duration', 'total_token_throughput', 'output_throughput',
                 'mean_ttft_ms', 'mean_tpot_ms', 'elapsed_sec'):
        value = metrics.get(name)
        if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
            raise ValueError('缺有效度量: ' + name)


def measure(task_path):
    # 原run_once内部subprocess.run不设session；本worker由父driver创建独立组，
    # 因此原bench及其子进程均归本组，父driver超时/异常可统一停止。
    task = json.loads(task_path.read_text(encoding='utf-8'))
    case = tuple(task['case'])
    if case not in CASES or task['round'] not in (1, 2):
        raise ValueError('非冻结两档两轮')
    benchmark = official()
    common_args = benchmark.build_common_args('/workspace/MiniCPM5-2B', 9031, 'minicpm')
    save(task_path.with_name('benchmark-command.json'), common_args + [
        '--random-input-len', str(case[0]), '--random-output-len', str(case[1]),
        '--max-concurrency', str(case[2]), '--num-prompts', str(case[3])])
    metrics = benchmark.run_once(case, task['round'], common_args)
    save(task_path.with_name('metrics.json'), metrics)
    validate_metrics(metrics, case)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_dir', type=Path, nargs='?')
    parser.add_argument('--source-dir', type=Path)
    parser.add_argument('--role', choices=('main', 'kv'))
    parser.add_argument('--measure-one', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.measure_one is not None:
        return measure(args.measure_one)
    if args.run_dir is None or args.source_dir is None or args.role is None:
        parser.error('需要RUN --source-dir SOURCE --role main|kv')
    run, source = args.run_dir.resolve(), args.source_dir.resolve(strict=True)
    if not run.is_relative_to(ROOT / 'framework') or run == ROOT / 'framework':
        raise ValueError('run须为framework内新目录')
    if not source.is_relative_to(ROOT / 'code') or not (source / 'vllm_fl/worker/model_runner.py').is_file():
        raise ValueError('source须为code内隔离插件')
    common = load(COMMON, COMMON_SHA, 'original_owned_common')
    benchmark = official()
    if sha(MONITOR) != MONITOR_SHA:
        raise ValueError('原GPU monitor变化')
    run.mkdir(parents=True, exist_ok=False)
    archive = run / 'source'
    archive.mkdir()
    for path in (Path(__file__).resolve(), BENCHMARK, COMMON, MONITOR):
        (archive / path.name).write_bytes(path.read_bytes())
    manifest = {'kind': '完整规模两轮筛选，非官方分数', 'role': args.role,
        'source_dir': str(source), 'server_command': common.SERVER, 'started_utc': common.utc(),
        'cases': CASES, 'screen_rounds_per_case': ROUNDS, 'official_constants_unchanged': {'RUNS': 4, 'SKIP_FIRST': 1},
        'profiler': False, 'smoke_requests': 0, 'cpu_before': common.cpu_state(),
        'source_sha256': {p.name: sha(p) for p in archive.iterdir()},
        'limitations': ['两轮分别报告，不丢首轮、不套官方三轮均值。',
                        'DB播种/恢复、完整source/native资格与两角色比较由外层owner负责。']}
    result = {'status': 'started', 'benchmark_completed': False, 'role': args.role,
              'cleanup_errors': [], 'rounds': [], 'owned_processes': []}
    lock = server = monitor = None
    workers, handlers = [], {}
    status = 1
    try:
        import fcntl
        lock = (ROOT / 'framework-device.lock').open('a')
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for signum in (signal.SIGTERM, signal.SIGINT):
            handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt(str(number))))
        manifest['preflight'] = common.preflight()
        env = common.child_environment(source)
        if env.get('BIV150_KV_VERIFY_RESTORE') != '0':
            raise ValueError('两个角色均须由owner显式VERIFY0')
        save(run / 'manifest.json', manifest)
        with (run / 'server.log').open('x') as output:
            server = subprocess.Popen(common.SERVER, cwd='/workspace', env=env, stdout=output,
                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        (run / 'server.pid').write_text(str(server.pid) + '\n')
        result['owned_processes'].append({'kind': 'server', 'pid': server.pid})
        with (run / 'monitor.log').open('x') as output:
            monitor = subprocess.Popen(['bash', str(archive / MONITOR.name), str(server.pid), str(run / 'gpu.csv')],
                stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
        (run / 'monitor.pid').write_text(str(monitor.pid) + '\n')
        result['owned_processes'].append({'kind': 'monitor', 'pid': monitor.pid})
        marker = 'BIV150_KV_PROTOCOL_INSTALLED' if args.role == 'kv' else 'BIV150_NATIVE_W8A8_INSTALL'
        common.wait_ready(server, marker, run)
        result['benchmark_started_utc'] = common.utc()
        for case in CASES:
            for round_number in range(1, ROUNDS + 1):
                folder = run / f'{case[0]}-round-{round_number}'
                folder.mkdir()
                task = {'case': case, 'round': round_number, 'role': args.role, 'started_utc': common.utc()}
                task_path = folder / 'task.json'
                save(task_path, task)
                command = [sys.executable, str(archive / 'driver.py'), '--measure-one', str(task_path)]
                save(folder / 'worker-command.json', command)
                with (folder / 'stdout.log').open('x') as output:
                    worker = subprocess.Popen(command, cwd=folder, env=env, stdout=output,
                        stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
                workers.append(worker)
                result['owned_processes'].append({'kind': folder.name, 'pid': worker.pid})
                (folder / 'worker.pid').write_text(str(worker.pid) + '\n')
                save(run / 'result.json', result)
                code = worker.wait(timeout=2400)
                (folder / 'exit-code').write_text(str(code) + '\n')
                metrics_path = folder / 'metrics.json'
                metrics = json.loads(metrics_path.read_text(encoding='utf-8')) if metrics_path.exists() else {}
                row = benchmark.format_result(case, metrics, include_successful_requests=True)
                row['Run Status'] = 'SUCCESS' if code == 0 else 'FAILED'
                benchmark.append_csv(row, str(run / 'raw_runs_screen.csv'), benchmark.RAW_CSV_COLUMNS)
                result['rounds'].append({**task, 'finished_utc': common.utc(), 'worker_exit_code': code,
                    'metrics': metrics, 'stdout': str(folder / 'stdout.log'), 'metrics_path': str(folder / 'metrics.json')})
                save(run / 'result.json', result)
                if code or server.poll() is not None:
                    raise RuntimeError('完整规模单轮失败或服务退出: ' + folder.name)
                validate_metrics(metrics, case)
        result.update(status='fullsize_two_rounds_completed', benchmark_completed=True,
                      benchmark_finished_utc=common.utc())
        status = 0
    except BaseException as error:
        result.update(status='failed', error=repr(error), traceback=traceback.format_exc())
    finally:
        for label, process in [(f'worker-{i+1}', p) for i, p in enumerate(workers)] + [('server', server), ('monitor', monitor)]:
            try:
                common.stop_owned_group(process)
            except BaseException as error:
                result['cleanup_errors'].append(label + ': ' + repr(error))
                status = 2
        if server is not None:
            try:
                result['postflight'] = common.preflight()
                if sha(BENCHMARK) != BENCHMARK_SHA or sha(COMMON) != COMMON_SHA or sha(MONITOR) != MONITOR_SHA:
                    raise ValueError('原官方脚本/common/monitor结束身份变化')
            except BaseException as error:
                result['cleanup_errors'].append('postflight: ' + repr(error))
                status = 2
        result.update(exit_code=status, finished_utc=common.utc(), cpu_after=common.cpu_state())
        save(run / 'manifest.json', manifest)
        save(run / 'result.json', result)
        (run / 'exit-code').write_text(str(status) + '\n')
        (run / 'finished-at.txt').write_text(result['finished_utc'] + '\n')
        for signum, handler in handlers.items():
            signal.signal(signum, handler)
        if lock is not None:
            lock.close()
    print(json.dumps({'run_dir': str(run), 'exit_code': status,
                      'benchmark_completed': result['benchmark_completed']}), flush=True)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
