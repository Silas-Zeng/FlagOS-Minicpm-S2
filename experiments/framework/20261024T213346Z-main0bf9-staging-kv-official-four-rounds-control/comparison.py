"""只读成功161030 main526与538组合官方原件；条件不齐仅列绝对结果。"""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/experiments/minicpm-s2')
PARENT_TREE = '8671e2ec040601981d1533d6a09beb20b9e507db'
BASE_RUN = '20261024T161030Z-main0bf9-main-official-four-rounds'
BASE_COMMIT = '0bf9d2efeaa10144dd7f0ff4597298df029f9328'
CASES = ((4096, 1024, 64, 256), (16384, 1024, 64, 128))
OFFICIAL = '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579'
DRIVER = '39ef67636b565a3bdf7e0da14184c50f9ecaa7081fcc59412a317263ac819e9e'
SEED = 'fb0353979939fb6cde016b826b181555aaf11cf1c9c256ddc49c532392f57cfe'
read = lambda path: json.loads(Path(path).read_bytes())
sha = lambda path: hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require(ok, message):
    if not ok:
        raise ValueError(message)

def completed(control, expected_count, expected_tree, role):
    control = Path(control)
    require(not control.is_symlink(), '比较control不可为symlink')
    control = control.resolve(strict=True)
    require(control.is_relative_to(ROOT/'official') and control.name.endswith('-control'), '比较control不在官方目录')
    state = read(control/'state.json')
    require(all(state.get(k) is True for k in ('completed','database_restored','source_unchanged','native_unchanged'))
            and state.get('driver_exit_code') == 0 and (control/'exit-code').read_text().strip() == '0'
            and state.get('role') == role and state.get('source_count') == expected_count
            and state.get('base_commit') == BASE_COMMIT and not state.get('cleanup_error')
            and state.get('tree') == expected_tree and Path(state['control']) == control,
            '比较源未成功收尾或不是指定候选')
    run = Path(state['run'])
    require(run == control.with_name(control.name[:-8]) and not run.is_symlink(), '比较run/control不对应')
    result, manifest = read(run/'result.json'), read(run/'manifest.json')
    require(state['result'] == result and result.get('benchmark_completed') is True
            and result.get('exit_code') == 0 and (run/'exit-code').read_text().strip() == '0'
            and not result.get('cleanup_errors') and result['validation'].get('complete') is True
            and result['validation'].get('summary_means_verified') is True
            and result['validation'].get('raw_rows') == 8 and result['validation'].get('summary_rows') == 2
            and result['validation'].get('runs_per_case') == 4 and result['validation'].get('skip_first') == 1,
            '比较源不是完整原官方四轮结果')
    require(sha(control/'official-driver.source.py') == OFFICIAL and sha(control/'driver.py') == DRIVER,
            '比较源driver身份变化')
    for relative, digest in result['validation']['sha256'].items():
        path = run/relative
        require(path.resolve(strict=True).is_relative_to(run) and sha(path) == digest, '比较原始CSV或日志变化')
    graph = read(run/'model-path/evidence.json')
    require(state['model_path'] == graph and graph.get('valid') is True
            and graph['graph']['layers'] == list(range(4,38)) and graph['fingerprint']['native_enabled'] is True,
            '比较源真实模型图证据缺失')
    return control, run, state, result, manifest, graph


def official_rows(run, result):
    raw, summary = None, None
    for relative in result['validation']['sha256']:
        path = run/relative
        if not (path.name.startswith('raw_runs_') or path.name.startswith('summary_')):
            continue
        with path.open(encoding='utf-8-sig', newline='') as file:
            rows = list(csv.DictReader(file))
        if path.name.startswith('raw_runs_'):
            require(raw is None, '多份raw CSV'); raw = rows
        else:
            require(summary is None, '多份summary CSV'); summary = rows
    case = lambda r: tuple(int(r[k]) for k in ('Prefill', 'Decode', 'Conc', 'Num Prompts'))
    require(raw is not None and summary is not None
            and [case(r) for r in raw] == [c for c in CASES for _ in range(4)]
            and [case(r) for r in summary] == list(CASES), '原四轮档位/行数不符')
    return raw, summary

def reference(control):
    control, run, state, result, manifest, graph = completed(control, 526, PARENT_TREE, 'main')
    require(run.name == BASE_RUN, '只接受成功161030 main526，不接受partial532')
    parent = read(Path(__file__).with_name('base-source-manifest.json'))
    require(parent['commit'] == BASE_COMMIT and parent['tree'] == PARENT_TREE and parent['source_count'] == 526, '基线manifest错误')
    hashes = {p:entry['sha256'] for p,entry in parent['files'].items()}
    require(len(hashes) == 526 and read(control/'source-sha256.json') == hashes, '比较源并非冻结526源码登记')
    official_rows(run, result)
    files = [control/'state.json',control/'source-sha256.json',
             control/'environment-overrides.json',run/'result.json',run/'manifest.json',run/'model-path/evidence.json']
    files += [run/relative for relative in result['validation']['sha256']]
    return dict(control=str(control), run=str(run), tree=state['tree'], source_count=526,
                files={str(p):sha(p) for p in files}, seed_sha256=state.get('seed_sha256'),
                database_before_sha256=state.get('database_before_sha256'),
                kv_tokens=state['observations']['kv_tokens'], cpu_before=manifest['cpu_before'],
                cpu_after=result['cpu_after'], gain_calculated=False)

