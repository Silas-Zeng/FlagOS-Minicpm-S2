"""原样提取成功 v3 的 FlagGems 实际注册函数；仅补必要 imports。"""
import hashlib
import inspect
import os
from pathlib import Path

INDEX_SHA = '47a7108bcf8424a96651021703f8731f1866a0e2eff88a1ac647e574ccf7e61d'

def require(value, message):
    if not value:
        raise ValueError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def enable_dispatch(torch, run):
    for key in ('VLLM_FL_FLAGOS_WHITELIST','VLLM_FL_FLAGOS_BLACKLIST','VLLM_FL_FLAGOS_BLACKLIST_APPEND',
                'FLAGGEMS_DB_URL','FLAGGEMS_CACHE_DIR'):
        require(not os.environ.get(key),'不同服务dispatch/cache覆盖: '+key)
    require(os.environ.get('USE_FLAGGEMS','True').lower() in ('true','1'),'FlagGems被关闭')
    import flag_gems
    flag_gems.enable(record=True,once=True,path=str(run/'flaggems-oplist.txt'))
    registrar=flag_gems.current_work_registrar
    entries=[x for x in registrar.config if x[0]=='index.Tensor']
    require(len(entries)==1 and entries[0][1] is flag_gems.index,'真实index绑定不同')
    fn=inspect.unwrap(flag_gems.index)
    path=Path(inspect.getsourcefile(fn)).resolve()
    require(sha(path)==INDEX_SHA,'实际index源不符')
    table=torch._C._dispatch_dump_table('aten::index.Tensor')
    (run/'dispatch-index.txt').write_text(table)
    require(any(x.startswith('CUDA:') and 'flag_gems/' in x.replace('\\','/') for x in table.splitlines()),'CUDA index未指向FlagGems')
    return dict(index_source_sha256=INDEX_SHA,registered=True,exclude_ops=list(registrar.get_unused_ops()))
