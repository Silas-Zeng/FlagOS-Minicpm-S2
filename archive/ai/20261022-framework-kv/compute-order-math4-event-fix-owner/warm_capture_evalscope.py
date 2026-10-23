"""原四题到原generate入口后等待事件；capture9e1、原请求/判卷保持不变。"""
import argparse
import asyncio
import functools
import hashlib
import importlib
import json
from pathlib import Path
import runpy
import sys
import threading
import time

CAPTURE_SHA = '9e1f6bcf44c0b3c78226e87d2b8ccc0b5a95aa6d5af98a2eeab6f66a41d74aa5'
ADAPTER_SHA = 'db603642a610f2cc80eaec13fae8e4ab55389a19cc442f94e618ad3806b65f5d'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True, type=Path)
    parser.add_argument('--capture', required=True, type=Path)
    parser.add_argument('--deadline-monotonic', required=True, type=float)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.args[1:] if args.args[:1] == ['--'] else args.args
    if hashlib.sha256(args.capture.read_bytes()).hexdigest() != CAPTURE_SHA:
        raise ValueError('原capture9e1身份变化')
    module = importlib.import_module('evalscope.models.openai_compatible')
    if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != ADAPTER_SHA:
        raise ValueError('原EvalScope adapter身份变化')
    cls = module.OpenAICompatibleAPI
    original, original_async = cls.generate, cls.generate_async
    for function in (original, original_async):
        if (function.__globals__ is not vars(module)
                or Path(function.__code__.co_filename).resolve() != Path(module.__file__).resolve()):
            raise ValueError('原generate入口已被其它包装替换')
    events, lock, calls = args.events.resolve(), threading.Lock(), []

    def arrived():
        with lock:
            calls.append(time.monotonic_ns())
            if len(calls) > 4:
                raise ValueError('超过原四题调用，拒绝重试或额外API题')
            if len(calls) == 4:
                path = events / 'math4-client-ready.json'
                temporary = path.with_suffix('.writing')
                with temporary.open('x', encoding='utf-8') as stream:
                    json.dump(dict(ready_calls=4, generate_enter_monotonic_ns=calls,
                        before_original_generate=True), stream)
                if path.exists():
                    raise FileExistsError(path)
                temporary.replace(path)

    def pending():
        if any((events / name).is_file() for name in ('observer-error.json', 'uncovered.json')):
            raise RuntimeError('本次observer未覆盖/失败，不放行四题')
        if time.monotonic() >= args.deadline_monotonic:
            raise TimeoutError('本次四题放行事件未到，不换题/重试')
        return not (events / 'math4-go.json').is_file()

    @functools.wraps(original)
    def generate(*positional, **keywords):
        arrived()
        while pending():
            threading.Event().wait(0.02)
        return original(*positional, **keywords)

    @functools.wraps(original_async)
    async def generate_async(*positional, **keywords):
        arrived()
        while pending():
            await asyncio.sleep(0.02)
        return await original_async(*positional, **keywords)

    cls.generate, cls.generate_async = generate, generate_async
    old_argv = sys.argv
    try:
        sys.argv = [str(args.capture), *argv]
        runpy.run_path(str(args.capture), run_name='__main__')
    finally:
        if cls.generate is generate:
            cls.generate = original
        if cls.generate_async is generate_async:
            cls.generate_async = original_async
        sys.argv = old_argv


if __name__ == '__main__':
    raise SystemExit(main())
