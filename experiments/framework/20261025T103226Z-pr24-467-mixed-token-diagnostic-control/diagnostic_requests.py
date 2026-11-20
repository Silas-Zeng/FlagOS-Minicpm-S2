"""freshserver原mixed请求只加return_token_ids；两响应收齐后总结语义失败。"""
from collections import Counter
import json
from pathlib import Path
import re
import shutil
import sys
import threading
import time
import traceback
import urllib.error
import urllib.request

import cache_gate as gate

HERE = Path(__file__).resolve().parent
URL = 'http://127.0.0.1:9031/v1/chat/completions'


def payload(folder, name):
    original = HERE / (name + '-request.json')
    shutil.copyfile(original, folder / (name + '-request.original.json'))
    value = json.loads(original.read_bytes())
    gate.require('return_token_ids' not in value, '原请求已有token诊断字段')
    value['return_token_ids'] = True
    gate.save(folder / (name + '-request.json'), value)
    return value


def request(value):
    return urllib.request.Request(URL, data=json.dumps(value).encode(),
        headers={'Content-Type': 'application/json'})


def token_summary(values):
    """只读响应里的原token IDs；不猜字段缺失时的token或自动加载模型。"""
    found = {}
    def visit(value, path):
        if isinstance(value, dict):
            for key, item in value.items():
                next_path = path + '/' + key
                if key.endswith('token_ids') and isinstance(item, list):
                    integers = [v for v in item if isinstance(v, int) and not isinstance(v, bool)]
                    if len(integers) == len(item):
                        found.setdefault(next_path, []).extend(integers)
                else:
                    visit(item, next_path)
        elif isinstance(value, list):
            for item in value:
                visit(item, path + '/*')
    for value in values:
        visit(value, '')
    return {path: dict(count=len(ids), unique=len(set(ids)),
        top_counts=Counter(ids).most_common(12), first=ids[:16], last=ids[-16:])
        for path, ids in found.items()}


def json_response(folder, name, value):
    """原始body先保存，再JSON解析；HTTP失败原body同样保存。"""
    status = None
    try:
        with urllib.request.urlopen(request(value), timeout=600) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as error:
        raw = error.read()
        (folder / (name + '-response.json')).write_bytes(raw)
        gate.save(folder / (name + '-http.json'), dict(status=error.code, error=repr(error)))
        raise
    (folder / (name + '-response.json')).write_bytes(raw)
    gate.save(folder / (name + '-http.json'), dict(status=status))
    response = json.loads(raw)
    gate.save(folder / (name + '-tokens.json'), token_summary([response]))
    return response


def judge_prefill(value):
    visible = gate.final_answer(value['choices'][0]['message'].get('content'), 85)
    gate.require(value.get('usage', {}).get('prompt_tokens', 0) >= 4096,
        '原长prefill不足4096 tokens')
    return visible


def mixed(run_dir):
    folder = Path(run_dir) / 'mixed-requests'
    folder.mkdir()
    first_content = threading.Event()
    errors = []
    rows = []
    counting = payload(folder, 'decode')
    long = payload(folder, 'prefill')

    def decode():
        started = time.monotonic()
        chunks = []; content = []; usage = {}; first = None
        result = dict(name='decode', completed=False, correct=False, started=started)
        try:
            with urllib.request.urlopen(request(counting), timeout=600) as response, (folder / 'decode-sse.txt').open('wb') as raw:
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
            result.update(completed=True, usage=usage, first_content_time=first)
            visible = ''.join(content).strip()
            result['visible_raw'] = visible
            while visible.startswith('<think>') and '</think>' in visible:
                visible = visible.split('</think>', 1)[1].strip()
            result['visible'] = visible
            numbers = [int(x) for x in re.findall(r'\d+', visible)]
            try:
                gate.require(numbers == list(range(1, 129)), 'mixed decode计数结果不完整或乱序')
                result['correct'] = True
            except Exception as error:
                result['semantic_error'] = repr(error)
        except Exception as error:
            if isinstance(error, urllib.error.HTTPError):
                (folder / 'decode-http-error.body').write_bytes(error.read())
                result['http_status'] = error.code
            result['transport_error'] = repr(error)
            errors.append(repr(error)); first_content.set()
        finally:
            result['finished'] = time.monotonic()
            gate.save(folder / 'decode-response.json', dict(result, chunks=chunks))
            gate.save(folder / 'decode-tokens.json', token_summary(chunks))
            rows.append(result)

    thread = threading.Thread(target=decode, daemon=True)
    thread.start()
    pending = None
    try:
        # 原mixed first-content同步条件保持，不在首chunk前提交长题。
        gate.require(first_content.wait(120), '120秒内未收到真实decode内容，未提交prefill')
        gate.require(not errors and thread.is_alive(), 'decode在prefill提交前已结束/失败')
        started = time.monotonic()
        value = json_response(folder, 'prefill', long)
        result = dict(name='prefill', completed=True, correct=False, usage=value.get('usage', {}),
            finish_reason=value.get('choices', [{}])[0].get('finish_reason'), started=started)
        try:
            result['visible'] = judge_prefill(value)
            result['correct'] = True
        except Exception as error:
            result['semantic_error'] = repr(error)
            (folder / 'prefill-semantic-failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
        result['finished'] = time.monotonic()
        gate.save(folder / 'prefill-result.json', result)
        rows.append(result)
    except Exception as error:
        pending = error
        (folder / 'failure.txt').write_text(traceback.format_exc(), encoding='utf-8')
    finally:
        # 必须排空此阶段的stream，在原owner退出前保留已完成decode证据。
        if sys.exc_info()[0] is None:
            thread.join(timeout=600)
        result = dict(completed=len(rows) == 2 and all(r['completed'] for r in rows),
            correct=len(rows) == 2 and all(r['correct'] for r in rows), requests=rows,
            thread_alive=thread.is_alive(), transport_errors=errors,
            limitation='首内容同步保留；HTTP重叠不等于已证明模型每步mixed覆盖')
        if pending is not None:
            result['error'] = repr(pending)
        gate.save(folder / 'result.json', result)
    gate.require(not thread.is_alive() and not errors, 'mixed stream未排空或运输失败: ' + repr(errors))
    if pending is not None:
        raise pending
    return result


def run(run_dir):
    result = dict(completed=False, all_correct=False,
        limitation='freshserver原main526 mixed基线故障诊断；仅返回token IDs，不是准确率或性能')
    path = Path(run_dir) / 'diagnostic-summary.json'
    gate.save(path, result)
    try:
        result['mixed'] = mixed(run_dir)
    except Exception as error:
        result['error'] = repr(error)
        gate.save(path, result)
        raise
    result['completed'] = result['mixed']['completed']
    result['all_correct'] = result['mixed']['correct']
    gate.save(path, result)
    return result
