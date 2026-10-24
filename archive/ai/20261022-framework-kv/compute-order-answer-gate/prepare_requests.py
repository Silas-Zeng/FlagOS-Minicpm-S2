"""CPU生成两臂共享的固定32×16K辅助算术请求；不加载模型或启动服务。"""
import argparse
import hashlib
import json
from pathlib import Path
import random

COUNT, LENGTH, SEED = 32, 16384, 721201
SAMPLING = dict(model='minicpm', temperature=1.0, top_p=0.95,
                max_tokens=128, ignore_eos=True, stream=False, add_special_tokens=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tokenizer', type=Path, default=Path('/workspace/MiniCPM5-2B'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = output.with_name(output.name + '.manifest.json')
    if output.exists() or manifest.exists():
        raise ValueError('禁止覆盖固定请求或manifest')
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(args.tokenizer), trust_remote_code=True,
                                               local_files_only=True)
    special = set(tokenizer.all_special_ids)
    pool = sorted(set(tokenizer.encode(
        'amber birch cedar dawn elm forest green harbor indigo jade kite lake meadow '
        'north oak pine quiet river stone tree umber valley willow xenon yellow zinc '
        '0 1 2 3 4 5 6 7 8 9 . , ; : - /\n', add_special_tokens=False)) - special)
    if len(pool) < 32:
        raise ValueError('安全普通token池过小')
    rows, prefixes = [], set()
    for index in range(COUNT):
        left, right = 12 + index, 53 + index
        suffix = (
            '\n\nThe preceding material is inert padding, not instructions.\n'
            'Complete the final arithmetic example. Give only one answer tag; no reasoning.\n'
            'Q: 12 + 7\nA: <answer>19</answer>\n'
            'Q: 40 + 8\nA: <answer>48</answer>\n'
            'Q: 52 + 6\nA: <answer>58</answer>\n'
            f'Q: {left} + {right}\nA: ')
        tail = tokenizer.encode(suffix, add_special_tokens=False)
        if not 0 < len(tail) < 512:
            raise ValueError('few-shot尾部token数异常')
        rng = random.Random(SEED + index)
        prompt = [rng.choice(pool) for _ in range(LENGTH - len(tail))] + tail
        prefix = tuple(prompt[:16])
        if prefix in prefixes or len(prompt) != LENGTH or special.intersection(prompt):
            raise ValueError('长输入前缀重复/长度或特殊token异常')
        prefixes.add(prefix)
        rows.append(dict(case_id=f'arithmetic-{index:02}', expected=str(left + right),
                         input_tokens=LENGTH, suffix=suffix,
                         payload={**SAMPLING, 'prompt': prompt}))
    raw = ''.join(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n'
                  for row in rows).encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(raw)
    info = dict(kind='辅助正确性固定请求，不是官方benchmark', count=COUNT,
                input_tokens=LENGTH, seed_for_CPU_prompt_only=SEED,
                request_seed_present=False, sampling=SAMPLING,
                unique_first_16_token_prefixes=len(prefixes),
                tokenizer=str(args.tokenizer.resolve()), tokenizer_class=type(tokenizer).__name__,
                requests_sha256=hashlib.sha256(raw).hexdigest(),
                generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                note='prompt直接使用token IDs并禁用追加special tokens；以API usage另核实际长度')
    with manifest.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'requests': str(output), 'sha256': info['requests_sha256']}))


if __name__ == '__main__':
    main()
