"""VERIFY0 多事务 FULL H2D 动态几何；不加载 SO 或设备框架。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

PINS = {'biv150_kv_pitched_copy.py': '818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd',
        'biv150_kv_pitched_restore.py': 'a7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c',
        'biv150_kv_pitched_restore_bridge.so': 'f9bf8757133b084cd198ea8a8b0b217af887ac03b2f2bfb9599fd806a9801d2c'}

def require(ok, message):
    if not ok:
        raise ValueError(message)

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def validate(run, control):
    run, control = Path(run), Path(control)
    sources = json.loads((control/'source-sha256.json').read_bytes())
    patch = control/'plugin-source/vllm_fl/patches'
    for name, pin in PINS.items():
        require(sources['vllm_fl/patches/'+name] == pin
                and hashlib.sha256((patch/name).read_bytes()).hexdigest() == pin,
                'FULL H2D 冻结来源变化: '+name)
    save = load(patch/'biv150_kv_pitched_copy.py', 'official_h2d_save_geometry')
    restore = load(patch/'biv150_kv_pitched_restore.py', 'official_h2d_restore_geometry')
    rows = []
    for line_no, line in enumerate((run/'server.log').read_text(encoding='utf-8').splitlines(), 1):
        if 'BIV150_KV_PROTOCOL ' not in line:
            continue
        event = json.loads(line.split('BIV150_KV_PROTOCOL ', 1)[1])
        if event['event'] != 'RPC_ACK' or event['command']['kind'] != 'RESTORE_FULL':
            continue
        command, reply = event['command'], event['worker_response']
        ids = command['pages']
        require(ids and ids == sorted(ids) and all(type(x) is int and x > 0 for x in ids), 'FULL 私有页序变化')
        plan = restore.make_restore_plan(ids, max(ids)+1, save_runtime=save)
        maximum = reply['restore_max_pitch_bytes']
        require(type(maximum) is int and maximum >= 16384, 'FULL max_pitch 无效')
        pieces, fallback = restore.segments_for_pitch(plan, max_pitch=maximum)
        pitched = sum(s.height > 1 and s.physical_step > 1 for s in pieces)
        linear = len(pieces)-pitched
        nbytes = len(ids)*16384*42
        require(reply['restore_implementation'] == 'C_batch_positive_stride_FULL_H2D'
                and reply['restore_layers'] == 42 and reply['restore_submission_completion_ack'] is False
                and reply['restore_runtime_sha256'] == PINS['biv150_kv_pitched_restore.py']
                and reply['restore_bridge_sha256'] == PINS['biv150_kv_pitched_restore_bridge.so'],
                '不是已验 H2D 的真实提交')
        require(command['prefix_tokens'] == len(ids)*16 and command['nbytes'] == nbytes
                and reply['nbytes'] == reply['submitted_bytes'] == reply['transferred_bytes'] == nbytes
                and reply['restore_segments_per_layer'] == len(plan.segments)
                and reply['copy_calls'] == 42*len(pieces) and reply['linear_calls'] == 42*linear
                and reply['pitched_calls'] == 42*pitched and reply['fallback_pitched_segments'] == 42*fallback
                and reply['original_c95f_calls'] == 42*plan.original_c95f_runs,
                'FULL 实际动态页数/字节/提交几何不符')
        require(type(reply['restore_current_stream_handle']) is int and reply['restore_current_stream_handle'] >= 0,
                'FULL 实际 current stream 无效')
        # 原 c147 在本函数前执行，仍严格拒绝任何 VERIFY0 回读字段。
        rows.append(dict(line=line_no, pid=event['pid'], key=command['key'], nbytes=nbytes,
                         copy_calls=reply['copy_calls'], linear_calls=42*linear, pitched_calls=42*pitched,
                         original_c95f_calls=reply['original_c95f_calls'], max_pitch=maximum,
                         stream_handle=reply['restore_current_stream_handle']))
    return dict(valid=True, full_count=len(rows), has_full_coverage=bool(rows), transactions=rows,
                total_copy_calls=sum(r['copy_calls'] for r in rows),
                total_original_c95f_calls=sum(r['original_c95f_calls'] for r in rows),
                total_bytes=sum(r['nbytes'] for r in rows), gain_calculated=False,
                limits=['零 FULL 没有方法覆盖；提交数量不代表耗时或吞吐收益。',
                        'VERIFY0 不作新的字节回读；资格引用调用方指定的成功535 VERIFY1。'])
