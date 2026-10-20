#!/usr/bin/env python3
"""Capture a deterministic model output fingerprint for change validation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests

PROMPT_TEXT = (
    "Explain why a KV cache improves decoder-only language model inference. "
    "Compare prefill and decode, describe the main memory-bandwidth cost, "
    "and give one concrete example. Keep the answer concise and technically "
    "accurate. "
) * 4


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:9031/v1/completions")
    parser.add_argument("--model", default="minicpm")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    # A normal prompt avoids pathological token sequences while remaining
    # deterministic across implementations.
    response = requests.post(
        args.url,
        json={
            "model": args.model,
            "prompt": PROMPT_TEXT,
            "max_tokens": 64,
            "temperature": 0,
            "ignore_eos": True,
        },
        timeout=600,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["text"]
    result = {
        "prompt": PROMPT_TEXT,
        "content": content,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "finish_reason": payload["choices"][0].get("finish_reason"),
        "service_fingerprint": payload.get("system_fingerprint"),
        "usage": payload.get("usage"),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({key: result[key] for key in ("sha256", "usage")}))


if __name__ == "__main__":
    main()
