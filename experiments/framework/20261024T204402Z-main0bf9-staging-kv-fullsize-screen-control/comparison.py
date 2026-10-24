"""526原官方四轮与538两轮筛选；仅计算条件匹配的组合描述性差，不生成官方分数。"""
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path('/workspace/experiments/minicpm-s2')
HERE = Path(__file__).resolve().parent
BASE_RUN = '20261024T161030Z-main0bf9-main-official-four-rounds'
BASE_COMMIT = '0bf9d2efeaa10144dd7f0ff4597298df029f9328'
BASE_TREE = '8671e2ec040601981d1533d6a09beb20b9e507db'
CANDIDATE_TREE = '835bd25c240a7a0bb25f74db86abd1e19867676a'
OFFICIAL = '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
OFFICIAL_WRAPPER = '39ef67636b565a3bdf7e0da14184c50f9ecaa7081fcc59412a317263ac819e9e'
SCREEN = '7828274129777a5d2fd98bdff082752e2a0c1a3fc8a63c09472646b9c97e6d26'
BENCHMARK = '0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565'
SO = '14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd'
SEED = 'fb0353979939fb6cde016b826b181555aaf11cf1c9c256ddc49c532392f57cfe'
CASES = ((4096, 1024, 64, 256), (16384, 1024, 64, 128))
read = lambda p: json.loads(Path(p).read_bytes())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def require(ok, message):
    if not ok:
        raise ValueError(message)


def inside(root, relative):
    path = root / relative
    require(path.resolve(strict=True).is_relative_to(root.resolve(strict=True)), '原件路径越界')
    return path


def successful(control, area, role, count, tree):
    control = Path(control)
    require(not control.is_symlink(), 'control不能是symlink')
    control = control.resolve(strict=True)
    require(control.is_relative_to(ROOT / area) and control.name.endswith('-control'), 'control目录错误')
    state = read(control / 'state.json')
    require(all(state.get(k) is True for k in ('completed', 'database_restored', 'source_unchanged', 'native_unchanged'))
            and state.get('driver_exit_code') == 0 and (control / 'exit-code').read_text().strip() == '0'
            and state.get('role') == role and state.get('source_count') == count
            and state.get('tree') == tree and state.get('base_commit') == BASE_COMMIT
            and Path(state['control']) == control, '指定来源未成功收尾')
    run = Path(state['run'])
    require(run == control.with_name(control.name[:-8]) and not run.is_symlink(), 'run/control不对应')
    result, manifest = read(run / 'result.json'), read(run / 'manifest.json')
    require(state['result'] == result and result.get('benchmark_completed') is True
            and result.get('exit_code') == 0 and not result.get('cleanup_errors')
            and (run / 'exit-code').read_text().strip() == '0', '测量结果未成功收尾')
    graph = read(run / 'model-path/evidence.json')
    require(state['model_path'] == graph and graph.get('valid') is True
            and graph['graph']['layers'] == list(range(4, 38))
            and graph['fingerprint']['native_enabled'] is True, '真实模型图证据缺失')
    return control, run, state, result, manifest, graph


def source_map(control, name, count, tree):
    manifest = read(HERE / name)
    require(manifest.get('tree') == tree and manifest.get('source_count') == count, '冻结source manifest不符')
    hashes = {p: entry['sha256'] for p, entry in manifest['files'].items()}
    require(len(hashes) == count and read(control / 'source-sha256.json') == hashes, '来源登记与冻结manifest不同')
    return manifest


def csv_case(row):
    return tuple(int(row[k]) for k in ('Prefill', 'Decode', 'Conc', 'Num Prompts'))


def baseline(control):
    data = successful(control, 'official', 'main', 526, BASE_TREE)
    control, run, state, result, manifest, graph = data
    require(run.name == BASE_RUN, '只接受已完成161030 main526；partial532不作资格')
    source_map(control, 'base-source-manifest.json', 526, BASE_TREE)
    require(sha(control / 'official-driver.source.py') == OFFICIAL
            and sha(control / 'driver.py') == OFFICIAL_WRAPPER, '基线driver变化')
    v = result['validation']
    require(v.get('complete') is True and v.get('raw_rows') == 8 and v.get('summary_rows') == 2
            and v.get('runs_per_case') == 4 and v.get('skip_first') == 1
            and v.get('summary_means_verified') is True, '基线不是已验原官方四轮')
    files, raw, summary = [], None, None
    for relative, digest in v['sha256'].items():
        path = inside(run, relative)
        require(sha(path) == digest, '原官方CSV变化')
        files.append(path)
        with path.open(encoding='utf-8-sig', newline='') as f:
            rows = list(csv.DictReader(f))
        if path.name.startswith('raw_runs_'):
            require(raw is None, '多份基线raw CSV'); raw = rows
        elif path.name.startswith('summary_'):
            require(summary is None, '多份基线summary CSV'); summary = rows
    require(raw is not None and summary is not None
            and [csv_case(r) for r in raw] == [c for c in CASES for _ in range(4)]
            and [csv_case(r) for r in summary] == list(CASES), '基线分轮/档位不符')
    return data, raw, summary, files


