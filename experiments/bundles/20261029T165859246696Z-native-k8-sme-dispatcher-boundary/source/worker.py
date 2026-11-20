#!/usr/bin/env python3
"""Root-owned short dispatcher-boundary check; CPU default, explicit GPU opt-in only."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
COMPONENT = HERE.parent
SOURCES = HERE / "sources"
PAGE_BYTES = 16384
SCALE = 128 ** -0.5 * 1.4426950408889634
SENTINEL = -321.25
OUTPUT_SENTINEL = 768.0
LENGTHS = (0, 1, 15, 16, 17, 31, 32, 33, 46, 47)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_component_worker():
    path = COMPONENT / "worker.py"
    spec = importlib.util.spec_from_file_location("native_k8_sme_component_worker", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load shared component helpers")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_build(summary_path: Path, source_dir: Path):
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    manifest_path = source_dir / "dispatcher-source-manifest.json"
    if not summary.get("completed") or summary.get("compile_only") is not True:
        raise RuntimeError("dispatcher build summary is not a successful compile-only result")
    if summary.get("operator_called") is not False or summary.get("gpu_initialized") is not False:
        raise RuntimeError("dispatcher build summary contains unexpected runtime activity")
    if sha(manifest_path) != summary.get("source_manifest_sha256"):
        raise RuntimeError("prepared dispatcher source manifest SHA mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if sha(source_dir / "biv150_native_k8_codec.cuh") != manifest["inputs"]["header"]["sha256"]:
        raise RuntimeError("dispatcher codec header SHA mismatch")
    libraries = {}
    for arm in ("A", "B"):
        row = summary["arms"][arm]
        suffix = arm.lower()
        expected_files = {f"dispatcher_{suffix}.cpp": row["source_sha256"][f"dispatcher_{suffix}.cpp"],
                          f"producer_{suffix}.cu": row["source_sha256"][f"producer_{suffix}.cu"],
                          f"codec_{suffix}.cu": row["source_sha256"][f"codec_{suffix}.cu"]}
        for name, expected in expected_files.items():
            if sha(source_dir / name) != expected:
                raise RuntimeError(f"dispatcher source SHA mismatch: {arm}/{name}")
        if expected_files[f"dispatcher_{suffix}.cpp"] != manifest["arms"][arm]["host_sha256"]:
            raise RuntimeError(f"dispatcher host identity differs from prepared manifest: {arm}")
        if expected_files[f"producer_{suffix}.cu"] != manifest["arms"][arm]["producer_sha256"]:
            raise RuntimeError(f"dispatcher producer identity differs from prepared manifest: {arm}")
        if expected_files[f"codec_{suffix}.cu"] != manifest["arms"][arm]["codec_sha256"]:
            raise RuntimeError(f"dispatcher codec identity differs from prepared manifest: {arm}")
        library = summary_path.parent / row["library"]
        if not library.is_file() or sha(library) != row["library_sha256"]:
            raise RuntimeError(f"dispatcher SO SHA mismatch: {arm}")
        libraries[arm] = library.resolve()
    return summary, manifest, libraries


def allocate_inputs(torch, batch: int, q_stride: int, seed: int):
    gen = torch.Generator(device="cuda").manual_seed(seed)
    pages = 3
    qstore = torch.empty((batch * q_stride,), dtype=torch.bfloat16, device="cuda")
    q = qstore.as_strided((batch, 16, 128), (q_stride, 128, 1))
    q.copy_(torch.randn(q.shape, generator=gen, device="cuda", dtype=torch.float32).to(torch.bfloat16))

    # One allocation backs the exact host-checked K/scale/V roles and provides
    # the shifted BF16 V view on the final page. Active pages stay intentionally small.
    storage = torch.empty((pages * PAGE_BYTES + 8192,), dtype=torch.uint8, device="cuda")
    storage.zero_()
    raw = storage[:pages * PAGE_BYTES]
    key = raw.view(torch.int8).as_strided((pages, 16, 2, 128), (16384, 256, 128, 1))
    scale_full = storage.view(torch.float32)
    value = storage.view(torch.bfloat16).as_strided(
        (pages, 16, 2, 128), (8192, 256, 128, 1), storage_offset=4096)

    # Produce the test cache through both registered codec entry points. Their
    # identical outputs become the exact encoded K code/scale fields consumed below.
    codec_input = torch.randn((pages * 32, 128), generator=gen, device="cuda", dtype=torch.float32).to(torch.bfloat16)
    codec_input_before = codec_input.clone()
    codes_a = torch.empty((pages * 32, 128), dtype=torch.int8, device="cuda")
    codes_b = torch.empty_like(codes_a)
    scales_a = torch.empty((pages * 32,), dtype=torch.float32, device="cuda")
    scales_b = torch.empty_like(scales_a)
    torch.ops.cjj_native_k8_klookahead_probe_a.codec(codec_input, codes_a, scales_a)
    torch.ops.cjj_native_k8_klookahead_probe_b.codec(codec_input, codes_b, scales_b)
    torch.cuda.current_stream().synchronize()
    if not torch.equal(codes_a, codes_b) or not torch.equal(scales_a, scales_b):
        raise AssertionError("A/B codec dispatcher outputs differ")
    if not torch.equal(codec_input, codec_input_before):
        raise AssertionError("codec dispatcher modified its readonly BF16 input")
    if not bool(torch.all(torch.isfinite(scales_a))) or not bool(torch.all(scales_a > 0)):
        raise AssertionError("codec generated invalid K scale")
    key.copy_(codes_a.view(pages, 16, 2, 128))
    scale_ids = (torch.arange(pages, device="cuda", dtype=torch.int64)[:, None] * 4096 + 1024
                 + torch.arange(32, device="cuda", dtype=torch.int64)[None, :])
    scale_full[scale_ids] = scales_a.view(pages, 32)
    value.copy_(torch.randn(value.shape, generator=gen, device="cuda", dtype=torch.float32).to(torch.bfloat16))

    lengths = torch.full((batch,), 32, dtype=torch.int32, device="cuda")
    for i, length in enumerate(LENGTHS):
        lengths[i] = length
    table = torch.zeros((batch, 3), dtype=torch.int32, device="cuda")
    table.copy_(torch.arange(3, dtype=torch.int32, device="cuda").expand(batch, 3))
    return dict(q=q, qstore=qstore, storage=storage, key=key, scale=scale_full,
                value=value, lengths=lengths, table=table, batch=batch,
                q_stride=q_stride, pages=pages, codec_rows=pages * 32,
                codec_input_immutable=True,
                codec_outputs_bitwise=True)


def allocate_outputs(torch, batch: int, segments: int):
    pstore = torch.full((batch * 16 * segments * 128 + 32,), SENTINEL,
                        dtype=torch.float32, device="cuda")
    mstore = torch.full((batch * 16 * segments + 32,), SENTINEL,
                        dtype=torch.float32, device="cuda")
    lstore = torch.full((batch * 16 * segments + 32,), SENTINEL,
                        dtype=torch.float32, device="cuda")
    partial = pstore[16:-16].view(batch, 16, segments, 128)
    maximum = mstore[16:-16].view(batch, 16, segments)
    summation = lstore[16:-16].view(batch, 16, segments)
    out_store = torch.full((batch * 16 * 128 + 32,), OUTPUT_SENTINEL,
                           dtype=torch.bfloat16, device="cuda")
    output = out_store[16:].as_strided((batch, 16, 128), (2048, 128, 1))
    return dict(partial=partial, maximum=maximum, summation=summation,
                pstore=pstore, mstore=mstore, lstore=lstore,
                output=output, out_store=out_store)


def dispatch(torch, arm: str, x, z, segments: int):
    op = getattr(getattr(torch.ops, f"cjj_native_k8_klookahead_probe_{arm.lower()}"), "produce")
    op(x["q"], x["key"], x["scale"], x["value"], x["lengths"], x["table"],
       z["partial"], z["maximum"], z["summation"], float(SCALE), segments)


def reduce(reducer, x, z, segments: int):
    reducer[(x["batch"], 16)](
        output_ptr=z["output"], segm_output_ptr=z["partial"],
        segm_max_ptr=z["maximum"], segm_expsum_ptr=z["summation"],
        seq_lens_ptr=x["lengths"], segment_stride_token=z["partial"].stride(0),
        segment_stride_head=z["partial"].stride(1), segment_stride_segment=z["partial"].stride(2),
        segment_stride_dim=z["partial"].stride(3), max_stride_token=z["maximum"].stride(0),
        max_stride_head=z["maximum"].stride(1), max_stride_segment=z["maximum"].stride(2),
        output_stride_token=z["output"].stride(0), output_stride_head=z["output"].stride(1),
        page_size=16, num_segments=segments, HEAD_SIZE=128, num_warps=1, num_stages=1)


def full_call(torch, reducer, arm: str, x, z, segments: int):
    dispatch(torch, arm, x, z, segments)
    reduce(reducer, x, z, segments)


def assert_equal(torch, za, zb, label: str):
    for name in ("partial", "maximum", "summation", "output", "pstore", "mstore", "lstore", "out_store"):
        if not torch.equal(za[name], zb[name]):
            raise AssertionError(f"A/B mismatch in {label}: {name}")


def assert_guards(torch, z):
    for key in ("pstore", "mstore", "lstore"):
        if not bool(torch.all(z[key][:16] == SENTINEL)) or not bool(torch.all(z[key][-16:] == SENTINEL)):
            raise AssertionError(f"scratch guard overwritten: {key}")
    if not bool(torch.all(z["out_store"][:16] == OUTPUT_SENTINEL)) or not bool(torch.all(z["out_store"][-16:] == OUTPUT_SENTINEL)):
        raise AssertionError("output guard overwritten")


def run_case(torch, reducer, segments: int, batch: int, seed: int):
    q_stride = 2560
    x = allocate_inputs(torch, batch, q_stride, seed)
    q_before = x["q"].clone()
    storage_before = x["storage"].clone()
    lengths_before = x["lengths"].clone()
    table_before = x["table"].clone()
    za = allocate_outputs(torch, batch, segments)
    zb = allocate_outputs(torch, batch, segments)
    stream = torch.cuda.Stream()
    stream.wait_stream(torch.cuda.current_stream())
    with torch.cuda.stream(stream):
        full_call(torch, reducer, "A", x, za, segments)
        full_call(torch, reducer, "B", x, zb, segments)
    stream.synchronize()
    assert_equal(torch, za, zb, "side-stream eager")
    assert_guards(torch, za)
    assert_guards(torch, zb)
    unchanged = {"q": bool(torch.equal(x["q"], q_before)),
                 "storage": bool(torch.equal(x["storage"], storage_before)),
                 "lengths": bool(torch.equal(x["lengths"], lengths_before)),
                 "table": bool(torch.equal(x["table"], table_before))}
    if not all(unchanged.values()):
        raise AssertionError(f"dispatcher mutated read-only inputs: {unchanged}")

    # Capture each namespace and replay after changing Q, on the same non-default stream.
    graphs = {arm: torch.cuda.CUDAGraph() for arm in ("A", "B")}
    graph_outputs = {arm: allocate_outputs(torch, batch, segments) for arm in ("A", "B")}
    stream.wait_stream(torch.cuda.current_stream())
    for arm in ("A", "B"):
        with torch.cuda.graph(graphs[arm], stream=stream):
            with torch.cuda.stream(stream):
                full_call(torch, reducer, arm, x, graph_outputs[arm], segments)
    with torch.cuda.stream(stream):
        x["q"].add_(1.0)
    stream.synchronize()
    with torch.cuda.stream(stream):
        graphs["A"].replay()
        graphs["B"].replay()
    stream.synchronize()
    assert_equal(torch, graph_outputs["A"], graph_outputs["B"], "changed-Q graph replay")
    if torch.equal(graph_outputs["A"]["output"], za["output"]):
        raise AssertionError("changed Q was not observed by graph replay")
    assert_guards(torch, graph_outputs["A"])
    assert_guards(torch, graph_outputs["B"])
    with torch.cuda.stream(stream):
        x["q"].copy_(q_before)
    stream.synchronize()
    if not torch.equal(x["q"], q_before):
        raise AssertionError("Q restoration after graph check failed")
    return {"batch": batch, "segments": segments, "q_stride": q_stride,
            "lengths_mixed": list(LENGTHS), "default_full_length": 32,
            "pages": x["pages"], "table_columns": int(x["table"].shape[1]),
            "active_pages_max": 3, "codec_rows": x["codec_rows"],
            "codec_input_immutable": x["codec_input_immutable"],
            "codec_dispatch_A_B_bitwise": x["codec_outputs_bitwise"],
            "side_stream_A_B_bitwise": True,
            "changed_Q_graph_A_B_bitwise": True, "graph_observed_Q_change": True,
            "input_immutability_before_graph": unchanged,
            "guards_intact": True, "original_reducer": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gpu", action="store_true")
    parser.add_argument("--root-owned-exclusive", action="store_true")
    parser.add_argument("--compiled", type=Path, help="dispatcher-build-summary.json from compile-only build")
    parser.add_argument("--main-root", type=Path)
    parser.add_argument("--sources", type=Path, default=SOURCES)
    parser.add_argument("--cudart", type=Path, default=Path("/usr/local/corex/lib64/libcudart.so"))
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if not args.gpu:
        if args.root_owned_exclusive or args.compiled or args.main_root or args.out:
            parser.error("GPU/build paths require explicit --gpu")
        print(json.dumps({"cpu_default": True, "gpu_executed": False,
                          "cases": ["S2/N64/KV<=47/Qstride2560", "S4/N32/KV<=47/Qstride2560"]}, indent=2))
        return 0
    if not args.root_owned_exclusive:
        parser.error("GPU execution requires --root-owned-exclusive")
    if not args.compiled or not args.main_root or not args.main_root.is_absolute() or not args.out:
        parser.error("Provide --compiled, absolute --main-root, and --out")
    if not args.out.is_absolute() or args.out.exists():
        parser.error("--out must be a fresh absolute result file")
    if not args.cudart.is_file():
        raise FileNotFoundError(f"CoreX runtime missing: {args.cudart}")
    summary_path = args.compiled.resolve()
    summary, manifest, libraries = load_build(summary_path, args.sources.resolve())

    import torch
    import triton
    component_worker = load_component_worker()
    reducer, reducer_path, reducer_function_sha, reducer_module_path = component_worker.load_reducer(
        args.main_root.resolve(), args.out.parent.resolve())
    if torch.cuda.is_initialized():
        raise RuntimeError("Unexpected initialized context before boundary checks")
    cudart = ctypes.CDLL(str(args.cudart.resolve()), mode=ctypes.RTLD_GLOBAL)
    # Explicitly load the built registrations in this fresh process. No operator is invoked until cases below.
    for arm in ("A", "B"):
        torch.ops.load_library(str(libraries[arm]))
        ns = getattr(torch.ops, f"cjj_native_k8_klookahead_probe_{arm.lower()}")
        if not hasattr(ns, "produce") or not hasattr(ns, "codec"):
            raise RuntimeError(f"Torch dispatcher registrations missing for {arm}")
    result = {"scope": "new dispatcher boundary only; isolated component, not production qualification",
              "gpu_executed": True, "service_qualification": False, "model_accuracy": False,
              "official_performance": False, "runtime_command": sys.argv, "python": sys.version,
              "torch": torch.__version__, "triton": triton.__version__,
              "device": torch.cuda.get_device_name(),
              "source_manifest_sha256": sha(args.sources / "dispatcher-source-manifest.json"),
              "declared_source_commit": manifest["main_commit"],
              "build_summary_path": str(summary_path), "build_summary_sha256": sha(summary_path),
              "build_summary": summary,
              "libs": {arm: {"path": str(path), "sha256": sha(path)} for arm, path in libraries.items()},
              "reducer_source": str(reducer_path), "reducer_file_sha256": sha(reducer_path),
              "reducer_function_sha256": reducer_function_sha,
              "reducer_module_path": str(reducer_module_path),
              "reducer_module_sha256": sha(reducer_module_path),
              "cudart": str(args.cudart.resolve()), "cudart_sha256": sha(args.cudart.resolve()),
              "current_stream": int(torch.cuda.current_stream().cuda_stream), "cases": []}
    result["cases"].append(run_case(torch, reducer, segments=2, batch=64, seed=164536))
    result["cases"].append(run_case(torch, reducer, segments=4, batch=32, seed=164537))
    result["cases_all_passed"] = True
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"out": str(args.out), "cases_all_passed": True,
                      "cases": result["cases"]}, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
