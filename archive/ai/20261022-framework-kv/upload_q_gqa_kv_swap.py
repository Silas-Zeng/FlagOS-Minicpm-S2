"""只上传已审KV组合输入，不创建候选源、不启动任何GPU任务。"""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import sys

base = Path('tmp/q-gqa-kv-swap')
identity = json.loads((base / 'identity-delta.json').read_text(encoding='utf-8'))
pins = dict(identity['assets_sha256'])
pins.update({
    'prepare_q_gqa_kv_swap.py': '6d09374054f2ae1df54f7dc9fceb5e221eae3f8b39bcbaf5a93c0500c5181cc4',
    'launch_q_gqa_kv_swap.sh': '1bd16b321ae7d1d11e105f7c0e3ed19e3712afb059b1989a5974556872d8e03e',
    'base-source-sha256.json': identity['base_map_sha256'],
    'expected-source-sha256.json': '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
})
destination = '/workspace/experiments/minicpm-s2/scripts/q-gqa-kv-swap-20261022'
lines = ['set -euo pipefail', 'mkdir ' + destination]
for name, pin in pins.items():
    data = (base / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == pin, name
    path = destination + '/' + name
    lines.extend([
        "printf '%s' '" + base64.b64encode(data).decode() + "' | base64 -d > '" + path + "'",
        "printf '%s\\n' '" + pin + '  ' + path + "' | sha256sum -c -",
    ])
args = ['ssh', '-F', 'NUL', '-i', 'C:/Users/Administrator/.ssh/id_ed25519_flagos_s2',
    '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes', '-o', 'ConnectTimeout=12',
    '-p', '2224', 'lab_inst_01M5D0Q7BQXT15N94DYK2V99EF@ssh.flagos.io', 'bash']
result = subprocess.run(args, input=('\n'.join(lines) + '\n').encode(), capture_output=True, timeout=45)
sys.stdout.buffer.write(result.stdout)
sys.stderr.buffer.write(result.stderr)
raise SystemExit(result.returncode)
