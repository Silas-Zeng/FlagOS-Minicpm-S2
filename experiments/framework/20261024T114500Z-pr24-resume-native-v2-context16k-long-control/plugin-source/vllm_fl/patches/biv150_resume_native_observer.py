"""PR24恢复窗口native诊断；独立模块保持runner/P/Q/native原字节。"""
from collections import deque
from functools import wraps
import hashlib, inspect, json, os, sys
from pathlib import Path
EXPECTED = {'vllm.v1.engine.core': '27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71', 'vllm.v1.executor.uniproc_executor': '4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe', 'vllm.v1.worker.worker_base': '7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe', 'vllm.v1.core.sched.scheduler': 'df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090', 'vllm.v1.core.sched.async_scheduler': 'da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884', 'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320', 'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b', 'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914', 'vllm.v1.kv_cache_interface': '7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003', 'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80', 'vllm.v1.core.sched.output': 'f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d', 'vllm_fl.worker.worker': 'a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24', 'vllm_fl.worker.model_runner': '677def25d5391887145b0bbabb2222531887c6f7c48b6ea53c1859ad08d8ef61', 'vllm_fl.patches.biv150_compute_order': 'a467c937dc6b4932944e70671259dcf87b05b51a61dd894dccbb97754fefbf0c', 'vllm_fl.patches.biv150_prefill_normalized': '24a421fa25e0ce7e21b54deb760a5bc893d3899a86ced4849bd3f3bfab50ed42', 'vllm_fl.patches.biv150_q_fragment_service': 'ea361e6b604fbd3c7e3a6b95776892a7bc9d22e9988927db3f7876412c6e310f', 'vllm_fl.patches.biv150_native_w8a8': '98ad16de1c25e914959c54d8f3352e6530b170d710d4abb7b41c334b4696f8a9', 'vllm_fl.patches.biv150_gqa_decode': '1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a', 'vllm_fl.dispatch.io_common': '6d8b4adf9ad75a5b79569e4ccc132c1ee69fd525198b3c4e25e2d6de6f3fff55'}

def check_pr24_native(modules):
    # 只核自然加载模块、Python绑定和构建凭据；不访问tensor/device/Future。
    native = modules['vllm_fl.patches.biv150_native_w8a8']
    q_module = modules['vllm_fl.patches.biv150_q_fragment_service']
    torch = sys.modules.get('torch')
    linear = sys.modules.get('vllm.model_executor.layers.linear')
    llama = sys.modules.get('vllm.model_executor.models.llama')
    if torch is None or linear is None or llama is None or native._LOADED is not True:
        raise ValueError('PR24 native尚未自然加载')
    if native._STATE.get('quantized_layers') != 34:
        raise ValueError('PR24 native未完成34层权重接入')
    for function, name in (
        (linear.UnquantizedLinearMethod.process_weights_after_loading, 'after'),
        (linear.UnquantizedLinearMethod.apply, 'apply'),
        (llama.LlamaMLP.forward, 'forward'),
    ):
        if (not inspect.isfunction(function) or function.__globals__ is not vars(native)
                or function.__qualname__ != 'install.<locals>.' + name
                or Path(function.__code__.co_filename).resolve() != Path(native.__file__).resolve()):
            raise ValueError('PR24 native实际方法绑定变化: ' + name)
    manager = q_module._MANAGER
    if (manager is None or manager.active is not True
            or manager.holder[manager.kernel_key] is not manager.wrapper):
        raise ValueError('PR24 Q实际kernel绑定变化')
    receipt_path = Path(os.environ['BIV150_RESUME_NATIVE_RECEIPT'])
    raw = receipt_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != os.environ['BIV150_RESUME_NATIVE_RECEIPT_SHA256']:
        raise ValueError('native构建凭据变化')
    receipt = json.loads(raw)
    library = Path(os.environ['BIV150_NATIVE_W8A8_LIBRARY']).resolve(strict=True)
    if (library != Path(receipt['runtime_library']).resolve(strict=True)
            or hashlib.sha256(library.read_bytes()).hexdigest() != receipt['library_sha256']
            or str(library) not in {str(Path(p).resolve()) for p in torch.ops.loaded_libraries}
            or str(torch.__version__) != receipt['abi']['torch_version']
            or bool(torch._C._GLIBCXX_USE_CXX11_ABI) is not receipt['abi']['cxx11_abi']):
        raise ValueError('PR24实际native库/ABI不符')
    emit('PR24_NATIVE_SCOPE', quantized_layers=34, library_sha256=receipt['library_sha256'],
         torch_version=str(torch.__version__), cxx11_abi=bool(torch._C._GLIBCXX_USE_CXX11_ABI),
         source_tree=receipt['source_tree'], native_methods_identity=True,
         q_kernel_binding_identity=True)



