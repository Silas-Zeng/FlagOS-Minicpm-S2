"""默认不安装的BI-V150单victim KV协议；只用于隔离候选。

exact UniProc/WorkerFL/normal42。worker产生真实完成ACK；本模块不采样、
不消费future、不重排请求，不更改官方serve参数。异常若无法证明settled则失败退出。
"""
from contextvars import ContextVar
from functools import wraps
import hashlib
import importlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap

from . import biv150_kv_completion_probe as scope_probe
from . import biv150_kv_transaction as protocol

MAX_HOST_BYTES = 1 << 30
_ACTIVE = ContextVar("biv150_kv_protocol", default=None)
_MARKER = "_biv150_kv_protocol_v1"
_SESSION = 0
_CAPACITY_REQUEST_CLASS = None
_CAPACITY_REQUEST_CHECKED = False
EXPECTED_CAPACITY_REQUEST = "06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80"
EXPECTED_INIT = "e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff"
EXPECTED_EXTRA = {
    "vllm.v1.executor.uniproc_executor": "4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe",
    "vllm.v1.serial_utils": "d75c17a098231b2398cbdb7da6f9983e5b9229c0ba138b2874934d45fafd1f28",
    "vllm.v1.worker.worker_base": "7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe",
    "vllm.v1.kv_cache_interface": "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003",
}
INIT_FOOTER = (b"\n    # _biv150_kv_protocol_v1\n"
               b"    from vllm_fl.patches.biv150_kv_protocol import install as _install_kv_protocol\n"
               b"    _install_kv_protocol(enabled=True)\n")


def transform_init(source):
    if hashlib.sha256(source).hexdigest() != EXPECTED_INIT:
        raise RuntimeError("requires exact isolated SQL+C3 init")
    return source + INIT_FOOTER


def _emit(state, event, **fields):
    print("BIV150_KV_PROTOCOL " + json.dumps({"pid": os.getpid(), "event": event,
          "single_victim": True, "host_payload_cap": MAX_HOST_BYTES,
          **state["counts"], **fields}, sort_keys=True), flush=True)


def _rpc(state, victim, operation):
    from . import biv150_kv_worker as worker_protocol
    key = operation.key
    command = {"key": [key.session, key.request_id, key.incarnation, key.attempt],
               "operation_serial": operation.serial, "kind": operation.kind,
               "pages": list(operation.pages), "prefix_tokens": victim["tx"].snapshot.prefix_tokens,
               "nbytes": operation.nbytes}
    try:
        result = state["engine"].model_executor.collective_rpc(
            worker_protocol.rpc, args=(command,), single_value=True)
    except BaseException as error:
        _emit(state, "RPC_EXCEPTION_COMPLETION_UNOBSERVED", command=command, error=repr(error))
        raise
    # 单victim稀疏完整证据；保留worker真实回读/事件/内存字段，不只转Receipt。
    _emit(state, "RPC_ACK", command=command, worker_response=result)
    for field in ("key", "operation_serial", "kind", "pages", "nbytes"):
        if result.get(field) != command[field]:
            raise RuntimeError("worker ACK command mismatch: " + field)
    if result.get("completed") is not True:
        raise RuntimeError("worker transfer未settle；禁止free、drop或发布")
    if result.get("worker_pid") != os.getpid():
        raise RuntimeError("only actual same-process UniProc worker is supported")
    victim["host_held"] = result.get("host_held") is True
    if operation.kind == "SAVE" and result.get("successful") is True and victim["host_held"]:
        victim["full_restore_descriptor"] = {name: result.get(name) for name in (
            "full_restore_supported", "saved_layers", "saved_page_bytes", "saved_prefix_pages", "saved_bytes")}
    if operation.kind == "RESTORE_FULL" and result.get("successful") is True:
        if (result.get("zero_stage_executed") is not False or result.get("zero_calls") != 0
                or result.get("full_coverage") is not True or result.get("destination_bound") is not True
                or result.get("full_coverage_bytes") != operation.nbytes):
            raise RuntimeError("RESTORE_FULL成功ACK缺完整覆盖/未执行ZERO的真实证明")
    return protocol.Receipt(operation, result["transferred_bytes"], True, result["successful"])


