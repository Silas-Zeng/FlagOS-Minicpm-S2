#!/usr/bin/env python3
"""CPU-only pinned source preparation for the NativeK8 K-SME component pair."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
LOOK = HERE.parent / "native-k8-sme-lookahead-20261029"
BASE = LOOK / "biv150_native_k8_klookahead_qk.base.cu"
CAND = LOOK / "biv150_native_k8_klookahead_sme.cu"
CODEC = LOOK / "biv150_native_k8_codec.cuh"
EXPECTED = {
    "base_source": "a491757fff161436a323305f75c3223d12d2d91bd8420b2332e633012f72dd4c",
    "candidate_source": "108131ada8a8b5cae65264f3348b2947ba34eeeb561ea790505bc84f3511ef45",
    "codec": "37d5c7548c0301ee522f50fb0d4d2da53300676e71b03bb806c2d88779801d79",
}
SYMBOLS = (
    "cjj_native_k8_klookahead_gqa_producer",
    "launch_cjj_native_k8_klookahead_s2",
    "launch_cjj_native_k8_klookahead_s4",
)

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def isolate(src: bytes, arm: str) -> tuple[bytes, list[dict]]:
    text = src.decode("utf-8")
    changes = []
    for old in SYMBOLS:
        count = len(re.findall(r"\b" + re.escape(old) + r"\b", text))
        if count < 1:
            raise ValueError(f"symbol missing: {old}")
        new = old.replace("cjj_native_k8_", f"cjj_native_k8_{arm}_", 1)
        text, n = re.subn(r"\b" + re.escape(old) + r"\b", new, text)
        if n != count:
            raise AssertionError((old, count, n))
        changes.append(dict(old=old, new=new, count=count))
    # Check that every delta is exactly the pinned symbol isolation.
    inverse = text
    for item in reversed(changes):
        inverse, n = re.subn(r"\b" + re.escape(item["new"]) + r"\b", item["old"], inverse)
        if n != item["count"]:
            raise AssertionError(item)
    if inverse.encode() != src:
        raise AssertionError("symbol isolation inverse is not byte-exact")
    return text.encode(), changes

def main() -> None:
    for path, key in ((BASE, "base_source"), (CAND, "candidate_source"), (CODEC, "codec")):
        if sha(path.read_bytes()) != EXPECTED[key]:
            raise SystemExit(f"pinned source mismatch: {path}")
    src = {"A": BASE.read_bytes(), "B": CAND.read_bytes()}
    out = HERE / "source"
    out.mkdir(parents=True, exist_ok=True)
    (out / "biv150_native_k8_codec.cuh").write_bytes(CODEC.read_bytes())
    records = {}
    for arm in ("A", "B"):
        data, edits = isolate(src[arm], arm.lower())
        path = out / f"native_k8_sme_{arm}.cu"
        path.write_bytes(data)
        records[arm] = dict(source=path.relative_to(HERE).as_posix(), source_sha256=sha(data),
                            upstream_sha256=sha(src[arm]), symbol_isolation=edits,
                            inverse_byte_exact=True, math_delta="none; symbol names only")
    manifest = dict(scope="isolated component source/build only; no production/service qualification",
                    upstream_pins=EXPECTED, codec_copy_sha256=sha(CODEC.read_bytes()),
                    arms=records, original_reducer={
                        "source": "tmp/framework-main899-shallow-20261029/vllm_fl/patches/biv150_gqa_decode.py",
                        "function": "_reduce_partials",
                        "producer_consumer_wrapper": "reduce_segments call in _make_wrapper",
                        "pin_sha256": sha((HERE.parent / "framework-main899-shallow-20261029/vllm_fl/patches/biv150_gqa_decode.py").read_bytes()),
                        "identity": "same unchanged Triton reducer for A and B; not a CPU/proxy reducer"})
    (HERE / "source-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
