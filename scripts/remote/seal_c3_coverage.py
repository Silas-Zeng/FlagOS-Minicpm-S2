#!/usr/bin/env python3
"""补齐已结束的 C3 诊断证据；仅标准库、只读设备与被测源码。"""
import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess

ROOT = Path('/workspace/experiments/minicpm-s2')
RUN = ROOT / 'framework/20261021T173003Z-c3-coverage-context16k'
CONTROL = Path(str(RUN) + '-control')
SOURCE = ROOT / 'code/c3-coverage-20261021T173003Z'
SITE = Path('/usr/local/lib/python3.12/site-packages')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def save(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

assert (RUN / 'exit-code').read_text().strip() == '0'
hashes = json.loads((CONTROL / 'source-sha256.json').read_text())
failures = [name for name, expected in hashes.items()
            if sha(SOURCE / name) != expected or sha(CONTROL / 'plugin-source' / name) != expected]
ports = {}
for family, host in ((socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')):
    with socket.socket(family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        ports[host] = sock.connect_ex((host, 9031)) != 0
query = subprocess.check_output(['ixsmi', '--query-gpu=memory.used,utilization.gpu', '--format=csv,noheader,nounits'], text=True)
table = subprocess.check_output(['ixsmi'], text=True)
processes = {}
for pid in (191100, 191113, 191286):
    status = Path('/proc') / str(pid) / 'status'
    processes[str(pid)] = status.read_text() if status.exists() else None
post = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'ports_closed': ports,
        'query': query, 'ixsmi': table, 'owned_process_status': processes,
        'source_count': len(hashes), 'source_failures': failures}
save(RUN / 'postflight-full.json', post)
assert not failures and all(ports.values()) and query.strip() == '68, 0'
assert 'No running processes found' in table
assert all(value is None or '\nState:\tZ ' in value for value in processes.values())
attention = SITE / 'vllm/v1/attention/ops/triton_unified_attention.py'
target = RUN / 'postflight-sources'
target.mkdir()
shutil.copyfile(attention, target / attention.name)
save(target / 'manifest.json', {'path': str(attention), 'sha256': sha(attention)})
assert sha(attention) == '54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f'
subprocess.run(['python3', str(ROOT / 'scripts/snapshot_tuning_db.py'), '--database',
                '/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db', '--output',
                str(CONTROL / 'db-after')], check=True)
snapshots = []
for line in (RUN / 'server.log').read_text(errors='replace').splitlines():
    if 'BIV150_C3_COVERAGE ' in line:
        raw = line.split('BIV150_C3_COVERAGE ', 1)[1]
        raw = re.sub(r'\x1b\[[0-9;]*m', '', raw)
        try:
            snapshots.append({'raw_line': line, 'data': json.loads(raw)})
        except json.JSONDecodeError:
            snapshots.append({'raw_line': line, 'parse_failed': True})
save(RUN / 'coverage-snapshots.json', {'snapshots': snapshots,
      'timing_is_performance_evidence': False, 'periodic_is_complete': False,
      'plan_is_forward_execution': False})
print(json.dumps({'postflight': post, 'snapshots': len(snapshots)}, indent=2))
