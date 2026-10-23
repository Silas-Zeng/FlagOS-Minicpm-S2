"""固定422的显式native或mixed计数模式；不改调度、算术或原runner文件。"""
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from types import MethodType


def _event(event, **fields):
    """最多几个窗口边界写入；失败只令诊断证据不完整。"""
    try:
        path = os.environ['MINICPM_NATIVE_PROFILE_EVENTS']
        with Path(path).open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(event=event, pid=os.getpid(),
                monotonic_ns=time.monotonic_ns(), source=__file__, **fields)) + '\n')
        return True
    except Exception:
        return False


def _shape(output):
    values = tuple(output.num_scheduled_tokens.values())
    ids = tuple(output.num_scheduled_tokens)
    eligible = (len(ids) >= 16 and all(type(q) is int and q == 1 for q in values)
        and output.total_num_scheduled_tokens == len(ids)
        and not output.scheduled_new_reqs
        and not output.scheduled_cached_reqs.resumed_req_ids
        and not output.preempted_req_ids and not output.finished_req_ids
        and not output.scheduled_spec_decode_tokens
        and not output.has_structured_output_requests
        and not output.pending_structured_output_tokens)
    return ids if eligible else None, len(ids), sum(values)


def _attach(runner, mode):
    names = ('execute_model', 'sample_tokens', 'shutdown', '_build_attention_metadata')
    if any(name in runner.__dict__ for name in names):
        raise ValueError('已有runner实例方法覆盖')
    original = {name: getattr(runner, name) for name in names}
    torch = sys.modules['torch']
    state = dict(active=False, done=False, attempted=False, warm_key=None,
        warm_steps=0, key=None, rows=[], error=None, in_execute=False, metadata_seen=False)
    coverage = dict(observation_mode=mode, execute_calls=0, metadata_steps=0, unsupported_steps=0,
        multiple_builds=0, observation_errors=0, mixed_steps=0,
        native_window_metadata_skipped=0, scalar_pure_steps_skipped=0, histogram={})
    try:
        backend = sys.modules['vllm.v1.attention.backends.triton_attn']
        coverage['single_attention_group_verified'] = bool(
            len(runner.attn_groups) == 1 and len(runner.attn_groups[0]) == 1
            and runner.attn_groups[0][0].backend is backend.TritonAttentionBackend)
    except Exception:
        coverage['single_attention_group_verified'] = False
    bindings = {}

    def restore(only=None):
        for name, binding in bindings.items():
            if only is not None and name not in only:
                continue
            try:
                if runner.__dict__.get(name) is binding:
                    del runner.__dict__[name]
            except Exception:
                pass

    def finish_impl(complete, reason):
        if mode == 'mixed_coverage_only':
            return  # 显式CPU计数模式没有CUDA profiler窗口或边界同步。
        if state['done']:
            return
        state['done'] = True
        was_active = state['active']
        state['active'] = False
        cpu_window_end_ns = time.monotonic_ns()
        result = None
        errors = []
        if was_active:
            # 沿原native门仅保留窗口边界sync；没有逐步新增GPU操作。
            try:
                torch.cuda.synchronize()
            except Exception as error:
                errors.append('boundary_sync:' + type(error).__name__)
            try:
                result = int(torch.cuda.cudart().cudaProfilerStop())
            except Exception as error:
                errors.append('profiler_stop:' + type(error).__name__)
        rows = state['rows']
        complete = bool(complete and was_active and result == 0 and not errors
            and len(rows) == 8 and all(row.get('execute_returned')
                and row.get('sample_returned') for row in rows))
        try:
            _event('stop' if complete else 'incomplete', result=result,
                reason=reason, errors=errors, cpu_window_end_ns=cpu_window_end_ns,
                executed_steps=rows, waiting='unknown_not_read',
                mixed_plan_coverage_partial=coverage,
                first_two_steps_boundary_perturbed=True,
                gpu_graph_completeness='requires_actual_trace_intervals',
                scope='CPU execute/sample returns; not GPU completion or performance')
        finally:
            # CPU metadata计数保持到shutdown；GPU窗口永不重启。
            restore(('sample_tokens',))

    def finish(complete, reason):
        try:
            finish_impl(complete, reason)
        except Exception:
            state['active'], state['done'] = False, True
            restore()

    @wraps(original['_build_attention_metadata'])
    def metadata(self, *args, **kwargs):
        result = original['_build_attention_metadata'](*args, **kwargs)
        try:
            if not state['in_execute'] or kwargs.get('for_cudagraph_capture', False):
                return result
            if state['active']:
                coverage['native_window_metadata_skipped'] += 1
                return result  # 八步纯decode窗口不做CPU offsets扫描或I/O。
            if state['metadata_seen']:
                coverage['multiple_builds'] += 1
                return result
            state['metadata_seen'] = True
            if kwargs.get('max_query_len') == 1:
                coverage['scalar_pure_steps_skipped'] += 1
                return result
            if not coverage['single_attention_group_verified']:
                coverage['unsupported_steps'] += 1
                return result
            # 固定cc442单attention group中各layer复用同一metadata，不遍历42层。
            per_layer, _ = result
            backend = sys.modules['vllm.v1.attention.backends.triton_attn']
            value = next(iter(per_layer.values())) if type(per_layer) is dict and per_layer else None
            n, m = kwargs['num_reqs'], kwargs['num_tokens']
            cpu = runner.query_start_loc.cpu
            if (type(value) is not backend.TritonAttentionMetadata or args
                    or kwargs.get('use_spec_decode', False) or kwargs.get('ubatch_slices') is not None
                    or cpu.device.type != 'cpu' or n != runner.input_batch.num_reqs
                    or value.num_actual_tokens != m or value.seq_lens.shape[0] != n
                    or value.query_start_loc.shape[0] != n + 1):
                coverage['unsupported_steps'] += 1
                return result
            offsets = cpu[:n + 1].tolist()
            lengths = [b - a for a, b in zip(offsets, offsets[1:])]
            if (not lengths or offsets[0] != 0 or offsets[-1] != m
                    or min(lengths) <= 0 or max(lengths) != value.max_query_len):
                raise ValueError('非原CPU query offsets')
            coverage['metadata_steps'] += 1
            dall = sum(q == 1 for q in lengths)
            if 0 < dall < n:
                prefix = next(i for i, q in enumerate(lengths) if q != 1)
                plan = getattr(value, '_biv150_natural_prefix_plan', None)
                planned = 0 if plan is None else plan.prefix_tokens
                if type(planned) is not int or not 0 <= planned <= prefix:
                    raise ValueError('未知原C3 plan')
                key = '/'.join(map(str, (n, m, dall, prefix, dall - prefix, planned)))
                coverage['histogram'][key] = coverage['histogram'].get(key, 0) + 1
                coverage['mixed_steps'] += 1
        except Exception:
            coverage['observation_errors'] += 1
        return result

    @wraps(original['execute_model'])
    def execute(self, output, *args, **kwargs):
        row = None
        try:
            if state['active'] and len(state['rows']) == 8:
                finish(state['rows'][-1].get('sample_returned') is True,
                    'eight_steps_then_next_execute_entry')
            if mode == 'puredecode_native' and not state['done']:
                key, n, m = _shape(output)
                if state['active'] and (key != state['key']
                        or (state['rows'] and not state['rows'][-1].get('sample_returned'))):
                    finish(False, 'mixed_abort_or_missing_sample')
                if not state['active'] and not state['done'] and not state['attempted']:
                    if key is not None and key == state['warm_key']:
                        state['warm_steps'] += 1
                    else:
                        state['warm_key'], state['warm_steps'] = key, int(key is not None)
                    if key is not None and state['warm_steps'] >= 3:
                        # 前两次已完整经过原Core采样，当前第三次才开启唯一窗口。
                        state['attempted'] = True
                        torch.cuda.synchronize()
                        result = int(torch.cuda.cudart().cudaProfilerStart())
                        if result:
                            raise RuntimeError('cudaProfilerStart returned nonzero')
                        state['active'], state['key'] = True, key
                        _event('start', result=result, N=n, M=m, request_ids=key,
                            warm_eligible_steps=2, waiting='unknown_not_read',
                            clock_implementation=time.get_clock_info('monotonic').implementation,
                            monotonic_clock='CLOCK_MONOTONIC; map via trace clock_snapshot',
                            max_execute_steps=8, boundary_sync_drained_prior_queue=True)
                if state['active']:
                    row = dict(index=len(state['rows']), N=n, M=m,
                        request_ids=key, all_q_one=True, phase='pure_decode_no_lifecycle_change',
                        execute_returned=False, sample_returned=False)
                    state['rows'].append(row)
                    row['execute_submit_start_ns'] = time.monotonic_ns()
        except Exception as error:
            state['error'] = type(error).__name__
            finish(False, 'observation_error:' + type(error).__name__)
        state['in_execute'], state['metadata_seen'] = True, False
        coverage['execute_calls'] += 1
        try:
            result = original['execute_model'](output, *args, **kwargs)
        except BaseException:
            try:
                finish(False, 'original_execute_exception')
            except Exception:
                restore()
            restore()
            raise
        finally:
            state['in_execute'] = False
        try:
            if row is not None:
                row['execute_return_ns'] = time.monotonic_ns()
                row['execute_returned'] = True
            if not state['active'] and coverage['execute_calls'] % 64 == 0:
                _event('mixed_plan_coverage_partial', **coverage,
                    workload_complete=False,
                    histogram_columns=['N', 'M', 'single_query_Dall', 'single_query_Dprefix', 'outside', 'plan_prefix_tokens'])
        except Exception:
            finish(False, 'execute_observation_error')
        return result

    @wraps(original['sample_tokens'])
    def sample(self, *args, **kwargs):
        row = None
        try:
            if state['active']:
                if not state['rows'] or state['rows'][-1].get('sample_returned'):
                    finish(False, 'unexpected_sample_order')
                else:
                    row = state['rows'][-1]
                    row['sample_submit_start_ns'] = time.monotonic_ns()
        except Exception:
            finish(False, 'sample_observation_error')
        try:
            result = original['sample_tokens'](*args, **kwargs)
        except BaseException:
            try:
                finish(False, 'original_sample_exception')
            except Exception:
                restore()
            restore()
            raise
        try:
            if row is not None:
                row['sample_return_ns'] = time.monotonic_ns()
                row['sample_returned'] = True
        except Exception:
            finish(False, 'sample_return_observation_error')
        return result

    @wraps(original['shutdown'])
    def shutdown(self, *args, **kwargs):
        try:
            finish(False, 'shutdown_before_complete_window')
            _event('mixed_plan_coverage', **coverage,
                histogram_columns=['N', 'M', 'single_query_Dall', 'single_query_Dprefix', 'outside', 'plan_prefix_tokens'],
                limit='actual CPU metadata plan; not forward coverage or confirmed decoded-token membership')
        finally:
            restore()
        return original['shutdown'](*args, **kwargs)

    try:
        for name, function in (('execute_model', execute), ('sample_tokens', sample),
                ('shutdown', shutdown), ('_build_attention_metadata', metadata)):
            if mode == 'mixed_coverage_only' and name == 'sample_tokens':
                continue
            bindings[name] = MethodType(function, runner)
            setattr(runner, name, bindings[name])
    except Exception:
        restore()
        raise
    _event('armed', observation_mode=mode, profiler_enabled=(mode == 'puredecode_native'),
        no_new_gpu_calls_at_install=True, source_runner_unchanged=True)
    return {'restore': restore, 'state': state}


