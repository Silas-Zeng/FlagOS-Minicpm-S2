"""请求结束且服务清理后，纯CPU读取原快照；不使用/复算GPU。"""
import json
from pathlib import Path


def inspect_row(raw, greedy, hidden, sampled):
    import numpy as np
    counts=lambda x: dict(nan=int(np.isnan(x).sum()),posinf=int(np.isposinf(x).sum()),
        neginf=int(np.isneginf(x).sum()),zero=int((x==0).sum()),numel=x.size)
    result=dict(raw=counts(raw),greedy=counts(greedy),hidden=counts(hidden),sampled_id=int(sampled),
        raw_equals_greedy=bool(np.array_equal(raw,greedy)),
        raw_token0=float(raw[0]),greedy_token0=float(greedy[0]))
    if not bool(np.isfinite(hidden).all()): category='hidden_nonfinite'
    elif not bool(np.isfinite(raw).all()): category='raw_logits_nonfinite'
    elif bool(np.isnan(greedy).any() or np.isposinf(greedy).any()) or not bool(np.isfinite(greedy).any()):
        category='processed_logits_invalid'
    else:
        best=int(greedy.argmax());result['cpu_greedy_argmax']=best
        result['argmax_value']=float(greedy[best]);result['tie_count']=int((greedy==greedy[best]).sum())
        category='argmax_or_row_mismatch' if best!=int(sampled) else 'finite_argmax_agrees'
    result['category']=category
    return result


def analyze(folder):
    import torch
    folder=Path(folder)
    meta=json.loads((folder/'metadata.json').read_text())
    tensors=torch.load(folder/'tensors.pt',map_location='cpu',weights_only=True)
    rows=[];missing=[]
    for step in meta['rows']:
        required={'raw','greedy','hidden','ids','indices'}
        if set(step['copied'])!=required or not step.get('sample_returned'):
            missing.append(step['index']);continue
        data={name:tensors[str(step['index'])+'/'+name] for name in required}
        for i,req in enumerate(step['req_ids']):
            row=dict(step=step['index'],row=i,req_id=req,target=req==meta['target'],
                discarded=bool(step['discard'][i]),logits_index=int(data['indices'][i]),
                M=step['M'],runtime_mode=step.get('runtime_mode'),descriptor=step.get('descriptor'),
                sampling=step.get('sampling'),**inspect_row(data['raw'][i].numpy(),data['greedy'][i].numpy(),data['hidden'][i].float().numpy(),data['ids'][i]))
            rows.append(row)
    relevant=[r for r in rows if r['target'] and not r['discarded']]
    bad=next((r for r in relevant if r['category']!='finite_argmax_agrees'),None)
    token0=next((r for r in relevant if r['sampled_id']==0),None)
    result=dict(valid=bool(rows and relevant and not missing and meta['flushed'] and meta['requests_completed_at_flush']),
        captured_steps=len(meta['rows']),missing_steps=missing,rows=rows,
        first_target_numerical_or_argmax_anomaly=bad,first_target_token0=token0,
        allocated_bytes=meta['allocated_bytes'],performance_claimed=False,
        limitation='只定位已捕获采样边界；有限且argmax一致选0仍不能证明模型正确；无复现不撤销旧失败；并未定位层或PR')
    (folder/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    import sys
    print(json.dumps(analyze(sys.argv[1]),ensure_ascii=False))
