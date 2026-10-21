#!/usr/bin/env python3
"""Read-only, CPU-only comparison of complete original13eb and SQL+C3 runs.

Exit 0: per-case comparison; 2: pending evidence; 1: invalid evidence.
Never runs a driver main(), device query, model import, benchmark, or writer.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
from statistics import mean
import sys


MODULES = {
    'run_accuracy_gate': '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54',
    'run_official_gate': '79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579',
    'snapshot_tuning_db': '0f2a57bf3bdb858756a1dedab5bd386a3a8bff384d925cf76461afb8c097e7a2',
}
ATTENTION = 'installed/vllm/v1/attention/ops/triton_unified_attention.py'
ORIGINAL = 'bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0'
RETAINED = '54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f'
CANDIDATE = {
    '__init__.py': 'e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff',
    'worker/model_runner.py': 'e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1',
    'patches/biv150_runtime.py': 'a0c09c51826e0b9e0e5c4f320e68451359db44001d56fd68e1e78de8dda2c9b4',
    'patches/biv150_sql_reflection.py': 'ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e',
    'patches/biv150_decode_launch_runtime.py': 'e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f',
    'patches/biv150_mixed_decode.py': 'a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42',
    'patches/biv150_top_p_triton.py': 'da77c411a88ad4ead072c99cdc4edb52b5bef5b8e5990b9cc8e04db08ed31ca9',
}
MODEL = {'config.json': '59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180',
         'generation_config.json': '9ac4f32e5f32358697a9f438a3ea89ef80e6ba786c72c49e932f9f21c122fdb1'}
PACKAGES = {'vllm': '0.24.0+empty', 'vllm-plugin-fl': '0.3.0rc0+g13eb9be69',
            'torch': '2.10.0+corex.4.5.0', 'transformers': '5.14.1',
            'flag-gems': '5.3.5', 'sqlalchemy': '2.0.48'}


class Pending(Exception):
    pass


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trusted_modules():
    """Exact audited modules: stdlib only except the pinned common helper."""
    loaded = {}
    old_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        for name, expected in MODULES.items():
            path = Path(__file__).resolve().parent / 'remote' / (name + '.py')
            require(sha(path) == expected, 'local reviewed module changed: ' + name)
            for node in ast.walk(ast.parse(path.read_bytes())):
                roots = ([alias.name.split('.')[0] for alias in node.names] if isinstance(node, ast.Import)
                         else [(node.module or '').split('.')[0]] if isinstance(node, ast.ImportFrom) else [])
                require(all(root in sys.stdlib_module_names or root == 'run_accuracy_gate' for root in roots),
                        'non-stdlib import in reviewed module: ' + name)
            require(name not in sys.modules, 'reserved helper name already loaded: ' + name)
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            loaded[name] = module
            spec.loader.exec_module(module)  # main guards remain false.
    finally:
        sys.dont_write_bytecode = old_bytecode
        for name in loaded:
            sys.modules.pop(name, None)
    return loaded['run_official_gate'], loaded['snapshot_tuning_db']


def completion(run):
    missing = [str(run / name) for name in ['manifest.json', 'result.json', 'exit-code']
               if not (run / name).is_file()]
    if missing:
        return missing
    result = read_json(run / 'result.json')
    require((run / 'exit-code').read_text().strip() == '0', str(run) + ': nonzero exit')
    require(result.get('exit_code') == 0 and result.get('benchmark_completed') is True
            and result.get('status') == 'official_benchmark_completed'
            and result.get('benchmark_exit_code') == 0 and result.get('cleanup_errors') == [],
            str(run) + ': not a successful complete official result')
    return []


def audit(run, role, driver, db):
    required = ['gpu.csv', 'server.log', 'postflight-full.json',
                'database-before/manifest.json', 'database-before/snapshot.sqlite',
                'database-after/manifest.json', 'database-after/snapshot.sqlite']
    missing = [str(run / name) for name in required if not (run / name).is_file()]
    missing.extend(str(run / 'benchmark_results' / pattern) for pattern in
                   ['raw_runs_*.csv', 'summary_*.csv'] if not list((run / 'benchmark_results').glob(pattern)))
    if missing:
        raise Pending(missing)
    manifest = read_json(run / 'manifest.json')
    require(manifest['server_command'] == driver.SERVER
            and manifest['benchmark_command'] == driver.benchmark_command(), role + ': CLI/model differs')
    require(manifest['profiler'] is False and manifest['smoke_requests'] == 0
            and manifest['repetitions'] == {'RUNS': 4, 'SKIP_FIRST': 1}, role + ': protocol differs')
    require(manifest['packages'] == PACKAGES and manifest['python'] == '3.12.11'
            and manifest['triton_source_version'] == '3.6.0'
            and manifest['flaggems_revision'] == '4df52d9168ac55c1c1061cefb4638c570292d896'
            and manifest['flaggems_status'] == '', role + ': fixed runtime identity differs')
    hashes, archive = manifest['sha256'], (run / 'source').resolve()
    missing = []
    for name, expected in hashes.items():
        path = (archive / name).resolve()
        require(path.is_relative_to(archive), role + ': archive path escapes source')
        if not path.is_file():
            missing.append(str(path))
        else:
            require(sha(path) == expected, role + ': source SHA mismatch: ' + name)
    if missing:
        raise Pending(missing)
    fixed = {**MODEL, 'benchmark_throughput_serve.py': driver.BENCHMARK_SHA256,
             **{name + '.py': value for name, value in MODULES.items()}}
    require(all(hashes.get(name) == value for name, value in fixed.items()), role + ': model/driver SHA differs')
    require(hashes.get(ATTENTION) == (ORIGINAL if role == 'baseline' else RETAINED), role + ': contaminated Attention')
    revision = manifest.get('plugin_base_revision', manifest.get('plugin_revision'))
    require(revision == ('13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0' if role == 'baseline'
                         else 'd60b02367a852826f653165953f31b6dc696658e'), role + ': wrong plugin base')
    plugin = archive / 'plugin/vllm_fl'
    if role == 'baseline':
        require(hashes.get('plugin/vllm_fl/worker/model_runner.py') ==
                '446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64', 'original baseline worker differs')
        require(not (plugin / 'patches/biv150_runtime.py').exists(), 'baseline retains runtime module')
        require(not any(b'biv150_runtime' in p.read_bytes() or b'_biv150_minicpm_attention_patched_v2' in p.read_bytes()
                        for p in plugin.rglob('*.py')), 'baseline retains hook/marker')
    else:
        require(all(hashes.get('plugin/vllm_fl/' + name) == value for name, value in CANDIDATE.items()),
                'candidate differs from the audited SQL+C3 core')
    with (run / 'gpu.csv').open(encoding='utf-8', newline='') as handle:
        samples = list(csv.DictReader(handle, skipinitialspace=True))
    require(bool(samples) and all(row['index'].strip() == '0' and row['gpu_name'].strip() == 'Iluvatar BI-V150'
                and row['memory.total'].strip() == '32768 MiB' for row in samples), role + ': physical/visible memory differs')
    post = read_json(run / 'postflight-full.json')
    require(post['port_9031_closed'] is True and post['memory_used_mib'] <= 68
            and post.get('gpu_utilization_percent', post.get('utilization_gpu_percent')) == 0, role + ': not idle postflight')
    states = {}
    for phase in ['before', 'after']:
        folder = run / ('database-' + phase)
        recorded, actual = read_json(folder / 'manifest.json'), db.fingerprint((folder / 'snapshot.sqlite').resolve())
        state = {key: actual[key] for key in ['schema_sha256', 'logical_content_sha256', 'table_count', 'row_count']}
        state['snapshot_sha256'] = sha(folder / 'snapshot.sqlite')
        require(all(recorded[key] == value for key, value in state.items()), role + ': DB snapshot fingerprint differs')
        states[phase] = state
    sizes = set(re.findall(r'GPU KV cache size: ([\d,]+) tokens', (run / 'server.log').read_text(encoding='utf-8', errors='replace')))
    require(len(sizes) == 1, role + ': missing/ambiguous real KV size')
    gate = driver.validate_outputs(run)  # The existing raw8/summary2 gate; never main().
    with next((run / 'benchmark_results').glob('raw_runs_*.csv')).open(encoding='utf-8-sig', newline='') as handle:
        rows = list(csv.DictReader(handle))
    return {'source_count': len(hashes), 'visible_memory_mib': 32768,
            'kv_capacity_tokens': int(next(iter(sizes)).replace(',', '')), 'database': states,
            'csv_gate': gate, 'installed_except_attention': {k: v for k, v in hashes.items()
                if k.startswith('installed/') and k != ATTENTION}}, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline_run', type=Path)
    parser.add_argument('candidate_run', type=Path)
    args = parser.parse_args()
    output = {'status': 'pending', 'gain_computed': False,
              'baseline_run': str(args.baseline_run.resolve()), 'candidate_run': str(args.candidate_run.resolve())}
    code = 2
    try:
        driver, db = trusted_modules()
        missing = completion(args.baseline_run) + completion(args.candidate_run)
        if missing:
            raise Pending(missing)
        base, raw_base = audit(args.baseline_run, 'baseline', driver, db)
        candidate, raw_candidate = audit(args.candidate_run, 'candidate', driver, db)
        require(base.pop('installed_except_attention') == candidate.pop('installed_except_attention'),
                'non-Attention installed dependencies differ')
        cases = []
        for index, case in enumerate(json.loads(driver.TEST_CASES)):
            b, c = raw_base[index * 4 + 1:index * 4 + 4], raw_candidate[index * 4 + 1:index * 4 + 4]
            bt, ct = (mean(float(row['Total tok/s']) for row in rows) for rows in [b, c])
            bf, cf = (mean(float(row['Mean TTFT (ms)']) for row in rows) for rows in [b, c])
            cases.append({'case': case, 'retained_original_rounds': [2, 3, 4],
                          'baseline_mean_total_tps': bt, 'candidate_mean_total_tps': ct,
                          'candidate_over_baseline_tps': ct / bt, 'throughput_change_percent': 100 * (ct / bt - 1),
                          'baseline_mean_ttft_ms': bf, 'candidate_mean_ttft_ms': cf,
                          'mean_ttft_change_percent': 100 * (cf / bf - 1)})
        output.update(status='compared', gain_computed=True, cases=cases, baseline=base, candidate=candidate,
                      interpretation='Per-case original-protocol descriptive ratios; positive TTFT means higher latency. '
                      'Inspect actual DB/KV differences; no causal stability or aggregate official score is inferred.')
        code = 0
    except Pending as error:
        output['missing_or_incomplete'] = error.args[0]
    except Exception as error:
        output.update(status='invalid', error=str(error))
        code = 1
    print(json.dumps(output, indent=2, allow_nan=False))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
