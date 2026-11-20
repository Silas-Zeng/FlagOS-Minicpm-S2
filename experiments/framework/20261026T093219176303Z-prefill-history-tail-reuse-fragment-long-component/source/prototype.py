"""独立组件：完整历史热循环与至多两次原causal尾tile；不安装生产。"""
from __future__ import annotations
import ast
import hashlib
import inspect
import linecache
import re
import types

STRIDES = ('block_table_stride', 'query_stride_0', 'query_stride_1',
    'output_stride_0', 'output_stride_1', 'stride_k_cache_0', 'stride_k_cache_1',
    'stride_k_cache_2', 'stride_v_cache_0', 'stride_v_cache_1', 'stride_v_cache_2')


def _once(text, old, new):
    if text.count(old) != 1:
        raise ValueError('唯一源码anchor变化: '+old[:100])
    return text.replace(old, new, 1)


def transform(source):
    """只改目标stride核的K循环；原尾tile源码逐字保留，原FP表达式不变。"""
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef))
    if fn.name != 'kernel_biv150_prefill_stride':
        raise ValueError('必须是main6971已特化stride、无LPT的原核')
    loops = [n for n in fn.body if isinstance(n, ast.For)
             and isinstance(n.target, ast.Name) and n.target.id == 'j']
    if len(loops) != 1 or ast.unparse(loops[0].iter) != 'range(loop_lo, loop_hi)':
        raise ValueError('原K循环变化')
    loop = loops[0]
    lines = source.splitlines(True)
    original = ''.join(lines[loop.lineno-1:loop.end_lineno])
    body = ''.join(lines[loop.body[0].lineno-1:loop.end_lineno])
    hot = body
    hot = _once(hot, '        tile_mask = seq_offset < max_seq_prefix_len\n', '')
    begin = hot.index('        query_abs_pos = context_len + query_pos[:, None]\n')
    end = hot.index('        # S : (BLOCK_M, TILE_SIZE)\n', begin)
    hot = hot[:begin] + hot[end:]
    hot = _once(hot, '''            K_load = tl.load(
                key_cache_ptr + k_offset,
                mask=dim_mask[:, None] & tile_mask[None, :],
                other=0.0,
            )''', '            K_load = tl.load(key_cache_ptr + k_offset)')
    hot = _once(hot, '''            V_load = tl.load(
                value_cache_ptr + v_offset,
                mask=dim_mask[None, :] & tile_mask[:, None],
                other=0.0,
            )''', '            V_load = tl.load(value_cache_ptr + v_offset)')
    hot = _once(hot, '''        S = tl.where(
            query_mask_1[:, None] & query_mask_0[:, None] & seq_mask, S, float("-inf")
        )
''', '')
    # Those references exist only in branches forbidden by the constexpr assertions.
    # Keeping inactive source preserves the original tail and its numerical code.
    asserts = '''    # 仅独立组件的已限定普通BF16 2D。未知flags拒编译，不改生产fallback。
    tl.static_assert(not IS_3D and not USE_TD and not USE_TD_QO)
    tl.static_assert(not USE_FP8 and not Q_IS_FP8 and KV_QUANT_MODE == 0)
    tl.static_assert(not USE_ALIBI_SLOPES and not USE_ALIBI_SQRT and not USE_QQ_BIAS)
    tl.static_assert(not USE_SOFTCAP and not USE_SINKS and not USE_MM_PREFIX)
    tl.static_assert(USE_CAUSAL and not USE_PER_SEQ_CAUSAL and SLIDING_WINDOW == 0)
    tl.static_assert(CHUNK_LOOKBACK == -1 and CHUNK_SIZE == -1)
    tl.static_assert(num_query_heads == 16 and num_queries_per_kv == 8)
    tl.static_assert(BLOCK_M == 128 and BLOCK_Q == 16 and TILE_SIZE == 64)
    tl.static_assert(BLOCK_SIZE == 16 and HEAD_SIZE == 128 and HEAD_SIZE_PADDED == 128)
    # 对ragged末块亦成立：最早有效query界定完整历史；无效Q行不写out。
    full_history_hi = tl.minimum(loop_hi, tl.maximum(loop_lo,
        (context_len + q_block_local_idx * BLOCK_Q + 1) // TILE_SIZE))
'''
    replacement = asserts + '    for j in range(loop_lo, full_history_hi):\n' + hot
    replacement += '\n    if full_history_hi < loop_hi:\n        j = full_history_hi\n' + body
    replacement += '\n    if full_history_hi + 1 < loop_hi:\n        j = full_history_hi + 1\n' + body
    candidate = source.replace(original, replacement, 1)
    # Exact splice inverse; no unrelated source mutation or kernel renaming.
    if candidate.replace(replacement, original, 1) != source:
        raise AssertionError('循环splice无法逐字逆回')
    ast.parse(candidate)
    # Verify the original FP calls and order separately in both blocks.
    fp_names = {'softmax_step', 'dot', 'apply_softcap', 'apply_alibi_to_score', 'load_qq_bias_tile'}
    def fp_calls(text):
        parsed = ast.parse('def f():\n'+text)
        calls = []
        for n in ast.walk(parsed):
            if isinstance(n, ast.Call):
                name = n.func.id if isinstance(n.func, ast.Name) else getattr(n.func, 'attr', '')
                if name in fp_names:
                    calls.append((n.lineno, ast.dump(n, include_attributes=False)))
        return [v for _, v in sorted(calls)]
    if fp_calls(hot) != fp_calls(body):
        raise AssertionError('原FP调用拓扑改变')
    return candidate


