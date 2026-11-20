"""实际新main callback的默认FlagGems mm.out dispatch；不装候选。"""
import hashlib,importlib,inspect,os
from pathlib import Path
ROWS=32
MM_SHA='4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090'
CALLBACK_SHA='1edfba6c9176665312962e7ea7dc9cac15132403ca4fbbd92d86fd4894325302'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(x,message):
    if not x:raise RuntimeError(message)
def enable_dispatch(torch,run):
    for key in ('VLLM_FL_FLAGOS_WHITELIST','VLLM_FL_FLAGOS_BLACKLIST','VLLM_FL_FLAGOS_BLACKLIST_APPEND','FLAGGEMS_DB_URL','FLAGGEMS_CACHE_DIR'):
        require(not os.environ.get(key),'服务dispatch/cache覆盖:'+key)
    require(os.environ.get('USE_FLAGGEMS','True').lower() in ('true','1'),'FlagGems关闭')
    from vllm_fl.utils import get_flag_gems_whitelist_blacklist
    whitelist,blacklist=get_flag_gems_whitelist_blacklist();require(not whitelist and not blacklist,'不是worker默认FlagGems分支')
    import flag_gems
    flag_gems.enable(record=True,once=True,path=str(run/'flaggems-oplist.txt'))
    entries=[x for x in flag_gems.current_work_registrar.config if x[0]=='mm.out']
    require(len(entries)==1 and entries[0][1] is flag_gems.mm_out,'mm.out registrar不同')
    function=inspect.unwrap(flag_gems.mm_out);module=importlib.import_module(function.__module__)
    require(function is module.mm_out and function.__globals__ is vars(module),'实际mm_out绑定/全局不同')
    source=Path(inspect.getsourcefile(function)).resolve();require(sha(source)==MM_SHA,'实际SDK mm源变化')
    table=torch._C._dispatch_dump_table('aten::mm.out');(run/'dispatch-mm-out.txt').write_text(table)
    require(any(x.startswith('CUDA:') and 'flag_gems/' in x.replace('\\','/') for x in table.splitlines()),'aten::mm.out未绑定FlagGems CUDA')
    callback=importlib.import_module('vllm_fl.patches.biv150_small_out_lowering')
    cb_source=Path(inspect.getsourcefile(callback.small_linear_out)).resolve()
    require(sha(cb_source)==CALLBACK_SHA,'实际callback不是merge594原件')
    require(callback.small_linear_out.__globals__ is vars(callback),'callback全局未知')
    (run/'source/actual-installed-mm.py').write_bytes(source.read_bytes())
    (run/'source/actual-small-out-lowering.py').write_bytes(cb_source.read_bytes())
    return module,callback,dict(mm_source_sha256=MM_SHA,callback_source_sha256=CALLBACK_SHA,
        registrar_mm_out=True,aten_dispatch='CUDA FlagGems',callback_installer_called=False,
        scope='原small_linear_out M32不依赖_LARGE_LINEAR策略，实际torch.mm(x,weight.t(),out=out)；不重编Inductor')
class Capture:
    def __init__(self,original):self.original,self.records=original,[]
    def __getitem__(self,grid):
        def launch(*args,**kwargs):
            require(len(args)>=12 and tuple(int(v) for v in args[3:6])==(ROWS,2048,6144),'实际callback没有执行M32 down MM ABI')
            require(tuple(int(v) for v in args[6:12])==(6144,1,1,6144,2048,1),'MM实际输入/原W转置/out stride不同')
            require(tuple(args[0].shape)==(ROWS,6144) and tuple(args[0].stride())==(6144,1),'A真实M32 descriptor不同')
            require(tuple(args[1].shape)==(6144,2048) and tuple(args[1].stride())==(1,6144),'B不是原W.t自然view')
            require(tuple(args[2].shape)==(ROWS,2048) and tuple(args[2].stride())==(2048,1),'caller out真实descriptor不同')
            require(kwargs.get('fp8_fast_accum') is True and kwargs.get('input_precision') is None and kwargs.get('GROUP_M')==8,'MM原数学参数变化')
            value=self.original[grid](*args,**kwargs)
            require(isinstance(value,tuple) and len(value)==2,'LibEntry返回ABI变化')
            kernel,constexprs=value
            resolved=dict(zip(self.original.arg_names,args));resolved.update(kwargs);resolved.update(constexprs)
            actual_grid=tuple(grid(resolved)) if callable(grid) else tuple(grid)
            keys=('BLOCK_M','BLOCK_N','BLOCK_K','SPLIT_K','num_warps','num_stages','num_ctas')
            config={k:int(resolved[k]) for k in keys}
            self.records.append(dict(M=ROWS,N=2048,K=6144,config=config,grid=actual_grid,kernel=kernel,
                constexprs={k:str(v) for k,v in constexprs.items()},
                mathematical_kwargs={k:str(v) for k,v in kwargs.items()},
                A_shape=list(args[0].shape),A_stride=list(args[0].stride()),
                B_transposed_W_shape=list(args[1].shape),B_transposed_W_stride=list(args[1].stride()),
                B_storage_offset=int(args[1].storage_offset()),out_shape=list(args[2].shape),out_stride=list(args[2].stride())))
            return value
        return launch
