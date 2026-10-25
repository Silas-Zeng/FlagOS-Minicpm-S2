"""同进程换合法非紧密 KV stride，核 JIT 身份与原 Graph 回切；不计时。"""


def check_alternate_stride(torch, arms, cache, query, common, grid, first, same_bits, dump, run):
    names = ("key_cache_ptr", "value_cache_ptr", "k_stride_block", "k_stride_slot", "k_stride_head",
             "v_stride_block", "v_stride_slot", "v_stride_head")
    saved_kwargs = {name: {key: arm.pk[key] for key in names} for name, arm in arms.items()}
    original = {name: tuple(t.clone() for t in arm.tensors) for name, arm in arms.items()}
    old_hash = first["candidate"].hash
    # 最后 channel 仍 stride1，page/slot/head 均加间隙；同值，不改变官方布局。
    storage = torch.full((*cache.shape[:-1], 256), -29, dtype=cache.dtype, device=cache.device)
    alternate = storage[..., :128]
    alternate.copy_(cache)
    keys, values = alternate[:, 0], alternate[:, 1]
    guards_before = (query.clone(), common.seq_lens.clone(), common.block_table_tensor.clone())
    cpu_rng, gpu_rng = torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone()
    checks, compiled, failed_alternate = {}, {}, None
    try:
        for name, arm in arms.items():
            arm.pk.update(key_cache_ptr=keys, value_cache_ptr=values,
                k_stride_block=keys.stride(0), k_stride_slot=keys.stride(1), k_stride_head=keys.stride(2),
                v_stride_block=values.stride(0), v_stride_slot=values.stride(1), v_stride_head=values.stride(2))
            for tensor in arm.tensors:
                tensor.fill_(-17)
            compiled[name] = arm.call()
        torch.cuda.synchronize()
        for name, arm in arms.items():
            checks[name + "_same_logical_output"] = all(same_bits(x, y) for x, y in zip(original[name], arm.tensors))
        checks["new_candidate_jit_identity"] = compiled["candidate"].hash != old_hash
        checks["all_five_stride_values_changed"] = all(arms["candidate"].pk[name] != saved_kwargs["candidate"][name]
            for name in ("k_stride_block", "k_stride_slot", "k_stride_head", "v_stride_block", "v_stride_slot"))
        checks["alternate_source_unchanged"] = same_bits(alternate, cache)
        checks["stride_padding_unchanged"] = bool((storage[..., 128:] == -29).all())
        checks["inputs_unchanged"] = all(same_bits(x, y) for x, y in zip(guards_before,
            (query, common.seq_lens, common.block_table_tensor)))
        checks["rng_unchanged"] = torch.equal(cpu_rng, torch.get_rng_state()) and torch.equal(gpu_rng, torch.cuda.get_rng_state())
        resources = {name: dump(kernel, run / ("ir-alternate-stride-" + name)) for name, kernel in compiled.items()}
        if not all(checks.values()):
            failed_alternate = {name: [t.cpu() for t in arm.tensors] for name, arm in arms.items()}
    finally:
        for name, arm in arms.items():
            arm.pk.update(saved_kwargs[name])
    returned = {name: arm.call() for name, arm in arms.items()}
    torch.cuda.synchronize()
    checks["original_candidate_jit_reused"] = returned["candidate"].hash == old_hash
    for name, arm in arms.items():
        checks[name + "_original_eager_restored"] = all(same_bits(x, y) for x, y in zip(original[name], arm.tensors))
        for tensor in arm.tensors:
            tensor.fill_(-17)
        arm.graph.replay()
    torch.cuda.synchronize()
    for name, arm in arms.items():
        checks[name + "_original_graph_still_bound"] = all(same_bits(x, y) for x, y in zip(original[name], arm.tensors))
    result = dict(checks=checks, original_stride=list(cache[:, 0].stride()),
                  alternate_stride=list(keys.stride()), resources=resources,
                  original_candidate_hash=old_hash, alternate_candidate_hash=compiled["candidate"].hash)
    from validate_hidden_row_gather import write
    write(run / "alternate-stride.json", result)
    if not all(checks.values()):
        torch.save({"original": {n: [t.cpu() for t in ts] for n, ts in original.items()},
                    "failed_alternate": failed_alternate,
                    "returned": {n: [t.cpu() for t in arm.tensors] for n, arm in arms.items()}},
                   run / "alternate-stride-failed.pt")
        raise RuntimeError("同进程 stride 特化/回切失败：" + repr(checks))
    return result
