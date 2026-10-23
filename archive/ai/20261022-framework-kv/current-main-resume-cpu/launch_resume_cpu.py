"""当前446加两路径纯CPU抢占/恢复观察，交原bc51单次longscreen；无profiler。"""
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
ROOT = Path('/workspace/experiments/minicpm-s2')
REFERENCE_NAME = '20261023T141159Z-current-main-compute-order-context16k'
REFERENCE = ROOT / 'framework' / REFERENCE_NAME
CONTROL = REFERENCE.with_name(REFERENCE_NAME + '-control')
SOURCE = ROOT / 'code/current-main-compute-order-3283672b-20261023T141159Z'
COMMIT = '3283672b92fa30f93f652b242193999836a95f88'
TREE = '5c77e68caff6aa0c8b6c230adb78a2d4c293cca1'
BLOBS_SHA = '340e2ce1254510864d2b8b8d90939a98622f70a28f10573f9a887eebface106e'
MANIFEST_SHA = '0b17b3a18fc89a3968f409d9e340190a19ffd4e7aadec3f456293f91281f4ec4'
LAUNCH_SHA = '88b35410fc49d1d259ebad0cc910c623a5cea2723220707932e38544f3c89e02'
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


def reference_ready():
    if sha(HERE / 'candidate-git-blobs.json') != BLOBS_SHA or sha(HERE / 'candidate-manifest.json') != MANIFEST_SHA:
        raise ValueError('冻结候选身份材料变化')
    expected, manifest = read(HERE / 'candidate-git-blobs.json'), read(HERE / 'candidate-manifest.json')
    if (len(expected) != 446 or manifest['base_commit'] != COMMIT
            or manifest['target_tree'] != TREE or manifest['target_blob_count'] != 446):
        raise ValueError('非冻结current-main+P完整446树')
    if (REFERENCE / 'exit-code').read_text().strip() != '0':
        raise ValueError('141159短测未成功结束')
    purpose, post = read(CONTROL / 'purpose.json'), read(REFERENCE / 'postflight-full.json')
    if (purpose['source'] != str(SOURCE) or purpose['commit'] != COMMIT or purpose['tree'] != TREE
            or purpose['source_count'] != 446 or post['source_count'] != 446
            or post['source_failures'] or post['query'].strip() != '68, 0'
            or not all(post['ports_closed'].values())
            or not all(value is None or '\nState:\tZ ' in value for value in post['owned_process_status'].values())):
        raise ValueError('短测源码/清理后态不完整')
    if (sha(CONTROL / 'launch_compute_order_main.py') != LAUNCH_SHA
            or sha(CONTROL / 'candidate-manifest.json') != MANIFEST_SHA
            or read(CONTROL / 'source-git-blobs.json') != expected):
        raise ValueError('受测control身份不符')
    hashes = read(CONTROL / 'source-sha256.json')
    if SOURCE.is_symlink() or source_maps(SOURCE) != (expected, hashes) or source_maps(CONTROL / 'plugin-source') != (expected, hashes):
        raise ValueError('受测完整源码/Git blobs/mode/内容已变化')
    log = (REFERENCE / 'server.log').read_text(errors='replace')
    selected, normalized = set(), set()
    for line in log.splitlines():
        pid = re.search(r'EngineCore pid=(\d+)', line)
        if not pid:
            continue
        if 'BIV150_COMPUTE_ORDER_FIRST_SELECTED ' in line:
            item = json.loads(line.split('BIV150_COMPUTE_ORDER_FIRST_SELECTED ', 1)[1])
            if (item.get('pid') == int(pid.group(1)) and item.get('original_model_forward_returned') is True
                    and item.get('runtime_mode') == 'NONE' and item.get('sampler_rows') == item.get('N')
                    and item.get('outside', 0) > 0):
                selected.add(int(pid.group(1)))
        if 'BIV150_PREFILL_NORMALIZATION_SELECTED ' in line:
            normalized.add(int(pid.group(1)))
    if len(selected) != 1 or not selected.issubset(normalized) or 'BIV150_COMPUTE_ORDER_SCOPE_REJECTED ' in log:
        raise ValueError('短测缺同Engine真实P/normalization命中或有scope拒绝')
    return expected, hashes, sorted(selected)


OBSERVER_MANIFEST_SHA = '64e819251918ea03be2965d9ec86f6140aa0de47800f762191dfb97c18b93c21'
OBSERVER_TREE = 'cd50086ea3dd618c890533bc37e6637888b6dbf5'
OBSERVER_PINS = {'vllm_fl/__init__.py': 'd7c3dbed639d77e766f072a04816835d39199f374cb7bee7bdd7c5b3b5b7a781', 'vllm_fl/patches/biv150_resume_cpu_observer.py': '0268b058718722874d3706db3bd9ecd3d424b1f94687a1ec0eb2191603011ca1'}


