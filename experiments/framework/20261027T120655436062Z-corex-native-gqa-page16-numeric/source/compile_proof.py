"""只读核本次单TU编译回执；不加载Torch、不执行设备代码。"""
from pathlib import Path
import hashlib,json

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def check(directory,source):
    directory=Path(directory).resolve(strict=True)
    record=json.loads((directory/'compile-check.json').read_bytes())
    # Keep the original failed front-end-name check. This exact inspected binary
    # path has the same machine exp/float_mode; device P/underflow is still hard.
    equivalence=json.loads((Path(__file__).parent/'backend-equivalence.json').read_bytes())
    assert record['passed'] is False
    assert sorted(k for k,v in record['checks'].items() if v is not True)==['original_exp2_2'],'出现未审阅的其他编译差异'
    assert equivalence['passed'] is True and all(v is True for v in equivalence['checks'].values())
    assert equivalence['original_asm_sha256']=='38d71308898d01219a518b63d5578282a1cc38c37824ea55783915b275c28102'
    assert equivalence['float_mode']==12
    assert equivalence['source_sha256']==sha(source)
    assert equivalence['candidate_files']==record['files']
    assert equivalence['original_compile_check_sha256']==sha(directory/'compile-check.json')
    assert record['gpu_executed'] is False and record['numeric_qualified'] is False
    for name in ('page16.ll','page16.s'):
        assert sha(directory/name)==record['files'][name],'编译产物变化'
    assert (directory/'input.sha256').read_text().split()[0]==sha(source),'编译输入不是本次page16源'
    return dict(source_sha256=sha(source),receipt_sha256=sha(directory/'compile-check.json'),files=record['files'],checks=record['checks'],backend_equivalence=equivalence,compile_only=True,numeric_qualified=False)
