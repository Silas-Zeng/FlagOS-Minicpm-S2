"""唯一新增 CPU 合同：实际 scope AST、覆盖资格、源码逆回；不模拟 GPU。"""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace as NS

sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    spec = importlib.util.spec_from_file_location("decode_cpu_gather_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Tensor:
    next_ptr = 1024

    def __init__(self, shape, device="cuda", dtype="int32"):
        self.shape, self.device, self.dtype = shape, NS(type=device), dtype
        self.ndim = len(shape)
        Tensor.next_ptr += 4096
        self.ptr = Tensor.next_ptr

    def stride(self, index):
        return int(np.prod(self.shape[index + 1:]))

    def is_contiguous(self):
        return True

    def untyped_storage(self):
        return NS(data_ptr=lambda: self.ptr)


def pure_scope(path, name, namespace):
    node = next(n for n in ast.parse(path.read_bytes()).body
                if isinstance(n, ast.FunctionDef) and n.name == name)
    unit = ast.Module(body=[copy.deepcopy(node)], type_ignores=[])
    exec(compile(ast.fix_missing_locations(unit), "actual-cpu-scope:" + name, "exec"), namespace)
    return namespace[name]


def fixture():
    text = NS(hidden_size=2048, num_hidden_layers=42, num_attention_heads=16, num_key_value_heads=2)
    model = NS(model="/workspace/MiniCPM5-2B", dtype="bf16", quantization=None,
               hf_text_config=text, is_encoder_decoder=False)
    parallel = NS(tensor_parallel_size=1, pipeline_parallel_size=1,
                  decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False)
    config = NS(model_config=model, parallel_config=parallel, speculative_config=None,
                lora_config=None, cache_config=NS(kv_sharing_fast_prefill=False))
    ids = ["req-%d" % i for i in range(62)]
    batch = NS(num_reqs=62, req_ids=ids, prev_req_id_to_index={rid: i for i, rid in enumerate(ids)},
               prev_sampled_token_ids=Tensor((62, 1)), req_prompt_embeds={},
               token_ids_cpu_tensor=Tensor((64, 131072), "cpu"),
               num_computed_tokens_cpu=np.full(64, 4096, dtype=np.int32))
    runner = NS(vllm_config=config, device=NS(type="cuda"), pin_memory=True,
                max_num_reqs=64, input_batch=batch, prepare_inputs_event=object(),
                input_ids=NS(cpu=Tensor((2048,), "cpu"), gpu=Tensor((2048,))),
                is_pooling_model=False, supports_mm_inputs=False, enable_prompt_embeds=False,
                use_aux_hidden_state_outputs=False, uses_mrope=False, uses_xdrope_dim=0,
                use_async_spec_decode=False, use_async_scheduling=True,
                num_spec_tokens=0, prev_num_spec_tokens=0, _draft_token_ids=None,
                mamba_prev_last_scheduled_idx=None)
    output = NS(total_num_scheduled_tokens=62, scheduled_spec_decode_tokens={})
    return runner, output, np.ones(62, dtype=np.int32)


def main():
    start = time.perf_counter()
    policy_path = HERE / "biv150_decode_cpu_gather.py"
    policy = load(policy_path)
    source_path = ROOT / "docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py"
    raw = source_path.read_bytes()
    candidate = policy.transform(raw)
    assert policy.reverse(candidate) == raw
    for bad in (raw + b"\n", candidate):
        try:
            policy.transform(bad)
        except ValueError:
            pass
        else:
            raise AssertionError("accepted changed/already-transformed source")
    original_ast, candidate_ast = ast.parse(raw), ast.parse(candidate)
    original_cls = next(n for n in original_ast.body if isinstance(n, ast.ClassDef) and n.name == "ModelRunnerFL")
    candidate_cls = next(n for n in candidate_ast.body if isinstance(n, ast.ClassDef) and n.name == "ModelRunnerFL")
    for name in ("_prepare_input_ids", "synchronize_input_prep", "_compute_prev_positions", "_get_cumsum_and_arange"):
        left = next(n for n in original_cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        right = next(n for n in candidate_cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
        assert ast.dump(left, include_attributes=False) == ast.dump(right, include_attributes=False), name
    cpu_sites, upload_sites = [], []
    for node in ast.walk(original_cls):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Attribute):
            value = node.value
            if isinstance(value.value, ast.Name) and value.value.id == "self" and value.attr == "input_ids":
                if node.attr in ("cpu", "np"):
                    cpu_sites.append(node.lineno)
                elif node.attr == "copy_to_gpu":
                    upload_sites.append(node.lineno)
    assert sorted(cpu_sites) == [2023], cpu_sites
    assert sorted(upload_sites) == [1794, 1852], upload_sites
    torch = NS(Tensor=Tensor, int32="int32", bfloat16="bf16")
    metadata_path = ROOT / "patches/framework/biv150_cpu_metadata.py"
    async_path = ROOT / "patches/framework/biv150_async_token_update.py"
    assert sha(metadata_path) == policy.EXPECTED_METADATA
    assert sha(async_path) == policy.EXPECTED_ASYNC
    metadata = NS(__file__=str(metadata_path),
                  _scope=pure_scope(metadata_path, "_scope", {"Path": Path}))
    asynchronous = NS(__file__=str(async_path), _runner_eligible=pure_scope(
        async_path, "_runner_eligible", {"Path": Path, "torch": torch, "current_platform": NS(vendor_name="iluvatar")}))
    names = ("torch", "vllm_fl.patches.biv150_cpu_metadata", "vllm_fl.patches.biv150_async_token_update")
    previous = {name: sys.modules.get(name) for name in names}
    checked = []
    try:
        sys.modules.update(dict(zip(names, (torch, metadata, asynchronous))))
        for label, change, expected in (
            ("identity", lambda r, o, a: None, True),
            ("reverse", lambda r, o, a: r.input_batch.prev_req_id_to_index.update(
                {rid: 61 - i for i, rid in enumerate(r.input_batch.req_ids)}), True),
            ("new-request", lambda r, o, a: r.input_batch.prev_req_id_to_index.pop("req-61"), False),
            ("no-previous", lambda r, o, a: setattr(r.input_batch, "prev_sampled_token_ids", None), False),
            ("duplicate-row", lambda r, o, a: r.input_batch.prev_req_id_to_index.update({"req-61": 0}), False),
            ("out-of-range-row", lambda r, o, a: r.input_batch.prev_req_id_to_index.update({"req-61": 62}), False),
            ("negative-row", lambda r, o, a: r.input_batch.prev_req_id_to_index.update({"req-61": -1}), False),
            ("duplicate-request", lambda r, o, a: r.input_batch.req_ids.__setitem__(61, "req-0"), False),
            ("mixed", lambda r, o, a: a.__setitem__(61, 2), False),
            ("spec", lambda r, o, a: o.scheduled_spec_decode_tokens.update({"req-0": [1]}), False),
            ("draft", lambda r, o, a: setattr(r, "_draft_token_ids", object()), False),
            ("embeds", lambda r, o, a: r.input_batch.req_prompt_embeds.update({0: object()}), False),
            ("enabled-embeds", lambda r, o, a: setattr(r, "enable_prompt_embeds", True), False),
            ("multimodal", lambda r, o, a: setattr(r, "supports_mm_inputs", True), False),
            ("bad-position", lambda r, o, a: r.input_batch.num_computed_tokens_cpu.__setitem__(0, -1), False),
            ("source-alias", lambda r, o, a: setattr(r.input_ids.cpu, "ptr", r.input_batch.token_ids_cpu_tensor.ptr), False),
        ):
            runner, output, lengths = fixture()
            change(runner, output, lengths)
            actual = policy.skip_dead_cpu_gather(runner, output, lengths)
            assert actual is expected, (label, actual)
            state = getattr(runner, policy.STATE)
            assert state == {"selected": int(expected), "fallback": int(not expected)}
            checked.append(label)
        # Qualification is recomputed after a successful step, not cached.
        runner, output, lengths = fixture()
        assert policy.skip_dead_cpu_gather(runner, output, lengths)
        runner.input_batch.prev_req_id_to_index.pop("req-0")
        assert not policy.skip_dead_cpu_gather(runner, output, lengths)
    finally:
        for name, value in previous.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value
    assert "torch" not in sys.modules and "triton" not in sys.modules and "vllm" not in sys.modules
    result = {"status": "pass", "kind": "one CPU source/descriptor contract, not GPU emulation",
              "elapsed_seconds": time.perf_counter() - start,
              "policy_sha256": sha(policy_path), "candidate_runner_sha256": hashlib.sha256(candidate).hexdigest(),
              "source_sha256": sha(source_path), "guard_cases": checked,
              "all_original_gpu_input_id_and_event_methods_ast_identical": True,
              "byte_reverse_exact": True, "self_input_ids_direct_cpu_np_sites": cpu_sites,
              "self_input_ids_indirect_upload_sites": upload_sites,
              "step_local_qualification": True, "Torch_Triton_vLLM_imported": False,
              "GPU_stream_copy_graph_RNG_performance": "not executed; root-owned device gate required"}
    (HERE / "cpu-check.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
