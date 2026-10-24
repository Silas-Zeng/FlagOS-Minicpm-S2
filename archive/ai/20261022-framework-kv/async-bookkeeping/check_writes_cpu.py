"""仅检查真实helper新增writes/原fallback；不模拟框架install或GPU。"""
import ast
import hashlib
import json
from pathlib import Path
import runpy
from types import SimpleNamespace as NS
import numpy as np


def main():
    here = Path(__file__).parent
    old = runpy.run_path(str(here / 'compare_cpu_fragment.py'))
    policy = runpy.run_path(str(here / 'biv150_async_bookkeeping.py'))
    prep = runpy.run_path(str(here / 'prepare_async_bookkeeping_service.py'))
    source = old['DEFAULT_RUNNER']
    baseline, _ = old['extract_baseline'](source)
    selected = policy['try_bulk_bookkeeping']
    checks = {}
    for n in (30, 31, 64):
        a, b = old['fixture'](n, baseline), old['fixture'](n, baseline)
        old['reset'](a,n); old['reset'](b,n)
        batch = b.input_batch
        batch.req_id_to_index = {rid:i for i,rid in enumerate(batch.req_ids)}
        for rid, req in b.requests.items(): req.req_id = rid
        b.speculative_config = None; b.num_spec_tokens = b.prev_num_spec_tokens = 0
        setattr(b,policy['STATE'], {'batch':batch,'rows':b.arange_np,'request_type':NS,
            'arrays':(batch.token_ids_cpu,batch.is_token_ids,batch.num_tokens_no_spec),
            'selected':0,'disabled':False})
        sample = NS(shape=(n,1),device=NS(type='cuda'))
        output = NS(total_num_scheduled_tokens=n)
        for _ in range(4):
            baseline(a,n,set(),True,n)
            assert selected(b,n,sample,set(),output)
        checks['N'+str(n)+'_writes_history'] = all((
            np.array_equal(a.input_batch.token_ids_cpu,batch.token_ids_cpu),
            np.array_equal(a.input_batch.is_token_ids,batch.is_token_ids),
            np.array_equal(a.input_batch.num_tokens_no_spec,batch.num_tokens_no_spec),
            all(a.requests[r].output_token_ids == b.requests[r].output_token_ids for r in b.requests)))
        counts = batch.num_tokens_no_spec.copy()
        histories = [list(b.requests[r].output_token_ids) for r in batch.req_ids]
        assert selected(b,n,sample,{0},output) is False
        assert selected(b,n,NS(shape=(n,2),device=sample.device),set(),output) is False
        assert selected(b,n,sample,set(),NS(total_num_scheduled_tokens=n+1)) is False
        checks['N'+str(n)+'_unknown_before_write'] = np.array_equal(counts,batch.num_tokens_no_spec) and histories == [b.requests[r].output_token_ids for r in batch.req_ids]
    # N1不读取runner；同步caller不求未定义invalid_set，不调用helper。
    checks['N1_no_runner_read'] = selected(object(),1,None,None,None) is False
    changed = prep['transform'](source.read_bytes(),(here/'service_append.py').read_bytes())
    text = changed.decode(); tree = ast.parse(text)
    cls = next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name=='ModelRunnerFL')
    method = next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='_bookkeeping_sync')
    gate = next(x for x in method.body if isinstance(x,ast.If) and isinstance(x.test,ast.UnaryOp) and any(isinstance(y,ast.Name) and y.id=='_biv150_try_bulk_bookkeeping' for y in ast.walk(x.test)))
    expr = ast.Expression(gate.test)
    checks['sync_shortcircuits_missing_invalid_set'] = eval(compile(ast.fix_missing_locations(expr),'<gate>','eval'),{'self':NS(use_async_scheduling=False),'num_sampled_tokens':30}) is True
    checks['N1_shortcircuits_missing_invalid_set'] = eval(compile(expr,'<gate>','eval'),{'self':NS(use_async_scheduling=True),'num_sampled_tokens':1}) is True
    assert all(checks.values()),checks
    result = {'checks':checks,'status':'passed','candidate_runner_sha256':hashlib.sha256(changed).hexdigest(),
        'limits':['CPU descriptors/cached scope only; real _initial_state/actual Tensor/GPU/service not executed',
                  'same original loop, import/guard/footer exact reverse asserted by transform',
                  'no old benchmark rerun; original CPU percentages exclude new per-request guards',
                  'all preparation before writes; errors after first mutation propagate without retry']}
    (here/'writes-cpu-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':'passed','checks':len(checks),'candidate_runner_sha256':result['candidate_runner_sha256']}))

if __name__=='__main__':main()
