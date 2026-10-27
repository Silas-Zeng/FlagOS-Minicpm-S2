"""V转置writer同址换值/槽位Graph；原始输入CPU overlay独立核全分配。"""
import numpy as np
import layout_reference


def bits(torch, tensor):
    return tensor.detach().contiguous().cpu().view(torch.int16).numpy().view(np.uint16)


def qualify(torch, run, arms, impl, layer, key, value, cache, slots, packed, kernels,
            sample_reference, query, lengths, table, active):
    B = active
    originals = (key.clone(), value.clone(), slots.clone(), cache.clone())
    graphs = {}
    for name, arm in arms.items():
        def fullcall(name=name, arm=arm):
            if name == 'baseline':
                impl.do_kv_cache_update(layer, key, value, cache, slots)
            else:
                kernels.write_rows[(B,)](key, value, slots, packed,
                    INPUT_STRIDE=key.stride(0), num_warps=1, num_stages=1)
            return arm.call()
        fullcall(); fullcall(); torch.cuda.synchronize()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            fullcall()
        graphs[name] = graph
    checks = []
    for phase in ('new_values', 'shifted_slot', 'negative_slot'):
        key[0].fill_(0.5); value[0].fill_(-0.25)
        slots.copy_(originals[2])
        if phase == 'shifted_slot':
            key[0, :, 0] = 2.0 ** -126; value[0, :, 0] = 2.0 ** -126
            old = int(originals[2][0].item())
            slots[0] = old - 1 if old % 16 else old + 1
        if phase == 'negative_slot':
            slots[1] = -1
        source_key, source_value = bits(torch, key[:B]), bits(torch, value[:B])
        mapping = slots.detach().cpu().numpy().astype(np.int64)
        pages = np.unique(mapping[mapping >= 0] // 16)
        ids = torch.tensor(pages, device=cache.device, dtype=torch.int64)
        target_data = bits(torch, packed.index_select(0, ids))
        target_cache = bits(torch, cache.index_select(0, ids))
        lookup = {int(page): i for i, page in enumerate(pages)}
        for slot_id in mapping[mapping >= 0]:
            p = lookup[int(slot_id // 16)]; s = int(slot_id % 16)
            for kind in range(2):
                for head in range(2):
                    target_data[p, layout_reference.offsets(kind, head, s)] = 0xA5A5
        packed.index_copy_(0, ids, torch.from_numpy(target_data.view(np.int16)).to(packed.device).view(torch.bfloat16))
        expected_data, expected_cache = packed.clone(), cache.clone()
        for token, slot_id in enumerate(mapping):
            if slot_id < 0:
                continue
            p = lookup[int(slot_id // 16)]; s = int(slot_id % 16)
            for kind, source in enumerate((source_key, source_value)):
                target_cache[p, kind, s] = source[token]
                for head in range(2):
                    target_data[p, layout_reference.offsets(kind, head, s)] = source[token, head]
        expected_data.index_copy_(0, ids, torch.from_numpy(target_data.view(np.int16)).to(packed.device).view(torch.bfloat16))
        expected_cache.index_copy_(0, ids, torch.from_numpy(target_cache.view(np.int16)).to(cache.device).view(torch.bfloat16))
        before_input = [x.clone() for x in (query, key, value, slots)]
        rng = (torch.get_rng_state().clone(), torch.cuda.get_rng_state().clone())
        for name, arm in arms.items():
            for tensor in arm.tensors:
                tensor.fill_(-17)
            graphs[name].replay()
        torch.cuda.synchronize()
        c = dict(phase=phase,
            packed_allocation_exact=bool(torch.equal(packed.view(torch.int16), expected_data.view(torch.int16))),
            original_writer_allocation_exact=bool(torch.equal(cache.view(torch.int16), expected_cache.view(torch.int16))),
            cross_arm_bitwise=bool(torch.equal(arms['baseline'].out.view(torch.int16), arms['candidate'].out.view(torch.int16))),
            inputs_unchanged=all(bool(torch.equal(a.view(torch.int16 if a.element_size() == 2 else torch.int64),
                b.view(torch.int16 if b.element_size() == 2 else torch.int64))) for a, b in zip(before_input, (query, key, value, slots))),
            rng_unchanged=bool(torch.equal(rng[0], torch.get_rng_state()) and torch.equal(rng[1], torch.cuda.get_rng_state())),
            output_guard=all(bool((arm.out[B:] == -17).all()) for arm in arms.values()))
        if not all(v for k, v in c.items() if k != 'phase'):
            raise RuntimeError('V转置writer Graph/全写位型失败:' + repr(c))
        # 先独立核writer，再以原cache值做FP64，不允许错误writer污染参考。
        oracle = sample_reference(torch, run, 'writer-' + phase, query, cache, lengths, table,
            {name: arm.out for name, arm in arms.items()}, active)
        c['independent_reference'] = oracle
        if not all(row['passed'] for row in oracle['arms'].values()):
            raise RuntimeError('writer Graph FP64失败')
        checks.append(c)
    for target, original in zip((key, value, slots, cache), originals):
        target.copy_(original)
    return graphs, checks
