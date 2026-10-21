"""Minimal CPU packaging check, not a simulated stream/tensor correctness test."""
import ast
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]
runtime = ROOT / "patches/framework/biv150_mixed_attention_overlap.py"
gate = ROOT / "scripts/remote/validate_mixed_attention_overlap.py"
tree = ast.parse(gate.read_text(encoding="utf-8"))
expected = next(ast.literal_eval(x.value) for x in tree.body if isinstance(x, ast.Assign)
                and isinstance(x.targets[0], ast.Name) and x.targets[0].id == "EXPECTED_OVERLAP")
assert hashlib.sha256(runtime.read_bytes()).hexdigest() == expected
compile(runtime.read_bytes(), str(runtime), "exec")
compile(gate.read_bytes(), str(gate), "exec")
comprehensions = [x for x in ast.walk(tree) if isinstance(x, ast.DictComp)
                  and isinstance(x.value, ast.Call) and isinstance(x.value.func, ast.Name)
                  and x.value.func.id == "digest"]
assert len(comprehensions) == 2
with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as folder:
    source = Path(folder)
    candidate = source / "overlap.py"
    candidate.write_bytes(runtime.read_bytes())
    spec = importlib.util.spec_from_file_location("overlap_cpu_source_contract", candidate)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    assert "torch" not in sys.modules and "triton" not in sys.modules
    # Include a real/synthetic bytecode directory as produced by a source load.
    (source / "__pycache__").mkdir(exist_ok=True)
    result_scope = {"source": source, "run": source.parent,
                    "digest": lambda path: hashlib.sha256(path.read_bytes()).hexdigest()}
    for expression in comprehensions:
        # Worker uses (run / 'source'); normalize only its path expression for
        # this local directory while retaining the exact file filter/hash body.
        if isinstance(expression.generators[0].iter.func.value, ast.BinOp):
            result_scope["run"] = source.parent
            nested = source / "source"
            nested.mkdir()
            (nested / "overlap.py").write_bytes(runtime.read_bytes())
            (nested / "__pycache__").mkdir()
            result_scope["run"] = source
        mapped = eval(compile(ast.Expression(expression), "gate:actual-source-hash-comprehension", "eval"), result_scope)
        assert mapped == {"overlap.py": expected}
    del sys.modules[spec.name]
print("runtime/gate syntax and pinned runtime SHA: PASS")
print("prototype import loads no torch/Triton/device context: PASS")
print("both actual source-hash comprehensions ignore __pycache__ directories: PASS")
print("CPU packaging only; no stream, tensor, bitwise or performance proof")