def transform_ir(raw):
    """只供新核：唯一只读Q allocation的同布局1/2/3次fragment load共享。

    第二处使用同布局identity convert，保留SSA定义/使用，避免全局名字替换。
    首load提升到唯一主循环前；该定义支配热循环和之后的tail if。
    """
    text = raw.decode('utf-8')
    lines = text.splitlines(True)
    allocations = [(i, re.search(r'(%[A-Za-z0-9_]+) = ttg.local_alloc .*tensor<128x128xbf16', s))
                   for i, s in enumerate(lines)]
    allocations = [(i,m.group(1)) for i,m in allocations if m]
    if len(allocations) != 1:
        raise RuntimeError('新核必须唯一Q allocation')
    alloc_i, alloc = allocations[0]
    loops = [i for i,s in enumerate(lines) if '= scf.for ' in s]
    if len(loops) != 1:
        raise RuntimeError('新核必须恰好一个K热循环，尾部只能if')
    loop_i = loops[0]
    loads = []
    pattern = re.compile(r'^(\s*)(%[A-Za-z0-9_]+) = ttg.local_load '+re.escape(alloc)
                         +r' : (.+) -> (tensor<128x128xbf16, .+>)( loc\(.+\))?\s*$')
    for i,s in enumerate(lines):
        if ('ttg.local_load ' in s and '-> tensor<128x128xbf16,' in s
                and 'dot_op<{opIdx = 0' in s
                and not re.search(r'ttg.local_load '+re.escape(alloc)+r'(?=\s| :)',s)):
            raise RuntimeError('还存在来自其它memdesc的Q形状fragment load')
        if re.search(re.escape(alloc)+r'(?![A-Za-z0-9_])', s) and i != alloc_i:
            match = pattern.match(s.rstrip('\n'))
            if match:
                loads.append((i,match))
            elif 'ttg.local_dealloc '+alloc not in s:
                raise RuntimeError('Q memdesc还有未核别名/写入/使用')
    if len(loads) not in (1,2,3):
        raise RuntimeError('新核Q fragment load不是1/2/3处')
    first_i, first = loads[0]
    # v2仅覆盖已回收的实际编译体：第一个Q fragment已在loop外，
    # hot loop内还有相同memdesc/layout的重复读取。保留支配定义，只复用它。
    if alloc_i < first_i < loop_i:
        if hashlib.sha256(raw).hexdigest() != '4f544f3dbd39b3ae3ffad2d1992af25793abdf9fbb6de0863993cfe3892ce769':
            raise RuntimeError('预存外层Q fragment不是已核真实IR；不泛化守卫')
        if len(loads) != 2:
            raise RuntimeError('实际v2必须外层first＋hot重复两处Q load')
        indent = re.match(r'^\s*', lines[loop_i]).group()
        alloc_indent = re.match(r'^\s*', lines[alloc_i]).group()
        second_i, second = loads[1]
        if not (alloc_indent == first.group(1) == indent
                and second.group(1) == indent+'  ' and second_i > loop_i
                and second.group(3) == first.group(3)
                and second.group(4) == first.group(4)
                and 'dot_op<{opIdx = 0' in first.group(4)):
            raise RuntimeError('外层定义/支配/相同Q来源与layout门失败')
        # Exact IR pin plus same outer block proves first dominates loop and both
        # later tail ifs. The common checks above reject any write/alias to Q.
        alias = (second.group(1)+second.group(2)+' = ttg.convert_layout '
                 +first.group(2)+' : '+first.group(4)+' -> '+first.group(4)
                 +(second.group(5) or '')+'\n')
        changed = lines.copy()
        changed[second_i] = alias
        restored = changed.copy(); restored[second_i] = lines[second_i]
        if restored != lines:
            raise AssertionError('真实v2 identity替换不能逐字逆回')
        return ''.join(changed).encode('utf-8')
    if not alloc_i < loop_i < first_i:
        raise RuntimeError('Q allocation/循环/首load顺序变化；不猜已优化IR')
    indent = re.match(r'^\s*',lines[loop_i]).group()
    alloc_indent = re.match(r'^\s*',lines[alloc_i]).group()
    if alloc_indent != indent or first.group(1) != indent+'  ':
        raise RuntimeError('Q allocation与主循环不在同一外层block')
    # The allocation initializes its shared value before the loop. Only read-only
    # loads/deallocation reference it, so moving the first read has no write race.
    qname, srctype, dtype = first.group(2), first.group(3), first.group(4)
    if 'dot_op<{opIdx = 0' not in dtype:
        raise RuntimeError('Q operand不是原dot op0布局')
    replacements = {}
    for i,m in loads[1:]:
        if m.group(3) != srctype or m.group(4) != dtype or m.group(1) != first.group(1):
            raise RuntimeError('两个Q fragment来源类型/布局/层级不同')
        replacements[i] = (m.group(1)+m.group(2)+' = ttg.convert_layout '+qname
                           +' : '+dtype+' -> '+dtype+(m.group(5) or '')+'\n')
    moved = indent + lines[first_i].lstrip()
    changed = []
    for i,s in enumerate(lines):
        if i == loop_i:
            changed.append(moved)
        if i == first_i:
            continue
        changed.append(replacements.get(i,s))
    # Mechanical exact inverse of this one splice / optional identity alias.
    restored = changed.copy()
    del restored[loop_i]
    restored.insert(first_i, lines[first_i])
    for i in replacements:
        restored[i] = lines[i]
    if restored != lines:
        raise AssertionError('新核Q共享无法逐字逆回')
    return ''.join(changed).encode('utf-8')


