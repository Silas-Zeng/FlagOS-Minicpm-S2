"""已清理后用原 reader 与设备本地 tokenizer 做 CPU 关联，不运行模型。"""
import hashlib
import json
import os
from pathlib import Path
import subprocess

control = Path(__file__).resolve().parent
run = control.with_name(control.name.removesuffix('-control'))
assert run.name == '20261023T130351Z-compute-order-math4-event'
assert (run / 'exit-code').read_text().strip() == '0'
post = json.loads((run / 'postflight-full.json').read_text())
assert post['query'].strip() == '68, 0' and all(post['ports_closed'].values())
assert not post['source_failures'] and not post['client_group_scan_errors']
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
reader = control / 'read_math4.py'
assert sha(reader) == '6b49cffb5672904f949f366d919a5c670a927b3ddf8be21994151c74e774fe05'
model = Path('/workspace/MiniCPM5-2B')
assert sha(model / 'config.json') == '59613157e5357d62bcb121e04cb90f2170b43d789b142380c12c3d4277d95180'
names = ['config.json','tokenizer_config.json','tokenizer.json','special_tokens_map.json',
         'added_tokens.json','vocab.json','merges.txt','tokenizer.model','generation_config.json']
identity = {name:dict(bytes=(model/name).stat().st_size, sha256=sha(model/name))
            for name in names if (model/name).is_file()}
with (control / 'tokenizer-identity.json').open('x') as f:
    json.dump(dict(model=str(model), files=identity,
        limitation='本轮实际目录身份；没有旧轮tokenizer哈希，不声称历史逐哈希一致'), f, ensure_ascii=False, indent=2)
reference = Path('/workspace/experiments/minicpm-s2/accuracy/20261023T061500Z-compute-order/math500-level3/20261023_141601/predictions/minicpm/math_500_Level 3.jsonl')
assert sha(reference) == 'fa96d12edf0b93ba5df05fbfc0c8f83d8871bfa033a5a2ead65a3f9d98ee895f'
predictions = list((run / 'context-16k/math500-level3').glob('*/predictions/minicpm/math_500_Level 3.jsonl'))
assert len(predictions) == 1
assert list((control / 'math4-artifacts').rglob('outside-*.json'))
command = ['python3', str(reader), '--eval-dir', str(predictions[0].parents[2]),
    '--raw-dir', str(control/'client-capture'), '--events-dir', str(control/'math4-artifacts'),
    '--reference-predictions', str(reference), '--output', str(control/'math4-review-decoded.json'),
    '--tokenizer', str(model)]
env = dict(os.environ, CUDA_VISIBLE_DEVICES='', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
with (control/'decode-command.json').open('x') as f:
    json.dump(dict(command=command, env={k:env[k] for k in ('CUDA_VISIBLE_DEVICES','HF_HUB_OFFLINE','TRANSFORMERS_OFFLINE')}),f,indent=2)
with (control/'decode-reader.log').open('x') as f:
    result = subprocess.run(command, env=env, stdout=f, stderr=subprocess.STDOUT)
report = json.loads((control/'math4-review-decoded.json').read_text())
print(json.dumps({k:v for k,v in report.items() if k not in ('questions','expected_questions')},ensure_ascii=False))
raise SystemExit(result.returncode)
