"""精确422→423计算序候选；默认仅生成隔离文件，不导入框架或操作设备。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
BASE_MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
HELPER_SHA = '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce'
RUNNER_PATH = 'vllm_fl/worker/model_runner.py'
MODULE_PATH = 'vllm_fl/patches/biv150_compute_order.py'
PINS = {RUNNER_PATH: RUNNER,
    'vllm_fl/patches/biv150_kv_worker.py': '2de7802d7b07d6f11c8e8f304df36d5503c1189cee9d4ad60f3fbc80fbb98a52',
    'vllm_fl/patches/biv150_kv_protocol.py': '91185a23dd56cc7b1d882e9b4b3ccbfdb0d491dce060e658b183ee563d04d3ab'}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def transform_runner(raw):
    if sha(raw) != RUNNER:
        raise ValueError('只接受原422 cc442 runner')
    edits = []
    def edit(old, new):
        nonlocal raw
        old, new = old.encode(), new.encode()
        if raw.count(old) != 1:
            raise ValueError('精确切口不唯一：' + old[:100].decode())
        raw = raw.replace(old, new)
        edits.append((old, new))
    edit('from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n',
         'from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update\n'
         'from vllm_fl.patches.biv150_compute_order import make_plan as _biv150_compute_order_plan\n')
    edit('    def _prepare_inputs(\n        self,\n        scheduler_output: "SchedulerOutput",\n        num_scheduled_tokens: np.ndarray,\n',
         '    def _prepare_inputs(\n        self,\n        scheduler_output: "SchedulerOutput",\n        num_scheduled_tokens: np.ndarray,\n        compute_order=None,\n')
    edit('        self.input_batch.block_table.commit_block_table(num_reqs)\n',
         '        if compute_order is None:\n            self.input_batch.block_table.commit_block_table(num_reqs)\n'
         '        else:\n            compute_order.copy_block_table(self)\n')
    edit('        req_indices = np.repeat(self.arange_np[:num_reqs], num_scheduled_tokens)\n',
         '        req_indices = np.repeat(\n            self.arange_np[:num_reqs] if compute_order is None else compute_order.permutation,\n'
         '            num_scheduled_tokens if compute_order is None else compute_order.scheduled,\n        )\n')
    edit('        cu_num_tokens = self._get_cumsum_and_arange(\n            num_scheduled_tokens, self.query_pos.np\n        )\n',
         '        cu_num_tokens = self._get_cumsum_and_arange(\n'
         '            num_scheduled_tokens if compute_order is None else compute_order.scheduled, self.query_pos.np\n        )\n')
    edit('        if not _biv150_try_cpu_metadata(self, positions_np, req_indices, num_scheduled_tokens):\n',
         '        if compute_order is not None:\n            compute_order.copy_metadata(self, positions_np, req_indices)\n'
         '        elif not _biv150_try_cpu_metadata(self, positions_np, req_indices, num_scheduled_tokens):\n')
    edit('            cu_num_tokens,\n        )\n\n        if self.uses_mrope:',
         '            cu_num_tokens if compute_order is None else compute_order.ends_by_original,\n        )\n\n        if self.uses_mrope:')
    edit('            logits_indices = query_start_loc[1:] - 1\n',
         '            logits_indices = (query_start_loc[1:] - 1 if compute_order is None\n'
         '                              else compute_order.logits_indices(self))\n')
    edit('        slot_mappings: dict[int, torch.Tensor] | None = None,\n',
         '        slot_mappings: dict[int, torch.Tensor] | None = None,\n        compute_order=None,\n')
    old = ('        num_computed_tokens_cpu = self.input_batch.num_computed_tokens_cpu_tensor[\n'
           '            :num_reqs_padded\n        ]\n'
           '        num_prompt_tokens_cpu = self.input_batch.num_prompt_tokens_cpu_tensor[\n'
           '            :num_reqs_padded\n        ]\n'
           '        seq_lens_cpu = self.optimistic_seq_lens_cpu[:num_reqs_padded]\n')
    edit(old, '        if compute_order is not None:\n'
         '            num_computed_tokens_cpu, num_prompt_tokens_cpu, seq_lens_cpu = compute_order.cpu_metadata(num_reqs_padded)\n'
         '        else:\n' + ''.join('    ' + line for line in old.splitlines(keepends=True)))
    edit('            logits_indices, spec_decode_metadata = self._prepare_inputs(\n'
         '                scheduler_output,\n                num_scheduled_tokens_np,\n            )\n',
         '            compute_order = _biv150_compute_order_plan(\n'
         '                self, scheduler_output, num_scheduled_tokens_np, max_num_scheduled_tokens\n            )\n'
         '            logits_indices, spec_decode_metadata = self._prepare_inputs(\n'
         '                scheduler_output,\n                num_scheduled_tokens_np,\n                compute_order=compute_order,\n            )\n')
    edit('            logger.debug(\n                "Running batch with cudagraph_mode: %s, batch_descriptor: %s, "',
         '            if compute_order is not None:\n'
         '                compute_order.check_dispatch(cudagraph_mode, batch_desc, should_ubatch, num_tokens_across_dp)\n\n'
         '            logger.debug(\n                "Running batch with cudagraph_mode: %s, batch_descriptor: %s, "')
    edit('                    cascade_attn_prefix_lens=cascade_attn_prefix_lens,\n                    slot_mappings=slot_mappings_by_group,\n',
         '                    cascade_attn_prefix_lens=cascade_attn_prefix_lens,\n                    slot_mappings=slot_mappings_by_group,\n                    compute_order=compute_order,\n')
    edit('        with record_function_or_nullcontext("gpu_model_runner: postprocess"):\n',
         '        if compute_order is not None:\n            compute_order.forward_returned()\n\n'
         '        with record_function_or_nullcontext("gpu_model_runner: postprocess"):\n')
    original = raw
    for old, new in reversed(edits):
        if original.count(new) != 1:
            raise ValueError('逆回切口不唯一')
        original = original.replace(new, old)
    if sha(original) != RUNNER:
        raise ValueError('未精确逆回原runner')
    compile(raw, RUNNER_PATH, 'exec')
    return raw, edits


def mapping(folder):
    result = {}
    for p in sorted(folder.rglob('*')):
        rel = p.relative_to(folder)
        if any(x in ('.git', '__pycache__') for x in rel.parts) or p.suffix in ('.pyc', '.pyo'):
            continue
        if p.is_symlink() and (not p.resolve().is_file() or not p.resolve().is_relative_to(folder.resolve())):
            raise ValueError('外部/目录链接不支持')
        if p.is_file():
            result[rel.as_posix()] = sha(p.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--emit-only', action='store_true', help='仅四个变更文件镜像，不整copy')
    args = parser.parse_args()
    base, output = args.base.resolve(strict=True), args.output.resolve()
    map_bytes = (HERE / 'base-source-sha256.json').read_bytes()
    if sha(map_bytes) != BASE_MAP_SHA or mapping(base) != json.loads(map_bytes):
        raise ValueError('固定422完整map不符')
    expected = json.loads(map_bytes)
    helper = (HERE / 'biv150_compute_order.py').read_bytes()
    if HELPER_SHA is None or sha(helper) != HELPER_SHA:
        raise ValueError('helper尚未冻结或source漂移')
    changes = {MODULE_PATH: helper}
    originals = {name: (base / name).read_bytes() for name in PINS}
    if any(sha(originals[name]) != pin for name, pin in PINS.items()):
        raise ValueError('基点三个原源不符')
    runner, edits = transform_runner(originals[RUNNER_PATH])
    runner_sha = sha(runner)
    if (f"EXPECTED_RUNNER = '{runner_sha}'").encode() not in helper:
        raise ValueError('helper未锁本次精确runner')
    changes[RUNNER_PATH] = runner
    for name in PINS:
        if name == RUNNER_PATH:
            continue
        old = originals[name]
        if old.count(RUNNER.encode()) != 1:
            raise ValueError('worker/protocol runner锁不唯一')
        changes[name] = old.replace(RUNNER.encode(), runner_sha.encode())
        if changes[name].replace(runner_sha.encode(), RUNNER.encode()) != old:
            raise ValueError('身份锁未精确逆回')
    for name, raw in changes.items():
        compile(raw, name, 'exec')
    if output.exists() or base == output or base in output.parents or output in base.parents:
        raise ValueError('只允许全新、非基点子/父目录')
    if args.emit_only:
        output.mkdir(parents=True)
    else:
        shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    for name, raw in changes.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    target = {**expected, **{name: sha(raw) for name, raw in changes.items()}}
    if len(target) != 423 or mapping(output) != ({name: sha(raw) for name, raw in changes.items()} if args.emit_only else target):
        raise ValueError('输出map/四路径差异不符')
    if mapping(base) != expected:
        raise ValueError('基点源发生变化')
    receipt = dict(base_map_sha256=BASE_MAP_SHA, source_count=423, emit_only=args.emit_only,
        runner_sha256=runner_sha, changed_paths={name: dict(before=expected.get(name), after=target[name]) for name in changes},
        runner_edits=[dict(before=a.decode(), after=b.decode()) for a, b in edits], output_map=target,
        validation='完整map/语法/精确逆回；未执行runtime、数值或GPU')
    with output.with_name(output.name + '-prepare.json').open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
