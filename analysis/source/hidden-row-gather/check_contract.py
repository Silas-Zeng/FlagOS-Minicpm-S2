"""Small CPU source/seam checks; no torch, Triton, vLLM, remote or device import."""
import ast
import hashlib
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
runtime_path = ROOT / "patches/framework/biv150_hidden_row_gather.py"
transform_path = ROOT / "patches/framework/biv150_hidden_row_gather_source.py"
original = (ROOT / "experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/"
            "plugin/vllm_fl/worker/model_runner.py").read_bytes()
spec = importlib.util.spec_from_file_location("hidden_gather_transform", transform_path)
transform = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transform)
changed = transform.transform_source(original)
compile(changed, "isolated:hidden-gather-runner", "exec")
assert changed.count(b"BIV150_FINAL_HIDDEN_ROW_GATHER_V1") == 2
assert changed.count(transform.IMPORT) == 1
assert changed.count(transform.REPLACEMENT) == 2
assert changed.replace(transform.IMPORT, b"", 1).replace(
    transform.REPLACEMENT, transform.ORIGINAL) == original
tree = ast.parse(changed)
calls = [x for x in ast.walk(tree) if isinstance(x, ast.Call)
         and isinstance(x.func, ast.Name) and x.func.id == "_biv150_try_hidden_row_gather"]
assert len(calls) == 2
assert all([x.id for x in call.args] == ["self", "hidden_states", "logits_indices",
                                       "num_scheduled_tokens_np"] for call in calls)
for invalid in (b"# mutation\n" + original, changed, original.replace(b"import torch\n", b"import torch \n", 1)):
    try:
        transform.transform_source(invalid)
    except RuntimeError:
        pass
    else:
        raise AssertionError("unaudited/repeated runner transformation accepted")
print("exact source, both branch sites, fallback inverse, syntax and fail-closed transform: PASS")

runtime_tree = ast.parse(runtime_path.read_text(encoding="utf-8"))
selected = [x for x in runtime_tree.body if isinstance(x, ast.FunctionDef)
            and x.name == "_query_end_contract"]
namespace = {"np": np}
exec(compile(ast.Module(body=selected, type_ignores=[]), "runtime:CPU-query-proof", "exec"), namespace)
proof = namespace["_query_end_contract"]
for total, count in ((259, 29), (952, 16), (62, 62)):
    lengths = np.array([1] * (count - 1) + [total - count + 1], dtype=np.int32)
    ends = np.cumsum(lengths, dtype=np.int32)
    runner = NS(query_start_loc=NS(np=np.r_[np.int32(0), ends]))
    assert proof(runner, lengths, count, total + 3)
    assert not proof(runner, lengths, count, total - 1)
    assert not proof(runner, lengths.astype(np.int64), count, total)
    bad = lengths.copy()
    bad[0] = 0
    assert not proof(runner, bad, count, total)
    runner.query_start_loc.np[-1] -= 1
    assert not proof(runner, lengths, count, total)
print("existing CPU query ends prove non-spec index bounds; malformed/changed proof rejects: PASS")

kernel = next(x for x in runtime_tree.body if isinstance(x, ast.FunctionDef)
              and x.name == "_copy_hidden_rows")
decorator = kernel.decorator_list[0]
assert isinstance(decorator, ast.Call)
assert {x.arg: ast.literal_eval(x.value) for x in decorator.keywords} == {
    "do_not_specialize": ["rows", "count"]}
print("kernel M/N explicitly runtime do_not_specialize; no source mutation or GPU claim: PASS")
print("transformed_runner_sha256=" + hashlib.sha256(changed).hexdigest())
