"""Replay the exact installed SME bit-selector with CPU tensor descriptors.

This runs only the pinned selector AST with stub imports; no Torch/Triton is
loaded. It proves descriptor-to-mask arithmetic, not native JIT/FP execution.
"""
import ast
import copy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[3]
ACTUAL = ROOT / "experiments/source-audits/20261021T183920Z-compiler-cache/installed-triton/spec/iluvatar/triton/runtime/jit.py"
assert hashlib.sha256(ACTUAL.read_bytes()).hexdigest() == "66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775"
tree = ast.parse(ACTUAL.read_bytes())
fn = copy.deepcopy(next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "get_corex_sme"))
# The only removed statements import torch/os; all selection arithmetic and
# branching execute unchanged against explicit descriptors and disabled=0.
fn.body = [node for node in fn.body if not isinstance(node, ast.Import)]


class Tensor:
    def __init__(self, shape, dtype="bfloat16", contiguous=True):
        self.shape, self.dtype, self.contiguous = shape, dtype, contiguous

    def dim(self):
        return len(self.shape)

    def squeeze(self):
        return Tensor(tuple(n for n in self.shape if n != 1), self.dtype, self.contiguous)

    def is_contiguous(self):
        return self.contiguous

    def element_size(self):
        return {"float32": 4, "float16": 2, "bfloat16": 2, "int8": 1, "int32": 4}[self.dtype]


torch = NS(corex=True, float16="float16", bfloat16="bfloat16", float32="float32", int8="int8",
           is_tensor=lambda value: isinstance(value, Tensor))
scope = {"torch": torch, "os": NS(getenv=lambda name, default=None: default)}
exec(compile(ast.Module(body=[fn], type_ignores=[]), str(ACTUAL) + ":get_corex_sme_imports_stubbed", "exec"), scope)
select = scope["get_corex_sme"]
out = Tensor((2048, 16, 128))
cu = Tensor((31,), "int32")
cache = Tensor((30 * 1025, 16, 2, 128), contiguous=False)
values = {"output_ptr": out, "query_ptr": out, "key_cache_ptr": cache, "value_cache_ptr": cache,
          "block_tables_ptr": Tensor((30, 1025), "int32"), "seq_lens_ptr": Tensor((30,), "int32"),
          "k_scale": Tensor((30, 2), "float32", contiguous=False),
          "v_scale": Tensor((30, 2), "float32", contiguous=False),
          "query_start_len_ptr": cu, "segm_output_ptr": out, "segm_max_ptr": out,
          "segm_expsum_ptr": out, "k_scale_cache_ptr": cache, "v_scale_cache_ptr": cache}
none = {"sink_ptr", "alibi_slopes_ptr", "qq_bias_ptr", "q_scale", "per_seq_causal_ptr", "mm_prefix_range_ptr"}


def mask(path, dummy=None):
    node = next(n for n in ast.parse(path.read_bytes()).body
                if isinstance(n, ast.FunctionDef) and n.name == "kernel_unified_attention")
    args, specialization, indices = [], [], {}
    position = 0
    for arg in node.args.args:
        constexpr = arg.annotation is not None and ast.unparse(arg.annotation) == "tl.constexpr"
        value = None if arg.arg in none else values.get(arg.arg, 0)
        if arg.arg == "decode_req_indices_ptr":
            value = dummy
        # Actual native-specialize represents None as constexpr; the six
        # None bindings are also independently consistent with the failing
        # numeric mask (segment output operands at bits25/26/27).
        constant = constexpr or value is None
        args.append(value)
        specialization.append(("constexpr" if constant else "pointer-or-scalar", None))
        if not constant:
            indices[arg.arg] = position
            position += 1
    return select(args, specialization), indices


original = ROOT / "experiments/official/20261021T092944Z-sql-mixed-official/source/installed/vllm/v1/attention/ops/triton_unified_attention.py"
broken = ROOT / "experiments/framework/20261021T183421Z-mapped-decode-gate/source/candidate_attention.py"
fixed = ROOT / "patches/framework/biv150_mapped_attention.py"
prefix = ROOT / "analysis/source/prefill-visible-prefix/triton_unified_attention_visible_prefix.py"
assert hashlib.sha256(broken.read_bytes()).hexdigest() == "67a9830eaa976e79d9d21f5f34ec4bbfe0215d3082d6571d415c1c8f33a85f47"
base, _ = mask(original)
before, positions = mask(broken, out)
after, _ = mask(fixed, cu)
prefix_mask, _ = mask(prefix)
assert positions["decode_req_indices_ptr"] == 36
assert base == after == prefix_mask == 0x0E000003
assert before == 68954357763 == base | (1 << 36)
assert before ^ after == 1 << 36
assert b"if biv150_mapped_decode else out," not in fixed.read_bytes()
assert fixed.read_bytes().count(b"if biv150_mapped_decode else cu_seqlens_q,") == 2
print(json.dumps({"status": "passed_actual_selector_descriptor_contract",
                  "actual_jit_sha256": hashlib.sha256(ACTUAL.read_bytes()).hexdigest(),
                  "baseline_mask": base, "prefix_mask": prefix_mask,
                  "failing_mask_exactly_reproduced": before, "corrected_mask": after,
                  "new_dummy_operand_index": 36, "removed_only_mask_bit": 36,
                  "no_use_sme_override": True,
                  "limitations": "AST selector on explicit CPU descriptors; native specializer, JIT/compiler, device output and model accuracy still untested."}, indent=2))
