"""独立CPU FP64页表参考；复用原Attention合成输入族的固定比较合同。"""
import numpy as np

def sampled_reference(torch,run,label,query,cache,seq_lens,table,outputs,active):
    selected=sorted({0,1,4,8,10,13,14,15,active-2,active-1})
    selected=[row for row in selected if 0<=row<active]
    lengths=seq_lens.detach().cpu().tolist()
    pages=table.detach().cpu().numpy().astype(np.int64)
    q=query.detach().float().cpu().numpy().astype(np.float64)
    reference=np.zeros((len(selected),16,128),dtype=np.float64)
    for i,row in enumerate(selected):
        length=int(lengths[row])
        if length==0:continue
        # Trusted tensor indexing only gathers the raw source pages. All attention
        # math is CPU NumPy FP64 and independent of both Triton implementations.
        ids=torch.tensor(pages[row,:(length+15)//16],device=cache.device,dtype=torch.int64)
        logical=cache.index_select(0,ids).detach().float().cpu().numpy()
        k=logical[:,0].reshape(-1,2,128)[:length].astype(np.float64)
        v=logical[:,1].reshape(-1,2,128)[:length].astype(np.float64)
        for head in range(2):
            scores=(q[row,head*8:(head+1)*8] @ k[:,head].T) * (128**-0.5)
            probability=np.exp(scores-scores.max(axis=1,keepdims=True))
            probability/=probability.sum(axis=1,keepdims=True)
            reference[i,head*8:(head+1)*8]=probability @ v[:,head]
    samples={};stats={}
    for name,output in outputs.items():
        actual=output.detach().float().cpu().numpy()[selected].astype(np.float64)
        error=actual-reference
        finite=bool(np.isfinite(actual).all())
        relative_l2=float(np.linalg.norm(error)/max(float(np.linalg.norm(reference)),1e-300)) if finite else None
        max_abs=float(np.abs(error).max()) if finite else None
        samples[name]=actual
        stats[name]=dict(finite=finite,max_abs=max_abs,relative_l2=relative_l2,
            passed=bool(finite and np.allclose(actual,reference,atol=.03,rtol=.03) and relative_l2<=.01))
    np.savez(run/(label+'-fp64.npz'),reference=reference,rows=selected,lengths=np.array(lengths)[selected],**samples)
    return dict(source='scripts/remote/validate_mapped_decode.py:70-92; FP64 CPU实现与额外relative_l2界',
        atol=.03,rtol=.03,relative_l2_limit=.01,rows=selected,heads=list(range(16)),
        lengths=[lengths[row] for row in selected],arms=stats,scope='合成组件抽样，不是模型准确率')
