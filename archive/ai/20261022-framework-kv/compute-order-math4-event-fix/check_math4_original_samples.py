"""仅在 CPU 重建原 benchmark 采样，核清内部长度；无 HTTP、模型或 GPU 调用。"""
import hashlib
import importlib
import json
from pathlib import Path

pins = {
    'vllm.benchmarks.datasets.datasets': '4aebfc9a1a13b01599a1de8a880e08ff2bae7f6403d430a585908508cc5811b4',
    'vllm.benchmarks.datasets.utils': '14efee4c78ea60b38e1be458c192ff1972c3295dbebe91bacff414ebcf89c3b6',
}
for name, expected in pins.items():
    module = importlib.import_module(name)
    assert hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() == expected
from vllm.benchmarks.datasets.datasets import RandomDataset
from vllm.tokenizers import get_tokenizer

tokenizer = get_tokenizer('/workspace/MiniCPM5-2B', tokenizer_mode='auto', trust_remote_code=False)
dataset = RandomDataset(random_seed=721201, dataset_path=None, disable_shuffle=False)
samples = dataset.sample(tokenizer=tokenizer, num_requests=32, prefix_len=0,
    input_len=16384, output_len=128, range_ratio=0.0, request_id_prefix='bench-5ab5f499-',
    batchsize=1, no_oversample=False)
result = dict(kind='CPU 原采样字段核对；不发送请求，不改变正式 payload',
    source_sha256=pins, seed=721201, requested_input_len=16384,
    num_special_tokens_to_add=int(tokenizer.num_special_tokens_to_add()),
    rows=[dict(index=i, prompt_len=s.prompt_len, expected_output_len=s.expected_output_len,
        multi_modal_is_none=s.multi_modal_data is None, request_id=s.request_id,
        prompt_sha256=hashlib.sha256(s.prompt.encode()).hexdigest()) for i,s in enumerate(samples)])
assert len(samples) == 32 and len({s.request_id for s in samples}) == 32
assert all(s.expected_output_len == 128 and s.multi_modal_data is None for s in samples)
print('MATH4_ORIGINAL_SAMPLES ' + json.dumps(result, ensure_ascii=False))