# 首Core冷scope复用已审7393；热allocator不包含在此诊断中。
EXPECTED = {
    'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320',
    'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b',
    'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914',
    'vllm.v1.core.block_pool': '3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe',
    'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80',
}

PRODUCTION = {
    **EXPECTED,
    'vllm.v1.engine.core': '27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71',
    'vllm.v1.core.sched.scheduler': 'df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090',
    'vllm.v1.core.sched.async_scheduler': 'da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884',
    'vllm.v1.kv_cache_interface': '7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003',
    'vllm.v1.executor.uniproc_executor': '4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe',
    'vllm.v1.worker.worker_base': '7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe',
    'vllm_fl.worker.worker': 'a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24',
    'vllm_fl.worker.model_runner': 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663',
    'vllm_fl.patches.biv150_kv_completion_probe': 'a4de3abea10b333aeb73d3c3ab49f82c91510c89cc8f9210c531f666feefb2c6',
    'vllm_fl.patches.biv150_kv_protocol': '91185a23dd56cc7b1d882e9b4b3ccbfdb0d491dce060e658b183ee563d04d3ab',
}

def _on_engine(engine, mode):
    modules = {}
    for name, pin in PRODUCTION.items():
        module = sys.modules.get(name)
        if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
            raise ValueError('未自然加载的固定422源: ' + name)
        modules[name] = module
    classes = {
        'schedulers': (modules['vllm.v1.core.sched.scheduler'].Scheduler, modules['vllm.v1.core.sched.async_scheduler'].AsyncScheduler),
        'manager': modules['vllm.v1.core.kv_cache_manager'].KVCacheManager,
        'coordinator': modules['vllm.v1.core.kv_cache_coordinator'].UnitaryKVCacheCoordinator,
        'full_manager': modules['vllm.v1.core.single_type_kv_cache_manager'].FullAttentionManager,
        'full_spec': modules['vllm.v1.kv_cache_interface'].FullAttentionSpec,
    }
    scheduler = engine.scheduler
    probe = modules['vllm_fl.patches.biv150_kv_completion_probe']
    executor = engine.model_executor
    wrapper = executor.__dict__.get('driver_worker')
    worker = None if wrapper is None else wrapper.__dict__.get('worker')
    runner = None if worker is None else worker.__dict__.get('model_runner')
    if (type(engine) is not modules['vllm.v1.engine.core'].EngineCoreProc
            or not probe._scope(engine, classes)
            or type(scheduler) is not classes['schedulers'][1]
            or type(executor) is not modules['vllm.v1.executor.uniproc_executor'].UniProcExecutor
            or type(wrapper) is not modules['vllm.v1.worker.worker_base'].WorkerWrapperBase
            or type(worker) is not modules['vllm_fl.worker.worker'].WorkerFL
            or type(runner) is not modules['vllm_fl.worker.model_runner'].ModelRunnerFL
            or engine.vllm_config.cache_config.kv_sharing_fast_prefill is not False
            or scheduler.is_encoder_decoder is not False
            or scheduler.kv_cache_manager.max_model_len != scheduler.max_model_len):
        raise ValueError('非固定MiniCPM normal42/单组Full16/Async noSpec/单进程scope')
    spec = scheduler.kv_cache_manager.kv_cache_config.kv_cache_groups[0].kv_cache_spec
    if (spec.head_size_v != 128 or spec.sliding_window is not None
            or spec.attention_chunk_size is not None or spec.non_causal is not False
            or spec.kv_quant_mode != 0):
        raise ValueError('未知KV格式/窗口/量化')
    return _attach(runner, mode)


