"""固定QGQA414仅把无消费者的computed H2D延后到metadataFalse；默认不运行。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

MAP_SHA = 'bf69d06dfe8b580e3628b7ddac3c0fe68a715d709c5def2b83ea5f745ea8d392'
RUNNER = 'vllm_fl/worker/model_runner.py'
INPUT_SHA = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
OUTPUT_SHA = '97f41ac455cad0db7c8ddfd2b9809e77326b6472285cb14e56ce486f2f0f7443'
CONDITION = b'        if (\n            self.use_async_spec_decode\n            and self.valid_sampled_token_count_gpu is not None\n            and prev_req_id_to_index\n        ):\n'
COPY = b'            self.num_computed_tokens[:num_reqs].copy_(\n                self.input_batch.num_computed_tokens_cpu_tensor[:num_reqs],\n                non_blocking=True,\n            )\n'
METADATA = b'        if not _biv150_try_cpu_metadata(self, positions_np, req_indices, num_scheduled_tokens):\n'
PENDING = b'        _biv150_computed_h2d_pending = False\n'
DEFERRED = b'        else:\n            _biv150_computed_h2d_pending = True\n'
COPY_ON_FALSE = METADATA + b'            if _biv150_computed_h2d_pending:\n' + b''.join(b'    '+line for line in COPY.splitlines(keepends=True))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def once(raw, old, new):
    if raw.count(old) != 1:
        raise ValueError('exact source anchor changed')
    return raw.replace(old, new, 1)


def transform_source(raw):
    if sha(raw) != INPUT_SHA:
        raise ValueError('only tested cc442 QGQA414 runner')
    changed = once(raw, CONDITION, PENDING + CONDITION)
    changed = once(changed, b'        else:\n' + COPY, DEFERRED)
    changed = once(changed, METADATA, COPY_ON_FALSE)
    restored = once(changed, COPY_ON_FALSE, METADATA)
    restored = once(restored, DEFERRED, b'        else:\n' + COPY)
    restored = once(restored, PENDING + CONDITION, CONDITION)
    if restored != raw or sha(changed) != OUTPUT_SHA:
        raise ValueError('inverse or final runner identity mismatch')
    compile(changed, RUNNER, 'exec')
    return changed


def mapping(folder):
    result = {}
    for path in sorted(folder.rglob('*')):
        rel = path.relative_to(folder)
        if any(p in ('.git', '__pycache__') for p in rel.parts) or path.suffix in ('.pyc', '.pyo'):
            continue
        if path.is_symlink():
            target = path.resolve(strict=True)
            if not target.is_file() or not target.is_relative_to(folder):
                raise ValueError('拒绝外部/目录链接')
        if path.is_file():
            result[rel.as_posix()] = sha(path.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-dir', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    base, output = args.base_dir.resolve(strict=True), args.output_dir.resolve()
    receipt = output.with_name(output.name + '-preparation.json')
    if output.exists() or receipt.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError('输出须全新且不与基点交叠')
    raw_map = (Path(__file__).parent/'base-source-sha256.json').read_bytes()
    if sha(raw_map) != MAP_SHA:
        raise ValueError('非184141完整414 map')
    expected_base = json.loads(raw_map)
    before = mapping(base)
    if before != expected_base or len(before) != 414 or before[RUNNER] != INPUT_SHA:
        raise ValueError('完整冻结QGQA414变化')
    changed = transform_source((base/RUNNER).read_bytes())
    expected = dict(before)
    expected[RUNNER] = OUTPUT_SHA
    shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    (output/RUNNER).write_bytes(changed)
    if mapping(base) != before or mapping(output) != expected:
        raise ValueError('出现未声明源变更')
    info = {'kind':'只在metadata成功时省computed H2D；未改变原参数/算子/固定buffer/event',
        'argv':sys.argv, 'base':str(base), 'source':str(output), 'base_source_sha256':before,
        'source_sha256':expected, 'base_map_sha256':MAP_SHA, 'changed_paths':[RUNNER],
        'preparer_sha256':sha(Path(__file__).read_bytes()), 'source_count':414,
        'inverse_exact':True, 'metadata_helper_unchanged':True, 'new_runtime_helper':False}
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'source':str(output), 'receipt':str(receipt), 'source_count':414}))


if __name__ == '__main__':
    main()