def build(attention, manager, helpers):
    source = transform(inspect.getsource(manager.raw.fn))
    digest = hashlib.sha256(source.encode()).hexdigest()
    filename = '<prefill-history-tail-'+digest+'.py>'
    linecache.cache[filename] = (len(source), None, source.splitlines(True), filename)
    namespace = dict(vars(attention))
    exec(compile(source, filename, 'exec'), namespace)
    return namespace['kernel_biv150_prefill_stride'], source


def private_manager(raw, attention, backend, qmod):
    from triton.runtime.jit import JITFunction
    cloned = JITFunction(raw.fn, version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug, noinline=raw.noinline, repr=raw._repr,
        launch_metadata=raw.launch_metadata)
    original = qmod.Manager._compile
    globals_copy = dict(original.__globals__, transform_ir=transform_ir)
    private_compile = types.FunctionType(original.__code__, globals_copy,
        original.__name__, original.__defaults__, original.__closure__)
    private_compile.__kwdefaults__ = original.__kwdefaults__
    private_type = type('HistoryTailManager', (qmod.Manager,), {'_compile': private_compile})
    return private_type(attention, backend, {'kernel':raw}, 'kernel', raw, cloned).install()


def machine_summary(compiled):
    assembly = compiled.asm.get('asm', '')
    def number(key):
        match = re.search(r'\b'+key+r'\s*[:=]\s*(\d+)', assembly)
        return int(match[1]) if match else None
    return dict(sgpr=number('warp_sgpr_count'), vgpr=number('workitem_vgpr_count'),
        sgpr_spill=number('sgpr_spill_count'), vgpr_spill=number('vgpr_spill_count'),
        integer_mul=len(re.findall(r'\b(?:sl|ml)_mul(?:l)?_[ui](?:32|64)(?:_[ui]32)?\b', assembly)),
        limits='真实ASM资源；不是动态时间或收益证明')
