"""已归档三条cache的纯CPU审计；不导入Torch/Triton，不改原件。"""
import hashlib
import json
from pathlib import Path
import re
import struct

ROOT = Path(__file__).resolve().parents[3]
AUDIT = ROOT / "experiments/source-audits/20261021T183920Z-compiler-cache"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def sections(path):
    raw = path.read_bytes()
    assert raw[:6] == b"\x7fELF\x02\x01", "only little-endian ELF64"
    header = struct.unpack_from("<16sHHIQQQIHHHHHH", raw)
    offset, entry_size, count, name_index = header[6], header[11], header[12], header[13]
    entries = [struct.unpack_from("<IIQQQQIIQQ", raw, offset + i * entry_size) for i in range(count)]
    names = entries[name_index]
    strings = raw[names[4]:names[4] + names[5]]
    result = {}
    for entry in entries:
        name = strings[entry[0]:].split(b"\0", 1)[0].decode("ascii")
        payload = raw[entry[4]:entry[4] + entry[5]] if entry[1] != 8 else b""
        result[name] = {"type": entry[1], "flags": entry[2], "size": entry[5], "sha256": sha(payload)}
    return result


def main():
    manifest = json.loads((AUDIT / "manifest.json").read_text(encoding="utf-8"))
    verified = 0
    for relative, record in manifest["sources"].items():
        if record["status"] == "copied":
            assert sha((AUDIT / "installed-triton" / relative).read_bytes()) == record["sha256"]
            verified += 1
    for role, item in manifest["entries"].items():
        for directory, entries in item["directories"].items():
            for name, record in entries.items():
                if record["status"] == "copied":
                    assert sha((AUDIT / "cache" / role / directory / name).read_bytes()) == record["sha256"]
                    verified += 1
    first = next((AUDIT / "cache/service_original").iterdir())
    second = next((AUDIT / "cache/gate_baseline").iterdir())
    a = json.loads((first / "mm_kernel.json").read_text())
    b = json.loads((second / "mm_kernel.json").read_text())
    metadata_differences = {k: [a.get(k), b.get(k)] for k in a.keys() | b.keys() if a.get(k) != b.get(k)}
    assert set(metadata_differences) == {"hash"}
    mlir = {}
    for extension in ("source", "ttir", "ttgir"):
        def normalized(path):
            return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                             if not re.match(r"^#loc\w* = loc\(", line))
        x, y = normalized(first / ("mm_kernel." + extension)), normalized(second / ("mm_kernel." + extension))
        assert x == y
        mlir[extension] = {"equal_after_removing_only_debug_loc_definitions": True, "normalized_sha256": sha(x.encode())}
    def llvm(path):
        return "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                         if not re.match(r"^!\d+ = (?:distinct )?!(?:DIFile|DISubprogram|DILocation)\(", line))
    x, y = llvm(first / "mm_kernel.llir"), llvm(second / "mm_kernel.llir")
    assert x == y
    sa, sb = sections(first / "mm_kernel.cubin"), sections(second / "mm_kernel.cubin")
    differences = {name: [sa.get(name), sb.get(name)] for name in sa.keys() | sb.keys() if sa.get(name) != sb.get(name)}
    assert set(differences) == {".debug_info", ".debug_line"}
    allocated = {name: entry for name, entry in sa.items() if entry["flags"] & 2}
    assert all(sb.get(name) == entry for name, entry in allocated.items())
    result = {"status": "archived_service_original_and_gate_baseline_executable_payloads_equal",
              "audit": str(AUDIT.relative_to(ROOT)), "verified_source_and_cache_files": verified,
              "collector_sha256": sha((AUDIT / "collector.py").read_bytes()),
              "metadata_differences": metadata_differences, "all_compiler_options_equal": True,
              "use_sme_both": a["use_sme"], "mlir": mlir,
              "llvm_equal_after_removing_only_source_debug_definitions": True,
              "llvm_normalized_sha256": sha(x.encode()), "different_ELF_sections": differences,
              "all_SHF_ALLOC_payload_type_flags_size_equal": True,
              "executable_sections": {name: entry for name, entry in allocated.items() if entry["flags"] & 4},
              "raw_binaries_equal": (first / "mm_kernel.cubin").read_bytes() == (second / "mm_kernel.cubin").read_bytes(),
              "GPU_executed": False,
              "limits": "Only these archived cache entries and this fixed configuration; no fresh compile, device or model accuracy claim."}
    output = Path(__file__).with_name("compile-cache-review.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
