"""085500固定现场的T64在线softmax单变量CPU模型；不调用旧reader或GPU。"""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np

EXPECTED_PAYLOAD = 'a1f29e5f340acc0a533bb6bca14b97afcd902556f8768917b378a670090f6e49'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(raw):
    if raw.dtype != np.int16:
        raise ValueError('只接受捕获的BF16原始int16 bits')
    return (raw.astype(np.uint16).astype(np.uint32) << 16).view(np.float32)


def bf16_rne(value):
    """有限FP32→BF16 RNE→FP32，保留ties-to-even；本模型P和输出必须finite。"""
    value = np.ascontiguousarray(value, dtype=np.float32)
    if not np.isfinite(value).all():
        raise ValueError('RNE只接收有限现场值')
    bits = value.view(np.uint32)
    rounded = (bits + np.uint32(0x7fff) + ((bits >> 16) & np.uint32(1))) & np.uint32(0xffff0000)
    return rounded.view(np.float32)


def errors(actual, reference):
    difference = actual.astype(np.float64) - reference.astype(np.float64)
    absolute = np.abs(difference)
    return dict(max_abs=float(absolute.max()), mean_abs=float(absolute.mean()),
        rms_abs=float(np.sqrt(np.mean(difference * difference))),
        per_head_max_abs=absolute.max(axis=1).tolist(),
        per_head_mean_abs=absolute.mean(axis=1).tolist())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir', required=True, type=Path)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    args = parser.parse_args()
    folder = args.artifact_dir.resolve(strict=True)
    payload = folder / 'oracle-context.npz'
    metadata = json.loads((folder / 'oracle-context.json').read_text(encoding='utf-8'))
    if digest(payload) != EXPECTED_PAYLOAD or metadata['payload_sha256'] != EXPECTED_PAYLOAD:
        raise ValueError('只接受封存085500的固定QKV现场')
    cfg, length = metadata['config'], metadata['seq_len']
    if (length != 16504 or metadata['original_request_row'] != 2
            or cfg['causal'] is not True or cfg['sliding_window'] != [-1, -1]
            or cfg['alibi'] or cfg['sinks'] or cfg['softcap'] != 0 or cfg['quant_mode'] != 0
            or cfg['use_alibi_sqrt'] or cfg['chunk_lookback'] != -1
            or (cfg['query_heads'], cfg['kv_heads'], cfg['head_size']) != (16, 2, 128)):
        raise ValueError('不是本次已核普通q1因果scope')
    with np.load(payload, allow_pickle=False) as source:
        q, k, v = (decode(source[name]) for name in ('query_bf16_bits', 'key_bf16_bits', 'value_bf16_bits'))
        original = decode(source['original_output_bf16_bits'])
        permuted = decode(source['permuted_output_bf16_bits'])
    reference = np.load(args.reference, allow_pickle=False)
    if (q.shape != (16, 128) or k.shape != (length, 2, 128) or v.shape != k.shape
            or reference.shape != q.shape or reference.dtype != np.float32
            or not all(np.isfinite(a).all() for a in (q, k, v, original, permuted, reference))):
        raise ValueError('实际输入/reference形状或有限值不符')
    if args.output_dir.exists():
        raise ValueError('只写新的CPU结果目录')
    # 两支共享QK、M、alpha和未舍入P的FP32分母；只PV输入是否round-BF16不同。
    maximum = np.full(16, -np.inf, dtype=np.float32)
    denominator = np.ones(16, dtype=np.float32)
    accumulators = {name: np.zeros((16, 128), dtype=np.float32) for name in ('P_fp32', 'P_bf16_rne')}
    start = time.perf_counter()
    for offset in range(0, length, 64):
        count = min(64, length - offset)
        ktile = np.zeros((64, 2, 128), dtype=np.float32)
        vtile = np.zeros_like(ktile)
        ktile[:count], vtile[:count] = k[offset:offset + count], v[offset:offset + count]
        scores = np.empty((16, 64), dtype=np.float32)
        for group in range(2):
            heads = slice(group * 8, (group + 1) * 8)
            scores[heads] = q[heads] @ ktile[:, group].T
        scores *= np.float32(cfg['scale'])
        scores[:, count:] = -np.inf
        next_maximum = np.maximum(maximum, np.max(scores, axis=1))
        next_maximum = np.where(next_maximum > -np.inf, next_maximum, np.float32(0)).astype(np.float32)
        probability = np.exp(scores - next_maximum[:, None]).astype(np.float32, copy=False)
        alpha = np.exp(maximum - next_maximum).astype(np.float32, copy=False)
        denominator = denominator * alpha + np.sum(probability, axis=1, dtype=np.float32)
        for name, p in (('P_fp32', probability), ('P_bf16_rne', bf16_rne(probability))):
            accumulator = accumulators[name]
            accumulator *= alpha[:, None]
            for group in range(2):
                heads = slice(group * 8, (group + 1) * 8)
                accumulator[heads] += p[heads] @ vtile[:, group]
        maximum = next_maximum
    elapsed = time.perf_counter() - start
    branches = {}
    output_arrays = {}
    for name, accumulator in accumulators.items():
        pre_store = accumulator / denominator[:, None]
        stored = bf16_rne(pre_store)
        output_arrays[name + '_pre_store_fp32'] = pre_store
        output_arrays[name + '_output_bf16_rne_as_fp32'] = stored
        branches[name] = {stage: {target: errors(array, value) for target, value in (
            ('actual_original_2D', original), ('actual_P_GQA', permuted), ('existing_FP32_reference', reference))}
            for stage, array in (('pre_store_FP32', pre_store), ('same_BF16_RNE_output', stored))}
    args.output_dir.mkdir(parents=True)
    for name, array in output_arrays.items():
        np.save(args.output_dir / (name + '.npy'), array, allow_pickle=False)
    result = dict(status='CPU_single_variable_analysis_no_pass_threshold', run_id='20261023T085500Z',
        original_request_row=2, seq_len=length, tile_size=64, tiles=(length + 63) // 64,
        actual_scale=cfg['scale'], numerator_only_P_rounding=True, denominator='shared unrounded FP32 P',
        input_payload_sha256=EXPECTED_PAYLOAD, reference_file=str(args.reference),
        reference_sha256=digest(args.reference), numpy_version=np.__version__, elapsed_CPU_wall_seconds=elapsed,
        actual_original_vs_reference=errors(original, reference), actual_P_GQA_vs_reference=errors(permuted, reference),
        branches=branches, limitations=[
            'CPU source-level numerical model, not native GPU instruction or exact FMA/reduction reproduction.',
            'Only fixed T64 and one P rounding control; no parameter sweep, GPU run or operator modification.',
            'Similarity is evidence about a mechanism, not model accuracy or a pass verdict.'])
    (args.output_dir / 'result.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(dict(status=result['status'], elapsed_CPU_wall_seconds=elapsed, branches=branches)))


if __name__ == '__main__':
    main()
