"""新增BN/完整A对照和resource门的CPU合同，不模拟设备除法。"""
from pathlib import Path
from types import SimpleNamespace as S
import ast,hashlib,importlib.util,json,copy
P=Path(__file__).resolve().parent;OLD=P.parent/'lm-head-temperature-r32-epilogue-component-20261027'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('head_bn256_factory',P/'factory.py');f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class Tensor:
    def __init__(self,shape):self.shape=shape
    def is_contiguous(self):return True
x,w,t,out=Tensor((32,2048)),Tensor((130560,2048)),Tensor((32,)),Tensor((32,130560))
calls=[]
class Kernel:
    def __getitem__(self,grid):
        def invoke(*args,**kwargs):calls.append((grid,args,kwargs));return S()
        return invoke
candidate=S(head_temperature_kernel=Kernel())
record=dict(args=(None,None,None,None,32,130560,2048,2048,1,2048,1,130560,1,0),grid=(2040,1),
    constants=dict(BLOCK_M=32,BLOCK_N=64,BLOCK_K=64,num_warps=8,num_stages=1,num_ctas=1,EVEN_K=True),kwargs=dict(BIAS=False,GROUP_M=8,SPLIT_K=1))
f.qualify_original_record(record)
for wide in (False,True):f.launch(candidate,record,x,w,t,out,wide=wide)
a,b=calls
assert a[0]==(2040,1) and b[0]==(510,1) and a[1]==b[1] and a[1][:4]==(x,w,w,out) and a[1][-1] is t
assert {k for k in a[2].keys()|b[2].keys() if a[2].get(k)!=b[2].get(k)}=={'BLOCK_N'}
assert a[2]['BLOCK_N']==64 and b[2]['BLOCK_N']==256
assert record['constants']['BLOCK_N']==64 and record['grid']==(2040,1),'不可改原capture记录'
for key,value in (('BLOCK_N',128),('BLOCK_K',32),('num_warps',16),('num_stages',2)):
    bad=copy.deepcopy(record);bad['constants'][key]=value
    try:f.qualify_original_record(bad)
    except AssertionError:pass
    else:raise AssertionError('接受改变的原配置')
assert 130560%256==0 and 2048%64==0 and 510*256==130560
assert sha(P/'candidate.py')==sha(OLD/'candidate.py')=='4c800693a2ae134fc580382d4166091b4c48e96dc2b7838ab417da7094cb2537'
dump=lambda n:ast.dump(n,include_attributes=False)
def function(path,name):return next(n for n in ast.parse(path.read_text(encoding='utf-8')).body if isinstance(n,ast.FunctionDef) and n.name==name)
oldw,neww=function(OLD/'worker.py','worker'),function(P/'worker.py','worker')
for name in ('rng','reset','equal_rng','observe','preserve'):
    get=lambda n:next(x for x in ast.walk(n) if isinstance(x,ast.FunctionDef) and x.name==name)
    assert dump(get(oldw))==dump(get(neww)),name
abba=lambda n:next(x for x in ast.walk(n) if isinstance(x,ast.For) and isinstance(x.iter,ast.Constant) and x.iter.value=='ABBA')
assert dump(abba(oldw))==dump(abba(neww))
om,nm=function(OLD/'entry.py','main'),function(P/'entry.py','main')
ot=next(n for n in om.body if isinstance(n,ast.Try));nt=next(n for n in nm.body if isinstance(n,ast.Try))
assert dump(ast.Module(body=ot.finalbody,type_ignores=[]))==dump(ast.Module(body=nt.finalbody,type_ignores=[]))
for name in ('base-source-manifest.json','installed-linear.py','installed-manifest.json','monitor_gpu.sh','reused_helpers.py','source_identity.py','candidate.py','kernel.diff'):
    assert (P/name).read_bytes()==(OLD/name).read_bytes(),name
# 实际新worker resource gate三句只读metadata：0spill通过，spill/缺项/旧A hash错拒绝。
nodes=list(ast.walk(neww));assign=next(n for n in nodes if isinstance(n,ast.Assign) and ast.unparse(n.targets[0])=="result['resource_gate']")
hard=next(n for n in nodes if isinstance(n,ast.Assert) and 'resource_gate' in ast.unparse(n.test))
gate_code=compile(ast.fix_missing_locations(ast.Module(body=[assign,hard],type_ignores=[])),'<actual-resource-gate>','exec')
digest='bacf34cbfb5b4a100448451f4a6f6eccf5309b10dad7e87b7e9259c023152c9e'
def resources(spills=0,n_regs=21,hash_a=digest):
    return {'A':S(n_spills=0,n_regs=21,metadata=S(hash=hash_a,shared=12288)),'B':S(n_spills=spills,n_regs=n_regs,metadata=S(hash='b'*64,shared=36864))}
for latest,allowed in ((resources(),True),(resources(spills=1),False),(resources(spills=None),False),(resources(n_regs=None),False),(resources(hash_a='a'*64),False)):
    scope=dict(latest=latest,result={'baseline_epilogue_expected_hash':digest})
    try:exec(gate_code,scope)
    except AssertionError:assert not allowed
    else:assert allowed
for file in P.glob('*.py'):ast.parse(file.read_text(encoding='utf-8'))
receipt=dict(cpu_only=True,kernel_bytes_unchanged=True,A_is_tested_epilogue_not_Flinear_timing=True,only_BN_and_grid_launch_difference=True,BN64_record_unmutated=True,old_rng_observer_resource_save_helpers_unchanged=True,original_ABBA_AST_equal=True,owner_finally_AST_equal=True,resource_gate_cases=5,original_configuration_mutants_rejected=4,numeric_device_qualification=False,rows=32,vocab=130560,scope='唯一BN256/w8/s1；未编译、未GPU/SSH/队列')
(P/'cpu-check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('BN256 incremental contracts passed')
