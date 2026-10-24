"""当前446的单RID抢占/恢复CPU诊断；不采设备、不改变原调度或采样。"""
from collections import deque
from functools import wraps
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys
import textwrap
import time
from types import MethodType

EXPECTED = {
    'vllm.v1.engine.core': '27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71',
    'vllm.v1.executor.uniproc_executor': '4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe',
    'vllm.v1.worker.worker_base': '7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe',
    'vllm.v1.core.sched.scheduler': 'df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090',
    'vllm.v1.core.sched.async_scheduler': 'da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884',
    'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320',
    'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b',
    'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914',
    'vllm.v1.kv_cache_interface': '7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003',
    'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80',
    'vllm.v1.core.sched.output': 'f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d',
    'vllm_fl.worker.worker': 'a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24',
    'vllm_fl.worker.model_runner': '183de0ab77ab27235eec00e231eb96d4a3b4037a9f628b9397cbe53d17fa3cab',
    'vllm_fl.patches.biv150_compute_order': '5bc850ebe2643cc4a553efa8e9508871be87d60a3fc30a3053e158b03938cd68',
    'vllm_fl.patches.biv150_prefill_normalized': '24a421fa25e0ce7e21b54deb760a5bc893d3899a86ced4849bd3f3bfab50ed42',
    'vllm_fl.patches.biv150_gqa_decode': '1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a',
}
SCHEDULE_SHA = '87a6016cdb08ae0d5bdb3fc2c14cb6974467a76b58d0ed41c35aadf1b697a8dd'
WAIT_BEFORE = '            new_blocks = self.kv_cache_manager.allocate_slots(\n                request,\n                num_new_tokens,\n                num_new_computed_tokens=num_new_local_computed_tokens,\n'
WAIT_AFTER = '            if new_blocks is None:\n                # The request cannot be scheduled.\n\n                # NOTE: we need to untouch the request from the encode cache\n'
ADMITTED = '            request.status = RequestStatus.RUNNING\n            request.num_computed_tokens = num_computed_tokens\n'
CALLS = (
    '            _resume_ticket = _resume_before(self, request, num_new_tokens, num_new_local_computed_tokens, num_external_computed_tokens, new_computed_blocks, num_computed_tokens)\n',
    '            _resume_allocated(self, _resume_ticket, new_blocks)\n',
    '            _resume_committed(self, request, _resume_ticket)\n',
)


def transform_schedule(source):
    if hashlib.sha256(source.encode()).hexdigest() != SCHEDULE_SHA:
        raise ValueError('非固定df780 schedule')
    result = source
    for old, new in ((WAIT_BEFORE, CALLS[0] + WAIT_BEFORE),
                     (WAIT_AFTER, CALLS[1] + WAIT_AFTER), (ADMITTED, ADMITTED + CALLS[2])):
        if result.count(old) != 1:
            raise ValueError('观察锚不唯一')
        result = result.replace(old, new, 1)
    reverse = result
    for call in CALLS:
        if reverse.count(call) != 1:
            raise ValueError('观察callback不唯一')
        reverse = reverse.replace(call, '', 1)
    if reverse != source:
        raise ValueError('schedule逆回不等原字节')
    return result


def emit(event, **fields):
    try:
        print('BIV150_RESUME_CPU ' + json.dumps(dict(event=event, pid=os.getpid(),
            monotonic_ns=time.monotonic_ns(), device_api_calls=False,
            future_readiness_queried=False, gpu_completed_floor=None, **fields), sort_keys=True), flush=True)
    except Exception:
        pass


def integer(value):
    if type(value) is not int or value < 0:
        raise ValueError('未知CPU计数字段')
    return value


