"""独立 normal FULL H2D 提交工具；导入不载库、不导入 Torch、不接管事务。

显式复用已加载且源码锁定的 818e SAVE runtime。物理目的页保原序，host
仍是完整逻辑页。PreparedRestore/bridge/stream 必须由原事务强持至真事件
完成或失败 settle；submit 的成功不是可发布 ACK，也不证明目的页所有权。
"""
import ctypes
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
from types import ModuleType

SAVE_RUNTIME_SHA256 = "818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd"
PAGE_BYTES = 16384


def _checked_runtime(runtime):
    if type(runtime) is not ModuleType:
        raise TypeError("显式传入已加载的冻结 SAVE runtime 模块")
    path = Path(runtime.__file__)
    if (path.is_symlink() or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != SAVE_RUNTIME_SHA256):
        raise RuntimeError("需要原 818e runtime；不主动 import/修改原模块")
    if (runtime.PAGE_BYTES != PAGE_BYTES or runtime.PAYLOAD_CAP != 1 << 30
            or ctypes.sizeof(runtime._Descriptor) != 72):
        raise RuntimeError("原 runtime 常量/descriptor ABI 不符")
    return runtime


@dataclass(frozen=True)
class RestoreSegment:
    physical_start: int
    logical_start: int
    height: int
    physical_step: int


@dataclass(frozen=True)
class RestorePlan:
    geometry: object
    runtime: object

    @property
    def destination_ids(self):
        return self.geometry.source_ids

    @property
    def destination_pages(self):
        return self.geometry.source_pages

    @property
    def logical_pages(self):
        return self.geometry.logical_pages

    @property
    def original_c95f_runs(self):
        return self.geometry.original_c95f_runs

    @property
    def segments(self):
        return tuple(RestoreSegment(s.source_start, s.destination_start, s.height, s.source_step)
                     for s in self.geometry.segments)


def make_restore_plan(destination_ids, destination_pages, *, save_runtime, page_bytes=PAGE_BYTES):
    """只换几何方向名；原 818e planner 校验唯一页/界/完整原序/size_t overflow。"""
    runtime = _checked_runtime(save_runtime)
    return RestorePlan(runtime.make_plan(destination_ids, destination_pages, page_bytes), runtime)


def _validated_plan(plan):
    if type(plan) is not RestorePlan or type(plan.geometry) is not plan.runtime.SavePlan:
        raise TypeError("需要 make_restore_plan 返回的冻结几何")
    # 不做文件 I/O 或设备调用；完整页展开验证由原 SavePlan 再执行一次。
    plan.geometry.__post_init__()
    return plan.runtime


def segments_for_pitch(plan, *, max_pitch):
    """纯整数：超目的 pitch 限制的二维段在任何提交前拆回单页，绝不重排。"""
    runtime = _validated_plan(plan)
    runtime._integer(max_pitch, PAGE_BYTES)
    pieces, fallbacks = [], 0
    for segment in plan.segments:
        s, d, h, step = (segment.physical_start, segment.logical_start,
                         segment.height, segment.physical_step)
        if h > 1 and step > 1 and runtime._multiply(step, PAGE_BYTES) > max_pitch:
            fallbacks += 1
            pieces.extend(RestoreSegment(s + j * step, d + j, 1, 1) for j in range(h))
        else:
            pieces.append(segment)
    return tuple(pieces), fallbacks


@dataclass(frozen=True)
class PreparedRestore:
    descriptors: object
    keepalive: tuple
    runtime: object
    submitted_bytes: int
    linear_calls: int
    pitched_calls: int
    fallback_pitched_segments: int
    original_c95f_calls: int


def _nonoverlapping_storage(tensor, base, seen, runtime):
    size = runtime._integer(tensor.untyped_storage().nbytes())
    if base > runtime.SIZE_MAX - size:
        raise ValueError("storage 地址 overflow")
    end = base + size
    if any(base < old_end and old_base < end for old_base, old_end in seen):
        raise ValueError("不支持同侧跨层 host/GPU storage alias")
    seen.append((base, end))


