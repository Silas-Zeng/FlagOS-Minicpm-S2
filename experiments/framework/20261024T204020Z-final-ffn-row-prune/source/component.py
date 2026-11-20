"""实权重末层组件；只有持设备锁的外层负责人才能显式调用run，导入本文件不导入Torch。"""
import hashlib
import importlib.util
import inspect
import json
import os
from pathlib import Path
import statistics
import sys
import time

HERE = Path(__file__).resolve().parent
CASES = ((2048,32), (2048,64), (32,32), (64,64))
KEYS = {
    'postnorm': ('model.layers.41.post_attention_layernorm.weight', (2048,)),
    'gate': ('model.layers.41.mlp.gate_proj.weight', (6144,2048)),
    'up': ('model.layers.41.mlp.up_proj.weight', (6144,2048)),
    'down': ('model.layers.41.mlp.down_proj.weight', (2048,6144)),
    'finalnorm': ('model.norm.weight', (2048,)),
}
MM_SHA = '4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090'

def require(ok, message):
    if not ok: raise ValueError(message)

def save(path, value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def enable_service_dispatch(torch, run_dir):
    # 固定161030单卡worker的enable-all分支，vendor默认排除项仍由原FlagGems处理。
    for key in ('VLLM_FL_FLAGOS_WHITELIST','VLLM_FL_FLAGOS_BLACKLIST','VLLM_FL_FLAGOS_BLACKLIST_APPEND',
                'FLAGGEMS_DB_URL','FLAGGEMS_CACHE_DIR'):
        require(not os.environ.get(key), '组件不接受不同服务dispatch/cache覆盖: '+key)
    require(os.environ.get('USE_FLAGGEMS','True').lower() in ('true','1'),'FlagGems被关闭')
    import flag_gems
    flag_gems.enable(record=True, once=True, path=str(run_dir/'flaggems-oplist.txt'))
    registrar=flag_gems.current_work_registrar
    active=set(registrar.get_all_keys())
    require({'mm.out','index.Tensor'}.issubset(active),'真实mm.out/index.Tensor未注册FlagGems')
    records={}
    (run_dir/'dispatch-source').mkdir(exist_ok=True)
    for op,name in (('mm.out','mm_out'),('index.Tensor','index')):
        entries=[x for x in registrar.config if x[0]==op]
        require(len(entries)==1 and entries[0][1] is getattr(flag_gems,name),'当前registrar函数绑定不一致: '+op)
        fn=inspect.unwrap(entries[0][1]);path=Path(inspect.getsourcefile(fn)).resolve(strict=True)
        raw=path.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        if op=='mm.out':require(digest==MM_SHA,'实际BI mm_out不同于161030来源')
        (run_dir/'dispatch-source'/f'{name}.py').write_bytes(raw)
        table=torch._C._dispatch_dump_table('aten::'+op)
        (run_dir/f'dispatch-{name}.txt').write_text(table,encoding='utf-8')
        require(any(line.startswith('CUDA:') and 'flag_gems/' in line.replace('\\','/')
                    for line in table.splitlines()),'实际CUDA dispatcher未指向FlagGems: '+op)
        records[op]={'module':fn.__module__,'qualname':fn.__qualname__,'source':str(path),
                     'source_sha256':digest,'cuda_dispatch_flaggems':True,'registered':True}
    records['exclude_ops']=list(registrar.get_unused_ops())
    save(run_dir/'dispatch.json',records)
    return records

def checked_indices(m, s, version=0, identity=False):
    require(type(m) is int and type(s) is int and 0<s<=m, '选择行数非法')
    if identity:
        require(m==s, 'identity decode要求S=M')
        return tuple(range(m))
    # 非单调逻辑行序；第二组含重复行，证明不排序/不去重。不是官方请求的真实indices。
    rows = tuple((m-1-61*i-17*version)%m for i in range(s))
    if version: rows = rows[:-1]+(rows[0],)
    require(len(rows)==s and all(0<=i<m for i in rows), 'indices越界')
    return rows

def load_weights(torch, model):
    from safetensors import safe_open
    model = Path(model).resolve(strict=True)
    config = json.loads((model/'config.json').read_bytes())
    require(all(config.get(k)==v for k,v in {'hidden_size':2048,'intermediate_size':6144,
            'num_hidden_layers':42,'hidden_act':'silu','rms_norm_eps':1e-6}.items()),'checkpoint几何变化')
    found = {}; records = {}
    for path in sorted(model.glob('*.safetensors')):
        with safe_open(str(path), framework='pt', device='cpu') as source:
            keys = set(source.keys())
            for alias,(key,shape) in KEYS.items():
                if key not in keys: continue
                require(alias not in found, '重复权重键: '+key)
                tensor = source.get_tensor(key)
                require(tuple(tensor.shape)==shape and tensor.dtype==torch.bfloat16, '权重shape/dtype变化: '+key)
                require(tensor.is_contiguous(), '实际checkpoint非连续，禁止静默换stride: '+key)
                records[alias] = {'key':key,'file':path.name,'shape':list(shape),'stride':list(tensor.stride()),
                    'bf16_sha256':hashlib.sha256(tensor.view(torch.uint8).numpy().tobytes()).hexdigest()}
                found[alias] = tensor
    require(set(found)==set(KEYS),'缺少实际末层权重，不使用随机权重替代')
    # installed Llama.load_weights: gate shard0, up shard1；与实际wrapper [12288,2048]一致。
    merged = torch.cat((found['gate'],found['up']),dim=0)
    weights = tuple(x.to('cuda') for x in (found['postnorm'],merged,found['down'],found['finalnorm']))
    require([tuple(x.stride()) for x in weights]==[(1,),(2048,1),(6144,1),(1,)],'设备实际权重stride变化')
    return weights, records, hashlib.sha256((model/'config.json').read_bytes()).hexdigest()

def run(run_dir, model_path='/workspace/MiniCPM5-2B'):
    """外层负责实时GPU/9031空闲、独占设备锁、PID/日志、异常进程组清理；本函数不启服务。"""
    run_dir=Path(run_dir);run_dir.mkdir(parents=True,exist_ok=True)
    pins=json.loads((HERE/'asset-pins.json').read_bytes())
    for name,digest in pins.items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'组件资产变化: '+name)
    import torch
    require(torch.__version__.split('+')[0]=='2.10.0','Torch版本变化')
    torch.cuda.set_device(0)
    props=torch.cuda.get_device_properties(0)
    require(props.multi_processor_count==16 and props.major==7,'非本实例BI-V150 16SM')
    dispatch=enable_service_dispatch(torch,run_dir)
    spec=importlib.util.spec_from_file_location('row_prune_exact_suffix',HERE/'exact_suffix.py')
    exact=importlib.util.module_from_spec(spec);sys.modules[spec.name]=exact;spec.loader.exec_module(exact)
    weights,weight_evidence,config_sha=load_weights(torch,model_path)
    result={'completed':False,'component_only':True,'source_pins':pins,'weights':weight_evidence,'dispatch':dispatch,
            'config_sha256':config_sha,'activation_kind':'synthetic BF16 post-o_proj and residual, actual strides',
            'cases':[],'model_accuracy_claimed':False,'end_to_end_gain_claimed':False,
            'o_proj_saving_claimed':False,'comparison_tolerance':'record BF16 differences; no arbitrary accuracy pass threshold'}
    save(run_dir/'results.json',result)
    def bitwise(a,b):return torch.equal(a.view(torch.uint8),b.view(torch.uint8))
    def difference(a,b):
        require(a.shape==b.shape and a.dtype==b.dtype==torch.bfloat16,'输出shape/dtype错误')
        require(bool(torch.isfinite(a).all() and torch.isfinite(b).all()),'出现非有限输出')
        x,y=a.float(),b.float();d=(x-y).abs()
        return {'bitwise_equal':bitwise(a,b),'elements':a.numel(),
                'different_elements':int((a!=b).sum().item()),'max_abs':d.max().item(),
                'rms_abs':d.square().mean().sqrt().item(),
                'relative_l2':(d.square().sum().sqrt()/x.square().sum().sqrt().clamp_min(1e-20)).item(),
                'reference_abs_max':x.abs().max().item(),'both_finite':True}
    try:
        for m,s in CASES:
            identity=m==s
            torch.manual_seed(504100+m+s)
            projected=torch.randn((m,2048),device='cuda',dtype=torch.float32).to(torch.bfloat16)
            residual=torch.randn((m,2048),device='cuda',dtype=torch.float32).mul_(2).to(torch.bfloat16)
            require(projected.stride()==residual.stride()==(2048,1),'激活stride不符实际wrapper')
            ids=checked_indices(m,s,identity=identity)
            indices=torch.tensor(ids,device='cuda',dtype=torch.int64)
            def baseline():
                return exact.suffix(projected,residual,*weights)[indices]
            def candidate():
                if identity:
                    # scheduler已知identity；保持原全行＋末尾选行，不增加两次gather。
                    return baseline()
                a=projected[indices]
                r=residual[indices]
                return exact.suffix(a,r,*weights)
            funcs={'baseline':baseline,'candidate':candidate}
            original=(projected.clone(),residual.clone(),indices.clone())
            for name in funcs:
                for _ in range(2): funcs[name]()
            torch.cuda.synchronize()
            executed=(run_dir/'flaggems-oplist.txt').read_text(encoding='utf-8')
            require('.mm_out:' in executed and '.index:' in executed,'本组件未记录实际mm_out/index执行')
            result['dispatch_execution_observed']={'mm_out':True,'index':True,'evidence':'flaggems-oplist.txt'}
            eager=difference(baseline(),candidate());torch.cuda.synchronize()
            require(all(bitwise(a,b) for a,b in zip((projected,residual,indices),original)),'输入被改写')
            if identity:require(eager['bitwise_equal'],'identity decode不应改变原路径')
            graphs={};outputs={};capture_stream=torch.cuda.Stream()
            capture_stream.wait_stream(torch.cuda.current_stream())
            for name,fn in funcs.items():
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=capture_stream): outputs[name]=fn()
                graphs[name]=graph
            torch.cuda.current_stream().wait_stream(capture_stream);torch.cuda.synchronize()
            changes=[]
            for version in (1,2):
                projected.add_(0.125 if version==1 else -0.25)
                residual.mul_(0.75 if version==1 else 1.25)
                ids=checked_indices(m,s,version,identity=identity)
                indices.copy_(torch.tensor(ids,device='cuda',dtype=torch.int64))
                original=(projected.clone(),residual.clone(),indices.clone())
                torch.cuda.synchronize()
                graphs['baseline'].replay();graphs['candidate'].replay();torch.cuda.synchronize()
                diff=difference(outputs['baseline'],outputs['candidate'])
                fresh=baseline();torch.cuda.synchronize()
                require(bitwise(fresh,outputs['baseline']),'Graph baseline未随新激活/residual/indices更新')
                fresh_candidate=candidate();torch.cuda.synchronize()
                require(bitwise(fresh_candidate,outputs['candidate']),'Graph candidate未随新激活/residual/indices更新')
                require(all(bitwise(a,b) for a,b in zip((projected,residual,indices),original)),'Graph改写输入')
                if identity:require(diff['bitwise_equal'],'Graph identity decode变化')
                changes.append({'version':version,'indices':list(ids),'comparison':diff,
                                'baseline_graph_matches_fresh':True,'candidate_graph_matches_fresh':True,
                                'inputs_unchanged':True})
            # 恢复无重复但不排序的代表indices；所有gather在各自函数/graph内部计时。
            indices.copy_(torch.tensor(checked_indices(m,s,identity=identity),device='cuda',dtype=torch.int64))
            torch.cuda.synchronize();samples=[]
            for execution in ('eager','graph'):
                for pair,order in enumerate((('baseline','candidate'),('candidate','baseline'),('baseline','candidate'))):
                    for name in order:
                        start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
                        t0=time.perf_counter();start.record()
                        for _ in range(5):
                            if execution=='eager': answer=funcs[name]()
                            else: graphs[name].replay()
                        end.record();end.synchronize();wall=(time.perf_counter()-t0)*1000/5
                        samples.append({'execution':execution,'pair':pair,'arm':name,'calls':5,
                                        'wall_ms_per_call':wall,'event_ms_per_call':start.elapsed_time(end)/5})
            row={'M':m,'S':s,'identity_decode_original_path':identity,'eager_comparison':eager,
                 'changed_input_graph':changes,'samples':samples,
                 'candidate_input_gather_count':0 if identity else 2,
                 'candidate_gather_output_bytes':0 if identity else 2*s*2048*2,
                 'memory_allocated_bytes':torch.cuda.memory_allocated(),
                 'memory_reserved_bytes':torch.cuda.memory_reserved()}
            row['median_wall_ms']={mode:{name:statistics.median(x['wall_ms_per_call'] for x in samples
                if x['execution']==mode and x['arm']==name) for name in funcs} for mode in ('eager','graph')}
            result['cases'].append(row);save(run_dir/'results.json',result)
            # 数据/图/输出保持到完成；不在异步运行期间复用或释放。
            torch.cuda.synchronize();graphs.clear();outputs.clear()
            del graph,answer,fresh,fresh_candidate,original,projected,residual,indices,capture_stream
        result.update(completed=True,limitations=[
            '实权重、合成激活；只测最后一层suffix，未纳入真实logits_indices准备/模型接线或官方成绩。',
            '候选减少M可能改变BLAS实现/舍入，prefill数值差异原样记录，最终须模型准确率。',
            '复用实际生成数学与heuristic，重新热编译；不冒称复用原服务机器码或launcher。',
            'CUDA Graph固定每case的M/S；改变输入/residual/indices值，不证明单图可改变S。',
            '两次candidate gather与原baseline末尾gather全部计入wall/event；o_proj未计入任何一臂。',
            'decode identity是明确CPU已知合同；实际S=M不一定identity，不能据长度自行跳过选择。'])
        save(run_dir/'results.json',result)
        return result
    finally:
        # 外层仍须终止失败进程/检查设备；错误不重试或静默回退。
        torch.cuda.synchronize()
