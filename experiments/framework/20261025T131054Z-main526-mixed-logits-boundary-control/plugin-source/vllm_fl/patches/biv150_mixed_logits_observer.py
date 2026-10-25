"""当前main526短窗native诊断；独立模块保持runner/P/Q/native原字节。"""
from collections import deque
from functools import wraps
import hashlib, inspect, json, os, sys
from pathlib import Path
EXPECTED = {'vllm.v1.engine.core': '27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71', 'vllm.v1.executor.uniproc_executor': '4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe', 'vllm.v1.worker.worker_base': '7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe', 'vllm.v1.core.sched.scheduler': 'df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090', 'vllm.v1.core.sched.async_scheduler': 'da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884', 'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320', 'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b', 'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914', 'vllm.v1.kv_cache_interface': '7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003', 'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80', 'vllm.v1.core.sched.output': 'f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d', 'vllm_fl.worker.worker': 'a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24', 'vllm_fl.worker.model_runner': '677def25d5391887145b0bbabb2222531887c6f7c48b6ea53c1859ad08d8ef61', 'vllm_fl.patches.biv150_compute_order': 'fb8509c5fe7e92960b95c4891a42aa72a236fc98ef54724296fe2779e293f44a', 'vllm_fl.patches.biv150_prefill_normalized': '24a421fa25e0ce7e21b54deb760a5bc893d3899a86ced4849bd3f3bfab50ed42', 'vllm_fl.patches.biv150_q_fragment_service': '3f90de854adeb7d3584b19bad1f317cb527f16f14bec15d40f55ffa3e13b4d8a', 'vllm_fl.patches.biv150_native_w8a8': '78a9af84ef73c295e85698bed215c60c7547a584f32635c31186dace5e0ac708', 'vllm_fl.patches.biv150_gqa_decode': '2596cc09caf9b5b38b49755ae9af41ebdcf59a1d5ad889fc8e9319d1584438d1', 'vllm_fl.dispatch.io_common': '6d8b4adf9ad75a5b79569e4ccc132c1ee69fd525198b3c4e25e2d6de6f3fff55'}

def check_pr24_native(modules):
    # 只核自然加载模块、Python绑定和构建凭据；不访问tensor/device/Future。
    native = modules['vllm_fl.patches.biv150_native_w8a8']
    q_module = modules['vllm_fl.patches.biv150_q_fragment_service']
    torch = sys.modules.get('torch')
    linear = sys.modules.get('vllm.model_executor.layers.linear')
    llama = sys.modules.get('vllm.model_executor.models.llama')
    if torch is None or linear is None or llama is None or native._LOADED is not True:
        raise ValueError('CURRENT native尚未自然加载')
    if native._STATE.get('quantized_layers') != 34:
        raise ValueError('CURRENT native未完成34层权重接入')
    for function, name in (
        (linear.UnquantizedLinearMethod.process_weights_after_loading, 'after'),
        (linear.UnquantizedLinearMethod.apply, 'apply'),
        (llama.LlamaMLP.forward, 'forward'),
    ):
        if (not inspect.isfunction(function) or function.__globals__ is not vars(native)
                or function.__qualname__ != 'install.<locals>.' + name
                or Path(function.__code__.co_filename).resolve() != Path(native.__file__).resolve()):
            raise ValueError('CURRENT native实际方法绑定变化: ' + name)
    manager = q_module._MANAGER
    if (manager is None or manager.active is not True
            or manager.holder[manager.kernel_key] is not manager.wrapper):
        raise ValueError('CURRENT Q实际kernel绑定变化')
    receipt_path = Path(os.environ['BIV150_RESUME_NATIVE_RECEIPT'])
    raw = receipt_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != os.environ['BIV150_RESUME_NATIVE_RECEIPT_SHA256']:
        raise ValueError('native构建凭据变化')
    receipt = json.loads(raw)
    library = Path(os.environ['BIV150_NATIVE_W8A8_LIBRARY']).resolve(strict=True)
    if (library != Path(receipt['runtime_library']).resolve(strict=True)
            or hashlib.sha256(library.read_bytes()).hexdigest() != receipt['library_sha256']
            or str(library) not in {str(Path(p).resolve()) for p in torch.ops.loaded_libraries}
            or str(torch.__version__) != receipt['abi']['torch_version']
            or bool(torch._C._GLIBCXX_USE_CXX11_ABI) is not receipt['abi']['cxx11_abi']):
        raise ValueError('CURRENT实际native库/ABI不符')
    emit('CURRENT_NATIVE_SCOPE', quantized_layers=34, library_sha256=receipt['library_sha256'],
         torch_version=str(torch.__version__), cxx11_abi=bool(torch._C._GLIBCXX_USE_CXX11_ABI),
         source_tree=receipt['source_tree'], native_methods_identity=True,
         q_kernel_binding_identity=True)



