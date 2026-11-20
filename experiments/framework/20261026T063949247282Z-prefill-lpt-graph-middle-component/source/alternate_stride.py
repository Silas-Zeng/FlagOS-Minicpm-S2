"""原eligible范围内同值合法stride切换/回切，不计入ABBA。"""


def check(torch, run, query, cache, common, kwargs, managers, outputs, graphs, grid, expected_hashes, qmod, preserve):
    from validate_hidden_row_gather import write
    def bits(a, b): return torch.equal(a.view(torch.int16), b.view(torch.int16))
    names = ('query_ptr', 'key_cache_ptr', 'value_cache_ptr', 'output_ptr', 'block_tables_ptr',
             'query_stride_0', 'output_stride_0', 'stride_k_cache_0', 'stride_v_cache_0', 'block_table_stride')
    saved = {name: {key: kw[key] for key in names} for name, kw in kwargs.items()}
    original = {name: out.clone() for name, out in outputs.items()}
    cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
    # 内层slot/head/dim保持原eligible规定；只为page/token/table行增加间隔。
    q_store = torch.full((query.shape[0]*2, *query.shape[1:]), -29, dtype=query.dtype, device=query.device)
    alt_q = q_store[::2]; alt_q.copy_(query)
    kv_store = torch.full((cache.shape[0]*2, *cache.shape[1:]), -29, dtype=cache.dtype, device=cache.device)
    alt_cache = kv_store[::2]; alt_cache.copy_(cache)
    k, v = alt_cache[:, 0], alt_cache[:, 1]
    table = common.block_table_tensor
    table_store = torch.full((table.shape[0], table.shape[1]*2), -29, dtype=table.dtype, device=table.device)
    alt_table = table_store[:, :table.shape[1]]; alt_table.copy_(table)
    out_stores = {name: torch.full_like(q_store, -29) for name in kwargs}
    alt_out = {name: storage[::2] for name, storage in out_stores.items()}
    for out in alt_out.values(): out.fill_(-17)
    checks, compiled, ir = {}, {}, {}
    try:
        for name, kw in kwargs.items():
            kw.update(query_ptr=alt_q[:query.shape[0]-3], key_cache_ptr=k, value_cache_ptr=v,
                output_ptr=alt_out[name][:query.shape[0]-3], block_tables_ptr=alt_table,
                query_stride_0=alt_q.stride(0), output_stride_0=alt_out[name].stride(0),
                stride_k_cache_0=k.stride(0), stride_v_cache_0=v.stride(0), block_table_stride=alt_table.stride(0))
            if not qmod._eligible(kw): raise RuntimeError('alternate stride超出原eligible')
            compiled[name] = managers[name].wrapper[grid](**kw)
            if compiled[name].hash not in managers[name].optimized:
                raise RuntimeError('alternate未实际Q-hoist')
        torch.cuda.synchronize()
        for name, kw in kwargs.items():
            checks[name+'_same_logical_output'] = bits(alt_out[name], original[name])
            graph = torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph):
                captured = managers[name].candidate[grid](**kw)
            checks[name+'_alternate_graph_hash'] = captured.hash == compiled[name].hash
            alt_out[name].fill_(-17); graph.replay(); torch.cuda.synchronize()
            checks[name+'_alternate_graph_bits'] = bits(alt_out[name], original[name])
            ir[name] = preserve(compiled[name], run/('ir-alternate-stride-'+name), qmod)
        checks['new_candidate_identity'] = compiled['stride'].hash != expected_hashes['stride']
        checks['five_allowed_strides_changed'] = all(kwargs['stride'][name] != saved['stride'][name]
            for name in ('query_stride_0','output_stride_0','stride_k_cache_0','stride_v_cache_0','block_table_stride'))
        checks['source_values_unchanged'] = bits(alt_q,query) and bits(alt_cache,cache) and torch.equal(alt_table,table)
        checks['padding_unchanged'] = bool((q_store[1::2]==-29).all() and (kv_store[1::2]==-29).all()
            and (table_store[:,table.shape[1]:]==-29).all() and all(bool((x[1::2]==-29).all()) for x in out_stores.values()))
        checks['rng_unchanged'] = torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
        if not all(checks.values()):
            torch.save({name: out.cpu() for name,out in alt_out.items()},run/'alternate-stride-failed.pt')
    finally:
        for name, kw in kwargs.items(): kw.update(saved[name])
    for name, kw in kwargs.items():
        outputs[name].fill_(-17)
        returned = managers[name].candidate[grid](**kw)
        torch.cuda.synchronize()
        checks[name+'_original_jit_hash'] = returned.hash == expected_hashes[name]
        checks[name+'_original_eager_bits'] = bits(outputs[name],original[name])
        outputs[name].fill_(-17); graphs[name].replay(); torch.cuda.synchronize()
        checks[name+'_original_graph_bits'] = bits(outputs[name],original[name])
    result = dict(checks=checks, ir=ir, original_candidate_hash=expected_hashes['stride'],
        alternate_candidate_hash=compiled['stride'].hash,
        changed_stride_values={name:dict(original=saved['stride'][name],alternate=value) for name,value in
            dict(query_stride_0=alt_q.stride(0),output_stride_0=alt_out['stride'].stride(0),
                stride_k_cache_0=k.stride(0),stride_v_cache_0=v.stride(0),block_table_stride=alt_table.stride(0)).items()},
        limit='11项特化；原eligible内仅5项允许改变，其余6项固定几何不放宽；单序列seq_idx=0，table行stride只覆盖特化身份，未数值覆盖非零行偏移')
    write(run/'alternate-stride.json',result)
    if not all(checks.values()): raise RuntimeError('stride切换/回切失败：'+repr(checks))
    return result
