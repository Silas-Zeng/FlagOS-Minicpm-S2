"""独立完整R等差SAVE候选worker；只改5d9a的SAVE，显式RPC才启用。

原页所有权/CPU输出消费由Core适配器负责。本模块只拥有单victim pinned
host与copy强引用；只有真实device/event完成后返回completed ACK。
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import Path
import sys
from threading import Lock

LAYERS, PAGE_BYTES, TOKEN_BYTES = 42, 16384, 43008
PAYLOAD_CAP, HEADROOM_GUARD = 1 << 30, 1 << 30
VERIFY_ENV = "BIV150_KV_VERIFY_RESTORE"
EXPECTED_SOURCES = {
    "vllm_fl.worker.worker": "a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24",
    "vllm_fl.worker.model_runner": "cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663",
    "vllm.v1.worker.worker_base": "7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe",
    "vllm_fl.patches.biv150_kv_page_copy": "c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c",
}
_LOCK = Lock()
_SLOT = None
_LAST_SERIAL = {}
_VERIFIED_ONCE = False


def _integer(value, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError("需要范围内Python整数")
    return value


def _command(value):
    if type(value) is not dict:
        raise TypeError("command必须是普通dict")
    key = value.get("key")
    if (type(key) not in (list, tuple) or len(key) != 4
            or any(type(x) is not str or not x for x in key[:2])):
        raise ValueError("key需要session/request/incarnation/attempt")
    _integer(key[2], 1)
    _integer(key[3], 1)
    kind = value.get("kind")
    if kind not in ("SAVE", "ZERO", "RESTORE", "RESTORE_FULL", "DROP"):
        raise ValueError("未知KV命令")
    serial = _integer(value.get("operation_serial"), 1)
    prefix = _integer(value.get("prefix_tokens"), 16)
    nbytes = _integer(value.get("nbytes"))
    if (prefix % 16 or prefix * TOKEN_BYTES > PAYLOAD_CAP
            or (nbytes != 0 if kind == "DROP" else nbytes != prefix * TOKEN_BYTES)):
        raise ValueError("prefix须完整16token页且payload不超过1GiB")
    pages = value.get("pages")
    if type(pages) not in (list, tuple):
        raise ValueError("pages须为普通列表")
    pages = tuple(pages)
    if kind == "DROP" and pages:
        raise ValueError("DROP不传输页面")
    if ((kind != "DROP" or pages) and len(pages) != prefix // 16
            or any(type(x) is not int or x < 1 for x in pages)
            or len(set(pages)) != len(pages)):
        raise ValueError("只接受非null、唯一、完整的物理prefix页")
    return {"key": tuple(key), "kind": kind, "operation_serial": serial,
            "prefix_tokens": prefix, "pages": pages, "nbytes": nbytes}


def _memory_headroom():
    for usage, limit in (("/sys/fs/cgroup/memory/memory.usage_in_bytes", "/sys/fs/cgroup/memory/memory.limit_in_bytes"),
                         ("/sys/fs/cgroup/memory.current", "/sys/fs/cgroup/memory.max")):
        try:
            used, cap = int(Path(usage).read_text()), int(Path(limit).read_text())
            if cap <= 0 or used < 0 or used > cap:
                raise ValueError("无有效cgroup硬限额")
            return {"used_bytes": used, "limit_bytes": cap, "headroom_bytes": cap - used}
        except FileNotFoundError:
            continue
    raise RuntimeError("未观测可用cgroup硬限额，拒绝分配pinned buffer")


def _budget(payload, verify_bytes, memory):
    if payload > PAYLOAD_CAP or memory["headroom_bytes"] < payload + verify_bytes + HEADROOM_GUARD:
        raise BufferError("payload/诊断额外buffer/1GiB guard不足")


def _context(wrapper):
    modules = {name: importlib.import_module(name) for name in EXPECTED_SOURCES}
    for name, expected in EXPECTED_SOURCES.items():
        if hashlib.sha256(Path(modules[name].__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("未经审阅的worker/copy源：" + name)
    if type(wrapper) is not modules["vllm.v1.worker.worker_base"].WorkerWrapperBase:
        raise TypeError("仅actual WorkerWrapperBase")
    worker = vars(wrapper).get("worker")
    if type(worker) is not modules["vllm_fl.worker.worker"].WorkerFL:
        raise TypeError("仅actual WorkerFL")
    runner = vars(worker).get("model_runner")
    if type(runner) is not modules["vllm_fl.worker.model_runner"].ModelRunnerFL:
        raise TypeError("仅actual ModelRunnerFL")
    config = worker.vllm_config
    model, parallel = config.model_config, config.parallel_config
    text = model.hf_text_config
    platform = importlib.import_module("vllm.platforms").current_platform
    torch = importlib.import_module("torch")
    if not (
        getattr(platform, "vendor_name", "") == "iluvatar"
        and Path(str(model.model).rstrip("/\\")).name == "MiniCPM5-2B"
        and str(model.dtype) == "torch.bfloat16" and model.quantization is None
        and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads, text.num_key_value_heads) == (2048, 42, 16, 2)
        and all(getattr(parallel, name, None) == 1 for name in (
            "tensor_parallel_size", "pipeline_parallel_size", "data_parallel_size", "decode_context_parallel_size"))
        and parallel.use_ubatching is False and config.speculative_config is None
        and config.lora_config is None and config.kv_transfer_config is None and config.ec_transfer_config is None
        and not runner.shared_kv_cache_layers and runner.cross_layers_kv_cache is None
        and runner._kernel_block_sizes == [16] and torch.cuda.current_device() == 0
    ):
        raise RuntimeError("未经审阅的worker scope")
    properties = torch.cuda.get_device_properties(0)
    if "BI-V150" not in properties.name or properties.multi_processor_count != 16:
        raise RuntimeError("需要已测BI-V150 16SM实例")
    caches = runner.kv_caches
    if type(caches) is not list or len(caches) != LAYERS:
        raise RuntimeError("仅actual42层KV list")
    pool = runner.kv_cache_config.num_blocks
    _integer(pool, 2)
    signatures, raw = [], []
    for tensor in caches:
        if (type(tensor) is not torch.Tensor or str(tensor.dtype) != "torch.bfloat16"
                or str(tensor.device) != "cuda:0" or tuple(tensor.shape) != (pool, 2, 16, 2, 128)
                or tuple(tensor.stride()) != (8192, 4096, 256, 128, 1)
                or tensor.storage_offset() != 0 or not tensor.is_contiguous()):
            raise RuntimeError("仅已观测normal42连续NHD布局")
        storage = tensor.untyped_storage()
        signature = (int(storage.data_ptr()), int(storage.nbytes()))
        if signature[1] != pool * PAGE_BYTES:
            raise RuntimeError("KV storage边界不符")
        signatures.append(signature)
        raw.append(tensor.view(torch.uint8).view(pool, PAGE_BYTES))
    if len(set(signatures)) != LAYERS:
        raise RuntimeError("不支持packed/shared alias KV")
    return torch, runner, modules["vllm_fl.patches.biv150_kv_page_copy"], raw, tuple(signatures), pool


def _finish(torch, slot):
    event = torch.cuda.Event()
    slot["event"] = event  # 若同步失败仍保持event/host/raw强引用。
    event.record()
    event.synchronize()
    slot["settled"] = True


def _copy(policy, sources, destinations, source_ids, destination_ids):
    plan = policy.make_plan(source_ids, destination_ids, sources[0].shape[0], destinations[0].shape[0], PAGE_BYTES)
    copied = [policy.submit_page_copy(s, d, plan) for s, d in zip(sources, destinations)]
    return {"submitted_bytes": sum(row["submitted_bytes"] for row in copied),
            "copy_calls": sum(row["copy_calls"] for row in copied)}


PITCHED_RUNTIME = "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"
PITCHED_BRIDGE = "9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0"
PITCHED_CUDART = "d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527"


def _pitched_assets(slot):
    """仅首次真实SAVE内晚加载；不改变profile/初始化的KV容量。"""
    runtime_path = Path(__file__).with_name("biv150_kv_pitched_copy.py")
    bridge_path = Path(__file__).with_name("biv150_kv_pitched_bridge.so")
    if (runtime_path.is_symlink() or not runtime_path.is_file()
            or hashlib.sha256(runtime_path.read_bytes()).hexdigest() != PITCHED_RUNTIME):
        raise RuntimeError("未经审阅的等差SAVE runtime")
    runtime = importlib.import_module("vllm_fl.patches.biv150_kv_pitched_copy")
    if Path(runtime.__file__).resolve(strict=True) != runtime_path.resolve(strict=True):
        raise RuntimeError("等差SAVE runtime不在同一隔离source")
    # Bridge固定SO实体/ABI；在任何maxpitch或copy调用前持有动态库。
    bridge = runtime.Bridge(bridge_path, expected_sha256=PITCHED_BRIDGE)
    slot["save_bridge"], slot["save_runtime"] = bridge, runtime
    library_paths = set()
    for line in Path("/proc/self/maps").read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 5)
        if len(fields) == 6 and "libcudart.so" in Path(fields[5]).name:
            library_paths.add(Path(fields[5]).resolve(strict=True))
    libraries = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(library_paths)}
    if len(libraries) != 1 or next(iter(libraries.values())) != PITCHED_CUDART:
        raise RuntimeError("实际加载的Corex libcudart身份不符")
    slot["save_loaded_libcudart"] = libraries
    return runtime, bridge


def _save_pitched(torch, raw, slot, packet, pool):
    runtime, bridge = _pitched_assets(slot)
    slot["save_bridge"] = bridge
    maximum_pitch = bridge.max_pitch(device=0)
    plan = runtime.make_plan(packet["pages"], pool)
    prepared = runtime.prepare_save(raw, slot["host"], plan, max_pitch=maximum_pitch)
    # 不能仅保helper local：部分提交且settle失败时须活到原slot可安全DROP。
    slot["save_prepared"], slot["save_plan"] = prepared, plan
    stream = torch.cuda.current_stream(0)
    slot["save_stream"] = stream
    handle = int(stream.cuda_stream)  # 真实当前流；合法default handle0也原样传递。
    info = bridge.submit(prepared, stream_handle=handle)
    if info["submitted_bytes"] != packet["nbytes"] or info["completion_ack"] is not False:
        raise RuntimeError("等差SAVE提交字节/完成语义不符")
    info = dict(info)
    info["save_submission_completion_ack"] = info.pop("completion_ack")
    info.update(save_implementation="C_batch_positive_stride_full_R", save_layers=LAYERS,
                save_segments_per_layer=len(plan.segments), save_runtime_sha256=PITCHED_RUNTIME,
                save_bridge_sha256=PITCHED_BRIDGE, save_max_pitch_bytes=maximum_pitch,
                save_current_stream_handle=handle)
    return info


# 独立FULL-only草稿：新桥尚无实际SO身份；None必须拒绝，不可部署。
RESTORE_RUNTIME = "a7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c"
RESTORE_BRIDGE = None


def _restore_assets(slot):
    """仅原FULL验证/绑定/fence后晚加载；未审SO绝不自动沿用SAVE桥。"""
    if (type(RESTORE_BRIDGE) is not str or len(RESTORE_BRIDGE) != 64
            or any(c not in "0123456789abcdef" for c in RESTORE_BRIDGE)):
        raise RuntimeError("RESTORE H2D草稿尚无已验SO pin；禁止提交")
    runtime_path = Path(__file__).with_name("biv150_kv_pitched_restore.py")
    bridge_path = Path(__file__).with_name("biv150_kv_pitched_restore_bridge.so")
    if (runtime_path.is_symlink() or not runtime_path.is_file()
            or hashlib.sha256(runtime_path.read_bytes()).hexdigest() != RESTORE_RUNTIME):
        raise RuntimeError("未经审阅的FULL H2D runtime")
    runtime = importlib.import_module("vllm_fl.patches.biv150_kv_pitched_restore")
    if Path(runtime.__file__).resolve(strict=True) != runtime_path.resolve(strict=True):
        raise RuntimeError("FULL H2D runtime不在同一隔离source")
    save_runtime = slot.get("save_runtime")
    save_path = Path(__file__).with_name("biv150_kv_pitched_copy.py")
    if (save_runtime is None or save_path.is_symlink()
            or Path(save_runtime.__file__).resolve(strict=True) != save_path.resolve(strict=True)
            or hashlib.sha256(save_path.read_bytes()).hexdigest() != PITCHED_RUNTIME):
        raise RuntimeError("只复用原SAVE已经持有的同source 818e模块")
    bridge = runtime.RestoreBridge(bridge_path, expected_sha256=RESTORE_BRIDGE, save_runtime=save_runtime)
    # 在maxpitch/prepare/首提交之前就把新库/runtime强持到原slot。
    slot["restore_bridge"], slot["restore_runtime"] = bridge, runtime
    library_paths = set()
    for line in Path("/proc/self/maps").read_text(encoding="utf-8").splitlines():
        fields = line.split(None, 5)
        if len(fields) == 6 and "libcudart.so" in Path(fields[5]).name:
            library_paths.add(Path(fields[5]).resolve(strict=True))
    libraries = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(library_paths)}
    if len(libraries) != 1 or next(iter(libraries.values())) != PITCHED_CUDART:
        raise RuntimeError("FULL H2D实际Corex libcudart身份不符")
    slot["restore_loaded_libcudart"] = libraries
    return runtime, bridge, save_runtime


def _restore_pitched(torch, raw, slot, packet, pool):
    """不接管资格/完成状态，只在原RESTORE_FULL处替换一次H2D提交。"""
    runtime, bridge, save_runtime = _restore_assets(slot)
    maximum_pitch = bridge.max_pitch(device=0)
    plan = runtime.make_restore_plan(packet["pages"], pool, save_runtime=save_runtime)
    slot["restore_plan"] = plan
    prepared = runtime.prepare_restore(slot["host"], raw, plan, max_pitch=maximum_pitch)
    slot["restore_prepared"] = prepared
    stream = torch.cuda.current_stream(0)
    slot["restore_stream"] = stream
    handle = int(stream.cuda_stream)
    # 原rpc except覆盖任何native异常（包括submitted=0），不catch后重试旧COPY。
    info = bridge.submit(prepared, stream_handle=handle)
    if info["submitted_bytes"] != packet["nbytes"] or info["completion_ack"] is not False:
        raise RuntimeError("FULL H2D提交字节/完成语义不符")
    info = dict(info)
    info["restore_submission_completion_ack"] = info.pop("completion_ack")
    info.update(restore_implementation="C_batch_positive_stride_FULL_H2D", restore_layers=LAYERS,
                restore_segments_per_layer=len(plan.segments), restore_runtime_sha256=RESTORE_RUNTIME,
                restore_bridge_sha256=RESTORE_BRIDGE, restore_max_pitch_bytes=maximum_pitch,
                restore_current_stream_handle=handle)
    return info


def _verify_saved_source(torch, policy, raw, slot, packet):
    """仅VERIFY1：源free前用原c95f独立核42层，不额外分配大buffer。"""
    if not slot["verify"]:
        return {"save_verification_performed": False}
    calls = 0
    count = packet["prefix_tokens"] // 16
    buffer = slot["verify_buffer"]  # 原预算的单层buffer继续留给FULL回读。
    for tensor, saved in zip(raw, slot["host"]):
        slot["settled"] = False
        row = _copy(policy, [tensor], [buffer], packet["pages"], range(count))
        calls += row["copy_calls"]
        _finish(torch, slot)
        if not torch.equal(buffer, saved):
            raise RuntimeError("诊断SAVE原source与pinned host全字节不匹配")
    slot["save_verification_passed"] = True
    return {"save_verification_performed": True, "save_verification_passed": True,
            "save_verification_layers": LAYERS, "save_verification_bytes": packet["nbytes"],
            "save_verification_copy_calls": calls}


def _full_restore_plan(torch, policy, slot, raw, pool, packet):
    """首次提交前证明42层raw整页全覆盖；只读描述符，不读KV值。"""
    count = packet["prefix_tokens"] // 16
    host = slot["host"]
    if (type(host) is not list or len(host) != LAYERS or len(raw) != LAYERS
            or packet["nbytes"] != count * PAGE_BYTES * LAYERS
            or "destination_pages" in slot):
        raise RuntimeError("RESTORE_FULL需要未绑定的完整42层host snapshot")
    host_signatures = []
    for saved, target in zip(host, raw):
        if (type(saved) is not torch.Tensor or str(saved.dtype) != "torch.uint8"
                or str(saved.device) != "cpu" or tuple(saved.shape) != (count, PAGE_BYTES)
                or not saved.is_contiguous() or saved.storage_offset() != 0 or not saved.is_pinned()
                or type(target) is not torch.Tensor or str(target.dtype) != "torch.uint8"
                or str(target.device) != "cuda:0" or tuple(target.shape) != (pool, PAGE_BYTES)
                or not target.is_contiguous() or target.storage_offset() != 0):
            raise RuntimeError("RESTORE_FULL仅支持完整pinned uint8页到normal42 raw页")
        storage = saved.untyped_storage()
        signature = (int(storage.data_ptr()), int(storage.nbytes()))
        if signature[1] != count * PAGE_BYTES:
            raise RuntimeError("RESTORE_FULL host storage不是完整页范围")
        host_signatures.append(signature)
    if len(set(host_signatures)) != LAYERS:
        raise RuntimeError("RESTORE_FULL不支持host层间alias")
    plan = policy.make_plan(range(count), packet["pages"], count, pool, PAGE_BYTES)
    if (plan.logical_pages != count or plan.page_bytes != PAGE_BYTES
            or sum(length for _, _, length in plan.runs) != count):
        raise RuntimeError("RESTORE_FULL计划未覆盖每个目标完整页")
    return plan


def _reply(command, successful, completed, *, error=None, **extra):
    slot = _SLOT
    return {**command, "key": list(command["key"]), "pages": list(command["pages"]),
            "worker_pid": os.getpid(), "successful": successful, "completed": completed,
            "transferred_bytes": command["nbytes"] if successful and command["kind"] != "DROP" else 0,
            "host_held": slot is not None, "host_payload_bytes": slot["nbytes"] if slot is not None else 0,
            "error": error, **extra}


def rpc(wrapper, command):
    """供strict UniProc collective_rpc(callable,single_value=True)同步调用。"""
    global _SLOT, _VERIFIED_ONCE
    try:
        packet = _command(command)
    except Exception as error:
        return {"successful": False, "completed": False, "transferred_bytes": 0,
                "host_held": _SLOT is not None, "worker_pid": os.getpid(), "error": repr(error)}
    if not _LOCK.acquire(blocking=False):
        return _reply(packet, False, False, error="worker RPC已有inflight事务")
    torch, submitted, accepted = None, False, False
    try:
        key, serial, kind = packet["key"], packet["operation_serial"], packet["kind"]
        slot = _SLOT
        if kind == "DROP":
            if (slot is None or key != slot["key"] or id(wrapper) != slot["owner_id"]
                    or serial < slot["last_serial"]
                    or not slot["settled"]):
                raise RuntimeError("不能DROP异epoch/陈旧/未settle的host")
            _LAST_SERIAL[key] = max(serial, _LAST_SERIAL.get(key, 0))
            _SLOT = None
            return _reply(packet, True, True, dropped=True)
        torch, runner, policy, raw, signatures, pool = _context(wrapper)
        if max(packet["pages"]) >= pool:
            raise ValueError("页号越KV pool界")
        if serial <= _LAST_SERIAL.get(key, 0):
            raise RuntimeError("陈旧operation serial")
        if kind == "SAVE":
            if slot is not None:
                raise RuntimeError("单host slot仍被占用")
            state = runner.requests.get(key[1])
            if state is None or tuple(state.block_ids[0][:len(packet["pages"])]) != packet["pages"]:
                raise RuntimeError("SAVE源不是实际worker请求的逻辑prefix页")
            verify = os.environ.get(VERIFY_ENV, "0") == "1" and not _VERIFIED_ONCE
            verify_bytes = packet["nbytes"] // LAYERS if verify else 0
            memory_before = _memory_headroom()
            _budget(packet["nbytes"], verify_bytes, memory_before)
            slot = {**packet, "owner_id": id(wrapper), "signatures": signatures, "raw": raw,
                    "host": [], "verify_buffer": None, "verify": verify,
                    "verify_bytes": verify_bytes, "phase": "ALLOCATING", "last_serial": serial,
                    "settled": False, "memory_before": memory_before}
            _SLOT = slot
            accepted = True
            # 显式producer fence覆盖所有已提交层KV writer；不取CPU future。
            torch.cuda.synchronize()
            slot["settled"] = True
            count = packet["prefix_tokens"] // 16
            for _ in range(LAYERS):
                slot["host"].append(torch.empty((count, PAGE_BYTES), dtype=torch.uint8, pin_memory=True))
            if verify:
                slot["verify_buffer"] = torch.empty((count, PAGE_BYTES), dtype=torch.uint8, pin_memory=True)
            slot["memory_after_pin"] = _memory_headroom()
            if slot["memory_after_pin"]["headroom_bytes"] < HEADROOM_GUARD:
                raise BufferError("pin后1GiB headroom guard不足")
            slot["settled"], submitted = False, True
            info = _save_pitched(torch, raw, slot, packet, pool)
            _finish(torch, slot)
            info.update(_verify_saved_source(torch, policy, raw, slot, packet))
            slot["phase"] = "SAVED"
            info.update(full_restore_supported=True, saved_layers=LAYERS,
                        saved_page_bytes=PAGE_BYTES, saved_prefix_pages=count,
                        saved_bytes=packet["nbytes"])
        else:
            if (slot is None or slot["key"] != key or slot["owner_id"] != id(wrapper)
                    or slot["nbytes"] != packet["nbytes"] or slot["signatures"] != signatures
                    or not slot["settled"]):
                raise RuntimeError("restore/zero的epoch、owner、KV storage或完成围栏不符")
            expected_phase = "SAVED" if kind in ("ZERO", "RESTORE_FULL") else "ZEROED"
            if slot["phase"] != expected_phase:
                raise RuntimeError("ZERO/RESTORE顺序不符")
            if kind == "RESTORE" and packet["pages"] != slot["destination_pages"]:
                raise RuntimeError("RESTORE不是已完成ZERO的同一逻辑目标映射")
            full_plan = _full_restore_plan(torch, policy, slot, raw, pool, packet) if kind == "RESTORE_FULL" else None
            slot["last_serial"] = serial
            accepted = True
            if full_plan is not None:
                # 原ZERO负责的目的绑定在真SAVED入口完成，不伪造ZERO阶段/Receipt。
                slot["destination_pages"], slot["full_restore_plan"] = packet["pages"], full_plan
                slot["phase"] = "RESTORE_FULL_BOUND"
            torch.cuda.synchronize()
            slot["settled"], submitted = False, True
            if kind == "ZERO":
                plan = policy.make_plan(packet["pages"], range(len(packet["pages"])), pool,
                                        len(packet["pages"]), PAGE_BYTES)
                for tensor in raw:
                    for start, _, count in plan.runs:
                        tensor.narrow(0, start, count).zero_()
                info = {"submitted_bytes": packet["nbytes"], "copy_calls": 0,
                        "zero_calls": LAYERS * len(plan.runs)}
                _finish(torch, slot)
                slot["destination_pages"], slot["phase"] = packet["pages"], "ZEROED"
            else:
                count = packet["prefix_tokens"] // 16
                if kind == "RESTORE_FULL":
                    info = _restore_pitched(torch, raw, slot, packet, pool)
                else:
                    info = _copy(policy, slot["host"], raw, range(count), packet["pages"])
                _finish(torch, slot)
                if slot["verify"]:
                    verify_buffer = slot["verify_buffer"]
                    readback_calls = 0
                    for tensor, saved in zip(raw, slot["host"]):
                        slot["settled"] = False
                        row = _copy(policy, [tensor], [verify_buffer], packet["pages"], range(count))
                        readback_calls += row["copy_calls"]
                        _finish(torch, slot)
                        if not torch.equal(verify_buffer, saved):  # 两者均pinned CPU uint8。
                            raise RuntimeError("诊断restore目标页全字节回读不匹配")
                    slot["verification_passed"] = True
                    _VERIFIED_ONCE = True
                    slot["verify_buffer"] = None
                    info.update(verification_performed=True, verification_passed=True,
                                verification_readback_bytes=packet["nbytes"], verification_copy_calls=readback_calls)
                if kind == "RESTORE_FULL":
                    info.update(zero_stage_executed=False, zero_calls=0, destination_bound=True,
                                full_coverage=True, full_coverage_bytes=packet["nbytes"])
                slot["phase"] = "RESTORED"
        _LAST_SERIAL[key] = serial
        return _reply(packet, True, True, **info, diagnostic_verify_requested=slot["verify"],
                      diagnostic_extra_pinned_bytes=slot["verify_bytes"],
                      memory_before=slot.get("memory_before"), memory_after_pin=slot.get("memory_after_pin"))
    except Exception as error:
        # 不知道是否已提交部分copy时也必须实际全device settle；失败保强引用。
        settled = False
        try:
            torch = torch or sys.modules.get("torch")
            if torch is not None:
                torch.cuda.synchronize()
                settled = True
        except Exception:
            pass
        if accepted and _SLOT is not None:
            _SLOT["settled"] = settled
            _SLOT["phase"] = "FAILED"
        if accepted:
            _LAST_SERIAL[packet["key"]] = max(packet["operation_serial"], _LAST_SERIAL.get(packet["key"], 0))
        return _reply(packet, False, settled, error=repr(error), submitted=submitted,
                      verification_performed=bool(_SLOT and _SLOT.get("verify") and packet["kind"] in ("RESTORE", "RESTORE_FULL")),
                      verification_passed=False)
    finally:
        _LOCK.release()
