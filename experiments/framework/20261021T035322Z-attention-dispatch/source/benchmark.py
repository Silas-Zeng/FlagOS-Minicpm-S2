#!/usr/bin/env python3
"""Short isolated launch/dispatch screen, with the retained attention arithmetic."""

import argparse
import fcntl
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess
import sys
import traceback

from validate_block_table_candidate import ROOT, preflight, IXSMI, utc


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(torch, lengths, kv_len, padded=False):
    n = len(lengths)
    tokens = max(sum(lengths), n) if padded else sum(lengths)
    blocks = (kv_len + 15) // 16
    q = torch.randn((tokens, 16, 128), dtype=torch.bfloat16, device='cuda')
    k = torch.randn((n * blocks, 16, 2, 128), dtype=q.dtype, device='cuda')
    v = torch.randn_like(k)
    cu = torch.tensor([0] + list(__import__('itertools').accumulate(lengths)),
                      dtype=torch.int32, device='cuda')
    seq = torch.tensor([kv_len if length else 0 for length in lengths],
                       dtype=torch.int32, device='cuda')
    table = torch.arange(n * blocks, dtype=torch.int32, device='cuda').reshape(n, blocks)
    scratch = {
        'softmax_segm_output': torch.empty((64, 16, 16, 128), device='cuda'),
        'softmax_segm_max': torch.empty((64, 16, 16), device='cuda'),
        'softmax_segm_expsum': torch.empty((64, 16, 16), device='cuda'),
    }
    return dict(q=q, k=k, v=v, cu_seqlens_q=cu, seqused_k=seq, block_table=table,
                max_seqlen_q=max(lengths), max_seqlen_k=kv_len,
                seq_threshold_3D=64, num_par_softmax_segments=16, **scratch)


def invoke(module, data, output):
    module.unified_attention(
        **data, out=output, softmax_scale=128 ** -0.5,
        causal=True, window_size=(-1, -1), softcap=0,
        q_descale=None, k_descale=None, v_descale=None,
    )


def times(torch, fn, graph_mode, repeats=5):
    for _ in range(2):
        fn()
    torch.cuda.synchronize()
    if graph_mode:
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            fn()
        torch.cuda.current_stream().wait_stream(stream)
        torch.cuda.synchronize()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            fn()
        fn = graph.replay
    values = []
    for _ in range(repeats):
        begin, end = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        begin.record()
        fn()
        end.record()
        end.synchronize()
        values.append(begin.elapsed_time(end))
    return values


