"""新main526→KV532原官方四轮顺序对照；实际图/同DB/原参数，无新增请求。"""
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
SEED_REFERENCE = ROOT / 'framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control'
BASE = None  # --base-source明确提供526根
HELPER = ROOT / 'scripts/pr24-kv-swap-v1-20261024122148Z/launch_kv_verify1.py'
HELPER_SHA = 'f1e30e77162762ca0da709d8c8b2e6ed9a5fab2cb2edd058e1240e20669ea543'
SEED_SHA = 'fb0353979939fb6cde016b826b181555aaf11cf1c9c256ddc49c532392f57cfe'
NATIVE_BUILD = ROOT / 'scripts/pr25-cache-service-check-20261024T1340/native-build-manifest.json'
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
    u.COMMIT = '0bf9d2efeaa10144dd7f0ff4597298df029f9328'
    original_maps = u.source_maps
    def source_maps(root):
        root = Path(root)
        if root.is_symlink():
            raise ValueError('源码根不可为symlink')
        root = root.resolve(strict=True)
        if not root.is_relative_to(ROOT):
            raise ValueError('源码根越出实验目录')
        blobs, hashes = original_maps(root)
        for relative, blob in blobs.items():
            if blob['mode'] == '120000':
                path = root / relative
                if not path.is_symlink() or not path.resolve(strict=True).is_relative_to(root):
                    raise ValueError('源码链接缺失或越界: ' + relative)
                hashes[relative] = hashlib.sha256(os.readlink(path).encode()).hexdigest()
        return blobs, hashes
    u.source_maps = source_maps
    return u

def qualification(u, verification_control):
    for name, pin in read(HERE / 'asset-pins.json').items():
        if sha(HERE / name) != pin:
            raise ValueError('筛选资产变化: ' + name)
    manifest = read(HERE / 'base-source-manifest.json')
    if manifest['commit'] != u.COMMIT or manifest['tree'] != '8671e2ec040601981d1533d6a09beb20b9e507db':
        raise ValueError('当前PR25缓存修复基线身份不符')
    blobs = {p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in manifest['files'].items()}
    hashes = {p:v['sha256'] for p,v in manifest['files'].items()}
    if u.source_maps(BASE) != (blobs, hashes):
        raise ValueError('当前526源码变化')
    proof = ROOT / 'framework/20261024T141536Z-pr25-cache-restart-recheck-control'
    state = read(proof / 'state.json')
    if not state.get('completed') or not state.get('database_restored') or not state['service_result']['completed']:
        raise ValueError('默认缓存重启和真实语义检查未通过')
    build = read(NATIVE_BUILD)
    library = Path(build['library'])
    log = NATIVE_BUILD.with_name('native-build.log')
    if (build['source_commit'] != '7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93'
            or build['source_tree'] != 'b37543afc3250b4bd9361a505eb9f932286667e6'
            or build['library_sha256'] != '14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
            or sha(library) != build['library_sha256'] or sha(log) != build['build_log_sha256']
            or not state['component_checks']['passed'] or state['component_checks']['gate'] != 9
            or state['component_checks']['cached_dispatch'] != 40):
        raise ValueError('新二进制/49组件门不符')
    for p,digest in build['source_sha256'].items():
        if hashes[p] != digest:
            raise ValueError('native构建源码不符: '+p)
    if sha(SEED_REFERENCE / 'database-after.sqlite') != SEED_SHA:
        raise ValueError('共同DB种子变化')
    candidate = read(HERE / 'source-manifest.json')
    if (candidate['base_commit'] != u.COMMIT or candidate['base_tree'] != manifest['tree']
            or candidate['tree'] != '350938b7dd507089e435b0bdc4b1980d9383567d' or candidate['source_count'] != 532):
        raise ValueError('候选不是冻结0bf9上的532来源')
    target_blobs = {p:dict(mode=v['mode'],sha=v['git_sha']) for p,v in candidate['files'].items()}
    target_hashes = {p:v['sha256'] for p,v in candidate['files'].items()}
    origin = verify_qualification(u, verification_control, target_blobs, target_hashes, candidate, build)
    return {'main': (BASE, blobs, hashes, manifest['tree']),
            'kv': (origin, target_blobs, target_hashes, candidate['tree'])}, (build, library, log)


