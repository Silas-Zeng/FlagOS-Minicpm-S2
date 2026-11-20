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
    assert sha(source)=='bb9bde970bcdd710bbdfe180e3711af069977d5815897538a62c358d84d28820'
    assert 'ILj4EE' in r['kernel'] # 唯一S4实际编译产物；输出SHA逐件以上核验
    assert r['files']=={'gqa.ll':'f6667944aa4d4fde02ff188929399abaf46a9919f1292af90e8ad97969198a8e','gqa.s':'22040d83a202072f50609ae1960fc0880cf3139d55533087de0046a097da7ab8'}
    return dict(source_sha256=sha(source),receipt_sha256=sha(d/'compile-check.json'),record=r,scope='编译证据；不自动授历史/tail/Graph/reducer/性能资格')
