"""只检新增非单调 end 映射的 CPU 合同；不模拟 Attention 或设备时序。"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace

import numpy as np

BASE_SHA = "cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663"
ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/framework/20261023T044216Z-q-gqa-mixed-coverage-only-diagnostic-control/plugin-source/vllm_fl/worker/model_runner.py"


class Tensor:
    def __init__(self, data):
        self.data = np.asarray(data)

    @property
    def shape(self):
        return self.data.shape

    def __getitem__(self, index):
        if isinstance(index, Tensor):
            index = index.data
        elif isinstance(index, tuple):
            index = tuple(x.data if isinstance(x, Tensor) else x for x in index)
        return Tensor(self.data[index])

    def copy_(self, other, non_blocking=False):
        self.data[...] = other.data
        return self

    def to(self, *args, **kwargs):
        return Tensor(self.data.copy())

    def numpy(self):
        return self.data

    def scatter_(self, dim, index, src):
        assert dim == 0
        self.data[index.data] = src.data
        return self


class Buffer:
    def __init__(self, data):
        self.cpu = Tensor(np.asarray(data).copy())
        self.gpu = Tensor(np.full_like(self.cpu.data, -999999))
        self.copies = 0

    def copy_to_gpu(self, count):
        self.gpu.data[:count] = self.cpu.data[:count]
        self.copies += 1


def method(tree, name):
    found = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(found) == 1, name
    return found[0]


def load_method(candidate):
    raw = BASE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == BASE_SHA
    original = method(ast.parse(raw), "_prepare_input_ids")
    if candidate is not None:
        other = method(ast.parse(candidate.read_bytes()), "_prepare_input_ids")
        assert ast.dump(original, include_attributes=False) == ast.dump(other, include_attributes=False), "原异步输入方法不得被改写"
    calls = []

    def fused(*args):
        calls.append("fused_guard")
        return False

    fake_torch = SimpleNamespace(
        Tensor=Tensor, int64=np.int64, int32=np.int32,
        tensor=lambda values, dtype, pin_memory: Tensor(np.asarray(values, dtype=dtype)),
    )
    env = {"np": np, "torch": fake_torch, "_biv150_fused_sampled_token_update": fused}
    module = ast.Module(body=[original], type_ignores=[])
    exec(compile(ast.fix_missing_locations(module), str(BASE), "exec"), env)
    return env["_prepare_input_ids"], calls


def case(run, calls, name, q, computed, previous):
    """Reference packs explicit (old request, token position) tuples, without inverse formula."""
    n = len(q)
    order = [r for r in range(n) if q[r] == 1] + [r for r in range(n) if q[r] != 1]
    packed = [(r, p) for r in order for p in range(computed[r], computed[r] + q[r])]
    ends = np.array([max(i for i, pair in enumerate(packed) if pair[0] == r) + 1 for r in range(n)], dtype=np.int32)
    cpu_ids = np.array([10000 * r + p for r, p in packed], dtype=np.int32)
    prev_values = np.arange(n + 3, dtype=np.int32) * 13 + 900000
    prev_rows = np.array(previous if previous is not None else [-1] * n, dtype=np.int32)
    runner = SimpleNamespace(
        input_batch=SimpleNamespace(
            prev_sampled_token_ids=None if previous is None else Tensor(prev_values[:, None]),
            req_ids=[f"r{r}" for r in range(n)],
        ),
        input_ids=Buffer(cpu_ids), prev_positions=SimpleNamespace(np=prev_rows),
        enable_prompt_embeds=False, pin_memory=True, device="cpu-substitute",
        prev_num_spec_tokens=0, _draft_token_ids=None,
    )
    before = len(calls)
    run(runner, SimpleNamespace(scheduled_spec_decode_tokens={}), n, len(packed), ends)
    expected = cpu_ids.copy()
    if previous is not None:
        for old_row, previous_row in enumerate(previous):
            if previous_row >= 0:
                # Use explicit request identity, independent of candidate inverse mapping.
                target = max(i for i, (r, _) in enumerate(packed) if r == old_row)
                expected[target] = prev_values[previous_row]
    np.testing.assert_array_equal(runner.input_ids.gpu.data, expected)
    assert len(set(int(x) for x in ends)) == n
    assert runner.input_batch.req_ids == [f"r{r}" for r in range(n)]
    assert runner.input_ids.copies == 1, "mixed 输入必须先完整上传 CPU token"
    return {"name": name, "rows": n, "tokens": len(packed), "ends_by_original": ends.tolist(),
            "used_fused_guard_fallback": len(calls) > before, "pass": True}


def plan_case(helper, q, computed):
    """直接执行新增 plan，冷 scope 已缓存替身不冒充设备资格验证。"""
    n, total = len(q), sum(q)
    original_rows = np.arange(n * 8192, dtype=np.int32).reshape(n, 8192) + 1000
    table_buffer = SimpleNamespace(np=original_rows.copy(), cpu=Tensor(original_rows.copy()),
                                   gpu=Tensor(np.full_like(original_rows, -1)))
    table = SimpleNamespace(block_table=table_buffer)
    mode = SimpleNamespace(FULL_DECODE_ONLY="FULL_DECODE_ONLY", FULL="FULL", PIECEWISE="PIECEWISE", NONE="NONE")
    full, piecewise = {"uniform-full-key"}, set()
    dispatcher = SimpleNamespace(cudagraph_mode=mode.FULL_DECODE_ONLY, cudagraph_keys={mode.FULL: full, mode.PIECEWISE: piecewise})
    prompt = np.array(computed, dtype=np.int32) + np.where(np.array(q) == 1, -3, 100)
    runner = SimpleNamespace(input_batch=SimpleNamespace(num_reqs=n, block_table=[table],
        num_computed_tokens_cpu=np.array(computed, dtype=np.int32),
        num_prompt_tokens_cpu_tensor=Tensor(prompt)), num_prompt_logprobs={},
        cudagraph_dispatcher=dispatcher, positions=Tensor(np.full(total, -1, dtype=np.int64)),
        seq_lens=Tensor(np.full(n + 3, -1, dtype=np.int32)), prepare_inputs_event=object(),
        req_indices=SimpleNamespace(np=np.full(total, -1, dtype=np.int64)),
        num_scheduled_tokens=SimpleNamespace(np=np.full(n, -1, dtype=np.int32)),
        max_num_tokens=total, device="cpu-substitute")
    state = dict(table=table, table_buffer=table_buffer, dispatcher=dispatcher, mode=mode,
        full=full, full_count=len(full), piecewise=piecewise, threshold=64,
        positions_gpu=runner.positions, seq_gpu=runner.seq_lens, event=runner.prepare_inputs_event,
        selected=0)
    for key, shape, dtype in (("table", (n, 8192), np.int32), ("positions", (total,), np.int64),
                             ("seq", (n + 3,), np.int32), ("computed", (n + 3,), np.int32),
                             ("prompt", (n + 3,), np.int32), ("logits", (n + 3,), np.int32)):
        state[key + "_cpu"] = Tensor(np.full(shape, -1, dtype=dtype))
        state[key + "_np"] = state[key + "_cpu"].data
    setattr(runner, helper._STATE, state)
    output = SimpleNamespace(total_num_scheduled_tokens=total, scheduled_spec_decode_tokens={},
        scheduled_encoder_inputs={}, scheduled_cached_reqs=SimpleNamespace(resumed_req_ids=set()),
        has_structured_output_requests=False, pending_structured_output_tokens=False)
    fake_torch = SimpleNamespace(cuda=SimpleNamespace(is_current_stream_capturing=lambda: False))
    previous_torch = sys.modules.get("torch")
    sys.modules["torch"] = fake_torch
    try:
        plan = helper.make_plan(runner, output, np.array(q, dtype=np.int32), max(q))
        assert plan is not None
        order = [r for r in range(n) if q[r] == 1] + [r for r in range(n) if q[r] != 1]
        packed = [(r, pos) for r in order for pos in range(computed[r], computed[r] + q[r])]
        ends_ref = [max(i for i, (r, _) in enumerate(packed) if r == old) + 1 for old in range(n)]
        np.testing.assert_array_equal(plan.permutation, order)
        np.testing.assert_array_equal(plan.ends_by_original, ends_ref)
        plan.copy_block_table(runner)
        np.testing.assert_array_equal(table_buffer.gpu.data, original_rows[order])
        np.testing.assert_array_equal(table_buffer.np, original_rows)
        positions = np.array([pos for _, pos in packed], dtype=np.int64)
        indices = np.array([r for r, _ in packed], dtype=np.int64)
        plan.copy_metadata(runner, positions, indices)
        expected_seq = [computed[r] + q[r] for r in order] + [0] * 3
        np.testing.assert_array_equal(runner.seq_lens.data, expected_seq)
        np.testing.assert_array_equal(runner.positions.data, positions)
        c, p, seq = plan.cpu_metadata(n)
        np.testing.assert_array_equal(c.data, np.array(computed)[order])
        np.testing.assert_array_equal(p.data, prompt[order])
        np.testing.assert_array_equal(seq.data, expected_seq[:n])
        # Simulate the frozen slot formula only: page IDs are deliberately nontrivial.
        actual_slots = []
        offset = 0
        for compute_row, count in enumerate(plan.scheduled):
            for pos in positions[offset:offset + count]:
                actual_slots.append(int(table_buffer.gpu.data[compute_row, pos // 16]) * 16 + int(pos % 16))
            offset += int(count)
        expected_slots = [int(original_rows[r, pos // 16]) * 16 + pos % 16 for r, pos in packed]
        np.testing.assert_array_equal(actual_slots, expected_slots)
        # Hidden vectors encode request identity; preserve all N sampled rows including discarded prefill.
        hidden = np.array([[r, pos] for r, pos in packed], dtype=np.int64)
        logits_indices = plan.logits_indices(runner).data
        np.testing.assert_array_equal(hidden[logits_indices], [[r, computed[r] + q[r] - 1] for r in range(n)])
        plan.check_dispatch(mode.NONE, SimpleNamespace(num_tokens=total, num_reqs=None), False, None)
        rejected = 0
        for m, tokens, nr, ub, dp in ((mode.FULL, total, n, False, None),
                (mode.NONE, total + 1, n, False, None), (mode.NONE, total, n + 1, False, None),
                (mode.NONE, total, n, True, None), (mode.NONE, total, n, False, [total])):
            try:
                plan.check_dispatch(m, SimpleNamespace(num_tokens=tokens, num_reqs=nr), ub, dp)
            except RuntimeError:
                rejected += 1
        assert rejected == 5
        try:
            plan.cpu_metadata(n + 1)
        except RuntimeError:
            pass
        else:
            raise AssertionError("metadata padding未拒绝")
        # A restored request must decline before the next staging write.
        before = {k: v.copy() for k, v in state.items() if k.endswith("_np")}
        output.scheduled_cached_reqs.resumed_req_ids.add("restored")
        assert helper.make_plan(runner, output, np.array(q, dtype=np.int32), max(q)) is None
        for key, old in before.items():
            np.testing.assert_array_equal(state[key], old)
    finally:
        if previous_torch is None:
            del sys.modules["torch"]
        else:
            sys.modules["torch"] = previous_torch
    return {"rows": n, "tokens": total, "full_table_stride": 8192,
            "no_padding_rejections": rejected + 1, "original_sampler_rows": n, "pass": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate", type=Path)
    ap.add_argument("--helper", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    run, calls = load_method(args.candidate)
    fixtures = [
        ("new_requests", [1, 7, 1, 1], [31, 40, 63, 95], None),
        ("mixed_identity_slice_with_nonmonotonic_ends", [1, 7, 1, 1], [31, 40, 63, 95], [0, -1, 1, 2]),
        ("previous_rows_permuted", [1, 7, 1, 1], [31, 40, 63, 95], [3, -1, 1, 0]),
        ("new_decode_and_continuing_prefill", [1, 7, 1, 1], [31, 40, 63, 95], [-1, 2, 0, -1]),
        ("multiple_prefill_segments", [1, 3, 1, 4, 1], [15, 16, 31, 29, 47], [4, 3, 1, -1, 0]),
        ("observed_n17_geometry", [1, 233] + [1] * 15, list(range(32, 49)), [16, -1] + list(range(15))),
    ]
    results = [case(run, calls, *fixture) for fixture in fixtures]
    plan_results = []
    if args.helper is not None:
        spec = importlib.util.spec_from_file_location("compute_order_under_review", args.helper)
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        plan_results = [plan_case(helper, fixture[1], fixture[2]) for fixture in (fixtures[4], fixtures[5])]
    receipt = {
        "gate": "新增非单调 ends_by_original 与真实原异步输入方法的 CPU 合同",
        "baseline_sha256": BASE_SHA,
        "candidate_sha256": hashlib.sha256(args.candidate.read_bytes()).hexdigest() if args.candidate else None,
        "helper_sha256": hashlib.sha256(args.helper.read_bytes()).hexdigest() if args.helper else None,
        "cases": results,
        "plan_cases": plan_results,
        "scope": "仅执行原 _prepare_input_ids AST 与 NumPy/Tensor 替身；fused helper 故意回退原 scatter；没有执行 CUDA、Attention、sampler 或性能测试。",
        "not_proven": ["冷scope/source资格与完整prepare接线", "真实 fused helper 动态接受率", "pinned H2D 生命周期/真实设备次序", "logits 数值与准确率", "性能收益"],
    }
    with args.output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(receipt, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(json.dumps({"passed": len(results), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
