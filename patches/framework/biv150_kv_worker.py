"""显式RPC才启用的normal42 KV事务worker；默认无安装或框架导入。

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
    "vllm_fl.worker.model_runner": "e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1",
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
    if kind not in ("SAVE", "ZERO", "RESTORE", "DROP"):
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
            info = _copy(policy, raw, slot["host"], packet["pages"], range(count))
            _finish(torch, slot)
            slot["phase"] = "SAVED"
        else:
            if (slot is None or slot["key"] != key or slot["owner_id"] != id(wrapper)
                    or slot["nbytes"] != packet["nbytes"] or slot["signatures"] != signatures
                    or not slot["settled"]):
                raise RuntimeError("restore/zero的epoch、owner、KV storage或完成围栏不符")
            expected_phase = "SAVED" if kind == "ZERO" else "ZEROED"
            if slot["phase"] != expected_phase:
                raise RuntimeError("ZERO/RESTORE顺序不符")
            if kind == "RESTORE" and packet["pages"] != slot["destination_pages"]:
                raise RuntimeError("RESTORE不是已完成ZERO的同一逻辑目标映射")
            slot["last_serial"] = serial
            accepted = True
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
                      verification_performed=bool(_SLOT and _SLOT.get("verify") and packet["kind"] == "RESTORE"),
                      verification_passed=False)
    finally:
        _LOCK.release()