def verify_qualification(u, control, blobs, hashes, candidate, build):
    control = Path(control)
    if control.is_symlink():
        raise ValueError('VERIFY1 control不可为symlink')
    control = control.resolve(strict=True)
    if not control.is_relative_to(ROOT / 'framework') or not control.name.endswith('-control'):
        raise ValueError('VERIFY1 control不在本实例framework')
    state = read(control / 'state.json')
    required = ('completed', 'database_restored', 'source_unchanged', 'native_unchanged')
    if (any(state.get(k) is not True for k in required) or state.get('driver_exit_code') != 0
            or (control / 'exit-code').read_text().strip() != '0'
            or state.get('base_commit') != candidate['base_commit'] or state.get('tree') != candidate['tree']
            or state.get('source_count') != 532 or state.get('seed_sha256') != SEED_SHA
            or Path(state['control']) != control):
        raise ValueError('当前532 VERIFY1尚未成功收尾或身份不同')
    origin = Path(state['source'])
    run = Path(state['run'])
    if run != control.with_name(control.name[:-len('-control')]) or run.is_symlink():
        raise ValueError('VERIFY1 run/control对应关系不符')
    for root in (origin, control / 'plugin-source'):
        if u.source_maps(root) != (blobs, hashes):
            raise ValueError('已验532源码发生变化: ' + str(root))
    if read(control / 'source-git-blobs.json') != blobs or read(control / 'source-sha256.json') != hashes:
        raise ValueError('VERIFY1源码登记并非532')
    for name, pin in read(HERE / 'verification-asset-pins.json').items():
        if sha(control / name) != pin:
            raise ValueError('VERIFY1资格资产不同: ' + name)
    coverage = read(control / 'coverage.json')
    model = read(run / 'model-path/semantic-validation.json')
    graph = read(run / 'model-path/graph-evidence.json')
    if (state.get('coverage') != coverage or coverage.get('valid') is not True
            or coverage.get('status') != 'passed_main0bf9_swap_verify1_mechanism'
            or state.get('model_path') != model or model.get('valid') is not True
            or model.get('correct') != 4 or model.get('native_layers') != list(range(4, 38))
            or graph['graph']['layers'] != model['native_layers']
            or graph['graph_sha256'] != model['graph_sha256']
            or graph['fingerprint'] != model['fingerprint']
            or model['fingerprint'].get('native_enabled') is not True
            or sha(run / 'model-path/cache-evidence/computation_graph.py') != model['graph_sha256']):
        raise ValueError('当前同服务字节/语义/34层真实图资格不完整')
    receipt = read(control / 'native/runtime-receipt.json')
    for name in ('source_commit', 'source_tree', 'library_sha256', 'source_sha256', 'abi'):
        if receipt.get(name) != build[name]:
            raise ValueError('VERIFY1 native构建身份不同: ' + name)
    if sha(Path(receipt['runtime_library'])) != build['library_sha256']:
        raise ValueError('VERIFY1 runtime SO发生变化')
    scope = coverage['pr24_binding_scope']
    if (scope.get('library_sha256') != build['library_sha256'] or scope.get('source_tree') != build['source_tree']
            or scope.get('native_methods_identity') is not True or scope.get('q_kernel_binding_identity') is not True
            or scope.get('pid') != coverage['engine_pid'] or scope.get('quantized_layers') != 34):
        raise ValueError('VERIFY1实际native/Q绑定不符')
    return origin


