#!/usr/bin/env python3
"""Capture a deterministic model output fingerprint for change validation."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import requests


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:9031/v1/completions")
    parser.add_argument("--model", default="minicpm")
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    # Fixed, ordinary token IDs avoid tokenizer and special-token variability.
    prompt = [((i * 7919) % 120000) for i in range(128)]
    response = requests.post(
        args.url,
        json={
            "model": args.model,
            "prompt": prompt,
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
        "prompt_token_ids": prompt,
        "content": content,
        "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
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
