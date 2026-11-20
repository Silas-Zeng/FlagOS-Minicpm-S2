"""仅标准库复现真实vendor logger归属/once过滤；不加载Torch或设备。"""
import ast
import json
import logging
from pathlib import Path
import runpy
import sys
import tempfile
import types

HERE=Path(__file__).resolve().parent
assert 'torch' not in sys.modules
tree=ast.parse((HERE/'source/installed-flag-gems-logging-utils.py').read_text(encoding='utf-8'))
names={'LogOncePerLocationFilter','_remove_file_handlers','setup_flaggems_logging'}
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in names]
scope={'logging':logging,'Path':Path}
exec(compile(ast.Module(body=nodes,type_ignores=[]),'installed_logging_subset','exec'),scope)
component=runpy.run_path(str(HERE/'component.py'))
backend=logging.getLogger('_iluvatar.ops.mm')
root=logging.getLogger();oldroot=root.level;root.setLevel(logging.WARNING)
backend.setLevel(logging.NOTSET);backend.propagate=True
namespace={'__name__':'_iluvatar.ops.mm','logger':backend}
exec(compile('def mm_out():\n    logger.debug("GEMS_ILUVATAR MM_OUT")\n','real_mm_log_site','exec'),namespace)
fake=types.ModuleType('flag_gems');fake.mm_out=namespace['mm_out']
prior=sys.modules.get('flag_gems');sys.modules['flag_gems']=fake
checks=[]
try:
    with tempfile.TemporaryDirectory() as td:
        path=Path(td)/'oplist.txt'
        scope['setup_flaggems_logging'](path,record=True,once=True)
        before=(backend.level,backend.propagate,tuple(backend.handlers))
        fake.mm_out()
        assert '.mm_out:' not in path.read_text()
        checks.append('真实flag_gems-only handler复现vendor mm_out不可见')
        with component['observe_backend_warm_logging']() as receipt:
            fake.mm_out();fake.mm_out()
        assert receipt['restored'] and (backend.level,backend.propagate,tuple(backend.handlers))==before
        assert path.read_text().count('.mm_out:')==1
        checks.append('原LogOncePerLocationFilter只记录一次真实vendor函数')
        try:
            with component['observe_backend_warm_logging'](): raise RuntimeError('模拟warm失败')
        except RuntimeError: pass
        assert (backend.level,backend.propagate,tuple(backend.handlers))==before
        checks.append('正常及异常finally精确恢复原logger状态')
        fake.mm_out()
        assert path.read_text().count('.mm_out:')==1
        checks.append('恢复后不为后续Graph或计时保留新增日志')
        scope['_remove_file_handlers'](logging.getLogger('flag_gems'))
finally:
    root.setLevel(oldroot)
    if prior is None:sys.modules.pop('flag_gems',None)
    else:sys.modules['flag_gems']=prior
assert 'torch' not in sys.modules
compile((HERE/'component.py').read_text(encoding='utf-8'),'component.py','exec')
result={'passed':True,'checks':checks,'gpu_executed':False,'torch_imported':False,
        'actual_failure':'20261024T204020Z-final-ffn-row-prune',
        'failure_archive_sha256':'f8178ffca980bea903af3d6c5aef1e213cdab1b2d8fb0d597ce6bda6952c5b12'}
(HERE/'logging-cpu-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