def verify_result(run, control, verification_control, native):
    spec = importlib.util.spec_from_file_location('unchanged_verify0', HERE / 'verify_transactions.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    result = checker.verify_run(run, control)
    result['verification_control'] = str(verification_control)
    result['limits'] = [line for line in result['limits'] if '20261024T122225Z' not in line]
    result['limits'].append('当前532字节/真实模型资格见verification_control；旧检查器来源仅为算法复用，不是本组合资格。')
    result['gain_calculated'] = False
    log = (run / 'server.log').read_text(errors='replace')
    scopes = [json.loads(line.split('BIV150_KV_PR24_SCOPE ', 1)[1])
              for line in log.splitlines() if 'BIV150_KV_PR24_SCOPE ' in line]
    if len(scopes) != 1 or result['engine_pids'] != [scopes[0]['pid']]:
        raise ValueError('完整负载与单Engine native scope未对应')
    scope = scopes[0]
    if (scope.get('library_sha256') != native[0]['library_sha256']
            or scope.get('source_tree') != native[0]['source_tree']
            or scope.get('native_methods_identity') is not True or scope.get('q_kernel_binding_identity') is not True
            or scope.get('quantized_layers') != 34
            or any(marker in log for marker in ('BIV150_Q_FRAGMENT_FALLBACK', 'BIV150_COMPUTE_ORDER_SCOPE_REJECTED', 'BIV150_KV_PR24_SCOPE_REJECTED'))):
        raise ValueError('本轮native/Q/P身份或fallback不符')
    q_rows = []
    for line in log.splitlines():
        if 'BIV150_Q_FRAGMENT_SELECTED ' not in line:
            continue
        prefix, payload = line.split('BIV150_Q_FRAGMENT_SELECTED ', 1)
        owner = re.search(r'EngineCore[^\s()]* pid=(\d+)', prefix)
        value = json.loads(payload)
        if owner is not None and int(owner.group(1)) == scope['pid'] and value.get('mode') == 'selected':
            q_rows.append(value)
    if not q_rows:
        raise ValueError('本轮同Engine Q实际SELECTED缺失')
    after_ready = log.rsplit('Application startup complete.', 1)[1] if 'Application startup complete.' in log else ''
    result.update(native_binding_scope=scope, q_selected_records=q_rows,
                  p_status='observed_selected' if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' in after_ready else 'not_observed',
                  native_execution_per_request_asserted=False)
    write(control / 'transactions.json', result)
    if result['passed_verify0_checks'] is not True:
        raise ValueError('VERIFY0事务后验未通过；保留原件，不自动重跑')
    return result


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

def run_role(u, role, inputs, native, verification_control):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    run = ROOT / 'official' / (stamp + '-main0bf9-' + role + '-official-four-rounds')
    control = run.with_name(run.name + '-control')
    source = ROOT / 'code' / (stamp + '-main0bf9-' + role + '-official')
    origin, blobs, hashes, tree = inputs
    control.mkdir(exist_ok=False)
    shutil.copytree(origin, source, symlinks=True, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if u.source_maps(source) != (blobs, hashes):
        raise ValueError('新独立源码复制不符')
    shutil.copytree(source, control / 'plugin-source', symlinks=True)
    write(control / 'source-git-blobs.json', blobs)
    write(control / 'source-sha256.json', hashes)
    shutil.copyfile(__file__, control / Path(__file__).name)
    for name in ('driver.py', 'official-driver.source.py', 'graph_gate.py', 'cache_gate.py',
                 'verify_transactions.py', 'summarize_official_transactions.source.py',
                 'source-manifest.json', 'base-source-manifest.json', 'verification-asset-pins.json'):
        shutil.copyfile(HERE / name, control / name)
    write(control / 'verification-reference.json', dict(control=str(verification_control),
        files={name:sha(verification_control / name) for name in
               ('state.json', 'coverage.json', 'source-sha256.json', 'source-git-blobs.json', 'native/runtime-receipt.json')}))
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
    env.pop('VLLM_CACHE_ROOT', None)
    env.pop('TORCHINDUCTOR_CACHE_DIR', None)
    env['VLLM_DISABLE_COMPILE_CACHE'] = '0'
    env.update(BIV150_KV_VERIFY_RESTORE='0', BIV150_NATIVE_W8A8_LIBRARY=str(runtime),
               BIV150_RESUME_NATIVE_RECEIPT=str(receipt), BIV150_RESUME_NATIVE_RECEIPT_SHA256=sha(receipt))
    (control / 'q-hoist-artifacts').mkdir()
    env['BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR'] = str(control / 'q-hoist-artifacts')
    write(control / 'environment-overrides.json', {k:v for k,v in env.items() if k.startswith(('BIV150_', 'VLLM_FL_BIV150_')) or k == 'VLLM_DISABLE_COMPILE_CACHE'})
    command = ['python3', str(HERE / 'driver.py'), str(run), '--source-dir', str(source), '--role', role,
               '--verification-control', str(verification_control), '--database', str(DATABASE)]
    (control / 'command.txt').write_text(shlex.join(command) + '\n')
    state = dict(owner_pid=os.getpid(), role=role, run=str(run), control=str(control), source=str(source),
                 base_commit=u.COMMIT, tree=tree, source_count=len(blobs), completed=False,
                 verification_control=str(verification_control),
                 benchmark_kind='原官方两档各四轮，保留原runs2-4汇总及首轮原件', seed_sha256=SEED_SHA,
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
        seed = SEED_REFERENCE / 'database-after.sqlite'
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
                or result.get('benchmark_completed') is not True or result.get('cleanup_errors')
                or result.get('validation', {}).get('complete') is not True
                or 'monitor_final_returncode' not in result):
            raise RuntimeError('原官方四轮未成功完成；保留原件')
        state['observations'] = observe(run)
        state['result'] = result
        state['model_path'] = read(run / 'model-path/evidence.json')
        if state['model_path'].get('valid') is not True:
            raise ValueError('本服务实际图未通过')
        if role == 'kv':
            state['transactions'] = verify_result(run, control, verification_control, native)
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
                for path in [run / 'server.pid', run / 'monitor.pid', run / 'benchmark.pid']:
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
    global BASE
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-source', required=True, type=Path)
    parser.add_argument('--verification-control', type=Path, required=True)
    args = parser.parse_args()
    BASE = args.base_source
    u = helper()
    verification_control = args.verification_control.resolve(strict=True)
    results = []
    for role in ('main', 'kv'):
        sources, native = qualification(u, args.verification_control)
        results.append(run_role(u, role, sources[role], native, verification_control))
    print(json.dumps({'completed_roles': [s['role'] for s in results], 'controls': [s['control'] for s in results]}), flush=True)

if __name__ == '__main__':
    main()
