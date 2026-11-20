"""完整融合链的fresh/slot/负slot Graph与独立CPU overlay；原cache不作自身oracle。"""
import numpy as np
from contract import validate

def bits(torch,t):
    return t.detach().contiguous().cpu().view(torch.int16).numpy().view(np.uint16)

def qualify(torch,run,arms,key,value,cache,cache_b,slots,query,lengths,table,sample_reference,active):
    B=active
    saved=[x.clone() for x in (key,value,slots,cache,lengths,table)]
    graphs={}
    for name,arm in arms.items():
        arm.call();arm.call();torch.cuda.synchronize()
        graph=torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):arm.call()
        graphs[name]=graph
    checks=[]
    for phase in ('new_values','coherent_shifted_tail_slot','negative_slot'):
        slots.copy_(saved[2]);lengths.copy_(saved[4]);table.copy_(saved[5])
        key.copy_(saved[0]);value.copy_(saved[1])
        key[0].fill_(0.5);value[0].fill_(-0.25)
        if phase=='coherent_shifted_tail_slot':
            lengths[0]-=1
            n=int(lengths[0].item());page=int(table[0,(n-1)//16].item())
            slots[0]=page*16+(n-1)%16
            key[0,:,0]=2.0**-126;value[0,:,0]=-(2.0**-126)
        if phase=='negative_slot':
            slots[1]=-1
            # Every BF16 payload differs bitwise; expected overlay must still skip row1.
            key[1].view(torch.int16).bitwise_xor_(-32768)
            value[1].view(torch.int16).bitwise_xor_(-32768)
        lens=lengths.cpu().tolist();tab=table.cpu().tolist();mapping=slots.cpu().tolist()
        admission=validate(lens,tab,mapping)
        cache.copy_(saved[3]);cache_b.copy_(saved[3])
        pages=np.unique(np.asarray(mapping,dtype=np.int64)[np.asarray(mapping)>=0]//16)
        ids=torch.tensor(pages,device=cache.device,dtype=torch.int64)
        before_pages=bits(torch,cache.index_select(0,ids))
        lookup={int(page):i for i,page in enumerate(pages)}
        # Poison touched rows before taking the independent expected allocation.
        for slot in mapping:
            if slot>=0:before_pages[lookup[slot//16],:,slot%16]=np.uint16(0xA5A5)
        poisoned=torch.from_numpy(before_pages.view(np.int16)).to(cache.device).view(torch.bfloat16)
        cache.index_copy_(0,ids,poisoned);cache_b.index_copy_(0,ids,poisoned)
        expected=cache.clone()
        source_key,source_value=bits(torch,key[:B]),bits(torch,value[:B])
        for row,slot in enumerate(mapping):
            if slot<0:continue
            p=lookup[slot//16];offset=slot%16
            before_pages[p,0,offset]=source_key[row]
            before_pages[p,1,offset]=source_value[row]
        expected.index_copy_(0,ids,torch.from_numpy(before_pages.view(np.int16)).to(cache.device).view(torch.bfloat16))
        before=[x.clone() for x in (query,key,value,slots,lengths,table)]
        rng=(torch.get_rng_state().clone(),torch.cuda.get_rng_state().clone())
        for name,arm in arms.items():
            for t in arm.tensors:t.fill_(-17)
            graphs[name].replay()
        torch.cuda.synchronize()
        c=dict(phase=phase,metadata_admission=admission,
            baseline_allocation_exact=bool(torch.equal(cache.view(torch.int16),expected.view(torch.int16))),
            fused_allocation_exact=bool(torch.equal(cache_b.view(torch.int16),expected.view(torch.int16))),
            cross_arm_bitwise=bool(torch.equal(arms['baseline'].out.view(torch.int16),arms['candidate'].out.view(torch.int16))),
            inputs_unchanged=all(bool(torch.equal(a.view(torch.int16 if a.element_size()==2 else torch.int64 if a.element_size()==8 else torch.int32),
                b.view(torch.int16 if b.element_size()==2 else torch.int64 if b.element_size()==8 else torch.int32)))
                for a,b in zip(before,(query,key,value,slots,lengths,table))),
            rng_unchanged=bool(torch.equal(rng[0],torch.get_rng_state()) and torch.equal(rng[1],torch.cuda.get_rng_state())),
            guard=all(bool((arm.out[B:]==-17).all()) for arm in arms.values()))
        if not all(v for k,v in c.items() if k not in ('phase','metadata_admission')):
            raise RuntimeError('融合writer Graph/全cache overlay失败:'+repr(c))
        oracle=sample_reference(torch,run,'writer-'+phase,query,expected,lengths,table,{name:arm.out for name,arm in arms.items()},active)
        c['independent_reference']=oracle
        if not all(x['passed'] for x in oracle['arms'].values()):raise RuntimeError('融合writer独立FP64失败')
        checks.append(c)
    for target,original in zip((key,value,slots,cache,lengths,table),saved):target.copy_(original)
    cache_b.copy_(cache)
    return graphs,checks