def qualify_reference(control):
    (control, run, state, result, manifest, graph), raw, summary, files = baseline(control)
    files += [control / p for p in ('state.json', 'source-sha256.json', 'environment-overrides.json',
                                    'driver.py', 'official-driver.source.py')]
    files += [run / p for p in ('result.json', 'manifest.json', 'model-path/evidence.json')]
    return dict(control=str(control), run=str(run), source_count=526, tree=BASE_TREE,
                files={str(p): sha(p) for p in files}, seed_sha256=state.get('seed_sha256'),
                database_before_sha256=state.get('database_before_sha256'),
                kv_tokens=state['observations']['kv_tokens'], gain_calculated=False)


def quota(state):
    try:
        return [int(state['cpu.cfs_quota_us']), int(state['cpu.cfs_period_us'])]
    except (KeyError, ValueError, TypeError):
        return None


def cpu_counters(before, after):
    def parse(value):
        return {k: int(v) for k, v in (line.split() for line in value.get('cpu.stat', '').splitlines())}
    left, right = parse(before), parse(after)
    return {k: right[k] - left[k] for k in left.keys() & right.keys()}


def screen_rows(run, result):
    rows = result['rounds']
    require([(tuple(r['case']), r['round']) for r in rows] == [(c, n) for c in CASES for n in (1, 2)],
            '候选必须恰两档各两轮')
    expected_common = ['vllm', 'bench', 'serve', '--backend', 'vllm', '--model', 'minicpm', '--tokenizer',
                       '/workspace/MiniCPM5-2B', '--endpoint', '/v1/completions', '--host', 'localhost',
                       '--port', '9031', '--dataset-name', 'random', '--ignore-eos']
    commands, evidence = [], {}
    for row in rows:
        case = tuple(row['case']); folder = inside(run, f'{case[0]}-round-{row["round"]}')
        m = read(folder / 'metrics.json')
        require(row['worker_exit_code'] == 0 and (folder / 'exit-code').read_text().strip() == '0'
                and m == row['metrics'], '候选轮次失败或metrics不一致')
        counts = dict(successful_requests=case[3], total_input_tokens=case[0] * case[3],
                      total_output_tokens=case[1] * case[3])
        require(all(m.get(k) == value for k, value in counts.items()), '候选请求/token不完整')
        require(all(type(m.get(k)) in (int, float) and math.isfinite(m[k]) and m[k] > 0 for k in
                    ('benchmark_duration', 'total_token_throughput', 'output_throughput',
                     'mean_ttft_ms', 'mean_tpot_ms', 'elapsed_sec')), '候选metrics无效')
        expected = expected_common + ['--random-input-len', str(case[0]), '--random-output-len', str(case[1]),
                                      '--max-concurrency', str(case[2]), '--num-prompts', str(case[3])]
        commands.append(read(folder / 'benchmark-command.json') == expected)
        for name in ('metrics.json', 'benchmark-command.json', 'stdout.log', 'task.json', 'exit-code'):
            evidence[str(folder / name)] = sha(folder / name)
    return rows, all(commands), evidence


