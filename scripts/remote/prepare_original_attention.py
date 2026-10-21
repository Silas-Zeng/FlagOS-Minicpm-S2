#!/usr/bin/env python3
"""Inspect, or explicitly restore, one audited installed Attention dependency.

Default mode only reads bytes and prints JSON. The --apply path is Linux-only,
owns the common device lock, and refuses any active service/accelerator. It is
preparation for a later original-13eb baseline, never a running experiment hook.
No vLLM/Torch/Triton imports, SQLite/cache resets, or recursive deletion.
"""

from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import tempfile


ROOT = Path('/workspace/experiments/minicpm-s2')
INSTALLED = Path('/usr/local/lib/python3.12/site-packages/vllm/v1/attention/ops/triton_unified_attention.py')
IXSMI = '/usr/local/corex-4.5.0/bin/ixsmi'
RUNTIME_SHA = 'a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4'
RETAINED_SHA = '54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f'
ORIGINAL_SHA = 'bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0'
ORIGINAL_SIZE = 41176


def utc():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reverse_retained(attention, runtime, original_reference):
    if digest(runtime) != RUNTIME_SHA or digest(attention) != RETAINED_SHA:
        raise RuntimeError('exact audited retained runtime/attention required')
    if digest(original_reference) != ORIGINAL_SHA:
        raise RuntimeError('independent a4 original reference hash mismatch')
    names = {'_LAUNCH_DEFAULTS', '_LAUNCH_TUNED', '_DECODE_TILE',
             '_DECODE_TILE_TUNED', '_ATTENTION_MARKER'}
    values = {}
    # Extract literal strings only; never execute/import the device runtime.
    for node in ast.parse(runtime).body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in names):
            name = node.targets[0].id
            if name in values:
                raise RuntimeError('duplicate retained literal: ' + name)
            value = ast.literal_eval(node.value)
            if type(value) is not str:
                raise RuntimeError('retained literal is not a string: ' + name)
            values[name] = value.encode('utf-8')
    if set(values) != names:
        raise RuntimeError('missing retained literal')
    for name in ['_LAUNCH_TUNED', '_DECODE_TILE_TUNED', '_ATTENTION_MARKER']:
        if attention.count(values[name]) != 1:
            raise RuntimeError('non-unique retained block: ' + name)
    suffix = b'\n' + values['_ATTENTION_MARKER'] + b'\n'
    if not attention.endswith(suffix):
        raise RuntimeError('retained marker is not the exact EOF suffix')
    original = attention[:-len(suffix)]
    for tuned, default in [('_LAUNCH_TUNED', '_LAUNCH_DEFAULTS'),
                           ('_DECODE_TILE_TUNED', '_DECODE_TILE')]:
        original = original.replace(values[tuned], values[default], 1)
    if (digest(original) != ORIGINAL_SHA or len(original) != ORIGINAL_SIZE
            or original != original_reference):
        raise RuntimeError('reverse does not equal the independently saved original bytes')
    return original


