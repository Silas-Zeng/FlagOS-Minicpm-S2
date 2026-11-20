"""重建原worker默认FlagGems上下文；仅注册原opaque，不安装候选到框架。"""
import hashlib
import importlib
import inspect
import os
from pathlib import Path

LINEAR_SHA = 'd431a4fa144ed67dc3deab46dd5beace3612858075f85c39e602447ba3bf768a'
OPAQUE_SHA = 'c5a2dd6c69c514531fee4145621e51bd4e41c0d784f4d4e086fe48aad98104ba'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(value, message):
    if not value:
        raise RuntimeError(message)


def enable_dispatch(torch, run):
    for key in ('VLLM_FL_FLAGOS_WHITELIST', 'VLLM_FL_FLAGOS_BLACKLIST',
                'VLLM_FL_FLAGOS_BLACKLIST_APPEND', 'FLAGGEMS_DB_URL', 'FLAGGEMS_CACHE_DIR'):
        require(not os.environ.get(key), '不同服务dispatch/cache覆盖: '+key)
    require(os.environ.get('USE_FLAGGEMS', 'True').lower() in ('true', '1'), 'FlagGems关闭')
    from vllm_fl.utils import get_flag_gems_whitelist_blacklist
    whitelist, blacklist = get_flag_gems_whitelist_blacklist()
    require(not whitelist and not blacklist, '不是原worker实际默认enable分支')
    import flag_gems
    # 原服务当前为无whitelist/blacklist覆盖的默认enable分支，沿用已核启动环境。
    flag_gems.enable(record=True, once=True, path=str(run/'flaggems-oplist.txt'))
    registrar = flag_gems.current_work_registrar
    entries = [x for x in registrar.config if x[0] == 'linear']
    require(len(entries) == 1 and entries[0][1] is flag_gems.linear, '实际linear注册绑定不同')
    fn = inspect.unwrap(flag_gems.linear)
    linear_path = Path(inspect.getsourcefile(fn)).resolve()
    require(sha(linear_path) == LINEAR_SHA, '实际FlagGems linear源码变化')
    table = torch._C._dispatch_dump_table('aten::linear')
    (run/'dispatch-linear.txt').write_text(table)
    require(any(x.startswith('CUDA:') and 'flag_gems/' in x.replace('\\', '/')
                for x in table.splitlines()), 'CUDA linear没有指向FlagGems')
    module = importlib.import_module(fn.__module__)
    require('linear_kernel' in vars(module), '实际linear函数没有受核linear_kernel')
    opaque = importlib.import_module('vllm_fl.patches.biv150_stable_small_o')
    opaque_path = Path(inspect.getsourcefile(opaque)).resolve()
    require(sha(opaque_path) == OPAQUE_SHA, '当前生产opaque不是main6971原版本')
    opaque._register()
    (run/'source/installed-linear.py').write_bytes(linear_path.read_bytes())
    (run/'source/installed-stable-small-o.py').write_bytes(opaque_path.read_bytes())
    return module, dict(linear_source_sha256=LINEAR_SHA, opaque_source_sha256=OPAQUE_SHA,
        registered=True, exclude_ops=list(registrar.get_unused_ops()),
        baseline_route='真实torch.ops.biv150_stable_small_o.linear→F.linear→原默认FlagGems linear；含分配')


class Capture:
    """只在身份门包裹真实linear_kernel；正式计时前恢复原对象。"""
    def __init__(self, original):
        self.original, self.records = original, []

    def __getitem__(self, grid):
        def launch(*args, **kwargs):
            value = self.original[grid](*args, **kwargs)
            require(isinstance(value, tuple) and len(value) == 2, '原LibEntry返回ABI变化')
            kernel, constexprs = value
            require(len(args) >= 7 and args[5] == 12288 and args[6] == 2048,
                    '实际opaque未执行目标merged gate linear')
            require(kwargs.get('GROUP_M') == 8 and kwargs.get('SPLIT_K') == 1
                    and kwargs.get('BIAS') is False, '原生产linear数学/分组不同')
            config = {k:int(constexprs[k]) for k in
                      ('BLOCK_M', 'BLOCK_N', 'BLOCK_K', 'num_warps', 'num_stages', 'num_ctas')}
            config['SPLIT_K'] = 1
            resolved = dict(zip(self.original.arg_names, args))
            resolved.update(kwargs)
            resolved.update(constexprs)
            actual_grid = tuple(grid(resolved)) if callable(grid) else tuple(grid)
            self.records.append(dict(rows=int(args[4]), config=config,
                constexprs={k:str(v) for k,v in constexprs.items()}, grid=actual_grid, kernel=kernel))
            return value
        return launch
