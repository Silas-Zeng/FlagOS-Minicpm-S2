#!/usr/bin/env python3
"""仅CPU读取Corex运行库导出及头文件；不加载库、不初始化CUDA、不测性能。"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess


ROOT = Path('/workspace/experiments/minicpm-s2')
NAMES = ('cudaMemcpy2DAsync', 'cudaMemcpy2D', 'cudaGetErrorString', 'cudaGetErrorName')


def main():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    out = ROOT / 'source-audits' / (stamp + '-memcpy2d-exports')
    out.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(__file__, out / 'inspect_memcpy2d_exports.py')
    libraries, seen = [], set()
    for spelling in ('/usr/local/corex/lib64/libcudart.so', '/usr/local/corex/lib/libcudart.so'):
        path = Path(spelling)
        if not path.is_file():
            continue
        resolved = path.resolve(strict=True)
        if resolved in seen:
            continue
        seen.add(resolved)
        cmd = ['readelf', '--dyn-syms', '--wide', str(resolved)]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        matches = [line for line in proc.stdout.splitlines() if any(name in line for name in NAMES)]
        libraries.append({'spelling': spelling, 'resolved': str(resolved),
                          'sha256': hashlib.sha256(resolved.read_bytes()).hexdigest(),
                          'bytes': resolved.stat().st_size, 'command': cmd,
                          'matching_export_lines': matches, 'stderr': proc.stderr})
    headers = []
    for spelling in ('/usr/local/corex/include/cuda_runtime_api.h', '/usr/local/corex/include/cuda_runtime.h'):
        path = Path(spelling)
        if not path.is_file():
            continue
        raw = path.read_bytes()
        lines = raw.decode('utf-8', errors='replace').splitlines()
        hits = [{'line': i+1, 'context_start_line': max(0, i-4)+1,
                 'context': lines[max(0, i-4):min(len(lines), i+8)]}
                for i, line in enumerate(lines) if any(name in line for name in NAMES)]
        headers.append({'path': spelling, 'resolved': str(path.resolve()),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'hits': hits})
    result = {'run_id': out.name, 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'kind': 'CPU-only ELF/header inspection', 'libraries': libraries, 'headers': headers,
              'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits_zh': ['没有加载运行库、导入torch/CUDA或调用设备API。',
                            '导出符号与声明仅证明入口存在，不证明BI-V150复制语义、stream兼容、正确性或收益。']}
    (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'result_sha256': hashlib.sha256((out/'result.json').read_bytes()).hexdigest(),
                      'libraries': libraries, 'header_paths': [x['path'] for x in headers]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
