"""一次并发原16K背景与原Math500前四题；诊断超时不重试，不是官方准确率。"""
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
CAPTURE_SHA = '9e1f6bcf44c0b3c78226e87d2b8ccc0b5a95aa6d5af98a2eeab6f66a41d74aa5'
OFFICIAL_SHA = '6e045c1cda5a6379ddff1bf7c41ab1e4cbaaddd51b2ca9b4b1d2a92cfa8bb5f4'
BACKGROUND_SHA = '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378'
DEADLINE_SECONDS = 210


class NotCovered(RuntimeError):
    pass


def stop_owned(job):
    # 即使父进程已经退出，也清理本次独立组内可能遗留的CPU子进程。
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
    parser.add_argument('--seed', type=int, required=True, choices=(721201,))
    args = parser.parse_args()
    folder, capture, output = (p.resolve() for p in (args.run_dir, args.capture, args.capture_output))
    official, background = ROOT / 'scripts/run_math500_level3.sh', ROOT / 'scripts/run_diagnostic_load.sh'
    for path, pin in ((official, OFFICIAL_SHA), (background, BACKGROUND_SHA), (capture, CAPTURE_SHA)):
        if pin is None or hashlib.sha256(path.read_bytes()).hexdigest() != pin:
            raise ValueError('未冻结或变化的负载源：' + str(path))
    if not folder.is_relative_to(ROOT) or not output.is_relative_to(ROOT) or output.exists():
        raise ValueError('诊断路径越界或capture输出已存在')
    if not os.environ.get('BIV150_COMPUTE_ORDER_MATH4_DIR'):
        raise ValueError('缺少原service capture目录ENV')
    folder.mkdir(parents=True, exist_ok=False)
    (folder / 'official-script.sh').write_bytes(official.read_bytes())
    # 从已锁6e045脚本文本提取原argv，不执行/改写原脚本；唯一诊断变化为limit4。
    body = official.read_text().split('evalscope eval \\\n', 1)[1].split('  2>&1 | tee ', 1)[0]
    original = shlex.split(body.replace('\\\n', ' '))
    original = [str(folder / 'math500-level3') if x == '$RUN_DIR' else x for x in original]
    commands = dict(background=['bash', str(background), str(folder / 'background'),
        'context-16k', '16384', '128', '64', '32', str(args.seed)],
        math4=[sys.executable, str(capture), '--output', str(output), '--', 'eval', *original, '--limit', '4'])
    result = dict(kind='一次混合诊断；非官方105题门或性能pair', status='started',
        commands=commands, deadline_seconds=DEADLINE_SECONDS, requested_dataset_scope='原Level 3 limit4；index0..3题身份待原报告后验',
        official_sha256=OFFICIAL_SHA, background_sha256=BACKGROUND_SHA, capture_sha256=CAPTURE_SHA,
        started_monotonic_ns=time.monotonic_ns(), jobs={}, cleanup_errors=[])
    jobs, code = {}, 1
    def interrupted(number, frame):
        raise KeyboardInterrupt('signal ' + str(number))
    for number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(number, interrupted)
    try:
        with ExitStack() as stack:
            deadline = time.monotonic() + DEADLINE_SECONDS
            # 仅候选诊断：背景先行，本次新mixed marker出现后才启动原EvalScope。
            server_log = folder.parent / 'server.log'
            begin = server_log.stat().st_size
            result['arrival_gate_log_start_byte'] = begin
            for label, command in commands.items():
                if label == 'math4':
                    marker, pending = 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ', b''
                    with server_log.open('rb') as stream:
                        stream.seek(begin)
                        while True:
                            if jobs['background'].poll() is not None:
                                raise NotCovered('背景已结束，未放行Math4；不重试')
                            if time.monotonic() >= deadline:
                                raise TimeoutError('210s内未得到本次背景mixed标志')
                            pending += stream.read()
                            lines = pending.split(b'\n')
                            pending = lines.pop()
                            hits = [line.decode(errors='replace').split(marker, 1)[1]
                                for line in lines if marker.encode() in line]
                            if hits:
                                result['arrival_gate'] = dict(marker=json.loads(hits[0]), monotonic_ns=time.monotonic_ns())
                                break
                            time.sleep(0.1)
                log = stack.enter_context((folder / (label + '-launcher.log')).open('x'))
                jobs[label] = subprocess.Popen(command, cwd='/workspace', stdin=subprocess.DEVNULL,
                    stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                result['jobs'][label] = dict(pid=jobs[label].pid, started_monotonic_ns=time.monotonic_ns())
            while any(job.poll() is None for job in jobs.values()):
                if any(job.poll() not in (None, 0) for job in jobs.values()):
                    raise RuntimeError('原负载子进程失败；不重试')
                if time.monotonic() >= deadline:
                    raise TimeoutError('210s诊断期限；四题未完成则inconclusive')
                time.sleep(0.1)
            if any(job.returncode != 0 for job in jobs.values()):
                raise RuntimeError('原负载子进程失败；不重试')
            result['status'], code = 'processes_completed_requires_report_review', 0
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
        result.update(finished_monotonic_ns=time.monotonic_ns(), exit_code=code)
        (folder / 'math4-load-summary.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
