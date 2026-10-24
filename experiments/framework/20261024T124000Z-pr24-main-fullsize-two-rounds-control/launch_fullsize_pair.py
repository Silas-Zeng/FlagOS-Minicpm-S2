"""完整官方规模的两轮筛选：原 benchmark 函数，不改变官方四轮成绩口径。"""
from datetime import datetime, timezone
import argparse
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import signal
import subprocess
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
REFERENCE = ROOT / 'framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control'
BASE = ROOT / 'code/main-pr24-1ad9a708-20261024T105037Z'
HELPER = ROOT / 'scripts/pr24-kv-swap-v1-20261024122148Z/launch_kv_verify1.py'
HELPER_SHA = 'f1e30e77162762ca0da709d8c8b2e6ed9a5fab2cb2edd058e1240e20669ea543'
SEED_SHA = 'fb0353979939fb6cde016b826b181555aaf11cf1c9c256ddc49c532392f57cfe'
NATIVE_BUILD = ROOT / 'framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json'
DATABASE = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def write(p, x):
    p.write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n')

def helper():
    if sha(HELPER) != HELPER_SHA:
        raise ValueError('受测 VERIFY1 owner 变化')
    spec = importlib.util.spec_from_file_location('sealed_verify1', HELPER)
    u = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(u)
    return u

def qualification(u):
    pins = read(HERE / 'asset-pins.json')
    for name, pin in pins.items():
        if sha(HERE / name) != pin:
            raise ValueError('筛选资产变化: ' + name)
    s, v = read(REFERENCE / 'state.json'), read(REFERENCE / 'coverage.json')
    if ((REFERENCE / 'exit-code').read_text().strip() != '0'
            or not all(s.get(k) is True for k in ('completed', 'source_unchanged', 'native_unchanged', 'database_restored'))
            or v.get('valid') is not True or s['tree'] != u.OBSERVER_TREE
            or sha(REFERENCE / 'launch_kv_verify1.py') != HELPER_SHA
            or sha(REFERENCE / 'database-after.sqlite') != SEED_SHA):
        raise ValueError('VERIFY1 未完成或共同 DB 种子变化')
    base_blobs, base_hashes = u.source_ready(BASE)
    candidate = Path(s['source'])
    candidate_maps = (read(REFERENCE / 'source-git-blobs.json'), read(REFERENCE / 'source-sha256.json'))
    if u.source_maps(candidate) != candidate_maps or u.source_maps(REFERENCE / 'plugin-source') != candidate_maps:
        raise ValueError('受测473源码变化')
    if len(candidate_maps[0]) != 473:
        raise ValueError('受测文件数变化')
    native = u.native_ready(NATIVE_BUILD, base_hashes)
    return {'main': (BASE, base_blobs, base_hashes, u.TREE),
            'kv': (candidate, *candidate_maps, u.OBSERVER_TREE)}, native

def snapshot(control, phase, u):
    script = ROOT / 'scripts/snapshot_tuning_db.py'
    if sha(script) != u.SCRIPTS['snapshot_tuning_db.py']:
        raise ValueError('DB快照脚本变化')
    with (control / ('db-' + phase + '.log')).open('x') as output:
        subprocess.run(['python3', str(script), '--database', str(DATABASE), '--output', str(control / ('db-' + phase))],
                       stdout=output, stderr=subprocess.STDOUT, check=True, timeout=120)

def observe(run):
    log = (run / 'server.log').read_text(errors='replace')
    tokens = sorted(set(int(x.replace(',', '')) for x in re.findall(r'GPU KV cache size:\s*([\d,]+)\s*tokens', log)))
    return dict(kv_tokens=tokens, q_selected=log.count('BIV150_Q_FRAGMENT_SELECTED '),
                q_fallback=log.count('BIV150_Q_FRAGMENT_FALLBACK '),
                p_selected=log.count('BIV150_COMPUTE_ORDER_FIRST_SELECTED '),
                native_installed=log.count('BIV150_NATIVE_W8A8_INSTALL'),
                resolve_benchmarker_lines=sum('resolve_benchmarker' in x for x in log.splitlines()))

