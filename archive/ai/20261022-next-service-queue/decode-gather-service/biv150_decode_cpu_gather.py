"""仅在整步 GPU token 覆盖可证明时，省去无消费者的 CPU token gather。

只供精确 6f918 runner 的独立源码变换使用；不安装、不上传、不启动设备。
原 input-ID GPU 准备、metadata、事件与采样代码完整保留。
"""
from __future__ import annotations

import hashlib
from numbers import Integral
from pathlib import Path
import sys


EXPECTED_RUNNER = "6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141"
EXPECTED_METADATA = "0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f"
EXPECTED_ASYNC = "1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc"
STATE = "_biv150_decode_cpu_gather"
_VERIFIED = None
_IMPORT = (b"from vllm_fl.patches.biv150_decode_cpu_gather import "
           b"skip_dead_cpu_gather as _biv150_skip_dead_cpu_gather\n")
_ANCHOR = (b"from vllm_fl.patches.biv150_async_token_update import "
           b"fused_sampled_token_update as _biv150_fused_sampled_token_update\n")
_GUARD = b"        if not _biv150_skip_dead_cpu_gather(self, scheduler_output, num_scheduled_tokens):\n"


def _gather_block(raw):
    start = raw.index(b"        # Get token indices.\n")
    end = raw.index(b"        if self.enable_prompt_embeds:\n", start)
    return raw[start:end]


def transform(raw):
    if hashlib.sha256(raw).hexdigest() != EXPECTED_RUNNER:
        raise ValueError("只接受原字节 6f918 CPU 组合 runner")
    block = _gather_block(raw)
    if raw.count(block) != 1 or raw.count(_ANCHOR) != 1:
        raise ValueError("CPU gather 或 import 边界不唯一")
    nested = b"".join(b"    " + line if line.strip() else line
                      for line in block.splitlines(keepends=True))
    changed = raw.replace(_ANCHOR, _ANCHOR + _IMPORT, 1).replace(block, _GUARD + nested, 1)
    compile(changed, "isolated:decode-cpu-gather", "exec")
    if reverse(changed) != raw:
        raise AssertionError("源码不可逐字节逆回")
    return changed


def reverse(raw):
    changed = raw.replace(_ANCHOR + _IMPORT, _ANCHOR, 1)
    begin = changed.index(_GUARD)
    end = changed.index(b"        if self.enable_prompt_embeds:\n", begin)
    nested = changed[begin + len(_GUARD):end]
    original = b"".join(line[4:] if line.strip() else line
                        for line in nested.splitlines(keepends=True))
    restored = changed[:begin] + original + changed[end:]
    if hashlib.sha256(restored).hexdigest() != EXPECTED_RUNNER:
        raise ValueError("逆变换未还原精确 6f918")
    return restored


def _dependencies():
    global _VERIFIED
    metadata = sys.modules.get("vllm_fl.patches.biv150_cpu_metadata")
    asynchronous = sys.modules.get("vllm_fl.patches.biv150_async_token_update")
    if metadata is None or asynchronous is None:
        return None
    pair = (metadata, asynchronous)
    if _VERIFIED != pair:
        for module, expected in zip(pair, (EXPECTED_METADATA, EXPECTED_ASYNC)):
            if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
                return None
        _VERIFIED = pair
    return pair


def _proof(runner, scheduler_output, scheduled, torch, np, metadata, asynchronous):
    if not metadata._scope(runner, torch) or not asynchronous._runner_eligible(runner):
        return False
    batch = runner.input_batch
    previous = batch.prev_sampled_token_ids
    count = batch.num_reqs
    if (type(count) is not int or not 0 < count <= runner.max_num_reqs
            or scheduler_output.total_num_scheduled_tokens != count
            or scheduler_output.scheduled_spec_decode_tokens
            or batch.req_prompt_embeds
            or not isinstance(scheduled, np.ndarray) or scheduled.dtype != np.int32
            or scheduled.shape != (count,) or not bool(np.all(scheduled == 1))
            or type(batch.req_ids) is not list or len(batch.req_ids) != count
            or type(batch.prev_req_id_to_index) is not dict
            or type(previous) is not torch.Tensor
            or previous.device != runner.device or previous.dtype != torch.int32
            or previous.ndim != 2 or previous.shape[1] != 1 or previous.stride(0) <= 0):
        return False
    cpu, gpu, table = runner.input_ids.cpu, runner.input_ids.gpu, batch.token_ids_cpu_tensor
    if (not all(type(value) is torch.Tensor for value in (cpu, gpu, table))
            or cpu.device.type != "cpu" or table.device.type != "cpu"
            or cpu.dtype != gpu.dtype or cpu.dtype != table.dtype or cpu.dtype != torch.int32
            or cpu.ndim != 1 or cpu.shape[0] < count or cpu.stride(0) != 1
            or gpu.device != runner.device or gpu.ndim != 1 or gpu.shape[0] < count or gpu.stride(0) <= 0
            or table.ndim != 2 or table.shape[0] < count or not table.is_contiguous()
            or cpu.untyped_storage().data_ptr() == table.untyped_storage().data_ptr()
            or gpu.untyped_storage().data_ptr() == previous.untyped_storage().data_ptr()):
        return False
    computed = batch.num_computed_tokens_cpu
    if (not isinstance(computed, np.ndarray) or computed.dtype != np.int32
            or computed.ndim != 1 or computed.shape[0] < count
            or not bool(np.all((computed[:count] >= 0) & (computed[:count] < table.shape[1])))):
        return False
    ids, rows = set(), set()
    for req_id in batch.req_ids:
        if type(req_id) is not str or req_id in ids:
            return False
        ids.add(req_id)
        row = batch.prev_req_id_to_index.get(req_id)
        if (not isinstance(row, Integral) or isinstance(row, bool)
                or not 0 <= row < previous.shape[0] or row in rows):
            return False
        rows.add(row)
    # All N requests have exactly one token and one valid previous row.
    # Original cumsum gives destinations 0..N-1. No CPU H2D branch is taken;
    # the unchanged identity copy or unchanged scatter covers all N GPU IDs.
    return True


def skip_dead_cpu_gather(runner, scheduler_output, scheduled):
    """逐步重验资格；不跨步缓存请求映射，不触碰任何 GPU 数值或同步。"""
    try:
        dependencies = _dependencies()
        torch, np = sys.modules.get("torch"), sys.modules.get("numpy")
        eligible = (dependencies is not None and torch is not None and np is not None
                    and _proof(runner, scheduler_output, scheduled, torch, np, *dependencies))
    except (AttributeError, TypeError, ValueError, OSError, KeyError, OverflowError):
        eligible = False
    state = getattr(runner, STATE, None)
    if state is None:
        state = {"selected": 0, "fallback": 0}
        setattr(runner, STATE, state)
    state["selected" if eligible else "fallback"] += 1
    return bool(eligible)