def _drop(state, victim):
    tx = victim["tx"]
    if tx.inflight is not None:
        raise RuntimeError("不能释放仍在transfer中的单victim")
    if victim.get("host_held"):
        op = protocol.Operation(tx.snapshot.key, tx.slot._next_serial(tx.snapshot.key), "DROP", (), 0)
        receipt = _rpc(state, victim, op)
        if receipt.successful is not True or victim.get("host_held"):
            raise RuntimeError("worker未释放host snapshot，不可复用slot")
    tx.close()
    if state["victim"] is victim:
        state["victim"] = None


def _discard_host(state, victim, reason):
    _emit(state, "HOST_DISCARDED", reason=reason,
          request_id=victim["request"].request_id)
    victim["tx"].discard()
    _drop(state, victim)


def _defer_restore(state, victim, scheduler, request, token_budget, reason):
    """仅保留host；原waiting路径继续，无park/提前消费/逐步日志。"""
    state["counts"]["restore_skips"] += 1
    if not victim.get("restore_defer_logged"):
        tx = victim["tx"]
        _emit(state, "RESTORE_DEFERRED", reason=reason, request_id=request.request_id,
              pending_frames=len(tx.pending_frames),
              output_placeholders=request.num_output_placeholders,
              token_budget=token_budget, free_blocks=scheduler.kv_cache_manager.block_pool.get_num_free_blocks(),
              saved_prefix_pages=len(tx.snapshot.source_pages), request_tokens=request.num_tokens,
              full_sequence_must_fit=scheduler.scheduler_reserve_full_isl,
              allocator_required_blocks_observed=False, host_retained=True)
        victim["restore_defer_logged"] = True


def _rollback(state, victim):
    """仅未发布且传输已settle时，原free实际成功后才确认回滚。"""
    tx, scheduler, request = victim["tx"], state["engine"].scheduler, victim["request"]
    if tx.phase in ("ALLOCATED", "ZERO_DONE", "RESTORE_DONE"):
        tx.rollback_unpublished()
    tx.release_private_allocation()
    # strict FullAttention needs_zero=False：new_block_ids是历史，完全不改。
    scheduler.kv_cache_manager.free(request)
    tx.private_allocation_released()
    request.num_computed_tokens = victim["original_computed"]
    state["counts"]["rollbacks"] += 1
    _drop(state, victim)


def _order_private_pages(state, victim, single, owned):
    """只重排尚未绑定/发布的完整私有页映射，不重排host逻辑内容。"""
    tx, request = victim["tx"], victim["request"]
    if len(owned) != 1:
        return False
    pages = owned[0]
    cached = single.num_cached_block.get(request.request_id)
    if (type(pages) is not list or single.req_to_blocks.get(request.request_id) is not pages
            or type(cached) is not int or cached != 0
            or tx.phase != "HOST_RESIDENT" or tx.pending_frames or tx.destination_pages
            or tx.inflight is not None or tx.cancelled or tx.closed or not tx.source_released
            or len(pages) != len(tx.snapshot.source_pages)
            or len(pages) * protocol.BLOCK_TOKENS != tx.snapshot.prefix_tokens
            or any(type(b.block_id) is not int or b.block_id <= 0 or b.ref_cnt != 1
                   or b.is_null or b.block_hash is not None for b in pages)):
        return False
    before = tuple(b.block_id for b in pages)
    objects = {id(b) for b in pages}
    if len(set(before)) != len(before) or len(objects) != len(pages):
        return False
    # actual非empty get_blocks保同list，cache_blocks随后按此逻辑位置关联hash。
    # new_block_ids历史及Block对象自身完全不改；future free(reverse(list))次序可变。
    pages.sort(key=lambda block: block.block_id)
    after = tuple(b.block_id for b in pages)
    if (single.req_to_blocks.get(request.request_id) is not pages
            or {id(b) for b in pages} != objects or after != tuple(sorted(before))):
        raise RuntimeError("private page排序破坏真实所有权映射")
    runs = lambda ids: 1 + sum(b != a + 1 for a, b in zip(ids, ids[1:]))
    _emit(state, "PRIVATE_PAGES_ORDERED", request_id=request.request_id,
          prefix_tokens=tx.snapshot.prefix_tokens, page_count=len(pages),
          increasing_runs_before=runs(before), increasing_runs_after=runs(after),
          same_page_ids=True, same_block_objects=True, owned_list_identity=True,
          host_logical_order_changed=False, future_free_order_may_change=True)
    return True


