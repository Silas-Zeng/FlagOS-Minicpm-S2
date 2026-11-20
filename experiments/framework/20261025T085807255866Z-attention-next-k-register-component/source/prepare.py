"""从冻结 v1 复制；仅将 worker 的资源阈值否决改为诊断。纯 CPU。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "attention-next-k-register-20261025"
V1_SHA = "d6bc61b26010f3f2210390ae57299b0870da989292dfd38957474718e21f8ca2"
sha = lambda raw: hashlib.sha256(raw).hexdigest()
if sha((BASE / "entry.tar.gz").read_bytes()) != V1_SHA:
    raise ValueError("冻结 v1 包发生变化")
pins = json.loads((BASE / "asset-pins.json").read_bytes())
for name, digest in pins.items():
    if sha((BASE / name).read_bytes()) != digest:
        raise ValueError("冻结 v1 资产变化：" + name)
    if name not in ("worker.py", "prepare.py", "README.md", "worker.diff"):
        shutil.copyfile(BASE / name, HERE / name)

changes = [(r'''    # BI 机器码资源与 runtime spill 两种证据都保存；无机器码证明则不计时。
    private = re.search(r"workitem_private_segment_byte_size\s*=\s*(\d+)", assembly)
    if not proof["mechanism_pass"] or private is None or int(private[1]) != 0:
        raise RuntimeError("Q-hoist 或 private0 机器码门未通过")
    if getattr(compiled, "n_spills", None) not in (None, 0):
        raise RuntimeError("runtime 报告 spill")
    return dict(q_hoist=proof, resources=resources, private_bytes=int(private[1]))
''', r'''    # 资源变化记录成本；Q-hoist 仍须真实保留，不能用静态资源替代净计时。
    private = re.search(r"workitem_private_segment_byte_size\s*=\s*(\d+)", assembly)
    if not proof["mechanism_pass"]:
        raise RuntimeError("Q-hoist 机器码门未通过")
    return dict(q_hoist=proof, resources=resources,
                private_bytes=int(private[1]) if private is not None else None,
                runtime_spills=getattr(compiled, "n_spills", None))
'''), ('''                    if (bres["shared"] != 32768 or bres["private_segment_fixed_size"] != 0
                            or bres["vgpr_spill_count"] != 0 or bres["vgpr_count"] > 128
                            or bres["sgpr_count"] > ares["sgpr_count"]):
                        raise RuntimeError("next-K 资源门失败；不扩大 shared/明显降低 raw 四CTA上界")
''', '''                    cost_fields = ("shared", "private_segment_fixed_size", "vgpr_count",
                                   "vgpr_spill_count", "sgpr_count", "sgpr_spill_count")
                    arm_info["resource_cost"] = dict(
                        delta={name: bres[name] - ares[name] for name in cost_fields},
                        static_resources_are_not_performance_gate=True,
                        actual_occupancy_proven=False)
''')]
original = (BASE / "worker.py").read_text(encoding="utf-8")
changed = original
for old, new in changes:
    if changed.count(old) != 1:
        raise ValueError("资源阈值锚点不唯一")
    changed = changed.replace(old, new, 1)
restored = changed
for old, new in reversed(changes):
    if restored.count(new) != 1:
        raise ValueError("逆回锚点不唯一")
    restored = restored.replace(new, old, 1)
if restored != original:
    raise ValueError("除资源判据外仍有变化")
ast.parse(changed)
(HERE / "worker.py").write_text(changed, encoding="utf-8")
(HERE / "worker.diff").write_text("".join(difflib.unified_diff(original.splitlines(True), changed.splitlines(True),
    fromfile="next-k-v1/worker.py", tofile="next-k-v2/worker.py")), encoding="utf-8")

# 只执行新的小函数：较大 private/runtime spill 不被误拒；Q-hoist 缺失仍拒。
node = next(n for n in ast.parse(changed).body if isinstance(n, ast.FunctionDef) and n.name == "preserve")
namespace = {"dump": lambda *_: None, "re": re}
exec(compile(ast.Module(body=[node], type_ignores=[]), "<v2-preserve-CPU>", "exec"), namespace)
compiled = SimpleNamespace(asm={"ttgir": "fixture", "llir": "fixture",
    "asm": "workitem_private_segment_byte_size = 64"}, n_spills=12)
qmod = SimpleNamespace(lowered_proof=lambda *_: {"mechanism_pass": True},
    _resources=lambda *_: {"n_spills": 12}, _q_debug_lines=lambda *_: set())
accepted = namespace["preserve"](compiled, None, qmod, SimpleNamespace(fn=None), SimpleNamespace(__file__="fixture"))
assert accepted["private_bytes"] == 64 and accepted["runtime_spills"] == 12
qmod.lowered_proof = lambda *_: {"mechanism_pass": False}
try:
    namespace["preserve"](compiled, None, qmod, SimpleNamespace(fn=None), SimpleNamespace(__file__="fixture"))
except RuntimeError:
    pass
else:
    raise AssertionError("Q-hoist 门不应放宽")
unchanged = {name: digest for name, digest in pins.items()
             if name not in ("worker.py", "prepare.py", "README.md", "worker.diff")}
assert all(sha((HERE / name).read_bytes()) == digest for name, digest in unchanged.items())
receipt = dict(status="CPU_RESOURCE_POLICY_DELTA_ONLY", parent_archive_sha256=V1_SHA,
    exact_inverse=True, larger_private_and_runtime_spill_recorded=True, absent_q_hoist_rejected=True,
    unchanged_assets=unchanged, repeated_old_address_checks=False,
    limits="未编译或执行GPU；静态资源没有证明真实驻留，净收益待同轮ABBA。")
(HERE / "resource-policy-check.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
assets = [*pins, "resource-policy-check.json"]
hashes = {name: sha((HERE / name).read_bytes()) for name in assets}
(HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n")
with tarfile.open(HERE / "entry.tar.gz", "w:gz") as archive:
    for name in [*assets, "asset-pins.json"]:
        archive.add(HERE / name, arcname=name)
print(json.dumps(dict(status=receipt["status"], files=len(assets),
    worker_sha256=hashes["worker.py"], archive_sha256=sha((HERE / "entry.tar.gz").read_bytes()))))
