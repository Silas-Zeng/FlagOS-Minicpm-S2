"""Small CPU-only packaging/source contract; no Torch/Triton simulation."""
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "experiments/official/20261021T092944Z-sql-mixed-official/source"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


transform = load("mapped_source_contract", ROOT / "patches/framework/biv150_mapped_decode_source.py")
runtime = load("mapped_runtime_contract", ROOT / "patches/framework/biv150_mapped_decode.py")
assert "torch" not in sys.modules and "triton" not in sys.modules
runner = (SOURCE / "plugin/vllm_fl/worker/model_runner.py").read_bytes()
attention = (SOURCE / "installed/vllm/v1/attention/ops/triton_unified_attention.py").read_bytes()
helpers = (SOURCE / "installed/vllm/v1/attention/ops/triton_attention_helpers.py").read_bytes()
derived = (ROOT / "patches/framework/biv150_mapped_attention.py").read_bytes()
changed_runner = transform.transform_runner(runner)
assert changed_runner[:-len(transform.RUNNER_FOOTER)] == runner
assert transform.transform_attention(attention, helpers) == derived
assert hashlib.sha256(derived).hexdigest() == runtime.EXPECTED_DERIVED
rejected = 0
for callback, args in ((transform.transform_runner, (runner + b"\n",)),
                       (transform.transform_runner, (changed_runner,)),
                       (transform.transform_attention, (attention + b"\n", helpers)),
                       (transform.transform_attention, (attention, helpers + b"\n"))):
    try:
        callback(*args)
    except RuntimeError:
        rejected += 1
assert rejected == 4

# Compare every floating reduction/dot/exp expression, plus key accumulation
# updates. Address/control changes are intentionally outside this assertion.
fp_calls = {"dot", "exp", "exp2", "sum", "max", "maximum", "minimum", "log", "log2", "clamp"}
fp_names = {"acc", "M", "L", "P", "P_v", "qk", "alpha", "m_ij", "l_ij", "overall_max",
            "overall_expsum", "acc_sum", "segm_expsum", "segm_output"}


def fp_expressions(source):
    tree = ast.parse(source)
    expressions = []
    for fn in tree.body:
        if not isinstance(fn, ast.FunctionDef) or fn.name not in ("kernel_unified_attention", "reduce_segments"):
            continue
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in fp_calls:
                expressions.append((fn.name, "call", ast.dump(node, include_attributes=False)))
            if isinstance(node, (ast.Assign, ast.AugAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(t, ast.Name) and t.id in fp_names for t in targets):
                    # Ignore loads whose pointer addresses were intentionally
                    # remapped; check their downstream FP formulas instead.
                    if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute) and node.value.func.attr == "load":
                        continue
                    expressions.append((fn.name, "assignment", ast.dump(node, include_attributes=False)))
    return sorted(expressions)


assert fp_expressions(attention) == fp_expressions(derived)
for name in ("biv150_mapped_decode_source.py", "biv150_mapped_attention.py", "biv150_mapped_decode.py"):
    path = ROOT / "patches/framework" / name
    compile(path.read_bytes(), str(path), "exec")
gate = ROOT / "scripts/remote/validate_mapped_decode.py"
compile(gate.read_bytes(), str(gate), "exec")
tree = ast.parse(gate.read_bytes())
pins = {node.targets[0].id: ast.literal_eval(node.value) for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id in {"EXPECTED_POLICY", "EXPECTED_TRANSFORM", "EXPECTED_DERIVED"}}
for key, relative in (("EXPECTED_POLICY", "patches/framework/biv150_mapped_decode.py"),
                      ("EXPECTED_TRANSFORM", "patches/framework/biv150_mapped_decode_source.py"),
                      ("EXPECTED_DERIVED", "patches/framework/biv150_mapped_attention.py")):
    assert pins[key] == hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
print(json.dumps({"status": "passed_cpu_source_contract", "unknown_sources_rejected": rejected,
                  "derived_exact": True, "runner_exact_append": True,
                  "floating_expressions_unchanged": len(fp_expressions(attention)),
                  "pins_and_syntax": True, "imports_no_accelerator_runtime": True,
                  "limitations": "No Triton compilation/execution, FP equivalence, stream or performance proof."}, indent=2))
