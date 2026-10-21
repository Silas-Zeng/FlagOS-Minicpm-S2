"""Tiny CPU wrapper contract check; uses no torch, device, or remote process."""
from dataclasses import dataclass
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location(
    "bucket_contract_subject", ROOT / "patches/framework/biv150_mixed_token_bucket.py")
bucket = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = bucket
spec.loader.exec_module(bucket)


class Buffer:
    def __init__(self, values, start=0, stop=None):
        self.values, self.start = values, start
        self.stop = len(values) if stop is None else stop
        self.shape = (self.stop - self.start,)

    def __getitem__(self, sl):
        return Buffer(self.values, self.start + (sl.start or 0),
                      self.stop if sl.stop is None else self.start + sl.stop)

    def zero_(self):
        self.values[self.start:self.stop] = [0] * (self.stop - self.start)


@dataclass(frozen=True)
class Descriptor:
    num_tokens: int
    num_reqs: int
    uniform: bool = False


@dataclass
class Stats:
    num_unpadded_tokens: int
    num_padded_tokens: int
    num_paddings: int
    runtime_mode: str


module = NS(CUDAGraphMode=NS(NONE="NONE"), CUDAGraphStat=Stats)
bucket._eligible = lambda *args: True  # Only wrapper/descriptor contracts here.


class Runner:
    def __init__(self):
        self.max_num_tokens = 2048
        self.input_ids = NS(gpu=Buffer([17] * 2048))
        self.positions = Buffer([23] * 2048)
        self.mode, self.uniform = "NONE", False
        self.override = {}

    def _determine_batch_execution_and_padding(self, num_tokens, num_reqs,
                                             num_scheduled_tokens_np,
                                             max_num_scheduled_tokens,
                                             use_cascade_attn, **kwargs):
        return (self.mode, Descriptor(num_tokens, num_reqs, self.uniform),
                False, None, Stats(num_tokens, num_tokens, 0, self.mode))

    def _preprocess(self, scheduler, count, intermediate_tensors=None):
        self.positions[scheduler.total_num_scheduled_tokens:count].zero_()
        return self.input_ids.gpu[:count], None, self.positions[:count], None, {}, None

    def execute_model(self, scheduler, intermediate_tensors=None):
        result = self._determine_batch_execution_and_padding(
            scheduler.total_num_scheduled_tokens, 7, None, scheduler.max_query,
            False, **self.override)
        self._preprocess(scheduler, result[1].num_tokens)
        return result


bucket._wrap_runner(Runner, module, None, None)
checks = []
for actual, padded in ((259, 384), (952, 1024)):
    runner = Runner()
    scheduler = NS(total_num_scheduled_tokens=actual, max_query=actual,
                   scheduled_encoder_inputs={}, scheduled_spec_decode_tokens={})
    result = runner.execute_model(scheduler)
    assert result[1] == Descriptor(padded, 7, False)
    assert result[4] == Stats(actual, padded, padded - actual, "NONE")
    assert runner.input_ids.gpu.values[:actual] == [17] * actual
    assert runner.input_ids.gpu.values[actual:padded] == [0] * (padded - actual)
    assert runner.input_ids.gpu.values[padded:] == [17] * (2048 - padded)
    assert runner.positions.values[:actual] == [23] * actual
    assert runner.positions.values[actual:padded] == [0] * (padded - actual)
    assert bucket._EXECUTION.get() is None
    checks.append(f"{actual}->{padded}: descriptor/stat/ID-tail/positions/context")

for attribute, value in (("uniform", True), ("mode", "FULL"),
                         ("max_num_tokens", 300), ("override", {"force_eager": True})):
    runner = Runner()
    setattr(runner, attribute, value)
    scheduler = NS(total_num_scheduled_tokens=259, max_query=259,
                   scheduled_encoder_inputs={}, scheduled_spec_decode_tokens={})
    assert runner.execute_model(scheduler)[1].num_tokens == 259
    assert runner.input_ids.gpu.values == [17] * 2048
    checks.append(f"fallback: {attribute}")

runner = Runner()
assert runner._determine_batch_execution_and_padding(259, 7, None, 259, False)[1].num_tokens == 259
checks.append("out-of-execute/dummy determine unchanged")

# Verify actual frozen prefix + exact opt-in suffix, without importing vLLM.
source = (ROOT / "experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/"
          "plugin/vllm_fl/worker/model_runner.py").read_bytes()
footer = (ROOT / "patches/framework/mixed_token_bucket_footer.py").read_bytes()
fixture_name = "bucket_source_fixture"
runner_type = type("ModelRunnerFL", (), {"__module__": fixture_name})
with tempfile.TemporaryDirectory(dir=ROOT / "tmp") as temporary:
    runner_file = Path(temporary) / "runner.py"
    fixture = NS(__file__=str(runner_file), ModelRunnerFL=runner_type)
    sys.modules[fixture_name] = fixture
    for content in (source, source + footer):
        runner_file.write_bytes(content)
        assert bucket._require_runner_source(runner_type) is fixture
    for content in (source + footer + b"# extra\n", b"# changed\n" + source + footer):
        runner_file.write_bytes(content)
        try:
            bucket._require_runner_source(runner_type)
        except RuntimeError:
            pass
        else:
            raise AssertionError("mutated source/footer accepted")
    del sys.modules[fixture_name]
checks.append("actual frozen source and footer pass; either mutation rejected")
print("\n".join(checks))
print("CPU contracts PASS; no actual tensor/KV/RNG/accuracy/performance claim")
