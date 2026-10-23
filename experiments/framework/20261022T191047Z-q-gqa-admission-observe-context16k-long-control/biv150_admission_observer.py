"""默认关闭的稀疏CPU准入观察；不预留KV、不改变调度、无设备API。"""
from collections import deque
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap
from types import MethodType

EXPECTED = {
    "vllm.v1.engine.core": "27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71",
    "vllm.v1.executor.uniproc_executor": "4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe",
    "vllm.v1.core.sched.scheduler": "df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090",
    "vllm.v1.core.sched.async_scheduler": "da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884",
    "vllm.v1.core.kv_cache_manager": "2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320",
    "vllm.v1.core.kv_cache_coordinator": "9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b",
    "vllm.v1.core.single_type_kv_cache_manager": "22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914",
    "vllm.v1.kv_cache_interface": "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003",
    "vllm.v1.request": "06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80",
    "vllm.v1.core.sched.output": "f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d",
    "vllm_fl.worker.model_runner": "cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663",
    "vllm_fl.patches.biv150_q_fragment_service": "51fcaf55133124c2e51dfa0385e1939bf908b65f8444ac63f912329f6ca73800",
    "vllm_fl.patches.biv150_gqa_decode": "1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a",
}
SCHEDULE_SHA = "87a6016cdb08ae0d5bdb3fc2c14cb6974467a76b58d0ed41c35aadf1b697a8dd"
WAIT_BEFORE = "            new_blocks = self.kv_cache_manager.allocate_slots(\n                request,\n                num_new_tokens,\n                num_new_computed_tokens=num_new_local_computed_tokens,\n"
WAIT_AFTER = "            if new_blocks is None:\n                # The request cannot be scheduled.\n\n                # NOTE: we need to untouch the request from the encode cache\n"
ADMITTED = "            request.status = RequestStatus.RUNNING\n            request.num_computed_tokens = num_computed_tokens\n"
FAILED = "                # The request cannot be scheduled.\n                # Preempt the lowest-priority request.\n"
PRE_CALL = "            _admission_ticket = _biv150_admission_before(self, request, num_new_tokens, num_new_local_computed_tokens, num_external_computed_tokens, new_computed_blocks, num_computed_tokens, token_budget, num_scheduled_tokens, reserved_blocks, effective_lookahead_tokens, load_kv_async, num_encoder_tokens)\n"
POST_CALL = "            _biv150_admission_allocated(self, _admission_ticket, new_blocks)\n"
ADMIT_CALL = "            _biv150_admission_committed(self, request, _admission_ticket, token_budget, num_scheduled_tokens)\n"
FAIL_CALL = "                _biv150_admission_running_failure(self, request, num_new_tokens, token_budget, req_index, num_scheduled_tokens)\n"


def transform_schedule(source):
    if hashlib.sha256(source.encode()).hexdigest() != SCHEDULE_SHA:
        raise ValueError("非exact df780原schedule方法")
    pairs = [(WAIT_BEFORE, PRE_CALL + WAIT_BEFORE), (WAIT_AFTER, POST_CALL + WAIT_AFTER),
             (ADMITTED, ADMITTED + ADMIT_CALL), (FAILED, FAIL_CALL + FAILED)]
    changed = source
    for before, after in pairs:
        if changed.count(before) != 1:
            raise ValueError("调度观察锚不唯一")
        changed = changed.replace(before, after, 1)
    restored = changed
    for call in (PRE_CALL, POST_CALL, ADMIT_CALL, FAIL_CALL):
        if restored.count(call) != 1:
            raise ValueError("callback不唯一")
        restored = restored.replace(call, "", 1)
    if restored != source:
        raise ValueError("调度原文逆回失败")
    return changed


def emit(event, **fields):
    try:
        print("BIV150_ADMISSION_OBSERVER " + json.dumps({"event": event, "pid": os.getpid(),
              "diagnostic_only": True, "device_api_calls": False, "future_readiness_queried": False,
              **fields}, sort_keys=True), flush=True)
    except Exception:
        pass


def integer(value):
    if type(value) is not int or value < 0:
        raise ValueError("非预期CPU非负整数")
    return value