def emit(event, **fields):
    print('BIV150_RESUME_NATIVE ' + json.dumps(dict(event=event, pid=os.getpid(), **fields)), flush=True)


def check_runner_bindings(runner, modules):
    cls = type(runner)
    module = modules[cls.__module__]
    io = modules['vllm_fl.dispatch.io_common']
    for name in ('execute_model', 'shutdown'):
        method = getattr(cls, name)
        bound = getattr(runner, name)
        if (name in vars(runner) or not inspect.isfunction(method)
                or getattr(bound, '__self__', None) is not runner
                or getattr(bound, '__func__', None) is not method):
            raise ValueError('非固定runner实例绑定: ' + name)
        if name == 'execute_model':
            cells = dict(zip(method.__code__.co_freevars, method.__closure__ or ()))
            raw = getattr(method, '__wrapped__', None)
            if (method.__globals__ is not vars(io)
                    or Path(method.__code__.co_filename).resolve() != Path(io.__file__).resolve()
                    or method.__code__.co_qualname != 'managed_inference_mode.<locals>.decorator.<locals>.wrapper'
                    or set(cells) != {'fn'} or cells['fn'].cell_contents is not raw
                    or not inspect.isfunction(raw) or hasattr(raw, '__wrapped__')
                    or raw.__globals__ is not vars(module)
                    or raw.__code__.co_qualname != 'ModelRunnerFL.execute_model'
                    or Path(raw.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
                raise ValueError('execute_model不是固定managed_inference_mode单层链')
        elif (inspect.unwrap(method) is not method or method.__globals__ is not vars(module)
                or method.__code__.co_qualname != 'ModelRunnerFL.shutdown'
                or Path(method.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise ValueError('shutdown不是固定原函数')


def install(*, enabled=False):
    if enabled is not True:
        return None
    module = sys.modules.get('vllm.v1.engine.core')
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED[module.__name__]:
        raise ValueError('原Core尚未自然加载')
    core, original = module.EngineCore, module.EngineCore.step_with_batch_queue
    if inspect.unwrap(original) is not original or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve():
        raise ValueError('Core已有wrapper')
    attempted, owners, handles = False, [], []

    def retire(engine):
        bound = vars(engine).get('step_fn')
        if getattr(bound, '__self__', None) is engine and getattr(bound, '__func__', None) is step:
            engine.step_fn = original.__get__(engine, type(engine))
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    @wraps(original)
    def step(engine, *args, **kwargs):
        nonlocal attempted
        if not attempted:
            attempted = True
            owners.append(engine)
            try:
                modules = {}
                for name, pin in EXPECTED.items():
                    item = sys.modules.get(name)
                    if item is None or hashlib.sha256(Path(item.__file__).read_bytes()).hexdigest() != pin:
                        raise ValueError('自然加载源不符: ' + name)
                    modules[name] = item
                check_pr24_native(modules)
                executor = engine.model_executor
                wrapper = vars(executor).get('driver_worker')
                worker = None if wrapper is None else vars(wrapper).get('worker')
                runner = None if worker is None else vars(worker).get('model_runner')
                if not (type(engine) is module.EngineCoreProc
                    and type(executor) is modules['vllm.v1.executor.uniproc_executor'].UniProcExecutor
                    and type(wrapper) is modules['vllm.v1.worker.worker_base'].WorkerWrapperBase
                    and type(worker) is modules['vllm_fl.worker.worker'].WorkerFL
                    and type(runner) is modules['vllm_fl.worker.model_runner'].ModelRunnerFL
                    and type(engine.batch_queue) is deque and engine.batch_queue_size == 2):
                    raise ValueError('非当前UniProc/WorkerFL/队列2')
                check_runner_bindings(runner, modules)
                handles.append(install_runner(runner))
            except Exception as error:
                emit('SCOPE_REJECTED', error_type=type(error).__name__)
                raise
            finally:
                retire(engine)
        return original(engine, *args, **kwargs)

    def restore():
        for handle in handles:
            handle()
        for engine in owners:
            retire(engine)
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    core.step_with_batch_queue = step
    return {'restore': restore}


def install_runner(runner):
    ModelRunnerFL = type(runner)
    torch = sys.modules["torch"]
    # 精确6f原路径：首次实际抢占请求恢复窗口；只诊断，不改调度/数值。
    import functools as _native_functools
    import json as _native_json
    import os as _native_os
    import time as _native_time
    from pathlib import Path as _NativePath


    def _native_event(event, **values):
        path = _native_os.environ.get('MINICPM_NATIVE_PROFILE_EVENTS')
        if path:
            with _NativePath(path).open('a', encoding='utf-8') as handle:
                handle.write(_native_json.dumps(dict(event=event, pid=_native_os.getpid(), monotonic_ns=_native_time.monotonic_ns(),
                    source=__file__, **values)) + '\n')


    def _native_cpu_request(self, rid):
        state = self.requests.get(rid)
        if state is None:
            return {'worker_cached_state_observed': False}
        return {
            'worker_cached_state_observed': True,
            'worker_computed_observed': int(state.num_computed_tokens),
            'prompt_length_observed': len(state.prompt_token_ids) if state.prompt_token_ids is not None else None,
            'output_length_observed': len(state.output_token_ids),
            'known_length_observed': int(state.num_tokens),
            'gpu_completed_floor': None,
            'limit': 'CPU cached state can lag or be optimistic; not GPU completion',
        }


    def _native_payload_computed(output, rid):
        for row in output.scheduled_new_reqs:
            if row.req_id == rid:
                return int(row.num_computed_tokens), 'new_request_payload'
        cached = output.scheduled_cached_reqs
        for index, item in enumerate(cached.req_ids):
            if item == rid:
                return int(cached.num_computed_tokens[index]), 'cached_request_payload'
        return None, 'unobserved'


    _native_event('module_loaded', kind='first_preempted_request_resume_up_to_eight_steps')
    _native_execute_original = ModelRunnerFL.execute_model
    _native_shutdown_original = ModelRunnerFL.shutdown


    def _native_stop(self, complete, reason):
        # 下一execute入口才stop，包含上一个execute外部的sample_tokens。
        torch.cuda.synchronize()
        result = int(torch.cuda.cudart().cudaProfilerStop())
        self._native_profile_active = False
        self._native_profile_done = True
        _native_event('stop' if complete else 'shutdown_incomplete', result=result,
            reason=reason, target_request_id=self._native_preemption_target,
            executed_steps=self._native_resume_steps,
            decode_histogram_partial=getattr(self, '_native_decode_histogram', {}),
            limit='window kernels include all co-batched requests; not per-request causal cost')
        if result:
            raise RuntimeError('cudaProfilerStop failed: ' + str(result))


    @_native_functools.wraps(_native_execute_original)
    def _native_profile_execute(self, scheduler_output, *args, **kwargs):
        # CPU形状累计包括driver单请求smoke；无逐步I/O或设备读取。
        values = list(scheduler_output.num_scheduled_tokens.values())
        histogram = getattr(self, '_native_decode_histogram', None)
        if histogram is None:
            histogram = self._native_decode_histogram = {}
        if values and all(value == 1 for value in values):
            n = len(values)
            histogram[n] = histogram.get(n, 0) + 1
            total = getattr(self, '_native_decode_steps', 0) + 1
            self._native_decode_steps = total
            changed = getattr(self, '_native_last_decode_n', None) != n
            self._native_last_decode_n = n
            change_records = getattr(self, '_native_hist_change_records', 0)
            if total & (total - 1) == 0 or (changed and change_records < 64):
                self._native_hist_change_records = change_records + int(changed)
                try:
                    _native_event('decode_histogram_partial', histogram=dict(histogram),
                        observed_pure_decode_steps=total, includes_driver_smoke=True,
                        workload_complete=False)
                except Exception:
                    pass  # 稀疏CPU观察失败不改变原执行；不逐步flush。

        if getattr(self, '_native_profile_active', False) and self._native_stop_next:
            _native_stop(self, True, self._native_stop_next)
        if getattr(self, '_native_profile_done', False):
            return _native_execute_original(self, scheduler_output, *args, **kwargs)

        if not getattr(self, '_native_preemption_target', None) and scheduler_output.preempted_req_ids:
            # 只绑定首个真实preempt事件；ID只作关联，不作为优化策略。
            rid = sorted(scheduler_output.preempted_req_ids)[0]
            self._native_preemption_target = rid
            self._native_preempt_observation = _native_cpu_request(self, rid)
            self._native_preempt_request_object = self.requests.get(rid)
            _native_event('preempt_observed', target_request_id=rid,
                preempted_request_count=len(scheduler_output.preempted_req_ids),
                observation=self._native_preempt_observation,
                confirmed_floor_observed=False, future_or_device_values_read=False)

        rid = getattr(self, '_native_preemption_target', None)
        if rid and (rid in scheduler_output.finished_req_ids or
                    (self._native_preempt_request_object is not None and
                     self.requests.get(rid) is not self._native_preempt_request_object)):
            if getattr(self, '_native_profile_active', False):
                _native_stop(self, True, 'target_lifecycle_ended_or_changed')
            else:
                self._native_profile_done = True
            _native_event('target_lifecycle_ended_or_changed', target_request_id=rid)
            return _native_execute_original(self, scheduler_output, *args, **kwargs)
        q = scheduler_output.num_scheduled_tokens.get(rid, 0) if rid else 0
        computed, source = _native_payload_computed(scheduler_output, rid) if rid else (None, 'unobserved')
        if (rid and q > 1 and computed is not None and not getattr(self, '_native_profile_active', False)):
            torch.cuda.synchronize()
            result = int(torch.cuda.cudart().cudaProfilerStart())
            if result:
                raise RuntimeError('cudaProfilerStart failed: ' + str(result))
            self._native_profile_active = True
            self._native_resume_steps = []
            self._native_stop_next = None
            _native_event('start', result=result, target_request_id=rid, target_q=q,
                payload_computed=computed, computed_source=source,
                preempt_observation=self._native_preempt_observation,
                confirmed_floor_observed=False, max_consecutive_execute_steps=8)

        # 原调用恰一次，且没有位于捕获原模型异常的except内。
        submit_start = _native_time.monotonic_ns() if getattr(self, '_native_profile_active', False) else None
        result = _native_execute_original(self, scheduler_output, *args, **kwargs)
        if getattr(self, '_native_profile_active', False):
            row = {'execute_submit_start_ns': submit_start,
                   'execute_return_ns': _native_time.monotonic_ns(), 'N': len(values), 'M': sum(values), 'max_q': max(values, default=0),
                   'scheduled_q': values, 'target_request_id': rid, 'target_q': q,
                   'payload_computed': computed, 'computed_source': source,
                   'optimistic_after_schedule': computed + q if computed is not None else None,
                   'execute_returned': True, 'gpu_completed_at_return_not_asserted': True}
            self._native_resume_steps.append(row)
            target = self._native_preempt_observation.get('known_length_observed')
            if (q > 0 and computed is not None and target is not None and computed + q >= target):
                self._native_stop_next = 'reached_preempt_CPU_known_length_not_completion_floor'
            elif len(self._native_resume_steps) >= 8:
                self._native_stop_next = 'eight_consecutive_execute_limit'
        return result


    @_native_functools.wraps(_native_shutdown_original)
    def _native_profile_shutdown(self):
        try:
            if getattr(self, '_native_profile_active', False):
                _native_stop(self, False, 'shutdown_before_next_execute')
            _native_event('decode_histogram', histogram=getattr(self, '_native_decode_histogram', {}),
                includes_driver_smoke=True, workload_complete_not_asserted=True,
                limit='N counts only; graph padding and critical path not inferred')
        finally:
            if ModelRunnerFL.execute_model is _native_profile_execute:
                ModelRunnerFL.execute_model = _native_execute_original
            if ModelRunnerFL.shutdown is _native_profile_shutdown:
                ModelRunnerFL.shutdown = _native_shutdown_original
        return _native_shutdown_original(self)


    ModelRunnerFL.execute_model = _native_profile_execute
    ModelRunnerFL.shutdown = _native_profile_shutdown
    print('BIV150_RESUME_NATIVE_ARMED diagnostics_only=1', flush=True)

    def restore():
        if ModelRunnerFL.execute_model is _native_profile_execute:
            ModelRunnerFL.execute_model = _native_execute_original
        if ModelRunnerFL.shutdown is _native_profile_shutdown:
            ModelRunnerFL.shutdown = _native_shutdown_original
    return restore
