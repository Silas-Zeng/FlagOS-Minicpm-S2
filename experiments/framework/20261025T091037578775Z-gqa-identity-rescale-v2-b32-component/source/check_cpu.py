"""执行实际新增条件块，禁止空切片调用all；无需Torch/FlagGems/GPU。"""
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-v2-20261025"
tree = ast.parse((HERE / "worker.py").read_text(encoding="utf8"))
node = next(n for n in ast.walk(tree) if isinstance(n, ast.If) and ast.unparse(n.test) == "active < B"
            and n.body and isinstance(n.body[0], ast.Assign)
            and 'checks[\'padded_output_zero\']' in ast.unparse(n.body[0]))
code = compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "actual-padding-check", "exec")


class Tensor:
    calls = 0
    def __init__(self, values): self.values = values
    def __getitem__(self, key): return Tensor(self.values[key])
    def __eq__(self, other): return Tensor([v == other for v in self.values])
    def all(self):
        if not self.values:
            raise AssertionError("不允许对空切片调用all")
        Tensor.calls += 1
        return all(self.values)


results = []
for active, B, corrupt in [(32, 32, False), (33, 40, False), (33, 40, True)]:
    Tensor.calls = 0
    arms = {}
    for arm in ("baseline", "candidate"):
        out = [0] * B
        partial = [-17] * B
        if corrupt and arm == "candidate":
            out[active] = 1
            partial[active] = 0
        arms[arm] = NS(out=Tensor(out), partial=Tensor(partial), maxima=Tensor([-17] * B), sums=Tensor([-17] * B))
    checks = {}
    exec(code, dict(active=active, B=B, arms=arms, checks=checks))
    assert all(checks.values()) is (not corrupt)
    assert Tensor.calls == (0 if active == B else (6 if corrupt else 8))
    results.append(dict(active=active, bucket=B, corrupt=corrupt, all_calls=Tensor.calls, checks=checks))

# 除新增if包裹的两项外，worker全部AST恢复成v2后必须相等。
old_tree = ast.parse((BASE / "worker.py").read_text(encoding="utf8"))
class Restore(ast.NodeTransformer):
    def visit_If(self, value):
        return value.body if value is node else self.generic_visit(value)
restored = Restore().visit(tree)
assert ast.dump(restored, include_attributes=False) == ast.dump(old_tree, include_attributes=False)
for name in ("entry.py", "candidate.py", "baseline.py", "kernel.diff", "source_identity.py",
             "distributed_bootstrap.py", "dispatch_bootstrap.py", "legacy_gate.py"):
    assert (HERE / name).read_bytes() == (BASE / name).read_bytes(), name
for path in HERE.glob("*.py"):
    ast.parse(path.read_text(encoding="utf8"))
result = dict(status="CPU_ONLY_PASS", cases=results,
    checks=["B32零padding不调用all", "B40保留8次非空检查", "B40损坏padding仍拒绝",
            "其余worker完整AST逐字语义一致", "owner数学与安装生命周期原件不变", "最终Python AST"],
    worker_sha256=hashlib.sha256((HERE / "worker.py").read_bytes()).hexdigest(),
    scope="仅验证器回归；不重跑旧数值/CPU套件，不证明GPU性能")
(HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps(result, ensure_ascii=False))
