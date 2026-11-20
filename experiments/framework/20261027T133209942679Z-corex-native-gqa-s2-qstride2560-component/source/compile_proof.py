"""只读绑定同步完整loop的实际编译回执；单页资格另列，不迁移历史门。"""
from pathlib import Path
import hashlib,json
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check(directory,source):
    d=Path(directory).resolve(strict=True);r=json.loads((d/'compile-check.json').read_bytes())
    assert r['passed'] is True and all(v is True for v in r['checks'].values())
    assert r['variant']=='synchronous_0' and r['gpu_executed'] is False and r['numeric_qualified'] is False
    for n in ('gqa.ll','gqa.s'):assert sha(d/n)==r['files'][n]
    assert (d/'input.sha256').read_text().split()[0]==sha(source)
    assert r['files']=={'gqa.ll':'cbf2448603dbe59fc420b4b14ab3e0168dea2d76a6185b7f3c61837411b84173','gqa.s':'457d5e25e1abf565aff4deacfc13874c10d660affa5d29135ffabb27a35db023'}
    return dict(source_sha256=sha(source),receipt_sha256=sha(d/'compile-check.json'),record=r,scope='编译证据；不自动授历史/tail/Graph/reducer/性能资格')
