"""仅复用source身份、idle和所属进程读取；无KV运行/资格入口。"""
import hashlib
import os
from pathlib import Path
import subprocess

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
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    return blobs, hashes

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
