"""一次纯 CPU 方向/几何检查；不构造 Tensor/Bridge、不编译 SDK、不执行原服务门。"""
import ctypes
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def check():
    old_path = ROOT / "patches/framework/candidates/biv150_kv_pitched_copy.py"
    old_cpp_path = ROOT / "patches/framework/candidates/biv150_kv_pitched_bridge.cpp"
    helper = HERE / "biv150_kv_pitched_restore.py"
    cpp = HERE / "biv150_kv_pitched_restore_bridge.cpp"
    log = ROOT / "experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/server.log"
    assert sha(log) == "58cf312b903604c8c6200fb41d44b34c3175a8988d2b4271201047b9cf50fa50"
    assert sha(old_path) == "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"
    assert sha(old_cpp_path) == "0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44"
    assert "torch" not in sys.modules
    original_cdll = ctypes.CDLL
    def forbidden(*args, **kwargs):
        raise AssertionError("CPU 检查不得载入库")
    ctypes.CDLL = forbidden
    try:
        runtime = load("restore_check_save_runtime", old_path)
        restore = load("restore_check_helper", helper)
        events = []
        for line_number, line in enumerate(log.read_text(encoding="utf-8").splitlines(), 1):
            if "BIV150_KV_PROTOCOL {" in line:
                event = json.loads(line.split("BIV150_KV_PROTOCOL ", 1)[1])
                if event["event"] == "RPC_ACK" and event["command"]["kind"] == "RESTORE_FULL":
                    events.append((line_number, event))
        assert len(events) == 1
        line_number, event = events[0]
        pages = event["command"]["pages"]
        pages_sha = hashlib.sha256(json.dumps(pages, separators=(",", ":")).encode()).hexdigest()
        assert pages_sha == "96df643679671a337327a223fda9a0bb58104d72958a93998ce194a04dffa227"
        plan = restore.make_restore_plan(pages, max(pages) + 1, save_runtime=runtime)
        pieces, fallbacks = restore.segments_for_pitch(plan, max_pitch=2147483647)
        expand = lambda parts: tuple(s.physical_start + j * s.physical_step for s in parts for j in range(s.height))
        logical = lambda parts: tuple(s.logical_start + j for s in parts for j in range(s.height))
        assert expand(pieces) == tuple(pages) and logical(pieces) == tuple(range(len(pages)))
        pitched = sum(s.height > 1 and s.physical_step > 1 for s in pieces)
        linear = len(pieces) - pitched
        assert (len(pages), plan.original_c95f_runs, len(pieces), linear, pitched, fallbacks) == (1043, 66, 14, 4, 10, 0)
        maximum_pitch = max(s.physical_step * 16384 for s in pieces if s.height > 1)
        assert maximum_pitch == 33570816
        split, split_fallbacks = restore.segments_for_pitch(plan, max_pitch=16384)
        assert expand(split) == tuple(pages) and logical(split) == tuple(range(len(pages)))
        assert len(split) == 66 and split_fallbacks == 10
        assert all(s.physical_step == 1 or s.height == 1 for s in split)
        # 唯一新增方向条件：不排序下降/不连续目的页，越界/重复仍由原严格几何拒绝。
        unusual = restore.make_restore_plan([9, 7, 8, 2], 10, save_runtime=runtime)
        assert expand(restore.segments_for_pitch(unusual, max_pitch=16384)[0]) == (9, 7, 8, 2)
        rejected = 0
        for bad in ([0, 0], [0, -1], [0, 10]):
            try:
                restore.make_restore_plan(bad, 10, save_runtime=runtime)
            except ValueError:
                rejected += 1
        assert rejected == 3 and "torch" not in sys.modules
    finally:
        ctypes.CDLL = original_cdll
    original, new = old_cpp_path.read_bytes(), cpp.read_bytes()
    assert new.startswith(original)
    save_body = original[original.index(b'extern "C" int biv150_pitched_save_batch('):]
    restore_body = new[new.index(b'extern "C" int biv150_pitched_restore_batch('):]
    # 函数体只重命名符号、方向和完成说明；原 D2H 字节前缀完全保持。
    expected = save_body.replace(b"biv150_pitched_save_batch", b"biv150_pitched_restore_batch").replace(
        b"cudaMemcpyDeviceToHost", b"cudaMemcpyHostToDevice").replace(
        "// 仅提交成功；调用者必须同stream真event完成后才读host/释放任何引用。".encode(),
        "// 仅H2D提交成功；同stream真event完成后才可发布目的KV/释放任何引用。".encode())
    assert restore_body == expected
    return {"status": "pass_cpu_geometry_only", "source_log": str(log.relative_to(ROOT)),
        "source_log_sha256": sha(log), "ack_line": line_number, "pages_sha256": pages_sha,
        "helper_sha256": sha(helper), "cpp_sha256": sha(cpp), "old_runtime_sha256": sha(old_path),
        "old_cpp_sha256": sha(old_cpp_path), "old_D2H_bytes_prefix_unchanged": True,
        "destination_pages": len(pages), "original_runs": 66, "segments": [s.__dict__ for s in pieces],
        "per_layer": {"linear_calls": linear, "pitched_calls": pitched, "copy_calls": len(pieces)},
        "normal42": {"old_calls": 2772, "new_calls": 588, "submitted_bytes": len(pages) * 16384 * 42},
        "max_destination_pitch_bytes": maximum_pitch,
        "low_pitch_control": {"max_pitch": 16384, "linear_calls": len(split), "fallback_segments": split_fallbacks},
        "scope": "未构造 Tensor/Bridge、未载库/编译/调用 SDK；非设备字节、事件、异步失败或收益验证"}


if __name__ == "__main__":
    result = check()
    result["check_sha256"] = sha(Path(__file__))
    output = HERE / "cpu-geometry-check.json"
    with output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "output": str(output)}, ensure_ascii=False))
