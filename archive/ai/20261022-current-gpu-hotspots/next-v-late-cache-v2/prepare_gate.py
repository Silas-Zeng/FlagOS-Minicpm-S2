"""仅本地生成：保留已测 policy 原件，给原门增加隔离 cache 因子。"""
import ast
import hashlib
from pathlib import Path

here = Path(__file__).parent
old = here.parent / "next-prefill-v-late"
def sha(raw): return hashlib.sha256(raw).hexdigest()
core = (old / "biv150_prefill_v_late.py").read_bytes()
assert sha(core) == "89134ef1d49d532d91d460094ae7a0563d1546c7d1b8b529490b77ecfa16ab08"
(here / "biv150_prefill_v_late.py").write_bytes(core)
source = (old / "validate_prefill_v_late.py").read_bytes()
assert sha(source) == "8f83395fbd8cef50cf1508e5cc05dfa94cba7fddc7961190920373c70a4675ae"
text = source.decode()
changes = []
def replace(before, after):
    global text
    assert text.count(before) == 1, before[:100]
    text = text.replace(before, after, 1)
    changes.append((before, after))

replace('"""One actual-backend D1/P2047 KV16K upper-bound case; only 2D V address/load/cast lifetime changes.',
        '"""复用 D1/P2047 正确性门；隔离 V-late 默认实例与仅设 PREFER_SHARED 的同 binary 实例。')
replace('TIMING_METHOD = "P2047 ABBA, 32 calls/window; prerecord events; wall includes record/submit/final sync; CPU submit clocks exclude final sync; v1 cpu.stat outside window"',
        'EXPECTED_CACHE_HELPER = "' + sha((here / 'cache_experiment.py').read_bytes()) + '"\n'
        'EXPECTED_CACHE_BRIDGE = "' + sha((here / 'cache_bridge.c').read_bytes()) + '"\n'
        'TIMING_METHOD = "baseline anchor, A default, B cache-only, B, A, baseline anchor; 32 calls/window; prerecord events; existing wall/CPU/event boundaries"')
replace('        result["manager_prepare_wall_ns"] = time.perf_counter_ns() - prepare_begin',
        '        result["manager_prepare_wall_ns"] = time.perf_counter_ns() - prepare_begin\n'
        '        cache_probe = load("isolated_cache_probe", run / "source/cache_experiment.py")\n'
        '        pair = cache_probe.CachePair(manager, run / "source/cache_bridge.c")\n'
        '        result["cache_experiment"] = pair.report\n'
        '        result["limitations"].append("Only per-function PREFER_SHARED is set; dynamic shared optin is untouched. No function cache getter exists; success rc is not proof of an effective carveout or occupancy change.")')
replace('            manager.restore()\n            manager.install()\n            before_bootstrap = manager.snapshot()',
        '            manager.restore()\n'
        '            pair.prepare(torch, lambda: impl.forward(layer, q, k, v, cache, metadata, changed))\n'
        '            manager.install()\n            before_bootstrap = manager.snapshot()')
replace('        for enabled, output in ((False, baseline_out), (True, candidate_out)):\n            manager.install() if enabled else manager.restore()',
        '        for name, output in (("baseline", baseline_out), ("late_v_default", candidate_out), ("candidate", candidate_out)):\n            pair.select(name)')
replace('for _ in range(4)]', 'for _ in range(6)]')
replace('        for name, pair in zip(("baseline", "candidate", "candidate", "baseline"), pairs):\n            manager.restore() if name == "baseline" else manager.install()',
        '        for name, event_pair in zip(("baseline", "late_v_default", "candidate", "candidate", "late_v_default", "baseline"), pairs):\n            pair.select(name)')
replace('row = timed_batch(torch, lambda: invoke(output), pair, 32)',
        'row = timed_batch(torch, lambda: invoke(output), event_pair, 32)')
replace('            if name == "candidate" and (delta(after, before, "selected_calls") != 32',
        '            if name != "baseline" and (delta(after, before, "selected_calls") != 32')
replace('        result["final_counters"] = manager.snapshot()',
        '        result["cache_only_comparison"] = {}\n'
        '        for kind in ("wall", "event"):\n'
        '            a = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "late_v_default")\n'
        '            b = statistics.median(x[kind + "_per_call_ms"] for x in result["timings"] if x["policy"] == "candidate")\n'
        '            result["cache_only_comparison"][kind] = {"late_v_default_ms": a, "late_v_cache_ms": b, "fraction_saved": 1 - b / a}\n'
        '        result["final_counters"] = manager.snapshot()')
replace('    parser.add_argument("--policy-path", type=Path)',
        '    parser.add_argument("--policy-path", type=Path)\n'
        '    parser.add_argument("--cache-helper-path", type=Path)\n'
        '    parser.add_argument("--cache-bridge-path", type=Path)')
replace('(args.runtime_path, args.mixed_path, args.policy_path)',
        '(args.runtime_path, args.mixed_path, args.policy_path, args.cache_helper_path, args.cache_bridge_path)')
replace('("mixed.py", args.mixed_path), ("policy.py", args.policy_path),',
        '("mixed.py", args.mixed_path), ("policy.py", args.policy_path),\n'
        '                           ("cache_experiment.py", args.cache_helper_path),\n'
        '                           ("cache_bridge.c", args.cache_bridge_path),')
replace('("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY)):',
        '("mixed.py", EXPECTED_C3), ("policy.py", EXPECTED_POLICY),\n'
        '                               ("cache_experiment.py", EXPECTED_CACHE_HELPER), ("cache_bridge.c", EXPECTED_CACHE_BRIDGE)):')
replace('"kind": "one actual-layer D1/P2047 late-V-only correctness case, new pointers/nondefault stream, 32 ABBA, no weights/service/score",',
        '"kind": "D1/P2047 cache-only isolation; original anchors and V-late default/cache ABBA32; original correctness gate; no service/score",')
restored = text
for before, after in reversed(changes):
    assert restored.count(after) == 1
    restored = restored.replace(after, before, 1)
assert restored.encode() == source
ast.parse(text)
(here / "validate_prefill_v_late_cache.py").write_text(text, encoding="utf-8", newline="\n")
launcher = (old / "launch_prefill_v_late_gate.sh").read_text(encoding="utf-8")
launcher = launcher.replace("# 仅延迟2D V加载，保持w8和数学；控制器独占卡，失败也保原件。",
                            "# 同worker隔离cache-only因子；原policy数学不变，保留baseline锚。")
launcher = launcher.replace("-prefill-v-late-gate", "-prefill-v-late-cache-gate")
launcher = launcher.replace("validate_prefill_v_late.py", "validate_prefill_v_late_cache.py")
launcher = launcher.replace('  --model /workspace/MiniCPM5-2B)',
    '  --cache-helper-path "$assets/cache_experiment.py"\n  --cache-bridge-path "$assets/cache_bridge.c"\n  --model /workspace/MiniCPM5-2B)')
launcher = launcher.replace('"$assets/biv150_prefill_v_late.py" >',
    '"$assets/biv150_prefill_v_late.py" "$assets/cache_experiment.py" "$assets/cache_bridge.c" >')
(here / "launch_prefill_v_late_cache_gate.sh").write_text(launcher, encoding="utf-8", newline="\n")
print("generated gate; original policy bytes and inverse gate transform verified")
