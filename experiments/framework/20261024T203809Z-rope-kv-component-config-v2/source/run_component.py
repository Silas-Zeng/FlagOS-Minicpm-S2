"""526实际combo＋KV写入 vs 同数学融合核：独立42层组件，非模型收益。"""
import argparse
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import shutil
import statistics
import subprocess
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=Path('/workspace/experiments/minicpm-s2')
COMMON_SHA='35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
KV_SHA='f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb'
LAYERS,POOL,GUARD=42,258,64
CASES=((2048,2018),(32,32),(64,63))  # 原hint为M2048，先让两臂在该shape热编译，再测小M。

def require(ok,message):
    if not ok:raise ValueError(message)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def save(p,data):Path(p).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now():return datetime.now(timezone.utc).isoformat()
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj;spec.loader.exec_module(obj);return obj

def check_assets():
    pins=read(HERE/'asset-pins.json')
    for name,digest in pins.items():require(sha(HERE/name)==digest,'资产变化: '+name)
    require(sha(HERE/'source/installed-triton_reshape_and_cache_flash.py')==KV_SHA,'原KV源码变化')
    return pins

def validate_slots(slots,actual,rows,pool=POOL):
    require(type(actual) is int and type(rows) is int and rows in (32,64,2048)
            and 0<actual<=rows and type(slots) is tuple and len(slots)==actual,'行数/CPU槽映射不符')
    require(all(type(x) is int and (x<0 or 16<=x<(pool-1)*16) for x in slots),'槽越界/guard页')
    valid=[x for x in slots if x>=0]
    require(len(valid)==len(set(valid)),'重复有效slot须在任何提交前拒绝；不定义竞争赢家')
    return slots

