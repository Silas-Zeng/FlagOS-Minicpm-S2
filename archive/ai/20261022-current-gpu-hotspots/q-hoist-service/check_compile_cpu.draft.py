"""未完成、未运行：root要求停止新增stub，采用syntax＋独立代码审阅后真实短服务。"""
import ast
import contextvars
import hashlib
import importlib.util
import json
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import patch

sys.dont_write_bytecode=True
begin=time.perf_counter_ns();here=Path(__file__).resolve().parent;root=here.parents[1]
path=here/'biv150_q_fragment_service.py'
spec=importlib.util.spec_from_file_location('q_service_cpu',path)
p=importlib.util.module_from_spec(spec);sys.modules[spec.name]=p;spec.loader.exec_module(p)
old=ast.parse((root/'tmp/next-q-fragment-hoist/biv150_q_fragment_hoist.py').read_text(encoding='utf-8'))
new=ast.parse(path.read_text(encoding='utf-8'))
for name in ('transform_ir','_freeze','_eligible','lowered_proof'):
    a=next(n for n in old.body if isinstance(n,ast.FunctionDef) and n.name==name)
    b=next(n for n in new.body if isinstance(n,ast.FunctionDef) and n.name==name)
    assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
raw_ir=(root/'analysis/source/current-attention-ir/baseline.ttgir').read_text(encoding='utf-8')
raw_llvm=(root/'analysis/source/current-attention-ir/baseline.llir').read_text(encoding='utf-8')
# Preparation stopped here. This file has NOT been executed and is no test receipt.