def install(*, enabled=False, mode='puredecode_native'):
    if enabled is not True:
        return None
    if mode not in ('puredecode_native', 'mixed_coverage_only'):
        raise ValueError('未知观测模式；未安装任何绑定')
    core_module = sys.modules.get('vllm.v1.engine.core')
    protocol = sys.modules.get('vllm_fl.patches.biv150_kv_protocol')
    if (core_module is None or protocol is None
            or hashlib.sha256(Path(core_module.__file__).read_bytes()).hexdigest() != PRODUCTION[core_module.__name__]
            or hashlib.sha256(Path(protocol.__file__).read_bytes()).hexdigest() != PRODUCTION[protocol.__name__]):
        raise ValueError('缺固定原Core/422协议')
    core = core_module.EngineCore
    original = core.step_with_batch_queue
    native = getattr(original, '__wrapped__', None)
    if (original.__globals__ is not vars(protocol)
            or original.__code__.co_qualname != '_wrap_core.<locals>.step'
            or Path(original.__code__.co_filename).resolve() != Path(protocol.__file__).resolve()
            or native is None or hasattr(native, '__wrapped__')
            or Path(native.__code__.co_filename).resolve() != Path(core_module.__file__).resolve()):
        raise ValueError('只允许exact原422协议Core wrapper')
    attempted = False
    handles = []

    def retire(engine):
        try:
            bound = engine.__dict__.get('step_fn')
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
            try:
                handles.append(_on_engine(engine, mode))
            except Exception as error:
                _event('rejected', reason=type(error).__name__)
            finally:
                retire(engine)
        return original(engine, *args, **kwargs)

    core.step_with_batch_queue = step
    print('BIV150_PUREDECODE_NATIVE_INSTALLED pid=' + str(os.getpid()) + ' mode=' + mode, flush=True)
    return {'installed': True, 'handles': handles}
