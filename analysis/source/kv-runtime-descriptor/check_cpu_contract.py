"""单次最小CPU包装/观察合同；不模拟GPU，绝不导入torch/vLLM。"""
import ast
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parents[3]
RUNTIME = ROOT / "patches/framework/biv150_kv_runtime_descriptor.py"
BUILDER = ROOT / "scripts/remote/prepare_kv_runtime_descriptor_source.py"
BASE = ROOT / "experiments/official/20261021T092944Z-sql-mixed-official/source/plugin"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


observer = load("descriptor_cpu_owner", RUNTIME)
assert observer.install() is False
assert "torch" not in sys.modules and not any(name.startswith("vllm") for name in sys.modules)
for path in (RUNTIME, BUILDER):
    compile(path.read_bytes(), str(path), "exec")
original_init = (BASE / "vllm_fl/__init__.py").read_bytes()
changed = observer.transform_init(original_init)
assert changed == original_init + observer.INIT_FOOTER
assert hashlib.sha256(changed).hexdigest() == "90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74"
try:
    observer.transform_init(changed)
    raise AssertionError("double-transform accepted")
except RuntimeError:
    pass


class Storage:
    def data_ptr(self):
        return 123456

    def nbytes(self):
        return 42 * 8192 * 2


class Tensor:
    dtype, device, shape = "torch.bfloat16", "cuda:0", (1, 2, 16, 2, 128)

    def __init__(self, layer):
        self.layer = layer

    def stride(self):
        return (344064, 4096, 256, 128, 1)

    def storage_offset(self):
        return self.layer * 8192

    def element_size(self):
        return 2

    def untyped_storage(self):
        return Storage()


sys.modules["torch"] = NS(Tensor=Tensor)
config = NS(model_config=NS(model="/workspace/MiniCPM5-2B", dtype="torch.bfloat16", quantization=None,
                          hf_text_config=NS(hidden_size=2048, num_hidden_layers=42,
                                            num_attention_heads=16, num_key_value_heads=2)),
            parallel_config=NS(tensor_parallel_size=1, pipeline_parallel_size=1,
                               decode_context_parallel_size=1, data_parallel_size=1, use_ubatching=False),
            speculative_config=None, lora_config=None, kv_transfer_config=None, ec_transfer_config=None)


class Runner:
    pass


class Worker:
    pass


class Engine:
    pass


runner = Runner()
runner.kv_caches = [Tensor(i) for i in range(42)]
names = ["model.layers." + str(i) + ".self_attn.attn" for i in range(42)]
runner.compilation_config = NS(static_forward_context={
    name: NS(kv_cache=[tensor]) for name, tensor in zip(names, runner.kv_caches)})
runner.kv_cache_config = NS(num_blocks=1, kv_cache_groups=[NS(layer_names=names,
    kv_cache_spec=NS(block_size=16, dtype="torch.bfloat16", num_kv_heads=2, head_size=128))])
runner._kernel_block_sizes = [16]
runner.shared_kv_cache_layers = {}
runner.cross_layers_kv_cache = None
worker = Worker()
worker.vllm_config, worker.model_runner = config, runner
payload = observer._worker(worker, Runner)
assert payload["status"] == "observed_complete" and payload["layer_count"] == 42
assert payload["storage_alias_group_count"] == 1 and payload["cross_layers_kv_cache"] == {"status": "observed_none"}
assert payload["runner_kv_cache_list"][-1]["storage_offset_elements"] == 41 * 8192
del runner.cross_layers_kv_cache
assert observer._worker(worker, Runner)["cross_layers_kv_cache"] == {"status": "unobserved_missing_attribute"}
runner.cross_layers_kv_cache = None

