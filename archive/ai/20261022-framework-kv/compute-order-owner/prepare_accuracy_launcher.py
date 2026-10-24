"""派生当前423的原官方准确率入口，不启动设备。"""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
here=Path(__file__).parent
original=(root/'tmp/q-gqa-kv-swap/launch_q_gqa_kv_swap_accuracy.sh').read_bytes()
assert hashlib.sha256(original).hexdigest()=='76d88d73309dd23e9bbfbe1d98b5b9ccffb943cf44f5e6df209c562d8d862c3b'
mapfile=root/'experiments/framework/20261023T060425Z-compute-order-candidate-context16k-control/source-sha256.json'
mapbytes=mapfile.read_bytes();expected=json.loads(mapbytes)
assert expected==json.loads((root/'tmp/compute-order/files-prepare.json').read_text())['output_map']
assert len(expected)==423 and expected['vllm_fl/worker/model_runner.py']=='ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'
mapsha=hashlib.sha256(mapbytes).hexdigest()
(here/'accuracy-source-sha256.json').write_bytes(mapbytes)
text=original.decode()
changes={
 '# 只验证冻结422的新组合资格；原35d Math500 Level3 owner/参数/阈值不变。':'# 验证计算序423；原35d Math500 Level3 owner/参数/阈值不变，另核真实compute-order命中。',
 'source_dir="$root/code/q-gqa-kv-swap-20261022T213134Z"':'source_dir="$root/code/compute-order-20261023T060425Z"',
 'reference="$root/framework/20261022T213134Z-q-gqa-kv-swap-verify1-context16k-long-control/source-sha256.json"':'reference="$root/framework/20261023T060425Z-compute-order-candidate-context16k-control/source-sha256.json"',
 'run="$root/accuracy/$stamp-q-gqa-kv-swap"':'run="$root/accuracy/$stamp-compute-order"',
 '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136':mapsha,
 'len(expected)!=422':'len(expected)!=423',
 '不是213134已受测422完整源':'不是060425已短筛423完整源',
 '422现有源变化':'423现有源变化',
 '冻结422独立Math500 Level3准确率；未通过状态不得继承旧414':'计算序423独立Math500 Level3准确率；不继承原422准确率，需核实际候选命中',
 "'source_count':422":"'source_count':423",
 '安装marker不是实际事务或accuracy通过':'安装marker不是实际命中或accuracy通过；需同Engine的COMPUTE_ORDER_FIRST_SELECTED及完整结果',
}
for a,b in changes.items():
 assert text.count(a)==1,a
 text=text.replace(a,b)
inverse=text
for a,b in reversed(list(changes.items())):
 assert inverse.count(b)==1
 inverse=inverse.replace(b,a)
assert inverse.encode()==original
# heredoc Python部分语法；Bash -n在部署后、执行前完成。
py=text.split("<<'PY'\n",1)[1].split('\nPY\n',1)[0];compile(py,'accuracy-inline','exec')
out=here/'launch_compute_order_accuracy.sh';out.write_text(text,encoding='utf-8',newline='\n')
receipt={'original_launcher_sha256':hashlib.sha256(original).hexdigest(),'source_map_sha256':mapsha,'launcher_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'replacements':len(changes),'inverse_exact':True,'python_compiled':True,'executed':False}
(here/'accuracy-wrapper-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))

