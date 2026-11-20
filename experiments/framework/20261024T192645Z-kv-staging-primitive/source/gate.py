"""535真实碎片传输 vs 单层scratch gather/scatter；仅primitive数值/时间，不运行模型。"""
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

HERE = Path(__file__).resolve().parent
ROOT = Path('/workspace/experiments/minicpm-s2')
COMMON_SHA = '35d30dfa4fc4d583c7fc62db1f18c992a7fd6a7e54fab95749710759b5df6a54'
CUDART_SHA = 'd39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527'
PAGE, GiB = 16384, 1 << 30

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_bytes())
def save(p, x): Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
def require(x, message):
    if not x: raise ValueError(message)
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    sys.modules[name] = obj
    spec.loader.exec_module(obj)
    return obj
def check_assets():
    pins = read(HERE / 'asset-pins.json')
    for name, digest in pins.items(): require(sha(HERE / name) == digest, '资产变化: ' + name)
    build = read(HERE/'build/manifest.json')
    require(build.get('compiled') is True and build.get('source_sha256') == pins['staging.cu']
            and build.get('builder_sha256') == pins['build.py'], 'primitive必须由当前源实际编译')
    require(not (HERE/'build/staging.so').is_symlink() and sha(HERE/'build/staging.so') == build['library_sha256']
            and sha(HERE/'build/build.log') == build['build_log_sha256'], 'primitive构建SO/日志变化')
    return dict(pins, **{'build/manifest.json':sha(HERE/'build/manifest.json'),
                        'build/staging.so':build['library_sha256'], 'build/build.log':build['build_log_sha256']})

def cpu_state():
    files = ('/sys/fs/cgroup/cpu.stat', '/sys/fs/cgroup/cpu.max',
             '/sys/fs/cgroup/cpu,cpuacct/cpu.stat', '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us',
             '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us')
    return {p: Path(p).read_text().strip() for p in files if Path(p).exists()}
def host_memory():
    values, budgets = {}, []
    for used, limit in (('/sys/fs/cgroup/memory.current', '/sys/fs/cgroup/memory.max'),
                        ('/sys/fs/cgroup/memory/memory.usage_in_bytes', '/sys/fs/cgroup/memory/memory.limit_in_bytes')):
        if Path(used).exists() and Path(limit).exists():
            u, m = Path(used).read_text().strip(), Path(limit).read_text().strip()
            values.update({used: u, limit: m})
            if u.isdigit() and m.isdigit(): budgets.append(int(m) - int(u))
    for line in Path('/proc/meminfo').read_text().splitlines():
        if line.startswith('MemAvailable:'): budgets.append(int(line.split()[1]) * 1024)
    require(budgets, '缺少可核host预算')
    return dict(raw=values, headroom_bytes=min(budgets))

