#!/usr/bin/env python3
"""封存已正常结束的准确率任务；复用既有判卷审阅器，不把退出0当准确率通过。"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess
import sys
import tarfile


ROOT = Path('/workspace/experiments/minicpm-s2')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def save(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_id')
    parser.add_argument('--reviewer', type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r'\d{8}T\d{6}Z-[a-z0-9-]+', args.run_id):
        raise ValueError('invalid run ID')
    parent = ROOT / 'accuracy'
    run, control = parent / args.run_id, parent / (args.run_id + '-control')
    archive = parent / (args.run_id + '.tgz')
    outputs = [run/'postflight-full.json', run/'accuracy-review.json', run/'accuracy-review.log',
               control/'evidence-seal.json', control/'seal_completed_accuracy.py',
               control/'review_accuracy_gate.py', control/'seal-command.json', archive]
    if any(path.exists() for path in outputs):
        raise FileExistsError('已有封存输出；先检查原件，不自动覆盖或重复封包')
    result, manifest = read(run/'result.json'), read(run/'manifest.json')
    if ((run/'exit-code').read_text().strip() != '0' or result['cleanup_errors']
            or result['evaluation_completed'] is not True):
        raise RuntimeError('仅处理已正常结束的完整任务；失败任务另行保留检查')
    expected = read(control/'source-sha256.json')
    source = Path(manifest['source_dir']).resolve(strict=True)
    if not source.is_relative_to(ROOT/'code'):
        raise ValueError('源码越出实验目录')
    actual = {p.relative_to(source).as_posix():sha(p) for p in source.rglob('*')
              if p.is_file() and not any(x in ('.git','__pycache__') for x in p.relative_to(source).parts)
              and p.suffix not in ('.pyc','.pyo')}
    failures = sorted(k for k in actual.keys() | expected.keys() if actual.get(k) != expected.get(k))
    archived_failures = [k for k,v in manifest['sha256'].items() if sha(run/'source'/k) != v]
    archived_failures += ['plugin/'+k for k,v in expected.items()
                          if (run/'source/plugin'/k).exists() and sha(run/'source/plugin'/k) != v]
    ports = {}
    for family, host in ((socket.AF_INET,'127.0.0.1'),(socket.AF_INET6,'::1')):
        with socket.socket(family,socket.SOCK_STREAM) as sock:
            sock.settimeout(2); ports[host] = sock.connect_ex((host,9031)) != 0
    query = subprocess.check_output(['ixsmi','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
    table = subprocess.check_output(['ixsmi'],text=True)
    pids = {int(p.read_text()) for p in (control/'runner.pid',run/'server.pid',run/'evaluation.pid')}
    pids.update(map(int,re.findall(r'EngineCore pid=(\d+)',(run/'server.log').read_text(errors='replace'))))
    states = {}
    for pid in sorted(pids):
        status = Path('/proc')/str(pid)/'status'
        states[str(pid)] = status.read_text() if status.exists() else None
    post = {'utc':datetime.now(timezone.utc).isoformat(),'source_count':len(expected),
            'source_failures':failures,'archived_source_failures':archived_failures,
            'ports_closed':ports,'query':query,'ixsmi':table,'owned_process_status':states}
    if (failures or archived_failures or not all(ports.values()) or query.strip() != '68, 0'
            or 'No running processes found' not in table
            or not all(s is None or '\nState:\tZ ' in s for s in states.values())):
        raise RuntimeError('后态不通过：'+json.dumps(post))
    evaluations = list((run/'math500-level3').glob('*/reports/minicpm/math_500.json'))
    if len(evaluations) != 1:
        raise RuntimeError('需要唯一完整官方报告')
    evaluation_dir = evaluations[0].parents[2]
    review = subprocess.run([sys.executable,str(args.reviewer.resolve(strict=True)),str(evaluation_dir)],capture_output=True,text=True)
    parsed = json.loads(review.stdout)
    if review.returncode not in (0,1) or parsed.get('validity') != 'valid':
        raise RuntimeError('审阅证据不完整：'+review.stdout+review.stderr)
    save(run/'postflight-full.json',post)
    save(run/'accuracy-review.json',parsed)
    save(control/'seal-command.json',{'argv':sys.argv,'review_command':review.args})
    with (run/'accuracy-review.log').open('x',encoding='utf-8') as stream:
        stream.write(review.stderr)
    with (control/'seal_completed_accuracy.py').open('xb') as stream:
        stream.write(Path(__file__).read_bytes())
    with (control/'review_accuracy_gate.py').open('xb') as stream:
        stream.write(args.reviewer.read_bytes())
    files = {str(p.relative_to(parent)):sha(p) for d in (run,control) for p in sorted(d.rglob('*')) if p.is_file()}
    save(control/'evidence-seal.json',{'utc':post['utc'],'exit_code':0,'files':files,
         'reviewer_sha256':sha(args.reviewer),'accuracy_gate':parsed['accuracy_gate']})
    with tarfile.open(archive,'x:gz') as package:
        package.add(run,arcname=run.name); package.add(control,arcname=control.name)
    print(json.dumps({'archive':str(archive),'bytes':archive.stat().st_size,'sha256':sha(archive),
                      'sealed_files':len(files),'accuracy_gate':parsed['accuracy_gate'],
                      'correct':parsed['correct'],'samples':parsed['samples']}))


if __name__ == '__main__':
    main()
