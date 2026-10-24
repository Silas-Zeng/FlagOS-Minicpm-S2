"""仅生成 accepted-fill 的薄编排；不调用构建器、emitter 或设备。"""
import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
base_paths = {
    'launch_candidate.py': ROOT / 'tmp/compute-order-owner/launch_candidate.py',
    'emit_candidate.py': ROOT / 'tmp/compute-order-owner/emit_candidate.py',
}
base_pins = {
    'launch_candidate.py': '995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c',
    'emit_candidate.py': 'bd0076eb1f82bc908e83d2b7b689f2be453a99d7d4260d3d0f47454e291591f3',
}
asset_pins = {
    'prepare_accepted_fill.py': '410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043',
    'base-source-sha256.json': '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136',
}
for name, pin in asset_pins.items():
    assert sha((ROOT / 'tmp/accepted-fill' / name).read_bytes()) == pin, name


def derive(name, replacements):
    raw = base_paths[name].read_bytes()
    assert sha(raw) == base_pins[name]
    original = raw.decode('utf-8')
    newline = '\r\n' if '\r\n' in original else '\n'
    changes = [(a.replace('\n', newline), b.replace('\n', newline))
               for a, b in replacements]
    candidate = original
    for before, after in changes:
        assert candidate.count(before) == 1, (name, before)
        candidate = candidate.replace(before, after, 1)
    restored = candidate
    for before, after in reversed(changes):
        assert restored.count(after) == 1, (name, after)
        restored = restored.replace(after, before, 1)
    assert restored.encode('utf-8') == raw
    compile(candidate, str(HERE / name), 'exec')
    data = candidate.encode('utf-8')
    (HERE / name).write_bytes(data)
    (HERE / (name + '.diff')).write_text(''.join(difflib.unified_diff(
        original.splitlines(True), candidate.splitlines(True),
        fromfile='compute-order-owner/' + name, tofile='accepted-fill-owner/' + name)),
        encoding='utf-8', newline='')
    return {'sha256': sha(data), 'base_sha256': base_pins[name],
            'replacement_count': len(changes), 'compile': True,
            'exact_inverse_bytes': True}


launcher = derive('launch_candidate.py', [
    ('计算序423短服务：固定四路径变化，原bc51负责SERVER/单卡锁/清理；非准确率证明。',
     'accepted GPU fill 422短服务：固定三路径变化，原bc51负责SERVER/单卡锁/清理；非准确率证明。'),
    ("    'prepare_compute_order.py': 'b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670',\n"
     "    'biv150_compute_order.py': '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce',",
     "    'prepare_accepted_fill.py': '410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043',"),
    ("SOURCE = ROOT / 'code' / ('compute-order-' + stamp)\n"
     "subprocess.run(['python3', str(assets / 'prepare_compute_order.py'), '--base', str(base_source), '--output', str(SOURCE)], check=True)",
     "SOURCE = ROOT / 'code' / ('accepted-fill-' + stamp)\n"
     "subprocess.run(['python3', str(assets / 'prepare_accepted_fill.py'), '--base', str(base_source), '--output', str(SOURCE)], check=True)"),
    ("assert receipt['source_count'] == len(expected) == 423\n"
     "assert expected['vllm_fl/worker/model_runner.py'] == 'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'\n"
     "assert set(receipt['changed_paths']) == {\n"
     "    'vllm_fl/patches/biv150_compute_order.py', 'vllm_fl/worker/model_runner.py',\n"
     "    'vllm_fl/patches/biv150_kv_worker.py', 'vllm_fl/patches/biv150_kv_protocol.py'}",
     "assert receipt['source_count'] == len(expected) == 422\n"
     "changed_pins = {\n"
     "    'vllm_fl/worker/model_runner.py': '03a0e007e820644d55ac5eaf3331416da3fb0e58147a4f57928d363cc8ff6fb2',\n"
     "    'vllm_fl/patches/biv150_kv_worker.py': '68def179673964bb5d4011ce3f57ace9ce7c776a89e4dff63fb914aa19095da6',\n"
     "    'vllm_fl/patches/biv150_kv_protocol.py': 'eab62b8444727f0968be4154c1b212b77917a95c355c4d9832058e9d5cca80c9',\n"
     "}\nassert set(receipt['changed_paths']) == set(changed_pins)\n"
     "assert {path: expected[path] for path in changed_pins} == changed_pins"),
    ("(stamp + '-compute-order-candidate-context16k')", "(stamp + '-accepted-fill-candidate-context16k')"),
    ("for name in ('prepare_compute_order.py', 'biv150_compute_order.py'):",
     "for name in ('prepare_accepted_fill.py',):"),
    ("'kind': '计算序423短服务；无profiler；实际命中和32/0只作集成及性能信号，不替代数值/准确率',",
     "'kind': 'accepted GPU fill 422短服务；无profiler；冷资格与真实prepare记录只作激活证据，不替代数值/准确率',"),
    ("'variant': 'candidate', 'source': str(SOURCE), 'source_count': 423,",
     "'variant': 'candidate', 'source': str(SOURCE), 'source_count': 422,"),
    ("'limits': ['不改官方SERVER；原context-screen/seed721201', '不继承原accuracy；收益须同DB/KV等可比性且实际命中；不自动排第二任务'],",
     "'limits': ['不改官方SERVER；原context-screen/seed721201', '不继承原accuracy；收益须同DB/KV等可比性且实际命中；不自动排第二任务', '054306仅比较参考；若准确率改变DB，由root另排基线，不自动复用旧成绩'],"),
])

emitter = derive('emit_candidate.py', [
    ("'launch_candidate.py':(root/'tmp/compute-order-owner/launch_candidate.py','995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c'),",
     "'launch_candidate.py':(root/'tmp/accepted-fill-owner/launch_candidate.py','" + launcher['sha256'] + "'),"),
    (" 'prepare_compute_order.py':(root/'tmp/compute-order/prepare_compute_order.py','b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670'),\n"
     " 'biv150_compute_order.py':(root/'tmp/compute-order/biv150_compute_order.py','5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce'),",
     " 'prepare_accepted_fill.py':(root/'tmp/accepted-fill/prepare_accepted_fill.py','410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043'),"),
    ("root/'tmp/compute-order/base-source-sha256.json'", "root/'tmp/accepted-fill/base-source-sha256.json'"),
    ("scripts/compute-order-candidate-20261023", "scripts/accepted-fill-candidate-20261023"),
])
receipt = {'status': 'CPU准备完成，未上传或启动',
           'launch_candidate.py': launcher, 'emit_candidate.py': emitter,
           'assets': asset_pins,
           'retained': ['bc51 driver/SERVER/context-screen/seed721201',
                        '422基点map与原reference', '即时BI-V150/68,0/双栈空闲检查',
                        'DBbefore/源码归档/VERIFY0/finiteunset/绝对Qartifact',
                        '单项Popen交原owner持锁、PID与清理；不自动pair'],
           'not_executed': ['builder', 'launcher', 'emitter', '框架测试', 'SSH', 'GPU']}
(HERE / 'owner-preparation.json').write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'launcher_sha256': launcher['sha256'],
                  'emitter_sha256': emitter['sha256'], 'compile': True,
                  'exact_inverse_bytes': True}, ensure_ascii=False))
