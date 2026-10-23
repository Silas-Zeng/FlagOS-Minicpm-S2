#!/usr/bin/env python3
"""Read one explicit EvalScope Math500 Level 3 result, without changing raw files.

JSON goes to stdout and a short verdict to stderr. Exit 0 means complete/pass,
1 complete/below 0.95, and 2 invalid or incomplete evidence. Requires PyYAML
for the saved task configuration; imports no model or accelerator libraries.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys


EXPECTED = 105
MAX_TOKENS = 32768
# Both retained official a8 and rejected a9 have these same 105 question IDs.
# Hash protocol: sorted IDs, ASCII JSON, separators=(',', ':').
EXPECTED_QUESTION_IDS_SHA256 = '408a7c94387cdbf7ac1eb86f9736dd57a5fee55f715dd443994d90d43b22b45b'
EXPECTED_DATASET_FINGERPRINT = 'sha256:d2a0a846c4e8e0b074d9cf260e5bb5c3a1d6e41086e4ecefc7d17c624949151a'


def review(directory):
    directory = Path(directory).resolve(strict=True)
    errors = []
    artifacts = {}

    def require(condition, message):
        if not condition:
            errors.append(message)

    def read(relative):
        path = directory / relative
        content = path.read_bytes()
        artifacts[relative] = hashlib.sha256(content).hexdigest()
        return content.decode('utf-8-sig')

    def jsonl(relative):
        return [json.loads(line) for line in read(relative).splitlines() if line.strip()]

    # Require the timestamp directory itself: never silently choose a report.
    report = json.loads(read('reports/minicpm/math_500.json'))
    predictions = jsonl('predictions/minicpm/math_500_Level 3.jsonl')
    reviews = jsonl('reviews/minicpm/math_500_Level 3.jsonl')
    import yaml
    config = yaml.safe_load(read('configs/task_config.yaml'))
    require(config.get('model') == 'minicpm', 'config model must be minicpm')
    require(config.get('api_url') == 'http://127.0.0.1:9031/v1/chat/completions',
            'config API endpoint differs from official command')
    require(config.get('eval_type') == 'openai_api' and config.get('datasets') == ['math_500'],
            'config must select only math_500 through openai_api')
    dataset = config.get('dataset_args', {}).get('math_500', {})
    require(dataset.get('dataset_id') == '/workspace/evalscope-datasets/math_500' and
            dataset.get('subset_list') == ['Level 3'], 'dataset path/subset differs')
    generation = config.get('generation_config', {})
    for key, value in {'temperature': 1.0, 'top_p': 0.95, 'max_tokens': MAX_TOKENS,
                       'timeout': 3600, 'batch_size': 8}.items():
        require(generation.get(key) == value, 'generation_config.' + key + ' differs')
    require(config.get('eval_batch_size') == 8, 'eval_batch_size must be 8')
    require(config.get('ignore_errors') is True, 'ignore_errors differs from official command')
    require(config.get('limit') is None and config.get('repeats') == 1 and
            config.get('rerun_review') is False and config.get('use_cache') is None,
            'limit/repeats/review/cache settings differ')
    benchmark = config.get('resolved_benchmarks', {}).get('math_500', {})
    require(benchmark.get('subset_list') == ['Level 3'] and benchmark.get('eval_split') == 'test'
            and benchmark.get('shuffle') is False and benchmark.get('few_shot_num') == 0,
            'resolved benchmark selection differs')
    identity = config.get('evaluation_identity', {}).get('benchmarks', {}).get('math_500', {})
    require(identity.get('cache_source') is None, 'result was reused from a cache')
    require(identity.get('fingerprint') == EXPECTED_DATASET_FINGERPRINT,
            'dataset/evaluation fingerprint differs from retained official runs')

    summary = report.get('execution_summary', {})
    require(report.get('dataset_name') == 'math_500' and report.get('model_name') == 'minicpm',
            'report model/dataset identity differs')
    require(report.get('num') == EXPECTED and summary.get('requested') == EXPECTED and
            summary.get('succeeded') == EXPECTED and summary.get('errored') == 0 and
            summary.get('incomplete') is False, 'report execution is incomplete or errored')
    require(summary.get('subsets') == {'Level 3': {'requested': EXPECTED,
            'succeeded': EXPECTED, 'errored': 0}}, 'execution subset coverage differs')
    metric_identity = {'name': 'accuracy', 'aggregation': 'mean', 'dimensions': {}}
    require(report.get('primary_metric_identity') == metric_identity and
            report.get('primary_metric_unavailable_reason') is None,
            'primary metric must be available mean accuracy')
    metrics = [m for m in report.get('metrics', []) if m.get('identity') == metric_identity]
    require(len(metrics) == 1, 'expected one mean accuracy metric')
    metric = metrics[0] if len(metrics) == 1 else {}
    require(metric.get('num') == EXPECTED, 'metric denominator differs')
    subsets = [s for c in metric.get('categories', []) for s in c.get('subsets', [])]
    require(len(subsets) == 1 and subsets[0].get('name') == 'Level 3' and
            subsets[0].get('num') == EXPECTED and subsets[0].get('is_aggregate') is False,
            'metric must contain exactly the 105-sample Level 3 subset')

    def index_rows(rows, label):
        indices = [row.get('index') for row in rows]
        require(len(rows) == EXPECTED, label + ' must have 105 rows')
        require(all(type(i) is int for i in indices) and sorted(indices) == list(range(EXPECTED)),
                label + ' indices must cover 0..104 once')
        return {row['index']: row for row in rows if type(row.get('index')) is int}

    pmap, rmap = index_rows(predictions, 'prediction'), index_rows(reviews, 'review')
    scores, prediction_ids, review_ids = [], [], []
    stops, statuses = Counter(), Counter()
    transport_errors, capped, empty_final, empty_extracted, missing_usage = [], [], [], [], []
    for row in predictions:
        index = row.get('index')
        prediction_ids.append(row.get('metadata', {}).get('question_id'))
        output = row.get('model_output', {})
        require(row.get('model') == 'minicpm' and output.get('model') == 'minicpm',
                f'prediction {index}: model differs')
        if output.get('error') is not None:
            transport_errors.append(index)
        choices = output.get('choices', [])
        require(len(choices) == 1, f'prediction {index}: expected one response choice')
        texts = []
        for choice in choices:
            stops[str(choice.get('stop_reason', choice.get('finish_reason')))] += 1
            content = choice.get('message', {}).get('content')
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                texts.extend(item.get('text', '') for item in content if item.get('type') == 'text')
        if not ''.join(texts).strip():
            empty_final.append(index)
        usage = output.get('usage') or {}
        tokens = usage.get('output_tokens', usage.get('completion_tokens'))
        if type(tokens) is not int:
            missing_usage.append(index)
        elif tokens >= MAX_TOKENS:
            capped.append(index)
    require(not transport_errors, 'predictions contain model_output.error')
    for row in reviews:
        index = row.get('index')
        sample = row.get('sample_score', {})
        score = sample.get('score', {})
        statuses[str(score.get('status'))] += 1
        require(sample.get('sample_id') == index and sample.get('generation_index') == 0,
                f'review {index}: sample/generation identity differs')
        require(score.get('status') == 'success', f'review {index}: score status is not success')
        value = score.get('value', {}).get('accuracy')
        valid = type(value) in (int, float) and math.isfinite(value) and value in (0, 1)
        require(valid, f'review {index}: accuracy must be finite binary 0/1')
        if valid:
            scores.append(int(value))
        review_ids.append(sample.get('sample_metadata', {}).get('question_id'))
        if not str(score.get('extracted_prediction') or '').strip():
            empty_extracted.append(index)
    for label, ids in [('prediction', prediction_ids), ('review', review_ids)]:
        require(all(isinstance(x, str) and x for x in ids) and len(set(ids)) == EXPECTED,
                label + ' question_id must contain 105 unique nonempty IDs')
        if all(isinstance(x, str) for x in ids):
            digest = hashlib.sha256(json.dumps(sorted(ids), ensure_ascii=True,
                    separators=(',', ':')).encode('ascii')).hexdigest()
            require(digest == EXPECTED_QUESTION_IDS_SHA256,
                    label + ' question IDs differ from retained official Level 3 set')
    for index in sorted(pmap.keys() & rmap.keys()):
        require(pmap[index].get('metadata', {}).get('question_id') ==
                rmap[index].get('sample_score', {}).get('sample_metadata', {}).get('question_id'),
                f'question_id mismatch at index {index}')
    correct = sum(scores)
    exact = correct / EXPECTED if len(scores) == EXPECTED else None
    for label, value in [('metric', metric.get('score'))] + [
            ('subset', s.get('score')) for s in subsets]:
        require(exact is not None and type(value) in (int, float) and math.isfinite(value)
                and abs(value - exact) <= 0.000050000001,
                label + ' rounded score disagrees with review numerator')
    valid = not errors
    passed = valid and 100 * correct >= 95 * EXPECTED
    return {'format': 'math500-level3-readonly-review-v1', 'evaluation_dir': str(directory),
            'validity': 'valid' if valid else 'invalid',
            'accuracy_gate': ('pass' if passed else 'reject') if valid else 'unassessed',
            'correct': correct, 'samples': len(scores), 'expected_samples': EXPECTED,
            'exact_accuracy': exact, 'threshold': 0.95, 'minimum_correct': 100,
            'reported_score': metric.get('score'), 'errors': errors,
            'diagnostics': {'stop_reasons': dict(stops), 'review_statuses': dict(statuses),
                            'transport_error_count': len(transport_errors),
                            'transport_error_indices': transport_errors,
                            'output_cap_count': len(capped), 'output_cap_indices': sorted(capped),
                            'empty_final_count': len(empty_final), 'empty_final_indices': sorted(empty_final),
                            'empty_extracted_count': len(empty_extracted),
                            'empty_extracted_indices': sorted(empty_extracted),
                            'missing_usage_indices': missing_usage},
            'evalscope_version': config.get('evalscope_version'),
            'dataset_fingerprint': identity.get('fingerprint'), 'artifact_sha256': artifacts,
            'limitations': ['Reads saved outputs only; does not prove server code installation or cleanup.',
                            'Truncation/empty-answer diagnostics do not change the official denominator.',
                            'Does not independently recompute the official answer judge.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('evaluation_dir', type=Path, help='explicit timestamp directory with reports/configs')
    args = parser.parse_args(argv)
    try:
        result = review(args.evaluation_dir)
    except Exception as error:
        result = {'validity': 'invalid', 'accuracy_gate': 'unassessed',
                  'errors': [type(error).__name__ + ': ' + str(error)]}
    print(json.dumps(result, ensure_ascii=True, indent=2, allow_nan=False))
    print('validity={} accuracy_gate={} correct={}/{}'.format(result['validity'],
          result['accuracy_gate'], result.get('correct', '?'), result.get('expected_samples', '?')),
          file=sys.stderr)
    return 2 if result['validity'] != 'valid' else (0 if result['accuracy_gate'] == 'pass' else 1)


if __name__ == '__main__':
    raise SystemExit(main())
