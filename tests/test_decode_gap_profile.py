"""Small stdlib-only proof of the bounded host diagnostic; no torch/GPU."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pstats
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "decode_gap_footer_test", ROOT / "scripts/remote/decode_gap_profile_footer.py")
footer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(footer)


def fake_classes():
    class Output:
        def __init__(self, value):
            self.value = value

        def get_output(self):
            return self.value

    class Runner:
        def __init__(self):
            self.result, self.output_result = object(), object()
            self.execute_calls, self.sample_calls = [], []
            self.error = None

        def execute_model(self, scheduler_output, *args, **kwargs):
            self.execute_calls.append((scheduler_output, args, kwargs))
            self._update_states(scheduler_output)
            self._prepare_inputs(scheduler_output)
            self._determine_batch_execution_and_padding()
            self._model_forward()
            self._update_states_after_model_execute()
            self.execute_model_state = NS(logits=NS(shape=(len(scheduler_output.num_scheduled_tokens), 130560)))
            if self.error:
                raise self.error
            return self.result

        def _prepare_inputs(self, scheduler_output):
            self._prepare_input_ids(scheduler_output)

        def _determine_batch_execution_and_padding(self):
            return ("FULL", NS(num_tokens=64, num_reqs=64), False)

        def sample_tokens(self, *args, **kwargs):
            self.sample_calls.append((args, kwargs))
            self._sample()
            self._bookkeeping_sync()
            return Output(self.output_result)

    for name in footer._GAP_STAGE_NAMES:
        if not hasattr(Runner, name):
            setattr(Runner, name, lambda self, *args, **kwargs: None)
    return Runner, Output


class DecodeGapProof(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def make_state(self, **kwargs):
        state = footer._GapState(self.directory, **kwargs)
        self.addCleanup(state.log.close)
        self.addCleanup(lambda: state.stop("test_cleanup") if state.active else None)
        runner, output = fake_classes()
        footer._gap_install(runner, output, state)
        return state, runner()

    def test_eight_steps_pass_objects_and_dump_before_next_execute(self):
        state, runner = self.make_state()
        extra, keyword = object(), object()
        for count in (64, 63, 62, 62, 61, 61, 60, 60, 59, 59, 58):
            schedule = NS(num_scheduled_tokens={i: 1 for i in range(count)})
            self.assertIs(runner.execute_model(schedule, extra, token=keyword), runner.result)
            self.assertIs(runner.execute_calls[-1][0], schedule)
            self.assertIs(runner.execute_calls[-1][1][0], extra)
            self.assertIs(runner.execute_calls[-1][2]["token"], keyword)
            output = runner.sample_tokens(keyword)
            self.assertIs(output.get_output(), runner.output_result)
        self.assertTrue(state.done)
        self.assertFalse(state.active)
        summary = json.loads((self.directory / "host-window-summary.json").read_text())
        self.assertTrue(summary["complete"])
        self.assertEqual(summary["profiled_steps"], 8)
        self.assertEqual([s["shape"][0] for s in summary["shapes"]], [62, 62, 61, 61, 60, 60, 59, 59])
        self.assertEqual([s["shape_occurrence"] for s in summary["shapes"]], [1, 2, 1, 2, 1, 2, 1, 2])
        stats = pstats.Stats(str(self.directory / "host-window.pstats"))
        self.assertTrue(any(key[2] == "_prepare_input_ids" for key in stats.stats)
                        or any(key[2] == "stage" for key in stats.stats))
        rows = [json.loads(line) for line in (self.directory / "host-walltime.jsonl").read_text().splitlines()]
        self.assertEqual(sum(row["event"] == "begin" and row.get("stage") == "execute_model" for row in rows), 8)
        self.assertTrue(any(row.get("stage") == "_update_states_after_model_execute" for row in rows))
        self.assertTrue(any(row.get("logits_shape") == [62, 130560] for row in rows))
        self.assertEqual(len(runner.execute_calls), 11)
        self.assertEqual(len(runner.sample_calls), 11)

    def test_interruption_and_original_exception_are_not_hidden(self):
        state, runner = self.make_state(skip=0)
        runner.execute_model(NS(num_scheduled_tokens={i: 1 for i in range(16)}))
        runner.sample_tokens(None).get_output()
        runner.execute_model(NS(num_scheduled_tokens={0: 7}))
        summary = json.loads((self.directory / "host-window-summary.json").read_text())
        self.assertEqual(summary["reason"], "interrupted")
        self.assertFalse(summary["complete"])
        # Separate directory/state for the exception path.
        second = self.directory / "second"
        second.mkdir()
        error_state = footer._GapState(second, skip=0)
        self.addCleanup(error_state.log.close)
        cls, output_cls = fake_classes()
        footer._gap_install(cls, output_cls, error_state)
        obj = cls()
        failure = RuntimeError("original failure")
        obj.error = failure
        with self.assertRaises(RuntimeError) as caught:
            obj.execute_model(NS(num_scheduled_tokens={i: 1 for i in range(16)}))
        self.assertIs(caught.exception, failure)
        self.assertFalse(error_state.active)
        self.assertTrue((second / "host-window.pstats").is_file())

    def test_footer_prefix_hash_rejects_source_drift(self):
        prefix = b"# tiny framing fixture\n"
        expected = hashlib.sha256(prefix).hexdigest()
        target = self.directory / "runner.py"
        target.write_bytes(prefix + b"\n" + footer._GAP_SOURCE_MARKER + b"\n")
        footer._gap_check_source(target, expected)
        target.write_bytes(prefix + b"# drift\n" + footer._GAP_SOURCE_MARKER)
        with self.assertRaisesRegex(RuntimeError, "exact isolated retained"):
            footer._gap_check_source(target, expected)

    def test_only_existing_profile_run_directory_is_allowed(self):
        profiles = self.directory / "profiles"
        run = profiles / "unique-run"
        run.mkdir(parents=True)
        with mock.patch.object(footer, "_GAP_ROOT", self.directory):
            with mock.patch.dict(os.environ, {"MINICPM_DECODE_GAP_RUN_DIR": str(run)}):
                self.assertEqual(footer._gap_run_dir(), run.resolve())
            for invalid in (self.directory, profiles, self.directory / "official" / "run"):
                with mock.patch.dict(os.environ, {"MINICPM_DECODE_GAP_RUN_DIR": str(invalid)}):
                    with self.assertRaises(RuntimeError):
                        footer._gap_run_dir()


if __name__ == "__main__":
    unittest.main()