def _capacity_request_class():
    """可选快捷路径守卫；未验证只禁快路，不import框架或阻断原协议。"""
    global _CAPACITY_REQUEST_CLASS, _CAPACITY_REQUEST_CHECKED
    if not _CAPACITY_REQUEST_CHECKED:
        _CAPACITY_REQUEST_CHECKED = True
        try:
            module = sys.modules.get("vllm.v1.request")
            cls = module.Request
            path = Path(module.__file__).resolve()
            if ((cls.__module__, cls.__name__) == ("vllm.v1.request", "Request")
                    and Path(inspect.getfile(cls)).resolve() == path
                    and hashlib.sha256(path.read_bytes()).hexdigest() == EXPECTED_CAPACITY_REQUEST
                    and all(inspect.unwrap(method) is method
                            and Path(method.__code__.co_filename).resolve() == path
                            for method in (cls.__init__, cls.append_output_token_ids, cls.num_tokens.fget))):
                _CAPACITY_REQUEST_CLASS = cls
        except Exception:
            pass
    return _CAPACITY_REQUEST_CLASS


def _capacity_fast_reject(state, victim, scheduler, request, token_budget):
    cls = _capacity_request_class()
    if (cls is None or type(request) is not cls
            or getattr(request, "resumable", None) is not False
            or getattr(request, "streaming_queue", False) is not None):
        return False
    tx = victim["tx"]
    prefix = tx.snapshot.prefix_tokens
    # 长度失效不能为容量不足而延迟DROP；实际源num_tokens仅O(1)len。
    if request.num_tokens <= prefix:
        _discard_host(state, victim, "token_prefix_changed")
        return True
    manager = scheduler.kv_cache_manager
    single = manager.coordinator.single_type_managers[0]
    cached = single.num_cached_block.get(request.request_id)
    if (prefix <= 0 or prefix % protocol.BLOCK_TOKENS or prefix > manager.max_model_len
            or single.req_to_blocks.get(request.request_id)
            or not (cached is None or type(cached) is int and cached == 0)):
        return False
    if manager.block_pool.get_num_free_blocks() < prefix // protocol.BLOCK_TOKENS:
        state["counts"]["fast_rejects"] += 1
        _defer_restore(state, victim, scheduler, request, token_budget, "capacity_lower_bound")
        return True
    return False


def _full_restore_ready(victim, single, owned):
    """SAVE真实normal42描述与未发布完整私有页同时成立才选新操作。"""
    tx, request = victim["tx"], victim["request"]
    prefix = tx.snapshot.prefix_tokens
    count = prefix // protocol.BLOCK_TOKENS
    expected = {"saved_layers": 42, "saved_page_bytes": 16384,
                "saved_prefix_pages": count, "saved_bytes": tx.snapshot.nbytes}
    descriptor = victim.get("full_restore_descriptor")
    if (type(descriptor) is not dict or descriptor.get("full_restore_supported") is not True
            or any(type(descriptor.get(k)) is not int or descriptor[k] != v for k, v in expected.items())
            or prefix % protocol.BLOCK_TOKENS or tx.snapshot.nbytes != 42 * count * 16384
            or tx.phase != "ALLOCATED" or tx.inflight is not None or tx.pending_frames
            or tx.cancelled or tx.closed or not victim.get("host_held")
            or request.num_computed_tokens != 0 or request.status.name != "PREEMPTED"
            or len(owned) != 1 or type(owned[0]) is not list
            or single.req_to_blocks.get(request.request_id) is not owned[0]
            or type(single.num_cached_block.get(request.request_id)) is not int
            or single.num_cached_block[request.request_id] != 0
            or len(owned[0]) != count
            or tuple(b.block_id for b in owned[0]) != tx.destination_pages
            or any(b.ref_cnt != 1 or b.is_null or b.block_hash is not None for b in owned[0])):
        return False
    return True


