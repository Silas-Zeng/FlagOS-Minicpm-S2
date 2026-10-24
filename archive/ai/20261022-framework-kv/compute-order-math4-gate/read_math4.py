"""只读四题原判卷与实际outside关联；可选本地tokenizer只解码真实IDs。"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re


def absolute(path):
    value = os.path.abspath(str(path))
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        value = '\\\\?\\UNC\\' + value[2:] if value.startswith('\\\\') else '\\\\?\\' + value
    return Path(value)


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rows(path):
    return [json.loads(s) for s in path.read_text(encoding='utf-8-sig').splitlines() if s.strip()]


def keyed(items):
    result = {d['index']: d for d in items}
    if len(result) != len(items):
        raise ValueError('重复原评测index')
    return result


def complete_box(text):
    # 仅保守时间界，不抽取数学值、不替代原judge；空box也使其不认覆盖。
    for match in re.finditer(r'\\boxed\s*\{', text):
        depth, escaped = 1, False
        for char in text[match.end():]:
            if escaped:
                escaped = False
            elif char == '\\':
                escaped = True
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return True
    return False


def matches(internal, external):
    # 本诊断锁默认单prompt/n=1分支：external后恰有一个8字符随机后缀。
    return internal.startswith(external + '-') and len(internal) == len(external) + 9


def review(args):
    reference = keyed(rows(args.reference_predictions))
    expected = {i: reference[i]['metadata']['question_id'] for i in range(4)}
    predictions = keyed(rows(args.eval_dir / 'predictions/minicpm/math_500_Level 3.jsonl'))
    reviews = keyed(rows(args.eval_dir / 'reviews/minicpm/math_500_Level 3.jsonl'))
    if set(predictions) != set(range(4)) or set(reviews) != set(range(4)):
        raise ValueError('原四题未完整生成/判卷，不认完整诊断')
    raw = [load(p) for p in sorted(args.raw_dir.glob('*.json'))]
    responses = {d['id']: d for d in raw}
    if len(raw) != 4 or len(responses) != 4:
        raise ValueError('旁存须有4个唯一原response.id')
    if len({d['model_output']['id'] for d in predictions.values()}) != 4 or set(responses) != {
            d['model_output']['id'] for d in predictions.values()}:
        raise ValueError('四题原prediction与raw response.id非一一对应')
    events = [load(p) for p in sorted(args.events_dir.rglob('outside-*.json'))]
    if len(events) > 4 or len({e['internal_request_id'] for e in events}) != len(events):
        raise ValueError('outside记录重复或超过4个请求')
    decoder = None
    decode_needed = any(matches(e['internal_request_id'], rid) for e in events for rid in responses)
    if args.tokenizer and decode_needed:
        from transformers import AutoTokenizer
        decoder = AutoTokenizer.from_pretrained(str(args.tokenizer), local_files_only=True, trust_remote_code=False)
    results, attributed = [], set()
    for index in range(4):
        prediction, reviewed = predictions[index], reviews[index]
        score = reviewed['sample_score']['score']
        if (prediction['metadata']['question_id'] != expected[index]
                or reviewed['sample_score']['sample_metadata']['question_id'] != expected[index]
                or reviewed['sample_score']['sample_id'] != index or score['status'] != 'success'
                or score['value']['accuracy'] not in (0, 1)):
            raise ValueError('固定index0..3题身份/原判卷状态不符')
        output = prediction['model_output']
        response = responses[output['id']]
        if len(response['choices']) != 1 or output.get('error') is not None:
            raise ValueError('非单choice正常题响应')
        ids, prompt_ids = response['choices'][0]['token_ids'], response['prompt_token_ids']
        if (not all(type(t) is int and t >= 0 for t in ids + prompt_ids)
                or response['usage']['completion_tokens'] != len(ids)
                or response['usage']['prompt_tokens'] != len(prompt_ids)):
            raise ValueError('真实token IDs/usage不符')
        row = dict(index=index, question_id=expected[index], response_id=output['id'],
            original_judge_accuracy=score['value']['accuracy'], original_judge_status=score['status'],
            generated_tokens=len(ids), prompt_tokens=len(prompt_ids), outside_sample_returned=False,
            conservative_before_first_complete_box=None)
        selected = [e for e in events if matches(e['internal_request_id'], output['id'])]
        if len(selected) > 1:
            raise ValueError('external→完整internal RID映射不唯一')
        if selected:
            event = selected[0]
            rid = event['internal_request_id']
            if rid in attributed:
                raise ValueError('同一内部RID错误对应多题')
            attributed.add(rid)
            c, length, token_index = event['input_position'], event['prompt_len'], event['predicted_output_token_index_0based']
            if (event['status'] != 'actual_outside_and_original_sample_returned'
                    or event['original_sample_calls'] != 1 or event['same_scheduler_output'] is not True
                    or event['query_tokens'] != 1 or event['sampler_rows'] != event['N']
                    or event['outside'] <= 0 or length != len(prompt_ids) or c < length
                    or token_index != c - length + 1 or not 0 <= token_index < len(ids)):
                raise ValueError('实际P/原sample/绝对位置/token范围关联不符')
            row.update(outside_sample_returned=True, internal_request_id=rid, event=event,
                decode_status='not_requested_no_answer_time_claim')
            if decoder:
                before = decoder.decode(ids[:token_index], skip_special_tokens=True, clean_up_tokenization_spaces=False)
                full = decoder.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)
                prior_box, full_box = complete_box(before), complete_box(full)
                row.update(decode_status='real_ID_prefix_and_full_only', prefix_has_complete_box=prior_box,
                    full_has_complete_box=full_box,
                    conservative_before_first_complete_box=not prior_box and full_box)
                decoded = args.output.with_name(args.output.stem + '-q' + str(index) + '-decoded.json')
                decoded.write_text(json.dumps(dict(response_id=output['id'], internal_request_id=rid,
                    token_index=token_index, before_P_sample=before, full_output=full,
                    generated_ids_sha256=hashlib.sha256(json.dumps(ids, separators=(',', ':')).encode()).hexdigest()),
                    ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
                row['decoded_artifact'] = str(decoded)
        results.append(row)
    return dict(status='limited_diagnostic_metadata_reviewed', expected_questions=expected,
        original_judge_correct=sum(r['original_judge_accuracy'] for r in results),
        outside_linked_questions=sum(r['outside_sample_returned'] for r in results),
        conservative_before_box_questions=sum(r['conservative_before_first_complete_box'] is True for r in results),
        unattributed_event_rids=[e['internal_request_id'] for e in events if e['internal_request_id'] not in attributed],
        questions=results, reference_predictions_sha256=hashlib.sha256(args.reference_predictions.read_bytes()).hexdigest(),
        limits=['仅诊断，不是105题官方准确率或性能结果', '沿原judge结果；boxed存在性只作保守时间界，不是数学判卷',
                '前缀空boxed也拒覆盖；完整输出无boxed或无decoder不作答案时刻断言',
                '原sample返回与最终HTTP响应不等价于逐层、token或RNG逐位一致'])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('eval-dir', 'raw-dir', 'events-dir', 'reference-predictions', 'output'):
        p.add_argument('--' + name, required=True, type=absolute)
    p.add_argument('--tokenizer', type=absolute)
    args = p.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    try:
        result = review(args)
        code = 0
    except Exception as error:
        result, code = dict(status='incomplete_or_invalid_diagnostic', error=type(error).__name__ + ': ' + str(error)), 2
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in result.items() if k not in ('questions', 'expected_questions')}, ensure_ascii=True))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
