"""只核新形状回执、KV条件分离及未变官方控制/清理；不运行设备。"""
from pathlib import Path
from types import SimpleNamespace,ModuleType
import ast,hashlib,importlib.util,json,sys,tempfile
P=Path(__file__).resolve().parent;OLD=P.parent/'lm-head-temperature-official-16k-20261027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
head=load('head_activation',P/'head_activation.py')
def markers(rows):
    grid={32:[2040,1],64:[510,1]}[rows]
    return ('BIV150_HEAD_TEMPERATURE_SELECTED '+repr(dict(rows=rows,grid=grid,hash='a'*64))+'\n'
        +'BIV150_HEAD_TEMPERATURE_SAMPLED '+repr(dict(rows=rows,chain='original stats/top-p/softmax/noise; temperature consumed once'))+'\n')
ready='BIV150_HEAD_TEMPERATURE_READY rows32/BM32/BN64/BK64/w8/s1;rows64/BM64/BN256/BK32/w16/s2\n'
cases=[('',True,False), (ready,True,False), (ready+markers(32),True,True), (ready+markers(64),True,True),
    (ready+markers(32)+markers(64),True,True),
    (ready+markers(32).splitlines(True)[0],False,False),
    (ready+markers(32)+markers(64).splitlines(True)[0],False,False),
    (ready+markers(32).splitlines(True)[0]+markers(64).splitlines(True)[1],False,False),
    (ready+markers(32).replace("'rows': 32","'rows': 40"),False,False),
    (ready+markers(32).replace('[2040, 1]','[510, 1]'),False,False),
    (ready+'BIV150_HEAD_TEMPERATURE_SAMPLED malformed\n',False,False),
    (ready+'BIV150_HEAD_TEMPERATURE_REJECTED reason\n',False,False),
    (ready+'BIV150_HEAD_TEMPERATURE_RAW_FALLBACK reason\n',False,False)]
with tempfile.TemporaryDirectory(dir=P.parent) as tmp:
    log=Path(tmp)/'server.log'
    for text,allowed,covered in cases:
        log.write_text(text,encoding='utf-8');record=head.capture(log)
        assert head.optional_scope_valid(record)==allowed and record['covered']==covered,(text,record)
    sys.path.insert(0,str(P));sup=load('head_r32_r64_official_cpu',P/'official_supervisor.py')
    activation=ModuleType('activation_evidence');activation.stack_evidence=lambda p:dict(valid=True);sys.modules['activation_evidence']=activation
    log.write_text(ready+markers(32)+'GPU KV cache size: 548,384 tokens\n',encoding='utf-8')
    equal=sup.first_round_stack(log,{'kv_tokens':548384});assert equal['valid'] and equal['compare_kv_match'] is True
    unequal=sup.first_round_stack(log,{'kv_tokens':548288});assert unequal['valid'] and unequal['compare_kv_match'] is False
    log.write_text(ready+markers(32),encoding='utf-8');missing=sup.first_round_stack(log,{'kv_tokens':548384});assert not missing['valid'] and missing['compare_kv_match'] is None
    log.write_text(ready+markers(32)+'GPU KV cache size: 548,384 tokens\nGPU KV cache size: 548,288 tokens\n',encoding='utf-8')
    assert not sup.first_round_stack(log,{'kv_tokens':548384})['valid']
    log.write_text(ready+markers(32)+'GPU KV cache size: 0 tokens\n',encoding='utf-8')
    assert not sup.first_round_stack(log,{'kv_tokens':548384})['valid']
    log.write_text(ready+markers(32)+'GPU KV cache size: 548,384 tokens\n',encoding='utf-8')
    activation.stack_evidence=lambda p:dict(valid=False);assert not sup.first_round_stack(log,{'kv_tokens':548384})['valid']
    def row(rate,status='SUCCESS'):
        return {'Prefill':'16384','Decode':'1024','Conc':'64','Num Prompts':'128','Run Status':status,'Successful Requests':'128','Total tok/s':str(rate)}
    assert sup.new_row_decision([row(4000),row(4528)],0,{16384:4529})['kind']=='performance'
    assert sup.new_row_decision([row(4000),row(4530),row(4400),row(4410)],0,{16384:4529}) is None
    assert sup.new_row_decision([row(4000),row(4530,'FAIL')],0,{16384:4529})['kind']=='runtime_error'
def main_try(path):
    m=next(n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name=='main')
    return m,next(n for n in m.body if isinstance(n,ast.Try))
dump=lambda n:ast.dump(n,include_attributes=False)
for name in ('official_owner.py','official_supervisor.py'):
    old,ot=main_try(OLD/name);new,nt=main_try(P/name)
    assert dump(ast.Module(body=ot.finalbody,type_ignores=[]))==dump(ast.Module(body=nt.finalbody,type_ignores=[])),name
    assignment=lambda m:next(n for n in ast.walk(m) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='command' for t in n.targets))
    assert dump(assignment(old))==dump(assignment(new)),name
for name in ('case_driver.py','baseline_reference.py','base_qualification.py','activation_evidence.py','cache_gate.py','graph_gate.py','lifecycle.py','provider_evidence.py','q32_evidence.py','team-source-manifest.json'):
    assert (OLD/name).read_bytes()==(P/name).read_bytes(),name
for file in P.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'))
result=dict(cpu_only=True,parser_cases=len(cases),per_shape_selected_sampled_closed=True,kv_equal_valid=True,kv_unequal_valid_but_compare_false=True,kv_missing_or_conflicting_rejected=True,original_stack_false_rejected=True,firstwarm_negative_stop=True,positive_then_four_rounds=True,runtime_error_stop=True,owner_supervisor_command_and_finally_ast_equal=True,baseline_fixed='20261027T075834Z-main56-control-16k-four-rounds',original_case_driver_sha256=sha(P/'case_driver.py'),production_source_tar_sha256='8d1a3de438f460bdc021d8bcb4a7ac66c1915a569ec8539f1392c3ec9c44f309',limitations='没有设备/SSH；KV不匹配只允许继续观测，不等于严格因果可比或官方准确率资格。')
(P/'cpu-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('new official contracts passed')