def _try_restore(scheduler, request, token_budget):
    frame = _ACTIVE.get()
    if frame is None or frame["engine"].scheduler is not scheduler:
        return
    state, victim = frame, frame["victim"]
    if victim is None or victim["request"] is not request:
        return
    tx = victim["tx"]
    if tx.phase != "HOST_RESIDENT":
        raise RuntimeError("unexpected waiting victim phase")
    if (scheduler.requests.get(request.request_id) is not request or request.is_finished()
            or request.num_preemptions != tx.snapshot.key.attempt):
        _discard_host(state, victim, "request_identity_terminal_or_epoch_changed")
        return
    if request.status.name != "PREEMPTED" or request.num_computed_tokens != 0:
        _discard_host(state, victim, "waiting_request_state_changed")
        return
    # 暂态不使已保存prefix失效；原FCFS仍可普通准入，返回output后才判断。
    if token_budget <= 0 or tx.pending_frames or request.num_output_placeholders != 0:
        reason = ("pending_frames" if tx.pending_frames else
                  "output_placeholders" if request.num_output_placeholders != 0 else "token_budget")
        _defer_restore(state, victim, scheduler, request, token_budget, reason)
        return
    if _capacity_fast_reject(state, victim, scheduler, request, token_budget):
        return
    tokens = list(request.all_token_ids)
    if (len(tokens) <= tx.snapshot.prefix_tokens
            or protocol.prefix_digest(tokens, tx.snapshot.prefix_tokens) != tx.snapshot.token_digest):
        _discard_host(state, victim, "token_prefix_changed")
        return
    manager = scheduler.kv_cache_manager
    single = manager.coordinator.single_type_managers[0]
    victim["zero_before"] = tuple(single.new_block_ids)
    blocks = manager.allocate_slots(request, 0, num_external_computed_tokens=tx.snapshot.prefix_tokens,
        delay_cache_blocks=True, num_lookahead_tokens=0,
        full_sequence_must_fit=scheduler.scheduler_reserve_full_isl,
        has_scheduled_reqs=bool(scheduler.running))
    if blocks is None:
        _defer_restore(state, victim, scheduler, request, token_budget, "allocation_none")
        return
    owned = manager.get_blocks(request.request_id).blocks
    if (len(owned) != 1 or any(b.ref_cnt != 1 or b.is_null or b.block_hash is not None for b in owned[0])):
        raise RuntimeError("restore requires newly allocated private unhashed pages")
    _order_private_pages(state, victim, single, owned)
    destination = tuple(b.block_id for b in owned[0])
    _, fresh = protocol.split_fresh_zero_ids(victim["zero_before"], single.new_block_ids,
                                            destination, pending_zero=False)
    tx.bind_private_allocation(tx.snapshot.key, tokens, destination, fresh)
    if _full_restore_ready(victim, single, owned):
        receipt = _rpc(state, victim, tx.submit_restore_full())
        tx.acknowledge(receipt)
        if not receipt.successful:
            _rollback(state, victim)
            return
    else:
        receipt = _rpc(state, victim, tx.submit_zero())
        tx.acknowledge(receipt)
        if not receipt.successful:
            _rollback(state, victim)
            return
        receipt = _rpc(state, victim, tx.submit_restore())
        tx.acknowledge(receipt)
        if not receipt.successful:
            _rollback(state, victim)
            return
    # 这仍是私有prepared状态。原后续allocate失败/预算退出时必须回滚到0。
    victim["prepared_tokens"] = tokens
    victim["output_count"] = request.num_output_tokens
    request.num_computed_tokens = tx.snapshot.prefix_tokens
    state["counts"]["restored"] += 1
    _emit(state, "RESTORE_ACK", prefix_tokens=tx.snapshot.prefix_tokens)


