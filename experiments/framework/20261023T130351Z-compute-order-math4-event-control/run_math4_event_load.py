"""原32背景单次采样，按真实worker事件拆到达；四题保持原采样和判卷。"""
import argparse
from contextlib import ExitStack
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time

ROOT = Path('/workspace/experiments/minicpm-s2')
HERE = Path(__file__).resolve().parent
CAPTURE_SHA = '9e1f6bcf44c0b3c78226e87d2b8ccc0b5a95aa6d5af98a2eeab6f66a41d74aa5'
OFFICIAL_SHA = '6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4'
BACKGROUND_SHA = '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378'
CLIENT_PINS = {'gate_benchmark_requests.py': 'b7422674fb183afe95aa909dffb12fe7ed56f574b6de768c78230a8267628604', 'warm_capture_evalscope.py': 'f630f5e50248deb772c641c289578e710c9ab630b7f98424d4767064ee51bba1'}
DEADLINE_SECONDS = 210


class NotCovered(RuntimeError):
    pass


def stop_owned(job):
    try:
        os.killpg(job.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        job.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(job.pid, signal.SIGKILL)
        job.wait(timeout=5)
    try:
        os.killpg(job.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--capture', required=True, type=Path)
    parser.add_argument('--capture-output', required=True, type=Path)
    parser.add_argument('--seed', required=True, type=int, choices=(721201,))
    args = parser.parse_args()
    folder, capture, output = (p.resolve() for p in (args.run_dir, args.capture, args.capture_output))
    events = Path(os.environ['BIV150_COMPUTE_ORDER_MATH4_EVENT_DIR']).resolve()
    official, background = ROOT / 'scripts/run_math500_level3.sh', ROOT / 'scripts/run_diagnostic_load.sh'
    for path, pin in ((official, OFFICIAL_SHA), (background, BACKGROUND_SHA), (capture, CAPTURE_SHA)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('冻结原负载身份变化：' + str(path))
    if set(CLIENT_PINS) != {'gate_benchmark_requests.py', 'warm_capture_evalscope.py'}:
        raise ValueError('新客户端尚未冻结')
    for name, pin in CLIENT_PINS.items():
        if hashlib.sha256((HERE / name).read_bytes()).hexdigest() != pin:
            raise ValueError('薄客户端身份变化：' + name)
    if (not all(p.is_relative_to(ROOT) for p in (folder, output, events))
            or folder.exists() or output.exists() or not os.environ.get('BIV150_COMPUTE_ORDER_MATH4_DIR')):
        raise ValueError('诊断路径越界/复用或缺原capture ENV')
    signals = ('background-request-ids.json', 'background-both-q1.json', 'release-background-tail.json',
        'math4-client-ready.json', 'math4-go.json', 'benchmark-original-requests.json',
        'benchmark-request-outcomes.json', 'background-0-returned.json', 'background-1-returned.json',
        'observer-error.json', 'uncovered.json')
    if any((events / name).exists() for name in signals):
        raise ValueError('事件目录含旧信号，拒绝重用')
    events.mkdir(parents=True, exist_ok=True)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'official-script.sh').write_bytes(official.read_bytes())
    (folder / 'background-script.sh').write_bytes(background.read_bytes())
    body = official.read_text().split('evalscope eval \\\n', 1)[1].split('  2>&1 | tee ', 1)[0]
    original = [str(folder / 'math500-level3') if x == '$RUN_DIR' else x
        for x in shlex.split(body.replace('\\\n', ' '))]
    # 仅解析已锁原shell的exec argv；同一次原CLI处理seed、get_samples及全部32请求。
    text = background.read_text().split('exec vllm ', 1)[1].split('  > ', 1)[0]
    replacements = {'$RUN_DIR/results': str(folder / 'background/results'), '$LABEL': 'context-16k',
        '$INPUT_LEN': '16384', '$OUTPUT_LEN': '128', '$CONCURRENCY': '64', '$NUM_PROMPTS': '32', '$SEED': str(args.seed)}
    background_argv = [replacements.get(x, x) for x in shlex.split(text.replace('\\\n', ' '))]
    if any('$' in x for x in background_argv):
        raise ValueError('原shell出现未知变量，拒绝猜测展开')
    (folder / 'background/results').mkdir(parents=True)
    deadline = time.monotonic() + DEADLINE_SECONDS
    common = ['--events', str(events), '--deadline-monotonic', str(deadline)]
    commands = dict(math4=[sys.executable, str(HERE / 'warm_capture_evalscope.py'), *common,
        '--capture', str(capture), '--', '--output', str(output), '--', 'eval', *original, '--limit', '4'],
        background=[sys.executable, str(HERE / 'gate_benchmark_requests.py'), *common, '--', *background_argv])
    result = dict(status='started', kind='单候选事件到达质量诊断；不是性能/105题门',
        commands=commands, deadline_seconds=DEADLINE_SECONDS, events=str(events), jobs={}, cleanup_errors=[],
        original_sources=dict(official=OFFICIAL_SHA, background=BACKGROUND_SHA, capture=CAPTURE_SHA),
        client_sha256=CLIENT_PINS, started_monotonic_ns=time.monotonic_ns())
    jobs, code = {}, 1

    def interrupted(number, frame):
        raise KeyboardInterrupt('signal ' + str(number))
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, interrupted)
    try:
        with ExitStack() as stack:
            for label, command in commands.items():
                if label == 'background':
                    # 先完成原四题CPU预热，再开始前2背景，避免靠import耗时碰到窗口。
                    ready_path = events / 'math4-client-ready.json'
                    while not ready_path.is_file():
                        if jobs['math4'].poll() is not None:
                            raise NotCovered('原四题未完成预热即退出，不启动背景/不重试')
                        if time.monotonic() >= deadline:
                            raise TimeoutError('同一210s内四题未到原generate入口')
                        time.sleep(0.02)
                    ready_value = json.loads(ready_path.read_text())
                    if ready_value.get('ready_calls') != 4 or not ready_value.get('before_original_generate'):
                        raise ValueError('原四题预热信号不完整')
                    result['math4_preheated_before_background_monotonic_ns'] = time.monotonic_ns()
                log = stack.enter_context((folder / (label + '-launcher.log')).open('x'))
                jobs[label] = subprocess.Popen(command, cwd='/workspace', stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                result['jobs'][label] = dict(pid=jobs[label].pid, started_monotonic_ns=time.monotonic_ns())
            while True:
                if time.monotonic() >= deadline:
                    raise TimeoutError('210s总期限，未覆盖/未完成即inconclusive，不重试')
                if any(job.poll() not in (None, 0) for job in jobs.values()):
                    raise RuntimeError('原负载子进程失败，不重试')
                if any((events / name).is_file() for name in ('observer-error.json', 'uncovered.json')):
                    raise NotCovered('observer已报失败/几何丢失，不放行或重试')
                ready, both, go = (events / name for name in
                    ('math4-client-ready.json', 'background-both-q1.json', 'math4-go.json'))
                if not go.exists() and ready.is_file() and both.is_file():
                    warm, observed = (json.loads(path.read_text()) for path in (ready, both))
                    config_sha = hashlib.sha256((events / 'background-request-ids.json').read_bytes()).hexdigest()
                    if (warm.get('ready_calls') != 4 or observed.get('event') != 'background_both_decode_q1'
                            or type(observed.get('pid')) is not int or observed['pid'] <= 0
                            or observed.get('config_sha256') != config_sha):
                        raise ValueError('原四题/首2真实q1信号不完整')
                    temporary = go.with_suffix('.writing')
                    with temporary.open('x', encoding='utf-8') as stream:
                        json.dump(dict(monotonic_ns=time.monotonic_ns(), warm=warm, observed=observed), stream)
                    temporary.replace(go)
                    result['math4_released_monotonic_ns'] = time.monotonic_ns()
                if (all((events / ('background-' + str(index) + '-returned.json')).is_file() for index in (0, 1))
                        and not (events / 'release-background-tail.json').is_file()):
                    raise NotCovered('两初始背景均已返回但几何事件未到，停止且不换时序')
                if all(job.poll() is not None for job in jobs.values()):
                    if not (events / 'release-background-tail.json').is_file():
                        raise NotCovered('尾30未放行，不称覆盖')
                    result['status'], code = 'processes_completed_requires_report_review', 0
                    break
                time.sleep(0.02)  # 只轮询文件事件，不以延时安排到达。
    except BaseException as error:
        result.update(status=('timeout_inconclusive' if isinstance(error, TimeoutError)
            else 'uncovered_inconclusive' if isinstance(error, NotCovered) else 'failed'), error=repr(error))
    finally:
        for label, job in jobs.items():
            try:
                stop_owned(job)
            except Exception as error:
                result['cleanup_errors'].append(label + ':' + repr(error))
                code = 1
            result['jobs'][label]['returncode'] = job.poll()
        result.update(exit_code=code, finished_monotonic_ns=time.monotonic_ns())
        (folder / 'math4-event-load-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
