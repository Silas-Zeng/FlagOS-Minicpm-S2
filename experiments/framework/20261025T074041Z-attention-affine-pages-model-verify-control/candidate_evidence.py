"""只读取本服务 ready 后的 affine 选中记录；不再生成额外负载。"""
import json
from pathlib import Path
import re

import cache_gate as gate
import qualification as q

HERE = Path(__file__).resolve().parent
TAG = 'BIV150_AFFINE_PAGES_SELECTED '
RUNTIME = 'vllm_fl/patches/biv150_attention_affine_pages.py'


def capture(run, after_bytes):
    run = Path(run)
    manifest = q.read(HERE / 'source-manifest.json')
    expected = manifest['files'][RUNTIME]['sha256']
    raw = (run / 'server.log').read_bytes()
    q.require(type(after_bytes) is int and 0 <= after_bytes <= len(raw), '服务日志边界变化')
    text = re.sub(r'\x1b\[[0-9;]*m', '', raw[after_bytes:].decode('utf-8', errors='replace'))
    rows = [json.loads(line.split(TAG, 1)[1]) for line in text.splitlines() if TAG in line]
    q.require(rows, '原四语义未实际命中 affine；不以安装日志替代执行')
    for row in rows:
        q.require(all(row.get(k) is True for k in ('actual_requests', 'q_hoisted',
                  'cpu_descriptor_verified', 'device_binding_verified'))
                  and row.get('graph_mode') == 'NONE'
                  and type(row.get('epoch')) is int and row['epoch'] > 0
                  and type(row.get('rows')) is int and row['rows'] > 0
                  and type(row.get('query_tokens')) is int and row['query_tokens'] > 1
                  and row.get('runtime_source_sha256') == expected,
                  '实际 metadata/epoch/Q/设备绑定或运行源码证据不符')
    folder = run / 'affine-binding'
    q.require(folder.is_dir() and not folder.is_symlink(), '本run绑定原件目录缺失')
    files = {}
    for path in sorted(folder.rglob('*')):
        if path.is_file():
            q.require(not path.is_symlink() and path.resolve().is_relative_to(folder.resolve()), '绑定原件越界')
            files[path.relative_to(run).as_posix()] = q.sha(path)
    q.require(files, '设备绑定验证未保存原件')
    evidence = dict(valid=True, selected=rows, evidence_files=files, log_offset=after_bytes,
        runtime_source_sha256=expected, source_count=manifest['source_count'], tree=manifest['tree'],
        limitation='只证明原四语义期间合法实际绑定命中；非完整105、非官方成绩、不恢复已知mixed2资格')
    gate.save(run / 'affine-evidence.json', evidence)
    return evidence
