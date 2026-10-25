"""仅 CPU 复核已回收 next-K：多行定位修正后仍保留原 CFG 否决条件。"""
import ast
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
V2 = HERE.parent / "attention-next-k-register-v2-20261025"
RUN = HERE.parent / "resume-exploration-20261025/next-k-component-extracted/20261025T085807255866Z-attention-next-k-register-component"
digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
source = (RUN / "candidate.kernel.py").read_text(encoding="utf-8")
assembly = (RUN / "ir-16384-candidate/asm.txt").read_text(encoding="utf-8")
ttgir = (RUN / "ir-16384-candidate/ttgir.txt").read_text(encoding="utf-8")
assert hashlib.sha256(source.encode()).hexdigest() == "ffbbfe288fbb7e2ee6a08918bf30f054631e5b25999e9b3446967cc521d6f0b5"
assert digest(RUN / "ir-16384-candidate/asm.txt") == "68da8a634d68567b15eb8d145bf55bcfbed4fd440470509828ee44b168bbb257"
calls = [node.value for node in ast.walk(ast.parse(source))
         if isinstance(node, ast.Assign)
         and any(isinstance(target, ast.Name) and target.id == "next_k_value" for target in node.targets)
         and isinstance(node.value, ast.Call)
         and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "load"]
assert len(calls) == 1
load_first, load_last = calls[0].lineno, calls[0].end_lineno
old_parser = (V2 / "next_k.py").read_text(encoding="utf-8")
old = 'if current_line == load_line and re.search(r"ml_lsa_(?:blkload|load)_", line):'
new = f'if current_line is not None and load_line <= current_line <= {load_last} and re.search(r"ml_lsa_(?:blkload|load)_", line):'
assert old_parser.count(old) == 1
# 只在本进程替换定位条件；冻结 helper、kernel、worker、包均不写入。
ns = {}
exec(compile(old_parser.replace(old, new, 1), "<CPU-only-call-range-parser>", "exec"), ns)
mechanism = ns["mechanism"]
pv = next(i + 1 for i, line in enumerate(source.splitlines()) if "acc += tl.dot(P.to(V.dtype), V)" in line)
source_sha = hashlib.sha256(source.encode()).hexdigest()
filename = "<affine-pages-component-" + source_sha + ".py>"
fixture_ir = "%carry = scf.for %x = %lo to %hi step %one iter_args(%k = %init) -> (tensor<128x64xbf16, #blocked>) {"
def fixture(line):
    return (f'.file 1 "{filename}"\nBB0_1:\n .loc 1 {line} 1\n ml_lsa_blkload_x1 v80, null\n sl_jump BB0_3\n'
            f'BB0_2:\n sl_exit\nBB0_3:\n .loc 1 {pv} 1\n' + ' ml_matrix_mad_f32_bf16_m16n16k16 v0\n' * 32)
positives = [fixture(load_first), fixture(load_first + 1)]
for machine in positives:
    assert mechanism(fixture_ir, machine, source)["pass_"]
machine = positives[-1]
negatives = [fixture(load_last + 1), machine.replace(f".loc 1 {load_first + 1} 1", f".loc 2 {load_first + 1} 1"),
             machine.replace("sl_jump BB0_3", "sl_wait vmcnt(0)\n sl_jump BB0_3"),
             machine.replace("sl_jump BB0_3", "sl_barrier\n sl_jump BB0_3"),
             machine.replace("sl_jump BB0_3", "sl_jump BB0_1"),
             machine.replace("sl_jump BB0_3", "sl_jump BB0_2")]
for case in negatives:
    try:
        mechanism(fixture_ir, case, source)
    except ValueError:
        pass
    else:
        raise AssertionError("定位或CFG负例漏拒")
try:
    mechanism(ttgir, assembly, source)
except ValueError as exc:
    actual_rejection = str(exc)
    assert actual_rejection.endswith("1080"), actual_rejection
else:
    raise AssertionError("实际 PV 前 vmcnt 不得通过")

# 独立遍历每条真实 next-K load 到第一个 wait/barrier/PV，不跳过任何分支。
lines = assembly.splitlines()
labels = {m[1]: i for i, line in enumerate(lines) if (m := re.match(r"^(BB\d+_\d+):", line))}
file_id = next(int(m[1]) for line in lines if (m := re.match(r'\s*\.file\s+(\d+)\s+"([^"]+)"', line)) and m[2] == filename)
load_indices, pv_indices, current = [], set(), None
for i, line in enumerate(lines):
    loc = re.match(r"\s*\.loc\s+(\d+)\s+(\d+)\s+\d+", line)
    if loc:
        current = int(loc[2]) if int(loc[1]) == file_id else None
    if current is not None and load_first <= current <= load_last and re.search(r"ml_lsa_(?:blkload|load)_", line):
        load_indices.append(i)
    if current == pv and "ml_matrix_mad_" in line:
        pv_indices.add(i)
assert len(load_indices) == 8 and len(pv_indices) == 32
paths = []
for load in load_indices:
    todo, visited, ends = [load + 1], set(), set()
    while todo:
        i = todo.pop()
        if i in visited:
            continue
        visited.add(i)
        assert 0 <= i < len(lines) and len(visited) < 4000
        line = lines[i]
        if ("sl_wait" in line and "vmcnt" in line) or "sl_barrier" in line or i in pv_indices:
            ends.add(i + 1)
            continue
        jump = re.search(r"\b(sl_jump|sl_cbr_\w+)\s+(BB\d+_\d+)", line)
        if jump:
            todo.append(labels[jump[2]])
            if jump[1] != "sl_jump":
                todo.append(i + 1)
        else:
            assert "sl_exit" not in line and "s_endpgm" not in line
            todo.append(i + 1)
    assert ends == {1080}, ends
    paths.append(dict(load_asm_line=load + 1, first_wait_barrier_or_pv=sorted(ends)))
receipt = dict(status="NO_GO_ACTUAL_WAIT_BEFORE_PV", source_sha256=source_sha,
    files={str(p.relative_to(ROOT)): digest(p) for p in [V2 / "next_k.py", V2 / "entry.tar.gz", RUN / "ir-16384-candidate/asm.txt", RUN / "ir-16384-candidate/ttgir.txt"]},
    load_source_span=[load_first, load_last], actual_load_debug_line=406,
    cpu_parser_positive=len(positives), cpu_parser_negative=len(negatives),
    actual_rejection=actual_rejection, all_load_paths=paths, first_pv_asm_line=min(pv_indices) + 1,
    mechanism="TTGIR460读取后461/462先local_alloc/local_load转dot layout；ASM1080 vmcnt(0)、1092 barrier先于1475首PV。",
    limits="仅离线定位/CFG复核；没有改原包或数学，没有计时，不把资源增加或缺少PV重叠宣称为已测吞吐回退。")
(HERE / "result.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(dict(status=receipt["status"], load_source_span=receipt["load_source_span"],
                     loads=len(paths), first_wait=1080, first_pv=1475)))
