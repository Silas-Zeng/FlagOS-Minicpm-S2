#!/usr/bin/env python3
"""Run one isolated NativeK8 SME arm through the unchanged official gate."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys

MAIN = "899ce77470b0b539aebc108fd122f668c2d5894d"
DRIVER_SHA = "79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579"
COMMON_SHA = "35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54"
BENCHMARK_SHA = "0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565"
OVERLAY_FILES = (
    "vllm_fl/patches/biv150_konly_encoded_native.py",
    "vllm_fl/compile_semantics.py",
    "vllm_fl/patches/biv150_konly_encoded_sources.json",
)
REQUIRED_DB = ("TunedConfig_iluvatar_triton_3_2.db", "TunedConfig_iluvatar_triton_3_6.db")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def check_file_entry(root, rel, entry):
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise RuntimeError("unsafe base-manifest path: " + rel)
    path = root / rel
    if entry.get("type") == "symlink":
        if not path.is_symlink() or os.readlink(path) != entry.get("target"):
            raise RuntimeError("source archive symlink mismatch: " + rel)
        if root not in path.resolve().parents:
            raise RuntimeError("source archive symlink escapes root: " + rel)
        return
    if entry.get("type") != "file" or path.is_symlink() or not path.is_file():
        raise RuntimeError("source archive member missing/type mismatch: " + rel)
    if path.stat().st_size != entry["bytes"] or sha(path) != entry["sha256"]:
        raise RuntimeError("source archive member SHA/size mismatch: " + rel)
    if bool(path.stat().st_mode & 0o111) != bool(int(entry["mode"], 8) & 0o111):
        raise RuntimeError("source archive executable bit mismatch: " + rel)


def verify_assets(a):
    source, archive = a.source.resolve(), a.source_archive.resolve()
    base_path, overlay_path = a.base_manifest.resolve(), a.overlay_manifest.resolve()
    base = json.loads(base_path.read_text(encoding="utf-8"))
    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
    common = json.loads(a.common_assets.read_text(encoding="utf-8"))
    if base.get("source_commit") != MAIN or overlay.get("declared_source_commit") != MAIN:
        raise RuntimeError("source manifests must identify main899")
    if sha(archive) != base.get("archive_sha256") or archive.stat().st_size != base.get("archive_bytes"):
        raise RuntimeError("main899 Git archive identity differs from manifest")
    if overlay.get("role") != a.arm or overlay.get("format") != "cjj-konly-rn32-rne-v2":
        raise RuntimeError("overlay role/format mismatch")
    if overlay.get("library_sha256") != common["libraries"][a.arm]["sha256"]:
        raise RuntimeError("dispatcher SO pin differs from common assets")
    for rel in OVERLAY_FILES:
        if overlay["source_inputs"].get(rel) != base["files"].get(rel, {}).get("sha256"):
            raise RuntimeError("overlay was not generated from the pinned Git archive: " + rel)
        entry = overlay["overlay_files"][rel]
        if sha(source / rel) != entry["sha256"] or (source / rel).stat().st_size != entry["bytes"]:
            raise RuntimeError("materialized overlay bytes differ: " + rel)
        if bool((source / rel).stat().st_mode & 0o111) != bool(int(base["files"][rel]["mode"], 8) & 0o111):
            raise RuntimeError("overlay changed original executable bit: " + rel)
    for rel, entry in base["files"].items():
        if rel not in OVERLAY_FILES:
            check_file_entry(source, rel, entry)
    if sha(a.native_library) != overlay["library_sha256"]:
        raise RuntimeError("selected dispatcher library SHA mismatch")
    for key, supplied in (("w8a8", a.gate_library), ("stock_gqa", a.native_gqa_library)):
        pin = common["libraries"][key]
        if supplied.resolve() != Path(pin["path"]).resolve() or sha(supplied) != pin["sha256"]:
            raise RuntimeError("common library path/SHA differs for " + key)
    dbs = common["database"]
    for name in REQUIRED_DB:
        entry = dbs[name]
        path = a.tuning_snapshot / name
        if sha(path) != entry["sha256"] or path.stat().st_size != entry["bytes"]:
            raise RuntimeError("frozen tuning DB differs: " + name)
    selected = a.tuning_snapshot / a.database_name
    if a.database_name not in REQUIRED_DB or not selected.is_file():
        raise RuntimeError("database name must select a frozen 3_2 or 3_6 snapshot")
    if sha(a.native_library) != common["libraries"][a.arm]["sha256"]:
        raise RuntimeError("dispatcher library does not match selected arm")
    if a.run_dir.exists():
        raise RuntimeError("official run directory must be new")
    root = Path("/workspace/experiments/minicpm-s2")
    if a.run_dir.resolve().parent != (root / "official") or source.parent != (root / "code"):
        raise RuntimeError("official driver requires source under ROOT/code and run under ROOT/official")
    return base, overlay, common, selected


def load_official_driver(driver, common_dir, benchmark):
    if sha(driver) != DRIVER_SHA or sha(common_dir / "run_accuracy_gate.py") != COMMON_SHA:
        raise RuntimeError("official gate/common source SHA mismatch")
    if sha(benchmark) != BENCHMARK_SHA:
        raise RuntimeError("official benchmark source SHA mismatch")
    sys.path.insert(0, str(common_dir.resolve()))
    sys.modules.pop("run_accuracy_gate", None)
    spec = importlib.util.spec_from_file_location("native_k8_sme_official_gate", driver)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    if Path(module.common.__file__).resolve() != (common_dir / "run_accuracy_gate.py").resolve():
        raise RuntimeError("official driver imported an unexpected common helper")
    if Path(module.BENCHMARK).resolve() != benchmark.resolve():
        raise RuntimeError("official benchmark path differs from its frozen command")
    if module.common.ROOT != Path("/workspace/experiments/minicpm-s2"):
        raise RuntimeError("official driver ROOT differs")
    module.check_benchmark_source()
    return module


def verify_installed_k8(log, overlay):
    marker = "BIV150_KONLY_NATIVE_DECODE_INSTALL "
    installs = [json.loads(line.split(marker, 1)[1]) for line in log.splitlines() if marker in line]
    wanted_operator = overlay["namespace"] + "::produce"
    if not installs:
        raise RuntimeError("NativeK8 adapter install record missing before official benchmark")
    for value in installs:
        lib = value.get("library", {})
        if (value.get("installed") is not True or value.get("enabled") is not True
                or value.get("loaded_library_confirmed") is not True
                or value.get("runtime_compile") is not False
                or lib.get("sha256") != overlay["library_sha256"]
                or value.get("operator") != wanted_operator
                or value.get("physical_page_bytes") != 16384):
            raise RuntimeError("installed NativeK8 adapter does not match selected A/B overlay")
    return installs


def inspect_runtime(log, overlay, prefill):
    installs = verify_installed_k8(log, overlay)
    selected, captured = [], []
    for marker, target in (("BIV150_KONLY_NATIVE_DECODE_SELECTED ", selected),
                           ("BIV150_KONLY_NATIVE_DECODE_CAPTURED ", captured)):
        for line in log.splitlines():
            if marker in line:
                target.append(json.loads(line.split(marker, 1)[1]))
    events = selected + captured
    rows, segments = (64, 2) if prefill == 4096 else (32, 4)
    matched = [event for event in events if event.get("shape") == rows and event.get("segments") == segments
               and event.get("library", {}).get("sha256") == overlay["library_sha256"]
               and event.get("operator") == overlay["namespace"] + "::produce"]
    if not matched:
        raise RuntimeError("official case has no selected-arm NativeK8 host/capture observation")
    return {"installations": installs, "host_or_capture_events": matched,
            "request_frequency_proven": False, "graph_replay_count_proven": False}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--prepare-only", action="store_true")
    p.add_argument("--run", action="store_true", help="explicitly invoke the official four-run gate")
    p.add_argument("--arm", choices=("A", "B"), required=True)
    p.add_argument("--prefill", choices=("4096", "16384"), required=True)
    for arg in ("source", "source-archive", "base-manifest", "overlay-manifest", "common-assets",
                "tuning-snapshot", "native-library", "gate-library", "native-gqa-library",
                "driver", "common-dir", "benchmark", "run-dir"):
        p.add_argument("--" + arg, required=True, type=Path)
    p.add_argument("--database-name", choices=REQUIRED_DB, required=True)
    a = p.parse_args()
    base, overlay, common_assets, selected_db = verify_assets(a)
    driver = load_official_driver(a.driver, a.common_dir, a.benchmark)
    cases = [[int(a.prefill), 1024, 64, 256 if a.prefill == "4096" else 128]]
    if a.prepare_only:
        print(json.dumps({"prepare_only": True, "gpu_executed": False,
            "source_commit": MAIN, "source_tree": base["source_tree"],
            "arm": a.arm, "library_sha256": overlay["library_sha256"],
            "namespace": overlay["namespace"], "official_driver_sha256": DRIVER_SHA,
            "official_common_sha256": COMMON_SHA, "official_benchmark_sha256": BENCHMARK_SHA,
            "official_cases": cases, "runs_per_case": 4, "skip_first": 1,
            "database_sha256": sha(selected_db)}, indent=2))
        return
    if not a.run:
        raise SystemExit("use --prepare-only or explicitly pass --run")

    cache_root = a.run_dir.parent / (a.run_dir.name + ".cache")
    if cache_root.exists():
        raise RuntimeError("per-arm isolated cache directory already exists")
    cache = cache_root / "config_cache"
    cache.mkdir(parents=True)
    cache_roots = {
        "triton": cache_root / "triton-cache",
        "inductor": cache_root / "inductor-cache",
        "vllm": cache_root / "vllm-cache",
    }
    for path in cache_roots.values():
        path.mkdir(parents=True)
    db_before = {}
    for name in REQUIRED_DB:
        source_db = a.tuning_snapshot / name
        target_db = cache / name
        shutil.copy2(source_db, target_db)
        if sha(source_db) != sha(target_db):
            raise RuntimeError("isolated tuning DB copy mismatch: " + name)
        db_before[name] = sha(target_db)
    selected_private_db = cache / a.database_name

    original_child_env = driver.common.child_environment
    def isolated_child_environment(source):
        env = original_child_env(source)
        # The base helper rejects inherited cache overrides. Add only our private per-arm paths afterwards.
        env.update(FLAGGEMS_CACHE_DIR=str(cache_root),
                   TRITON_CACHE_DIR=str(cache_roots["triton"]),
                   TORCHINDUCTOR_CACHE_DIR=str(cache_roots["inductor"]),
                   VLLM_CACHE_ROOT=str(cache_roots["vllm"]),
                   BIV150_NATIVE_W8A8_LIBRARY=str(a.gate_library.resolve()),
                   BIV150_NATIVE_GQA_LIBRARY=str(a.native_gqa_library.resolve()),
                   VLLM_FL_BIV150_KONLY_ENCODED_SERVICE="1",
                   VLLM_FL_BIV150_KONLY_NATIVE_DECODE="1",
                   VLLM_FL_BIV150_KONLY_NATIVE_LIBRARY=str(a.native_library.resolve()),
                   VLLM_FL_BIV150_KONLY_NATIVE_LIBRARY_SHA256=overlay["library_sha256"],
                   VLLM_FL_BIV150_KONLY_MIXED_NATIVE="0",
                   VLLM_FL_BIV150_KONLY_COMPACT_SERVICE="0")
        return env
    original_wait_ready = driver.common.wait_ready
    def checked_wait_ready(server, log_marker, run):
        original_wait_ready(server, log_marker, run)
        text = (run / "server.log").read_text(errors="replace")
        verify_installed_k8(text, overlay)

    driver.common.child_environment = isolated_child_environment
    driver.common.wait_ready = checked_wait_ready
    driver.TEST_CASES = json.dumps(cases, separators=(",", ":"))
    argv = [str(a.run_dir), "--source-dir", str(a.source), "--database", str(selected_private_db),
            "--require-log-marker", "BIV150_KONLY_NATIVE_DECODE_INSTALL"]
    status = None
    try:
        status = driver.main(argv)
    finally:
        driver.common.child_environment = original_child_env
        driver.common.wait_ready = original_wait_ready
    result = {"arm": a.arm, "prefill": int(a.prefill), "cases": cases,
              "driver_exit_code": status, "overlay_manifest_sha256": sha(a.overlay_manifest),
              "base_manifest_sha256": sha(a.base_manifest), "common_assets_sha256": sha(a.common_assets),
              "source_archive_sha256": base["archive_sha256"], "database_before": db_before,
              "database_after": {name: sha(cache / name) for name in REQUIRED_DB},
              "isolated_cache_root": str(cache_root), "official_run_dir": str(a.run_dir),
              "official_driver_is_unchanged": True, "formal_model_qualification": False}
    try:
        if not a.run_dir.is_dir():
            raise RuntimeError("official gate did not produce a run directory")
        log_path = a.run_dir / "server.log"
        raw = log_path.read_text(errors="replace") if log_path.is_file() else ""
        result["native_k8_runtime"] = inspect_runtime(raw, overlay, int(a.prefill))
        driver_result_path = a.run_dir / "result.json"
        driver_result = (json.loads(driver_result_path.read_text(encoding="utf-8"))
                         if driver_result_path.is_file() else None)
        result["official_driver_result"] = driver_result
        if (status != 0 or not isinstance(driver_result, dict)
                or driver_result.get("exit_code") != 0
                or not driver_result.get("benchmark_completed")):
            raise RuntimeError("official four-run gate failed; preserve original run evidence")
        result["official_four_run_validation"] = driver.validate_outputs(a.run_dir)
        result["completed"] = True
        write_json(a.run_dir / "native-k8-sme-owner-result.json", result)
        return 0
    except BaseException as error:
        result["completed"] = False
        result["owner_error"] = repr(error)
        if a.run_dir.is_dir():
            write_json(a.run_dir / "native-k8-sme-owner-result.json", result)
        raise


if __name__ == "__main__":
    raise SystemExit(main())
