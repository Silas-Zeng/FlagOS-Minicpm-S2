#!/usr/bin/env python3
"""隔离组件的唯一设备 owner，保存终态并回收证据。"""
import argparse, datetime, fcntl, hashlib, io, json, os, signal, socket, subprocess, sys, tarfile, traceback
from pathlib import Path

ROOT = Path('/workspace/experiments/minicpm-s2')
HERE = Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def save(p, value): p.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def preflight(out, label):
    for family, address in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        try:
            with socket.socket(family) as sock:
                sock.settimeout(1)
                if sock.connect_ex((address, 9031)) == 0: raise RuntimeError('port 9031 occupied')
        except OSError:
            if family == socket.AF_INET: raise
    p = subprocess.run(['/usr/local/corex-4.5.0/bin/ixsmi'], text=True, capture_output=True, timeout=15)
    (out/(label+'-ixsmi.txt')).write_text(p.stdout+p.stderr)
    if p.returncode or 'No running processes found' not in p.stdout:
        raise RuntimeError('GPU process active or unknown')
    return dict(utc=utc(), port_9031='free', GPU_processes='none')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); ap.add_argument('--compiled',type=Path,required=True)
    a=ap.parse_args(); out=a.out.resolve()
    if ROOT not in out.parents: raise ValueError('output must be within experiment root')
    out.mkdir(parents=True,exist_ok=False)
    state=dict(status='running',owner_pid=os.getpid(),utc_start=utc(),entry=str(HERE),run=str(out),commands=[],official_performance=False)
    save(out/'state.json',state);(out/'owner.pid').write_text(str(os.getpid())+'\n')
    lock=None; child=None; ran=False
    try:
        review=json.loads((HERE/'runtime-review.json').read_text())
        state['runtime_review']=review
        state['input_sha256']={str(p.relative_to(HERE)):sha(p) for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        state['compiled_summary_sha256']=sha(a.compiled)
        lock=(ROOT/'framework-device.lock').open('a'); fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state['preflight']=preflight(out,'preflight');save(out/'state.json',state)
        cmd=[sys.executable,'-u',str(HERE/'worker.py'),'--gpu','--root-owned-exclusive','--main-root',str(HERE/'main-source'),'--compiled',str(a.compiled),'--out',str(out/'summary.json')]
        state['commands'].append(cmd)
        with (out/'component.log').open('w') as log:
            child=subprocess.Popen(cmd,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            ran=True;state['child_pid']=child.pid;save(out/'state.json',state)
            print('started',json.dumps(state),flush=True)
            try: rc=child.wait(timeout=900)
            except subprocess.TimeoutExpired:
                os.killpg(child.pid,signal.SIGTERM)
                try: child.wait(timeout=10)
                except subprocess.TimeoutExpired: os.killpg(child.pid,signal.SIGKILL);child.wait()
                raise
        state['exit_code']=rc
        if rc: raise RuntimeError('component exit '+str(rc))
        result=json.loads((out/'summary.json').read_text())
        state['case_count']=len(result['cases']);state['status']='pass'
    except Exception:
        state['status']='fail';state['error']=traceback.format_exc()
    finally:
        if lock is not None:
            if ran:
                try: state['postflight']=preflight(out,'postflight')
                except Exception: state['status']='fail';state['postflight_error']=traceback.format_exc()
            lock.close()
        state['utc_end']=utc();save(out/'state.json',state)
    files=[]
    for folder in (HERE,out):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts:
                files.append(dict(path=p.relative_to(ROOT).as_posix(),bytes=p.stat().st_size,sha256=sha(p)))
    bundle=ROOT/(out.name+'-recovery.tar.gz')
    with tarfile.open(bundle,'w:gz') as tar:
        for f in files: tar.add(ROOT/f['path'],arcname=f['path'],recursive=False)
        data=json.dumps(dict(run=out.name,files=files),indent=2).encode(); item=tarfile.TarInfo('manifest.json');item.size=len(data);tar.addfile(item,io.BytesIO(data))
    print('terminal',json.dumps(state),flush=True)
    print('archive',json.dumps(dict(path=str(bundle),sha256=sha(bundle),bytes=bundle.stat().st_size,files=len(files))),flush=True)
    return 0 if state['status']=='pass' else 1

if __name__=='__main__':raise SystemExit(main())