def compare(reference, state):
    for path, pin in reference['files'].items():
        require(sha(path) == pin, '526比较原件在候选运行期间变化')
    (bc, br, bs, bresult, bm, bg), raw, summaries, _ = baseline(reference['control'])
    cc, cr, cs, cresult, cm, cg = successful(state['control'], 'framework', 'kv', 538, CANDIDATE_TREE)
    require(cs == state, '调用方state与成功收尾原件不同')
    candidate = source_map(cc, 'source-manifest.json', 538, CANDIDATE_TREE)
    require(sha(cc / 'driver.py') == sha(cr / 'source/driver.py') == SCREEN
            and sha(cr / 'source/benchmark_throughput_serve.py') == BENCHMARK, '原两轮driver/benchmark身份不同')
    rows, command_ok, evidence = screen_rows(cr, cresult)
    bkv, ckv = bs['observations']['kv_tokens'], cs['observations']['kv_tokens']
    quotas = [quota(x) for x in (bm['cpu_before'], bresult['cpu_after'], cm['cpu_before'], cresult['cpu_after'])]
    outer_command = ['python3', '/workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py',
                     '--model', '/workspace/MiniCPM5-2B', '--served-model-name', 'minicpm', '--port', '9031',
                     '--test-cases', '[[4096,1024,64,256],[16384,1024,64,128]]']
    conditions = dict(
        source_lineage=candidate.get('base_commit') == BASE_COMMIT and candidate.get('base_tree') == BASE_TREE,
        seed_and_database_before=all(s.get('seed_sha256') == s.get('database_before_sha256') == SEED for s in (bs, cs)),
        actual_kv=len(bkv) == len(ckv) == 1 and bkv == ckv,
        cpu_quota=all(q is not None and q == quotas[0] and q[0] == 6 * q[1] for q in quotas),
        original_commands=bm['server_command'] == cm['server_command'] and bm['benchmark_command'] == outer_command
                          and command_ok and cm.get('screen_rounds_per_case') == 2
                          and cm.get('cases') == [list(c) for c in CASES]
                          and cm.get('official_constants_unchanged') == bm.get('repetitions') == {'RUNS': 4, 'SKIP_FIRST': 1},
        native_library=bg['native_library_sha256'] == cg['native_library_sha256'] == SO,
        idle_gpu=bs['preflight']['gpu'].strip() == cs['preflight']['gpu'].strip() == '68, 0',
        verify0=all(read(c / 'environment-overrides.json').get('BIV150_KV_VERIFY_RESTORE') == '0' for c in (bc, cc)),
        no_extra_requests_or_profiler=all(m.get('profiler') is False and m.get('smoke_requests') == 0 for m in (bm, cm)),
        candidate_method_coverage=read(cc / 'transactions.json').get('qualified_method_coverage') is True)
    matched = all(conditions.values())
    cases = []
    metric_map = {'total_token_throughput': 'Total tok/s', 'benchmark_duration': 'Benchmark Duration (s)',
                  'mean_ttft_ms': 'Mean TTFT (ms)'}
    for index, case in enumerate(CASES):
        braw = raw[index * 4:index * 4 + 4]; crow = rows[index * 2:index * 2 + 2]
        differences = None
        if matched:
            differences = {label: {k: (crow[1]['metrics'][k] / float(b[column]) - 1) * 100
                                   for k, column in metric_map.items()}
                           for label, b in (('round2_vs_baseline_round2_percent', braw[1]),
                                            ('round2_vs_baseline_official_retained_mean_percent', summaries[index]))}
        cases.append(dict(case=case, baseline_raw_rounds=[dict(round=i+1, csv_row=r) for i, r in enumerate(braw)],
                          baseline_official_retained_rounds=[2, 3, 4], baseline_official_summary=summaries[index],
                          candidate_raw_rounds=[dict(round=r['round'], metrics=r['metrics']) for r in crow],
                          descriptive_combination_differences=differences))
    out = dict(baseline_control=str(bc), candidate_control=str(cc), comparison_kind='538组合相对526的两轮筛选',
               conditions=conditions, matched_recorded_conditions=matched,
               mismatches=[k for k, v in conditions.items() if not v], actual_kv=dict(baseline=bkv, candidate=ckv),
               cpu_quotas=quotas, cpu_counter_deltas=dict(baseline=cpu_counters(bm['cpu_before'], bresult['cpu_after']),
                                                       candidate=cpu_counters(cm['cpu_before'], cresult['cpu_after'])),
               database_after=dict(baseline=bs.get('database_after_sha256'), candidate=cs.get('database_after_sha256'),
                                   equal=bs.get('database_after_sha256') == cs.get('database_after_sha256')),
               cases=cases, candidate_evidence_sha256=evidence, gain_calculated=matched,
               stable_gain_confirmed=False, strict_causal_gain_claimed=False, official_candidate_score=None,
               limits=['只用成功161030 main526作基线；partial532不是资格或独立staging收益对照。',
                       '候选两轮逐轮展示，不生成官方分数；round2的描述性差不代表稳定收益或独立staging收益。',
                       '首轮不假定相同冷态，不计算首轮增益；16K之前基线已跑4次4K、候选只跑2次，预热历史不同。',
                       'CPU配额相同不证明后台主机负载相同；保留cpu.stat、DB终态和所有原始轮次。',
                       '任一记录条件不齐只列绝对值；最终准确率与正式复现另行判定。'])
    (cc / 'comparison.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return out