def prepare_source(stamp, blobs, hashes):
    raw = (HERE / 'observer-manifest.json').read_bytes()
    manifest = json.loads(raw)
    if (hashlib.sha256(raw).hexdigest() != OBSERVER_MANIFEST_SHA
            or manifest['base_tree'] != TREE or manifest['source_count'] != 447):
        raise ValueError('observer两路径身份变化')
    source = ROOT / 'code' / ('current-main-resume-cpu-' + stamp)
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
        raise ValueError('不是current446仅init/observer变化')
    shutil.copytree(SOURCE, source, symlinks=True, ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','*.pyo'))
    for name, data in payload.items():
        target = source / name
        if target.is_symlink():
            raise ValueError('不覆写payload symlink')
        target.write_bytes(data)
        target.chmod(0o644)
    actual_blobs, actual_hashes = source_maps(source)
    if (len(actual_blobs) != 447 or actual_blobs != expected
            or {k:v for k,v in actual_hashes.items() if k not in payload}
                != {k:v for k,v in hashes.items() if k not in payload}
            or source_maps(SOURCE) != (blobs, hashes)):
        raise ValueError('原446或新447出现未声明变更')
    return source, actual_blobs, actual_hashes


def main():
    blobs, hashes, selected = reference_ready()
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    source, blobs, hashes = prepare_source(stamp, blobs, hashes)
    for name, pin in SCRIPTS.items():
        if sha(ROOT / 'scripts' / name) != pin:
            raise ValueError('原准确率owner/评测/快照/monitor变化：' + name)
    env = os.environ.copy()
    removed = [name for name in env if name.startswith('BIV150_') or name in
               ('MINICPM_NATIVE_PROFILE_EVENTS', 'MINICPM_DECODE_GAP_RUN_DIR')]
    for name in removed:
        env.pop(name)
    env['BIV150_RESUME_CPU_OBSERVE'] = '1'
    for name in ('VLLM_FL_BIV150_PREFILL_NORMALIZE', 'VLLM_FL_BIV150_GQA_DECODE'):
        if env.get(name, '1') != '1':
            raise ValueError('不允许关闭受测normalized/GQA：' + name)
    run = ROOT / 'framework' / (stamp + '-current-main-resume-cpu-context16k-long')
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
    shutil.copyfile(__file__, control / 'launch_resume_cpu.py')
    save(control / 'reference-short-screen.json', dict(run=REFERENCE_NAME, source=str(SOURCE),
        selected_engine_pids=selected, source_count=446, candidate_tree=TREE,
        postflight_sha256=sha(REFERENCE / 'postflight-full.json'), server_log_sha256=sha(REFERENCE / 'server.log')))
    save(control / 'purpose.json', dict(kind='当前446原路单RID抢占/恢复CPU因果诊断，无profiler/收益结论',
        source=str(source), source_count=447, base_commit=COMMIT, base_tree=TREE, tree=OBSERVER_TREE,
        reference_short_screen=REFERENCE_NAME, removed_environment_names=sorted(removed),
        limits=['原446仅init+observer，runner/P/normalized字节不变，无KV策略/传输',
            '原bc51 context-long-screen/32x16K+1024/seed721201/SERVER/锁/到达/采样不变',
            '仅实际CPU提交/原execute返回，GPU完成/重算耗时未知；最多16target片段，未覆盖不补跑']))
    command = ['python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(source),
        '--context-long-screen', '--seed', '721201', '--require-log-marker', 'BIV150_RESUME_CPU_OBSERVER_CORE_HOOKED']
    quota_root=Path('/sys/fs/cgroup/cpu,cpuacct')
    quota={name:(quota_root/name).read_text() for name in ('cpu.cfs_quota_us','cpu.cfs_period_us','cpu.stat')}
    if int(quota['cpu.cfs_quota_us']) != 6*int(quota['cpu.cfs_period_us']):
        raise ValueError('不是当前6CPU quota，拒绝静默改变条件')
    save(control / 'cpu-before.json', quota)
    import socket
    ports={}
    for family,host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
        with socket.socket(family,socket.SOCK_STREAM) as sock:
            sock.settimeout(2);ports[host]=sock.connect_ex((host,9031)) != 0
    gpu=subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
    gpu_table=subprocess.check_output(['/usr/local/corex-4.5.0/bin/ixsmi'],text=True)
    save(control / 'preflight.json', dict(ports_closed=ports,gpu=gpu,ixsmi=gpu_table,under_device_lock=False))
    if not all(ports.values()) or gpu.strip() != '68, 0' or 'No running processes found' not in gpu_table:
        raise RuntimeError('当前卡/端口非严格空闲；原bc51仍是唯一锁owner')
    shutil.copyfile(ROOT / 'scripts/snapshot_tuning_db.py',control / 'snapshot_tuning_db.py')
    with (control / 'db-before.log').open('x') as output:
        subprocess.run(['python3',str(control / 'snapshot_tuning_db.py'),'--database',
            '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db','--output',str(control / 'db-before')],
            stdout=output,stderr=subprocess.STDOUT,check=True)
    (control / 'command.txt').write_text(shlex.join(command) + '\n', encoding='utf-8')
    save(control / 'scripts-sha256.json', SCRIPTS)
    with (control / 'runner.log').open('x') as log:
        process = subprocess.Popen(command, cwd='/workspace', env=env, stdin=subprocess.DEVNULL,
            stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    (control / 'runner.pid').write_text(str(process.pid) + '\n')
    print(json.dumps(dict(run=str(run), control=str(control), source=str(source), runner_pid=process.pid)))


if __name__ == '__main__':
    main()
