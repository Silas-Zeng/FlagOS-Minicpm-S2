"""accepted-fill 422→422短服务；只适配既有e3ae公共门，不重跑封存或方法测试。"""
import argparse
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[2]
if os.name == 'nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT = Path('\\\\?\\' + str(ROOT))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
read = lambda path: json.loads(path.read_text(encoding='utf-8'))
REUSED_SHA = 'e3ae768c5fe251c3a634472fd86871e536ec3cd835aae6047e18be09dedb7961'
MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
BUILDER_SHA = '410b2c6e07018e745406cec62213fe982945edc6a29c599e3d3696bf6ff4c043'
PREPARED_SHA = 'a1404883cdb1c63a73110b31e51da6f2062801b4d96bf5e3fc36ed6b77cce002'
LAUNCH_SHA = {
    'baseline': '7049cfd0bd207b1daad3e943da9281b133729cedced99ac9b754562580a8c000',
    'candidate': 'e972c800915a319acbd29823e13abb590e56ced8f584bbf4fa2ddfe15c3a7960',
}
RUNS = {
    'baseline': '20261023T064838Z-accepted-fill-baseline-context16k',
    'candidate': '20261023T065325Z-accepted-fill-candidate-context16k',
}
PINS = {
    'vllm_fl/worker/model_runner.py': '03a0e007e820644d55ac5eaf3331416da3fb0e58147a4f57928d363cc8ff6fb2',
    'vllm_fl/patches/biv150_kv_worker.py': '68def179673964bb5d4011ce3f57ace9ce7c776a89e4dff63fb914aa19095da6',
    'vllm_fl/patches/biv150_kv_protocol.py': 'eab62b8444727f0968be4154c1b212b77917a95c355c4d9832058e9d5cca80c9',
}


def exact_launch(control, run, manifest, label):
    remote = '/workspace/experiments/minicpm-s2'
    match = re.fullmatch(r'(\d{8}T\d{6}Z)-accepted-fill-' + label + '-context16k', run.name)
    if not match or run.name != RUNS[label]:
        return {'matches': False, 'reason': '非声明的本次UTC/run ID'}
    source = (remote + '/code/q-gqa-kv-swap-20261022T213134Z' if label == 'baseline'
        else remote + '/code/accepted-fill-' + match.group(1))
    expected = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION', 'BIV150_KV_VERIFY_RESTORE=0',
        f'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR={remote}/framework/{run.name}-control/q-hoist-artifacts',
        'python3', remote + '/scripts/run_framework_screen.py', remote + '/framework/' + run.name,
        '--source-dir', source, '--context-screen', '--seed', '721201',
        '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']
    actual = shlex.split((control / 'command.txt').read_text(encoding='utf-8'))
    return {'argv': actual, 'expected_argv': expected,
        'matches': actual == expected and manifest['source_dir'] == source}


