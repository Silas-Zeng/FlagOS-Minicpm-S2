"""唯一新增CPU合同；真实IR文本＋JIT/编译器stub，不导入设备框架。"""
import hashlib
import ast
import importlib.util
import json
import sys
import tempfile
import time
import types
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode=True
start=time.perf_counter_ns()
here=Path(__file__).resolve().parent
root=here.parents[1]
policy_path=here/'biv150_q_fragment_hoist.py'
spec=importlib.util.spec_from_file_location('q_hoist_cpu_policy',policy_path)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
ir_dir=root/'analysis/source/current-attention-ir'
raw=(ir_dir/'baseline.ttgir').read_bytes()
changed=p.transform_ir(raw)
old=raw.decode().splitlines(keepends=True)
new=changed.decode().splitlines(keepends=True)
line=next(x for x in old if '%Q_222 = ttg.local_load %Q_131' in x)
loop=next(i for i,x in enumerate(old) if '= scf.for ' in x)
at=old.index(line)
reverse=new.copy();assert reverse.pop(loop)==line[2:];reverse.insert(at,line)
assert reverse==old
for needle in ('ttg.local_alloc %Q_130','scf.yield','tt.dot '):
    assert [x for x in old if needle in x]==[x for x in new if needle in x]
for mutated in (raw+b'\n',raw.replace(b'%Q_222',b'%Q_CHANGED',1)):
    try:p.transform_ir(mutated)
    except RuntimeError:pass
    else:raise AssertionError('changed original IR accepted')
baseline_proof=p.lowered_proof(raw.decode(),(ir_dir/'baseline.llir').read_text(encoding='utf-8'))
assert not baseline_proof['mechanism_pass'] and baseline_proof['llvm_q_memory_reads_in_loop']==16
fake_llir='''define void @k() {
entry:
  %q = load <2 x bfloat>, ptr addrspace(3) %ptr, align 4, !dbg !52
  br label %loop
loop:
  br i1 %again, label %loop, label %exit
exit:
  ret void
}
!52 = !DILocation(line: 352, column: 12, scope: !8)
'''
assert p.lowered_proof(changed.decode(),fake_llir)['mechanism_pass']

class Tensor:
    def __init__(self,ptr,shape=(2048,16,128),stride=(2048,128,1)):
        self.ptr=ptr;self.shape=shape;self._stride=stride
        self.dtype='torch.bfloat16';self.device=types.SimpleNamespace(index=0)
    def data_ptr(self):return self.ptr
    def stride(self):return self._stride

NS=types.SimpleNamespace
jit_file=root/'experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/runtime/jit.py'
compiler_file=root/'experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/compiler/compiler.py'
backend_file=root/'experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/backends/iluvatar/compiler.py'
c2_file=root/'patches/framework/biv150_decode_launch_runtime.py'
interface_file=root/'experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/kv_cache_interface.py'
interface_tree=ast.parse(interface_file.read_text(encoding='utf-8'))
quant_class=next(x for x in interface_tree.body if isinstance(x,ast.ClassDef) and x.name=='KVQuantMode')
enum_globals={'IntEnum':p.IntEnum,'__name__':'vllm.v1.kv_cache_interface'}
exec(compile(ast.Module(body=[quant_class],type_ignores=[]),str(interface_file),'exec'),enum_globals)
knobs=NS(compilation=NS(override=False,instrumentation_mode=''),
         runtime=NS(debug=False,add_stages_inspection_hook=None),language=NS(default_fp_fusion=True))
calls=[];failure=None
class Compiled:
    def __init__(self,candidate=False):
        self.hash='candidate' if candidate else 'original'
        self.src=NS(signature={'q':'*bf16'},constants={(0,):False},attrs={(1,):[['tt.divisibility',4]]})
        self.asm={'ttgir':changed.decode() if candidate else raw.decode(),
                  'llir':fake_llir if candidate else (ir_dir/'baseline.llir').read_text(encoding='utf-8')}
        self.metadata=NS(num_warps=8,num_stages=1,shared=32768 if candidate else 65536)
        self.n_regs=118 if candidate else 102;self.n_spills=0
