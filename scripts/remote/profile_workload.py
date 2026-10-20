#!/usr/bin/env python3
"""Send exact-length completion requests for diagnostic profiling."""

from __future__ import annotations

import argparse
import json
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def one_request(url: str, model: str, input_len: int, output_len: int, seed: int):
    rng = random.Random(seed)
    token_ids = [rng.randrange(0, 120000) for _ in range(input_len)]
    payload = {
        "model": model,
        "prompt": token_ids,
        "max_tokens": output_len,
        "ignore_eos": True,
    }
    started = time.time()
    response = requests.post(url, json=payload, timeout=3600)
    elapsed = time.time() - started
    response.raise_for_status()
    body = response.json()
    usage = body.get("usage", {})
    return {
        "elapsed_s": elapsed,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "finish_reason": body.get("choices", [{}])[0].get("finish_reason"),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:9031/v1/completions")
    parser.add_argument("--model", default="minicpm")
    parser.add_argument("--input-len", type=int, required=True)
    parser.add_argument("--output-len", type=int, required=True)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261021)
    args = parser.parse_args()

    started = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [
            pool.submit(
                one_request,
                args.url,
                args.model,
                args.input_len,
                args.output_len,
                args.seed + index,
            )
            for index in range(args.concurrency)
        ]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            print(json.dumps(result), flush=True)

    wall_s = time.time() - started
    completion_tokens = sum(result["completion_tokens"] or 0 for result in results)
    prompt_tokens = sum(result["prompt_tokens"] or 0 for result in results)
    print(
        json.dumps(
            {
                "wall_s": wall_s,
                "requests": len(results),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens_s": (prompt_tokens + completion_tokens) / wall_s,
                "completion_tokens_s": completion_tokens / wall_s,
            }
        )
    )


if __name__ == "__main__":
    main()
