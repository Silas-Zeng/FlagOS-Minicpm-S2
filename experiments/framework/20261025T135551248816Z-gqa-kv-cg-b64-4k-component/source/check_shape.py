"""仅新增shape和页界接线；不导入Torch或执行旧套件。"""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from prepare import HERE, BASE, INHERITED

checks = []
def check(name, ok):
    if not ok:
        raise AssertionError(name)
    checks.append(name)

check("all_inherited_assets_exact", all((HERE / n).read_bytes() == (BASE / n).read_bytes() for n in INHERITED))
text = (HERE / "worker.py").read_text(encoding="utf8")
old_text = (BASE / "worker.py").read_text(encoding="utf8")
tree = ast.parse(text)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "worker")
body = next(n for n in fn.body if isinstance(n, ast.Try)).body
index = next(i for i,n in enumerate(body) if isinstance(n, ast.If) and ast.unparse(n.test) == "shape == 'hotspot'")
select = ast.Module(body=body[index:index+2], type_ignores=[])
for shape, expected in (("hotspot", (40,33,16,16384)), ("b32", (32,32,4,16384)), ("b64-4k", (64,64,2,4096))):
    ns = dict(shape=shape)
    exec(compile(select, "actual-worker-shape", "exec"),ns)
    check("actual_shape_selection_" + shape, tuple(ns[k] for k in ("B","active","segments","L")) == expected)
source = ast.parse((HERE / "baseline.py").read_text(encoding="utf8"))
pick = next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name == "_pick_segments")
ns = dict(TARGET_PROGRAMS=256)
exec(compile(ast.Module(body=[pick],type_ignores=[]), "frozen-production-policy", "exec"),ns)
check("actual_production_policy_B64_S2", ns["_pick_segments"](64,2,16)==2)
# 小参考枚举实际 writer 的64个末token，null页0未写；页表与slot同向偏移。
slots = [row*4096+4095+16 for row in range(64)]
check("reserved_null_writer_slot_bounds", min(slots)>=16 and max(slots)<(64*256+1)*16 and
      all(slot//16 == 1+row*256+255 for row,slot in enumerate(slots)))
ns = dict(L=4096, active=64, B=64, changed_row=15, shape="b64-4k")
for n in ast.walk(fn):
    if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ("changed_page","ragged_pattern","ragged"):
        exec(compile(ast.Module(body=[n],type_ignores=[]),"actual-boundary", "exec"),ns)
check("actual_ragged_and_changed_page_bounded", min(ns["ragged"])==0 and max(ns["ragged"])==4096 and
      4095 in ns["ragged"] and ns["changed_page"]==3841)
new_check = next(n for n in ast.walk(fn) if isinstance(n,ast.FunctionDef) and n.name=="check")
old_check = next(n for n in ast.walk(ast.parse(old_text)) if isinstance(n,ast.FunctionDef) and n.name=="check")
check("full_numerics_and_empty_padding_guard_unchanged", ast.dump(new_check)==ast.dump(old_check))
check("restored_state_and_ABBA_tail_unchanged", text[text.index('        for target, saved in zip('):] ==
      old_text[old_text.index('        for target, saved in zip('):])
check("owner_only_shape_choice", (HERE/"entry.py").read_text(encoding="utf8").replace(
    'choices=("hotspot", "b32", "b64-4k"), default="b64-4k"',
    'choices=("hotspot", "b32"), default="hotspot"')==(BASE/"entry.py").read_text(encoding="utf8"))
help_result = subprocess.run([sys.executable,"-B","-X","utf8",str(HERE/"entry.py"),"--help"],capture_output=True,text=True,encoding="utf8")
check("inert_new_cli_shape", help_result.returncode==0 and "b64-4k" in help_result.stdout)
result=dict(status="CPU_SHAPE_ONLY_PASS", gpu_run=False, checks=checks,
            baseline_sha256=hashlib.sha256((HERE/"baseline.py").read_bytes()).hexdigest(),
            candidate_sha256=hashlib.sha256((HERE/"candidate.py").read_bytes()).hexdigest(),
            qualification="组件shape入口；实际Builder网格与数值/Graph/ASM/计时待唯一设备验证，非模型或官方结果")
(HERE/"shape-check.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(result,ensure_ascii=False))