def quota(state):
    try:
        return [int(state['cpu.cfs_quota_us']), int(state['cpu.cfs_period_us'])]
    except (KeyError, ValueError, TypeError):
        return None

def cpu_counters(before, after):
    def parse(value):
        return {k:int(v) for k,v in (line.split() for line in value.get('cpu.stat','').splitlines())}
    left, right = parse(before), parse(after)
    return {key:right[key]-left[key] for key in left.keys() & right.keys()}

def compare(candidate_control, snapshot):
    for path, pin in snapshot['files'].items():
        require(sha(path)==pin, '526比较原件在测量期间变化')
    bc, br, bs, bresult, bm, bg = completed(snapshot['control'],526,PARENT_TREE,'main')
    require(br.name == BASE_RUN, '比较基线不是161030')
    candidate = read(Path(__file__).with_name('source-manifest.json'))
    cc, cr, cs, cresult, cm, cg = completed(candidate_control,538,candidate['tree'],'kv')
    require(read(cc/'source-sha256.json') == {p:v['sha256'] for p,v in candidate['files'].items()}, '候选source登记变化')
    braw, bsummary = official_rows(br, bresult)
    craw, csummary = official_rows(cr, cresult)
    bkv, ckv = bs['observations']['kv_tokens'], cs['observations']['kv_tokens']
    quotas = [quota(x) for x in (bm['cpu_before'],bresult['cpu_after'],cm['cpu_before'],cresult['cpu_after'])]
    conditions = dict(
        source_lineage=candidate.get('base_commit') == BASE_COMMIT and candidate.get('base_tree') == PARENT_TREE,
        seed_and_database_before=all(s.get('seed_sha256')==s.get('database_before_sha256')==SEED for s in (bs,cs)),
        actual_kv=len(bkv)==len(ckv)==1 and bkv==ckv,
        cpu_quota=all(q is not None and q==quotas[0] and q[0]==6*q[1] for q in quotas),
        original_commands=bm['server_command']==cm['server_command'] and bm['benchmark_command']==cm['benchmark_command']
                          and bm.get('repetitions')==cm.get('repetitions')=={'RUNS':4,'SKIP_FIRST':1},
        native_library=bg['native_library_sha256']==cg['native_library_sha256']=='14f4457a82388a634e9d381190251223dc925d278753a27011e29999e42dd8fd',
        idle_gpu=bs['preflight']['gpu'].strip()==cs['preflight']['gpu'].strip()=='68, 0',
        verify0=all(read(c/'environment-overrides.json').get('BIV150_KV_VERIFY_RESTORE')=='0' for c in (bc,cc)),
        candidate_method_coverage=read(cc/'transactions.json').get('qualified_method_coverage') is True)
    matched = all(conditions.values())
    cases = []
    for i, case in enumerate(CASES):
        difference = None
        if matched:
            difference = {key: (float(csummary[i][key]) / float(bsummary[i][key]) - 1) * 100
                          for key in ('Total tok/s', 'Benchmark Duration (s)', 'Mean TTFT (ms)')}
        cases.append(dict(case=case, baseline_raw_rounds=braw[i*4:i*4+4],
                          candidate_raw_rounds=craw[i*4:i*4+4],
                          baseline_official_summary=bsummary[i], candidate_official_summary=csummary[i],
                          descriptive_combination_difference_percent=difference))
    out = dict(baseline_control=str(bc),candidate_control=str(cc),conditions=conditions,
               comparison_kind='538 KV＋staging组合相对main526，非staging独立收益',cases=cases,
               matched_recorded_conditions=all(conditions.values()), mismatches=[k for k,v in conditions.items() if not v],
               actual_kv=dict(baseline=bkv,candidate=ckv),cpu_quotas=quotas,
               cpu_counter_deltas=dict(baseline=cpu_counters(bm['cpu_before'],bresult['cpu_after']),
                                       candidate=cpu_counters(cm['cpu_before'],cresult['cpu_after'])),
               database_after=dict(baseline=bs.get('database_after_sha256'),candidate=cs.get('database_after_sha256'),
                                   equal=bs.get('database_after_sha256')==cs.get('database_after_sha256')),
               gain_calculated=matched, strict_causal_gain_claimed=False, stable_gain_confirmed=False,
               limits=['仅比较已记录条件；CPU配额相同不证明后台主机负载完全相同，保留cpu.stat增量。',
                       'DB终态差异单独展示；原始四轮CSV不改写，条件不齐只报告绝对结果。',
                       '只用成功161030 main526作对照；partial532不作资格，差值不是staging独立收益。',
                       'KV不等或其他条件不齐时差值为null；各自官方原分数仍完整保留。',
                       '零FULL不说明方法收益；四轮与完整准确率最终结论由主智能体汇总。'])
    (cc/'comparison.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return out
