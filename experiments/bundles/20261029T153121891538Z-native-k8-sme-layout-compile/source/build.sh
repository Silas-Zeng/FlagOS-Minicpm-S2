#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p build
CMD=(/usr/local/corex/bin/clang++
  -D__ILUVATAR__ -D__MR__
  -O2 -std=c++17 -fPIC -x ivcore
  --cuda-gpu-arch=ivcore11 --cuda-path=/usr/local/corex
  -shared native_k8_sme_probe.cu
  -L/usr/local/corex/lib64 -lcudart
  -o build/libnative_k8_sme_probe.so)
printf '%q ' "${CMD[@]}" > build/build-command.txt
printf '\n' >> build/build-command.txt
"${CMD[@]}" 2>&1 | tee build/build.log
sha256sum native_k8_sme_probe.cu build/libnative_k8_sme_probe.so > build/build-sha256.txt
