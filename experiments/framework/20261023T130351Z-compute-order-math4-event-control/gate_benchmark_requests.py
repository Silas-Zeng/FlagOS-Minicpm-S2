"""同一次原 benchmark 生成32份 payload，只以文件事件阻塞尾30次原请求调用。"""
import argparse
import asyncio
import dataclasses
import functools
import hashlib
import importlib
from importlib.metadata import distribution
import inspect
import json
from pathlib import Path
import sys
import time

PINS = {
    'vllm.benchmarks.serve': 'b09e85eed6f5f7a9075b40a19fc1dd8e94a1c449665c2c6510f349e0409e77b7',
    'vllm.benchmarks.lib.endpoint_request_func': '5fd4b66d9ac6a88a278c2b7d65dcd17b8a9424279859ade14bddb69e342a312d',
}


def write_new(path, value):
    temporary = path.with_suffix('.writing')
    with temporary.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
    if path.exists():
        raise FileExistsError(path)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events', required=True, type=Path)
    parser.add_argument('--deadline-monotonic', required=True, type=float)
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.args[1:] if args.args[:1] == ['--'] else args.args
    if argv[:2] != ['bench', 'serve']:
        parser.error('只包装原 vllm bench serve')
    events = args.events.resolve()
    modules = {name: importlib.import_module(name) for name in PINS}
    for name, module in modules.items():
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != PINS[name]:
            raise ValueError('实际benchmark源码变化：' + name)
    serve = modules['vllm.benchmarks.serve']
    endpoint = modules['vllm.benchmarks.lib.endpoint_request_func']
    original_benchmark = serve.benchmark
    original_request = serve.ASYNC_REQUEST_FUNCS['vllm']
    if original_request is not endpoint.async_request_openai_completions:
        raise ValueError('原vllm请求入口已改变')
    requests, entered, finished = {}, set(), {}

    @functools.wraps(original_benchmark)
    async def benchmark(*positional, **keywords):
        values = inspect.signature(original_benchmark).bind(*positional, **keywords).arguments
        samples = values['input_requests']
        if (requests or len(samples) != 32 or values['endpoint_type'] != 'vllm'
                or values['num_warmups'] != 0 or not values['ignore_eos']
                or values['max_concurrency'] != 64 or values['profile']):
            raise ValueError('非原32×16K/128 c64单次benchmark')
        rows = []
        for index, sample in enumerate(samples):
            raw = dataclasses.asdict(sample)
            rid = sample.request_id
            # 原RandomDataset的prompt_len不含当前tokenizer的1个BOS；不改16384原CLI/payload。
            if (not isinstance(rid, str) or not rid or rid in requests
                    or sample.prompt_len != 16383 or sample.expected_output_len != 128
                    or sample.multi_modal_data is not None):
                raise ValueError('原请求身份/负载范围不符')
            requests[rid] = index
            encoded = json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
            rows.append(dict(index=index, header_request_id=rid, response_request_id='cmpl-' + rid,
                engine_input_request_id='cmpl-' + rid + '-0',
                sample_sha256=hashlib.sha256(encoded).hexdigest(), sample=raw))
        identity = dict(engine_input_request_ids=[row['engine_input_request_id'] for row in rows[:2]])
        write_new(events / 'background-request-ids.json', identity)
        identity_sha = hashlib.sha256((events / 'background-request-ids.json').read_bytes()).hexdigest()
        write_new(events / 'benchmark-original-requests.json', dict(requests=rows,
            seed=721201, one_original_sample_list=True, source_sha256=PINS,
            identity_config_sha256=identity_sha, monotonic_ns=time.monotonic_ns()))
        return await original_benchmark(*positional, **keywords)

    @functools.wraps(original_request)
    async def request(request_func_input, session, pbar=None):
        rid = request_func_input.request_id
        if rid is None:
            # 原endpoint ready check不属于32请求；不增删或改写它。
            return await original_request(request_func_input=request_func_input, session=session, pbar=pbar)
        if rid not in requests or rid in entered:
            raise ValueError('原请求未知或重复，不重试')
        entered.add(rid)
        index = requests[rid]
        if index >= 2:
            while not (events / 'release-background-tail.json').is_file():
                if any((events / name).is_file() for name in ('observer-error.json', 'uncovered.json')):
                    raise RuntimeError('本次observer未覆盖/失败，不放行尾30')
                if time.monotonic() >= args.deadline_monotonic:
                    raise TimeoutError('本次尾30事件未到，不重排重试')
                await asyncio.sleep(0.02)
            pair, release = (json.loads((events / name).read_text()) for name in
                ('background-both-q1.json', 'release-background-tail.json'))
            identity_sha = hashlib.sha256((events / 'background-request-ids.json').read_bytes()).hexdigest()
            if (pair.get('pid') != release.get('pid') or type(pair.get('pid')) is not int
                    or pair['pid'] <= 0 or pair.get('config_sha256') != identity_sha
                    or release.get('config_sha256') != identity_sha
                    or release.get('event') != 'release_background_tail'):
                raise ValueError('本次尾30信号PID/原身份SHA不符')
        value = await original_request(request_func_input=request_func_input, session=session, pbar=pbar)
        finished[rid] = dict(index=index, success=value.success, monotonic_ns=time.monotonic_ns())
        if index < 2:
            write_new(events / ('background-' + str(index) + '-returned.json'), finished[rid])
        return value

    entries = [ep for ep in distribution('vllm').entry_points if ep.group == 'console_scripts' and ep.name == 'vllm']
    if len(entries) != 1 or entries[0].value != 'vllm.entrypoints.cli.main:main':
        raise ValueError('非固定vllm console入口')
    console = entries[0].load()
    old_argv = sys.argv
    serve.benchmark, serve.ASYNC_REQUEST_FUNCS['vllm'] = benchmark, request
    try:
        sys.argv = ['vllm', *argv]
        return console()
    finally:
        serve.benchmark, serve.ASYNC_REQUEST_FUNCS['vllm'] = original_benchmark, original_request
        sys.argv = old_argv
        write_new(events / 'benchmark-request-outcomes.json', dict(
            original_requests=len(requests), entered=len(entered), finished=finished,
            tail_released=(events / 'release-background-tail.json').is_file(),
            monotonic_ns=time.monotonic_ns()))


if __name__ == '__main__':
    raise SystemExit(main())
