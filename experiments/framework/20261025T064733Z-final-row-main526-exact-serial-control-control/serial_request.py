"""只提交原已保存prefill请求一次，先保存原始HTTP响应再按原规则判分。"""
import json
from pathlib import Path
import shutil
import time
import urllib.error
import urllib.request
import cache_gate as gate

HERE=Path(__file__).resolve().parent


def run(run_dir):
    folder=Path(run_dir)/'serial-prefill'
    folder.mkdir()
    shutil.copyfile(HERE/'prefill-request.json',folder/'prefill-request.json')
    payload=json.loads((HERE/'prefill-request.json').read_bytes())
    started=time.monotonic()
    request=urllib.request.Request('http://127.0.0.1:9031/v1/chat/completions',
        data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=600) as response:
            raw=response.read()
    except urllib.error.HTTPError as error:
        (folder/'prefill-response.json').write_bytes(error.read())
        gate.save(folder/'response-metadata.json',dict(http_status=error.code,
            elapsed_seconds=time.monotonic()-started,request_sha256=gate.sha(folder/'prefill-request.json'),
            token_metadata_override=False))
        raise
    (folder/'prefill-response.json').write_bytes(raw)
    value=json.loads(raw)
    gate.save(folder/'response-metadata.json',dict(usage=value.get('usage',{}),
        finish_reason=value.get('choices',[{}])[0].get('finish_reason'),
        elapsed_seconds=time.monotonic()-started,request_sha256=gate.sha(folder/'prefill-request.json'),
        token_metadata_override=False))
    visible=gate.final_answer(value['choices'][0]['message'].get('content'),85)
    gate.require(value.get('usage',{}).get('prompt_tokens',0)>=4096,'原长prefill不足4096 tokens')
    result=dict(completed=True,correct=True,visible=visible,usage=value.get('usage',{}),
        elapsed_seconds=time.monotonic()-started,request_sha256=gate.sha(folder/'prefill-request.json'),
        limitation='仅原长题独立串行正确性定位，无并发计数/其它请求，不是完整准确率或性能')
    gate.save(folder/'result.json',result)
    return result
