#!/bin/sh
# CPU compiler only. No model/torch import or kernel launch.
set -eu
here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
out=$1
mkdir "$out"
cxx=/usr/local/corex/bin/clang++
"$cxx" --version > "$out/compiler-version.txt"
sha256sum "$here/gqa_s4_draft.cu" > "$out/input.sha256"
"$cxx" -O3 -std=c++17 -D__ILUVATAR__ -D__MR__ -DCOREX_NATIVE_GQA_V_OVERLAP=0 -x ivcore --cuda-gpu-arch=ivcore11 --cuda-path=/usr/local/corex --cuda-device-only -S -emit-llvm "$here/gqa_s4_draft.cu" -o "$out/gqa.ll" > "$out/llvm-build.log" 2>&1
"$cxx" -O3 -std=c++17 -D__ILUVATAR__ -D__MR__ -DCOREX_NATIVE_GQA_V_OVERLAP=0 -x ivcore --cuda-gpu-arch=ivcore11 --cuda-path=/usr/local/corex --cuda-device-only -S "$here/gqa_s4_draft.cu" -o "$out/gqa.s" > "$out/asm-build.log" 2>&1
python3 "$here/check-compile.py" "$out" > "$out/compile-check.log" 2>&1