def counts(value):
    if type(value) is not dict or any(type(k) is not str or type(v) is not int or v < 0 for k, v in value.items()):
        raise ValueError("未知scheduled映射")
    return dict(value)


class Observer:
    def __init__(self, engine):
        modules = {}
        for name, pin in EXPECTED.items():
            module = sys.modules.get(name)
            if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
                raise ValueError("自然加载源不符: " + name)
            modules[name] = module
        scheduler = engine.scheduler
        manager = scheduler.kv_cache_manager
        coordinator = manager.coordinator
        groups = manager.kv_cache_config.kv_cache_groups
        cfg, parallel = engine.vllm_config, engine.vllm_config.parallel_config
        model, text = cfg.model_config, cfg.model_config.hf_text_config
        if not (type(engine) is modules['vllm.v1.engine.core'].EngineCoreProc
            and type(engine.model_executor) is modules['vllm.v1.executor.uniproc_executor'].UniProcExecutor
            and type(scheduler) is modules['vllm.v1.core.sched.async_scheduler'].AsyncScheduler
            and type(manager) is modules['vllm.v1.core.kv_cache_manager'].KVCacheManager
            and type(coordinator) is modules['vllm.v1.core.kv_cache_coordinator'].UnitaryKVCacheCoordinator
            and len(groups) == 1 and type(groups[0].kv_cache_spec) is modules['vllm.v1.kv_cache_interface'].FullAttentionSpec
            and groups[0].kv_cache_spec.block_size == 16 and len(groups[0].layer_names) == 42
            and len(coordinator.single_type_managers) == 1
            and type(coordinator.single_type_managers[0]) is modules['vllm.v1.core.single_type_kv_cache_manager'].FullAttentionManager
            and type(engine.batch_queue) is deque and engine.batch_queue_size == 2
            and scheduler.scheduler_reserve_full_isl is True and scheduler.defer_block_free is False
            and scheduler.connector is None and scheduler.ec_connector is None
            and scheduler.num_lookahead_tokens == 0 and scheduler.policy.value == 'fcfs'
            and cfg.speculative_config is None and cfg.lora_config is None
            and cfg.kv_transfer_config is None and cfg.ec_transfer_config is None
            and Path(str(model.model).rstrip('/\\')).name == 'MiniCPM5-2B'
            and str(model.dtype) == 'torch.bfloat16' and model.quantization is None
            and (text.hidden_size, text.num_hidden_layers, text.num_attention_heads, text.num_key_value_heads) == (2048,42,16,2)
            and all(getattr(parallel, key, None) == 1 for key in ('tensor_parallel_size','pipeline_parallel_size','data_parallel_size','decode_context_parallel_size','prefill_context_parallel_size'))
            and parallel.use_ubatching is False):
            raise ValueError('非当前QGQA/单组FullAttention/Async队列2子集')
        self.engine, self.scheduler, self.manager = engine, scheduler, manager
        self.single = coordinator.single_type_managers[0]
        self.request_cls = modules['vllm.v1.request'].Request
        self.status_cls = modules['vllm.v1.request'].RequestStatus
        self.output_cls = modules['vllm.v1.core.sched.output'].SchedulerOutput
        self.attempted, self.admitted = set(), set()
        self.attempt_count, self.failures, self.disabled = 0, 0, False
        self.original = scheduler.schedule
        original = modules['vllm.v1.core.sched.scheduler'].Scheduler.schedule
        if ('schedule' in vars(scheduler) or self.original.__func__ is not original
            or modules['vllm.v1.core.sched.async_scheduler'].AsyncScheduler.schedule is not original
            or inspect.unwrap(original) is not original or original.__code__.co_freevars):
            raise ValueError('schedule已有wrapper')
        for name in ('allocate_slots',):
            fn = getattr(type(manager), name)
            if name in vars(manager) or inspect.unwrap(fn) is not fn or Path(fn.__code__.co_filename).resolve() != Path(modules['vllm.v1.core.kv_cache_manager'].__file__).resolve():
                raise ValueError('allocator被替换')
        self.source = textwrap.dedent(inspect.getsource(original))
        namespace = dict(original.__globals__)
        namespace.update(_biv150_admission_before=self.before,
                         _biv150_admission_allocated=self.allocated,
                         _biv150_admission_committed=self.committed,
                         _biv150_admission_running_failure=self.running_failure)
        exec(compile(transform_schedule(self.source), '<biv150-admission-observer>', 'exec'), namespace)
        self.binding = MethodType(namespace['schedule'], scheduler)

    def error(self, error):
        self.disabled = True
        emit('OBSERVATION_DISABLED', error_type=type(error).__name__)

    def rows(self):
        rows = []
        for index, req in enumerate(self.scheduler.running):
            rows.append(self.row(req, index))
        return rows

    def row(self, req, index=None):
        if type(req) is not self.request_cls or self.scheduler.requests.get(req.request_id) is not req:
            raise ValueError('请求对象身份变化')
        blocks = self.single.req_to_blocks.get(req.request_id)
        if blocks is not None and type(blocks) is not list:
            raise ValueError('owned页列表类型变化')
        cached = self.single.num_cached_block.get(req.request_id)
        return {'running_index': index, 'request_id': req.request_id, 'request_object_id': id(req),
            'status': req.status.name, 'prompt_tokens': integer(req.num_prompt_tokens),
            'known_tokens': integer(req.num_tokens), 'confirmed_output_tokens': integer(req.num_output_tokens),
            'max_tokens': integer(req.max_tokens), 'issued_computed_tokens': integer(req.num_computed_tokens),
            'output_placeholders': integer(req.num_output_placeholders), 'is_prefill_chunk': req.is_prefill_chunk,
            'next_decode_eligible_step': integer(req.next_decode_eligible_step), 'num_preemptions': integer(req.num_preemptions),
            'owned_logical_pages': 0 if blocks is None else len(blocks), 'owned_mapping_present': blocks is not None,
            'cached_full_pages': None if cached is None else integer(cached),
            'resumable': req.resumable, 'structured_output': req.use_structured_output,
            'has_encoder_inputs': req.has_encoder_inputs, 'has_mm_features': bool(req.mm_features)}

    def state(self, scheduled, budget):
        queue = self.engine.batch_queue
        if type(queue) is not deque:
            raise ValueError('异步队列类型变化')
        frames = []
        for i, item in enumerate(queue):
            if type(item) is not tuple or len(item) != 3 or type(item[1]) is not self.output_cls:
                raise ValueError('未知异步帧；不猜完成态')
            frames.append({'deque_index': i, 'output_object_id': id(item[1]),
                           'scheduled_tokens': counts(item[1].num_scheduled_tokens)})
        return {'scheduler_step': integer(self.scheduler.current_step), 'running_count': len(self.scheduler.running),
            'free_blocks': integer(self.manager.block_pool.free_block_queue.num_free_blocks),
            'pool_blocks_including_null': integer(self.manager.block_pool.num_gpu_blocks),
            'watermark_blocks': integer(self.manager.watermark_blocks),
            'current_scheduled_tokens_not_yet_issued': counts(scheduled), 'remaining_token_budget': integer(budget),
            'running': self.rows(), 'queue_size': self.engine.batch_queue_size, 'queued_frames': frames,
            'owned_counts_are_logical_not_unique_releasable': True, 'gpu_completed_prefix_unknown': True}

    def before(self, scheduler, request, q, local, external, blocks, computed, budget, scheduled,
               reserved, lookahead, load_async, encoder):
        try:
            if self.disabled or scheduler is not self.scheduler or len(scheduler.running) < 29:
                return None
            key = (request.request_id, integer(request.num_preemptions), request.status.name)
            if key in self.admitted:
                return None
            if request.status not in (self.status_cls.WAITING, self.status_cls.PREEMPTED):
                raise ValueError('非WAITING准入状态')
            if self.attempt_count >= 4096 or (key not in self.attempted and len(self.attempted) >= 8):
                self.disabled = True
                emit('OBSERVATION_LIMIT', attempts=self.attempt_count, keys=len(self.attempted))
                return None
            first = key not in self.attempted
            self.attempted.add(key)
            self.attempt_count += 1
            # 保存首次成功前的真实CPU状态：重试只临时O(N)标量复制，不遍历KV页、不逐步输出。
            return {'key': key, 'first_attempt': first, 'attempt_index': self.attempt_count,
                'before_allocate': self.state(scheduled, budget), 'candidate_before': self.row(request),
                'allocation_args': {'num_new_tokens': integer(q), 'local_prefix_hit_tokens': integer(local),
                    'external_prefix_tokens': integer(external), 'existing_apc_block_counts': [len(g) for g in blocks.blocks],
                    'effective_computed_tokens': integer(computed), 'reserved_blocks': integer(reserved),
                    'lookahead_tokens': integer(lookahead), 'load_kv_async': load_async, 'encoder_tokens': integer(encoder),
                    'full_sequence_must_fit': scheduler.scheduler_reserve_full_isl}}
        except Exception as error:
            self.error(error)
        return None

    def allocated(self, scheduler, ticket, result):
        try:
            if self.disabled or ticket is None or scheduler is not self.scheduler:
                return
            ticket['allocator_returned_none'] = result is None
            ticket['after_allocate_free_blocks'] = integer(self.manager.block_pool.free_block_queue.num_free_blocks)
            if result is not None:
                ticket['new_allocated_block_counts'] = [len(g) for g in result.blocks]
            elif ticket['first_attempt']:
                emit('WAITING_FIRST_ATTEMPT', **ticket)
        except Exception as error:
            self.error(error)

    def committed(self, scheduler, request, ticket, budget, scheduled):
        try:
            if self.disabled or ticket is None or scheduler is not self.scheduler:
                return
            if request.status is not self.status_cls.RUNNING or not any(r is request for r in scheduler.running):
                raise ValueError('准入后的原running状态不符')
            if ticket.get('allocator_returned_none') is not False:
                raise ValueError('缺成功allocator阶段')
            self.admitted.add(ticket['key'])
            emit('WAITING_FIRST_ADMISSION', **ticket, after_admission_before_update=self.state(scheduled, budget),
                 candidate_after=self.row(request), computed_update_after_schedule_not_yet_applied=True)
        except Exception as error:
            self.error(error)

    def running_failure(self, scheduler, request, q, budget, index, scheduled):
        try:
            if self.disabled or self.failures or scheduler is not self.scheduler:
                return
            self.failures += 1
            emit('FIRST_RUNNING_ALLOCATION_FAILURE', candidate=self.row(request), failed_running_index=index,
                 num_new_tokens=q, state=self.state(scheduled, budget), original_victim_policy_unchanged=True)
        except Exception as error:
            self.error(error)

    def install(self):
        self.scheduler.schedule = self.binding
        return self

    def restore(self):
        self.disabled = True
        if vars(self.scheduler).get('schedule') is self.binding:
            del self.scheduler.__dict__['schedule']


