"""测量服务只读生产选中日志；不设置设备同步诊断变量、不创建新请求。"""
import json
from pathlib import Path
import re
import cache_gate as gate
import qualification as q

HERE = Path(__file__).resolve().parent


def capture(run):
    manifest = q.read(HERE/'source-manifest.json')
    expected = manifest['files']['vllm_fl/patches/biv150_attention_affine_pages.py']['sha256']
    text = re.sub(r'\x1b\[[0-9;]*m','',(Path(run)/'server.log').read_text(encoding='utf-8',errors='replace'))
    tag = 'BIV150_AFFINE_PAGES_SELECTED '
    rows = [json.loads(line.split(tag,1)[1]) for line in text.splitlines() if tag in line]
    q.require(rows and all(all(r.get(k) is True for k in ('actual_requests','q_hoisted','cpu_descriptor_verified'))
        and r.get('device_binding_verified') is False and r.get('graph_mode') == 'NONE'
        and type(r.get('epoch')) is int and r['epoch'] > 0 and r.get('runtime_source_sha256') == expected
        for r in rows), '测量服务未实际启用 affine 或意外带设备同步诊断')
    result = dict(valid=True,selected=rows,performance_claimed=False,diagnostic_device_sync=False)
    gate.save(Path(run)/'affine-selection.json',result)
    return result