def worker(run):
    run=Path(run);check_assets()
    # 只有root显式启动、父进程持设备锁后才进入本函数。
    import torch
    import importlib
    from torch._C import _cuda_getCurrentRawStream as get_stream
    require(torch.__version__.split('+')[0]=='2.10.0','本实例Torch身份变化')
    props=torch.cuda.get_device_properties(0)
    require(props.multi_processor_count==16 and props.major==7,'只覆盖本实例BI-V150 16SM')
    baseline=module(HERE/'baseline_kernel.py','rope_component_baseline').triton_poi_fused_1
    fused=module(HERE/'candidate_kernel.py','rope_component_fused').rope_kv_fused
    kv=importlib.import_module('vllm.v1.attention.ops.triton_reshape_and_cache_flash')
    require(sha(kv.__file__)==KV_SHA,'实际原KV写入模块变化')
    config=read(HERE/'source/model-config.json')
    require(config['rope_theta']==5000000 and config['rope_scaling'] is None
            and config['max_position_embeddings']==131072 and config['head_dim']==128,'模型RoPE几何变化')
    # 同配置BF16表，数值原件由两条路径共享；不加载模型权重。
    inv=1.0/(float(config['rope_theta'])**(torch.arange(0,128,2,dtype=torch.float32)/128))
    angles=torch.outer(torch.arange(131072,dtype=torch.float32),inv)
    table_cpu=torch.cat((angles.cos(),angles.sin()),dim=-1).to(torch.bfloat16)
    table=table_cpu.to('cuda');table_original=table.clone();scale=torch.ones((),device='cuda',dtype=torch.float32)
    table_hash=hashlib.sha256(table_cpu.view(torch.uint8).numpy().tobytes()).hexdigest()
    del angles,inv,table_cpu
    output={'completed':False,'component_only':True,'source_sha256':check_assets(),
            'reference_run':'20261024T161030Z-main0bf9-main-official-four-rounds',
            'installed_kv_source':str(kv.__file__),'table_bf16_sha256':table_hash,
            'activation_kind':'synthetic BF16, same strided layout; not saved model activations',
            'initial_autotune_rows':2048,
            'cases':[],'model_accuracy_claimed':False,'end_to_end_gain_claimed':False}
    save(run/'results.json',output)
    def bits_equal(a,b):return torch.equal(a.view(torch.uint8),b.view(torch.uint8))
    for rows,actual in CASES:
        # Both arms remain allocated concurrently; 42 different KV/QKV storages, never aliases.
        estimate=LAYERS*(rows*2560*2*2 + 2*(rows*(2048+256)*2+4*GUARD*2) + 2*POOL*16384)+64*(1<<20)
        free,total=torch.cuda.mem_get_info(0)
        require(free>estimate+512*(1<<20),'42层完整组件预算不足，停止而不缩成单层外推')
        torch.manual_seed(721201+rows)
        qkv=[torch.randn((rows,2560),device='cuda',dtype=torch.float32).to(torch.bfloat16) for _ in range(LAYERS)]
        original=[x.clone() for x in qkv]
        positions=torch.arange(rows,device='cuda',dtype=torch.int64).mul_(61).remainder_(131072)
        slots_cpu=tuple(-1 if i%11==0 else 16+(37*i)%4096 for i in range(actual))
        validate_slots(slots_cpu,actual,rows)
        slots=torch.tensor(slots_cpu,device='cuda',dtype=torch.int64)
        arms={}
        for name in ('baseline','fused'):
            layers=[]
            for index in range(LAYERS):
                k_storage=torch.full((rows*256+2*GUARD,),-7,device='cuda',dtype=torch.bfloat16)
                q_storage=torch.full((rows*2048+2*GUARD,),-7,device='cuda',dtype=torch.bfloat16)
                layers.append(dict(k_storage=k_storage,q_storage=q_storage,
                    k=k_storage[GUARD:-GUARD].view(rows,2,128),q=q_storage[GUARD:-GUARD].view(rows,16,128),
                    cache=torch.full((POOL,2,16,2,128),-7,device='cuda',dtype=torch.bfloat16)))
            arms[name]=layers
        pointers=[x.untyped_storage().data_ptr() for x in qkv]
        pointers += [l['cache'].untyped_storage().data_ptr() for layers in arms.values() for l in layers]
        require(len(pointers)==len(set(pointers))==126,'42层或两条路径storage存在alias')
        def prepare(name):
            # Candidate new CPU contract is charged to total wall; no GPU readback.
            if name=='fused':validate_slots(slots_cpu,actual,rows)
            return [(qkv[i],l['k'],l['q'],qkv[i][:,2304:].view(rows,2,128),l['cache'],
                     l['cache'][:,0],l['cache'][:,1]) for i,l in enumerate(arms[name])]
        def launch(name,prepared):
            stream=get_stream(0)
            for x,k,q,v,cache,kc,vc in prepared:
                if name=='baseline':
                    baseline.run(x,positions,table,k,q,rows*256,rows*2048,stream=stream)
                    kv.triton_reshape_and_cache_flash(k,v,kc,vc,slots,'auto',scale,scale)
                else:
                    fused.run(x,positions,table,k,q,rows*256,rows*2048,cache,slots,actual,stream=stream)
        def reset():
            for layers in arms.values():
                for layer in layers:
                    layer['cache'].fill_(-7);layer['k_storage'].fill_(-7);layer['q_storage'].fill_(-7)
        def verify(label):
            valid=torch.tensor([i for i,s in enumerate(slots_cpu) if s>=0],device='cuda',dtype=torch.int64)
            selected=slots[valid]
            for i,(a,b) in enumerate(zip(arms['baseline'],arms['fused'])):
                require(bits_equal(a['q'],b['q']) and bits_equal(a['k'],b['k']),f'{label}: Q/K位模式差异层{i}')
                require(bits_equal(qkv[i],original[i]),f'{label}: QKV/V输入被改写层{i}')
                expected=torch.full_like(a['cache'],-7)
                expected[selected//16,0,selected%16]=a['k'][valid]
                expected[selected//16,1,selected%16]=qkv[i][:,2304:].view(rows,2,128)[valid]
                require(bits_equal(a['cache'],expected) and bits_equal(b['cache'],expected),f'{label}: KV/guard/未写页差异层{i}')
                for arm in (a,b):
                    for key in ('q_storage','k_storage'):
                        require(bool(torch.all(arm[key][:GUARD]==-7)) and bool(torch.all(arm[key][-GUARD:]==-7)),f'{label}: 输出guard变化')
            require(bits_equal(table,table_original),f'{label}: cos表变化')
            return dict(q_k_bitwise=True,v_and_qkv_unchanged=True,all_layer_cache_bitwise=True,
                        negative_and_padding_skipped=True,guards_and_unselected_unchanged=True,layers=42)
        # Warm and numerical gate before timing; all compilation excluded from samples.
        for name in ('baseline','fused'):launch(name,prepare(name))
        torch.cuda.synchronize();eager_check=verify('eager')
        graphs={};capture_stream=torch.cuda.Stream();capture_stream.wait_stream(torch.cuda.current_stream())
        for name in ('baseline','fused'):
            args=prepare(name);graph=torch.cuda.CUDAGraph()
            with torch.cuda.graph(graph,stream=capture_stream):launch(name,args)
            graphs[name]=graph
        torch.cuda.current_stream().wait_stream(capture_stream);torch.cuda.synchronize()
        graph_checks=[]
        for version in range(2):
            for i,x in enumerate(qkv):x.add_(0.125 if version==0 else -0.0625);original[i].copy_(x)
            positions.add_(17).remainder_(131072)
            # Stable GPU addresses, changed values. Second32 case also proves all-negative slots.
            slots_cpu=tuple(-1 if rows==32 and version==1 or i%7==0 else 16+(37*i+23*(version+1))%4096 for i in range(actual))
            validate_slots(slots_cpu,actual,rows);slots.copy_(torch.tensor(slots_cpu,device='cuda',dtype=torch.int64))
            reset();torch.cuda.synchronize()
            for name in ('baseline','fused'):graphs[name].replay()
            torch.cuda.synchronize();graph_checks.append(verify('graph_changed_'+str(version)))
        # Restore representative nonempty mapping for samples, no transfers inside either sample.
        slots_cpu=tuple(-1 if i%11==0 else 16+(37*i)%4096 for i in range(actual))
        slots.copy_(torch.tensor(slots_cpu,device='cuda',dtype=torch.int64));torch.cuda.synchronize()
        samples=[]
        def measure(name,execution):
            start,end=torch.cuda.Event(enable_timing=True),torch.cuda.Event(enable_timing=True)
            t0=time.perf_counter();args=prepare(name);prepared_at=time.perf_counter();start.record()
            if execution=='eager':launch(name,args)
            else:graphs[name].replay()
            end.record();end.synchronize();done=time.perf_counter()
            return dict(arm=name,execution=execution,metadata_prepare_ms=(prepared_at-t0)*1000,
                        device_window_ms=start.elapsed_time(end),total_wall_ms=(done-t0)*1000)
        for execution in ('eager','graph'):
            for pair,order in enumerate((('baseline','fused'),('fused','baseline'),('baseline','fused'))):
                for name in order:samples.append(dict(pair=pair,**measure(name,execution)))
        row=dict(rows=rows,actual_rows=actual,layers=42,cache_pool=POOL,estimated_allocated_bytes=estimate,
                 free_before_bytes=free,total_device_bytes=total,eager_correctness=eager_check,
                 changed_input_graph_correctness=graph_checks,samples=samples,
                 memory_allocated_bytes=torch.cuda.memory_allocated(),memory_reserved_bytes=torch.cuda.memory_reserved(),
                 original_config=[str(c) for c in (getattr(baseline,'configs',[]) or [])],
                 fused_config=[str(c) for c in (getattr(fused,'configs',[]) or [])],
                 selected_launchers={name:[{'config':str(getattr(fn,'config',None)),
                                           'n_regs':str(getattr(fn,'n_regs',None)),
                                           'n_spills':str(getattr(fn,'n_spills',None))}
                                          for fn in (getattr(kernel,'launchers',[]) or [])]
                                     for name,kernel in [('baseline',baseline),('fused',fused)]})
        row['medians']={execution:{name:{metric:statistics.median(s[metric] for s in samples if s['execution']==execution and s['arm']==name)
                                       for metric in ('metadata_prepare_ms','device_window_ms','total_wall_ms')}
                                  for name in ('baseline','fused')} for execution in ('eager','graph')}
        output['cases'].append(row);save(run/'results.json',output)
        graphs.clear();del graph,args,arms,qkv,original,positions,slots,capture_stream,layers,k_storage,q_storage,x
        gc.collect();torch.cuda.synchronize()
    output.update(completed=True,all_correctness_passed=True,
                  limitations=['独立BF16合成激活组件；不替代模型准确率或官方吞吐。',
                    '42独立层避免单tensor反复访问；未测实际L2命中率，不宣称完全冷cache。',
                    'Graph事件只度量原始CUDA Graph组件；新custom-op mutation/模型图接线尚未实现。',
                    '每个capture的actual_rows固定为32/63/2018；变输入重放不证明同一图支持actual_rows变化。',
                    'CPU完整slot元组仅属于组件输入，校验成本计入候选wall；不证明实际runner已有CPU页映射或廉价唯一性，未来不可为此加GPU回读。',
                    '原动态combo数学由526实际handle绑定；两臂按原heuristic重新编译热身并保存本次launcher配置，未直接复用旧机器码或锁定旧服务XBLOCK。',
                    '组件完整路径对照不能解释旧服务精确核占比或外推整模型收益；实际模型接线后仍须端到端验证。'])
    save(run/'results.json',output)
    return 0

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker: return worker(args.run_dir)
    import fcntl
    check_assets()
    common_path = ROOT/'scripts/run_accuracy_gate.py'
    require(sha(common_path)==COMMON_SHA, '原设备清理helper变化')
    common = module(common_path, 'budget_common')
    run = args.run_dir.resolve()
    require(run.is_relative_to(ROOT/'diagnostics') and run != ROOT/'diagnostics', '只允许独立diagnostics目录')
    run.mkdir(parents=True, exist_ok=False)
    state = dict(started_utc=now(), owner_pid=os.getpid(), command=sys.argv, completed=False, diagnostic=True)
    process = None
    lock = (ROOT/'framework-device.lock').open('a')
    def stop(signum, frame): raise KeyboardInterrupt(str(signum))
    for sig in (signal.SIGTERM,signal.SIGINT): signal.signal(sig,stop)
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        state['preflight'] = common.preflight()
        table = subprocess.check_output([common.IXSMI],text=True,timeout=10)
        query = subprocess.check_output([common.IXSMI,'--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=10)
        (run/'preflight-ixsmi.txt').write_text(table)
        require('No running processes found' in table and query.strip()=='68, 0', '启动前设备不空闲')
        env = {k:v for k,v in os.environ.items() if not k.startswith(('BIV150_','VLLM_FL_BIV150_','MINICPM_NATIVE_','MINICPM_DECODE_GAP_'))}
        env.pop('PYTHONPATH',None); env['PYTHONUNBUFFERED']='1'
        state['assets'] = check_assets()
        (run/'source').mkdir()
        for name in [*state['assets'],'asset-pins.json']:
            (run/'source'/name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(HERE/name,run/'source'/name)
        save(run/'manifest.json',state)
        with (run/'worker.log').open('x') as log:
            process = subprocess.Popen([sys.executable,'-B',str(Path(__file__).resolve()),'--run-dir',str(run),'--worker'],
                env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        state['worker_pid']=process.pid; save(run/'manifest.json',state)
        deadline=time.monotonic()+300
        with (run/'gpu.csv').open('x') as output:
            fields='timestamp,memory.used,memory.total,utilization.gpu'
            output.write(fields+'\n'); output.flush()
            while process.poll() is None:
                require(time.monotonic()<deadline,'组件编译/校验超过300秒，停止，不自动重试')
                output.write(subprocess.check_output([common.IXSMI,'--query-gpu='+fields,'--format=csv,noheader'],text=True,timeout=10))
                output.flush(); time.sleep(1)
        state['worker_exit_code']=process.wait()
        require(process.returncode==0 and read(run/'results.json')['completed'],'worker失败；保留原件')
        state['completed']=True
    except BaseException: state['error']=traceback.format_exc()
    finally:
        try:
            common.stop_owned_group(process,timeout=6)
            state['postflight']=common.preflight()
            state['postflight_query']=subprocess.check_output([common.IXSMI,'--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=10)
            require(state['postflight_query'].strip()=='68, 0','收尾GPU未回空闲基准')
            state['source_unchanged']=check_assets()==state.get('assets')
            require(state['source_unchanged'],'资产变化')
        except BaseException: state.update(completed=False,cleanup_error=traceback.format_exc())
        state['finished_utc']=now(); save(run/'state.json',state)
        (run/'exit-code').write_text('0\n' if state['completed'] else '1\n')
        lock.close()
    return 0 if state['completed'] else 1

if __name__=='__main__': raise SystemExit(main())