def _commit_resume(state, output, victim):
    tx, request = victim["tx"], victim["request"]
    if tx.phase != "RESTORE_DONE":
        return
    rid = request.request_id
    new = [r for r in output.scheduled_new_reqs if r.req_id == rid]
    if rid not in output.num_scheduled_tokens:
        _rollback(state, victim)
        return
    if (len(new) != 1 or request.status.name != "RUNNING"
            or new[0].num_computed_tokens != tx.snapshot.prefix_tokens
            or len(new[0].block_ids) != 1
            or tuple(new[0].block_ids[0][:len(tx.destination_pages)]) != tx.destination_pages
            or state["engine"].scheduler.requests.get(rid) is not request):
        raise RuntimeError("V2 restored resume payload不符合已审路径")
    cached = output.scheduled_cached_reqs
    if rid in cached.req_ids:
        raise RuntimeError("同一resume不能同时在new/cached中")
    if cached.new_token_ids:
        raise RuntimeError("single-rank async scope cannot carry PP token payload")
    # 只改本次新建output，绝不改任何已排队的旧SchedulerOutput。
    output.scheduled_new_reqs = [r for r in output.scheduled_new_reqs if r.req_id != rid]
    cached.req_ids.append(rid)
    cached.resumed_req_ids.add(rid)
    cached.new_block_ids.append(new[0].block_ids)
    cached.num_computed_tokens.append(tx.snapshot.prefix_tokens)
    cached.num_output_tokens.append(victim["output_count"])
    cached.all_token_ids[rid] = list(victim["prepared_tokens"])
    cached.__dict__.pop("_req_id_to_num_output_tokens", None)
    output.__dict__[_MARKER + "_resume"] = {
        "key": [tx.snapshot.key.session, rid, tx.snapshot.key.incarnation, tx.snapshot.key.attempt],
        "request_id": rid, "prefix_tokens": tx.snapshot.prefix_tokens,
        "output_count": victim["output_count"], "all_token_ids": list(victim["prepared_tokens"]),
        "block_ids": tuple(tuple(ids) for ids in new[0].block_ids),
        "cached_state_id": victim["cached_state_id"], "generator_id": victim["generator_id"]}
    tx.publish(tx.snapshot.key, list(request.all_token_ids))
    state["counts"]["published"] += 1
    _emit(state, "RESUME_PUBLISHED", prefix_tokens=tx.snapshot.prefix_tokens)
    _drop(state, victim)


def _wrap_preempt(original):
    @wraps(original)
    def preempt(self, request, *args, **kwargs):
        state = _ACTIVE.get()
        if state is None or state["engine"].scheduler is not self or state["victim"] is not None:
            return original(self, request, *args, **kwargs)
        try:
            queue = tuple(state["engine"].batch_queue or ())
            frames = {}
            frame_refs = {}
            for _, output, _ in queue:
                n = output.num_scheduled_tokens.get(request.request_id, 0)
                if n:
                    state["frame_serial"] += 1
                    frames[state["frame_serial"]] = n
                    frame_refs[id(output)] = (state["frame_serial"], output)
            blocks = self.kv_cache_manager.get_blocks(request.request_id).blocks
            if len(blocks) != 1:
                raise ValueError("only one actual FullAttention group is supported")
            state["incarnation"] += 1
            key = protocol.Key(state["session"], request.request_id, state["incarnation"], request.num_preemptions + 1)
            snapshot = protocol.plan_snapshot(key, request.num_computed_tokens,
                list(request.all_token_ids), [b.block_id for b in blocks[0]], frames)
            tx = protocol.Transaction(snapshot, state["slot"])
        except (ValueError, BufferError):
            state["counts"]["save_skips"] += 1
            return original(self, request, *args, **kwargs)
        victim = {"tx": tx, "request": request, "frames": frame_refs,
                  "original_computed": 0, "host_held": False}
        wrapper = state["engine"].model_executor.__dict__["driver_worker"]
        runner = wrapper.__dict__["worker"].__dict__["model_runner"]
        cached = runner.requests[request.request_id]
        victim["cached_state_id"], victim["generator_id"] = id(cached), id(cached.generator)
        state["victim"] = victim
        receipt = _rpc(state, victim, tx.submit_save())
        tx.acknowledge(receipt)
        # 即使save失败也只能在真实settled ACK后走原抢占。
        if not tx.source_free_permitted():
            raise RuntimeError("save ACK未授权source free")
        result = original(self, request, *args, **kwargs)
        tx.source_free_committed()
        if receipt.successful:
            state["counts"]["saved"] += 1
            _emit(state, "SAVE_ACK_FREE", prefix_tokens=snapshot.prefix_tokens)
        else:
            _drop(state, victim)
        return result
    return preempt


def _wrap_update(original):
    @wraps(original)
    def update(self, output, *args, **kwargs):
        result = original(self, output, *args, **kwargs)
        state = _ACTIVE.get()
        victim = None if state is None else state["victim"]
        if victim is not None and state["engine"].scheduler is self:
            item = victim["frames"].pop(id(output), None)
            if item is not None:
                if item[1] is not output:
                    raise RuntimeError("output frame身份复用")
                victim["tx"].frame_processed(victim["tx"].snapshot.key, item[0])
        resume = output.__dict__.get(_MARKER + "_resume")
        if state is not None and resume is not None:
            _emit(state, "RESUME_OUTPUT_PROCESSED", key=resume["key"],
                  scheduled_tokens=output.num_scheduled_tokens.get(resume["request_id"]),
                  after_original_update=True)
        return result
    return update


