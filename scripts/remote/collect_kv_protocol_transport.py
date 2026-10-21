#!/usr/bin/env python3
"""只读归档已安装的两份KV协议通信依赖；不导入框架或访问GPU。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


ROOT = Path('/workspace/experiments/minicpm-s2/source-audits')
SITE = Path('/usr/local/lib/python3.12/site-packages')
FILES = ('vllm/v1/serial_utils.py', 'vllm/v1/worker/worker_base.py')


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = ROOT / (stamp + '-kv-protocol-transport')
    out.mkdir(parents=True, exist_ok=False)
    records = {}
    for name in FILES:
        original = SITE / name
        data = original.read_bytes()
        target = out / 'source' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        records[name] = {'path': str(original), 'bytes': len(data),
                         'sha256': hashlib.sha256(data).hexdigest()}
    script = Path(__file__).read_bytes()
    (out / 'collector.py').write_bytes(script)
    manifest = {'utc': datetime.now(timezone.utc).isoformat(),
                'kind': 'installed-source-only; no framework import or GPU access',
                'sources': records, 'collector_sha256': hashlib.sha256(script).hexdigest()}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'status': 'complete', 'output': str(out), 'sources': records}, indent=2))


if __name__ == '__main__':
    main()
