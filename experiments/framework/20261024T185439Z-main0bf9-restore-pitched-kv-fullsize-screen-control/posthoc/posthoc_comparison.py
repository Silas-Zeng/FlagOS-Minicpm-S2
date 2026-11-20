"""只读成功原件，复用冻结比较器；仅另存事后比较，不改原 state/日志。"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

sys.dont_write_bytecode = True
COMPARATOR_SHA256 = '9ca30c3249ff1cb7addda5b124ca11ff34268193f2c88e46777d9d7ffe227867'
BASELINE = '/workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comparison-assets', required=True, type=Path)
    parser.add_argument('--candidate-control', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assets = args.comparison_assets.resolve(strict=True)
    control = args.candidate_control.resolve(strict=True)
    output = args.output.resolve()
    if output.name != 'posthoc-comparison.json' or output.exists():
        raise ValueError('输出必须是尚不存在的 posthoc-comparison.json')
    output.parent.resolve(strict=True)
    if any(output.is_relative_to(p) for p in (assets, control, control.with_name(control.name.removesuffix('-control')))):
        raise ValueError('事后输出须位于新的资产目录，不能写入冻结资产或原 run/control')

    comparator_path = assets / 'comparison.py'
    comparator_bytes = comparator_path.read_bytes()
    if hashlib.sha256(comparator_bytes).hexdigest() != COMPARATOR_SHA256:
        raise ValueError('冻结比较器身份不符')
    state_path = control / 'state.json'
    state_bytes = state_path.read_bytes()
    state = json.loads(state_bytes)
    spec = importlib.util.spec_from_file_location('frozen_535_comparison', comparator_path)
    comparator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(comparator)
    reference = comparator.qualify_reference(BASELINE)
    original_target = (control / 'comparison.json').resolve()
    original_comparison = original_target.read_bytes() if original_target.exists() else None
    provenance = dict(
        posthoc=True,
        created_utc=datetime.now(timezone.utc).isoformat(),
        comparator_sha256=COMPARATOR_SHA256,
        input_state=str(state_path),
        input_state_sha256=hashlib.sha256(state_bytes).hexdigest(),
        original_comparison_target=str(original_target),
        note='外层 owner 的内存 state 与 JSON 原件结构比较失败；读取已成功收尾的 state.json 重算。原 owner 异常日志、原 state 和冻结比较器均保留，不重跑性能，不追改原轮完成状态。',
    )
    writes = []

    def redirect_write(path, data, encoding=None, errors=None, newline=None):
        if path.resolve() != original_target or writes:
            raise RuntimeError('比较器发生预期以外或重复写入')
        result = json.loads(data)
        if 'posthoc' in result:
            raise ValueError('原比较器出现意外 posthoc 字段')
        result['posthoc'] = provenance
        serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
        with output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(serialized)
        writes.append(str(output))
        return len(data)

    with patch.object(Path, 'write_text', redirect_write):
        result = comparator.compare(reference, state)
    if len(writes) != 1 or state_path.read_bytes() != state_bytes or comparator_path.read_bytes() != comparator_bytes:
        raise RuntimeError('输出数量或冻结原件发生意外变化')
    current_original = original_target.read_bytes() if original_target.exists() else None
    if current_original != original_comparison:
        raise RuntimeError('原 comparison.json 被意外改变')
    print(json.dumps(dict(
        posthoc=True, output=str(output),
        sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
        mismatches=result['mismatches'],
        actual_kv=result['actual_kv'],
        gain_calculated=result['gain_calculated'],
        stable_gain_confirmed=result['stable_gain_confirmed'],
        raw_state_and_comparator_unchanged=True,
    ), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
