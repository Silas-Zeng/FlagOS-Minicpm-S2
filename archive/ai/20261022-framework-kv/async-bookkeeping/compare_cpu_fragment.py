"""纯CPU原片段比较：不是服务runtime，不导入torch/vLLM，不改变线程配置。"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
from time import perf_counter_ns, thread_time_ns
from types import SimpleNamespace as NS
import numpy as np

EXPECTED_RUNNER = '6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141'
DEFAULT_RUNNER = Path('docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py')


def extract_baseline(path):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != EXPECTED_RUNNER:
        raise ValueError('only actual6f source accepted')
    text = raw.decode()
    tree = ast.parse(text)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'ModelRunnerFL')
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_bookkeeping_sync')
    loop = next(n for n in fn.body if isinstance(n, ast.For) and isinstance(n.target, ast.Name)
                and n.target.id == 'req_idx')
    # 原for完整AST，连async分支、range assert、三数组写及history.extend一起保留。
    original = ast.get_source_segment(text, loop)
    original = '\n'.join(line[8:] if i and line.startswith('        ') else line
                         for i, line in enumerate(original.splitlines()))
    source = ('def baseline(self, n, invalid, no_spec=True, total_tokens=None):\n'
              '    num_sampled_tokens = n\n    invalid_req_indices_set = invalid\n'
              '    valid_sampled_token_ids = []\n    req_ids = self.input_batch.req_ids\n' +
              '\n'.join('    '+line for line in original.splitlines()) + '\n    return False\n')
    namespace = {}
    exec(compile(source, 'extracted-original-bookkeeping-loop', 'exec'), namespace)
    return namespace['baseline'], source


def candidate(self, n, invalid, no_spec=True, total_tokens=None):
    batch = self.input_batch
    ids, flags, counts = batch.token_ids_cpu, batch.is_token_ids, batch.num_tokens_no_spec
    # 全部新增guard、view、copy和reduction在计时内；不依赖token内容/请求序号。
    if (n < 16 or not self.use_async_scheduling or not no_spec or invalid
            or n != batch.num_reqs or total_tokens != n
            or ids.dtype != np.int32 or flags.dtype != np.bool_ or counts.dtype != np.int32
            or ids.ndim != 2 or flags.shape != ids.shape or counts.ndim != 1
            or ids.shape[0] < n or counts.size < n or ids.shape[1] != self.max_model_len
            or not ids.flags.writeable or not flags.flags.writeable or not counts.flags.writeable):
        return self.baseline(self, n, invalid, no_spec, total_tokens)
    # 必须copy，不能让后续counts写入改变scatter的旧列索引。
    starts = counts[:n].copy()
    if starts.min() < 0 or starts.max() >= self.max_model_len:
        return self.baseline(self, n, invalid, no_spec, total_tokens)
    rows = self.arange_np[:n]
    ends = starts + 1
    ids[rows, starts] = -1
    flags[rows, starts] = True
    counts[:n] = ends
    # 保留实际每请求history更新，不能把它挪窗外或据此声称省D2H/events。
    req_ids = batch.req_ids
    for req_idx in range(n):
        self.requests[req_ids[req_idx]].output_token_ids.extend([-1])
    return True


def fixture(n, baseline):
    # 活跃64行即可保原131072列/row stride，三种dtype均取actual InputBatch。
    ids = np.zeros((64, 131072), dtype=np.int32)
    flags = np.zeros((64, 131072), dtype=np.bool_)
    counts = np.zeros(64, dtype=np.int32)
    request_ids = ['r'+str(i) for i in range(n)]
    return NS(input_batch=NS(num_reqs=n, req_ids=request_ids, token_ids_cpu=ids,
                            is_token_ids=flags, num_tokens_no_spec=counts),
              requests={rid:NS(output_token_ids=[]) for rid in request_ids},
              use_async_scheduling=True, max_model_len=131072,
              arange_np=np.arange(2048, dtype=np.int64), baseline=baseline)


def reset(state, n):
    state.input_batch.num_tokens_no_spec[:n] = 16384 + np.arange(n, dtype=np.int32) * 7
    for value in state.requests.values():
        value.output_token_ids.clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runner', type=Path, default=DEFAULT_RUNNER)
    parser.add_argument('--calls', type=int, default=1024)
    parser.add_argument('--output', type=Path, default=Path(__file__).with_name('cpu-result.json'))
    args = parser.parse_args()
    if not 32 <= args.calls <= 4096:
        raise ValueError('bounded CPU comparison only')
    baseline, original = extract_baseline(args.runner)
    results = []
    for n in (30, 31, 64, 1):
        a, b = fixture(n, baseline), fixture(n, baseline)
        reset(a, n); reset(b, n)
        for _ in range(32):
            baseline(a, n, set(), True, n)
            selected = candidate(b, n, set(), True, n)
        checks = {
            'ids_equal': np.array_equal(a.input_batch.token_ids_cpu, b.input_batch.token_ids_cpu),
            'flags_equal': np.array_equal(a.input_batch.is_token_ids, b.input_batch.is_token_ids),
            'counts_equal': np.array_equal(a.input_batch.num_tokens_no_spec, b.input_batch.num_tokens_no_spec),
            'history_equal': all(a.requests[r].output_token_ids == b.requests[r].output_token_ids for r in a.requests),
            'selection_matches_scope': selected is (n >= 16),
            'index_snapshot_separate': not np.shares_memory(b.input_batch.num_tokens_no_spec,
                                                          b.input_batch.num_tokens_no_spec[:n].copy()),
        }
        if not all(checks.values()):
            raise AssertionError(checks)
        windows = []
        for label, fn, state in (('A1', baseline, a), ('B1', candidate, b),
                                 ('B2', candidate, b), ('A2', baseline, a)):
            reset(state, n)  # reset/allocation不在窗内，两个路径都保history增长。
            selected_count = 0
            wall0, cpu0 = perf_counter_ns(), thread_time_ns()
            for _ in range(args.calls):
                selected_count += bool(fn(state, n, set(), True, n))
            cpu_elapsed, wall_elapsed = thread_time_ns()-cpu0, perf_counter_ns()-wall0
            windows.append({'label':label, 'calls':args.calls, 'selected':selected_count,
                            'wall_ns_per_call':wall_elapsed/args.calls,
                            'thread_cpu_ns_per_call':cpu_elapsed/args.calls})
        results.append({'N':n, 'checks':checks, 'windows':windows,
                        'row_stride_bytes':a.input_batch.token_ids_cpu.strides[0],
                        'dtypes':[str(a.input_batch.token_ids_cpu.dtype),str(a.input_batch.is_token_ids.dtype),
                                  str(a.input_batch.num_tokens_no_spec.dtype)]})
    value = {'runner_sha256':EXPECTED_RUNNER, 'numpy_version':np.__version__, 'results':results,
             'original_loop_source':original,
             'limits':['local CPU fragment; not BI-V150 service or accuracy',
                       'full guards/start copy/ends/history append included',
                       'no D2H/event/prev mapping/output snapshot changes',
                       'mutation failure must propagate; never fallback after writes',
                       'queue2 can hide CPU saving; no E2E gain inferred']}
    args.output.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(args.output),'N':[r['N'] for r in results],'checks_passed':True}))


if __name__=='__main__':main()
