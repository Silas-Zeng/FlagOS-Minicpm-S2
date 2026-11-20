"""末层FFN选行独立组件owner：复用设备锁、实时空闲门和有界子进程清理。"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
DATABASE = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def now():
    return datetime.now(timezone.utc).isoformat()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj


def check_assets():
    pins = read(HERE / 'asset-pins.json')
    require({'run_component.py', 'component.py', 'exact_suffix.py'}.issubset(pins), '必要资产未固定')
    for name, digest in pins.items():
        require(sha(HERE / name) == digest, '资产变化: ' + name)
    return pins


def worker(run_dir):
    check_assets()
    component = module(HERE / 'component.py', 'final_ffn_row_component')
    component.run(Path(run_dir), Path('/workspace/MiniCPM5-2B'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        return worker(args.run_dir)
    import fcntl
    check_assets()
    common_path = ROOT / 'scripts/run_accuracy_gate.py'
    require(sha(common_path) == COMMON_SHA, '原设备清理helper变化')
    common = module(common_path, 'final_ffn_common')
    run = args.run_dir.resolve()
    require(run.is_relative_to(ROOT / 'diagnostics') and run != ROOT / 'diagnostics', '只允许独立diagnostics目录')
    run.mkdir(parents=True, exist_ok=False)
    state = dict(started_utc=now(), owner_pid=os.getpid(), command=sys.argv, completed=False, diagnostic=True)
    process = None
    original = None
    lock = (ROOT / 'framework-device.lock').open('a')

    def stop(signum, frame):
        raise KeyboardInterrupt(str(signum))

    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, stop)
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state['preflight'] = common.preflight()
        table = subprocess.check_output([common.IXSMI], text=True, timeout=10)
        query = subprocess.check_output([common.IXSMI, '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True, timeout=10)
        (run / 'preflight-ixsmi.txt').write_text(table)
        require('No running processes found' in table and query.strip() == '68, 0', '启动前设备不空闲')
        shutil.copyfile(DATABASE, run / 'database-original.sqlite')
        original = sha(run / 'database-original.sqlite')
        state['database_before_sha256'] = original
        env = {k: v for k, v in os.environ.items() if not k.startswith(('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
        env.pop('PYTHONPATH', None)
        env['PYTHONUNBUFFERED'] = '1'
        state['assets'] = check_assets()
        (run / 'source').mkdir()
        for name in [*state['assets'], 'asset-pins.json']:
            (run / 'source' / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE / name, run / 'source' / name)
        save(run / 'manifest.json', state)
        with (run / 'worker.log').open('x') as log:
            process = subprocess.Popen([sys.executable, '-B', str(Path(__file__).resolve()), '--run-dir', str(run), '--worker'],
                                       env=env, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state['worker_pid'] = process.pid
        save(run / 'manifest.json', state)
        deadline = time.monotonic() + 300
        with (run / 'gpu.csv').open('x') as output:
            fields = 'timestamp,memory.used,memory.total,utilization.gpu'
            output.write(fields + '\n')
            output.flush()
            while process.poll() is None:
                require(time.monotonic() < deadline, '组件编译/校验超过300秒，停止，不自动重试')
                output.write(subprocess.check_output([common.IXSMI, '--query-gpu=' + fields, '--format=csv,noheader'], text=True, timeout=10))
                output.flush()
                time.sleep(1)
        state['worker_exit_code'] = process.wait()
        require(process.returncode == 0 and read(run / 'results.json')['completed'], 'worker失败；保留原件')
        state['completed'] = True
    except BaseException:
        state['error'] = traceback.format_exc()
    finally:
        try:
            common.stop_owned_group(process, timeout=6)
            state['postflight'] = common.preflight()
            state['postflight_query'] = subprocess.check_output([common.IXSMI, '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True, timeout=10)
            require(state['postflight_query'].strip() == '68, 0', '收尾GPU未回空闲基准')
            if original is not None:
                shutil.copyfile(DATABASE, run / 'database-after.sqlite')
                state['database_after_sha256'] = sha(run / 'database-after.sqlite')
                shutil.copyfile(run / 'database-original.sqlite', DATABASE)
                state['database_restored'] = sha(DATABASE) == original
                require(state['database_restored'], '原DB恢复失败')
            state['source_unchanged'] = check_assets() == state.get('assets')
            require(state['source_unchanged'], '资产变化')
        except BaseException:
            state.update(completed=False, cleanup_error=traceback.format_exc())
        state['finished_utc'] = now()
        save(run / 'state.json', state)
        (run / 'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
    return 0 if state['completed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
