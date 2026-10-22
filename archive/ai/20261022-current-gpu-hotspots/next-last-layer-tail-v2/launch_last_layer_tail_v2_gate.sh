#!/usr/bin/env bash
# Python入口自行新建唯一UTC run并派生单个controller；不再启动另一设备owner。
set -euo pipefail
test "$#" -eq 0
assets=$(cd -- "$(dirname -- "$0")" && pwd)
outer="$assets/launch_last_layer_tail_v2_gate.py"
test "$(sha256sum "$outer" | cut -d' ' -f1)" = 510bd1623177d00a7bd5cd6f462dfccb439a0cab2e362cb107ce1a977297e206
exec python3 "$outer"