def run_role(u, role, inputs, native):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'framework' / (stamp + '-pr24-' + role + '-fullsize-two-rounds')
    control = run.with_name(run.name + '-control')
    source = ROOT / 'code' / (stamp + '-pr24-' + role + '-fullsize')
    origin, blobs, hashes, tree = inputs
    control.mkdir(exist_ok=False)
    shutil.copytree(origin, source, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if u.source_maps(source) != (blobs, hashes):
        raise ValueError('新独立源码复制不符')
    shutil.copytree(source, control / 'plugin-source', symlinks=True)
    write(control / 'source-git-blobs.json', blobs)
    write(control / 'source-sha256.json', hashes)
    shutil.copyfile(__file__, control / Path(__file__).name)
    shutil.copyfile(HERE / 'driver.py', control / 'driver.py')
    shutil.copyfile(HERE / 'asset-pins.json', control / 'asset-pins.json')
    shutil.copyfile(HELPER, control / 'reused_verify1_owner.py')
    build, library, build_log = native
    (control / 'native').mkdir()
    runtime = control / 'native/biv150_native_w8a8.so'
    shutil.copyfile(library, runtime)
    shutil.copyfile(build_log, control / 'native/build.log')
    shutil.copyfile(NATIVE_BUILD, control / 'native/build-manifest.original.json')
    receipt = control / 'native/runtime-receipt.json'
    write(receipt, dict(build, runtime_library=str(runtime)))
    if sha(runtime) != build['library_sha256']:
        raise ValueError('native 复制不符')
    env = os.environ.copy()
    removed = [k for k in env if k.startswith('BIV150_') or k in ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR')]
    for k in removed:
        env.pop(k)
    for k in ('VLLM_FL_BIV150_PREFILL_NORMALIZE', 'VLLM_FL_BIV150_GQA_DECODE', 'VLLM_FL_BIV150_Q_FRAGMENT', 'VLLM_FL_BIV150_NATIVE_W8A8'):
        if env.get(k, '1') != '1':
            raise ValueError('不允许关闭当前受测方法: ' + k)
    env.update(BIV150_KV_VERIFY_RESTORE='0', BIV150_NATIVE_W8A8_LIBRARY=str(runtime),
               BIV150_RESUME_NATIVE_RECEIPT=str(receipt), BIV150_RESUME_NATIVE_RECEIPT_SHA256=sha(receipt))
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    write(control / 'environment-overrides.json', {k:v for k,v in env.items() if k.startswith(('BIV150_', 'VLLM_FL_BIV150_'))})
    command = ['python3', str(HERE / 'driver.py'), str(run), '--source-dir', str(source), '--role', role]
    (control / 'command.txt').write_text(shlex.join(command) + '\n')
    state = dict(owner_pid=os.getpid(), role=role, run=str(run), control=str(control), source=str(source),
                 base_commit=u.COMMIT, tree=tree, source_count=len(blobs), completed=False,
                 benchmark_kind='官方规模两轮筛选；不是官方四轮成绩', seed_sha256=SEED_SHA,
                 removed_environment_names=sorted(removed), driver_sha256=sha(HERE / 'driver.py'))
    lock = (ROOT / 'framework-device.lock').open('a')
    process, original, success, cleanup = None, None, False, False
    backup = control / 'database-original.sqlite'
    handlers = {}
    try:
        for signum in (signal.SIGTERM, signal.SIGINT):
            handlers[signum] = signal.getsignal(signum)
            signal.signal(signum, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt(str(number))))
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state['preflight'] = u.idle()
        cpu = Path('/sys/fs/cgroup/cpu,cpuacct')
        if int((cpu / 'cpu.cfs_quota_us').read_text()) != 6 * int((cpu / 'cpu.cfs_period_us').read_text()):
            raise ValueError('当前非6CPU配额')
        shutil.copyfile(DATABASE, backup)
        original = sha(backup)
        seed = REFERENCE / 'database-after.sqlite'
        if sha(seed) != SEED_SHA:
            raise ValueError('共同DB种子变化')
        shutil.copyfile(seed, control / 'database-seed.sqlite')
        shutil.copyfile(seed, DATABASE)
        if sha(DATABASE) != SEED_SHA:
            raise ValueError('DB播种失败')
        state.update(database_original_sha256=original, database_before_sha256=SEED_SHA)
        snapshot(control, 'before', u)
        fcntl.flock(lock, fcntl.LOCK_UN)
        with (control / 'runner.log').open('x') as log:
            process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state.update(driver_pid=process.pid, stage='running')
        write(control / 'state.json', state)
        (control / 'runner.pid').write_text(str(process.pid) + '\n')
        print(json.dumps(state), flush=True)
        code = process.wait()
        state['driver_exit_code'] = code
        result = read(run / 'result.json')
        if (code != 0 or (run / 'exit-code').read_text().strip() != '0'
                or result.get('benchmark_completed') is not True or result.get('cleanup_errors')):
            raise RuntimeError('两轮完整规模筛选未成功完成；保留原件')
        state['observations'] = observe(run)
        state['result'] = result
        success = True
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc())
    finally:
        try:
            if process is not None and process.poll() is None:
                # 只清理由本owner创建的driver组；子服务由driver的signal handler清理。
                os.killpg(process.pid, signal.SIGTERM)
                process.wait(timeout=120)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state['postflight'] = u.idle()
            if process is not None:
                owned_pids = {process.pid}
                result_file = run / 'result.json'
                if result_file.exists():
                    for item in read(result_file).get('owned_processes', []):
                        if type(item.get('pid')) is not int or item['pid'] <= 1:
                            raise ValueError('driver声明的owned PID格式不符')
                        owned_pids.add(item['pid'])
                for path in [run / 'server.pid', run / 'monitor.pid', *run.glob('*-round-*/worker.pid')]:
                    if path.exists():
                        pid = int(path.read_text().strip())
                        if pid <= 1:
                            raise ValueError('本轮PID文件不符')
                        owned_pids.add(pid)
                groups = [u.owned_group(pid) for pid in sorted(owned_pids)]
                deadline = time.monotonic() + 6
                while (not any(g['errors'] for g in groups)
                       and any(x['state'] != 'Z' for g in groups for x in g['members'])
                       and time.monotonic() < deadline):
                    time.sleep(.2)
                    groups = [u.owned_group(pid) for pid in sorted(owned_pids)]
                write(control / 'owner-process-group.json', dict(groups=groups, max_grace_seconds=6))
                if any(g['errors'] for g in groups) or any(x['state'] != 'Z' for g in groups for x in g['members']):
                    raise RuntimeError('本轮独立进程组未清理；保留DB不恢复')
                state['postflight_after_grace'] = u.idle()
            if original is not None:
                snapshot(control, 'after', u)
                shutil.copyfile(DATABASE, control / 'database-after.sqlite')
                state['database_after_sha256'] = sha(control / 'database-after.sqlite')
                shutil.copyfile(backup, DATABASE)
                state['database_restored'] = sha(DATABASE) == original
                if not state['database_restored']:
                    raise RuntimeError('原DB恢复失败')
            state['source_unchanged'] = all(u.source_maps(p) == (blobs, hashes) for p in (origin, source, control / 'plugin-source'))
            state['native_unchanged'] = sha(runtime) == build['library_sha256']
            if not state['source_unchanged'] or not state['native_unchanged']:
                raise RuntimeError('源码/native发生变化')
            cleanup = True
        except BaseException as error:
            state['cleanup_error'] = repr(error)
        state.update(completed=success and cleanup, finished_utc=datetime.now(timezone.utc).isoformat())
        write(control / 'state.json', state)
        (control / 'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
        for signum, handler in handlers.items():
            signal.signal(signum, handler)
    if not state['completed']:
        raise RuntimeError('本角色未完成，停止后继: ' + str(control))
    return state

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--roles', choices=['main', 'kv', 'pair'], default='pair')
    args = parser.parse_args()
    u = helper()
    sources, native = qualification(u)
    results = []
    for role in (['main', 'kv'] if args.roles == 'pair' else [args.roles]):
        # 前一角色可能运行较久；每次重新核对封存资格与执行资产。
        sources, native = qualification(u)
        results.append(run_role(u, role, sources[role], native))
    print(json.dumps({'completed_roles': [s['role'] for s in results], 'controls': [s['control'] for s in results]}), flush=True)

if __name__ == '__main__':
    main()
