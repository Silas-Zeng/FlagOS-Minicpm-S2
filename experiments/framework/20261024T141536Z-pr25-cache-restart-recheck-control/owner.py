"""复用未变的组件门和首次建图，只补默认缓存重启；保留原格式误判。"""
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
DB = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
PREVIOUS = ROOT / 'accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/state.json'
DRIVER_SHA = '84a67eed8c9db23d9f9085974dd9d2ffe4ebcc66e8a536091659ed363d355bd0'
LIBRARY_SHA = '14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
PRIOR = ROOT / 'framework/20261024T135749Z-pr25-cache-first-restart'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    previous = json.loads(PREVIOUS.read_text())
    assert all(previous.get(k) is True for k in ('completed', 'database_restored', 'source_unchanged', 'native_unchanged'))
    build = json.loads((HERE / 'native-build-manifest.json').read_text())
    assert build['exit_code'] == 0 and build['source_commit'] == '7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93'
    assert build['library_sha256'] == LIBRARY_SHA
    assert sha(HERE / 'driver.py') == DRIVER_SHA
    driver = load_module(HERE / 'driver.py', 'frozen_cache_driver')
    assert sha(driver.COMMON) == driver.COMMON_SHA
    common = load_module(driver.COMMON, 'frozen_common')
    def idle():
        result = common.preflight()
        query = subprocess.check_output([common.IXSMI, '--query-gpu=memory.used,utilization.gpu',
                    '--format=csv,noheader,nounits'], text=True).strip()
        used, utilization = [int(x.strip()) for x in query.split(',')]
        full = subprocess.check_output([common.IXSMI], text=True)
        if used > 100 or utilization != 0 or 'No running processes found' not in full:
            raise RuntimeError('设备尚未空闲: ' + query)
        return dict(result, memory_used_mib=used, utilization=utilization, no_gpu_processes=True)
    source, library = Path(build['source']), Path(build['library'])
    mapping = json.loads((HERE / 'source-sha256.json').read_text())
    driver.identity(source, mapping, library, LIBRARY_SHA)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'framework' / (stamp + '-pr25-cache-restart-recheck')
    control = run.with_name(run.name + '-control')
    control.mkdir(exist_ok=False)
    for name in ('owner.py', 'driver.py', 'source-manifest.json', 'source-sha256.json', 'native-build-manifest.json', 'native-build.log'):
        shutil.copyfile(HERE / name, control / name)
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
                 source_commit=build['source_commit'], source_tree=build['source_tree'], completed=False)
    save(control / 'state.json', state)
    env = {k:v for k,v in os.environ.items() if not k.startswith(('BIV150_', 'VLLM_FL_BIV150_', 'MINICPM_NATIVE_', 'MINICPM_DECODE_GAP_'))}
    env.update(PYTHONPATH=str(source), PYTHONUNBUFFERED='1', BIV150_NATIVE_W8A8_LIBRARY=str(library))
    lock = (ROOT / 'framework-device.lock').open('a')
    process = None
    original = None
    handlers = {}
    commands = []
    def stage(name, command):
        nonlocal process
        commands.append(dict(name=name, command=command))
        save(control / 'commands.json', commands)
        with (control / (name + '.log')).open('x') as log:
            process = subprocess.Popen(command, cwd=source, env=env, stdin=subprocess.DEVNULL,
                                       stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state.update(stage=name, child_pid=process.pid)
        save(control / 'state.json', state)
        code = process.wait(timeout=1800)
        if code != 0:
            raise RuntimeError(name + ' failed: ' + str(code))
    try:
        for sig in (signal.SIGTERM, signal.SIGINT):
            handlers[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda number, frame: (_ for _ in ()).throw(KeyboardInterrupt(str(number))))
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        state['preflight'] = idle()
        shutil.copyfile(DB, control / 'database-original.sqlite')
        original = sha(control / 'database-original.sqlite')
        state['database_before_sha256'] = original
        prior_control = PRIOR.with_name(PRIOR.name + '-control')
        prior_state = json.loads((prior_control / 'state.json').read_text())
        assert prior_state['database_restored'] and prior_state['identity_after']['library_sha256'] == LIBRARY_SHA
        assert prior_state['source_commit'] == build['source_commit'] and prior_state['component_checks']['passed']
        assert json.loads((prior_control / 'source-sha256.json').read_text()) == mapping
        for name in ('gate-auto.json', 'cached-dispatch.json'):
            shutil.copyfile(prior_control / name, control / name)
        gate = json.loads((control / 'gate-auto.json').read_text())
        cached = json.loads((control / 'cached-dispatch.json').read_text())
        assert len(gate['records']) == 9 and all(r['passed'] for r in gate['records']) and gate['original_weight_fallback_unchanged']
        assert cached['completed'] and len(cached['records']) == 40 and all(r['bit_exact'] and r['changed_input_graph'] for r in cached['records'])
        state['component_checks'] = dict(gate=9, cached_dispatch=40, passed=True, reused_from=str(prior_control))
        fcntl.flock(lock, fcntl.LOCK_UN)
        stage('cache-service', [sys.executable, str(HERE / 'driver.py'), str(run), '--source-dir', str(source),
              '--source-sha256-json', str(HERE / 'source-sha256.json'), '--library', str(library), '--library-sha256', LIBRARY_SHA,
              '--prior-run', str(PRIOR)])
        result = json.loads((run / 'result.json').read_text())
        assert result['completed'] and result['exit_code'] == 0 and not result['cleanup_errors']
        state['service_result'] = result
        state['service_completed'] = True
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc())
    finally:
        try:
            if process is not None:
                common.stop_owned_group(process)
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            groups = [] if process is None else [driver.owned_group(process.pid)]
            result_path = run / 'result.json'
            if result_path.exists():
                groups.extend(driver.owned_group(x['pid']) for x in json.loads(result_path.read_text()).get('owned_processes', []))
            save(control / 'owner-process-groups.json', groups)
            assert not any(g['errors'] or any(m['state'] != 'Z' for m in g['members']) for g in groups)
            state['postflight'] = idle()
            if original is not None:
                shutil.copyfile(DB, control / 'database-after.sqlite')
                state['database_after_sha256'] = sha(DB)
                shutil.copyfile(control / 'database-original.sqlite', DB)
                state['database_restored'] = sha(DB) == original
                assert state['database_restored']
            state['identity_after'] = driver.identity(source, mapping, library, LIBRARY_SHA)
            state['completed'] = state.get('service_completed', False)
        except BaseException as error:
            state['cleanup_error'] = repr(error)
        state['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        save(control / 'state.json', state)
        (control / 'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    return 0 if state['completed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