def library():
    path = ROOT / 'tmp/compute-order-owner/compare_service_pair.py'
    assert sha(path) == REUSED_SHA, '已审e3ae公共门身份变化'
    spec = importlib.util.spec_from_file_location('readonly_accepted_fill_common', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT, module.exact_launch = ROOT, exact_launch
    return module.library()


def compare(baseline, candidate):
    assert (baseline, candidate) == (RUNS['baseline'], RUNS['candidate'])
    lib = library()
    arms = {label: lib['load_arm'](label, name, 'context16k') for label, name in RUNS.items()}
    map_path, frozen_path = (ROOT / 'tmp/accepted-fill' / name
        for name in ('base-source-sha256.json', 'files-prepare.json'))
    assert sha(map_path) == MAP_SHA and sha(frozen_path) == PREPARED_SHA
    expected_b, frozen = read(map_path), read(frozen_path)
    expected_a = frozen['output_map']
    assert len(expected_b) == len(expected_a) == frozen['source_count'] == 422
    assert set(frozen['changed_paths']) == set(PINS)
    assert {key: expected_a[key] for key in PINS} == PINS
    data = {key: arm['data'] for key, arm in arms.items()}
    db = [value['db'][side] for value in data.values() for side in ('db-before', 'db-after')]
    load = [['bash', '/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh',
        '<RUN>/context-16k', 'context-16k', '16384', '128', '64', '32', '721201']]
    checks = lib['common_checks'](arms, expected_b, db, load)
    checks['baseline_exact_422'] = checks.pop('baseline_exact_current_QGQA_414')
    extras = {}
    for label, arm in arms.items():
        run = ROOT / 'experiments/framework' / data[label]['run_id']
        control = run.with_name(run.name + '-control')
        lines = (run / 'server.log').read_text(encoding='utf-8', errors='replace').splitlines()
        pid = (data[label]['q_actual_markers'] or [{}])[0].get('pid')
        markers = {}
        for name, marker, payload in (
            ('enabled', 'BIV150_ACCEPTED_GPU_FILL_SKIP_ENABLED ', 'scope=non_spec_full cpu_fill_retained=1'),
            ('metadata', 'BIV150_CPU_METADATA_FIRST_SELECTED ', 'positions_seq_h2d=2'),
        ):
            markers[name] = [{'line': index + 1, 'pid': lib['engine_pid'](line.split(marker, 1)[0]),
                'payload': line.split(marker, 1)[1].strip()} for index, line in enumerate(lines) if marker in line]
            markers[name + '_same_engine_exact'] = all(value['pid'] == pid and value['payload'] == payload
                for value in markers[name])
        gpu = list(csv.DictReader((run / 'gpu.csv').open(encoding='utf-8')))
        post = read(run / 'postflight-full.json')
        extras[label] = {**markers, 'q_actual_pid': pid,
            'frozen_launcher': sha(control / ('launch_' + label + '.py')) == LAUNCH_SHA[label],
            'single_BIV150_32GiB': bool(gpu) and all(row['memory.total'].strip() == '32768 MiB'
                and 'BI-V150' in row['gpu_name'] for row in gpu),
            'owned_inactive': all(value is None or '\nState:\tZ ' in value
                for value in post['owned_process_status'].values())}
    control = ROOT / 'experiments/framework' / (candidate + '-control')
    preparation = read(control / 'prepare.json')
    prepared_ok = (sha(control / 'prepare_accepted_fill.py') == BUILDER_SHA
        and preparation['source_count'] == 422 and preparation['emit_only'] is False
        and preparation['base_map_sha256'] == MAP_SHA and preparation['output_map'] == expected_a
        and preparation['changed_paths'] == frozen['changed_paths']
        and preparation['runner_edits'] == frozen['runner_edits']
        and preparation['new_gpu_storage_bytes'] == 0 and preparation['runtime_helper_added'] is False)
    changed = sorted(key for key in arms['baseline']['source'].keys() | arms['candidate']['source'].keys()
        if arms['baseline']['source'].get(key) != arms['candidate']['source'].get(key))
    cold, metadata = extras['candidate']['enabled'], extras['candidate']['metadata']
    checks.update(candidate_exact_422=arms['candidate']['source'] == expected_a,
        only_declared_three_accepted_fill_paths=changed == sorted(PINS),
        candidate_frozen_complete_preparation=prepared_ok,
        both_original_launch=all(value['launch']['matches'] for value in data.values()),
        both_frozen_launchers=all(value['frozen_launcher'] for value in extras.values()),
        both_single_BIV150_32GiB=all(value['single_BIV150_32GiB'] for value in extras.values()),
        both_owned_inactive=all(value['owned_inactive'] for value in extras.values()),
        both_original_six_CPU=all(int(value['manifest']['cpu_before']['cpu.cfs_quota_us'])
            / int(value['manifest']['cpu_before']['cpu.cfs_period_us']) == 6 for value in arms.values()),
        both_actual_prepare_same_Engine=all(len(value['metadata']) == 1 and value['metadata_same_engine_exact']
            for value in extras.values()),
        candidate_cold_enabled_before_actual_prepare_same_Engine=len(cold) == len(metadata) == 1
            and extras['candidate']['enabled_same_engine_exact'] and cold[0]['line'] < metadata[0]['line']
            and not extras['baseline']['enabled'],
        neither_finite=all(not value['finite_markers'] for value in data.values()))
    ar, br = data['candidate']['benchmark'], data['baseline']['benchmark']
    percent = {'total_token_throughput_change': 100 * (ar['total_token_throughput'] / br['total_token_throughput'] - 1),
        'duration_saved': 100 * (1 - ar['duration'] / br['duration']),
        'mean_ttft_change': 100 * (ar['mean_ttft_ms'] / br['mean_ttft_ms'] - 1),
        'mean_tpot_change': 100 * (ar['mean_tpot_ms'] / br['mean_tpot_ms'] - 1)}
    ok = all(checks.values())
    return {'kind': 'accepted GPU fill 422→422原context16k128单pair', 'runs': data,
        'checks': checks, 'pair_comparable': ok,
        'status': 'single_pair_only' if ok else 'confounded_no_performance_conclusion',
        'gain': percent if ok else None, 'descriptive_percent': percent, 'actual_markers': extras,
        'declared_source_changes': changed, 'reader_sha256': sha(Path(__file__)),
        'reused_reader_sha256': REUSED_SHA, 'frozen_preparation_sha256': PREPARED_SHA,
        'limits': ['单pair不证明稳定收益；可比项失败gain=null，不放宽KV条件或重启凑容量。',
            '同Engine冷ENABLED后原CPU_METADATA_FIRST_SELECTED只证明首次实际prepare经过该处，不证明全程覆盖、GPU完成或数值相同。',
            '候选不继承原422准确率；本次32请求短服务不是新完整准确率。',
            '原seal逐文件核复用root导入；公共DB四端/KV/参数/环境/清理门复用已审e3ae，不重跑方法测试。',
            '共享cgroup和exporter计数仅描述资源，不视为本策略的因果CPU成本。']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-run', required=True)
    parser.add_argument('--candidate-run', required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('不覆盖旧配对结果')
    result = compare(args.baseline_run, args.candidate_run)
    with args.output.open('x', encoding='utf-8') as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
        output.write('\n')
    print(json.dumps({key: result[key] for key in ('status', 'checks', 'gain')}, ensure_ascii=False))
    raise SystemExit(0 if result['pair_comparable'] else 1)
