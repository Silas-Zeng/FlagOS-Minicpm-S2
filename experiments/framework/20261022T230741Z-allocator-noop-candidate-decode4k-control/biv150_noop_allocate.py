"""默认不安装。仅普通RUNNING q1本次槽位与hash均无操作时返回原empty单例。"""
from functools import wraps
import hashlib
import inspect
from pathlib import Path

EXPECTED = {
    'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320',
    'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b',
    'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914',
    'vllm.v1.core.block_pool': '3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe',
    'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80',
}


def create(manager, *, modules, requests):
    """只构造已核来源的实例wrapper；生产模型/scheduler scope由接线先核。

    modules是自然已加载的原模块；不导入框架或设备。CPU合同可显式装载这些
    原类/原方法片段，不能因此声称已验证生产构造、GPU或新分配路径。
    """
    for name, pin in EXPECTED.items():
        module = modules[name]
        if module.__name__ != name or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
            raise ValueError('非固定actual来源: ' + name)
    km, co, st, bp, rq = (modules[name] for name in EXPECTED)
    if (type(manager) is not km.KVCacheManager or type(manager.coordinator) is not co.UnitaryKVCacheCoordinator
            or len(manager.coordinator.single_type_managers) != 1
            or type(manager.coordinator.single_type_managers[0]) is not st.FullAttentionManager
            or type(manager.block_pool) is not bp.BlockPool or type(requests) is not dict
            or manager.enable_caching is not True or manager.use_eagle is not False):
        raise ValueError('非固定单组Full/cache/request实例')
    single = manager.coordinator.single_type_managers[0]
    if (single.block_size != 16 or single.scheduler_block_size != 16
            or single._max_admission_blocks_per_request is not None
            or single.block_pool is not manager.block_pool
            or single.use_eagle is not False or single.enable_caching is not True
            or manager.max_model_len <= 0 or manager.coordinator.retention_interval is not None
            or len(manager.empty_kv_cache_blocks.blocks) != 1
            or manager.empty_kv_cache_blocks.blocks != ((),)):
        raise ValueError('非固定无skip/无retention/empty配置')
    for obj, names, module in (
        (manager, ('allocate_slots', 'create_kv_cache_blocks'), km),
        (manager.coordinator, ('remove_skipped_blocks', 'get_num_blocks_to_allocate', 'allocate_new_blocks', 'cache_blocks'), co),
        (single, ('remove_skipped_blocks', 'get_num_skipped_tokens', 'get_num_blocks_to_allocate', 'allocate_new_blocks', 'cache_blocks'), st),
        (manager.block_pool, ('get_num_free_blocks',), bp),
    ):
        for name in names:
            method = getattr(obj, name)
            if (name in obj.__dict__ or inspect.unwrap(method.__func__) is not method.__func__
                    or Path(method.__func__.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
                raise ValueError('已有方法替换/身份未知: ' + name)
    if st.FullAttentionManager.get_num_skipped_tokens is not st.SingleTypeKVCacheManager.get_num_skipped_tokens:
        raise ValueError('Full skip不再原恒0实现')
    original = manager.allocate_slots
    maximum, empty, running, request_cls = manager.max_model_len, manager.empty_kv_cache_blocks, rq.RequestStatus.RUNNING, rq.Request
    counts = {'selected': 0, 'fallback': 0}

    @wraps(original)
    def allocate(request, num_new_tokens, *args, **kwargs):
        selected = False
        # 这里只读；guard出错后在except外调用原方法，不污染原异常上下文。
        try:
            if (not args and type(num_new_tokens) is int and num_new_tokens == 1
                    and (not kwargs or (len(kwargs) == 1
                        and type(kwargs.get('num_lookahead_tokens')) is int
                        and kwargs['num_lookahead_tokens'] == 0))
                    and type(request) is request_cls and request.status is running
                    and requests.get(request.request_id) is request
                    and request.stop_reason is None and request.resumable is False
                    and not request.spec_token_ids and not request.mm_features
                    and request.prompt_embeds is None and request.pooling_params is None
                    and request.structured_output_request is None
                    and request.async_tokens_to_discard == 0
                    and request.num_output_tokens < request.max_tokens):
                rid, computed = request.request_id, request.num_computed_tokens
                known = request.num_tokens
                owned = single.req_to_blocks.get(rid)
                cached = single.num_cached_block.get(rid)
                if (type(computed) is int and request.num_prompt_tokens <= computed < maximum
                        and type(cached) is int and type(owned) is list
                        and ((computed + 1 + 15) // 16) <= len(owned)
                        and min(computed + 1, known) // 16 <= cached):
                    selected = True
        except Exception:
            pass
        if selected:
            counts['selected'] += 1
            return empty
        counts['fallback'] += 1
        return original(request, num_new_tokens, *args, **kwargs)

    return {'call': allocate, 'original': original, 'counts': counts,
            'empty': empty, 'manager': manager, 'single': single,
            'scope_pending': '生产只允许固定422/MiniCPM/normal42/Async无spec等scope；本模块尚无安装入口'}


# 以下生产接线只在首次Core入口核一次；上方已测热guard逐字节保留。
import json
import os
import sys

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


def _emit(event, **fields):
    try:
        print('BIV150_ALLOCATOR_NOOP_' + event + ' ' + json.dumps({'pid': os.getpid(), 'event': event, **fields}), flush=True)
    except Exception:
        pass


def _on_engine(engine):
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
    handle = create(scheduler.kv_cache_manager, modules=modules, requests=scheduler.requests)
    scheduler.kv_cache_manager.__dict__['allocate_slots'] = handle['call']
    return handle


def install(*, enabled=False):
    """仅固定422原协议wrapper后追加；未知绑定拒绝，不导入框架或设备。"""
    if enabled is not True:
        return None
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
        raise ValueError('只允许exact原422协议Core wrapper，不泛化unwrap')
    handles = []
    owners = []
    attempted = False
    reported = False

    def retire(engine):
        # actual Core构造器缓存了bound step_fn，必须同时归还该owned入口。
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
        nonlocal attempted, reported
        if not attempted:
            attempted = True
            try:
                owners.append(engine)
                handles.append(_on_engine(engine))
                _emit('ARMED', source_scope='fixed422', no_device_calls=True)
            except Exception as error:
                _emit('REJECTED', reason=type(error).__name__)
                retire(engine)
        handle = None
        before = 0
        try:
            handle = handles[0] if handles else None
            before = handle['counts']['selected'] if handle is not None else 0
        except Exception:
            retire(engine)
        # 原Core（含原协议）恰一次，在观察except外；异常不重试。
        result = original(engine, *args, **kwargs)
        try:
            if (handle is not None and handle['counts']['selected'] > before
                    and len(engine.scheduler.running) >= 2 and not reported):
                reported = True
                _emit('FIRST_SELECTED', selected_in_core_step=handle['counts']['selected']-before,
                    selected_total=handle['counts']['selected'], original_core_step_returned=True,
                    running=len(engine.scheduler.running), same_empty_object=True,
                    gpu_completion_claimed=False, no_page_or_hash_mutation=True)
                # 真实多请求命中后撤掉一次性Core观察层，保留实例allocator。
                retire(engine)
        except Exception:
            pass
        return result

    def restore():
        for handle in handles:
            if handle['manager'].__dict__.get('allocate_slots') is handle['call']:
                del handle['manager'].__dict__['allocate_slots']
        for engine in owners:
            retire(engine)
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    core.step_with_batch_queue = step
    _emit('HOOKED', actual_fast_return_not_yet_observed=True)
    return {'restore': restore, 'handles': handles}
