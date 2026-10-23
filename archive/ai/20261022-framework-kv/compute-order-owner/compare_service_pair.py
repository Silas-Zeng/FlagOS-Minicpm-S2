"""计算序423原context-screen单pair；复用公共门，不重跑seal/方法测试。"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[2]
if os.name == 'nt' and not str(ROOT).startswith('\\\\?\\'):
    ROOT = Path('\\\\?\\' + str(ROOT))
HERE = ROOT / 'tmp/compute-order-owner'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
PREPARER_SHA = 'b1a804a0c6da15b7c295a4eb5b62d0a6d853fc15d104b6ddcffd36c8a7211670'
HELPER_SHA = '5ce6f7b6a815ab54d9d9965c30f37362fd1d271c82d442caa76829e01f4938ce'
PREPARED_SHA = '87af19c9f4de68557189f3d3c9a0d788475b8f6d8f66c251c3fb7495dbc33a13'
LAUNCH_SHA = {
    'baseline': '90554d08b1a274458e355ad7c7da739740c52da0a5045aee48eea16757447abe',
    'candidate': '995d27bc3295bd54d90a213aeb94b0cda072c0f9b3d5f718adf8f8301056699c',
}
RUNS = {
    'baseline': '20261023T054306Z-compute-order-baseline-context16k',
    'candidate': '20261023T060425Z-compute-order-candidate-context16k',
}


def exact_launch(control, run, manifest, label):
    remote = '/workspace/experiments/minicpm-s2'
    match = re.fullmatch(r'(\d{8}T\d{6}Z)-compute-order-' + label + '-context16k', run.name)
    if not match or run.name != RUNS[label]:
        return {'matches': False, 'reason': '非本次声明的UTC/run ID'}
    source = (remote + '/code/q-gqa-kv-swap-20261022T213134Z' if label == 'baseline'
        else remote + '/code/compute-order-' + match.group(1))
    expected = ['env', '-u', 'BIV150_FINITE_GROWTH_ADMISSION', 'BIV150_KV_VERIFY_RESTORE=0',
        f'BIV150_Q_FRAGMENT_SERVICE_ARTIFACT_DIR={remote}/framework/{run.name}-control/q-hoist-artifacts',
        'python3', remote + '/scripts/run_framework_screen.py', remote + '/framework/' + run.name,
        '--source-dir', source, '--context-screen', '--seed', '721201',
        '--require-log-marker', 'BIV150_KV_PROTOCOL_INSTALLED']
    actual = shlex.split((control / 'command.txt').read_text(encoding='utf-8'))
    return {'argv': actual, 'expected_argv': expected,
        'matches': actual == expected and manifest['source_dir'] == source}


def library():
    # 复用8c0→03e的原20公共门；仅适配实际context-screen目录及屏幕资格。
    shared = ROOT / 'tmp/skip-computed-h2d-service/compare_service_pair.py'
    assert sha(shared) == '8c0fc7925947dd2b46db24abff1f3fe94dffeff66dd5dfa42989d223a8130efa'
    text, sep, _ = shared.read_text(encoding='utf-8').partition('\ndef compare(')
    assert sep
    old = "text=LEGACY.read_text(encoding='utf-8');prefix,sep,_=text.partition('\\ndef compare(')"
    new = """text=LEGACY.read_text(encoding='utf-8')
    for before,after in (
        ("case='context-16k-long' if screen=='context16k-long' else 'decode-4k'", "case='context-16k'"),
        ("and not x['manifest']['context_screen']", "and x['manifest']['context_screen']==(screen=='context16k')"),
    ):
        require(text.count(before)==1,'原context-screen适配锚变化')
        text=text.replace(before,after)
    prefix,sep,_=text.partition('\\ndef compare(')"""
    assert text.count(old) == 1
    text = text.replace(old, new)
    old = 'n,isl,osl,screen=64,4096,128,"decode4k"'
    assert text.count(old) == 1
    text = text.replace(old, 'n,isl,osl,screen=32,16384,128,"context16k"')
    namespace = {'__file__': str(shared), '__name__': 'readonly_compute_order_pair_library'}
    exec(compile(text, str(shared) + ':context_screen_library', 'exec'), namespace)
    namespace['ROOT'], namespace['exact_launch'] = ROOT, exact_launch
    return namespace['library']()


def compare(baseline, candidate):
    assert baseline == RUNS['baseline'] and candidate == RUNS['candidate']
    lib = library()
    arms = {label: lib['load_arm'](label, name, 'context16k')
        for label, name in (('baseline', baseline), ('candidate', candidate))}
    baseline_map = ROOT / 'tmp/compute-order/base-source-sha256.json'
    frozen_file = ROOT / 'tmp/compute-order/files-prepare.json'
    assert sha(baseline_map) == MAP_SHA and sha(frozen_file) == PREPARED_SHA
    expected_b, frozen = read(baseline_map), read(frozen_file)
    expected_a = frozen['output_map']
    assert frozen['source_count'] == len(expected_a) == 423 and len(expected_b) == 422
    data = {key: arm['data'] for key, arm in arms.items()}
    db = [value['db'][side] for value in data.values() for side in ('db-before', 'db-after')]
    load = [['bash', '/workspace/experiments/minicpm-s2/scripts/run_diagnostic_load.sh',
        '<RUN>/context-16k', 'context-16k', '16384', '128', '64', '32', '721201']]
    checks = lib['common_checks'](arms, expected_b, db, load)
    checks['baseline_exact_422'] = checks.pop('baseline_exact_current_QGQA_414')
    logs, extras = {}, {}
    for label, arm in arms.items():
        run = ROOT / 'experiments/framework' / data[label]['run_id']
        control = run.with_name(run.name + '-control')
        logs[label] = (run / 'server.log').read_text(encoding='utf-8', errors='replace')
        gpu = list(csv.DictReader((run / 'gpu.csv').open(encoding='utf-8')))
        post = read(run / 'postflight-full.json')
        extras[label] = {
            'frozen_launcher': sha(control / ('launch_' + label + '.py')) == LAUNCH_SHA[label],
            'single_BIV150_32GiB': bool(gpu) and all(row['memory.total'].strip() == '32768 MiB'
                and 'BI-V150' in row['gpu_name'] for row in gpu),
            'owned_gone': all(value is None or '\nState:\tZ ' in value
                for value in post['owned_process_status'].values()),
        }
    marker = 'BIV150_COMPUTE_ORDER_FIRST_SELECTED '
    actual = lib['markers'](logs['candidate'], marker)
    pid = (data['candidate']['q_actual_markers'] or [{}])[0].get('pid')
    observed = []
    for value in actual:
        if (value.get('same_engine_log_pid') and value.get('pid') == pid
                and all(type(value.get(key)) is int for key in ('N', 'M', 'Dall', 'Dprefix', 'outside', 'sampler_rows'))
                and 0 < value['Dprefix'] < value['Dall'] < value['N'] < value['M']
                and value['outside'] == value['Dall'] - value['Dprefix']
                and value['sampler_rows'] == value['N']
                and value.get('original_model_forward_returned') is True
                and value.get('runtime_mode') == 'NONE'
                and value.get('inverse_logits_order') == 'original_request_rows'
                and value.get('token_bitwise_equivalence_claimed') is False):
            observed.append(value)
    control = ROOT / 'experiments/framework' / (candidate + '-control')
    preparation = read(control / 'prepare.json')
    prepared_ok = (sha(control / 'prepare_compute_order.py') == PREPARER_SHA
        and sha(control / 'biv150_compute_order.py') == HELPER_SHA
        and preparation['source_count'] == 423 and preparation['emit_only'] is False
        and preparation['base_map_sha256'] == MAP_SHA
        and preparation['output_map'] == expected_a
        and preparation['changed_paths'] == frozen['changed_paths']
        and preparation['runner_sha256'] == frozen['runner_sha256'])
    changed = sorted(key for key in arms['baseline']['source'].keys() | arms['candidate']['source'].keys()
        if arms['baseline']['source'].get(key) != arms['candidate']['source'].get(key))
    checks.update(candidate_exact_423=arms['candidate']['source'] == expected_a,
        only_declared_four_compute_order_paths=changed == sorted(frozen['changed_paths']) and len(changed) == 4,
        candidate_frozen_complete_preparation=prepared_ok,
        both_original_launch=all(value['launch']['matches'] for value in data.values()),
        both_frozen_launchers=all(value['frozen_launcher'] for value in extras.values()),
        both_single_BIV150_32GiB=all(value['single_BIV150_32GiB'] for value in extras.values()),
        both_owned_gone=all(value['owned_gone'] for value in extras.values()),
        both_original_six_CPU=all(int(value['manifest']['cpu_before']['cpu.cfs_quota_us'])
            / int(value['manifest']['cpu_before']['cpu.cfs_period_us']) == 6 for value in arms.values()),
        candidate_actual_compute_order_same_Engine=len(actual) == len(observed) == 1 and marker not in logs['baseline'],
        neither_compute_order_scope_rejected=all('BIV150_COMPUTE_ORDER_SCOPE_REJECTED ' not in log for log in logs.values()),
        neither_finite=all(not value['finite_markers'] for value in data.values()))
    ar, br = data['candidate']['benchmark'], data['baseline']['benchmark']
    percent = {'total_token_throughput_change': 100 * (ar['total_token_throughput'] / br['total_token_throughput'] - 1),
        'duration_saved': 100 * (1 - ar['duration'] / br['duration']),
        'mean_ttft_change': 100 * (ar['mean_ttft_ms'] / br['mean_ttft_ms'] - 1),
        'mean_tpot_change': 100 * (ar['mean_tpot_ms'] / br['mean_tpot_ms'] - 1)}
    ok = all(checks.values())
    return {'kind': '422→计算序423原context16k128单pair', 'runs': data, 'checks': checks,
        'pair_comparable': ok, 'status': 'single_pair_only' if ok else 'confounded_no_performance_conclusion',
        'gain': percent if ok else None, 'descriptive_percent': percent, 'actual_markers': actual,
        'declared_source_changes': changed, 'reader_sha256': sha(Path(__file__)),
        'frozen_preparation_sha256': PREPARED_SHA,
        'limits': ['单pair不证明稳定收益；任一可比项失败gain=null，已知KV失配不放宽或重启凑容量。',
            '计算序新runner不继承422准确率；32/0及forward返回标记不证明数值/token逐位相同或新accuracy。',
            '首次同Engine标记核N等于原sampler_rows及逆映射声明，不表示全程覆盖、采样完成或GPU完成。',
            '原seal逐文件核复用root导入；这里只读完整归档源与原公共DB四端/KV/参数/环境/清理门。',
            '共享cgroup和exporter计数只描述资源，不当新增CPU策略的因果成本。']}


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
