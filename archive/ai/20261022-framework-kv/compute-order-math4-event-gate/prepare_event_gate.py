"""冻结060425计算序423→事件驱动四题诊断425；不包含结构shadow或额外模型前向。"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
MAP = HERE.parent / 'compute-order-owner/accuracy-source-sha256.json'
MAP_SHA = '6cf2e1d7e3084d95e0fd8db23ceaa426c5c5ab6ff887dffcd8f036e60b98a7b9'
OLD = 'ea64a59cff6197c42babbc190246ab24dce4f540874b2025c0f4ebfee02195ac'
RUNNER = 'vllm_fl/worker/model_runner.py'
HELPER = 'vllm_fl/patches/biv150_compute_order_math4.py'
EVENTS = 'vllm_fl/patches/biv150_math4_events.py'
LOCKS = ('vllm_fl/patches/biv150_compute_order.py',
         'vllm_fl/patches/biv150_kv_worker.py', 'vllm_fl/patches/biv150_kv_protocol.py')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping(folder):
    values = {}
    for p in sorted(folder.rglob('*')):
        if any(s in ('.git', '__pycache__') for s in p.relative_to(folder).parts) or p.suffix in ('.pyc', '.pyo'):
            continue
        if p.is_symlink():
            raise ValueError('诊断源不接受链接')
        if p.is_file():
            values[p.relative_to(folder).as_posix()] = sha(p.read_bytes())
    return values


def transform(raw):
    if sha(raw) != OLD:
        raise ValueError('只接受冻结060425 ea64 runner')
    text, edits = raw.decode(), []
    def edit(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('math4切口不唯一')
        text = text.replace(old, new, 1)
        edits.append((old, new))
    edit('from vllm_fl.patches.biv150_compute_order import make_plan as _biv150_compute_order_plan\n',
         'from vllm_fl.patches.biv150_compute_order import make_plan as _biv150_compute_order_plan\n'
         'from vllm_fl.patches.biv150_compute_order_math4 import after_forward as _math4_forward, before_sample as _math4_before, after_sample as _math4_after\n')
    edit('        self.execute_model_state = ExecuteModelState(\n',
         '        _math4_forward(self, compute_order, scheduler_output, num_scheduled_tokens_np, logits)\n\n'
         '        self.execute_model_state = ExecuteModelState(\n')
    edit('            sampler_output = self._sample(logits, spec_decode_metadata)\n',
         '            math4_ticket = _math4_before(self, scheduler_output, logits, spec_decode_metadata)\n'
         '            sampler_output = self._sample(logits, spec_decode_metadata)\n'
         '            _math4_after(math4_ticket, self, scheduler_output, sampler_output)\n')
    edit('from vllm_fl.patches.biv150_compute_order_math4 import after_forward as _math4_forward, before_sample as _math4_before, after_sample as _math4_after\n',
         'from vllm_fl.patches.biv150_compute_order_math4 import after_forward as _math4_forward, before_sample as _math4_before, after_sample as _math4_after\n'
         'from vllm_fl.patches.biv150_math4_events import observe_batch as _math4_event_batch\n')
    edit('            logits_indices, spec_decode_metadata = self._prepare_inputs(\n',
         '            _math4_event_batch(self, scheduler_output, num_scheduled_tokens_np, compute_order)\n'
         '            logits_indices, spec_decode_metadata = self._prepare_inputs(\n')
    inverse = text
    for old, new in reversed(edits):
        if inverse.count(new) != 1:
            raise ValueError('math4逆回切口不唯一')
        inverse = inverse.replace(new, old, 1)
    if inverse.encode() != raw:
        raise ValueError('未精确逆回冻结P')
    compile(text, RUNNER, 'exec')
    return text.encode(), edits


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--emit-only', action='store_true')
    args = p.parse_args()
    base, out = args.base.resolve(strict=True), args.output.resolve()
    map_raw = MAP.read_bytes()
    expected = json.loads(map_raw)
    if sha(map_raw) != MAP_SHA or len(expected) != 423 or mapping(base) != expected:
        raise ValueError('非完整冻结060425计算序423')
    original = (base / RUNNER).read_bytes()
    runner, edits = transform(original)
    new = sha(runner)
    math_helper = (HERE / 'biv150_compute_order_math4.py').read_bytes()
    if sha(math_helper) != '29b95266476c0c26e3ee755ccc3eab95cdf700c4e0a2ce446c74fd784fc00a3a':
        raise ValueError('原outside/sample证明须逐字保留')
    changes = {RUNNER: runner, HELPER: math_helper, EVENTS: (HERE / 'biv150_math4_events.py').read_bytes()}
    for name in LOCKS:
        value = (base / name).read_bytes()
        if value.count(OLD.encode()) != 1:
            raise ValueError('原显式runner锁不唯一')
        changed = value.replace(OLD.encode(), new.encode())
        if changed.replace(new.encode(), OLD.encode()) != value:
            raise ValueError('锁未精确逆回')
        changes[name] = changed
    for name, value in changes.items():
        compile(value, name, 'exec')
    if out.exists() or out == base or base in out.parents or out in base.parents:
        raise ValueError('须全新独立输出目录')
    if args.emit_only:
        out.mkdir(parents=True)
    else:
        shutil.copytree(base, out, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    for name, value in changes.items():
        target = out / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value)
    target_map = {**expected, **{k: sha(v) for k, v in changes.items()}}
    if len(target_map) != 425 or mapping(base) != expected or mapping(out) != (
            {k: sha(v) for k, v in changes.items()} if args.emit_only else target_map):
        raise ValueError('输入输出完整map异常')
    receipt = dict(source_count=425, base_map_sha256=MAP_SHA, runner_sha256=new,
        helper_sha256=sha(changes[HELPER]), event_helper_sha256=sha(changes[EVENTS]), output_map=target_map, emit_only=args.emit_only,
        changed_paths={k: dict(before=expected.get(k), after=target_map[k]) for k in changes},
        inverse_exact_to_frozen_P=True, original_sample_body_unchanged=True,
        additional_model_forward=False, checks='compile/map/逆回；未导入模型或运行设备')
    out.with_name(out.name + '-prepare.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (HERE / 'runner.diff').write_text(''.join(difflib.unified_diff(original.decode().splitlines(True),
        runner.decode().splitlines(True), fromfile='frozen060425-P-ea64', tofile='math4')), encoding='utf-8')
    print(json.dumps({k: receipt[k] for k in ('source_count', 'runner_sha256', 'helper_sha256', 'event_helper_sha256')}))


if __name__ == '__main__':
    main()
