"""原四语义题与HTTP/判分逐字复用，只选择顺序与分段原件目录。"""
import json
import time
import urllib.request
from cache_gate import save, final_answer, require


def run_cases(folder, case_names):
    folder.mkdir(exist_ok=False)
    cases = [('add', '计算 27 + 58。', 85), ('multiply', '计算 17 × 19。', 323),
             ('divide', '计算 144 ÷ 12。', 12),
             ('long-prefill', ('以下均为无关背景，请勿计算或回答：山边有树，河边有桥。\n' * 256)
              + '\n背景结束。唯一问题：计算 37 + 58。', 95)]
    lookup = {row[0]: row for row in cases}
    require(len(case_names) == len(set(case_names)) and all(name in lookup for name in case_names), "语义题选择不符")
    cases = [lookup[name] for name in case_names]
    rows = []
    for name, prompt, expected in cases:
        request = {'model': 'minicpm', 'messages': [
            {'role': 'system', 'content': '请只输出最终答案的十进制整数，不要解释，也不要重复题目。'},
            {'role': 'user', 'content': prompt}], 'temperature': 0, 'max_tokens': 1024}
        save(folder / (name + '-request.json'), request)
        started = time.monotonic()
        http = urllib.request.Request('http://127.0.0.1:9031/v1/chat/completions',
                                      data=json.dumps(request).encode(), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(http, timeout=600) as response:
            value = json.load(response)
        save(folder / (name + '-response.json'), value)
        message = value['choices'][0]['message']
        content = message.get('content')
        visible = final_answer(content, expected)
        usage = value.get('usage', {})
        if name == 'long-prefill':
            require(usage.get('prompt_tokens', 0) >= 4096, '长 prefill 未达到 4096 prompt tokens')
        rows.append({'name': name, 'expected': expected, 'visible': visible, 'usage': usage,
                     'elapsed_seconds': time.monotonic() - started, 'correct': True})
        save(folder / 'requests.json', rows)
    return rows
