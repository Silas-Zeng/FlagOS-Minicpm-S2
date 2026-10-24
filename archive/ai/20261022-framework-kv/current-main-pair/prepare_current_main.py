"""从固定本地Git对象导出完整main，不触碰checkout；生成原tar launcher的短服务副本。"""
import difflib
import gzip
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REPO = ROOT / 'collaboration/FlagOS-S2-vllm-plugin-FL'
COMMIT = '3283672b92fa30f93f652b242193999836a95f88'
TREE = 'a6e53d5219addc76700718880f86c33ab014b311'


def git(*args, data=None):
    return subprocess.run(['git', '-C', str(REPO), *args], input=data, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, check=True).stdout


def main():
    if git('rev-parse', COMMIT+'^{tree}').decode().strip() != TREE:
        raise ValueError('固定main tree不符')
    entries = []
    for raw in git('ls-tree', '-r', '-z', COMMIT).split(b'\0'):
        if not raw:
            continue
        header, path = raw.split(b'\t', 1)
        mode, kind, digest = header.decode().split()
        if kind != 'blob' or mode not in ('100644', '100755', '120000'):
            raise ValueError('不接受submodule/特殊Git条目')
        entries.append(dict(path=path.decode(), mode=mode, type=kind, sha=digest))
    digests = sorted({entry['sha'] for entry in entries})
    batch = git('cat-file', '--batch', data=('\n'.join(digests)+'\n').encode())
    objects, cursor = {}, 0
    for expected in digests:
        end = batch.index(b'\n', cursor)
        digest, kind, length = batch[cursor:end].decode().split()
        length = int(length)
        data = batch[end+1:end+1+length]
        if digest != expected or kind != 'blob' or batch[end+1+length:end+2+length] != b'\n':
            raise ValueError('Git batch对象不符')
        objects[digest] = data
        cursor = end+2+length
    if cursor != len(batch):
        raise ValueError('Git batch多余字节')
    timestamp = int(git('show', '-s', '--format=%ct', COMMIT))
    archive = io.BytesIO()
    prefix = 'current-main-3283672b/'
    with tarfile.open(fileobj=archive, mode='w', format=tarfile.PAX_FORMAT) as tar:
        for entry in entries:
            data = objects[entry['sha']]
            item = tarfile.TarInfo(prefix+entry['path'])
            item.mtime = timestamp
            item.mode = 0o755 if entry['mode']=='100755' else 0o644
            if entry['mode']=='120000':
                item.type, item.linkname = tarfile.SYMTYPE, data.decode()
                tar.addfile(item)
            else:
                item.size = len(data)
                tar.addfile(item, io.BytesIO(data))
    bundle = gzip.compress(archive.getvalue(), mtime=0)
    with (HERE/'current-main-3283672b.tar.gz').open('xb') as stream:
        stream.write(bundle)
    mapping = dict(sha=TREE, commit=COMMIT, truncated=False, tree=entries)
    rawmap = (json.dumps(mapping, indent=2)+'\n').encode()
    with (HERE/'main-tree.json').open('xb') as stream:
        stream.write(rawmap)
    bypath = {entry['path']: entry for entry in entries}
    runner = 'vllm_fl/worker/model_runner.py'
    helper = 'vllm_fl/patches/biv150_prefill_normalized.py'
    pins = dict(archive=hashlib.sha256(bundle).hexdigest(), mapping=hashlib.sha256(rawmap).hexdigest(),
        runner=hashlib.sha256(objects[bypath[runner]['sha']]).hexdigest(),
        helper=hashlib.sha256(objects[bypath[helper]['sha']]).hexdigest())
    original = (ROOT/'tmp/pr15-accuracy/launch_pr15_accuracy.py').read_text(encoding='utf-8')
    text = original
    edits = []
    def edit(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('launcher切口不唯一：'+old[:70])
        text = text.replace(old, new, 1)
        edits.append((old,new))
    edit('固定PR15源码包→原35d准确率owner；不改评测、不安装包或修改已有源码。',
         '固定当前main完整Git树→原bc51短服务；不改生产源、SERVER或准确率。')
    edit("COMMIT = '638c4ac0f07ed98e4476a5971c849630d9cdd580'",f'COMMIT = {COMMIT!r}')
    edit("BASE = '2b59d7612666452f7a1b8cca0f634af0b5e887b8'",f'BASE = {TREE!r}')
    edit("TREE = 'd6a9597c34c29d06613562a40a95b91f70eeb70f'",f'TREE = {TREE!r}')
    edit("ARCHIVE_SHA = 'a61e717f7d3623d558008d621e4e9b95b7c05f571e2191c79dd31541be44f25a'",f"ARCHIVE_SHA = {pins['archive']!r}")
    edit("MAP_SHA = '411f2a68b9220cc05a53719e1e8dd6c6d90171eb04303bbe7976b4ec7a2c2dcf'",f"MAP_SHA = {pins['mapping']!r}")
    edit("RUNNER_SHA = '195cc806a127ab4e43b6838aaee70ef70a4d8b2f02dd38df6f0e815374202b88'",f"RUNNER_SHA = {pins['runner']!r}")
    edit("HELPER = 'vllm_fl/patches/biv150_cpu_metadata.py'",f'HELPER = {helper!r}')
    edit("HELPER_SHA = '0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f'",f"HELPER_SHA = {pins['helper']!r}")
    old_scripts = original[original.index('SCRIPTS = {'):original.index('\n\n\ndef sha')]
    scripts = {
        'run_framework_screen.py': 'bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9',
        'run_diagnostic_load.sh': '621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378',
        'snapshot_tuning_db.py': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
        'monitor_gpu.sh': 'af90002eebd4dadE188c8efd58e025c3ce3cbcfa022a0e2d7a49fe2e8870f88a'.lower(),
    }
    edit(old_scripts, 'SCRIPTS = '+repr(scripts))
    start = text.index('    if len(entries) != 432')
    end = text.index('    return entries', start)
    edit(text[start:end], f"    if len(entries) != {len(entries)} or tree_oid(entries) != TREE or entries[RUNNER]['sha'] != {bypath[runner]['sha']!r}:\n        raise ValueError('当前main完整Git tree不符')\n")
    edit("default=ROOT / 'code/pr15-computed-h2d-638c4ac0'", "default=None")
    edit('    source = args.source_dir.resolve()\n',
         "    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')\n    source = (args.source_dir or ROOT / 'code' / ('current-main-baseline-3283672b-'+stamp)).resolve()\n")
    edit("status='fixed_PR15_tar_tree_verified_CPU_only'", "status='fixed_current_main_tar_tree_verified_CPU_only'")
    edit("    if source != ROOT / 'code/pr15-computed-h2d-638c4ac0' or source.exists():\n", "    if not source.is_relative_to(ROOT / 'code') or source.exists():\n")
    edit("    run = ROOT / 'accuracy' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-pr15-computed-h2d')\n", "    run = ROOT / 'framework' / (stamp + '-current-main-baseline-context16k')\n")
    edit("shutil.copyfile(__file__, control / 'launch_pr15_accuracy.py')", "shutil.copyfile(__file__, control / 'launch_current_main_baseline.py')")
    start = text.index("    save(control / 'purpose.json'")
    end = text.index("    (control / 'command.txt')",start)
    replacement = '''    save(control / 'purpose.json', dict(kind='当前main完整代码的独立短服务基线；不是新准确率或优化收益',
        source=str(source), source_count=len(hashes), commit=COMMIT, tree=TREE,
        archive_sha256=ARCHIVE_SHA, runner_sha256=RUNNER_SHA, normalization_helper_sha256=HELPER_SHA,
        accuracy_reused='PR16已有完整105题102/105及原官方4K/16K证据；本轮不重跑',
        limits=['只完整main，不叠PR15或实验Q/KV/P资产', '安装marker不等实际选中，真实NORMALIZATION_SELECTED须本轮后验',
                '原bc51单锁/CPU quota观察/monitor/240s及清理不变；DB-after由原seal_framework_screen收集']))
    command = ['python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(source),
        '--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_PREFILL_NORMALIZATION_INSTALL']
    env = os.environ.copy()
    removed = {name: env.pop(name) for name in list(env) if name.startswith('BIV150_')
        or name in ('MINICPM_NATIVE_PROFILE_EVENTS','MINICPM_DECODE_GAP_RUN_DIR')}
    if env.get('VLLM_FL_BIV150_PREFILL_NORMALIZE','1') != '1':
        raise ValueError('不允许关闭已合入normalization')
    save(control / 'removed-experiment-environment.json', {'removed_names':sorted(removed)})
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
'''
    edit(text[start:end],replacement)
    # Only wording changes below; verification implementations remain unchanged.
    edit('不是冻结的PR15 tarball','不是冻结的当前main tarball')
    edit('tar未覆盖完整PR15树','tar未覆盖完整当前main树')
    edit('解包源码与完整PR15 tree不符','解包源码与完整当前main tree不符')
    inverse = text
    for old,new in reversed(edits):
        if inverse.count(new) != 1:
            raise ValueError('launcher逆回不唯一')
        inverse=inverse.replace(new,old,1)
    if inverse != original:
        raise ValueError('非精确逆回原launcher')
    compile(text,'launch_current_main_baseline.py','exec')
    (HERE/'launch_current_main_baseline.py').write_text(text,encoding='utf-8',newline='\n')
    (HERE/'launcher.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),text.splitlines(True),
        fromfile='pr15/launch_pr15_accuracy.py',tofile='current-main/launch_current_main_baseline.py')),encoding='utf-8')
    receipt=dict(commit=COMMIT,tree=TREE,files=len(entries),pins=pins,
        symlinks=[dict(path=e['path'],target=objects[e['sha']].decode()) for e in entries if e['mode']=='120000'],
        launcher_sha256=hashlib.sha256((HERE/'launch_current_main_baseline.py').read_bytes()).hexdigest(),
        inverse_exact=True,syntax_compiled=True,production_checkout_changed=False,device_used=False,
        launcher_executed=False,source_blobs_from='local Git objects only',archive_bytes=len(bundle))
    (HERE/'preparation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