def worker(run):
    pins = check_assets()
    trace = read(HERE / 'trace-case.json')
    pool, count = trace['pool_blocks'], trace['logical_page_count']
    ids = {'fragmented': (trace['source_pages'], trace['destination_pages']),
           'staged': (trace['source_pages'], trace['destination_pages'])}
    result = dict(started_utc=now(), pid=os.getpid(), diagnostic=True, official_performance=False,
                  trace_case_sha256=pins['trace-case.json'], samples=[], correctness={}, completed=False,
                  limitations=['实际staging总成本含临时分配、索引上传、pack/scatter及同stream完成；仍不是模型端到端收益。',
                               '本门无模型/服务并发，producer fence为空闲事务围栏，不能代表生产等待。',
                               'CUDA event包含两次record间同流提交空档，不是独立纯DMA时长。',
                               'SDK调用数不是硬件DMA描述符数；单层结果不外推42层。'])
    torch = None
    try:
        import torch
        torch.set_num_threads(6)
        require(torch.cuda.device_count() == 1, '要求唯一设备')
        torch.cuda.set_device(0)
        props = torch.cuda.get_device_properties(0)
        require('BI-V150' in props.name and props.multi_processor_count == 16, '设备不是本实例16SM BI-V150')
        free, total = torch.cuda.mem_get_info()
        hm = host_memory()
        layer_raw, layer_payload = pool * PAGE, count * PAGE
        # host: expected/output各P + 一层完整回读 + 一层bool校验临时空间 + 1GiB余量。
        budgets = {n: dict(device=n*layer_raw + layer_payload + count*8 + 2*GiB,
                           host=2*n*layer_payload + 2*layer_raw + count*16 + GiB) for n in (42, 1)}
        layers = next((n for n in (42, 1) if free >= budgets[n]['device'] and hm['headroom_bytes'] >= budgets[n]['host']), None)
        require(layers is not None, '单层也超预算，停止；不缩页映射或别名42层')
        result.update(layers=layers, full_42_layers=layers == 42, torch_version=torch.__version__,
                      device=str(props), memory_before=dict(device_free=free, total=total, host=hm),
                      budget=budgets[layers], bytes_per_direction=layers*layer_payload,
                      fallback_reason=None if layers == 42 else '42层预算不够，明确仅单层，不外推')
        runtime = module(HERE / 'biv150_kv_pitched_copy.py', 'budget_save_runtime')
        restore = module(HERE / 'biv150_kv_pitched_restore.py', 'budget_restore_runtime')
        sb = runtime.Bridge(HERE / 'biv150_kv_pitched_bridge.so', expected_sha256=pins['biv150_kv_pitched_bridge.so'])
        rb = restore.RestoreBridge(HERE / 'biv150_kv_pitched_restore_bridge.so',
            expected_sha256=pins['biv150_kv_pitched_restore_bridge.so'], save_runtime=runtime)
        stage = module(HERE/'staging.py', 'actual_staging_primitive')
        stage_build = read(HERE/'build/manifest.json')
        bridge = stage.Bridge(HERE/'build/staging.so', expected_sha256=stage_build['library_sha256'])
        result['staging_build'] = stage_build
        libraries = {str(Path(parts[5]).resolve()) for line in Path('/proc/self/maps').read_text().splitlines()
                     if len(parts := line.split(None, 5)) == 6 and 'libcudart.so' in Path(parts[5]).name}
        result['loaded_libcudart'] = {p: sha(p) for p in sorted(libraries)}
        require(len(libraries) == 1 and set(result['loaded_libcudart'].values()) == {CUDART_SHA}, 'CoreX SDK身份不符')
        pitch = min(sb.max_pitch(0), rb.max_pitch(0))
        stream = torch.cuda.current_stream(0)
        result.update(stream_handle=int(stream.cuda_stream), max_pitch=pitch, cpu_before=cpu_state())
        started = time.perf_counter_ns()
        raw = [torch.empty((pool, PAGE), dtype=torch.uint8, device='cuda') for _ in range(layers)]
        require(len({x.untyped_storage().data_ptr() for x in raw}) == layers, '禁止跨层storage别名')
        result['device_allocate_ms'] = (time.perf_counter_ns()-started)/1e6
        started = time.perf_counter_ns()
        expected = [torch.empty((count, PAGE), dtype=torch.uint8, pin_memory=True) for _ in range(layers)]
        hosts = [torch.empty((count, PAGE), dtype=torch.uint8, pin_memory=True) for _ in range(layers)]
        full = torch.empty((pool, PAGE), dtype=torch.uint8, pin_memory=True)
        result['host_pin_allocate_ms'] = (time.perf_counter_ns()-started)/1e6
        row = torch.arange(count, dtype=torch.int64) * (1 << 32)
        column = torch.arange(PAGE//8, dtype=torch.int64)
        for layer, target in enumerate(expected): target.view(torch.int64).copy_(row[:, None] + column[None, :] + ((layer+1) << 16))
        begin, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        begin.record(stream); end.record(stream); end.synchronize()
        def transfer(mode, direction, timed, repetition):
            source_ids, destination_ids = ids[mode]
            chosen_ids = source_ids if direction == 'D2H' else destination_ids
            cpu0 = cpu_state()
            transaction_started = time.perf_counter_ns()
            t = time.perf_counter_ns()
            if mode == 'staged': plan = stage.make_plan(chosen_ids, pool)
            else: plan = runtime.make_plan(source_ids, pool) if direction == 'D2H' else restore.make_restore_plan(destination_ids, pool, save_runtime=runtime)
            plan_ms = (time.perf_counter_ns()-t)/1e6
            t = time.perf_counter_ns()
            if mode == 'staged': prepared = stage.prepare(raw, hosts, plan, copy_runtime=runtime)
            else: prepared = runtime.prepare_save(raw, hosts, plan, max_pitch=pitch) if direction == 'D2H' else restore.prepare_restore(hosts, raw, plan, max_pitch=pitch)
            prepare_ms = (time.perf_counter_ns()-t)/1e6
            allocated = torch.cuda.memory_allocated()
            try:
                t = time.perf_counter_ns(); torch.cuda.synchronize(); fence_ms = (time.perf_counter_ns()-t)/1e6
                start = time.perf_counter_ns(); begin.record(stream)
                t = time.perf_counter_ns()
                if mode == 'staged': info = bridge.submit(prepared, direction=direction, stream_handle=int(stream.cuda_stream))
                else: info = (sb if direction == 'D2H' else rb).submit(prepared, stream_handle=int(stream.cuda_stream))
                submitted_ms = (time.perf_counter_ns()-t)/1e6
                end.record(stream)
                t = time.perf_counter_ns(); end.synchronize(); wait_ms = (time.perf_counter_ns()-t)/1e6
                copy_ms = (time.perf_counter_ns()-start)/1e6
                event_ms = begin.elapsed_time(end)
                require(info['submitted_bytes'] == layers*layer_payload and info['completion_ack'] is False, '提交字节/ACK不符')
            except BaseException:
                result['submission_error'] = traceback.format_exc()
                # prepared仍在本作用域强持raw/host/两个IDs/scratch/描述符。
                # 不允许在外层finally之前释放未知是否完成的临时GPU内存。
                try:
                    torch.cuda.synchronize()
                    result['failed_submission_settled'] = True
                except BaseException:
                    result['failed_submission_settled'] = False
                    result['settle_error'] = traceback.format_exc()
                    save(run/'results.json',result)
                    os._exit(2)  # context由进程退出清理，禁止执行GC/返回ACK/重试。
                save(run/'results.json',result)
                raise
            t = time.perf_counter_ns(); del prepared, plan
            release_ms = (time.perf_counter_ns()-t)/1e6
            total_ms = (time.perf_counter_ns()-transaction_started)/1e6
            sample = dict(mode=mode, direction=direction, timed=timed, repetition=repetition,
                          plan_cpu_ms=plan_ms, prepare_cpu_ms=prepare_ms, producer_fence_wall_ms=fence_ms,
                          submit_wall_ms=submitted_ms, wait_wall_ms=wait_ms, copy_window_wall_ms=copy_ms,
                          cuda_event_ms=event_ms, release_wall_ms=release_ms,
                          total_transaction_wall_ms=total_ms,
                          device_allocated_after_prepare=allocated, info=info,
                          cpu_before=cpu0, cpu_after=cpu_state())
            result['samples'].append(sample)
            save(run/'results.json', result)
            return sample

        # 一次/几何全字节门兼作预热；初始化和oracle都在计时窗口外。
        for mode in ('fragmented', 'staged'):
            src, dst = ids[mode]
            require(min(src+dst)>0 and max(src+dst)<pool-1, '两端guard页被实际页序占用')
            src_cpu, dst_cpu = torch.tensor(src), torch.tensor(dst)
            for gpu, golden in zip(raw, expected):
                full.fill_(165); full[0].fill_(90); full[-1].fill_(90)
                full.index_copy_(0, src_cpu, golden)
                gpu.copy_(full, non_blocking=True); end.record(stream); end.synchronize()
            transfer(mode, 'D2H', False, -1)
            require(all(torch.equal(h, e) for h,e in zip(hosts,expected)), 'SAVE全字节错误')
            for gpu, golden in zip(raw, expected):
                full.copy_(gpu, non_blocking=True); end.record(stream); end.synchronize()
                require(torch.equal(full.index_select(0,src_cpu), golden), 'SAVE后原源页改变')
                require(bool((full[0] == 90).all()) and bool((full[-1] == 90).all()), 'SAVE改写guard')
                full.index_fill_(0, src_cpu, 165); full[0].fill_(165); full[-1].fill_(165)
                require(bool((full == 165).all()), 'SAVE改写非源页')
            for gpu in raw: gpu.fill_(165); gpu[0].fill_(90); gpu[-1].fill_(90)
            torch.cuda.synchronize()
            transfer(mode, 'H2D', False, -1)
            dst_gpu = dst_cpu.to('cuda')
            for gpu, golden in zip(raw, expected):
                # 原normal BF16层视图消费已完成的恢复页；不是Attention/模型精度门。
                view = gpu.view(torch.bfloat16).reshape(pool, 2, 16, 2, 128)
                consumer = view.index_select(0, dst_gpu).view(torch.uint8).reshape(count, PAGE)
                require(torch.equal(consumer.cpu(), golden), '事件后层视图消费者错误')
                full.copy_(gpu, non_blocking=True); end.record(stream); end.synchronize()
                require(torch.equal(full.index_select(0,dst_cpu), golden), 'FULL目的页全字节错误')
                require(bool((full[0] == 90).all()) and bool((full[-1] == 90).all()), 'guard被改写')
                full.index_fill_(0, dst_cpu, 165); full[0].fill_(165); full[-1].fill_(165)
                require(bool((full == 165).all()), '非目的页被改写')
            result['correctness'][mode] = dict(saved_all_bytes=True, save_raw_unchanged=True, restored_all_bytes=True,
                guard_pages_untouched=True, unselected_pages_still_poison=True, event_ordered_layer_consumer=True)
            save(run/'results.json', result)
        del full, consumer, view, dst_gpu
        gc.collect()
        # 固定三轮交替，AB/BA/AB；不因结果增加重复，不含初始化或oracle。
        for repetition in range(3):
            for mode in (('fragmented','staged') if repetition%2==0 else ('staged','fragmented')):
                for direction in ('D2H','H2D'): transfer(mode, direction, True, repetition)
        result['medians'] = {}
        for mode in ids:
            result['medians'][mode] = {}
            for direction in ('D2H','H2D'):
                rows = [s for s in result['samples'] if s['timed'] and s['mode']==mode and s['direction']==direction]
                result['medians'][mode][direction] = {key:statistics.median(r[key] for r in rows) for key in
                    ('plan_cpu_ms','prepare_cpu_ms','producer_fence_wall_ms','submit_wall_ms','wait_wall_ms','copy_window_wall_ms','cuda_event_ms','release_wall_ms','total_transaction_wall_ms')}
        result['paired_primitive_net_saving_ms'] = [sum(
            (1 if s['mode']=='fragmented' else -1) * s['total_transaction_wall_ms']
            for s in result['samples'] if s['timed'] and s['repetition']==r) for r in range(3)]
        result['primitive_all_three_pairs_faster'] = all(x > 0 for x in result['paired_primitive_net_saving_ms'])
        result['model_net_gain_confirmed'] = False
        result.update(completed=True, memory_after=dict(host=host_memory(), device_free=torch.cuda.mem_get_info()[0],
                      peak_allocated=torch.cuda.max_memory_allocated()), cpu_after=cpu_state())
    except BaseException:
        result['error'] = traceback.format_exc()
        traceback.print_exc()
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try: torch.cuda.synchronize()
            except BaseException: result.update(completed=False, cleanup_error=traceback.format_exc())
        result.update(finished_utc=now(), source_sha256=check_assets())
        save(run/'results.json', result)
    return 0 if result['completed'] else 1

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
        deadline=time.monotonic()+120
        with (run/'gpu.csv').open('x') as output:
            fields='timestamp,memory.used,memory.total,utilization.gpu'
            output.write(fields+'\n'); output.flush()
            while process.poll() is None:
                require(time.monotonic()<deadline,'诊断超过120秒，停止，不自动重试')
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
