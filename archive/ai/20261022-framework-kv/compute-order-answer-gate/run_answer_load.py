"""只发固定辅助答案请求；逐条保存原始响应，不重试，不改服务或RNG状态。"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import re
import shutil
import time
import urllib.error
import urllib.request

SAMPLING = dict(model='minicpm', temperature=1.0, top_p=0.95,
                max_tokens=128, ignore_eos=True, stream=False, add_special_tokens=False)
TAG = re.compile(r'<answer>(.*?)</answer>', re.DOTALL)
MARKER = 'BIV150_COMPUTE_ORDER_FIRST_SELECTED '


def load_requests(path):
    raw = path.read_bytes()
    manifest_path = path.with_name(path.name + '.manifest.json')
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    pin = hashlib.sha256(raw).hexdigest()
    if pin != manifest['requests_sha256'] or manifest['count'] != 32:
        raise ValueError('固定请求manifest不匹配')
    rows = [json.loads(line) for line in raw.decode().splitlines()]
    if len(rows) != 32 or len({row['case_id'] for row in rows}) != 32:
        raise ValueError('要求32个唯一请求')
    if len({tuple(row['payload']['prompt'][:16]) for row in rows}) != 32:
        raise ValueError('请求首个KV块前缀重复')
    for index, row in enumerate(rows):
        payload = row['payload']
        if (row['case_id'] != f'arithmetic-{index:02}'
                or row['expected'] != str(65 + 2 * index)
                or row['input_tokens'] != 16384
                or {k: v for k, v in payload.items() if k != 'prompt'} != SAMPLING
                or len(payload['prompt']) != 16384
                or any(type(token) is not int or token < 0 for token in payload['prompt'])):
            raise ValueError('固定问题/采样参数/token IDs变化')
    return rows, pin, manifest_path


def send_one(row, folder):
    case = row['case_id']
    begin = time.monotonic_ns()
    request_raw = json.dumps(row['payload'], ensure_ascii=False, separators=(',', ':')).encode()
    (folder / (case + '.request.json')).write_bytes(request_raw)
    request = urllib.request.Request('http://127.0.0.1:9031/v1/completions', data=request_raw,
        headers={'Content-Type': 'application/json', 'X-Answer-Gate-Case': case})
    result = dict(case_id=case, expected=row['expected'], transport_ok=False,
                  answer_correct=False, length_valid=False)
    try:
        with urllib.request.urlopen(request, timeout=240) as response:
            raw = response.read()
            result['http_status'] = response.status
        (folder / (case + '.response.json')).write_bytes(raw)
        parsed = json.loads(raw)
        choices = parsed.get('choices', [])
        if len(choices) != 1 or not isinstance(choices[0].get('text'), str):
            raise ValueError('单条completion返回结构异常')
        text = choices[0]['text']
        found = TAG.search(text)
        inner = found.group(1).strip() if found else None
        answer = str(int(inner)) if inner is not None and re.fullmatch(r'[+-]?\d+', inner) else None
        result.update(transport_ok=True, answer=answer, first_complete_tag=found.group(0) if found else None,
                      answer_correct=answer == row['expected'], finish_reason=choices[0].get('finish_reason'),
                      usage=parsed.get('usage', {}))
        usage = result['usage']
        result['length_valid'] = (usage.get('prompt_tokens') == 16384
                                  and usage.get('completion_tokens') == 128)
    except urllib.error.HTTPError as error:
        (folder / (case + '.http-error.body')).write_bytes(error.read())
        result['error'] = f'HTTPError:{error.code}'
    except Exception as error:
        result['error'] = type(error).__name__ + ':' + str(error)
    result['elapsed_ns'] = time.monotonic_ns() - begin
    return result


def selection_records(log):
    records = []
    for line in log.read_text(encoding='utf-8', errors='replace').splitlines():
        if MARKER not in line:
            continue
        record, _ = json.JSONDecoder().raw_decode(line.split(MARKER, 1)[1].lstrip())
        if (type(record.get('pid')) is int and record['pid'] > 0
                and type(record.get('N')) is int and 3 <= record['N'] <= 64
                and type(record.get('M')) is int and record['M'] > record['N']
                and type(record.get('Dprefix')) is int and record['Dprefix'] > 0
                and type(record.get('outside')) is int and record['outside'] > 0
                and record.get('Dall') == record['Dprefix'] + record['outside'] < record['N']
                and record.get('sampler_rows') == record['N']
                and record.get('original_model_forward_returned') is True
                and record.get('runtime_mode') == 'NONE'
                and record.get('inverse_logits_order') == 'original_request_rows'
                and record.get('token_bitwise_equivalence_claimed') is False):
            records.append(record)
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--requests', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--variant', choices=('baseline', 'candidate'), required=True)
    parser.add_argument('--server-log', type=Path, required=True)
    args = parser.parse_args()
    rows, pin, manifest_path = load_requests(args.requests)
    folder = args.run_dir.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.requests, folder / 'requests.jsonl')
    shutil.copyfile(manifest_path, folder / 'requests-manifest.json')
    # A cold-start marker must not stand in for a hit during this answer load.
    before = selection_records(args.server_log)
    results = []
    with ThreadPoolExecutor(max_workers=64) as pool:
        futures = {pool.submit(send_one, row, folder): row['case_id'] for row in rows}
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            (folder / (result['case_id'] + '.result.json')).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    results.sort(key=lambda row: row['case_id'])
    after = selection_records(args.server_log)
    selected = after[len(before):] if after[:len(before)] == before else []
    actual_hit = bool(selected and len({record['pid'] for record in selected}) == 1)
    passed_answers = all(row['transport_ok'] and row['answer_correct'] and row['length_valid'] for row in results)
    passed = passed_answers and (actual_hit if args.variant == 'candidate' else not after)
    summary = dict(kind='辅助答案正确性，不是官方accuracy/数值或RNG逐位证明', variant=args.variant,
        passed=passed, questions=32, transport_success=sum(row['transport_ok'] for row in results),
        correct_answers=sum(row['answer_correct'] for row in results),
        valid_lengths=sum(row['length_valid'] for row in results), requests_sha256=pin,
        selection_before_load=before, actual_selection_during_load=selected,
        candidate_actual_hit=actual_hit, baseline_own_failure_means_inconclusive=args.variant == 'baseline' and not passed,
        limits=['只核各题首个完整answer tag，忽略强制128输出的后续续写',
                '原global RNG路径，无request seed/额外sampler；不声称随机token逐位一致',
                'FIRST_SELECTED在forward返回后、logits/sampler前；32条完整答案是另一个事实',
                '单次命中不代表全部请求/全部batch覆盖；两臂正确性不作性能收益'],
        results=results)
    (folder / 'answer-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
