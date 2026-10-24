#!/usr/bin/env bash
# Full official 4K/16K throughput for PR15 + PR21 + Q-hoist.
set -euo pipefail
test "$#" -eq 5
source_dir=$1
commit=$2
tree=$3
seed_database=$4
baseline_summary=$5

root=/workspace/experiments/minicpm-s2
database=/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db
test -f "$database"
test -f "$seed_database"
test -f "$baseline_summary"
test "$(find "$source_dir" \( -type f -o -type l \) \
  ! -path '*/__pycache__/*' ! -name '*.pyc' ! -name '*.pyo' | wc -l)" = 447
test "$(sha256sum "$source_dir/vllm_fl/worker/model_runner.py" | cut -d' ' -f1)" = \
  fa6f2387d258804021e53130ef8ae362ea91a9a23d9b1dcaf1c3d37cb4e0ee9f
test "$(sha256sum "$source_dir/vllm_fl/patches/biv150_compute_order.py" | cut -d' ' -f1)" = \
  0d9f2e7db1725411d587ae9ace5971ebd27747e1c2633e79f8ab618567e32565
test "$(sha256sum "$source_dir/vllm_fl/patches/biv150_q_fragment_service.py" | cut -d' ' -f1)" = \
  ea361e6b604fbd3c7e3a6b95776892a7bc9d22e9988927db3f7876412c6e310f
test "$(ixsmi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits)" = "68, 0"
python3 - <<'PY'
import socket
for family, address in ((socket.AF_INET, "127.0.0.1"), (socket.AF_INET6, "::1")):
    try:
        with socket.socket(family) as sock:
            sock.settimeout(1)
            if sock.connect_ex((address, 9031)) == 0:
                raise RuntimeError("port 9031 occupied on " + address)
    except OSError:
        if family == socket.AF_INET:
            raise
PY

stamp=$(date -u +%Y%m%dT%H%M%SZ)
overall="$root/framework/$stamp-pr15-pr21-qfragment-official-control"
run="$root/official/$stamp-pr15-pr21-qfragment-official"
control="${run}-control"
mkdir "$overall" "$control"
cp "$0" "$overall/run_official_q.sh"

original_db="$overall/database-original.sqlite"
seed_db="$overall/database-seed.sqlite"
cp --preserve=all "$database" "$original_db"
cp --preserve=all "$seed_database" "$seed_db"
original_sha=$(sha256sum "$original_db" | cut -d' ' -f1)
seed_sha=$(sha256sum "$seed_db" | cut -d' ' -f1)
test "$seed_sha" = 1907e03e01190b82b75ff6aad18d5e7fd73cf596eb6c1cc694adc58bd7c5ec72
restore_original() {
  cp --preserve=all "$original_db" "$database"
}
trap restore_original EXIT
cp --preserve=all "$seed_db" "$database"
test "$(sha256sum "$database" | cut -d' ' -f1)" = "$seed_sha"

sha256sum \
  "$root/scripts/run_official_gate.py" \
  "$root/scripts/snapshot_tuning_db.py" \
  "$root/scripts/monitor_gpu.sh" > "$overall/scripts.sha256"
sha256sum \
  "$source_dir/vllm_fl/worker/model_runner.py" \
  "$source_dir/vllm_fl/patches/biv150_compute_order.py" \
  "$source_dir/vllm_fl/patches/biv150_q_fragment_service.py" > "$overall/source-key.sha256"

python3 - "$overall/purpose.json" "$source_dir" "$commit" "$tree" \
  "$seed_sha" "$original_sha" "$run" "$baseline_summary" <<'PY'
import json
from pathlib import Path
import sys

(path, source, commit, tree, seed_sha, original_sha, run,
 baseline_summary) = sys.argv[1:]
value = {
    "kind": "official PR15 + PR21 + Q-hoist throughput before accuracy/PR",
    "source": source,
    "source_count": 447,
    "integration_commit": commit,
    "integration_tree": tree,
    "database_seed_sha256": seed_sha,
    "database_seed_source": "prior PR15+PR21 official database-before",
    "database_restore_sha256": original_sha,
    "official_run": run,
    "baseline_summary": baseline_summary,
    "acceptance": {
        "16k_gain_at_least_percent": 1.0,
        "4k_regression_no_more_than_percent": -1.0,
        "q_fragment_selected_required": True
    },
    "limits": [
        "Throughput-only screen; no accuracy or final merge claim until the full 105-item gate passes.",
        "C500 is not inferred from BI-V150.",
    ],
}
Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