def install(*, enabled=False):
    if enabled is not True:
        return None
    module = sys.modules.get('vllm.v1.engine.core')
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED[module.__name__]:
        raise ValueError('Core未自然加载/源码变化')
    core, original = module.EngineCore, module.EngineCore.step_with_batch_queue
    if inspect.unwrap(original) is not original or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve():
        raise ValueError('Core已有wrapper')
    observers, checked = [], set()
    @wraps(original)
    def step(engine, *args, **kwargs):
        try:
            if id(engine) not in checked:
                checked.add(id(engine))
                observer = Observer(engine).install()
                observers.append(observer)
                emit('ARMED', source_reverse_exact=True, base_source_count=414,
                     minimum_running_before_admission=29, maximum_keys=8, maximum_attempts=4096,
                     limits='CPU临时状态复制及日志均属诊断开销，不作为吞吐；不读取EOS未来、不预测页释放。')
        except Exception as error:
            emit('SCOPE_REJECTED', error_type=type(error).__name__)
        return original(engine, *args, **kwargs)
    def restore():
        for observer in observers:
            try:
                emit('FINAL', attempts=observer.attempt_count, admitted_keys=len(observer.admitted),
                     running_failures=observer.failures, disabled=observer.disabled, whole_workload_coverage_not_asserted=True)
                observer.restore()
            except Exception:
                pass
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original
    core.step_with_batch_queue = step
    return {'restore': restore, 'observers': observers}