class Observer:
    def __init__(self, engine):
        modules = {}
        for name, pin in EXPECTED.items():
            module = sys.modules.get(name)
            if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
                raise ValueError('自然加载源不符: ' + name)
            modules[name] = module
        scheduler = engine.scheduler
        manager = scheduler.kv_cache_manager
        coordinator = manager.coordinator
        groups = manager.kv_cache_config.kv_cache_groups
        cfg, parallel = engine.vllm_config, engine.vllm_config.parallel_config
        model, text = cfg.model_config, cfg.model_config.hf_text_config
        executor = engine.model_executor
        wrapper = executor.__dict__.get('driver_worker')
        worker = None if wrapper is None else wrapper.__dict__.get('worker')
        runner = None if worker is None else worker.__dict__.get('model_runner')
        if not (type(engine) is modules['vllm.v1.engine.core'].EngineCoreProc
            and type(executor) is modules['vllm.v1.executor.uniproc_executor'].UniProcExecutor
            and type(wrapper) is modules['vllm.v1.worker.worker_base'].WorkerWrapperBase
            and type(worker) is modules['vllm_fl.worker.worker'].WorkerFL
            and type(runner) is modules['vllm_fl.worker.model_runner'].ModelRunnerFL
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
            raise ValueError('非当前446/单组Full/Async队列2子集')
        self.engine, self.scheduler, self.runner = engine, scheduler, runner
        self.single = coordinator.single_type_managers[0]
        self.request_cls = modules['vllm.v1.request'].Request
        self.status_cls = modules['vllm.v1.request'].RequestStatus
        self.output_cls = modules['vllm.v1.core.sched.output'].SchedulerOutput
        self.target, self.preempt, self.rows, self.done = None, None, [], False
        self.attempts = 0
        self.bindings = []
        original = modules['vllm.v1.core.sched.scheduler'].Scheduler.schedule
        if ('schedule' in vars(scheduler) or scheduler.schedule.__func__ is not original
            or modules['vllm.v1.core.sched.async_scheduler'].AsyncScheduler.schedule is not original
            or inspect.unwrap(original) is not original or original.__code__.co_freevars):
            raise ValueError('schedule已有wrapper')
        namespace = dict(original.__globals__)
        namespace.update(_resume_before=self.before, _resume_allocated=self.allocated, _resume_committed=self.committed)
        source = textwrap.dedent(inspect.getsource(original))
        exec(compile(transform_schedule(source), '<biv150-resume-cpu>', 'exec'), namespace)
        self.bindings.append((scheduler, 'schedule', MethodType(namespace['schedule'], scheduler)))
        for owner, name in ((scheduler, '_preempt_request'), (runner, 'execute_model'), (runner, 'shutdown')):
            if name in vars(owner):
                raise ValueError('已有实例方法覆盖: ' + name)
        preempt_original, execute_original, shutdown_original = scheduler._preempt_request, runner.execute_model, runner.shutdown
        if (preempt_original.__func__ is not modules['vllm.v1.core.sched.scheduler'].Scheduler._preempt_request
                or execute_original.__func__ is not modules['vllm_fl.worker.model_runner'].ModelRunnerFL.execute_model
                or shutdown_original.__func__ is not modules['vllm_fl.worker.model_runner'].ModelRunnerFL.shutdown):
            raise ValueError('非固定原方法绑定')

        @wraps(preempt_original)
        def preempt(this, request, timestamp):
            try:
                self.preempt_before(request)
            except Exception as error:
                self.error(error)
            return preempt_original(request, timestamp)  # 原调用恰一次，异常原样传播。

        @wraps(execute_original)
        def execute(this, output, *args, **kwargs):
            row = None
            try:
                row = self.execute_before(output)
            except Exception as error:
                self.error(error)
            try:
                result = execute_original(output, *args, **kwargs)
            except BaseException:
                self.finish(False, 'original_execute_exception')
                raise
            try:
                if row is not None and not self.done:
                    row.update(execute_returned=True, execute_return_ns=time.monotonic_ns())
                    self.rows.append(row)
                    emit('TARGET_EXECUTE', target_request_id=self.target.request_id, **row)
                    if row['payload_computed'] + row['target_q'] >= self.preempt['known_tokens']:
                        self.finish(True, 'reached_recorded_preempt_known_endpoint')
                    elif len(self.rows) >= 16:
                        self.finish(False, 'sixteen_target_submissions_limit')
            except Exception as error:
                self.error(error)
            return result

        @wraps(shutdown_original)
        def shutdown(this, *args, **kwargs):
            self.finish(False, 'shutdown_before_target_endpoint' if self.target else 'no_preemption_observed')
            return shutdown_original(*args, **kwargs)

        self.bindings.extend(((scheduler, '_preempt_request', MethodType(preempt, scheduler)),
                              (runner, 'execute_model', MethodType(execute, runner)),
                              (runner, 'shutdown', MethodType(shutdown, runner))))

    def restore(self):
        for owner, name, binding in self.bindings:
            try:
                if vars(owner).get(name) is binding:
                    del vars(owner)[name]
            except Exception:
                pass

    def install(self):
        try:
            for owner, name, binding in self.bindings:
                setattr(owner, name, binding)
        except BaseException:
            self.restore()
            raise
        emit('ARMED', source_count=447, maximum_target_submissions=16, CPU_only=True)
        return self

    def finish(self, complete, reason):
        if self.done:
            return
        self.done = True
        try:
            emit('FINAL', cpu_recording_complete=complete, reason=reason,
                target_request_id=None if self.target is None else self.target.request_id,
                preempt_before=self.preempt, executed_target_rows=self.rows,
                waiting_attempts=self.attempts,
                limits='仅CPU实际提交/原execute返回，非GPU完成、实际GPU重算秒数或性能；不读取future完成态。')
        finally:
            self.restore()

    def error(self, error):
        emit('OBSERVATION_DISABLED', error_type=type(error).__name__)
        self.finish(False, 'observation_error')

    def row(self, request):
        if type(request) is not self.request_cls or self.scheduler.requests.get(request.request_id) is not request:
            raise ValueError('请求身份变化')
        return dict(request_id=request.request_id, request_object_id=id(request), status=request.status.name,
            prompt_tokens=integer(request.num_prompt_tokens), known_tokens=integer(request.num_tokens),
            confirmed_output_tokens=integer(request.num_output_tokens),
            issued_computed_tokens=integer(request.num_computed_tokens),
            output_placeholders=integer(request.num_output_placeholders), num_preemptions=integer(request.num_preemptions),
            is_prefill_chunk=request.is_prefill_chunk)

    def preempt_before(self, request):
        if self.done:
            return
        if self.target is not None:
            if request is self.target:
                self.finish(False, 'target_preempted_again')
            return
        self.preempt = self.row(request)
        if request.status is not self.status_cls.RUNNING:
            raise ValueError('非真实RUNNING preempt参数')
        self.target = request
        frames = []
        for item in self.engine.batch_queue:
            if type(item) is not tuple or len(item) != 3 or type(item[1]) is not self.output_cls:
                raise ValueError('未知队列帧，不查询future')
            frames.append(dict(output_object_id=id(item[1]), target_q=integer(item[1].num_scheduled_tokens.get(request.request_id, 0))))
        emit('PREEMPT_BEFORE', candidate=self.preempt, scheduler_step=integer(self.scheduler.current_step),
            queued_frames=frames, current_schedule_not_yet_issued=True)

    def before(self, scheduler, request, q, local, external, blocks, computed):
        try:
            if self.done or scheduler is not self.scheduler or request is not self.target:
                return None
            if request.status is not self.status_cls.PREEMPTED or request.num_preemptions != self.preempt['num_preemptions'] + 1:
                raise ValueError('非同次抢占恢复')
            self.attempts += 1
            if self.attempts > 4096:
                self.finish(False, 'waiting_attempt_limit')
                return None
            return dict(attempt=self.attempts, candidate_before=self.row(request),
                target_q=integer(q), local_prefix_hit_tokens=integer(local), external_prefix_tokens=integer(external),
                effective_computed_tokens=integer(computed), existing_apc_block_counts=[len(g) for g in blocks.blocks])
        except Exception as error:
            self.error(error)
        return None

    def allocated(self, scheduler, ticket, result):
        try:
            if self.done or ticket is None or scheduler is not self.scheduler:
                return
            ticket['allocator_returned_none'] = result is None
            if ticket['attempt'] == 1:
                emit('RESUME_FIRST_ATTEMPT', **ticket)
        except Exception as error:
            self.error(error)

    def committed(self, scheduler, request, ticket):
        try:
            if self.done or ticket is None or scheduler is not self.scheduler:
                return
            if (request is not self.target or ticket.get('allocator_returned_none') is not False
                    or request.status is not self.status_cls.RUNNING or not any(r is request for r in scheduler.running)):
                raise ValueError('缺实际准入成功')
            emit('RESUME_ADMITTED', **ticket, candidate_after=self.row(request),
                computed_update_after_schedule_not_yet_applied=True)
        except Exception as error:
            self.error(error)

    def execute_before(self, output):
        if self.done or self.target is None:
            return None
        rid = self.target.request_id
        if rid in output.finished_req_ids or self.scheduler.requests.get(rid) is not self.target:
            self.finish(False, 'target_lifecycle_ended_or_changed')
            return None
        q = integer(output.num_scheduled_tokens.get(rid, 0))
        if not q:
            return None
        computed, origin = None, None
        for request in output.scheduled_new_reqs:
            if request.req_id == rid:
                computed, origin = integer(request.num_computed_tokens), 'new_request_payload'
        cached = output.scheduled_cached_reqs
        for index, name in enumerate(cached.req_ids):
            if name == rid:
                if computed is not None:
                    raise ValueError('同RID两份payload')
                computed, origin = integer(cached.num_computed_tokens[index]), 'cached_request_payload'
        if computed is None:
            raise ValueError('缺本次computed payload')
        values = tuple(output.num_scheduled_tokens.values())
        return dict(N=len(values), M=sum(values), target_q=q, payload_computed=computed,
            computed_source=origin, scheduler_output_object_id=id(output),
            execute_submit_start_ns=time.monotonic_ns(), optimistic_after_schedule=computed + q)


def install(*, enabled=False):
    if enabled is not True:
        return None
    module = sys.modules.get('vllm.v1.engine.core')
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED[module.__name__]:
        raise ValueError('原Core尚未自然加载')
    core, original = module.EngineCore, module.EngineCore.step_with_batch_queue
    if inspect.unwrap(original) is not original or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve():
        raise ValueError('Core已有wrapper')
    attempted, handles, owners = False, [], []

    def retire(engine):
        try:
            bound = vars(engine).get('step_fn')
            if getattr(bound, '__self__', None) is engine and getattr(bound, '__func__', None) is step:
                engine.step_fn = original.__get__(engine, type(engine))
            if core.step_with_batch_queue is step:
                core.step_with_batch_queue = original
        except Exception:
            pass

    @wraps(original)
    def step(engine, *args, **kwargs):
        nonlocal attempted
        if not attempted:
            attempted = True
            owners.append(engine)
            try:
                handles.append(Observer(engine).install())
            except Exception as error:
                emit('SCOPE_REJECTED', error_type=type(error).__name__)
            finally:
                retire(engine)
        return original(engine, *args, **kwargs)

    def restore():
        for handle in handles:
            handle.finish(False, 'process_exit_before_target_endpoint')
        for engine in owners:
            retire(engine)
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    core.step_with_batch_queue = step
    return {'restore': restore, 'handles': handles}
