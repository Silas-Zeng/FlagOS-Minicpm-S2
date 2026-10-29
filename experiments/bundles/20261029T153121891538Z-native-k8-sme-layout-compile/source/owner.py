#!/usr/bin/env python3
"""单一设备 owner；compile 不启动 GPU，gpu 只运行隔离布局探针。"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import traceback

ROOT = Path('/workspace/experiments/minicpm-s2')
IXSMI = '/usr/local/corex-4.5.0/bin/ixsmi'
FILES = ('native_k8_sme_probe.cu', 'build.sh', 'probe.py', 'run.sh', 'README.md', 'review.md')

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')

def preflight(out, label):
    for family, address in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        try:
            with socket.socket(family) as sock:
                sock.settimeout(1)
                if sock.connect_ex((address, 9031)) == 0:
                    raise RuntimeError('port 9031 occupied')
        except OSError:
            if family == socket.AF_INET:
                raise
    p = subprocess.run([IXSMI], text=True, capture_output=True, timeout=15)
    (out/(label+'-ixsmi.txt')).write_text(p.stdout+p.stderr)
    if p.returncode or 'No running processes found' not in p.stdout:
        raise RuntimeError('GPU pre/postflight reports active or unknown processes')
    return {'utc': utc(), 'port_9031': 'free', 'GPU_processes': 'none'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=('compile', 'gpu'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--compiled', type=Path)
    a = ap.parse_args()
    out = a.out.resolve()
    if ROOT not in out.parents:
        raise ValueError('output must be a fresh experiment directory')
    out.mkdir(parents=True, exist_ok=False)
    state = {'mode': a.mode, 'utc_start': utc(), 'owner_pid': os.getpid(),
             'entry': str(Path(__file__).resolve()), 'owner_sha256': sha(__file__),
             'commands': [], 'status': 'running', 'GPU_performance_claim': False}
    save(out/'state.json', state)
    (out/'owner.pid').write_text(str(os.getpid())+'\n')
    lock = None
    def run(cmd, name, timeout):
        state['commands'].append(cmd)
        save(out/'state.json', state)
        with (out/(name+'.log')).open('w') as log:
            child = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT)
            state['child_pid'] = child.pid
            save(out/'state.json', state)
            try:
                code = child.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                child.terminate()
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    child.kill(); child.wait()
                raise
        state['last_exit_code'] = code
        if code:
            raise RuntimeError(name+' failed with exit '+str(code))
    try:
        if a.mode == 'compile':
            source = out/'source'
            source.mkdir()
            here = Path(__file__).resolve().parent
            for name in FILES:
                shutil.copyfile(here/name, source/name)
            state['input_sha256'] = {name: sha(source/name) for name in FILES}
            run(['bash', str(source/'build.sh')], 'compile', 180)
            library = source/'build/libnative_k8_sme_probe.so'
            state['library'] = {'path': str(library), 'sha256': sha(library)}
            # 从实际SO提取指令；不加载库，不导入Torch，不运行kernel。
            for fmt in ('IR', 'sass'):
                run(['/usr/local/corex/bin/ixobjdump', '--'+fmt, str(library)], 'actual-SO-'+fmt, 30)
            run(['/usr/local/corex/bin/clang++', '--version'], 'compiler-version', 15)
        else:
            if a.compiled is None:
                raise ValueError('explicit compiled result required')
            old = json.loads((a.compiled/'state.json').read_text())
            if old['status'] != 'pass' or old['mode'] != 'compile':
                raise ValueError('compile did not pass')
            source = a.compiled/'source'
            for name, expected in old['input_sha256'].items():
                if sha(source/name) != expected:
                    raise ValueError('compiled input changed: '+name)
            library = Path(old['library']['path'])
            if sha(library) != old['library']['sha256']:
                raise ValueError('compiled library changed')
            state['compiled_state_sha256'] = sha(a.compiled/'state.json')
            state['library'] = old['library']
            lock = (ROOT/'framework-device.lock').open('a')
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state['preflight'] = preflight(out, 'preflight')
            run([sys.executable, str(source/'probe.py'), '--library', str(library),
                 '--output', str(out/'probe-result.json')], 'probe', 120)
            result = json.loads((out/'probe-result.json').read_text())
            if result.get('status') != 'PASS':
                raise ValueError('layout equality failed')
            state['case_count'] = result['case_count']
        state['status'] = 'pass'
    except Exception:
        state['status'] = 'fail'
        state['error'] = traceback.format_exc()
    finally:
        if lock is not None:
            try: state['postflight'] = preflight(out, 'postflight')
            except Exception:
                state['status'] = 'fail'
                state['postflight_error'] = traceback.format_exc()
            lock.close()
        state['utc_end'] = utc()
        save(out/'state.json', state)
    print(json.dumps(state, ensure_ascii=False), flush=True)
    return 0 if state['status'] == 'pass' else 1

if __name__ == '__main__':
    raise SystemExit(main())
