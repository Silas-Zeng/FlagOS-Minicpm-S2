"""只读旧NPZ重算coverage；不改原result/不Torch/不GPU。"""
from pathlib import Path
import hashlib,io,json,tarfile
import numpy as np
root=Path(__file__).resolve().parents[3]
bundle=root/'tmp/20261027T120655436062Z-corex-native-gqa-page16-numeric-recovery.tar.gz'
expected='6cfacbf03cea667cd121f93b2c914514d465e18ab6c21aadb90bf46483c5b4a8'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert sha(bundle.read_bytes())==expected
prefix='framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/'
with tarfile.open(bundle) as archive:
 raw=archive.extractfile(prefix+'underflow_P-partial-mismatch.npz').read()
 result_raw=archive.extractfile(prefix+'result.json').read()
result=json.loads(result_raw);arrays=np.load(io.BytesIO(raw))
assert arrays['native_score'].dtype==np.float32
scores=arrays['native_score'].astype(np.float64)
p=np.exp2(scores-scores.max(axis=1,keepdims=True))
coverage=dict(normal=bool(np.any(p>=2.0**-126)),subnormal=bool(np.any((p>0)&(p<2.0**-126))),below_smallest_subnormal=bool(np.any(p<(2.0**-149)*.5)))
assert all(coverage.values())
assert np.array_equal(arrays['native_probability'].view(np.uint32),arrays['tl_exp2_probability'].view(np.uint32))
subnormal=(p>0)&(p<2.0**-126)
record=dict(bundle_sha256=expected,npz_member=prefix+'underflow_P-partial-mismatch.npz',npz_sha256=sha(raw),original_result_sha256=sha(result_raw),original_result_preserved=True,original_status=result['status'],original_coverage=result['underflow_input_coverage'],CPU_float64_coverage=coverage,score_dtype='float32 source -> CPU NumPy astype(float64)',thresholds={'min_normal':2.0**-126,'min_subnormal':2.0**-149},score_row0=scores[0].tolist(),exact_probability_min=float(p.min()),exact_probability_max=float(p.max()),all_FP32_P_bitwise=True,native_and_reference_subnormal_range_both_zero=bool(np.all(arrays['native_probability'][subnormal]==0)&np.all(arrays['tl_exp2_probability'][subnormal]==0)),interpretation='原coverage路径先在GPU转double且依赖CPU float32 nextafter；这里只从已存float32在CPU转换并使用精确Python阈值。输入确覆盖三范围，设备数值已记录全逐位；不改原false，不补称尚未执行的Graph/side通过。',graph_or_side_completed=False,gpu_executed_here=False)
(Path(__file__).parent/'result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,ensure_ascii=False))
