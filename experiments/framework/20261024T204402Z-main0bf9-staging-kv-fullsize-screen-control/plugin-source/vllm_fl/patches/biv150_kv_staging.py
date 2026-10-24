"""独立bit-copy primitive；准备不上传，submit非ACK，调用者负责真event/异常settle。"""
import ctypes
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys

PAGE = 16384
class Layer(ctypes.Structure):
    _fields_ = [('raw',ctypes.c_void_p),('host',ctypes.c_void_p),('raw_bytes',ctypes.c_size_t),('host_bytes',ctypes.c_size_t)]
class Submitted(ctypes.Structure):
    _fields_ = [('index_copies',ctypes.c_size_t),('data_copies',ctypes.c_size_t),('kernels',ctypes.c_size_t)]
@dataclass(frozen=True)
class Plan:
    ids: tuple
    pool: int
    def __post_init__(self):
        if (type(self.pool) is not int or self.pool <= 0 or self.pool > ((1<<64)-1)//PAGE
                or type(self.ids) is not tuple or not self.ids or len(self.ids)>65536
                or any(type(x) is not int or not 0 <= x < self.pool for x in self.ids)
                or len(set(self.ids)) != len(self.ids)):
            raise ValueError('页号必须保序、唯一、完整且在真实pool内')
def make_plan(ids, pool): return Plan(tuple(ids),pool)
@dataclass(frozen=True)
class Prepared:
    descriptors: object
    keepalive: tuple
    host_ids: object
    device_ids: object
    scratch: object
    pages: int
    pool: int
    nbytes: int

def prepare(raw, hosts, plan, *, copy_runtime):
    if type(plan) is not Plan: raise TypeError('需要固定页序Plan')
    torch = sys.modules.get('torch')
    if torch is None: raise RuntimeError('仅调用者已加载torch时可准备')
    raw,hosts=tuple(raw),tuple(hosts)
    count=len(plan.ids)
    if len(raw) not in (1,42) or len(hosts)!=len(raw) or count*PAGE*len(raw)>1<<30:
        raise ValueError('仅1/42层及不超过1GiB完整payload')
    # 每方向临时分配一次并计入prepare；不预上传、不隐藏scratch/索引开销。
    scratch=torch.empty((count,PAGE),dtype=torch.uint8,device='cuda:0')
    host_ids=torch.empty((count,),dtype=torch.int64,pin_memory=True)
    host_ids.copy_(torch.tensor(plan.ids,dtype=torch.int64))
    device_ids=torch.empty((count,),dtype=torch.int64,device='cuda:0')
    pointer, scratch_bytes, scratch_storage=copy_runtime._tensor_range(torch,scratch,(count,PAGE),'cuda:0')
    if pointer%16 or scratch_bytes!=count*PAGE: raise ValueError('scratch对齐/范围')
    descriptors=[]
    gpu_storages={scratch_storage,device_ids.untyped_storage().data_ptr()}
    cpu_storages={host_ids.untyped_storage().data_ptr()}
    if len(gpu_storages)!=2: raise ValueError('scratch/device IDs别名')
    for gpu,host in zip(raw,hosts):
        gp,gn,gs=copy_runtime._tensor_range(torch,gpu,(plan.pool,PAGE),'cuda:0')
        hp,hn,hs=copy_runtime._tensor_range(torch,host,(count,PAGE),'cpu')
        if gp%16 or hp%16 or gs in gpu_storages or hs in cpu_storages:
            raise ValueError('跨层/临时storage别名或uint4未对齐')
        gpu_storages.add(gs);cpu_storages.add(hs)
        descriptors.append(Layer(gp,hp,gn,hn))
    for ids,device in ((host_ids,'cpu'),(device_ids,'cuda:0')):
        if (type(ids) is not torch.Tensor or str(ids.dtype)!='torch.int64' or str(ids.device)!=device
                or tuple(ids.shape)!=(count,) or not ids.is_contiguous() or ids.storage_offset()!=0
                or ids.data_ptr()%8 or ids.untyped_storage().nbytes()!=count*8
                or device=='cpu' and not ids.is_pinned()):
            raise ValueError('索引Tensor ABI/存储/固定页不符')
    if tuple(host_ids.tolist())!=plan.ids: raise ValueError('实际CPU索引内容改变')
    array=(Layer*len(descriptors))(*descriptors)
    return Prepared(array,raw+hosts+(host_ids,device_ids,scratch),host_ids,device_ids,scratch,count,plan.pool,count*PAGE*len(raw))

class SubmissionError(RuntimeError):
    def __init__(self,code,submitted):
        self.code,self.submitted=code,submitted
        super().__init__(f'staging提交失败{code}: {submitted}; 必须settle，禁止重试/ACK')
class Bridge:
    def __init__(self,path,*,expected_sha256):
        path=Path(path)
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected_sha256:
            raise ValueError('只加载本实例编译且SHA固定的普通SO')
        self.library=ctypes.CDLL(str(path.resolve()))
        for name,expected,restype in (('staging_abi',1,ctypes.c_uint32),('staging_layer_size',32,ctypes.c_size_t),('staging_submitted_size',24,ctypes.c_size_t)):
            fn=getattr(self.library,name);fn.argtypes=[];fn.restype=restype
            if fn()!=expected: raise ValueError('primitive ABI不符: '+name)
        if ctypes.sizeof(Layer)!=32 or ctypes.sizeof(Submitted)!=24: raise ValueError('ctypes ABI不符')
        self.call=self.library.staging_submit
        self.call.argtypes=[ctypes.POINTER(Layer),ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p,
            ctypes.c_size_t,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_uint32,ctypes.c_void_p,ctypes.POINTER(Submitted)]
        self.call.restype=ctypes.c_int
    def submit(self,prepared,*,direction,stream_handle):
        if type(prepared) is not Prepared or direction not in ('D2H','H2D') or type(stream_handle) is not int or not 0<=stream_handle<(1<<64):
            raise ValueError('准备对象/方向/stream错误')
        count=Submitted()
        code=self.call(prepared.descriptors,len(prepared.descriptors),prepared.host_ids.data_ptr(),
            prepared.device_ids.data_ptr(),prepared.pages,prepared.pool,prepared.scratch.data_ptr(),
            prepared.pages*PAGE,1 if direction=='D2H' else 2,stream_handle,ctypes.byref(count))
        info={name:int(getattr(count,name)) for name,_ in Submitted._fields_}
        if code or info!={'index_copies':1,'data_copies':len(prepared.descriptors),'kernels':len(prepared.descriptors)}:
            raise SubmissionError(code or -1008,info)
        return dict(info,submitted_bytes=prepared.nbytes,index_bytes=prepared.pages*8,
                    copy_calls=count.data_copies+count.index_copies,scratch_bytes=prepared.pages*PAGE,
                    device_index_bytes=prepared.pages*8,completion_ack=False)