def emit(event, **fields):
    print('BIV150_MIXED_LOGITS ' + json.dumps(dict(event=event, pid=os.getpid(), **fields)), flush=True)


def check_runner_bindings(runner, modules):
    cls = type(runner)
    module = modules[cls.__module__]
    io = modules['vllm_fl.dispatch.io_common']
    for name in ('execute_model', 'shutdown'):
        method = getattr(cls, name)
        bound = getattr(runner, name)
        if (name in vars(runner) or not inspect.isfunction(method)
                or getattr(bound, '__self__', None) is not runner
                or getattr(bound, '__func__', None) is not method):
            raise ValueError('非固定runner实例绑定: ' + name)
        if name == 'execute_model':
            cells = dict(zip(method.__code__.co_freevars, method.__closure__ or ()))
            raw = getattr(method, '__wrapped__', None)
            if (method.__globals__ is not vars(io)
                    or Path(method.__code__.co_filename).resolve() != Path(io.__file__).resolve()
                    or method.__code__.co_qualname != 'managed_inference_mode.<locals>.decorator.<locals>.wrapper'
                    or set(cells) != {'fn'} or cells['fn'].cell_contents is not raw
                    or not inspect.isfunction(raw) or hasattr(raw, '__wrapped__')
                    or raw.__globals__ is not vars(module)
                    or raw.__code__.co_qualname != 'ModelRunnerFL.execute_model'
                    or Path(raw.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
                raise ValueError('execute_model不是固定managed_inference_mode单层链')
        elif (inspect.unwrap(method) is not method or method.__globals__ is not vars(module)
                or method.__code__.co_qualname != 'ModelRunnerFL.shutdown'
                or Path(method.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise ValueError('shutdown不是固定原函数')


def install(*, enabled=False):
    if enabled is not True:
        return None
    module = sys.modules.get('vllm.v1.engine.core')
    if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED[module.__name__]:
        raise ValueError('原Core尚未自然加载')
    core, original = module.EngineCore, module.EngineCore.step_with_batch_queue
    if inspect.unwrap(original) is not original or Path(original.__code__.co_filename).resolve() != Path(module.__file__).resolve():
        raise ValueError('Core已有wrapper')
    attempted, owners, handles = False, [], []

    def retire(engine):
        bound = vars(engine).get('step_fn')
        if getattr(bound, '__self__', None) is engine and getattr(bound, '__func__', None) is step:
            engine.step_fn = original.__get__(engine, type(engine))
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    @wraps(original)
    def step(engine, *args, **kwargs):
        nonlocal attempted
        if not attempted:
            attempted = True
            owners.append(engine)
            try:
                modules = {}
                for name, pin in EXPECTED.items():
                    item = sys.modules.get(name)
                    if item is None or hashlib.sha256(Path(item.__file__).read_bytes()).hexdigest() != pin:
                        raise ValueError('自然加载源不符: ' + name)
                    modules[name] = item
                check_pr24_native(modules)
                executor = engine.model_executor
                wrapper = vars(executor).get('driver_worker')
                worker = None if wrapper is None else vars(wrapper).get('worker')
                runner = None if worker is None else vars(worker).get('model_runner')
                if not (type(engine) is module.EngineCoreProc
                    and type(executor) is modules['vllm.v1.executor.uniproc_executor'].UniProcExecutor
                    and type(wrapper) is modules['vllm.v1.worker.worker_base'].WorkerWrapperBase
                    and type(worker) is modules['vllm_fl.worker.worker'].WorkerFL
                    and type(runner) is modules['vllm_fl.worker.model_runner'].ModelRunnerFL
                    and type(engine.batch_queue) is deque and engine.batch_queue_size == 2):
                    raise ValueError('非当前UniProc/WorkerFL/队列2')
                check_runner_bindings(runner, modules)
                handles.append(install_runner(runner))
            except Exception as error:
                emit('SCOPE_REJECTED', error_type=type(error).__name__)
                raise
            finally:
                retire(engine)
        return original(engine, *args, **kwargs)

    def restore():
        for handle in handles:
            handle()
        for engine in owners:
            retire(engine)
        if core.step_with_batch_queue is step:
            core.step_with_batch_queue = original

    core.step_with_batch_queue = step
    return {'restore': restore}


def install_runner(runner):
    """图外前8步快照；请求运行中不作D2H、tensor.item或同步。"""
    from types import MethodType
    torch = sys.modules['torch']
    context_module = sys.modules['vllm.forward_context']
    sampler_module = sys.modules['vllm.v1.sample.sampler']
    if type(runner.sampler) is not sampler_module.Sampler:
        raise ValueError('采样器不是原vLLM Sampler')
    names = ('execute_model', '_prepare_inputs', '_model_forward', '_sample', 'shutdown')
    if any(name in vars(runner) for name in names) or 'greedy_sample' in vars(runner.sampler):
        raise ValueError('不叠加既有实例wrapper')
    original = {name: getattr(runner, name) for name in names}
    greedy_original = runner.sampler.greedy_sample
    if greedy_original.__module__ != sampler_module.__name__:
        raise ValueError('greedy_sample绑定不符')
    folder = Path(os.environ['BIV150_MIXED_LOGITS_DIR'])
    folder.mkdir(exist_ok=False)
    # 15.94MiB logits + 64KiB hidden + 256B indices/IDs。模型图已capture。
    device = runner.device
    buffers = {
        'raw': torch.empty((8,2,130560), dtype=torch.float32, device=device),
        'greedy': torch.empty((8,2,130560), dtype=torch.float32, device=device),
        'hidden': torch.empty((8,2,2048), dtype=torch.bfloat16, device=device),
        'indices': torch.empty((8,2), dtype=torch.int64, device=device),
        'ids': torch.empty((8,2), dtype=torch.int64, device=device),
    }
    state = dict(rows=[], current=None, target=None, flushed=False, errors=[],
        allocated_bytes=sum(t.numel()*t.element_size() for t in buffers.values()),
        sampler_source=str(Path(sampler_module.__file__).resolve()),
        sampler_sha256=hashlib.sha256(Path(sampler_module.__file__).read_bytes()).hexdigest(),
        runtime_difference='main526 + plugin注册接线/图外快照，模型图/数学/采样不变；额外内存和copy可扰动复现',
        limitations=['只捕获前8个涉及长题的模型步','未复现不能撤销旧失败','未保存各层中间值，不能确定责任内核'])
    if state['allocated_bytes'] > 17*1024*1024:
        raise ValueError('快照内存超出约16MiB预算')
    bindings = {}

    def copy(name, tensor):
        row = state['current']
        if row is None: return
        n = len(row['req_ids'])
        expected = (n,130560) if name in ('raw','greedy') else (n,2048) if name=='hidden' else (n,)
        if tuple(tensor.shape) != expected or tensor.device != device:
            raise ValueError('快照shape/device不符: '+name+str(tuple(tensor.shape)))
        buffers[name][row['index'], :n].copy_(tensor, non_blocking=True)
        row['copied'].append(name)
        row.setdefault('copy_streams',{})[name] = int(torch.cuda.current_stream().cuda_stream)

    def flush(reason):
        if state['flushed']: return
        state['flushed'] = True
        state['flush_reason'] = reason
        state['current'] = None
        summary=folder.parent/'diagnostic-summary.json'
        state['requests_completed_at_flush']=summary.is_file() and json.loads(summary.read_text()).get('completed',False)
        # 仅owner发起原关闭流程后执行；从来不在推理步内等待GPU。
        torch.cuda.synchronize(device)
        state['shutdown_sync_completed']=True
        tensors = {}
        for row in state['rows']:
            for name in row['copied']:
                tensors[str(row['index'])+'/'+name] = buffers[name][row['index'], :len(row['req_ids'])].cpu()
        torch.save(tensors, folder/'tensors.pt')
        (folder/'metadata.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        emit('LOGITS_FLUSHED', rows=len(state['rows']), folder=str(folder))

    @wraps(original['execute_model'])
    def execute(self, output, *args, **kwargs):
        state['current'] = None
        for request in output.scheduled_new_reqs:
            if request.prompt_token_ids is not None and len(request.prompt_token_ids)>=4096:
                if state['target'] not in (None, request.req_id):
                    raise ValueError('不接受第二个长题')
                state['target'] = request.req_id
        if state['target'] in output.num_scheduled_tokens and len(state['rows'])<8:
            row = dict(index=len(state['rows']), target_req_id=state['target'],
                scheduled=dict(output.num_scheduled_tokens), M=output.total_num_scheduled_tokens,
                copied=[], req_ids=[])
            state['rows'].append(row); state['current'] = row
        result = original['execute_model'](output,*args,**kwargs)
        if state['current'] is not None:
            model_state = self.execute_model_state
            if model_state is None or model_state.spec_decode_metadata is not None:
                raise ValueError('无原模型输出/意外spec_decode')
            copy('hidden', model_state.sample_hidden_states)
            copy('raw', model_state.logits)
        return result

    @wraps(original['_prepare_inputs'])
    def prepare(self, *args, **kwargs):
        result = original['_prepare_inputs'](*args,**kwargs)
        row = state['current']
        if row is not None:
            n = self.input_batch.num_reqs
            if not 1<=n<=2: raise ValueError('原双请求之外的并发')
            row.update(req_ids=list(self.input_batch.req_ids[:n]),
                discard=self.discard_request_mask.np[:n].tolist(),
                num_prompt_tokens=self.input_batch.num_prompt_tokens[:n].tolist(),
                num_computed_tokens=self.input_batch.num_computed_tokens_cpu[:n].tolist())
            copy('indices', result[0])
        return result

    @wraps(original['_model_forward'])
    def forward(self,*args,**kwargs):
        row = state['current']
        if row is not None:
            context = context_module.get_forward_context()
            row['runtime_mode'] = context.cudagraph_runtime_mode.name
            d = context.batch_descriptor
            row['descriptor'] = None if d is None else dict(num_tokens=d.num_tokens,num_reqs=d.num_reqs)
            row['stream'] = int(torch.cuda.current_stream().cuda_stream)
        return original['_model_forward'](*args,**kwargs)

    def greedy(logits):
        if state['current'] is not None: copy('greedy', logits)
        return greedy_original(logits)

    @wraps(original['_sample'])
    def sample(self, logits, spec_decode_metadata):
        row = state['current']
        if row is not None:
            md = self.input_batch.sampling_metadata
            holder = md.thinking_budget_state_holder
            row['sampling'] = dict(all_greedy=bool(md.all_greedy), all_random=bool(md.all_random),
                no_penalties=bool(md.no_penalties), bad_words=bool(md.bad_words_token_ids),
                allowed_mask=md.allowed_token_ids_mask is not None,
                processors=[type(p).__module__+'.'+type(p).__name__ for p in md.logitsprocs.non_argmax_invariant],
                thinking_tracked=holder is not None and holder.has_tracked_requests())
            if not md.all_greedy or spec_decode_metadata is not None:
                raise ValueError('本诊断只接受原双请求greedy路径')
        result = original['_sample'](logits,spec_decode_metadata)
        if row is not None:
            copy('ids', result.sampled_token_ids.reshape(-1))
            row['sample_returned'] = True
            state['current'] = None
        return result

    @wraps(original['shutdown'])
    def shutdown(self,*args,**kwargs):
        try: flush('original_runner_shutdown')
        finally: result = original['shutdown'](*args,**kwargs)
        return result

    def restore():
        for name,binding in bindings.items():
            if vars(runner).get(name) is binding: delattr(runner,name)
        if vars(runner.sampler).get('greedy_sample') is greedy:
            delattr(runner.sampler,'greedy_sample')
    for name,function in (('execute_model',execute),('_prepare_inputs',prepare),('_model_forward',forward),('_sample',sample),('shutdown',shutdown)):
        binding=MethodType(function,runner);setattr(runner,name,binding);bindings[name]=binding
    runner.sampler.greedy_sample=greedy
    (folder/'installed.json').write_text(json.dumps({k:v for k,v in state.items() if k!='current'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    emit('LOGITS_INSTALLED',allocated_bytes=state['allocated_bytes'],folder=str(folder))
    return restore
