"""仅验证新增提取/输入合同，不导入Torch，不执行任何设备代码。"""
import ast
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
assert 'torch' not in sys.modules
for path in HERE.glob('*.py'): compile(path.read_text(encoding='utf-8'),str(path),'exec')
module=runpy.run_path(str(HERE/'component.py'))
assert 'torch' not in sys.modules
indices=module['checked_indices']
for m,s in module['CASES']:
    for version in (0,1,2):
        x=indices(m,s,version,identity=m==s)
        assert len(x)==s and min(x)>=0 and max(x)<m
        if m==s: assert x==tuple(range(m))
        else:
            assert x!=tuple(sorted(x))
            if version: assert x[0]==x[-1]
for args,kw in [((0,0),{}),((32,64),{}),((2048,32),{'identity':True})]:
    try: indices(*args,**kw)
    except ValueError: pass
    else: raise AssertionError('非法indices合同未拒绝')
extraction=json.loads((HERE/'extraction.json').read_bytes())
assert extraction['suffix_ast_identical'] and extraction['kernel_assignments_ast_identical']
actual=hashlib.sha256((HERE/'exact_suffix.py').read_bytes()).hexdigest()
assert actual==extraction['generated_sha256']
llama=ast.parse((HERE/'source/llama.py').read_text(encoding='utf-8'))
mapping=next(n.value for n in ast.walk(llama) if isinstance(n,ast.Assign)
             and any(isinstance(x,ast.Name) and x.id=='stacked_params_mapping' for x in n.targets))
items=ast.literal_eval(mapping)
assert ('.gate_up_proj','.gate_proj',0) in items and ('.gate_up_proj','.up_proj',1) in items
assert 'torch' not in sys.modules
result={'passed':True,'checks':['各资产语法','纯标准库导入未加载Torch','四shape精确保序/重复/identity输入合同',
        '非法输入拒绝','三kernel和suffix数学AST逆回一致','真实Llama gate/up shard0/1映射一致'],
        'gpu_executed':False,'weights_loaded':False,'numerical_pass_claimed':False}
(HERE/'cpu-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