base_compiled=Compiled();candidate_compiled=Compiled(True)
def binder(**kw):
    return dict(kw),[('ptr',str(kw['query_ptr'].dtype)),('scalar',kw.get('scale',1.0))],{'num_warps':8}
class JIT:
    def __init__(self,fn,version=None,do_not_specialize=None,do_not_specialize_on_alignment=None,
                 debug=None,noinline=None,repr=None,launch_metadata=None):
        self.fn=fn;self.version=version;self.do_not_specialize=do_not_specialize or []
        self.do_not_specialize_on_alignment=do_not_specialize_on_alignment or []
        self.debug=debug;self.noinline=noinline;self._repr=repr;self.launch_metadata=launch_metadata
        self.pre_run_hooks=[];self.device_caches={}
    def __getitem__(self,grid):
        def call(*a,**kw):return self.run(*a,grid=grid,**kw)
        return call
run_globals={'knobs':knobs,'calls':calls,'base_compiled':base_compiled,
             'candidate_compiled':candidate_compiled,'failure':None}
exec(compile('def run(self,*args,grid=None,**kwargs):\n    calls.append((self,args,kwargs,grid))\n    if failure is not None: raise failure\n    return candidate_compiled if "ir_override" in kwargs else base_compiled\n',str(jit_file),'exec'),run_globals)
JIT.run=run_globals['run']
# Factory source identities are real-file guards; only execution bodies are stubs.
JIT.__init__.__code__=JIT.__init__.__code__.replace(co_filename=str(jit_file))
Compiled.__init__.__code__=Compiled.__init__.__code__.replace(co_filename=str(compiler_file))
exec(compile('def init_handles(self): pass',str(compiler_file),'exec'),run_globals)
Compiled._init_handles=run_globals['init_handles']
def fn():pass
raw_jit=JIT(fn,version=7,do_not_specialize=[0],debug=False,noinline=False)
raw_jit.device_caches[0]=({'base':base_compiled},{'key':'base'},'cuda:71',None,binder)
class C2:
    def __init__(self,original):self.original=original
c2_globals={}
exec(compile('def getitem(self,grid):\n    return self.original[grid]\n',str(c2_file),'exec'),c2_globals)
C2.__getitem__=c2_globals['getitem']
attention=types.ModuleType('cpu_attention')
attention.__file__=str(root/'tmp/remote-source/triton_unified_attention.py')
attention.current_platform=NS(vendor_name='iluvatar')
attention.KVQuantMode=enum_globals['KVQuantMode']
exec('def unified_attention(): pass',vars(attention))
attention.kernel_unified_attention=C2(raw_jit)
backend=NS(__file__=str(root/'tmp/remote-source/triton_attn.py'),
           unified_attention=attention.unified_attention,TritonAttentionImpl=NS(forward=object()))
helpers=NS(__file__=str(root/'tmp/remote-source/triton_attention_helpers.py'))
modules={'triton.runtime.jit':NS(__file__=str(jit_file),JITFunction=JIT),
         'triton.compiler.compiler':NS(__file__=str(compiler_file),CompiledKernel=Compiled),
         'triton.backends.iluvatar.compiler':NS(__file__=str(backend_file))}
with patch('importlib.import_module',side_effect=lambda name:modules[name]):
    m=p.create(attention,helpers,backend)
assert m.candidate is not raw_jit and m.candidate.fn is raw_jit.fn
assert m.candidate.device_caches is not raw_jit.device_caches
original=attention.kernel_unified_attention
values={'query_ptr':Tensor(256),'output_ptr':Tensor(512),'scale':1.0,'IS_3D':False,
        'KV_QUANT_MODE':attention.KVQuantMode.NONE}
