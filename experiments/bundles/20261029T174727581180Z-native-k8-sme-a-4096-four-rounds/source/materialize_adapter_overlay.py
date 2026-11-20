#!/usr/bin/env python3
"""Generate a private NativeK8 A/B adapter overlay from the pinned main899 tree.

This emits only three replacement source files and a manifest; it never edits
the supplied checkout and never changes the existing 5898 qualification pins.
"""
import argparse
import hashlib
import json
from pathlib import Path

MAIN = "899ce77470b0b539aebc108fd122f668c2d5894d"
ROLES = {
    "A": {
        "sha256": "824f7dda043dd8e101b0f2296cba4aeda14d0718ae673805da1564a141c1f734",
        "namespace": "cjj_native_k8_klookahead_probe_a",
    },
    "B": {
        "sha256": "bdc16c49fef721b5dad7d7627f9c046f726f29a2f9c589297b9f4f036b08b6ef",
        "namespace": "cjj_native_k8_klookahead_probe_b",
    },
}
ROOT_FILES = {
    "adapter": "vllm_fl/patches/biv150_konly_encoded_native.py",
    "semantics": "vllm_fl/compile_semantics.py",
    "sources": "vllm_fl/patches/biv150_konly_encoded_sources.json",
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise ValueError(f"{label}: expected one anchor, found {count}")
    return text.replace(old, new, 1)


def generate(main, out, role):
    main = main.resolve()
    out = out.resolve()
    if not main.is_dir() or out == main or main in out.parents:
        raise ValueError("main root must exist; output must be outside it")
    pin = ROLES[role]
    inputs = {name: (main / rel).read_bytes() for name, rel in ROOT_FILES.items()}
    adapter = inputs["adapter"].decode("utf-8")
    adapter = replace_once(adapter,
        "LIBRARY_SHA='5898a00a4a4e3314ee8ed1fc40dffde02a766ca6d0e5c116dbd161dccaa3286b'",
        f"LIBRARY_SHA='{pin['sha256']}'", "adapter library pin")
    adapter = replace_once(adapter,
        "OPERATOR='cjj_native_k8_klookahead_probe::produce'",
        f"OPERATOR='{pin['namespace']}::produce'", "adapter operator")
    adapter = replace_once(adapter,
        "SCHEMA='cjj_native_k8_klookahead_probe::produce(",
        f"SCHEMA='{pin['namespace']}::produce(", "adapter schema")
    adapter = replace_once(adapter,
        "namespace=torch.ops.cjj_native_k8_klookahead_probe",
        f"namespace=torch.ops.{pin['namespace']}", "adapter namespace lookup")
    adapter = replace_once(adapter,
        "self.op=torch.ops.cjj_native_k8_klookahead_probe.produce.default",
        f"self.op=torch.ops.{pin['namespace']}.produce.default", "adapter op binding")
    adapter = replace_once(adapter,
        "self.op is self.torch.ops.cjj_native_k8_klookahead_probe.produce.default",
        f"self.op is self.torch.ops.{pin['namespace']}.produce.default", "adapter identity verification")

    semantics = inputs["semantics"].decode("utf-8")
    semantics = replace_once(semantics,
        "expected = '5898a00a4a4e3314ee8ed1fc40dffde02a766ca6d0e5c116dbd161dccaa3286b'",
        f"expected = '{pin['sha256']}'", "fingerprint library pin")
    semantics = replace_once(semantics,
        "operator='cjj_native_k8_klookahead_probe::produce'",
        f"operator='{pin['namespace']}::produce'", "fingerprint operator")

    source_doc = json.loads(inputs["sources"])
    native = source_doc["native_decode"]
    native["adapter"]["sha256"] = sha(adapter.encode())
    native["library_sha256"] = pin["sha256"]
    native["operator"] = f"{pin['namespace']}::produce"
    native["overlay_role"] = role
    source_raw = (json.dumps(source_doc, ensure_ascii=False, indent=2) + "\n").encode()
    emitted = {
        ROOT_FILES["adapter"]: adapter.encode(),
        ROOT_FILES["semantics"]: semantics.encode(),
        ROOT_FILES["sources"]: source_raw,
    }
    if out.exists():
        raise ValueError(f"refusing to overwrite existing output: {out}")
    for rel, raw in emitted.items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    manifest = {
        "schema": 1,
        "declared_source_commit": MAIN,
        "role": role,
        "library_sha256": pin["sha256"],
        "namespace": pin["namespace"],
        "format": "cjj-konly-rn32-rne-v2",
        "physical_page_bytes": 16384,
        "service_qualified": False,
        "model_accuracy_verified": False,
        "source_inputs": {ROOT_FILES[k]: sha(v) for k, v in inputs.items()},
        "overlay_files": {rel: {"sha256": sha(raw), "bytes": len(raw)} for rel, raw in emitted.items()},
        "install_instruction": "Copy overlay files into a disposable main899 source copy; do not modify or reuse the 5898 source pins.",
    }
    (out / "native-k8-sme-overlay.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def main_cli():
    p = argparse.ArgumentParser()
    p.add_argument("--main-root", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--role", choices=tuple(ROLES), required=True)
    a = p.parse_args()
    generate(a.main_root, a.out, a.role)


if __name__ == "__main__":
    main_cli()
