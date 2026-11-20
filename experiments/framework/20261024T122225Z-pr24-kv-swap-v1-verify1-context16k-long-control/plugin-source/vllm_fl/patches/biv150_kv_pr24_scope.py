"""只核当前PR24来源/配置/方法/SO绑定；不声明逐请求native设备执行。"""
import hashlib, inspect, json, os, sys
from pathlib import Path
EXPECTED = {'vllm.v1.engine.core': '27b23827a86fd488f1f7cc9a2722fe76d284087ca7cfefef5a30c5e74f21bc71', 'vllm.v1.executor.uniproc_executor': '4625c8e59aef1482600b02204701d348d7f716427581d3cf23b06bff9b056abe', 'vllm.v1.worker.worker_base': '7da44338c2645ebf03d23394e452b31a8e3da1011fd1b42fcfcccfe99551b3fe', 'vllm.v1.core.sched.scheduler': 'df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090', 'vllm.v1.core.sched.async_scheduler': 'da6343d7e7c394a1738cf72905cbecc208003ffa461ccb441268333a3eb9f884', 'vllm.v1.core.kv_cache_manager': '2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320', 'vllm.v1.core.kv_cache_coordinator': '9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b', 'vllm.v1.core.single_type_kv_cache_manager': '22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914', 'vllm.v1.kv_cache_interface': '7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003', 'vllm.v1.request': '06b1c6ad3cc0223c2036b4a2e317868fa4988391b4b024bc5e5f54672b7d2c80', 'vllm.v1.core.sched.output': 'f2816589726053556dc6eef90e09b901c51f1e08ba41c9b79106d9f4acb89f6d', 'vllm_fl.worker.worker': 'a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24', 'vllm_fl.worker.model_runner': '677def25d5391887145b0bbabb2222531887c6f7c48b6ea53c1859ad08d8ef61', 'vllm_fl.patches.biv150_compute_order': 'a467c937dc6b4932944e70671259dcf87b05b51a61dd894dccbb97754fefbf0c', 'vllm_fl.patches.biv150_prefill_normalized': '24a421fa25e0ce7e21b54deb760a5bc893d3899a86ced4849bd3f3bfab50ed42', 'vllm_fl.patches.biv150_q_fragment_service': 'ea361e6b604fbd3c7e3a6b95776892a7bc9d22e9988927db3f7876412c6e310f', 'vllm_fl.patches.biv150_native_w8a8': '98ad16de1c25e914959c54d8f3352e6530b170d710d4abb7b41c334b4696f8a9', 'vllm_fl.patches.biv150_gqa_decode': '1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a'}

def emit(event, **fields):
    print("BIV150_KV_PR24_SCOPE " + json.dumps(dict(event=event, pid=os.getpid(), **fields)), flush=True)

def check_pr24_native(modules):
    # 只核自然加载模块、Python绑定和构建凭据；不访问tensor/device/Future。
    native = modules['vllm_fl.patches.biv150_native_w8a8']
    q_module = modules['vllm_fl.patches.biv150_q_fragment_service']
    torch = sys.modules.get('torch')
    linear = sys.modules.get('vllm.model_executor.layers.linear')
    llama = sys.modules.get('vllm.model_executor.models.llama')
    if torch is None or linear is None or llama is None or native._LOADED is not True:
        raise ValueError('PR24 native尚未自然加载')
    if native._STATE.get('quantized_layers') != 34:
        raise ValueError('PR24 native未完成34层权重接入')
    for function, name in (
        (linear.UnquantizedLinearMethod.process_weights_after_loading, 'after'),
        (linear.UnquantizedLinearMethod.apply, 'apply'),
        (llama.LlamaMLP.forward, 'forward'),
    ):
        if (not inspect.isfunction(function) or function.__globals__ is not vars(native)
                or function.__qualname__ != 'install.<locals>.' + name
                or Path(function.__code__.co_filename).resolve() != Path(native.__file__).resolve()):
            raise ValueError('PR24 native实际方法绑定变化: ' + name)
    manager = q_module._MANAGER
    if (manager is None or manager.active is not True
            or manager.holder[manager.kernel_key] is not manager.wrapper):
        raise ValueError('PR24 Q实际kernel绑定变化')
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
        raise ValueError('PR24实际native库/ABI不符')
    emit('PR24_NATIVE_SCOPE', quantized_layers=34, library_sha256=receipt['library_sha256'],
         torch_version=str(torch.__version__), cxx11_abi=bool(torch._C._GLIBCXX_USE_CXX11_ABI),
         source_tree=receipt['source_tree'], native_methods_identity=True,
         q_kernel_binding_identity=True)



def check(runner):
    modules = {}
    for name, pin in EXPECTED.items():
        module = sys.modules.get(name)
        if module is None or hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
            raise ValueError("当前PR24自然加载源不符: " + name)
        modules[name] = module
    if type(runner) is not modules["vllm_fl.worker.model_runner"].ModelRunnerFL:
        raise ValueError("非当前ModelRunnerFL")
    check_pr24_native(modules)