def _wrap_schedule(original, injected):
    @wraps(original)
    def schedule(self, *args, **kwargs):
        state = _ACTIVE.get()
        if state is None or state["engine"].scheduler is not self:
            return original(self, *args, **kwargs)
        try:
            output = injected(self, *args, **kwargs)
        except BaseException:
            # 尚未dispatch当前output；只对可证明settle/未发布的private prefix清理。
            victim = state["victim"]
            if victim is not None and victim["tx"].phase in ("ALLOCATED", "ZERO_DONE", "RESTORE_DONE"):
                try:
                    _rollback(state, victim)
                except Exception as error:
                    _emit(state, "ROLLBACK_ERROR_ORIGINAL_EXCEPTION_PRESERVED", error=repr(error))
            raise
        victim = state["victim"]
        if victim is not None and victim["tx"].phase == "RESTORE_DONE":
            _commit_resume(state, output, victim)
        elif (victim is not None and victim["tx"].phase == "HOST_RESIDENT"
                and output.num_scheduled_tokens.get(victim["request"].request_id, 0) > 0):
            # 仅本次原output真正发出该rid的普通work才释放；不凭RUNNING推断。
            _discard_host(state, victim, "ordinary_recompute_admitted")
        return output
    return schedule


def _wrap_runner_states(original):
    @wraps(original)
    def update(self, output, *args, **kwargs):
        result = original(self, output, *args, **kwargs)
        resume = output.__dict__.get(_MARKER + "_resume")
        if resume is not None:
            state = _ACTIVE.get()
            rid, count = resume["request_id"], resume["output_count"]
            cached = self.requests[rid]
            index = self.input_batch.req_id_to_index[rid]
            expected_output = resume["all_token_ids"][-count:] if count else []
            checks = {
                "cached_state_same": id(cached) == resume["cached_state_id"],
                "generator_same": id(cached.generator) == resume["generator_id"],
                "computed_prefix": cached.num_computed_tokens == resume["prefix_tokens"],
                "output_token_ids": list(cached.output_token_ids) == expected_output,
                "full_block_replacement": tuple(tuple(ids) for ids in cached.block_ids) == resume["block_ids"],
                "cpu_computed_prefix": int(self.input_batch.num_computed_tokens_cpu[index]) == resume["prefix_tokens"],
            }
            if state is None or not all(checks.values()):
                raise RuntimeError("restored runner state不符合原cached-resume语义：" + repr(checks))
            _emit(state, "RUNNER_RESUME_STATE_CHECKED", key=resume["key"], checks=checks,
                  before_attention=True, gpu_completion_claimed=False)
        return result
    return update


def _wrap_core(original, classes):
    @wraps(original)
    def step(self, *args, **kwargs):
        global _SESSION
        if _ACTIVE.get() is not None:
            return original(self, *args, **kwargs)
        state = self.__dict__.get(_MARKER)
        if state is None:
            wrapper = self.model_executor.__dict__.get("driver_worker")
            worker = None if wrapper is None else wrapper.__dict__.get("worker")
            runner = None if worker is None else worker.__dict__.get("model_runner")
            eligible = (scope_probe._scope(self, classes)
                and type(self.model_executor) is classes["executor"]
                and type(wrapper) is classes["wrapper"] and worker is not None and runner is not None
                and (type(worker).__module__, type(worker).__name__) == ("vllm_fl.worker.worker", "WorkerFL")
                and (type(runner).__module__, type(runner).__name__) == ("vllm_fl.worker.model_runner", "ModelRunnerFL")
                and type(self.scheduler.scheduler_reserve_full_isl) is bool
                and self.scheduler.needs_kv_cache_zeroing is False and self.batch_queue_size == 2)
            _SESSION += 1
            state = {"engine": self, "eligible": eligible, "session": str(os.getpid()) + ":" + str(_SESSION),
                "slot": protocol.HostSlot(MAX_HOST_BYTES), "victim": None, "incarnation": 0, "frame_serial": 0,
                "counts": dict.fromkeys(("saved", "restored", "published", "rollbacks", "save_skips", "restore_skips", "fast_rejects"), 0)}
            self.__dict__[_MARKER] = state
            if eligible and not getattr(type(runner), _MARKER + "_runner", False):
                method = type(runner)._update_states
                if (hashlib.sha256(Path(inspect.getfile(type(runner))).read_bytes()).hexdigest()
                        != "03a0e007e820644d55ac5eaf3331416da3fb0e58147a4f57928d363cc8ff6fb2"
                        or inspect.unwrap(method) is not method):
                    raise RuntimeError("runner source/method不是原e155")
                type(runner)._update_states = _wrap_runner_states(method)
                setattr(type(runner), _MARKER + "_runner", True)
            _emit(state, "FIRST_CHECKED", eligible=eligible)
        if not state["eligible"]:
            return original(self, *args, **kwargs)
        token = _ACTIVE.set(state)
        try:
            result = original(self, *args, **kwargs)
            victim = state["victim"]
            if victim is not None:
                request = victim["request"]
                if self.scheduler.requests.get(request.request_id) is not request or request.is_finished():
                    victim["tx"].cancel()
                    _drop(state, victim)
            return result
        finally:
            _ACTIVE.reset(token)
    return step


