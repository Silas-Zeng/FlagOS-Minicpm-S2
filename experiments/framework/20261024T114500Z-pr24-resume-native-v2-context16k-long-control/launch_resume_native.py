"""PR24首次恢复窗口native诊断；同源nativeSO、固定warmed DB、单driver。"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
SEED_PATH = Path('/workspace/experiments/minicpm-s2/framework/20261024T110545Z-current-main-pr24-resume-cpu-context16k-long-control/database-after-recovery.sqlite')
SEED_SHA = '8acaab58dbfabc950eb7a4c84a6088f9676870b561a62d3fc8621012c79bead6'
DRIVER_SHA = 'c0e163524a0ebb4fa1dcf84b0f61103f4e8a4fa593394ba20c7aca30d967f79b'
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMIT = '1ad9a708ee77323372f0fa5975a04a52d294852c'
TREE = 'd1a96e3f56723956a7902cba7e676fd285c83d0c'
BASE_COUNT = 467
TARGET_COUNT = 468
BLOBS_SHA = '2859052a2ffa80a217ae15c88e52e1507c2de47b431b71f56b6218ee57d7ff8d'
MANIFEST_SHA = '6db1717c9c9557404111e11bb6a422f0200c8bf50a98d72138fa264cafc7fd12'
SCRIPTS = {'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9', 'run_diagnostic_load.sh': '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378', 'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2', 'monitor_gpu.sh': 'af90002eebd4dade188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def source_maps(source):
    # 复用已审owner的Git link文字/mode及常规目标内容SHA两种身份。
    blobs, hashes = {}, {}
    for path in sorted(source.rglob('*')):
        relative = path.relative_to(source)
        if any(x in ('.git', '__pycache__') for x in relative.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            if not path.resolve(strict=True).is_relative_to(source):
                raise ValueError('source symlink越界')
            data, mode = os.readlink(path).encode(), '120000'
        elif path.is_file():
            data, mode = path.read_bytes(), '100755' if path.stat().st_mode & 0o111 else '100644'
        else:
            continue
        digest = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        blobs[relative.as_posix()] = dict(mode=mode, sha=digest)
        hashes[relative.as_posix()] = sha(path)
    return blobs, hashes


def source_ready(source):
    if source.is_symlink() or not source.resolve().is_relative_to(ROOT / 'code'):
        raise ValueError('main源码必须是本实验code下独立真实目录')
    if sha(HERE / 'candidate-git-blobs.json') != BLOBS_SHA or sha(HERE / 'candidate-manifest.json') != MANIFEST_SHA:
        raise ValueError('冻结main身份材料变化')
    expected, manifest = read(HERE / 'candidate-git-blobs.json'), read(HERE / 'candidate-manifest.json')
    hashes = manifest['source_sha256']
    if (len(expected) != BASE_COUNT or manifest['base_commit'] != COMMIT
            or manifest['target_tree'] != TREE or manifest['target_blob_count'] != BASE_COUNT
            or source_maps(source) != (expected, hashes)):
        raise ValueError('并非冻结PR24完整Git源码；拒绝附带build产物')
    return expected, hashes


def native_ready(path, source_hashes):
    manifest = read(path)
    if manifest['source_commit'] != COMMIT or manifest['source_tree'] != TREE:
        raise ValueError('native构建来自其它commit/tree')
    for relative in ('csrc/iluvatar/native_w8a8.cpp', 'csrc/iluvatar/native_w8a8.cu',
                     'tools/build_biv150_native_w8a8.py'):
        if manifest['source_sha256'].get(relative) != source_hashes[relative]:
            raise ValueError('native构建源码不符: ' + relative)
    library, build_log = Path(manifest['library']), Path(manifest['build_log'])
    if (not library.is_absolute() or library.is_symlink() or not build_log.is_absolute()
            or sha(library) != manifest['library_sha256'] or sha(build_log) != manifest['build_log_sha256']
            or library.read_bytes()[:4] != b'\x7fELF' or manifest.get('exit_code') != 0
            or not manifest.get('build_command') or not manifest.get('compiler')
            or not isinstance(manifest.get('abi'), dict)
            or not manifest['abi'].get('torch_version')
            or type(manifest['abi'].get('cxx11_abi')) is not bool):
        raise ValueError('缺完整native构建/ELF/ABI/日志凭据')
    control = path.parent
    state, summary, checks = read(control / 'state.json'), read(control / 'summary.json'), read(control / 'operator-check.json')
    if ((control / 'exit-code').read_text().strip() != '0' or state.get('completed') is not True
            or state.get('database_restored') is not True or state.get('source_unchanged') is not True
            or summary.get('coverage') is not True or summary.get('source_commit') != COMMIT
            or summary.get('source_tree') != TREE or summary.get('library_sha256') != manifest['library_sha256']
            or summary['result'].get('completed') != 32 or summary['result'].get('failed') != 0
            or len(checks['records']) != 9 or not all(r.get('passed') is True for r in checks['records'])
            or checks.get('original_weight_fallback_unchanged') is not True):
        raise ValueError('本实例PR24九项+32请求/PQ/native接入或清理未完成；不继承其它实例')
    return manifest, library, build_log


def idle():
    import socket
    ports = {}
    for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            sock.settimeout(2)
            ports[host] = sock.connect_ex((host, 9031)) != 0
    query = subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
    table = subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi'], text=True)
    result = dict(ports_closed=ports, gpu=query, ixsmi=table)
    if not all(ports.values()) or query.strip() != '68, 0' or 'No running processes found' not in table:
        raise RuntimeError('当前卡/9031不空闲，拒绝启动或恢复DB')
    return result


def owned_group(pid):
    members, errors = [], []
    for proc in Path('/proc').iterdir():
        if not proc.name.isdigit():
            continue
        try:
            raw = (proc / 'stat').read_text()
            fields = raw[raw.rindex(')') + 2:].split()
            if int(fields[2]) == pid or int(fields[3]) == pid:
                members.append(dict(pid=int(proc.name), state=fields[0], pgrp=int(fields[2]), session=int(fields[3])))
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, ValueError, IndexError) as error:
            errors.append(dict(pid=proc.name, error_type=type(error).__name__))
    return dict(owner_pid=pid, members=members, errors=errors)


def verify_coverage(control, run):
    log = (run / 'server.log').read_text(errors='replace')
    after_ready = log.rsplit('Application startup complete.', 1)[1] if 'Application startup complete.' in log else ''
    selected = [json.loads(line.split('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', 1)[1])
                for line in after_ready.splitlines() if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' in line]
    p_actual = any(row.get('original_model_forward_returned') is True
        and row.get('runtime_mode') == 'NONE' and row.get('outside', 0) > 0
        and row.get('inverse_logits_order') == 'original_request_rows'
        and row.get('sampler_rows') == row.get('N') for row in selected)
    marker_names = ['BIV150_NATIVE_W8A8_FIRST_WEIGHT', 'BIV150_Q_FRAGMENT_SELECTED',
                    'BIV150_RESUME_NATIVE_ARMED', 'BIV150_Q_FRAGMENT_FALLBACK',
                    'BIV150_COMPUTE_ORDER_SCOPE_REJECTED']
    markers = {name: name in log for name in marker_names}
    scopes = [json.loads(line.split('BIV150_RESUME_NATIVE ', 1)[1]) for line in log.splitlines()
              if 'BIV150_RESUME_NATIVE ' in line]
    native_scope = [row for row in scopes if row.get('event') == 'PR24_NATIVE_SCOPE']
    validation = read(run / 'native-validation.json')
    valid = bool(p_actual and all(markers[name] for name in marker_names[:3])
        and not any(markers[name] for name in marker_names[3:])
        and len(native_scope) == 1 and native_scope[0].get('native_methods_identity') is True
        and native_scope[0].get('q_kernel_binding_identity') is True
        and not any(row.get('event') == 'SCOPE_REJECTED' for row in scopes)
        and validation.get('valid') is True
        and validation['stops'][0].get('reason') == 'reached_preempt_CPU_known_length_not_completion_floor')
    save(control / 'coverage.json', dict(valid=valid, p_actual=p_actual, p_after_ready=selected,
        markers=markers, native_scope=native_scope, native_validation=validation,
        limits=['仅诊断；窗口包含同批其它请求，GPU kernel并非全可省',
                '八步截断/无恢复不自动复跑；冷调优另按轨迹判断，不作为收益']))
    if not valid:
        raise RuntimeError('当前P/Q/native或完整恢复窗口未命中；不自动重跑')


def run_owned(control, run, command, env, source, blobs, hashes):
    # bc51保持唯一GPU driver；外层仅交接同一设备锁，负责DB与原件收尾。
    import fcntl
    import traceback
    import time
    database = Path('/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db')
    lock = (ROOT / 'framework-device.lock').open('a')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    state = dict(owner_pid=os.getpid(), run=str(run), control=str(control), source=str(source),
                 source_count=TARGET_COUNT, base_commit=COMMIT, tree=OBSERVER_TREE, completed=False)
    backup, original, process, success = control / 'database-original.sqlite', None, None, False
    def state_save():
        (control / 'state.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n')
    try:
        save(control / 'preflight.json', dict(**idle(), under_device_lock=True))
        shutil.copy2(database, backup)
        original = sha(backup)
        state['database_original_sha256'] = original
        if SEED_PATH.is_symlink() or sha(SEED_PATH) != SEED_SHA:
            raise ValueError('固定warmed DB原件不符')
        shutil.copy2(SEED_PATH, control / 'database-seed.sqlite')
        shutil.copy2(SEED_PATH, database)
        if sha(database) != SEED_SHA or sha(control / 'database-seed.sqlite') != SEED_SHA:
            raise ValueError('warmed DB复制后不符')
        state.update(database_before_sha256=SEED_SHA, database_seed=str(SEED_PATH))
        shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py', control / 'snapshot_tuning_db.py')
        with (control / 'db-before.log').open('x') as output:
            subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database', str(database),
                '--output', str(control / 'db-before')], stdout=output, stderr=subprocess.STDOUT, check=True)
        (control / 'command.txt').write_text(shlex.join(command) + '\n')
        save(control / 'scripts-sha256.json', SCRIPTS)
        fcntl.flock(lock, fcntl.LOCK_UN)
        with (control / 'runner.log').open('x') as log:
            process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        (control / 'runner.pid').write_text(str(process.pid) + '\n')
        state.update(runner_pid=process.pid, stage='bc51-running')
        state_save()
        print(json.dumps(state), flush=True)
        code = process.wait()
        state.update(runner_exit_code=code, stage='cleanup')
        if code != 0 or (run / 'exit-code').read_text().strip() != '0':
            raise RuntimeError('bc51未成功结束；保存失败原件')
        verify_coverage(control, run)
        success = True
    except BaseException as error:
        state['error'] = repr(error)
        (control / 'failure.txt').write_text(traceback.format_exc())
        raise
    finally:
        cleanup_ok = True
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state['postflight'] = idle()
            if process is not None:
                group = owned_group(process.pid)
                deadline = time.monotonic() + 3.0
                samples = [group]
                while not group['errors'] and any(x['state'] != 'Z' for x in group['members']) and time.monotonic() < deadline:
                    time.sleep(min(0.2, max(0, deadline - time.monotonic())))
                    group = owned_group(process.pid)
                    samples.append(group)
                save(control / 'owner-process-group-grace.json', dict(max_seconds=3, samples=samples))
                state['postflight_after_grace'] = idle()
                save(control / 'owner-process-group.json', group)
                if group['errors'] or any(x['state'] != 'Z' for x in group['members']):
                    raise RuntimeError('本次bc51进程组未清理，保留DB原件不恢复')
            if original is not None:
                with (control / 'db-after.log').open('x') as output:
                    subprocess.run(['python3', str(control / 'snapshot_tuning_db.py'), '--database', str(database),
                        '--output', str(control / 'db-after')], stdout=output, stderr=subprocess.STDOUT, check=True)
                shutil.copy2(database, control / 'database-after.sqlite')
                shutil.copy2(backup, database)
                state['database_restored'] = sha(database) == original
                if not state['database_restored']:
                    raise RuntimeError('DB恢复后hash不符')
        except Exception as error:
            cleanup_ok = False
            state.update(cleanup_error=repr(error), database_backup=str(backup))
        try:
            if source_maps(source) != (blobs, hashes) or source_maps(control / 'plugin-source') != (blobs, hashes):
                raise RuntimeError('诊断结束源码身份变化')
            state['source_unchanged'] = True
            if sha(control / 'native/biv150_native_w8a8.so') != read(control / 'native/runtime-receipt.json')['library_sha256']:
                raise RuntimeError('诊断结束native库变化')
            state['native_unchanged'] = True
        except Exception as error:
            cleanup_ok = False
            state['source_error'] = repr(error)
        state.update(completed=success and cleanup_ok, finished_utc=datetime.now(timezone.utc).isoformat())
        state_save()
        (control / 'exit-code').write_text('0\n' if success and cleanup_ok else '1\n')
        lock.close()
        if not cleanup_ok:
            raise RuntimeError('收尾未完成；参见state.json及保留的DB备份')




OBSERVER_MANIFEST_SHA = 'b3b976063c6ed6bc4ea11e419d103434fdff823762d9f580c583bfb4fc86c9fd'
OBSERVER_TREE = '347e4947540422713583cd9839d7f5a1efa6089c'
OBSERVER_PINS = {'vllm_fl/__init__.py': '1f094fa127d4a266f2617b0a1ec09c96485f177f51f1951d0718cb244ece72b2', 'vllm_fl/patches/biv150_resume_native_observer.py': '07cdcefe3a1f5384c5355e4250d47b75d44c9c222e07cabe56bdf7e9be9d7e0b'}


def prepare_source(stamp, blobs, hashes, base_source):
    raw = (HERE / 'observer-manifest.json').read_bytes()
    manifest = json.loads(raw)
    if (hashlib.sha256(raw).hexdigest() != OBSERVER_MANIFEST_SHA
            or manifest['base_tree'] != TREE or manifest['source_count'] != TARGET_COUNT):
        raise ValueError('observer两路径身份变化')
    source = ROOT / 'code' / ('pr24-resume-native-v2-' + stamp)
    if source.exists():
        raise FileExistsError(source)
    expected = dict(blobs)
    payload = {}
    for name, pin in OBSERVER_PINS.items():
        data = (HERE / 'files' / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != pin:
            raise ValueError('observer payload变化：' + name)
        payload[name] = data
        expected[name] = dict(mode='100644', sha=hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest())
    delta = {name: dict(before=blobs.get(name), after=expected[name], sha256=hashlib.sha256(data).hexdigest())
             for name, data in payload.items()}
    if manifest['changed_paths'] != delta or manifest['target_tree'] != OBSERVER_TREE:
        raise ValueError('不是PR24 main仅init/observer变化')
    shutil.copytree(base_source, source, symlinks=True, ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    for name, data in payload.items():
        target = source / name
        if target.is_symlink():
            raise ValueError('不覆写payload symlink')
        target.write_bytes(data)
        target.chmod(0o644)
    actual_blobs, actual_hashes = source_maps(source)
    if (len(actual_blobs) != TARGET_COUNT or actual_blobs != expected
            or {k:v for k,v in actual_hashes.items() if k not in payload}
                != {k:v for k,v in hashes.items() if k not in payload}
            or source_maps(base_source) != (blobs, hashes)):
        raise ValueError('原PR24或新468出现未声明变更')
    return source, actual_blobs, actual_hashes


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--native-build-manifest', type=Path, required=True)
    args = parser.parse_args()
    base_source = args.source_dir
    blobs, hashes = source_ready(base_source)
    native, library, build_log = native_ready(args.native_build_manifest, hashes)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    source, blobs, hashes = prepare_source(stamp, blobs, hashes, base_source)
    for name, pin in SCRIPTS.items():
        if sha(ROOT / 'scripts' / name) != pin:
            raise ValueError('原bc51/负载/快照/monitor变化：' + name)
    env = os.environ.copy()
    removed = [name for name in env if name.startswith('BIV150_') or name in
               ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR')]
    for name in removed:
        env.pop(name)
    env['BIV150_RESUME_NATIVE_OBSERVE'] = '1'
    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE', 'VLLM_FL_BIV150_GQA_DECODE', 'VLLM_FL_BIV150_Q_FRAGMENT', 'VLLM_FL_BIV150_NATIVE_W8A8'):
        if env.get(name, '1') != '1':
            raise ValueError('不允许关闭受测normalized/GQA：' + name)
    run = ROOT / 'framework' / (stamp + '-pr24-resume-native-v2-context16k-long')
    control = run.with_name(run.name + '-control')
    if run.exists():
        raise FileExistsError(run)
    control.mkdir(parents=True, exist_ok=False)
    shutil.copytree(source, control / 'plugin-source', symlinks=True,
                    ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    if source_maps(source) != (blobs, hashes) or source_maps(control / 'plugin-source') != (blobs, hashes):
        raise ValueError('归档期间源码变化')
    save(control / 'source-sha256.json', hashes)
    save(control / 'source-git-blobs.json', blobs)
    for name in ('candidate-git-blobs.json', 'candidate-manifest.json', 'observer-manifest.json'):
        shutil.copyfile(HERE / name, control / name)
    shutil.copyfile(__file__, control / 'launch_resume_native.py')
    if sha(HERE / 'run_resume_native_screen.py') != DRIVER_SHA:
        raise ValueError('冻结native driver变化')
    shutil.copyfile(HERE / 'run_resume_native_screen.py', control / 'run_resume_native_screen.py')
    native_dir = control / 'native'
    native_dir.mkdir()
    runtime_library = native_dir / 'biv150_native_w8a8.so'
    shutil.copyfile(library, runtime_library)
    shutil.copyfile(build_log, native_dir / 'build.log')
    shutil.copyfile(args.native_build_manifest, native_dir / 'build-manifest.original.json')
    if (sha(runtime_library) != native['library_sha256']
            or sha(native_dir / 'build.log') != native['build_log_sha256']):
        raise ValueError('native复制后身份变化')
    receipt = dict(native, runtime_library=str(runtime_library))
    receipt_path = native_dir / 'runtime-receipt.json'
    save(receipt_path, receipt)
    env['BIV150_NATIVE_W8A8_LIBRARY'] = str(runtime_library)
    env['BIV150_RESUME_NATIVE_RECEIPT'] = str(receipt_path)
    env['BIV150_RESUME_NATIVE_RECEIPT_SHA256'] = sha(receipt_path)
    save(control / 'purpose.json', dict(kind='PR24首次恢复窗口native GPU诊断，非官方成绩或收益' ,
        source=str(source), source_count=TARGET_COUNT, base_source=str(base_source),
        base_commit=COMMIT, base_tree=TREE, tree=OBSERVER_TREE,
        removed_environment_names=sorted(removed), native_library_sha256=native['library_sha256'],
        limits=['完整PR24 main仅init+observer；P/Q/native原字节保留，无KV策略/传输',
            '旧native driver保持原bc51 32x16K+1024/seed721201/SERVER/锁/到达/采样，trace独立' ,
            '首个真实恢复q>1至known端点，8步上限，未覆盖不补跑；GPU轨迹包含同批其它请求' ,
            '新实例新main诊断不继承其它实例PR24容量/正确性/性能资格']))
    command = ['python3', str(control / 'run_resume_native_screen.py'), str(run), '--source-dir', str(source),
        '--context-long-screen', '--native-profile', '--seed', '721201', '--require-log-marker', 'BIV150_RESUME_NATIVE_CORE_HOOKED']
    quota_root=Path('/sys/fs/cgroup/cpu,cpuacct')
    quota={name:(quota_root/name).read_text() for name in ('cpu.cfs_quota_us','cpu.cfs_period_us','cpu.stat')}
    if int(quota['cpu.cfs_quota_us']) != 6*int(quota['cpu.cfs_period_us']):
        raise ValueError('不是当前6CPU quota，拒绝静默改变条件')
    save(control / 'cpu-before.json', quota)
    run_owned(control, run, command, env, source, blobs, hashes)



if __name__ == '__main__':
    main()
