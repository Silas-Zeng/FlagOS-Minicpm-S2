"""仅标准库：从真实526 wrapper提取三个原kernel和o_proj之后的原计算体。"""
import ast
import hashlib
import json
from pathlib import Path
import textwrap

HERE = Path(__file__).resolve().parent
SOURCE_SHA = '32458fbd627192ecd69c70c7cfc6ac8363e926787f2e5fbe78fb3f9ee15b2b49'
NAMES = ('triton_red_fused_fused_add_rms_norm_0',
         'triton_poi_fused_mul_silu_slice_1',
         'triton_red_fused_fused_add_rms_norm_2')

def main():
    raw = (HERE/'source/wrapper-subgraph-42-0.py').read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    source = raw.decode('utf-8'); tree = ast.parse(source)
    assignments = {n.targets[0].id: n for n in tree.body
                   if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name)}
    kernels = []
    for name in NAMES:
        node = assignments[name]
        assert isinstance(node.value, ast.Call) and ast.unparse(node.value.func) == 'async_compile.triton'
        assert node.value.args[0].value == name
        kernels.append(ast.get_source_segment(source, node))
    runner = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Runner')
    call = next(n for n in runner.body if isinstance(n, ast.FunctionDef) and n.name == 'call')
    block = next(n for n in call.body if isinstance(n, ast.With))
    first = next(i for i,n in enumerate(block.body) if isinstance(n, ast.Assign)
                 and isinstance(n.targets[0], ast.Name) and n.targets[0].id == 'buf2')
    lines = source.splitlines()
    suffix = textwrap.dedent('\n'.join(lines[block.body[first].lineno-1:block.body[-1].end_lineno]))
    assert suffix.count('extern_kernels.mm(') == 2
    assert all(suffix.count(name+'.run(') == 1 for name in NAMES)
    header = '''# 从source/wrapper-subgraph-42-0.py实际AST提取；不执行文件首的历史docstring。
import torch
from torch._inductor.async_compile import AsyncCompile
from torch._inductor.select_algorithm import extern_kernels
from torch._C import _cuda_getCurrentRawStream as get_raw_stream
empty_strided_cuda = torch._C._dynamo.guards._empty_strided_cuda
reinterpret_tensor = torch._C._dynamo.guards._reinterpret_tensor
async_compile = AsyncCompile()
'''
    function = '''\ndef suffix(buf0, arg4_1, arg3_1, arg5_1, arg6_1, arg7_1):
    # buf0已经是self_attn返回的o_proj输出；本组件不计算/不计省o_proj。
    s72 = buf0.shape[0]
'''+textwrap.indent(suffix, '    ')+'\n    return buf7\n'
    generated = header+'\n\n'.join(kernels)+'\nasync_compile.wait(globals())\ndel async_compile\n'+function
    ast.parse(generated)
    (HERE/'exact_suffix.py').write_bytes(generated.encode('utf-8'))
    # 逆回只比实际数学/launch语句AST；删掉的仅DeviceGuard/完整o_proj段。
    out = ast.parse(generated)
    fn = next(n for n in out.body if isinstance(n, ast.FunctionDef))
    assert [ast.dump(n,include_attributes=False) for n in fn.body[1:-1]] == [
        ast.dump(n,include_attributes=False) for n in block.body[first:]]
    for name in NAMES:
        actual = next(n for n in out.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name)
        assert ast.dump(actual,include_attributes=False) == ast.dump(assignments[name],include_attributes=False)
    report = {'source_sha256': SOURCE_SHA, 'source_lines': [block.body[first].lineno, block.body[-1].end_lineno],
              'kernel_names': list(NAMES), 'kernel_assignments_ast_identical': True,
              'suffix_ast_identical': True, 'gemm_count': 2, 'triton_count': 3,
              'torch_imported_during_preparation': False,
              'generated_sha256': hashlib.sha256(generated.encode()).hexdigest()}
    (HERE/'extraction.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__ == '__main__': main()
