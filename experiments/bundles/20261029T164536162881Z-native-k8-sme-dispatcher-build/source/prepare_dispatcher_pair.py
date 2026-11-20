#!/usr/bin/env python3
"""Prepare two isolated Torch dispatchers from pinned local main899 sources; CPU only."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[2]
COMPONENT = HERE.parent
DEFAULT_FRAMEWORK = PROJECT / "tmp/framework-main899-shallow-20261029"
EXPECTED = {
    "main": "899ce77470b0b539aebc108fd122f668c2d5894d",
    "qk_cpp": "157b6fcdf4af464406b889d92801a92cbdedffd9dd68d4e3104f785e46fb363e",
    "codec_cu": "50258694d7844a654dcf006ae4ad052f66b7db4c0e650437962822911c56c3be",
    "codec_header": "37d5c7548c0301ee522f50fb0d4d2da53300676e71b03bb806c2d88779801d79",
    "A_cu": "434b596af854108cca4cfdd2025121cf431d20d31e7e1d93718cfd450d337542",
    "B_cu": "8df62a7cdbd284d0593ba8f1bee825b3765b966b1d3a8b90fbb06db0c2ca075a",
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, count: int) -> tuple[str, dict]:
    found = len(re.findall(r"\b" + re.escape(old) + r"\b", text))
    if found != count:
        raise ValueError(f"Expected {count} occurrences of {old}, found {found}")
    changed, n = re.subn(r"\b" + re.escape(old) + r"\b", new, text)
    if n != count:
        raise AssertionError((old, count, n))
    return changed, {"old": old, "new": new, "count": n}


def isolate_host(raw: bytes, arm: str) -> tuple[bytes, list[dict]]:
    text = raw.decode("utf-8")
    suffix = arm.lower()
    edits = []
    replacements = [
        ("cjj_native_k8_klookahead_probe", f"cjj_native_k8_klookahead_probe_{suffix}", 2),
        ("launch_cjj_native_k8_klookahead_s2", f"launch_cjj_native_k8_{suffix}_klookahead_s2", 2),
        ("launch_cjj_native_k8_klookahead_s4", f"launch_cjj_native_k8_{suffix}_klookahead_s4", 2),
        ("cjj_launch_native_k8_klookahead_codec", f"cjj_launch_native_k8_{suffix}_klookahead_codec", 2),
    ]
    for old, new, count in replacements:
        text, record = replace_once(text, old, new, count)
        edits.append(record)
    inverse = text
    for e in reversed(edits):
        inverse, n = re.subn(r"\b" + re.escape(e["new"]) + r"\b", e["old"], inverse)
        if n != e["count"]:
            raise AssertionError(e)
    if inverse.encode("utf-8") != raw:
        raise AssertionError("host source isolation is not byte-reversible")
    return text.encode("utf-8"), edits


def isolate_codec(raw: bytes, arm: str) -> tuple[bytes, list[dict]]:
    suffix = arm.lower()
    text = raw.decode("utf-8")
    edits = []
    for old, new in (
        ("cjj_native_k8_klookahead_codec_probe", f"cjj_native_k8_{suffix}_klookahead_codec_probe"),
        ("cjj_launch_native_k8_klookahead_codec", f"cjj_launch_native_k8_{suffix}_klookahead_codec"),
    ):
        count = len(re.findall(r"\b" + re.escape(old) + r"\b", text))
        if count < 1:
            raise ValueError(f"Codec symbol absent: {old}")
        text, record = replace_once(text, old, new, count)
        edits.append(record)
    inverse = text
    for e in reversed(edits):
        inverse, n = re.subn(r"\b" + re.escape(e["new"]) + r"\b", e["old"], inverse)
        if n != e["count"]:
            raise AssertionError(e)
    if inverse.encode("utf-8") != raw:
        raise AssertionError("codec source isolation is not byte-reversible")
    return text.encode("utf-8"), edits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--framework-root", type=Path, default=DEFAULT_FRAMEWORK)
    parser.add_argument("--out", type=Path, default=HERE / "sources")
    args = parser.parse_args()
    framework = args.framework_root.resolve()
    out = args.out.resolve()
    if out.exists():
        raise SystemExit(f"Refusing to overwrite prepared source directory: {out}")
    git_head = subprocess.check_output(["git", "-C", str(framework), "rev-parse", "HEAD"], text=True).strip()
    if git_head != EXPECTED["main"]:
        raise SystemExit(f"Wrong source checkout: expected {EXPECTED['main']}, got {git_head}")
    root = framework / "tools/kernels"
    inputs = {
        "host": root / "biv150_native_k8_klookahead_qk.cpp",
        "codec": root / "biv150_native_k8_klookahead_codec.cu",
        "header": COMPONENT / "source/biv150_native_k8_codec.cuh",
        "A": COMPONENT / "source/native_k8_sme_A.cu",
        "B": COMPONENT / "source/native_k8_sme_B.cu",
    }
    expected = {"host": EXPECTED["qk_cpp"], "codec": EXPECTED["codec_cu"],
                "header": EXPECTED["codec_header"], "A": EXPECTED["A_cu"], "B": EXPECTED["B_cu"]}
    blobs = {key: path.read_bytes() for key, path in inputs.items()}
    for key, raw in blobs.items():
        if sha(raw) != expected[key]:
            raise SystemExit(f"Pinned source mismatch for {key}: {sha(raw)}")
    out.mkdir(parents=True)
    manifest = {"scope": "isolated compile-only Torch dispatchers; no production install or device use",
                "main_commit": git_head, "inputs": {}, "arms": {}, "qualification": "none"}
    for key, raw in blobs.items():
        manifest["inputs"][key] = {"sha256": sha(raw), "origin": str(inputs[key])}
    (out / "biv150_native_k8_codec.cuh").write_bytes(blobs["header"])
    for arm in ("A", "B"):
        suffix = arm.lower()
        host, host_edits = isolate_host(blobs["host"], arm)
        codec, codec_edits = isolate_codec(blobs["codec"], arm)
        # The tested device CU already has isolated A/B producer and launcher symbols.
        kernels = blobs[arm]
        for name, data in ((f"dispatcher_{suffix}.cpp", host),
                           (f"codec_{suffix}.cu", codec),
                           (f"producer_{suffix}.cu", kernels)):
            (out / name).write_bytes(data)
        manifest["arms"][arm] = {
            "namespace": f"cjj_native_k8_klookahead_probe_{suffix}",
            "launcher_prefix": f"launch_cjj_native_k8_{suffix}_klookahead",
            "host_sha256": sha(host), "codec_sha256": sha(codec), "producer_sha256": sha(kernels),
            "host_edits": host_edits, "codec_edits": codec_edits,
            "all_host_and_codec_edits_inverse_byte_exact": True,
        }
    (out / "dispatcher-source-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
