"""冻结本轮四题诊断接线；不连接设备、不运行模型。"""
import argparse, base64, difflib, hashlib, json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'tmp/compute-order-math4-owner'
HERE.mkdir(exist_ok=True)
sha=lambda data: hashlib.sha256(data).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--prepared-dir',type=Path,required=True);p.add_argument('--receipt',type=Path,required=True)
a=p.parse_args(); prepared=a.prepared_dir.resolve()
assert prepared.is_relative_to(ROOT/'tmp/compute-order-math4-gate')
base_bytes=(ROOT/'tmp/compute-order/base-source-sha256.json').read_bytes()
assert sha(base_bytes)=='82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
base=json.loads(base_bytes)
receipt=json.loads(a.receipt.read_text(encoding='utf-8'))
target=receipt['output_map']
assert len(base)==422 and len(target)==424 and set(base)<=set(target)
changed=sorted(k for k in target if base.get(k)!=target[k])
assert changed==['vllm_fl/patches/biv150_compute_order.py','vllm_fl/patches/biv150_compute_order_math4.py','vllm_fl/patches/biv150_kv_protocol.py','vllm_fl/patches/biv150_kv_worker.py','vllm_fl/worker/model_runner.py']
baseline423=ROOT/'experiments/framework/20261023T060425Z-compute-order-candidate-context16k-control'
map423_bytes=(baseline423/'source-sha256.json').read_bytes()
assert sha(map423_bytes)=='6cf2e1d7e3084d95e0fd8db23ceaa426c5c5ab6ff887dffcd8f036e60b98a7b9'
map423=json.loads(map423_bytes)
for rel in changed:
    source=prepared/rel
    if not source.exists():
        assert target[rel]==map423[rel]
        source=baseline423/'plugin-source'/rel
    data=source.read_bytes(); assert sha(data)==target[rel]
    out=HERE/'files'/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
extras={
    'run_math4_gate.py':ROOT/'tmp/compute-order-math4-owner-load/run_math4_gate.py',
    'run_math4_load.py':ROOT/'tmp/compute-order-math4-owner-load/run_math4_load.py',
    'capture_evalscope.py':ROOT/'tmp/compute-order-math4-gate/capture_evalscope.py',
}
pins={}
for name,source in extras.items():
    data=source.read_bytes();compile(data,name,'exec');(HERE/name).write_bytes(data);pins[name]=sha(data)
deployment=dict(kind='固定前4题与原16K背景的单服务混合答案诊断，非官方成绩',source_count=len(target),output_map=target,changed_paths=changed,diagnostic_asset_sha256=pins)
deployment_bytes=(json.dumps(deployment,ensure_ascii=False,indent=2)+'\n').encode()
(HERE/'deployment.json').write_bytes(deployment_bytes)
(HERE/'base-source-sha256.json').write_bytes(base_bytes)
old=(ROOT/'tmp/compute-order-structure-owner/launch_candidate.py').read_bytes()
assert sha(old)=='8decab3f6694ba259d9dcc5178d380ac94996f02f4cc290b86a4c1a8e286ed87'
text=old.decode();edits=[]
def replace(before,after):
    global text
    assert text.count(before)==1,before
    text=text.replace(before,after,1);edits.append((before,after))
