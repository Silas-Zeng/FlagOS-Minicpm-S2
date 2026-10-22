#!/usr/bin/env python3
"""仅CPU保存实际Corex类型、Torch stream指针和链接证据，不导入torch/载库。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess


def main():
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-memcpy2d-abi'
    out = Path('/workspace/experiments/minicpm-s2/source-audits') / run_id
    out.mkdir(exist_ok=False)
    shutil.copyfile(__file__, out / Path(__file__).name)
    entries = [
        ('/usr/local/corex/include/IX/ixrt/driver_types.h', [(367, 379), (778, 789), (1172, 1181)]),
        ('/usr/local/corex/include/IX/crt/host_defines.h', [(20, 53), (65, 75)]),
        ('/usr/local/corex/include/IX/ixrt/ix_runtime_api.h', [(25, 75), (447, 470)]),
        ('/usr/local/corex/include/IX/mapping_cudart.h', []),
        ('/usr/local/lib/python3.12/site-packages/torch/cuda/streams.py', [(97, 114)]),
    ]
    headers = []
    for name, spans in entries:
        p = Path(name)
        raw = p.read_bytes()
        lines = raw.decode('utf-8').splitlines()
        if not spans:
            spans = [(max(1, i - 1), min(len(lines), i + 2)) for i, line in enumerate(lines, 1)
                     if any(n in line for n in ('cudaMemcpyAsync ', 'cudaMemcpy2DAsync ',
                        'cudaMemcpyDeviceToHost ', 'cudaDeviceGetAttribute ', 'cudaDevAttrMaxPitch '))]
        headers.append({'path': name, 'resolved': str(p.resolve()),
                        'sha256': hashlib.sha256(raw).hexdigest(),
                        'excerpts': [{'start_line': a, 'end_line': b, 'lines': lines[a-1:b]}
                                     for a, b in spans]})
    lib = Path('/usr/local/corex/lib64/libcudart.so').resolve()
    command = ['readelf', '--dyn-syms', '--wide', str(lib)]
    proc = subprocess.run(command, capture_output=True, text=True, check=True)
    names = ('ixMemcpyAsync', 'ixMemcpy2DAsync', 'ixDeviceGetAttribute', 'ixGetErrorString',
             'cudaMemcpyAsync', 'cudaMemcpy2DAsync', 'cudaDeviceGetAttribute')
    exports = [line for line in proc.stdout.splitlines() if any(n + '@' in line for n in names)]
    compiler = subprocess.run(['g++', '--version'], capture_output=True, text=True, check=True)
    doc = {'run_id': run_id, 'kind': 'CPU-only actual ABI source evidence',
           'recorded_utc': datetime.now(timezone.utc).isoformat(), 'platform': platform.platform(),
           'headers': headers, 'library': {'path': str(lib),
              'sha256': hashlib.sha256(lib.read_bytes()).hexdigest(),
              'export_command': command, 'exports': exports, 'stderr': proc.stderr},
           'compiler': {'command': ['g++', '--version'], 'stdout': compiler.stdout, 'stderr': compiler.stderr},
           'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
           'limits_zh': ['未导入torch、加载库或调用设备API。',
                         '编译桥必须使用这些实际头文件；类型证据不代表真实复制成功。',
                         'pitch能力需设备查询及真实字节门；stream指针适配仍需设备验证。']}
    p = out / 'result.json'
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'directory': str(out), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
