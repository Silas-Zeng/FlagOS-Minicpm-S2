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
                    and (not kwargs or kwargs == {'num_lookahead_tokens': 0})
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