# Execute the exact actual WorkerFL method with fake dependencies; original
# ensure/init ordering remains intact and observation is only after return.
source = (BASE / "vllm_fl/worker/worker.py").read_text(encoding="utf-8")
cls = next(node for node in ast.parse(source).body if isinstance(node, ast.ClassDef) and node.name == "WorkerFL")
method = next(node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name == "initialize_from_config")
trace = []
namespace = {"KVCacheConfig": object, "ensure_kv_transfer_initialized": lambda *args: trace.append("ensure")}
exec(compile(ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[])), "actual-worker-method", "exec"), namespace)
runner.initialize_kv_cache = lambda cfg: trace.append("initialize")
emitted = []
saved_write = observer._write
observer._write = lambda row: (trace.append("observe"), emitted.append(row))
wrapped = observer._wrap_worker(namespace["initialize_from_config"], Runner)
assert wrapped(worker, runner.kv_cache_config) is None
assert trace == ["ensure", "initialize", "observe"]
wrapped(worker, runner.kv_cache_config)
assert trace[-2:] == ["ensure", "initialize"] and len(emitted) == 1
engine = Engine()
engine.vllm_config, engine.model_executor = config, NS(driver_worker=NS(worker=worker))
engine.scheduler, engine.batch_queue_size, engine.async_scheduling = NS(), 2, True
core_value = object()
assert observer._wrap_core(lambda self: core_value)(engine) is core_value
assert observer._wrap_core(lambda self: core_value)(engine) is core_value
assert len(emitted) == 2 and emitted[-1]["direct_worker"]["object_id_in_this_pid"] == id(worker)

# Read failure cannot replace original return; original exception propagates
# before any post-success observation. No tensor operations are available.
bad = Worker()
bad.vllm_config, bad.model_runner = config, Runner()
assert observer._wrap_worker(lambda self: core_value, Runner)(bad) is core_value
assert emitted[-1]["status"] == "observation_error"
exception = ValueError("original")
try:
    observer._wrap_worker(lambda self: (_ for _ in ()).throw(exception), Runner)(worker)
    raise AssertionError("original exception swallowed")
except ValueError as caught:
    assert caught is exception
observer._write = saved_write
del sys.modules["torch"]

sys.path.insert(0, str(ROOT / "scripts/remote"))
builder = load("descriptor_builder_cpu_owner", BUILDER)
scratch = ROOT / "tmp/patch-check" / ("kv-runtime-descriptor-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
base, assets, output = scratch / "code" / builder.owner.BASE_NAME, scratch / "scripts", scratch / "code/descriptor-test"
assets.mkdir(parents=True)
shutil.copytree(BASE, base, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
shutil.copy2(RUNTIME, assets / RUNTIME.name)
before = builder.owner.source_files(base)
manifest = builder.prepare(base, output, assets, root=scratch)
assert builder.owner.source_files(base) == before
assert set(manifest["changes"]) == {"vllm_fl/__init__.py", "vllm_fl/patches/" + RUNTIME.name}
assert (output / "vllm_fl/worker/model_runner.py").read_bytes() == (base / "vllm_fl/worker/model_runner.py").read_bytes()
try:
    builder.prepare(base, output, assets, root=scratch)
    raise AssertionError("existing output accepted")
except FileExistsError:
    pass
assert "torch" not in sys.modules and not any(name.startswith("vllm") for name in sys.modules)
report = {"status": "cpu_contract_passed", "actual_worker_method_ast_used": True,
          "original_order_return_exception_preserved": True, "once_and_diagnostic_failure_preserved": True,
          "fake_packed_42_alias_descriptor_passed": True, "double_init_transform_rejected": True,
          "full_copy_verified": True, "base_unchanged": True,
          "input_file_count": len(before), "output_count_including_manifest": len(builder.owner.source_files(output)),
          "scratch": str(scratch), "candidate_sha256": hashlib.sha256(RUNTIME.read_bytes()).hexdigest(),
          "builder_sha256": hashlib.sha256(BUILDER.read_bytes()).hexdigest(),
          "limits": "Fake CPU descriptors prove no tensor math; not actual storage API/device layout/installation/EngineCore success."}
Path(__file__).with_name("cpu-contract.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, ensure_ascii=True, indent=2))
