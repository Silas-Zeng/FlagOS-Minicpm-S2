"""固定422→一次原序/P shadow诊断424；只本地生成隔离source。"""
import argparse
import difflib
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parent / 'compute-order'
BASE_MAP = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
PREPARER = 'b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670'
P_HELPER = '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce'
P_RUNNER = 'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'
RUNNER = 'vllm_fl/worker/model_runner.py'
HELPER = 'vllm_fl/patches/biv150_compute_order.py'
SHADOW = 'vllm_fl/patches/biv150_compute_order_shadow.py'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def transform(raw):
    if sha(raw) != P_RUNNER:
        raise ValueError('只接受冻结ea64 P runner')
    text = raw.decode('utf-8')
    edits = []
    def edit(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('shadow切口不唯一：' + old[:80])
        text = text.replace(old, new)
        edits.append((old, new))
    edit('from vllm_fl.patches.biv150_compute_order import make_plan as _biv150_compute_order_plan\n',
         'from vllm_fl.patches.biv150_compute_order import make_plan as _biv150_compute_order_plan\n'
         'from vllm_fl.patches.biv150_compute_order_shadow import create as _biv150_shadow_create\n')
    start = text.index('            logits_indices, spec_decode_metadata = self._prepare_inputs(\n',
                       text.index('            compute_order = _biv150_compute_order_plan('))
    stop = text.index('\n\n            cascade_attn_prefix_lens', start)
    prepare = text[start:stop]
    slots_start = text.index('            slot_mappings_by_group, slot_mappings = self._get_slot_mappings(\n', start)
    metadata_start = text.index('            attn_metadata, spec_decode_common_attn_metadata = (\n', slots_start)
    preprocess_start = text.index('            (\n                input_ids,\n', metadata_start)
    block_end = text.index('\n\n        # Set cudagraph mode to none', preprocess_start)
    slots = text[slots_start:metadata_start].rstrip()
    metadata = text[metadata_start:preprocess_start].rstrip()
    preprocess = text[preprocess_start:block_end]
    edit(prepare, '            shadow = _biv150_shadow_create(self, compute_order, scheduler_output, num_scheduled_tokens_np)\n'
         '            preparation_order = None if shadow is not None else compute_order\n'
         + prepare.replace('compute_order=compute_order', 'compute_order=preparation_order'))
    edit(metadata, metadata.replace('compute_order=compute_order', 'compute_order=preparation_order'))
    shadow_call = '''            if shadow is not None:
                shadow.shadow(input_ids=input_ids, positions=positions, inputs_embeds=inputs_embeds,
                    intermediate_tensors=intermediate_tensors, model_kwargs=model_kwargs,
                    attn_metadata=attn_metadata, slot_mappings=slot_mappings, batch_desc=batch_desc,
                    mode=cudagraph_mode, num_tokens=num_tokens_padded,
                    num_tokens_across_dp=num_tokens_across_dp, ubatch_slices=ubatch_slices_padded)
'''
    # 第二次只重建原本就会被本步覆盖的输入/metadata，dispatcher、_update_states、采样不重复。
    rebuild = '\n\n'.join((prepare, slots, metadata, preprocess))
    indented = '\n'.join('    ' + line if line else '' for line in rebuild.split('\n'))
    edit(preprocess, preprocess + '\n\n' + shadow_call + indented + '\n'
         '                shadow.check_slots(slot_mappings, permuted=True)')
    forward_start = text.index('        with (\n            set_forward_context(\n',
        text.index('        # Run the model.'))
    forward_end = text.index('\n\n        if compute_order is not None:\n            compute_order.forward_returned()', forward_start)
    forward = text[forward_start:forward_end]
    edit(forward, '        try:\n'
         '            if shadow is not None:\n                shadow.layer_probe.install()\n'
         + '\n'.join('    ' + line if line else '' for line in forward.split('\n'))
         + '\n        finally:\n            if shadow is not None:\n                shadow.layer_probe.restore()')
    edit('        self.execute_model_state = ExecuteModelState(\n',
         '        if shadow is not None:\n            shadow.finish(logits)\n\n'
         '        self.execute_model_state = ExecuteModelState(\n')
    reverse = text
    for old, new in reversed(edits):
        if reverse.count(new) != 1:
            raise ValueError('shadow逆回切口不唯一')
        reverse = reverse.replace(new, old)
    if reverse.encode() != raw:
        raise ValueError('shadow未精确逆回ea64')
    result = text.encode()
    compile(result, RUNNER, 'exec')
    return result, edits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--emit-only', action='store_true')
    args = parser.parse_args()
    base, output = args.base.resolve(strict=True), args.output.resolve()
    original_script = (ORIGINAL / 'prepare_compute_order.py').read_bytes()
    if sha(original_script) != PREPARER:
        raise ValueError('原P preparer身份漂移')
    spec = importlib.util.spec_from_file_location('frozen_compute_order_preparer', ORIGINAL / 'prepare_compute_order.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    map_raw = (ORIGINAL / 'base-source-sha256.json').read_bytes()
    expected = json.loads(map_raw)
    if sha(map_raw) != BASE_MAP or module.mapping(base) != expected:
        raise ValueError('原422完整map不符')
    p_runner, _ = module.transform_runner((base / RUNNER).read_bytes())
    runner, edits = transform(p_runner)
    runner_sha = sha(runner)
    helper = (ORIGINAL / 'biv150_compute_order.py').read_bytes()
    if sha(helper) != P_HELPER or helper.count(P_RUNNER.encode()) != 1:
        raise ValueError('冻结P helper不符')
    helper = helper.replace(P_RUNNER.encode(), runner_sha.encode())
    shadow = (HERE / 'biv150_compute_order_shadow.py').read_bytes()
    changes = {RUNNER: runner, HELPER: helper, SHADOW: shadow}
    for name, pin in module.PINS.items():
        if name == RUNNER:
            continue
        original = (base / name).read_bytes()
        if sha(original) != pin or original.count(module.RUNNER.encode()) != 1:
            raise ValueError('原worker/protocol锁不符')
        changes[name] = original.replace(module.RUNNER.encode(), runner_sha.encode())
        if changes[name].replace(runner_sha.encode(), module.RUNNER.encode()) != original:
            raise ValueError('runner身份未精确逆回')
    for name, raw in changes.items():
        compile(raw, name, 'exec')
    if output.exists() or base == output or base in output.parents or output in base.parents:
        raise ValueError('只允许全新非基点子/父目录')
    if args.emit_only:
        output.mkdir(parents=True)
    else:
        shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    for name, raw in changes.items():
        path = output / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    target = {**expected, **{name: sha(raw) for name, raw in changes.items()}}
    if len(target) != 424 or module.mapping(base) != expected or module.mapping(output) != (
            {name: sha(raw) for name, raw in changes.items()} if args.emit_only else target):
        raise ValueError('完整输入/输出map不符')
    receipt = dict(source_count=424, emit_only=args.emit_only, base_map_sha256=BASE_MAP,
        runner_sha256=runner_sha, shadow_helper_sha256=sha(shadow), output_map=target,
        changed_paths={name: dict(before=expected.get(name), after=target[name]) for name in changes},
        exact_inverse_to_P_runner=True, duplicate_dispatcher=False, duplicate_update_states=False,
        duplicate_sampling=False, validation='语法/完整map/精确逆回；未导入框架或运行设备',
        shadow_edits=[dict(before=a, after=b) for a, b in edits])
    output.with_name(output.name + '-prepare.json').write_text(
        json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'runner.diff').write_text(''.join(difflib.unified_diff(
        p_runner.decode().splitlines(True), runner.decode().splitlines(True), fromfile='frozen-P-ea64',
        tofile='one-shot-shadow')), encoding='utf-8')
    print(json.dumps(dict(source_count=424, runner_sha256=runner_sha,
        shadow_helper_sha256=sha(shadow), changed_paths=list(changes))))


if __name__ == '__main__':
    main()