command=(python3 "$root/scripts/run_official_gate.py" "$run" \
  --source-dir "$source_dir" --require-log-marker BIV150_PREFILL_NORMALIZATION_INSTALL \
  --database "$database")
printf '%q ' "${command[@]}" > "$control/command.txt"
printf '\n' >> "$control/command.txt"
set +e
"${command[@]}" > "$control/runner.log" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "$control/runner-exit-code"
test "$code" = 0
test "$(cat "$run/exit-code")" = 0

python3 - "$overall/summary.json" "$run" "$baseline_summary" \
  "$source_dir" "$commit" "$tree" "$seed_sha" <<'PY'
import csv
import json
from pathlib import Path
import re
import sys

out, run, baseline_summary, source, commit, tree, seed_sha = sys.argv[1:]
run = Path(run)
summary_files = sorted((run / "benchmark_results").glob("summary_*.csv"))
raw_files = sorted((run / "benchmark_results").glob("raw_runs_*.csv"))
if len(summary_files) != 1 or len(raw_files) != 1:
    raise RuntimeError("official CSV set differs")

def read_cases(path):
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))

baseline = {int(row["Prefill"]): float(row["Total tok/s"])
            for row in read_cases(baseline_summary)}
candidate = {int(row["Prefill"]): float(row["Total tok/s"])
             for row in read_cases(summary_files[0])}
if set(baseline) != {4096, 16384} or set(candidate) != set(baseline):
    raise RuntimeError("official cases differ")
gain_4k = (candidate[4096] / baseline[4096] - 1) * 100
gain_16k = (candidate[16384] / baseline[16384] - 1) * 100
log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
selected = [
    json.loads(line.split("BIV150_Q_FRAGMENT_SELECTED ", 1)[1])
    for line in log.splitlines() if "BIV150_Q_FRAGMENT_SELECTED " in line
]
fallbacks = [
    line for line in log.splitlines()
    if "BIV150_Q_FRAGMENT_FALLBACK " in line
]
kv_matches = re.findall(r"GPU KV cache size: ([0-9,]+) tokens", log)
kv = [int(value.replace(",", "")) for value in kv_matches]
passed = (
    gain_16k >= 1.0
    and gain_4k >= -1.0
    and bool(selected)
    and not fallbacks
)
value = {
    "status": "pass" if passed else "reject",
    "source": source,
    "source_count": 447,
    "integration_commit": commit,
    "integration_tree": tree,
    "database_seed_sha256": seed_sha,
    "baseline": baseline,
    "candidate": candidate,
    "gain_4k_percent": gain_4k,
    "gain_16k_percent": gain_16k,
    "q_fragment_selected": selected,
    "q_fragment_fallback_count": len(fallbacks),
    "kv_cache_capacities": sorted(set(kv)),
    "summary_csv": str(summary_files[0]),
    "raw_csv": str(raw_files[0]),
    "acceptance": {
        "16k_gain_at_least_1_percent": gain_16k >= 1.0,
        "4k_no_regression_over_1_percent": gain_4k >= -1.0,
        "q_fragment_selected": bool(selected),
        "no_q_fragment_fallback": not fallbacks,
    },
    "accuracy": "pending; throughput-only run",
    "limits": [
        "Official absolute throughput comparison on the same database seed; not a per-method decomposition.",
        "No final baseline or PR merge decision until accuracy passes.",
    ],
}
Path(out).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": value["status"], "gain_4k_percent": gain_4k,
                  "gain_16k_percent": gain_16k,
                  "selected": len(selected), "fallbacks": len(fallbacks),
                  "kv": value["kv_cache_capacities"], "summary": out}))
PY

restore_original
trap - EXIT
test "$(sha256sum "$database" | cut -d' ' -f1)" = "$original_sha"
test "$(ixsmi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits)" = "68, 0"
curl -sS --max-time 1 http://127.0.0.1:9031/health >/dev/null 2>&1 && exit 9 || true
printf 'OVERALL_CONTROL=%s\nOFFICIAL_RUN=%s\n' "$overall" "$run"
