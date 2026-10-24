#!/usr/bin/env bash
# Python入口自行新建唯一UTC run并派生单个controller；不再启动另一设备owner。
set -euo pipefail
test "$#" -eq 0
assets=$(cd -- "$(dirname -- "$0")" && pwd)
outer="$assets/launch_last_layer_tail_gate.py"
test "$(sha256sum "$outer" | cut -d' ' -f1)" = 75b06e49dbae9d39301b3cc13144a0f0b12821d6c570584cda2acea0466d4f1b
exec python3 "$outer"
