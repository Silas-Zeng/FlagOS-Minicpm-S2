"""只在独立EvalScope客户端旁存raw token IDs；原响应转换与判卷保持原路。"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

PINS = {
    'evalscope.models.openai_compatible': 'db603642a610f2cc80eaec13fae8e4ab55389a19cc442f94e618ad3806b65f5d',
    'evalscope.models.utils.openai': 'eb5ba96a6769912992a8dfc71270f1572c021bbafb7a5753e4747dbaeea5cb54',
    'evalscope.api.model.model_output': '5d24feda4a0eeb31cde6eb6fb8c92704b0ac1e1d378ac876bcf01259ea20eaf4',
}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('args', nargs=argparse.REMAINDER)
    args = p.parse_args()
    argv = args.args[1:] if args.args[:1] == ['--'] else args.args
    if not argv or argv[0] != 'eval':
        p.error('须保留原evalscope eval子命令')
    folder = args.output.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    import importlib
    for name, pin in PINS.items():
        module = importlib.import_module(name)
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != pin:
            raise ValueError('非固定EvalScope1.11.1源码：' + name)
    module = sys.modules['evalscope.models.openai_compatible']
    cls = module.OpenAICompatibleAPI
    original_params, original_response = cls.completion_params, cls.on_response
    for function in (original_params, original_response):
        if (function.__globals__ is not vars(module)
                or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise ValueError('EvalScope原hook已被其它包装替换')
    def params(self, config, tools):
        value = original_params(self, config, tools)
        extra = dict(value.get('extra_body') or {})
        if extra.get('return_token_ids') not in (None, True):
            raise ValueError('与原显式return_token_ids冲突')
        extra['return_token_ids'] = True
        return {**value, 'extra_body': extra}
    def response(self, raw):
        result = original_response(self, raw)
        rid = raw.get('id')
        if (not isinstance(rid, str) or not rid.startswith('chatcmpl-')
                or len(raw.get('choices', [])) != 1
                or not isinstance(raw['choices'][0].get('token_ids'), list)):
            raise ValueError('原API未保留单题真实token IDs')
        # 不修改raw/原返回对象；拒重复响应而不是静默重采样。
        name = hashlib.sha256(rid.encode()).hexdigest() + '.json'
        with (folder / name).open('x', encoding='utf-8') as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        return result
    cls.completion_params, cls.on_response = params, response
    old_argv = sys.argv
    try:
        from evalscope.cli.cli import run_cmd
        sys.argv = ['evalscope', *argv]
        return run_cmd()
    finally:
        if cls.completion_params is params:
            cls.completion_params = original_params
        if cls.on_response is response:
            cls.on_response = original_response
        sys.argv = old_argv


if __name__ == '__main__':
    raise SystemExit(main())
