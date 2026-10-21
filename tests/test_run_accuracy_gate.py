"""Small CPU-only command/ownership contract; no instance or GPU access."""

import ast
import hashlib
import importlib.util
import os
from pathlib import Path
import signal
import subprocess
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'accuracy_gate_test', ROOT / 'scripts/remote/run_accuracy_gate.py')
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


class AccuracyGateContract(unittest.TestCase):
    def test_original_server_and_official_script_are_unchanged(self):
        tree = ast.parse((ROOT / 'scripts/remote/run_framework_screen.py').read_text(encoding='utf-8'))
        server = next(ast.literal_eval(node.value) for node in tree.body
                      if isinstance(node, ast.Assign) and
                      any(isinstance(target, ast.Name) and target.id == 'SERVER' for target in node.targets))
        self.assertEqual(gate.SERVER, server)
        script = ROOT / 'scripts/remote/run_math500_level3.sh'
        self.assertEqual(hashlib.sha256(script.read_bytes()).hexdigest(), gate.OFFICIAL_SCRIPT_SHA256)
        driver = (ROOT / 'scripts/remote/run_accuracy_gate.py').read_text(encoding='utf-8')
        self.assertIn("command = ['bash', str(run / 'source/run_math500_level3.sh'), str(run / 'math500-level3')]", driver)

    def test_environment_has_no_profile_or_sampling_override(self):
        source = Path('/isolated/plugin')
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(gate.child_environment(source),
                             dict(VLLM_PLUGINS='fl', PYTHONPATH=str(source), PYTHONUNBUFFERED='1'))
        for name in ['MINICPM_DECODE_GAP_RUN_DIR', 'MINICPM_NATIVE_PROFILE_EVENTS',
                     'VLLM_FL_ILUVATAR_COMPILE_SAMPLER', 'FLAGGEMS_DB_URL']:
            with mock.patch.dict(os.environ, {name: 'unexpected'}, clear=True):
                with self.assertRaisesRegex(RuntimeError, name):
                    gate.child_environment(source)

    def test_timeout_only_kills_owned_group(self):
        process = mock.Mock(pid=501)
        process.wait.side_effect = [subprocess.TimeoutExpired('owned', 45), 0]
        with mock.patch.object(gate.signal, 'SIGKILL', 9, create=True), \
                mock.patch.object(gate.os, 'killpg', create=True) as kill:
            gate.stop_owned_group(process)
        self.assertEqual(kill.call_args_list,
                         [mock.call(501, signal.SIGTERM), mock.call(501, 9)])
        self.assertEqual(process.wait.call_args_list, [mock.call(timeout=45), mock.call(timeout=10)])
        with mock.patch.object(gate.os, 'killpg', create=True,
                               side_effect=ProcessLookupError):
            gate.stop_owned_group(mock.Mock(pid=502))
        gate.stop_owned_group(None)


if __name__ == '__main__':
    unittest.main()
