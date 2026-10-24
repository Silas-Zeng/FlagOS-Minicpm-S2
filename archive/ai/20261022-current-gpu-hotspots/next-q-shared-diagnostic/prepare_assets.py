"""CPU-only：从已测门提取原 fixture，最小改动旧 owner；不运行设备或网络。"""
import ast
import hashlib
import json
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[1]
old = root / "tmp/next-prefill-v-late/validate_prefill_v_late.py"
saved = root / "experiments/framework/20261022T130457Z-prefill-v-late-cache-v2-gate/source"
sha = lambda raw: hashlib.sha256(raw).hexdigest()
raw = old.read_bytes()
assert sha(raw) == "8f83395fbd8cef50cf1508e5cc05dfa94cba7fddc7961190920373c70a4675ae"
old_text = raw.decode()
fixture_source = (saved / "validate_mixed_decode.py").read_bytes()
assert sha(fixture_source) == "b6275ee86f4fb24824091e72fccd774d174247975f8189d360400f333a20351f"


def function(text, name):
    node = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    return "\n".join(text.splitlines()[node.lineno - 1:node.end_lineno])


fixture = ('"""原门两函数逐行提取；只准备数据，不加载候选。"""\n'
           'import itertools\nfrom types import SimpleNamespace\n\n'
           + function(fixture_source.decode(), "make_data") + "\n\n"
           + function(old_text, "prepare_pages") + "\n")
(here / "fixture.py").write_text(fixture, encoding="utf-8", newline="\n")
for name in ("runtime.py", "mixed.py"):
    (here / name).write_bytes((saved / name).read_bytes())
worker = (here / "worker.py").read_bytes()
pins = {"worker.py": sha(worker), "fixture.py": sha(fixture.encode())}
(here / "asset-pins.json").write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
header = ('#!/usr/bin/env python3\n"""原单卡 owner 的 baseline-only ixsys 诊断分支，不产生性能比较。"""\n'
          'from __future__ import annotations\nimport argparse\nimport importlib.metadata\nimport json\nimport os\n'
          'from pathlib import Path\nimport shlex\nimport signal\nimport subprocess\nimport sys\n'
          'import traceback\nfrom validate_hidden_row_gather import digest, utc, write\n'
          'EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"\n'
          'EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"\n'
          'ASSET_PINS = ' + repr(pins) + '\n')
main = function(old_text, "main")
changes = []


def replace(before, after):
    global main
    assert main.count(before) == 1, before
    main = main.replace(before, after, 1)
    changes.append((before, after))


replace('    parser.add_argument("--policy-path", type=Path)\n', '')
replace('    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)\n', '')
replace('    if args.worker:\n        return worker(args.run_dir, args.model)\n', '')
replace('(args.runtime_path, args.mixed_path, args.policy_path)', '(args.runtime_path, args.mixed_path)')
replace('parser.error("controller requires C2, C3 and late-V candidate paths")', 'parser.error("controller requires original C2 and C3 paths")')
replace('    import validate_mixed_decode as previous\n', '')
replace('"kind": "one actual-layer D1/P2047 late-V-only correctness case, new pointers/nondefault stream, 32 ABBA, no weights/service/score",\n                "timing_loops": 32, "timing_method": TIMING_METHOD,',
        '"kind": "baseline-only D1/P2047 KV16K hardware-metrics diagnostic; no performance verdict",\n                "profile_calls": 128,')
replace('("gate.py", Path(__file__)), ("runtime.py", args.runtime_path),\n                           ("mixed.py", args.mixed_path), ("policy.py", args.policy_path),',
        '("controller.py", Path(__file__)), ("runtime.py", args.runtime_path),\n                           ("mixed.py", args.mixed_path),\n                           ("worker.py", Path(__file__).with_name("worker.py")),\n                           ("fixture.py", Path(__file__).with_name("fixture.py")),\n                           ("asset-pins.json", Path(__file__).with_name("asset-pins.json")),')
replace('                           ("validate_mixed_decode.py", Path(previous.__file__)),\n', '')
replace('(("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY))',
        '(("runtime.py", EXPECTED_C2), ("mixed.py", EXPECTED_C3), *ASSET_PINS.items())')
replace('raise RuntimeError("unaudited prefill late-V gate asset: " + name)', 'raise RuntimeError("unaudited baseline diagnostic asset: " + name)')
replace('        manifest["worker_command"] = [sys.executable, str(source / "gate.py"), "--worker", "--run-dir", str(run),\n                                      "--model", str(args.model)]',
        '        if json.loads((source / "asset-pins.json").read_text()) != ASSET_PINS:\n'
        '            raise RuntimeError("worker asset manifest drift")\n'
        '        ixsys = "/usr/local/corex-4.5.0/bin/ixsys"\n'
        '        manifest["ixsys"] = {"path": ixsys, "sha256": digest(Path(ixsys))}\n'
        '        manifest["worker_command"] = [ixsys, "-t", "cuda", "--profile-from-start", "off",\n'
        '            "--gpu-metrics-device", "0", "--gpu-metrics-set", "3", "--gpu-metrics-frequency", "500",\n'
        '            "-o", str(run / "native-trace.json"), sys.executable, str(source / "worker.py"),\n'
        '            "--worker", "--run-dir", str(run), "--model", str(args.model)]')
restored = main
for before, after in reversed(changes):
    if after:
        assert restored.count(after) == 1
        restored = restored.replace(after, before, 1)
# The removed lines are checked by the frozen old source and targeted AST below.
controller = header + "\n\n" + main + '\n\nif __name__ == "__main__":\n    raise SystemExit(main())\n'
ast.parse(controller)
(here / "diagnose_q_shared.py").write_text(controller, encoding="utf-8", newline="\n")
print(json.dumps({"worker": pins["worker.py"], "fixture": pins["fixture.py"], "controller": sha(controller.encode())}))
