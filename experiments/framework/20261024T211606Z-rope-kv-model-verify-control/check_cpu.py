"""仅新增FX绑定的标准库夹具；不导入Torch、不执行模型或设备。"""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rope_graph


def fixture():
    lines = ['def forward(self, qkv, pos, table, out):']
    for i in range(42):
        lines += [f'    fused_{i} = torch.ops.vllm.biv150_rope_kv.default(qkv, pos, table, "model.layers.{i}.self_attn.attn")',
                  f'    query_{i}: "bf16[s0, 2048]" = fused_{i}[0]',
                  f'    key_{i}: "bf16[s0, 256]" = operator.getitem(fused_{i}, 1)',
                  f'    dep_{i}: "bf16[0]" = fused_{i}[2]',
                  f'    fused_{i} = None',
                  f'    qview_{i}: "bf16[s0,16,128]" = query_{i}.view(-1,16,128)',
                  f'    kview_{i}: "bf16[s0,2,128]" = key_{i}.reshape(-1,2,128)',
                  f'    a_{i} = torch.ops.vllm.unified_attention_with_output(qview_{i}, kview_{i}, qkv, out, "model.layers.{i}.self_attn.attn", kv_cache_dummy_dep=dep_{i})']
    return '\n'.join(lines)+'\n'


def main():
    checks = []
    def run(name, action):
        action();checks.append({'name': name, 'passed': True})
    def accept(text):
        result = rope_graph.inspect_graph(text)
        assert result['fusion_count'] == result['attention_consumers'] == 42
    def reject(text):
        try:rope_graph.inspect_graph(text)
        except ValueError:return
        raise AssertionError('应拒绝的FX通过')
    text = fixture()
    run('42层typed Assign/AnnAssign/getitem/view真实接口布局', lambda: accept(text))
    run('错层dep拒绝', lambda: reject(text.replace('kv_cache_dummy_dep=dep_1)', 'kv_cache_dummy_dep=dep_0)')))
    run('旧KV写入拒绝', lambda: reject(text+'    old = torch.ops.vllm.unified_kv_cache_update(k,v,"model.layers.0.self_attn.attn")\n'))
    run('缺少一层拒绝', lambda: reject('\n'.join(x for x in text.splitlines() if not x.startswith('    a_41 ='))))
    run('QK返回交换拒绝', lambda: reject(text.replace('fused_0[0]', 'fused_0[1]')))
    run('layer标签错位拒绝', lambda: reject(text.replace('"model.layers.1.self_attn.attn", kv_cache', '"model.layers.0.self_attn.attn", kv_cache')))
    run('已释放fusion变量不得重新伪绑定', lambda: reject(text.replace('qview_0: "bf16[s0,16,128]" = query_0.view(-1,16,128)', 'qview_0 = fused_0[0]')))
    def syntax():
        for name in ('verify_service.py','graph_gate.py','rope_graph.py'):
            tree=ast.parse((HERE/name).read_text(encoding='utf-8'))
            assert not any(isinstance(n,ast.Import) and any(a.name.split('.')[0]=='torch' for a in n.names)
                           or isinstance(n,ast.ImportFrom) and (n.module or '').split('.')[0]=='torch'
                           for n in ast.walk(tree))
        import verify_service
        assert 'torch' not in sys.modules
    run('新增入口语法和CPU导入无Torch', syntax)
    manifest=json.loads((HERE/'source-manifest.json').read_bytes())
    assert manifest['source_count']==528 and manifest['tree']=='57bb317de9d9040e3e52b27dc3b91ecc52eaae5e'
    report={'passed':True,'new_checks':checks,'device_run':False,
            'fixture_limitation':'模拟真实FX语法/接口的解析夹具，实际528图仍待同服务读取，不能冒充设备覆盖',
            'sha256':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest()
                      for name in ('verify_service.py','graph_gate.py','rope_graph.py','source-manifest.json')}}
    (HERE/'cpu-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'passed':True,'new_checks':len(checks),'device_run':False}))


if __name__=='__main__':main()
