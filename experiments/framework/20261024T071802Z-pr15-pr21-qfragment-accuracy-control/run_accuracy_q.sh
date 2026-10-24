#!/usr/bin/env bash
# Full Math500 Level 3 accuracy gate for PR15 + PR21 + Q-hoist.
set -euo pipefail
test "$#" -eq 4
source_dir=$1
commit=$2
tree=$3
seed_database=$4

root=/workspace/experiments/minicpm-s2
database=/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db
test -f "$database"
test -f "$seed_database"
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
overall="$root/framework/$stamp-pr15-pr21-qfragment-accuracy-control"
run="$root/accuracy/$stamp-pr15-pr21-qfragment"
control="${run}-control"
mkdir "$overall" "$control"
cp "$0" "$overall/run_accuracy_q.sh"

original_db="$overall/database-original.sqlite"
seed_db="$overall/database-seed.sqlite"
cp --preserve=all "$database" "$original_db"
cp --preserve=all "$seed_database" "$seed_db"
original_sha=$(sha256sum "$original_db" | cut -d' ' -f1)
seed_sha=$(sha256sum "$seed_db" | cut -d' ' -f1)
test "$seed_sha" = df2ab42beda86421586139bda8219516d31c07b61e7b7b768b879ea95dae3ebe
restore_original() {
  cp --preserve=all "$original_db" "$database"
}
trap restore_original EXIT
cp --preserve=all "$seed_db" "$database"
test "$(sha256sum "$database" | cut -d' ' -f1)" = "$seed_sha"

sha256sum \
  "$root/scripts/run_accuracy_gate.py" \
  "$root/scripts/run_math500_level3.sh" \
  "$root/scripts/review_accuracy_gate.py" \
  "$root/scripts/snapshot_tuning_db.py" \
  "$root/scripts/monitor_gpu.sh" > "$overall/scripts.sha256"
sha256sum \
  "$source_dir/vllm_fl/worker/model_runner.py" \
  "$source_dir/vllm_fl/patches/biv150_compute_order.py" \
  "$source_dir/vllm_fl/patches/biv150_q_fragment_service.py" > "$overall/source-key.sha256"

python3 - "$overall/purpose.json" "$source_dir" "$commit" "$tree" \
  "$seed_sha" "$original_sha" "$run" <<'PY'
import json
from pathlib import Path
import sys

(path, source, commit, tree, seed_sha, original_sha, run) = sys.argv[1:]
value = {
    "kind": "full Math500 Level 3 accuracy for PR15 + PR21 + Q-hoist",
    "source": source,
    "source_count": 447,
    "integration_commit": commit,
    "integration_tree": tree,
    "database_seed_sha256": seed_sha,
    "database_seed_source": "prior PR15+PR21 accuracy database-before",
    "database_restore_sha256": original_sha,
    "accuracy_run": run,
    "acceptance": {
        "minimum_correct": 100,
        "samples": 105,
        "q_fragment_selected_required": True,
        "no_q_fragment_fallback": True,
    },
    "limits": [
        "Single stochastic 105-item Level 3 evaluation.",
        "C500 is not inferred from BI-V150.",
    ],
}
Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
PY

command=(python3 "$root/scripts/run_accuracy_gate.py" "$run" \
  --source-dir "$source_dir" --require-log-marker BIV150_Q_FRAGMENT_INSTALL \
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

mapfile -t evaluation_dirs < <(find "$run/math500-level3" -mindepth 1 -maxdepth 1 -type d | sort)
test "${#evaluation_dirs[@]}" -eq 1
set +e
python3 "$root/scripts/review_accuracy_gate.py" "${evaluation_dirs[0]}" \
  > "$run/accuracy-review.json" 2> "$run/accuracy-review.log"
review_code=$?
set -e
printf '%s\n' "$review_code" > "$control/review-exit-code"
test "$review_code" = 0

python3 - "$overall/summary.json" "$run" "$source_dir" "$commit" "$tree" \
  "$seed_sha" <<'PY'
import json
from pathlib import Path
import sys

out, run, source, commit, tree, seed_sha = sys.argv[1:]
run = Path(run)
review = json.loads((run / "accuracy-review.json").read_text(encoding="utf-8"))
log = (run / "server.log").read_text(encoding="utf-8", errors="replace")
selected = [
    line for line in log.splitlines()
    if "BIV150_Q_FRAGMENT_SELECTED " in line
]
fallbacks = [
    line for line in log.splitlines()
    if "BIV150_Q_FRAGMENT_FALLBACK " in line
]
passed = (
    review.get("validity") == "valid"
    and review.get("accuracy_gate") == "pass"
    and review.get("samples") == 105
    and review.get("correct", 0) >= 100
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
    "accuracy": review,
    "q_fragment_selected_count": len(selected),
    "q_fragment_fallback_count": len(fallbacks),
    "acceptance": {
        "valid_105_samples": review.get("validity") == "valid"
        and review.get("samples") == 105,
        "at_least_100_correct": review.get("correct", 0) >= 100,
        "q_fragment_selected": bool(selected),
        "no_q_fragment_fallback": not fallbacks,
    },
    "limits": [
        "Single stochastic 105-item evaluation, not repeated accuracy statistics.",
        "C500 is not inferred from BI-V150.",
    ],
}
Path(out).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"status": value["status"], "correct": review.get("correct"),
                  "samples": review.get("samples"), "selected": len(selected),
                  "fallbacks": len(fallbacks), "summary": out}))
PY

restore_original
trap - EXIT
test "$(sha256sum "$database" | cut -d' ' -f1)" = "$original_sha"
test "$(ixsmi --query-gpu=memory.used,utilization.gpu --format=csv,noheader,nounits)" = "68, 0"
curl -sS --max-time 1 http://127.0.0.1:9031/health >/dev/null 2>&1 && exit 9 || true
printf 'OVERALL_CONTROL=%s\nACCURACY_RUN=%s\n' "$overall" "$run"
