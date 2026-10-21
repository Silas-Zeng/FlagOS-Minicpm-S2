"""Use real retained/rejected evidence and in-memory corruption; never edit raw."""

import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('accuracy_review', ROOT / 'scripts/review_accuracy_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)
PASS = ROOT / 'experiments/remote-evidence/a8-official-candidate/math500-level3/20261021_063351'
REJECT = ROOT / 'experiments/remote-evidence/a9-final/math500-level3/20261021_071243'
REPORT = 'reports/minicpm/math_500.json'
PREDICTIONS = 'predictions/minicpm/math_500_Level 3.jsonl'
REVIEWS = 'reviews/minicpm/math_500_Level 3.jsonl'
CONFIG = 'configs/task_config.yaml'


class AccuracyReview(unittest.TestCase):
    def mutate(self, replacements):
        original = Path.read_bytes
        def read(path):
            relative = path.relative_to(PASS).as_posix()
            return replacements[relative] if relative in replacements else original(path)
        with mock.patch.object(Path, 'read_bytes', read):
            return gate.review(PASS)

    def test_real_pass_and_reject_leave_all_inputs_unchanged(self):
        for directory, correct, verdict, capped in [(PASS, 101, 'pass', 1), (REJECT, 88, 'reject', 15)]:
            before = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                      for name in [REPORT, PREDICTIONS, REVIEWS, CONFIG]}
            result = gate.review(directory)
            self.assertEqual((result['validity'], result['accuracy_gate'], result['correct']),
                             ('valid', verdict, correct))
            self.assertEqual(result['diagnostics']['output_cap_count'], capped)
            self.assertEqual(result['artifact_sha256'], before)
            self.assertEqual(before, {name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
                                     for name in before})

    def test_ignored_transport_failure_cannot_pass(self):
        report = json.loads((PASS / REPORT).read_text(encoding='utf-8'))
        report['execution_summary']['errored'] = 1
        result = self.mutate({REPORT: json.dumps(report).encode()})
        self.assertEqual((result['validity'], result['accuracy_gate']), ('invalid', 'unassessed'))

    def test_duplicate_or_different_question_cannot_pass(self):
        rows = [json.loads(x) for x in (PASS / PREDICTIONS).read_text(encoding='utf-8').splitlines()]
        rows[-1]['index'] = rows[0]['index']
        rows[-1]['metadata']['question_id'] = 'test/other/unknown.json'
        result = self.mutate({PREDICTIONS: ('\n'.join(json.dumps(x) for x in rows) + '\n').encode()})
        self.assertEqual((result['validity'], result['accuracy_gate']), ('invalid', 'unassessed'))
        self.assertTrue(any('indices' in error for error in result['errors']))
        self.assertTrue(any('question IDs differ' in error for error in result['errors']))

    def test_exact_integer_boundary_not_rounded_percentage(self):
        original_reviews = [json.loads(x) for x in (PASS / REVIEWS).read_text(encoding='utf-8').splitlines()]
        for correct, verdict in [(100, 'pass'), (99, 'reject')]:
            report = json.loads((PASS / REPORT).read_text(encoding='utf-8'))
            rows = json.loads(json.dumps(original_reviews))
            for i, row in enumerate(rows):
                row['sample_score']['score']['value']['accuracy'] = float(i < correct)
            metric = report['metrics'][0]
            metric['score'] = metric['categories'][0]['subsets'][0]['score'] = round(correct / 105, 4)
            result = self.mutate({REPORT: json.dumps(report).encode(),
                REVIEWS: ('\n'.join(json.dumps(x) for x in rows) + '\n').encode()})
            self.assertEqual((result['validity'], result['accuracy_gate'], result['correct']),
                             ('valid', verdict, correct))


if __name__ == '__main__':
    unittest.main()