replace('一次自然命中的计算顺序shadow诊断；原bc51负责SERVER/单卡锁/清理，不计性能。','固定4题的真实混合答案诊断；bc51派生owner负责SERVER/单卡锁/清理，不计性能。')
replace("'370a757740f44cdde4d5976a425f85d7fd94be75c3a596b7819cdfa19f37ca86'",repr(sha(deployment_bytes)))
replace("'vllm_fl/patches/biv150_compute_order_structure.py'","'vllm_fl/patches/biv150_compute_order_math4.py'")
replace("base_source = SOURCE\n", "for rel, pin in receipt['diagnostic_asset_sha256'].items():\n    assert sha(assets / rel) == pin, rel\nbase_source = SOURCE\n")
replace("'compute-order-structure-' + stamp","'compute-order-math4-' + stamp")
replace("stamp + '-compute-order-structure-context16k'","stamp + '-compute-order-math4-mixed'")
replace("shutil.copyfile(__file__, control / 'launch_candidate.py')", "shutil.copyfile(__file__, control / 'launch_candidate.py')\nfor rel in receipt['diagnostic_asset_sha256']:\n    shutil.copyfile(assets / rel, control / rel)")
replace("'单次完整M输入与N个logits索引映射、原sample衔接诊断；不计性能'","'固定前4题、原采样与原判卷的独立混合诊断；不计性能或官方准确率'")
replace("'variant': 'shadow-diagnostic'","'variant': 'math4-mixed-diagnostic'")
replace("'不改官方SERVER；原context-screen/seed721201', '必须有实际shadow完成证据；未命中为未覆盖；不同bit不自动等于算法错误；不自动排第二任务'", "'不改官方SERVER/原题/采样/judge；诊断limit4与原context-screen/seed721201', '必须逐题关联实际P outside采样与原响应；未命中或超时为未覆盖，不重试换题，不自动排第二任务'")
replace("(control / 'structure-artifacts').mkdir()", "(control / 'math4-artifacts').mkdir()")
replace("'BIV150_COMPUTE_ORDER_STRUCTURE_DIR=' + str(control / 'structure-artifacts')", "'BIV150_COMPUTE_ORDER_MATH4_DIR=' + str(control / 'math4-artifacts')")
replace("'python3', str(ROOT / 'scripts/run_framework_screen.py'), str(run), '--source-dir', str(SOURCE)", "'python3', str(assets / 'run_math4_gate.py'), str(run), '--source-dir', str(SOURCE)")
replace("'--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']", "'--context-screen', '--seed', '721201', '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED',\n    '--math4-capture', str(assets / 'capture_evalscope.py'), '--math4-capture-output', str(control / 'client-capture')]")
reverse=text
for before,after in reversed(edits):
    assert reverse.count(after)==1;reverse=reverse.replace(after,before,1)
assert reverse.encode()==old
compile(text,'launch_candidate.py','exec')
(HERE/'launch_candidate.py').write_text(text,encoding='utf-8',newline='\n')
(HERE/'owner.diff').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),text.splitlines(True),fromfile='structure-owner',tofile='math4-owner')),encoding='utf-8',newline='\n')
payload={}
paths=[HERE/'launch_candidate.py',HERE/'deployment.json',HERE/'base-source-sha256.json',*[HERE/rel for rel in extras],*[HERE/'files'/rel for rel in changed]]
for path in paths:
    data=path.read_bytes();payload[path.relative_to(HERE).as_posix()]=dict(sha256=sha(data),data=base64.b64encode(data).decode())
(HERE/'payload.json').write_text(json.dumps(payload),encoding='utf-8',newline='\n')
emitter=(ROOT/'tmp/compute-order-structure-owner/emit_start.py').read_text(encoding='utf-8')
emitter=emitter.replace('compute-order-structure-20261023','compute-order-math4-20261023')
emitter=emitter.replace("'launch_candidate.py', 'deployment.json', 'base-source-sha256.json'", "'launch_candidate.py', 'deployment.json', 'base-source-sha256.json', 'run_math4_gate.py', 'run_math4_load.py', 'capture_evalscope.py'")
compile(emitter,'emit_start.py','exec');(HERE/'emit_start.py').write_text(emitter,encoding='utf-8',newline='\n')
check=dict(original_owner_sha256=sha(old),launch_sha256=sha(text.encode()),deployment_sha256=sha(deployment_bytes),diagnostic_asset_sha256=pins,changes=len(edits),inverse_exact=True,compiled=True,source_count=len(target),changed_paths=changed)
(HERE/'owner-preparation.json').write_text(json.dumps(check,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(check,ensure_ascii=False))
