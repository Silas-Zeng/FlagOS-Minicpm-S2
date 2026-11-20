"""只执行新增padding源码与shape边界；不重复旧数学suite或导入设备。"""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace as NS
import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-20261025"
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


class T:
    def __init__(self, values): self.a = np.asarray(values)
    def __getitem__(self, key): return T(self.a[key])
    def add_(self, n): self.a[...] += n; return self
    def zero_(self): self.a[...] = 0; return self
    def fill_(self, n): self.a[...] = n; return self
    def clamp_(self, *, max): self.a[...] = np.minimum(self.a, max); return self
    def copy_(self, other): self.a[...] = other.a; return self


torch = NS(zeros_like=lambda t: T(np.zeros_like(t.a)),
           cat=lambda ts, dim: T(np.concatenate([t.a for t in ts], axis=dim)))
tree = ast.parse((HERE / "worker.py").read_text(encoding="utf8"))
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "worker")
padding = next(n for n in ast.walk(fn) if isinstance(n, ast.If) and ast.unparse(n.test) == "active < B")
module = ast.Module(body=[padding], type_ignores=[])
code = compile(ast.fix_missing_locations(module), "actual-worker-padding", "exec")
for B, active in [(40, 33), (32, 32)]:
    L = 32  # 仅缩小纯CPU backing；执行同一实际padding语句。
    common = NS(num_reqs=B, num_actual_tokens=B,
        block_table_tensor=T(np.tile(np.arange(8192), (B, 1)).astype(np.int32)),
        seq_lens=T(np.full(B, L, dtype=np.int32)), query_start_loc_cpu=T(np.arange(B + 1)),
        query_start_loc=T(np.arange(B + 1)), slot_mapping=T(np.arange(B) * L + L - 1))
    common.block_table_tensor.a[:, :2] = np.arange(B * 2).reshape(B, 2)
    cache = T(np.full((B * 2, 2, 16, 2, 128), 7, dtype=np.int16))
    env = dict(B=B, active=active, L=L, common=common, cache=cache, torch=torch)
    exec(code, env)
    if active < B:
        check("N33_B40_actual_padding_block", np.array_equal(common.query_start_loc.a, np.minimum(np.arange(41), 33))
            and np.array_equal(common.seq_lens.a, [L] * 33 + [0] * 7)
            and np.all(common.block_table_tensor.a[33:] == 0)
            and np.array_equal(common.block_table_tensor.a[:33, :2], np.arange(66).reshape(33, 2) + 1)
            and np.array_equal(common.slot_mapping.a[:33], np.arange(33) * L + L - 1 + 16)
            and np.all(common.slot_mapping.a[33:] == -1)
            and np.all(env["cache"].a[0] == 0) and np.all(env["cache"].a[1:] == 7)
            and common.num_reqs == common.num_actual_tokens == 40)
    else:
        check("B32_no_padding_behavior_change", np.array_equal(common.query_start_loc.a, np.arange(33))
              and np.all(common.seq_lens.a == L) and env["cache"] is cache)

baseline_ast = ast.parse((BASE / "baseline.py").read_text())
pick = next(n for n in baseline_ast.body if isinstance(n, ast.FunctionDef) and n.name == "_pick_segments")
env = {"TARGET_PROGRAMS": 256}
exec(compile(ast.Module(body=[pick], type_ignores=[]), "production-pick-segments", "exec"), env)
check("production_policy_S4_S16", env["_pick_segments"](32, 2, 16) == 4 and env["_pick_segments"](40, 2, 16) == 16)
boundary_node = next(n for n in ast.walk(fn) if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == "boundary")
boundary_expr = compile(ast.Expression(body=boundary_node.value), "actual-boundary-expression", "eval")
for S, active in [(4, 32), (16, 33)]:
    boundary = eval(boundary_expr, {"segments": S})
    check(f"S{S}_real_multitile_and_tail", (boundary[-2] + S * 16 - 1) // (S * 16) >= 2
          and boundary[-1] % 16 != 0 and (S != 4 or boundary == [0, 1, 15, 16, 17, 64, 160, 163]))
check("changed_KV_and_page_still_live", 15 < 33 and [0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65, 4095, 4096, 4097, 16383, 16384][15] == 16384)
check("candidate_and_all_inherited_code_frozen", all((HERE / name).read_bytes() == (BASE / name).read_bytes()
    for name in ("baseline.py", "candidate.py", "kernel.diff", "legacy_gate.py", "source_identity.py",
                 "distributed_bootstrap.py", "dispatch_bootstrap.py", "validate_mixed_decode.py")))
main_finally = lambda path: next(n.finalbody for n in ast.walk(ast.parse(path.read_text(encoding="utf8")))
                                if isinstance(n, ast.Try) and any(isinstance(x, ast.For) for x in n.finalbody))
check("owner_finally_ast_unchanged", [ast.dump(n) for n in main_finally(HERE / "entry.py")] ==
      [ast.dump(n) for n in main_finally(BASE / "entry.py")])
for path in HERE.glob("*.py"):
    ast.parse(path.read_text(encoding="utf8"))
probe = subprocess.run([sys.executable, "-B", "-X", "utf8", str(HERE / "entry.py"), "--help"],
                       capture_output=True, text=True, encoding="utf8")
check("entry_shape_cli_CPU_only", probe.returncode == 0 and "{hotspot,b32}" in probe.stdout)
result = dict(status="CPU_ONLY_PASS", checks=checks, old_suite="复用c62的11项CPU与4解析器边界；本轮不重跑",
    scope="实际新增padding AST使用NumPy backing执行；GPU数值/Graph/性能尚未运行")
(HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
print(json.dumps(result, ensure_ascii=False))