def idle_evidence():
    for family, address in [(socket.AF_INET, '127.0.0.1'), (socket.AF_INET6, '::1')]:
        try:
            with socket.socket(family) as sock:
                sock.settimeout(1)
                if sock.connect_ex((address, 9031)) == 0:
                    raise RuntimeError('port 9031 occupied')
        except OSError:
            if family == socket.AF_INET:
                raise
    command = [IXSMI, '--query-gpu=memory.used,utilization.gpu',
               '--format=csv,noheader,nounits']
    raw = subprocess.check_output(command, text=True, timeout=10)
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if len(lines) != 1:
        raise RuntimeError('expected exactly one accelerator')
    fields = [field.strip() for field in lines[0].split(',')]
    if (len(fields) != 2 or not all(field.isdigit() for field in fields)
            or int(fields[0]) > 68 or int(fields[1]) != 0):
        raise RuntimeError('expected idle accelerator <=68MiB and 0%: ' + repr(lines))
    full = subprocess.check_output([IXSMI], text=True, timeout=10)
    if 'No running processes found' not in full:
        raise RuntimeError('accelerator process table is not empty')
    return {'utc': utc(), 'port_9031_closed': True, 'command': command,
            'query_raw': raw, 'ixsmi_raw': full}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attention', type=Path, required=True)
    parser.add_argument('--runtime', type=Path, required=True)
    parser.add_argument('--original-reference', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='later idle-device preparation only')
    parser.add_argument('--record-dir', type=Path, help='new ROOT/dependency-restores child; apply only')
    args = parser.parse_args(argv)
    attention = args.attention.read_bytes()
    runtime = args.runtime.read_bytes()
    reference = args.original_reference.read_bytes()
    original = reverse_retained(attention, runtime, reference)
    report = {'utc': utc(), 'mode': 'inspect', 'command': [sys.executable, *sys.argv],
              'runtime_sha256': digest(runtime), 'before_sha256': digest(attention),
              'before_size': len(attention), 'after_sha256': digest(original),
              'after_size': len(original), 'independent_reference_byte_equal': True}
    if not args.apply:
        if args.record_dir is not None:
            parser.error('--record-dir is only used by --apply')
        print(json.dumps(report, indent=2))
        return 0
    if sys.platform != 'linux' or args.record_dir is None:
        parser.error('--apply requires Linux and a new --record-dir')
    if (args.attention.is_symlink() or args.attention.resolve() != INSTALLED
            or not stat.S_ISREG(args.attention.stat().st_mode)):
        raise RuntimeError('apply target must be the exact regular installed source')
    records = (ROOT / 'dependency-restores').resolve()
    record = args.record_dir.resolve()
    if record == records or not record.is_relative_to(records):
        raise RuntimeError('record-dir must be a new child of ROOT/dependency-restores')
    import fcntl
    with (ROOT / 'framework-device.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        report['preflight'] = idle_evidence()
        if args.attention.read_bytes() != attention:
            raise RuntimeError('installed source changed before restoration')
        record.mkdir(parents=True, exist_ok=False)
        report.update(mode='apply', status='prepared', record_dir=str(record))
        shutil.copyfile(Path(__file__), record / 'prepare_original_attention.py')
        for name, data in [('before.py', attention), ('original-reference.py', reference),
                           ('retained-runtime.py', runtime)]:
            with (record / name).open('xb') as handle:
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            if (record / name).read_bytes() != data:
                raise RuntimeError('backup integrity failure: ' + name)
        old_stat = args.attention.stat()
        report['original_stat'] = {'mode': old_stat.st_mode, 'uid': old_stat.st_uid,
                                   'gid': old_stat.st_gid, 'mtime_ns': old_stat.st_mtime_ns}
        manifest = record / 'manifest.json'
        manifest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        temporary = None
        try:
            # Recheck after backups; no cache/import work has occurred.
            report['pre_replace_idle'] = idle_evidence()
            if args.attention.read_bytes() != attention:
                raise RuntimeError('installed source changed after backup')
            fd, temporary = tempfile.mkstemp(prefix='.biv150-original-', dir=INSTALLED.parent)
            with os.fdopen(fd, 'wb') as handle:
                os.fchmod(handle.fileno(), stat.S_IMODE(old_stat.st_mode))
                os.fchown(handle.fileno(), old_stat.st_uid, old_stat.st_gid)
                handle.write(original)
                handle.flush()
                os.fsync(handle.fileno())
            if Path(temporary).read_bytes() != original:
                raise RuntimeError('temporary source integrity failure')
            os.replace(temporary, args.attention)
            temporary = None
            if args.attention.read_bytes() != original:
                raise RuntimeError('installed post-replace identity failure')
            report.update(status='restored', finished_utc=utc(),
                          postflight=idle_evidence(), installed_sha256=digest(args.attention.read_bytes()))
        except BaseException as error:
            report.update(status='failed', error=repr(error), finished_utc=utc())
            raise
        finally:
            if temporary is not None:
                Path(temporary).unlink(missing_ok=True)
            manifest.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
