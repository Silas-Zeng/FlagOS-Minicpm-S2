"""只用两个真实请求形成 decode + 长 prefill；不伪造 scheduler/metadata。"""
import json
from pathlib import Path
import re
import threading
import time
import urllib.request

import cache_gate as gate


def run_pair(run):
    folder = Path(run) / 'mixed-requests'
    folder.mkdir()
    first_content = threading.Event()
    errors = []
    rows = []
    counting = {'model': 'minicpm', 'messages': [
        {'role': 'system', 'content': '请严格按要求输出，不解释，不省略。'},
        {'role': 'user', 'content': '从1开始依次列出到128的每个整数。每个整数单独一行，全部列完，不要省略，不要添加其他文字。'}],
        'temperature': 0, 'max_tokens': 1024, 'stream': True,
        'stream_options': {'include_usage': True}}
    long = {'model': 'minicpm', 'messages': [
        {'role': 'system', 'content': '请只输出最终答案的十进制整数，不要解释，也不要重复题目。'},
        {'role': 'user', 'content': ('以下均为无关背景，请勿计算或回答：岸边有花，山间有路。\n' * 256)
            + '\n背景结束。唯一问题：计算 46 + 39。'}],
        'temperature': 0, 'max_tokens': 1024}
    gate.save(folder / 'decode-request.json', counting)
    gate.save(folder / 'prefill-request.json', long)

    def decode():
        started = time.monotonic()
        chunks = []; content = []; usage = {}; first = None
        try:
            request = urllib.request.Request('http://127.0.0.1:9031/v1/chat/completions',
                data=json.dumps(counting).encode(), headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(request, timeout=600) as response, (folder / 'decode-sse.txt').open('wb') as raw:
                for line in response:
                    raw.write(line); raw.flush()
                    if not line.startswith(b'data: '): continue
                    data = line[6:].strip()
                    if data == b'[DONE]': break
                    value = json.loads(data)
                    chunks.append(value)
                    if value.get('usage'): usage = value['usage']
                    for choice in value.get('choices', []):
                        piece = choice.get('delta', {}).get('content')
                        if piece:
                            content.append(piece)
                            if first is None:
                                first = time.monotonic(); first_content.set()
            visible = ''.join(content).strip()
            while visible.startswith('<think>') and '</think>' in visible:
                visible = visible.split('</think>', 1)[1].strip()
            numbers = [int(x) for x in re.findall(r'\d+', visible)]
            gate.require(numbers == list(range(1, 129)), 'mixed decode计数结果不完整或乱序')
            result = dict(name='decode', correct=True, visible=visible, usage=usage,
                first_content_time=first, started=started, finished=time.monotonic())
            gate.save(folder / 'decode-response.json', dict(result, chunks=chunks))
            rows.append(result)
        except BaseException as error:
            errors.append(repr(error)); first_content.set()

    thread = threading.Thread(target=decode, daemon=True)
    thread.start()
    gate.require(first_content.wait(120), '120秒内未收到真实decode内容，未提交prefill')
    gate.require(not errors and thread.is_alive(), 'decode在prefill提交前已结束/失败')
    started = time.monotonic()
    request = urllib.request.Request('http://127.0.0.1:9031/v1/chat/completions',
        data=json.dumps(long).encode(), headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request, timeout=600) as response:
        value = json.load(response)
    gate.save(folder / 'prefill-response.json', value)
    visible = gate.final_answer(value['choices'][0]['message'].get('content'), 85)
    gate.require(value.get('usage', {}).get('prompt_tokens', 0) >= 4096, 'mixed长prefill不足4096 tokens')
    rows.append(dict(name='prefill', correct=True, visible=visible, usage=value.get('usage', {}),
        started=started, finished=time.monotonic()))
    thread.join(timeout=600)
    gate.require(not thread.is_alive() and not errors, 'decode未完成或失败: '+repr(errors))
    gate.save(folder / 'result.json', dict(completed=True, requests=rows,
        limitation='请求时间重叠不等于mixed覆盖；实际FIRST_SELECTED及双prefix图另核'))
    return rows