old_eligible=p._eligible
p._eligible=lambda values:values.get('IS_3D') is False
with tempfile.TemporaryDirectory(prefix='q-hoist-contract-') as temp:
    m.artifact_dir=Path(temp)
    with patch.object(p.inspect,'getsourcefile',return_value=str(compiler_file)):
        m.install_baseline_observer();assert attention.kernel_unified_attention[(128,2,1)](**values) is base_compiled
    m.restore();state=m._original_cache()
    m.install();assert attention.kernel_unified_attention[(128,2,1)](**values) is candidate_compiled
    assert calls[-1][2]['query_ptr'] is values['query_ptr']
    fresh=dict(values,query_ptr=Tensor(768),output_ptr=Tensor(1024))
    original_read=Path.read_bytes
    def no_hot_ir_read(path):
        if path==m.ir_path: raise AssertionError('timing hot path read IR')
        return original_read(path)
    with patch.object(Path,'read_bytes',no_hot_ir_read):
        assert attention.kernel_unified_attention[(128,2,1)](**fresh) is candidate_compiled
    assert calls[-1][2]['query_ptr'] is fresh['query_ptr'] and calls[-1][2]['output_ptr'] is fresh['output_ptr']
    assert m._original_cache()==state and m.mechanism['mechanism_pass']
    for changed_values in (dict(fresh,scale=0.5),dict(fresh,query_ptr=Tensor(768,(2016,16,128))),
                           dict(fresh,query_ptr=Tensor(770)),dict(fresh,IS_3D=True)):
        assert attention.kernel_unified_attention[(128,2,1)](**changed_values) is base_compiled
        assert 'ir_override' not in calls[-1][2]
    n=len(calls);error=RuntimeError('original launch error')
    run_globals['failure']=error
    try:attention.kernel_unified_attention[(128,2,1)](**fresh)
    except RuntimeError as caught:assert caught is error and caught.__context__ is None
    else:raise AssertionError('launch error lost')
    assert len(calls)==n+1
    run_globals['failure']=None
    m.ir_path.write_bytes(b'changed')
    n=len(calls)
    try:m.verify_ir()
    except RuntimeError:pass
    else:raise AssertionError('IR content mutation accepted')
    assert len(calls)==n
    m.restore();assert attention.kernel_unified_attention is original and not m.active
p._eligible=old_eligible
assert not any(x in sys.modules for x in ('torch','triton','vllm'))
receipt={'status':'pass','elapsed_seconds':(time.perf_counter_ns()-start)/1e9,
         'policy_sha256':hashlib.sha256(policy_path.read_bytes()).hexdigest(),
         'original_ttgir_sha256':p.EXPECTED_TTGIR,'hoisted_ttgir_sha256':hashlib.sha256(changed).hexdigest(),
         'baseline_llvm_q_memory_reads_in_loop':baseline_proof['llvm_q_memory_reads_in_loop'],
         'checks':['exact single-local_load move inverse; Q allocation/dot/yield retained',
                   'unknown original IR rejected','real baseline LLVM CFG observes 16 repeated Q reads',
                   'fake hoisted LLVM CFG and TTGIR mechanism parser accepts outside-loop reads',
                   'actual source-pinned clone factory via stub imports; private cache identity',
                   'native-binder specialization/options recipe; current Q/output pointers',
                   'actual KVQuantMode AST IntEnum kept as original argument; explicit scalar freezing',
                   'hot cached path does not read the IR file; explicit boundary SHA verification',
                   'scalar/shape/alignment/3D fallback; original cache unchanged',
                   'same launch exception object/context once; changed IR content rejects; exact restore'],
         'limits':'Only CPU IR text and isolated JIT/compiler stubs. No Torch/Triton import, actual compilation, barriers, resources, device bytes or timing proof.'}
(here/'cpu-check.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False))
