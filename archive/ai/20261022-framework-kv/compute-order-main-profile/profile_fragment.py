def _function_cells(function, module, qualname):
    if (not isinstance(function, types.FunctionType)
            or function.__globals__ is not vars(module)
            or function.__code__.co_qualname != qualname
            or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
        raise ValueError('非固定main函数绑定：' + qualname)
    return dict(zip(function.__code__.co_freevars,
                    (cell.cell_contents for cell in (function.__closure__ or ()))))


def _main_stack(torch):
    attention = sys.modules['vllm.v1.attention.ops.triton_unified_attention']
    backend = sys.modules['vllm.v1.attention.backends.triton_attn']
    normalized = sys.modules['vllm_fl.patches.biv150_prefill_normalized']
    gqa = sys.modules['vllm_fl.patches.biv150_gqa_decode']
    mixed = sys.modules['vllm_fl.patches.biv150_mixed_decode']
    top = attention.unified_attention
    if (backend.unified_attention is not top
            or getattr(attention, normalized._INSTALLED, False) is not True
            or getattr(attention, gqa._INSTALLED_ATTR, False) is not True):
        raise ValueError('main normalized/GQA安装或双统一入口不符')
    cells = _function_cells(top, normalized, 'install.<locals>.wrapper')
    if set(cells) != {'normalized', 'original', 'signature'}:
        raise ValueError('normalization闭包不符')
    previous = cells['original']
    if getattr(top, '__wrapped__', None) is not previous:
        raise ValueError('normalization原路不是本GQA')
    old = _function_cells(previous, gqa, '_make_wrapper.<locals>.patched')
    if set(old) != {'original'} or getattr(previous, '__wrapped__', None) is not old['original']:
        raise ValueError('GQA原路存在未知包装')
    generic = old['original']
    if _function_cells(generic, attention, 'unified_attention'):
        raise ValueError('generic存在未知闭包')
    clone = cells['normalized']
    if (not isinstance(clone, types.FunctionType) or clone.__code__ is not generic.__code__
            or getattr(clone, '__wrapped__', None) is not generic
            or clone.__globals__ is generic.__globals__
            or clone.__defaults__ != generic.__defaults__
            or clone.__kwdefaults__ != generic.__kwdefaults__
            or clone.__closure__ is not generic.__closure__
            or clone.__globals__.get('reduce_segments') is not attention.reduce_segments
            or not isinstance(cells['signature'], inspect.Signature)
            or cells['signature'] != inspect.signature(previous)):
        raise ValueError('normalized统一函数不是原generic的独立global克隆')
    source = inspect.getsource(attention.kernel_unified_attention.fn)
    old_mass = 'L = tl.full([BLOCK_M], 1.0, dtype=tl.float32)'
    old_name = 'def kernel_unified_attention('
    if source.count(old_mass) != 1 or source.count(old_name) != 1:
        raise ValueError('pinned原kernel源码形态不符')
    expected = source.replace(old_mass, 'L = tl.zeros([BLOCK_M], dtype=tl.float32)')
    expected = expected.replace(old_name, 'def kernel_biv150_prefill_normalized(', 1)
    kernel = clone.__globals__.get('kernel_unified_attention')
    fn = getattr(kernel, 'fn', None)
    digest = hashlib.sha256(expected.encode()).hexdigest()
    if (kernel is attention.kernel_unified_attention or not isinstance(fn, types.FunctionType)
            or fn.__code__.co_filename != '<biv150-prefill-normalized-' + digest + '.py>'
            or fn.__code__.co_name != 'kernel_biv150_prefill_normalized'
            or inspect.getsource(fn) != expected):
        raise ValueError('normalized kernel不是本次已核L=0克隆')
    for function, name, original_name, qualname in (
        (backend.TritonAttentionMetadataBuilder.build, 'build', 'original_build', 'TritonAttentionMetadataBuilder.build'),
        (backend.TritonAttentionImpl.forward, 'forward', 'original_forward', 'TritonAttentionImpl.forward'),
    ):
        captured = _function_cells(function, mixed, '_wrap_backend.<locals>.' + name)
        original = captured.get(original_name)
        if (set(captured) != {'backend', original_name, 'torch'}
                or captured['backend'] is not backend or captured['torch'] is not torch
                or getattr(function, mixed._MARKER, False) is not True
                or getattr(function, '__wrapped__', None) is not original
                or _function_cells(original, backend, qualname)):
            raise ValueError('C3原build/forward闭包或动态backend不符')
