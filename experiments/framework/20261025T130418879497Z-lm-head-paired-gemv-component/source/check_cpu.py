"""执行新增 kernel 的 NumPy 语义：完整K、两行权重复用与输出写覆盖。"""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np

HERE=Path(__file__).resolve().parent


class Tensor(np.ndarray):
    def to(self,dtype): return self.astype(dtype).view(Tensor)


class Ptr:
    def __init__(self, array, offset=0, counts=None):
        self.array=array; self.offset=offset
        self.counts=np.zeros(array.size,dtype=np.int16) if counts is None else counts
    def __add__(self, offset):return Ptr(self.array,self.offset+offset,self.counts)


class TL:
    float32=np.float32
    pid=0
    @staticmethod
    def arange(a,b):return np.arange(a,b).view(Tensor)
    @staticmethod
    def zeros(shape,dtype):return np.zeros(shape,dtype=dtype).view(Tensor)
    def program_id(self,_):return self.pid
    @staticmethod
    def load(ptr,mask=True,other=0):
        offset=np.asarray(ptr.offset)
        mask=np.broadcast_to(mask,offset.shape)
        np.add.at(ptr.counts,offset[mask],1)
        return np.where(mask,ptr.array[np.clip(offset,0,len(ptr.array)-1)],other).view(Tensor)
    @staticmethod
    def store(ptr,value,mask=True):
        offset=np.asarray(ptr.offset); mask=np.broadcast_to(mask,offset.shape)
        ptr.array[offset[mask]]=np.asarray(value)[mask]
        np.add.at(ptr.counts,offset[mask],1)
    @staticmethod
    def sum(x,axis):return np.sum(x,axis=axis,dtype=np.float32).view(Tensor)


def main():
    source=(HERE/'candidate.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='paired_gemv_kernel')
    node.decorator_list=[]
    for arg in node.args.args:arg.annotation=None
    code=ast.fix_missing_locations(ast.Module(body=[node],type_ignores=[]))
    tl=TL();ns={'tl':tl};exec(compile(code,'actual-kernel-source','exec'),ns)
    rng=np.random.default_rng(20261025)
    checks=[]
    for n in (64,65):
        # 值截为BF16可精确表示；输入独立两行，完整2048归约。
        x=(rng.standard_normal((2,2048)).astype(np.float32).view(np.uint32)&np.uint32(0xffff0000)).view(np.float32)
        w=(rng.standard_normal((n,2048)).astype(np.float32).view(np.uint32)&np.uint32(0xffff0000)).view(np.float32)
        out=np.full((2,n),np.nan,np.float32)
        xp,wp,yp=Ptr(x.ravel()),Ptr(w.ravel()),Ptr(out.ravel())
        for pid in range((n+31)//32):
            tl.pid=pid;ns['paired_gemv_kernel'](xp,wp,yp,n,2048,32,256)
        ref=x.astype(np.float64)@w.astype(np.float64).T
        assert np.allclose(out,ref,rtol=2e-5,atol=2e-4)
        assert np.all(wp.counts==1) and np.all(yp.counts==1)
        checks.append(dict(N=n,max_abs_vs_fp64=float(np.abs(out-ref).max()),
            weight_reads=int(wp.counts.sum()),each_weight_read_once=True,each_output_written_once=True))
    reuse=json.loads((HERE/'reuse.json').read_text(encoding='utf-8'))
    for item in reuse:
        src=Path(item['source']).read_text(encoding='utf-8')
        fn=next(n for n in ast.parse(src).body if isinstance(n,ast.FunctionDef) and n.name==item['function'])
        copied=(HERE/'reused_helpers.py').read_text(encoding='utf-8')
        new=next(n for n in ast.parse(copied).body if isinstance(n,ast.FunctionDef) and n.name==item['function'])
        assert ast.get_source_segment(src,fn)==ast.get_source_segment(copied,new)
    for path in HERE.glob('*.py'):compile(path.read_text(encoding='utf-8'),str(path),'exec')
    result=dict(status='CPU_ONLY_PASS',candidate_sha256=hashlib.sha256(source.encode()).hexdigest(),
        semantic_cases=checks,reused_functions_byte_identical=len(reuse),
        limitations='NumPy执行源码语义，不证明Triton编译/设备结果、RNG、资源或性能。')
    (HERE/'cpu-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