def compare(torch, left, right, count):
    left, right = left[:count], right[:count]
    return {'valid_tokens': count, 'bitwise_equal': torch.equal(left, right),
            'finite': bool(torch.isfinite(left).all() and torch.isfinite(right).all()),
            'max_abs_diff': float((left.float() - right.float()).abs().max())}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--transform-path', type=Path, required=True)
    args = parser.parse_args()
    run = args.run_dir.resolve()
    if not run.is_relative_to(ROOT) or run == ROOT:
        raise ValueError('run directory must be new and inside experiment workspace')
    run.mkdir(parents=True, exist_ok=False)
    rows, monitor = [], None
    manifest = {'started_utc': utc(), 'command': sys.argv,
                'kind': 'single-layer diagnostic; not a model score'}
    status, torch = 1, None
    lock = (ROOT / 'framework-device.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        manifest['preflight'] = preflight(IXSMI)
        import os
        import torch
        import vllm.v1.attention.ops.triton_unified_attention as installed
        import vllm.v1.attention.ops.triton_attention_helpers as helpers
        torch.cuda.set_device(0)
        torch.manual_seed(1234)
        source = run / 'source'
        source.mkdir()
        original_path, candidate_path = source / 'original.py', source / 'direct_decode.py'
        original_bytes = Path(installed.__file__).read_bytes()
        helper_bytes = Path(helpers.__file__).read_bytes()
        original_path.write_bytes(original_bytes)
        (source / 'helpers.py').write_bytes(helper_bytes)
        transform_path = source / 'transform.py'
        transform_path.write_bytes(args.transform_path.read_bytes())
        transform = load('biv150_decode_transform', transform_path)
        candidate_path.write_bytes(transform.transform(original_bytes, helper_bytes))
        (source / 'benchmark.py').write_bytes(Path(__file__).read_bytes())
        manifest['sha256'] = {p.name: digest(p) for p in source.iterdir() if p.is_file()}
        manifest['device'] = str(torch.cuda.get_device_properties(0))
        (run / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        original = load('biv150_attention_control', original_path)
        candidate = load('biv150_attention_direct_decode', candidate_path)
        monitor = subprocess.Popen(['bash', str(ROOT / 'scripts/monitor_gpu.sh'),
                                    str(os.getpid()), str(run / 'gpu.csv')],
                                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cases = [
            ('dense-4k', [1] * 64, 4096, False),
            ('dense-16k', [1] * 30, 16384, False),
            ('padded-tail', [1] * 13 + [0] * 3, 4096, True),
            ('zero-middle', [1, 0, 1, 1, 0, 1, 1, 1], 127, True),
            ('prefill-fallback', [16, 13], 256, False),
        ]
        for label, lengths, kv_len, padded in cases:
            data = inputs(torch, lengths, kv_len, padded)
            control, changed = torch.empty_like(data['q']), torch.empty_like(data['q'])
            invoke(original, data, control)
            invoke(candidate, data, changed)
            torch.cuda.synchronize()
            row = dict(kind='direct-decode', case=label,
                       **compare(torch, control, changed, sum(lengths)))
            if not row['finite'] or not row['bitwise_equal']:
                rows.append(row)
                raise AssertionError('direct decode failed exact output gate: ' + label)
            if label.startswith('dense'):
                a = times(torch, lambda: invoke(original, data, control), True)
                b = times(torch, lambda: invoke(candidate, data, changed), True)
                row.update(original_ms=a, candidate_ms=b,
                           original_median_ms=statistics.median(a),
                           candidate_median_ms=statistics.median(b))
            rows.append(row)
            print(json.dumps(row), flush=True)
        # Upper-bound opportunity screen: split only attention, keep KV and
        # token order. Metadata normalization is prepared once outside timing.
        for kv_len in (4096, 16384):
            d = 16
            data = inputs(torch, [1] * d + [2048 - d], kv_len)
            control, changed = torch.empty_like(data['q']), torch.empty_like(data['q'])
            decode, prefill = data.copy(), data.copy()
            decode.update(q=data['q'][:d], cu_seqlens_q=data['cu_seqlens_q'][:d + 1],
                          seqused_k=data['seqused_k'][:d], block_table=data['block_table'][:d],
                          max_seqlen_q=1)
            prefill.update(q=data['q'][d:], cu_seqlens_q=data['cu_seqlens_q'][d:] - d,
                           seqused_k=data['seqused_k'][d:], block_table=data['block_table'][d:],
                           max_seqlen_q=2048 - d)

            def split():
                invoke(original, decode, changed[:d])
                invoke(original, prefill, changed[d:])

            invoke(original, data, control)
            split()
            torch.cuda.synchronize()
            row = {'kind': 'mixed-attention-split', 'kv_len': kv_len,
                   'decode_requests': d, 'prefill_tokens': 2048 - d,
                   'decode_output': compare(torch, control[:d], changed[:d], d),
                   'prefill_output': compare(torch, control[d:], changed[d:], 2048 - d),
                   'limitation': 'single layer, approximate numerical candidate; excludes metadata normalization cost'}
            if not row['decode_output']['finite'] or not row['prefill_output']['finite']:
                rows.append(row)
                raise AssertionError('mixed split nonfinite output')
            a = times(torch, lambda: invoke(original, data, control), False)
            b = times(torch, split, False)
            row.update(original_ms=a, candidate_ms=b,
                       original_median_ms=statistics.median(a), candidate_median_ms=statistics.median(b))
            rows.append(row)
            print(json.dumps(row), flush=True)
        status = 0
    except BaseException:
        manifest['error'] = traceback.format_exc()
        print(manifest['error'], flush=True)
    finally:
        if torch is not None and torch.cuda.is_initialized():
            try:
                torch.cuda.synchronize()
            except BaseException:
                manifest['shutdown_error'] = traceback.format_exc()
                status = 1
        if monitor is not None:
            monitor.terminate()
            monitor.wait(timeout=10)
        manifest.update(finished_utc=utc(), exit_code=status)
        (run / 'manifest.json').write_text(json.dumps(manifest, indent=2))
        (run / 'results.json').write_text(json.dumps(rows, indent=2))
        (run / 'exit-code').write_text(str(status) + '\n')
        lock.close()
    return status


if __name__ == '__main__':
    raise SystemExit(main())
