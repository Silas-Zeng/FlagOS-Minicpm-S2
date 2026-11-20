"""新增writer的独立CPU位参考/全字节写覆盖及同址Graph转换门。"""
import numpy as np
import soa_codec


def bits(torch,t):
    return t.detach().contiguous().cpu().view(torch.int16).numpy().view(np.uint16)


def qualify(torch,run,arms,impl,layer,key,value,cache,slots,packed,metadata,kernels,
            sample_reference,query,lengths,table,active):
    B=active
    originals=(key.clone(),value.clone(),slots.clone(),cache.clone())
    graphs={}
    for name,arm in arms.items():
        def fullcall(name=name,arm=arm):
            if name=='baseline':impl.do_kv_cache_update(layer,key,value,cache,slots)
            else:kernels.write_rows[(B,2,2)](key,value,slots,packed,metadata,
                    INPUT_STRIDE=key.stride(0),num_warps=1,num_stages=1)
            return arm.call()
        fullcall();fullcall();torch.cuda.synchronize()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):fullcall()
        graphs[name]=graph
    checks=[]
    for phase in ('compressed','raw_shifted','compressed_negative_slot'):
        key[0].fill_(0.5);value[0].fill_(-0.25)
        slots.copy_(originals[2])
        if phase=='raw_shifted':
            key[0,:,0]=2.0**-126;value[0,:,0]=2.0**-126
            old=int(originals[2][0].item());slots[0]=old-1 if old%16 else old+1
        if phase=='compressed_negative_slot':slots[1]=-1
        source_key,source_value=bits(torch,key[:B]),bits(torch,value[:B])
        mapping=slots.detach().cpu().numpy().astype(np.int64)
        pages=np.unique(mapping[mapping>=0]//16)
        ids=torch.tensor(pages,device=cache.device,dtype=torch.int64)
        target_data=packed.index_select(0,ids).cpu().numpy()
        target_meta=metadata.index_select(0,ids).cpu().numpy()
        target_cache=bits(torch,cache.index_select(0,ids))
        lookup={int(page):i for i,page in enumerate(pages)}
        # 只毒化真实writer本轮mapped row；其余所有byte纳入精确预期。
        for slot_id in mapping[mapping>=0]:
            p=lookup[int(slot_id//16)];s=int(slot_id%16)
            for group in range(4):
                target_data[p,group,s*128:(s+1)*128]=165
                target_data[p,group,2048+s*64:2048+(s+1)*64]=165
                target_data[p,group,3072+s*64:3072+(s+1)*64]=165
                target_meta[p,group,s*2:s*2+2]=204
        packed.index_copy_(0,ids,torch.from_numpy(target_data).to(packed.device))
        metadata.index_copy_(0,ids,torch.from_numpy(target_meta).to(metadata.device))
        expected_data,expected_meta=packed.clone(),metadata.clone()
        expected_cache=cache.clone()
        for token,slot_id in enumerate(mapping):
            if slot_id<0:continue
            p=lookup[int(slot_id//16)];s=int(slot_id%16)
            for kind,source in enumerate((source_key,source_value)):
                target_cache[p,kind,s]=source[token]
                for head in range(2):soa_codec.store_row(target_data,target_meta,p,kind,head,s,source[token,head])
        expected_data.index_copy_(0,ids,torch.from_numpy(target_data).to(packed.device))
        expected_meta.index_copy_(0,ids,torch.from_numpy(target_meta).to(metadata.device))
        expected_cache.index_copy_(0,ids,torch.from_numpy(target_cache.view(np.int16)).to(cache.device).view(torch.bfloat16))
        before_input=[x.clone() for x in (query,key,value,slots)]
        rng=(torch.get_rng_state().clone(),torch.cuda.get_rng_state().clone())
        for name,arm in arms.items():
            for tensor in arm.tensors:tensor.fill_(-17)
            graphs[name].replay()
        torch.cuda.synchronize()
        c=dict(phase=phase,packed_allocation_exact=bool(torch.equal(packed,expected_data)),
            metadata_allocation_exact=bool(torch.equal(metadata,expected_meta)),
            original_writer_allocation_exact=bool(torch.equal(cache.view(torch.int16),expected_cache.view(torch.int16))),
            cross_arm_bitwise=bool(torch.equal(arms['baseline'].out.view(torch.int16),arms['candidate'].out.view(torch.int16))),
            inputs_unchanged=all(bool(torch.equal(a.view(torch.int16 if a.element_size()==2 else torch.int64),b.view(torch.int16 if b.element_size()==2 else torch.int64)))
                for a,b in zip(before_input,(query,key,value,slots))),
            rng_unchanged=bool(torch.equal(rng[0],torch.get_rng_state()) and torch.equal(rng[1],torch.cuda.get_rng_state())),
            output_guard=all(bool((arm.out[B:]==-17).all()) for arm in arms.values()))
        # 先证明实际cache逐位等于CPU原输入overlay，再使用原独立FP64，避免错误writer污染参考。
        if not all(v for k,v in c.items() if k!='phase'):raise RuntimeError('writer Graph/全写字节失败:'+repr(c))
        oracle=sample_reference(torch,run,'writer-'+phase,query,cache,lengths,table,
            {name:arm.out for name,arm in arms.items()},active)
        c['independent_reference']=oracle
        if not all(row['passed'] for row in oracle['arms'].values()):raise RuntimeError('writer Graph FP64失败')
        checks.append(c)
    for target,original in zip((key,value,slots,cache),originals):target.copy_(original)
    return graphs,checks