def install(*, enabled=False):
    if enabled is not True:
        return False
    if hashlib.sha256(Path(scope_probe.__file__).read_bytes()).hexdigest() != "a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6":
        raise RuntimeError("unaudited scope helper")
    modules = {name: importlib.import_module(name) for name in {**scope_probe.EXPECTED_SOURCES, **EXPECTED_EXTRA}}
    for name, expected in {**scope_probe.EXPECTED_SOURCES, **EXPECTED_EXTRA}.items():
        if hashlib.sha256(Path(modules[name].__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("unaudited KV protocol source: " + name)
    core = modules["vllm.v1.engine.core"].EngineCore
    if getattr(core, _MARKER, False):
        return False
    scheduler = modules["vllm.v1.core.sched.scheduler"].Scheduler
    original = scheduler.schedule
    if inspect.unwrap(original) is not original or original.__code__.co_freevars:
        raise RuntimeError("unexpected schedule wrapper/closure")
    for cls, name in ((scheduler, "_preempt_request"), (scheduler, "update_from_output"),
                      (core, "step_with_batch_queue")):
        method = getattr(cls, name)
        if (inspect.unwrap(method) is not method
                or Path(method.__code__.co_filename).resolve() != Path(modules[cls.__module__].__file__).resolve()):
            raise RuntimeError("unexpected pre-existing protocol method wrapper")
    source = textwrap.dedent(inspect.getsource(original))
    needle = "            # Get already-cached tokens.\n"
    if source.count(needle) != 1:
        raise RuntimeError("exact waiting restore切口不唯一")
    changed = source.replace(needle, "            _biv150_restore_before_admit(self, request, token_budget)\n" + needle)
    namespace = dict(original.__globals__)
    namespace["_biv150_restore_before_admit"] = _try_restore
    exec(compile(changed, "<biv150-private-kv-protocol-schedule>", "exec"), namespace)
    classes = {"schedulers": (scheduler, modules["vllm.v1.core.sched.async_scheduler"].AsyncScheduler),
        "manager": modules["vllm.v1.core.kv_cache_manager"].KVCacheManager,
        "coordinator": modules["vllm.v1.core.kv_cache_coordinator"].UnitaryKVCacheCoordinator,
        "full_manager": modules["vllm.v1.core.single_type_kv_cache_manager"].FullAttentionManager,
        "full_spec": importlib.import_module("vllm.v1.kv_cache_interface").FullAttentionSpec,
        "executor": modules["vllm.v1.executor.uniproc_executor"].UniProcExecutor,
        "wrapper": modules["vllm.v1.worker.worker_base"].WorkerWrapperBase}
    scheduler.schedule = _wrap_schedule(original, namespace["schedule"])
    scheduler._preempt_request = _wrap_preempt(scheduler._preempt_request)
    scheduler.update_from_output = _wrap_update(scheduler.update_from_output)
    core.step_with_batch_queue = _wrap_core(core.step_with_batch_queue, classes)
    setattr(core, _MARKER, True)
    print("BIV150_KV_PROTOCOL_INSTALLED pid=" + str(os.getpid()), flush=True)
    return True
