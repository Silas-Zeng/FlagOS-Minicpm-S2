"""仅CPU：执行实际pack/unpack函数、地址/选择器/原dot合同；不import GPU库。"""
from pathlib import Path
from types import SimpleNamespace
import ast
import copy
import hashlib
import json
import subprocess
import numpy as np
from ir_contract import b_sme_contract

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
N,K,PN,BK=2048,6144,128,64
JIT=ROOT/'experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/runtime/jit.py'
JIT_SHA='66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775'


class CPUArray:
    dtype='bf16'
    device=SimpleNamespace(type='cpu')
    def __init__(self,array):self.a=array
    @property
    def shape(self):return self.a.shape
    def is_contiguous(self):return self.a.flags.c_contiguous
    def reshape(self,*shape):return CPUArray(self.a.reshape(*shape))
    def permute(self,*dims):return CPUArray(self.a.transpose(*dims))
    def contiguous(self):return CPUArray(np.ascontiguousarray(self.a))


def main():
    tree=ast.parse((HERE/'candidate.py').read_bytes())
    fns=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('pack_cpu','unpack_cpu')]
    scope=dict(torch=SimpleNamespace(bfloat16='bf16'))
    exec(compile(ast.Module(body=fns,type_ignores=[]),'actual-pack-functions','exec'),scope)
    w=(np.arange(N*K,dtype=np.uint32)%65536).astype(np.uint16).reshape(N,K)
    p=scope['pack_cpu'](CPUArray(w)).a
    restored=scope['unpack_cpu'](CPUArray(p)).a
    assert p.shape==(16,K,128) and p.flags.c_contiguous
    assert np.array_equal(w,restored) and p.nbytes==w.nbytes==25165824
    assert np.all(np.bincount(p.flatten().astype(np.int64),minlength=65536)==N*K//65536)
    flat=p.reshape(-1);tiles=0
    for bn in (32,64,128):
        for bk in (32,64,128):
            for pn in range(N//bn):
                ns=np.arange(pn*bn,(pn+1)*bn,dtype=np.int64)
                pointer=(pn*bn//128)*K*128+np.arange(bk,dtype=np.int64)[:,None]*128+(pn*bn%128+np.arange(bn,dtype=np.int64))[None,:]
                for block in range(K//bk):
                    ks=np.arange(block*bk,(block+1)*bk,dtype=np.int64)
                    closed=(ns[None,:]//128)*K*128+ks[:,None]*128+ns[None,:]%128
                    assert np.array_equal(pointer,closed)
                    assert np.array_equal(flat[pointer],w[ns[:,None],ks[None,:]].T)
                    pointer+=bk*128;tiles+=1
    source=subprocess.check_output(['git','-C',str(ROOT/'collaboration/FlagGems'),'show',
        '4df52d9168ac55c1c1061cefb4638c570292d896:src/flag_gems/runtime/backend/_iluvatar/ops/linear.py'])
    dot=lambda t:next(n for n in ast.walk(t) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='dot')
    assert ast.dump(dot(tree),include_attributes=False)==ast.dump(dot(ast.parse(source)),include_attributes=False)
    kernel=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='nonly_other_rows_linear')
    loop=next(n for n in ast.walk(kernel) if isinstance(n,ast.For))
    assert not any(isinstance(n,(ast.If,ast.IfExp)) for n in ast.walk(loop))
    assert len([n for n in ast.walk(loop) if isinstance(n,ast.Call) and ast.unparse(n.func)=='tl.dot'])==1
    assert any(isinstance(n,ast.AugAssign) and ast.unparse(n.target)=='acc' and n.value is dot(tree) for n in ast.walk(loop))
    for m in (32,2048):
        for bm in (32,64,128,256):
            for bn in (32,64,128):
                gm=(m+bm-1)//bm;gn=N//bn;covered=[]
                for pid in range(gm*gn):
                    width=8*gn;g=pid//width;size=min(gm-g*8,8)
                    pm=g*8+pid%size;pn=(pid%width)//size
                    covered.append((pm,pn))
                    assert all(0<=r%m<m for r in range(pm*bm,(pm+1)*bm))
                assert len(set(covered))==gm*gn
                assert set(covered)=={(i,j) for i in range(gm) for j in range(gn)}
    assert hashlib.sha256(JIT.read_bytes()).hexdigest()==JIT_SHA
    select=copy.deepcopy(next(n for n in ast.parse(JIT.read_bytes()).body if isinstance(n,ast.FunctionDef) and n.name=='get_corex_sme'))
    select.body=[n for n in select.body if not isinstance(n,ast.Import)]
    class Tensor:
        dtype='bf16'
        def __init__(self,shape):self.shape=shape
        def dim(self):return len(self.shape)
        def squeeze(self):return Tensor(tuple(n for n in self.shape if n!=1))
        def is_contiguous(self):return True
        def element_size(self):return 2
    torch=SimpleNamespace(corex=True,float16='fp16',bfloat16='bf16',float32='fp32',int8='int8',is_tensor=lambda t:isinstance(t,Tensor))
    scope=dict(torch=torch,os=SimpleNamespace(getenv=lambda name,default=None:default))
    exec(compile(ast.Module(body=[select],type_ignores=[]),'exact-installed-selector','exec'),scope)
    mask=scope['get_corex_sme']([Tensor((64,K)),Tensor((16,K,PN)),Tensor((64,N))],[('ptr',None)]*3)
    old_mask=scope['get_corex_sme']([Tensor((64,K)),Tensor((N*K,)),Tensor((64,N))],[('ptr',None)]*3)
    assert mask==7 and old_mask==5
    original_ir=(ROOT/'archive/hotspot-layout-20261026/batch-101034/profiles/20261026T084521Z-main6971-production-hotspot-4k/triton-cache/CXXRLKRJTVIHMAOONGAO4S6VNEUBIJJJI4P3W7TD5KKHBXYEV5XQ/linear_kernel.ttgir').read_text(encoding='utf-8')
    original_sme=b_sme_contract(original_ir)
    assert original_sme['passed'] and original_sme['records'][0]['B_useSme_values']==[2]
    for mode in (1,2):
        fixture=f'%b = ttg.local_load %mb token %t : t -> tensor<64x128xbf16, #ttg.dot_op<{{opIdx = 1, useSme = {mode}}}>>\n%c = tt.dot %a, %b, %z'
        assert b_sme_contract(fixture)['passed']
    false_fixture='%a = ttg.local_load %ma token %t : t -> tensor<64x64xbf16, #ttg.dot_op<{opIdx = 0, useSme = 1}>>\n%b = ttg.local_load %mb token %t : t -> tensor<64x128xbf16, #ttg.dot_op<{opIdx = 1, useSme = 0}>>\n%c = tt.dot %a, %b, %z'
    assert not b_sme_contract(false_fixture)['passed']
    for name in ('candidate.py','worker.py','entry.py','dispatch_bootstrap.py','ir_contract.py'):
        ast.parse((HERE/name).read_bytes())
    result=dict(status='CPU_ONLY_NOT_GPU_QUALIFIED',actual_pack_unpack_functions_executed_on_numpy_interface=True,
        layout=[16,K,PN],tile_address_cases=tiles,full_uint16_bitwise=True,all_65536_patterns=True,
        original_dot_AST_identical=True,one_dot_per_original_K_step=True,constant_packed_step="actual_BK*128, no select",
        contiguous_tile_bytes=BK*PN*2,original_tile_address_span_bytes=((PN-1)*K+BK)*2,
        host_selector=dict(exact_installed_jit_sha256=JIT_SHA,nonly_3D_mask=mask,old_1D_mask=old_mask,
                           actual_compiled_SME_proven=False),
        B_SME_SSA_contract=dict(original_actual_IR=original_sme,new_row_or_col_fixture_pass=True,A_only_false_fixture_rejected=True),
        config="actual opaque capture; preserve BM/BK/warps/stages, preserve BN<=128 or explicit256->128",
        source_linear_sha256=hashlib.sha256(source).hexdigest(),
        candidate_sha256=hashlib.sha256((HERE/'candidate.py').read_bytes()).hexdigest(),
        unverified=['真实opaque新捕获config/kernel/DB','GPU逐位/有限性/FP64/Graph/side/尾M','实际SME方向与资源/完整Graph ABBA净性能'])
    (HERE/'cpu-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