def prepare_restore(hosts, gpu_raw, plan, *, max_pitch):
    """首提交前验证完整 batch；不分配 GPU、不读取 Tensor 值、不改 host 或页表。

    此层仅证明 raw 存储界及无 alias，不证明 fresh/ref1/unhashed/42层覆盖资格；
    后者仍须原 FULL worker 的 _full_restore_plan 和私有目的绑定检查。
    """
    runtime = _validated_plan(plan)
    pieces, fallbacks = segments_for_pitch(plan, max_pitch=max_pitch)
    torch = sys.modules.get("torch")
    if torch is None:
        raise RuntimeError("只供已加载 Torch 的 worker，不主动导入框架")
    hosts, gpu_raw = tuple(hosts), tuple(gpu_raw)
    layers = len(hosts)
    if layers not in (1, 42) or len(gpu_raw) != layers:
        raise ValueError("仅独立单层门或原 normal42 层")
    nbytes = runtime._multiply(runtime._multiply(plan.logical_pages, PAGE_BYTES), layers)
    if nbytes > runtime.PAYLOAD_CAP:
        raise ValueError("FULL restore payload 不超过原 1GiB cap")
    host_storage, gpu_storage, ranges = [], [], []
    for host, gpu in zip(hosts, gpu_raw):
        src, src_bytes, src_base = runtime._tensor_range(torch, host, (plan.logical_pages, PAGE_BYTES), "cpu")
        dst, dst_bytes, dst_base = runtime._tensor_range(torch, gpu, (plan.destination_pages, PAGE_BYTES), "cuda:0")
        _nonoverlapping_storage(host, src_base, host_storage, runtime)
        _nonoverlapping_storage(gpu, dst_base, gpu_storage, runtime)
        ranges.append((src, src_bytes, dst, dst_bytes))
    descriptors, linear, pitched = [], 0, 0
    for src, src_bytes, dst, dst_bytes in ranges:
        for segment in pieces:
            physical, logical, rows, step = (segment.physical_start, segment.logical_start,
                                            segment.height, segment.physical_step)
            source_offset = runtime._multiply(logical, PAGE_BYTES)
            destination_offset = runtime._multiply(physical, PAGE_BYTES)
            kind = 2 if rows > 1 and step > 1 else 1
            width = PAGE_BYTES if kind == 2 else runtime._multiply(rows, PAGE_BYTES)
            height = rows if kind == 2 else 1
            source_pitch = PAGE_BYTES if kind == 2 else width
            destination_pitch = runtime._multiply(step, PAGE_BYTES) if kind == 2 else width
            descriptors.append(runtime._Descriptor(src + source_offset, dst + destination_offset,
                src_bytes - source_offset, dst_bytes - destination_offset,
                width, height, source_pitch, destination_pitch, kind, 0))
            linear += kind == 1
            pitched += kind == 2
    if len(descriptors) > 65536:
        raise ValueError("batch descriptor 数超独立桥界")
    array = (runtime._Descriptor * len(descriptors))(*descriptors)
    return PreparedRestore(array, hosts + gpu_raw + (plan, runtime), runtime, nbytes, linear,
                           pitched, fallbacks * layers, plan.original_c95f_runs * layers)


class RestoreSubmissionError(RuntimeError):
    def __init__(self, code, submitted_calls, total_calls):
        self.code, self.submitted_calls, self.total_calls = code, submitted_calls, total_calls
        self.partial = submitted_calls > 0
        super().__init__(f"native FULL H2D 提交失败 code={code}, submitted={submitted_calls}/{total_calls}; "
                         "必须 settle，禁止旧路重试或发布")


class RestoreBridge:
    """显式加载新 SDK 桥；复用旧 ABI/最大 pitch 查询，不调用旧 SAVE submit。"""
    def __init__(self, path, *, expected_sha256, save_runtime):
        self.runtime = _checked_runtime(save_runtime)
        self._base = self.runtime.Bridge(path, expected_sha256=expected_sha256)
        self._submit = self._base._library.biv150_pitched_restore_batch
        self._submit.argtypes = [ctypes.POINTER(self.runtime._Descriptor), ctypes.c_size_t,
                                 ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t)]
        self._submit.restype = ctypes.c_int

    def max_pitch(self, device=0):
        return self._base.max_pitch(device)

    def submit(self, prepared, *, stream_handle):
        if type(prepared) is not PreparedRestore or prepared.runtime is not self.runtime:
            raise TypeError("需要同一冻结 runtime 的 PreparedRestore")
        self.runtime._integer(stream_handle)  # 0 是合法 native stream；生产继续传实际 current stream。
        submitted = ctypes.c_size_t()
        code = self._submit(prepared.descriptors, len(prepared.descriptors),
                            ctypes.c_void_p(stream_handle), ctypes.byref(submitted))
        if code or submitted.value != len(prepared.descriptors):
            raise RestoreSubmissionError(code or -1006, submitted.value, len(prepared.descriptors))
        return {"submitted_bytes": prepared.submitted_bytes, "copy_calls": submitted.value,
                "linear_calls": prepared.linear_calls, "pitched_calls": prepared.pitched_calls,
                "fallback_pitched_segments": prepared.fallback_pitched_segments,
                "original_c95f_calls": prepared.original_c95f_calls, "completion_ack": False}
