#!/usr/bin/env python3
"""Tiny CoreX external timing-event graph capability gate; not performance."""
import fcntl
import json
from pathlib import Path
import sys
import traceback

from validate_block_table_candidate import ROOT, IXSMI, preflight, utc


def main():
    run = Path(sys.argv[1]).resolve()
    if not run.is_relative_to(ROOT) or run == ROOT:
        raise ValueError('run outside experiment directory')
    run.mkdir(parents=True, exist_ok=False)
    (run / 'probe.py').write_bytes(Path(__file__).read_bytes())
    result = {'started_utc': utc(), 'kind': 'graph event capability; not timing score'}
    lock = (ROOT / 'framework-device.lock').open('a')
    status = 1
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        result['preflight'] = preflight(IXSMI)
        import torch
        result['torch'] = torch.__version__
        torch.cuda.set_device(0)
        x = torch.arange(4096, device='cuda', dtype=torch.float32)
        output = torch.empty_like(x)
        start = torch.cuda.Event(enable_timing=True, external=True)
        stop = torch.cuda.Event(enable_timing=True, external=True)
        stream = torch.cuda.Stream()
        stream.wait_stream(torch.cuda.current_stream())
        with torch.cuda.stream(stream):
            torch.add(x, 1, out=output)
        torch.cuda.synchronize()
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph, stream=stream):
            start.record()
            torch.add(x, 1, out=output)
            stop.record()
        samples = []
        for _ in range(3):
            graph.replay()
            torch.cuda.synchronize()
            samples.append(start.elapsed_time(stop))
            if not torch.equal(output, x + 1):
                raise AssertionError('captured event graph output mismatch')
        if not all(value > 0 for value in samples):
            raise AssertionError('nonpositive graph event duration')
        result.update(passed=True, replay_event_ms=samples)
        status = 0
    except Exception:
        result.update(passed=False, error=traceback.format_exc())
    finally:
        result.update(finished_utc=utc(), exit_code=status)
        (run / 'result.json').write_text(json.dumps(result, indent=2))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
