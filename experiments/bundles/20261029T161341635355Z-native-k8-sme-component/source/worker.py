#!/usr/bin/env python3
"""Root-owned GPU-only correctness and paired timing entry; no default execution."""
from __future__ import annotations
import argparse
import ast
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
PAGES = 34276
PAGE_BYTES = 16384
SCALE = 128 ** -0.5 * 1.4426950408889634
SHAPES = ((64, 2, 4096), (32, 4, 16384))
Q_STRIDES = (2048, 2560)
SENT = -123456.0

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def ptr(t):
    return ctypes.c_void_p(t.data_ptr())

def load_reducer(root: Path, module_dir: Path):
    path = root / "vllm_fl/patches/biv150_gqa_decode.py"
    pin = json.loads((HERE / "source-manifest.json").read_text(encoding="utf-8"))["original_reducer"]
    if sha(path) != pin["source_file_sha256"]:
        raise RuntimeError("original reducer file pin mismatch")
    text = path.read_text(encoding="utf-8")  # universal newline conversion is recorded below
    tree = ast.parse(text)
    node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_reduce_partials")
    body = ast.get_source_segment(text, node)
    function_source = "@triton.jit\n" + body + "\n"
    function_sha = hashlib.sha256(function_source.encode("utf-8")).hexdigest()
    if function_sha != pin["function_source_sha256"]:
        raise RuntimeError("normalized original reducer function pin mismatch")
    module_source = "import triton\nimport triton.language as tl\n\n" + function_source
    module_dir.mkdir(parents=True, exist_ok=True)
    module_path = module_dir / f"native_k8_sme_original_reducer_{function_sha[:12]}.py"
    if module_path.exists():
        if module_path.read_text(encoding="utf-8") != module_source:
            raise RuntimeError("existing reducer module differs from pinned source")
    else:
        module_path.write_text(module_source, encoding="utf-8", newline="\n")
    spec = importlib.util.spec_from_file_location("native_k8_sme_original_reducer", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load original reducer module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module._reduce_partials, path, function_sha, module_path

def bind(libpath: Path, arm: str, segments: int):
    lib = ctypes.CDLL(str(libpath), mode=ctypes.RTLD_LOCAL)
    fn = getattr(lib, f"launch_cjj_native_k8_{arm.lower()}_klookahead_s{segments}")
    fn.argtypes = [ctypes.c_void_p] * 6 + [ctypes.c_int, ctypes.c_float] + [ctypes.c_int64] * 8 + [ctypes.c_void_p] * 4
    fn.restype = None
    return lib, fn

def allocate_inputs(torch, batch: int, segments: int, seqlen: int, q_stride: int, seed: int):
    gen = torch.Generator(device="cuda").manual_seed(seed)
    pages_per_row = (seqlen + 15) // 16
    qstore = torch.empty((batch * q_stride,), dtype=torch.bfloat16, device="cuda")
    q = qstore.as_strided((batch, 16, 128), (q_stride, 128, 1))
    q.copy_(torch.randn(q.shape, generator=gen, device="cuda", dtype=torch.float32).to(torch.bfloat16))
    # The typed views use the same owned cache bytes; trailing redzone only makes
    # the shifted V view legal as a PyTorch view for its final page.
    storage = torch.empty((PAGES * PAGE_BYTES + 8192,), dtype=torch.uint8, device="cuda")
    storage.random_(0, 255, generator=gen)
    raw = storage[:PAGES * PAGE_BYTES]
    key = raw.view(torch.int8)
    scale_full = storage.view(torch.float32)
    value = storage.view(torch.bfloat16).as_strided(
        (PAGES, 16, 2, 128), (8192, 256, 128, 1), storage_offset=4096)
    # Set every key scale to a finite positive value at the exact full-view ABI offset.
    scale_ids = (torch.arange(PAGES, device="cuda", dtype=torch.int64)[:, None] * 4096 + 1024
                 + torch.arange(32, device="cuda", dtype=torch.int64)[None, :])
    scale_full[scale_ids] = 0.02
    value.copy_(torch.randn(value.shape, generator=gen, device="cuda", dtype=torch.float32).to(torch.bfloat16))
    lengths = torch.full((batch,), seqlen, dtype=torch.int32, device="cuda")
    table = torch.zeros((batch, 8192), dtype=torch.int32, device="cuda")
    # Disjoint random physical page IDs keep the active working set > typical L2.
    order = torch.randperm(PAGES, generator=gen, device="cuda")[:batch * pages_per_row]
    table[:, :pages_per_row] = order.reshape(batch, pages_per_row)
    return dict(q=q, qstore=qstore, storage=storage, key=key, scale=scale_full, value=value,
                lengths=lengths, table=table, pages_per_row=pages_per_row,
                segments=segments, batch=batch, q_stride=q_stride)

def scratch(torch, batch: int, segments: int):
    pstore = torch.full((batch * 16 * segments * 128 + 32,), SENT, dtype=torch.float32, device="cuda")
    mstore = torch.full((batch * 16 * segments + 32,), SENT, dtype=torch.float32, device="cuda")
    lstore = torch.full((batch * 16 * segments + 32,), SENT, dtype=torch.float32, device="cuda")
    partial = pstore[16:-16].view(batch, 16, segments, 128)
    maximum = mstore[16:-16].view(batch, 16, segments)
    summation = lstore[16:-16].view(batch, 16, segments)
    output_storage = torch.full((batch * 16 * 128 + 32,), 768.0, dtype=torch.bfloat16, device="cuda")
    output = output_storage[16:].as_strided((batch, 16, 128), (2048, 128, 1))
    return dict(partial=partial, maximum=maximum, summation=summation,
                pstore=pstore, mstore=mstore, lstore=lstore,
                output=output, output_storage=output_storage)

def launch_producer(fn, x, z, stream):
    fn(ptr(x["q"]), ptr(x["key"]), ptr(x["scale"]), ptr(x["value"]),
       ptr(x["lengths"]), ptr(x["table"]), x["batch"], ctypes.c_float(SCALE),
       x["table"].stride(0), x["q"].stride(0), x["q"].stride(1),
       z["partial"].stride(0), z["partial"].stride(1), z["partial"].stride(2),
       z["maximum"].stride(0), z["maximum"].stride(1), ptr(z["partial"]),
       ptr(z["maximum"]), ptr(z["summation"]), ctypes.c_void_p(int(stream.cuda_stream)))

def launch_reducer(reducer, x, z, stream):
    n, s = x["batch"], x["segments"]
    reducer[(n, 16)](
        output_ptr=z["output"], segm_output_ptr=z["partial"], segm_max_ptr=z["maximum"],
        segm_expsum_ptr=z["summation"], seq_lens_ptr=x["lengths"],
        segment_stride_token=z["partial"].stride(0), segment_stride_head=z["partial"].stride(1),
        segment_stride_segment=z["partial"].stride(2), segment_stride_dim=z["partial"].stride(3),
        max_stride_token=z["maximum"].stride(0), max_stride_head=z["maximum"].stride(1),
        max_stride_segment=z["maximum"].stride(2), output_stride_token=z["output"].stride(0),
        output_stride_head=z["output"].stride(1), page_size=16, num_segments=s, HEAD_SIZE=128,
        num_warps=1, num_stages=1)

def full_call(torch, reducer, fn, x, z, stream):
    with torch.cuda.stream(stream):
        launch_producer(fn, x, z, stream)
        launch_reducer(reducer, x, z, stream)

def same_outputs(torch, a, b):
    names = ("partial", "maximum", "summation", "output", "output_storage",
             "pstore", "mstore", "lstore")
    mismatch = [k for k in names if not torch.equal(a[k], b[k])]
    if mismatch:
        raise AssertionError(f"A/B output mismatch: {mismatch}")

def timed(torch, reducer, funcs, x, stream, repeats=16):
    results = []
    for order in (("A", "B", "B", "A"), ("B", "A", "A", "B")):
        z = {arm: scratch(torch, x["batch"], x["segments"]) for arm in ("A", "B")}
        stream.wait_stream(torch.cuda.current_stream())
        for _ in range(3):
            for arm in order:
                full_call(torch, reducer, funcs[arm], x, z[arm], stream)
        stream.synchronize()
        for arm in order:
            start, stop = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
            wall0 = time.perf_counter()
            start.record(stream)
            for _ in range(repeats):
                full_call(torch, reducer, funcs[arm], x, z[arm], stream)
            stop.record(stream); stop.synchronize()
            wall = time.perf_counter() - wall0
            results.append(dict(order=list(order), arm=arm, repeats=repeats,
                                raw_event_ms=start.elapsed_time(stop), event_ms_per_call=start.elapsed_time(stop)/repeats,
                                wall_seconds=wall, wall_ms_per_call=wall*1000/repeats))
    return results

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gpu", action="store_true")
    p.add_argument("--root-owned-exclusive", action="store_true")
    p.add_argument("--main-root", type=Path)
    p.add_argument("--compiled", type=Path, help="pinned build-summary.json beside the two compiled SOs")
    p.add_argument("--library-a", type=Path)
    p.add_argument("--library-b", type=Path)
    p.add_argument("--build-summary", type=Path, help="required with explicit --library-a/--library-b")
    p.add_argument("--cudart", type=Path, default=Path("/usr/local/corex/lib64/libcudart.so"))
    p.add_argument("--out", type=Path)
    p.add_argument("--seed", type=int, default=20261029)
    a = p.parse_args()
    if not a.gpu:
        if any((a.compiled, a.library_a, a.library_b, a.build_summary, a.out, a.root_owned_exclusive)):
            p.error("Device arguments require --gpu")
        print(json.dumps(dict(readonly_CPU_default=True, gpu_executed=False,
                              component_only=True, original_reducer="pinned biv150_gqa_decode::_reduce_partials"), indent=2))
        return 0
    if not a.root_owned_exclusive or not a.out:
        p.error("Root must provide exclusive device ownership and output")
    if a.compiled and (a.library_a or a.library_b or a.build_summary):
        p.error("Use either --compiled or --build-summary with explicit libraries")
    if a.compiled:
        summary_path = a.compiled.resolve()
        if not summary_path.is_file(): p.error("--compiled must name build-summary.json")
        build_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        library_paths = {arm: summary_path.parent / build_summary["arms"][arm]["library"] for arm in ("A", "B")}
    else:
        if not (a.library_a and a.library_b and a.build_summary):
            p.error("Provide --compiled, or both explicit libraries plus --build-summary")
        summary_path = a.build_summary.resolve()
        build_summary = json.loads(summary_path.read_text(encoding="utf-8"))
        library_paths = {"A": a.library_a.resolve(), "B": a.library_b.resolve()}
    if a.main_root is None or not a.main_root.is_absolute() or not a.out.is_absolute() or a.out.exists():
        p.error("Use absolute main root and fresh absolute output")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    import torch
    import triton
    reducer, reducer_path, reducer_function_sha, reducer_module_path = load_reducer(a.main_root, a.out.parent)
    if not a.cudart.is_file(): raise FileNotFoundError(f"CoreX runtime missing: {a.cudart}")
    cudart = ctypes.CDLL(str(a.cudart.resolve()), mode=ctypes.RTLD_GLOBAL)
    if not build_summary.get("completed") or not build_summary.get("compile_only") or build_summary.get("gpu_executed"):
        raise RuntimeError("compiled manifest is not a successful compile-only build")
    for path in library_paths.values():
        if not path.is_file(): raise FileNotFoundError(path)
    for arm, path in library_paths.items():
        row = build_summary["arms"][arm]
        if sha(path) != row["library_sha256"]:
            raise RuntimeError(f"compiled library SHA mismatch for {arm}")
        if path.name != row["library"]:
            raise RuntimeError(f"compiled library name mismatch for {arm}")
        source_pin = json.loads((HERE / "source-manifest.json").read_text(encoding="utf-8"))["arms"][arm]["source_sha256"]
        if row["source_sha256"] != source_pin:
            raise RuntimeError(f"compiled source identity mismatch for {arm}")
    result = dict(component_only=True, service_qualification=False, model_accuracy=False,
                  official_performance=False, reducer_path=str(reducer_path), reducer_sha256=sha(reducer_path),
                  reducer_function_sha256_after_universal_newlines=reducer_function_sha,
                  reducer_module_path=str(reducer_module_path), reducer_module_sha256=sha(reducer_module_path),
                  reducer_load="AST-extracted original _reduce_partials only; production install/wrapper not imported",
                  cudart_path=str(a.cudart.resolve()), cudart_sha256=sha(a.cudart.resolve()),
                  build_summary_path=str(summary_path), build_summary_sha256=sha(summary_path),
                  build_summary=build_summary,
                  source_manifest_sha256=sha(HERE / "source-manifest.json"),
                  libs={x: dict(path=str(pth.resolve()), sha256=sha(pth.resolve())) for x,pth in library_paths.items()},
                  env=dict(torch=torch.__version__, triton=triton.__version__, device=torch.cuda.get_device_name(),
                           current_stream=int(torch.cuda.current_stream().cuda_stream)), cases=[])
    result["runtime_command"] = sys.argv
    result["python"] = sys.version
    for batch, segments, seqlen in SHAPES:
        for qstride in Q_STRIDES:
            x = allocate_inputs(torch, batch, segments, seqlen, qstride, a.seed + batch + qstride)
            # One mixed boundary batch covers empty, short, partial-page and
            # segment-tail handling without expanding the shape matrix.
            edges = [0, 1, 15, 17, min(257, seqlen), seqlen - 1]
            for i, length in enumerate(edges):
                x["lengths"][i] = length
            # Exact active arena snapshot and Q/table/length snapshots check input immutability.
            before = {k: x[k].clone() for k in ("q", "storage", "lengths", "table")}
            funcs = {arm: bind(library_paths[arm], arm, segments)[1] for arm in ("A", "B")}
            z = {arm: scratch(torch, batch, segments) for arm in ("A", "B")}
            stream = torch.cuda.Stream()
            stream.wait_stream(torch.cuda.current_stream())
            for arm in ("A", "B"):
                full_call(torch, reducer, funcs[arm], x, z[arm], stream)
            stream.synchronize()
            same_outputs(torch, z["A"], z["B"])
            for arm in ("A", "B"):
                zz = z[arm]
                if not (bool(torch.all(zz["output_storage"][:16] == 768)) and bool(torch.all(zz["output_storage"][-16:] == 768))):
                    raise AssertionError("final output guard changed")
                if not all(bool(torch.all(zz[k][:16] == SENT)) and bool(torch.all(zz[k][-16:] == SENT)) for k in ("pstore", "mstore", "lstore")):
                    raise AssertionError("scratch output guard changed")
            unchanged = {k: bool(torch.equal(x[k], v)) for k,v in before.items()}
            if not all(unchanged.values()): raise AssertionError(f"input modified: {unchanged}")
            # Graph replay with changed Q proves the captured producer/reducer pair uses live inputs.
            graph_outputs, graphs = {}, {}
            for arm in ("A", "B"):
                graph_outputs[arm] = scratch(torch, batch, segments)
                graphs[arm] = torch.cuda.CUDAGraph()
            stream.wait_stream(torch.cuda.current_stream())
            for arm in ("A", "B"):
                with torch.cuda.graph(graphs[arm], stream=stream):
                    full_call(torch, reducer, funcs[arm], x, graph_outputs[arm], stream)
            with torch.cuda.stream(stream): x["q"].add_(2.0)
            stream.synchronize()
            with torch.cuda.stream(stream):
                for arm in ("A", "B"): graphs[arm].replay()
            stream.synchronize()
            same_outputs(torch, graph_outputs["A"], graph_outputs["B"])
            if torch.equal(graph_outputs["A"]["output"], z["A"]["output"]):
                raise AssertionError("changed Q was not observed by graph replay")
            with torch.cuda.stream(stream):
                x["q"].copy_(before["q"])
                x["lengths"].fill_(seqlen)
            stream.synchronize()
            fullz = {arm: scratch(torch, batch, segments) for arm in ("A", "B")}
            stream.wait_stream(torch.cuda.current_stream())
            for arm in ("A", "B"):
                full_call(torch, reducer, funcs[arm], x, fullz[arm], stream)
            stream.synchronize()
            same_outputs(torch, fullz["A"], fullz["B"])
            record = dict(batch=batch, segments=segments, seqlen=seqlen, q_stride=qstride,
                          active_pages=batch * ((seqlen+15)//16), cache_pages=PAGES,
                          active_cache_bytes=batch*((seqlen+15)//16)*PAGE_BYTES,
                          numeric_bitwise_all_arrays=True, full_length_bitwise_all_arrays=True,
                          input_immutability=unchanged,
                          graph_changed_q_bitwise=True,
                          timings=timed(torch, reducer, funcs, x, torch.cuda.Stream()))
            result["cases"].append(record)
            print(json.dumps(record, sort_keys=True), flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
