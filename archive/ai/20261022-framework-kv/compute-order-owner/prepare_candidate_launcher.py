"""由已审baseline编排派生候选入口；只准备文件，不上卡。"""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
base=(root/'tmp/compute-order-owner/launch_baseline.py').read_bytes()
assert hashlib.sha256(base).hexdigest()=='90554d08b1a274458e355ad7c7da739740c52da0a5045aee48eea16757447abe'
text=base.decode()
edits=[]
def edit(a,b):
 global text
 assert text.count(a)==1,a
 text=text.replace(a,b);edits.append((a,b))
edit('原422短负载基线：仅编排已有bc51 owner，保原SERVER与原始证据。','计算序423短服务：固定四路径变化，原bc51负责SERVER/单卡锁/清理；非准确率证明。')
anchor="stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')\n"
addition="""assets = Path(__file__).parent
for name, pin in {
    'prepare_compute_order.py': 'b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670',
    'biv150_compute_order.py': '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce',
}.items():
    assert sha(assets / name) == pin, name
base_source = SOURCE
SOURCE = ROOT / 'code' / ('compute-order-' + stamp)
subprocess.run(['python3', str(assets / 'prepare_compute_order.py'), '--base', str(base_source), '--output', str(SOURCE)], check=True)
prepared = SOURCE.with_name(SOURCE.name + '-prepare.json')
receipt = json.loads(prepared.read_text())
expected = receipt['output_map']
assert receipt['source_count'] == len(expected) == 423
assert expected['vllm_fl/worker/model_runner.py'] == 'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'
assert set(receipt['changed_paths']) == {
    'vllm_fl/patches/biv150_compute_order.py', 'vllm_fl/worker/model_runner.py',
    'vllm_fl/patches/biv150_kv_worker.py', 'vllm_fl/patches/biv150_kv_protocol.py'}
assert mapping(SOURCE) == expected
reference_bytes = (json.dumps(expected, indent=2) + '\\n').encode()
"""
edit(anchor,anchor+addition)
edit("stamp + '-compute-order-baseline-context16k'","stamp + '-compute-order-candidate-context16k'")
edit("control.mkdir()\n","control.mkdir()\nshutil.copyfile(prepared, control / 'prepare.json')\nfor name in ('prepare_compute_order.py', 'biv150_compute_order.py'):\n    shutil.copyfile(assets / name, control / name)\n")
edit("control / 'launch_baseline.py'","control / 'launch_candidate.py'")
edit("'原422计算顺序候选的短负载基线；无新观察helper、无profiler、非官方分数'","'计算序423短服务；无profiler；实际命中和32/0只作集成及性能信号，不替代数值/准确率'")
edit("'variant': 'baseline', 'source': str(SOURCE), 'source_count': 422","'variant': 'candidate', 'source': str(SOURCE), 'source_count': 423")
edit("'reference_control': str(REFERENCE), 'verify_restore': '0'","'reference_control': str(REFERENCE), 'comparison_baseline': '20261023T054306Z-compute-order-baseline-context16k', 'verify_restore': '0'")
edit("'候选须另过正确性门和源码/DB/KV可比检查，不自动排第二任务'","'不继承原accuracy；收益须同DB/KV等可比性且实际命中；不自动排第二任务'")
inverse=text
for a,b in reversed(edits):
 assert inverse.count(b)==1
 inverse=inverse.replace(b,a)
assert inverse.encode()==base
compile(text,'launch_candidate.py','exec')
out=root/'tmp/compute-order-owner/launch_candidate.py'
out.write_text(text,encoding='utf-8',newline='\n')
(root/'tmp/compute-order-owner/candidate-wrapper-check.json').write_text(json.dumps({'baseline_sha256':hashlib.sha256(base).hexdigest(),'candidate_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'edits':len(edits),'inverse_exact':True,'compiled':True,'executed':False},indent=2)+'\n')
print(hashlib.sha256(out.read_bytes()).hexdigest())

