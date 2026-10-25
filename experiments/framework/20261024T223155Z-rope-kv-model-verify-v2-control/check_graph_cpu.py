"""实际211606失败FX的CPU事后回放及错连负例；不恢复原轮模型资格。"""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import rope_graph

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
FX=ROOT/'tmp/rope-kv-model-verify/failed-original/failed-posthoc/0-computation_graph.py'
text=FX.read_text(encoding='utf-8')
source=ast.parse(text)
checks=[]
def good(name,action):action();checks.append({'name':name,'passed':True})
def rejection(change):
    model=copy.deepcopy(source);change(model)
    try:rope_graph.inspect_graph(ast.unparse(model))
    except ValueError:return
    raise AssertionError('错误调用图不应通过')
def subcall(model,name):
    return next(n for n in ast.walk(model) if isinstance(n,ast.Call) and rope_graph.dotted(n.func)=='self.'+name)
def attn(model):
    return next(n for n in ast.walk(model) if isinstance(n,ast.Call) and rope_graph.dotted(n.func) in rope_graph.ATTENTION)
def cls(model,name):return next(n for n in ast.walk(model) if isinstance(n,ast.ClassDef) and n.name==name)
def fn(model,name):return next(n for n in cls(model,name).body if isinstance(n,ast.FunctionDef) and n.name=='forward')

evidence=rope_graph.inspect_graph(text)
assert evidence['fusion_count']==evidence['attention_consumers']==42
assert len(evidence['module_invocations'])==86
checks.append({'name':'211606原始FX：顶层与85子模块真实参数/返回传播闭合42层Q/K/dep','passed':True})
old_path=ROOT/'tmp/rope-kv-model-verify/rope_graph.py'
spec=importlib.util.spec_from_file_location('original_rope_graph',old_path)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
try:old.inspect_graph(text)
except ValueError as error:original_rejection=str(error)
else:raise AssertionError('原解析器应重现本轮误拒')
checks.append({'name':'原解析器在同一FX重现原错误，原文件/资格不改','passed':True})

def swapped_inputs(model):
    n=subcall(model,'submod_1');n.args[0],n.args[2]=n.args[2],n.args[0]
good('顶层向Attention子模块交换Q/K实参必须拒绝',lambda:rejection(swapped_inputs))
def wrong_dep(model):
    n=subcall(model,'submod_1');n.args[5]=copy.deepcopy(n.args[2])
good('顶层将K作为dep传入必须拒绝',lambda:rejection(wrong_dep))
def wrong_return(model):
    ret=next(n for n in fn(model,'submod_0').body if isinstance(n,ast.Return));ret.value.elts[4]=copy.deepcopy(ret.value.elts[0])
good('生产子模块返回tuple中的dep槽错接必须拒绝',lambda:rejection(wrong_return))
def wrong_layer(model):attn(model).args[4]=ast.Constant('model.layers.1.self_attn.attn')
good('Attention层号与实际融合来源不符必须拒绝',lambda:rejection(wrong_layer))
def old_update(model):
    fn(model,'submod_1').body.insert(0,ast.parse("torch.ops.vllm.unified_kv_cache_update(k, v, 'model.layers.0.self_attn.attn')").body[0])
good('残留旧KV写入必须拒绝',lambda:rejection(old_update))
def missing_call(model):
    outer=fn(model,'GraphModule')
    outer.body=[n for n in outer.body if not (isinstance(n,ast.Assign) and isinstance(n.value,ast.Call)
                 and rope_graph.dotted(n.value.func)=='self.submod_1')]
good('仅定义而未从顶层调用的Attention不得计入42层',lambda:rejection(missing_call))
assert 'torch' not in sys.modules
report={'passed':True,'checks':checks,'raw_fx_path':str(FX.relative_to(ROOT)).replace('\\','/'),
        'raw_fx_sha256':hashlib.sha256(FX.read_bytes()).hexdigest(),
        'parser_sha256':hashlib.sha256((HERE/'rope_graph.py').read_bytes()).hexdigest(),
        'graph_gate_sha256':hashlib.sha256((HERE/'graph_gate.py').read_bytes()).hexdigest(),
        'original_parser_rejection':original_rejection,'posthoc_graph':evidence,
        'original_run_qualification_changed':False,'device_run':False,
        'limitations':'只证明旧原件的跨模块静态依赖；原211606仍失败，生产cache位置修改后的新tree须新真实服务验证。'}
(HERE/'graph-replay-cpu.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ('passed','raw_fx_sha256','parser_sha256','graph_gate_sha256','original_run_qualification_changed','device_run')}|{'checks':len(checks),'fusions':42,'module_invocations':len(evidence['module_invocations'])},ensure_ascii=False))
