"""独立CPU NumPy QK→FP32稳定softmax→PV；只输出原始误差，不设通过阈值。"""
import argparse
import hashlib
import json
from pathlib import Path


def read(folder, include_float64):
    import numpy as np
    meta = json.loads((folder / 'oracle-context.json').read_text(encoding='utf-8'))
    path = folder / 'oracle-context.npz'
    if meta['status'] != 'single_outside_context_captured' or hashlib.sha256(path.read_bytes()).hexdigest() != meta['payload_sha256']:
        raise ValueError('捕获状态/原始payload SHA不符')
    cfg, length = meta['config'], meta['seq_len']
    if (cfg['causal'] is not True or cfg['sliding_window'] != [-1, -1] or cfg['alibi'] or cfg['sinks']
            or cfg['softcap'] != 0 or cfg['use_alibi_sqrt'] or cfg['chunk_lookback'] != -1
            or cfg['quant_mode'] != 0 or cfg['cache_dtype'] not in ('auto', 'bfloat16')
            or (cfg['query_heads'], cfg['kv_heads'], cfg['head_size']) != (16, 2, 128)
            or meta['position'] != length - 1 or meta['visible_interval'] != [0, length]
            or not meta['actual_inputs_QKV_slots_seq_used_pages_bit_equal']
            or not meta['actual_effective_tables_equal'] or not meta['actual_cache_last_token_equals_observed_current_KV']):
        raise ValueError('独立oracle范围不明')
    with np.load(path, allow_pickle=False) as data:
        def bf16(name, shape):
            raw = data[name]
            if raw.dtype != np.int16 or raw.shape != shape:
                raise ValueError('BF16原bits形状/类型不符：' + name)
            return (raw.astype(np.uint16).astype(np.uint32) << 16).view(np.float32)
        query = bf16('query_bf16_bits', (16, 128))
        key, value = bf16('key_bf16_bits', (length, 2, 128)), bf16('value_bf16_bits', (length, 2, 128))
        original = bf16('original_output_bf16_bits', (16, 128))
        permuted = bf16('permuted_output_bf16_bits', (16, 128))
        pages = data['physical_pages'].copy()
    arrays = (query, key, value, original, permuted)
    if not all(np.isfinite(a).all() for a in arrays) or not np.isfinite(cfg['scale']) or cfg['scale'] <= 0:
        raise ValueError('实际输入/输出/scale非有限')
    if pages.shape != (meta['valid_pages'],) or pages.dtype != np.int64 or np.any(pages <= 0):
        raise ValueError('实际页表范围不符')
    def reference(dtype):
        output = np.empty((16, 128), dtype=dtype)
        q, k, v = query.astype(dtype), key.astype(dtype), value.astype(dtype)
        # 每8个Q heads共享1个KV head；不调用Triton/Attention/GQA，也不做分页算法复用。
        for group in range(2):
            scores = q[group * 8:(group + 1) * 8] @ k[:, group, :].T
            scores *= dtype(cfg['scale'])
            scores -= np.max(scores, axis=1, keepdims=True)
            weights = np.exp(scores).astype(dtype, copy=False)
            weights /= np.sum(weights, axis=1, keepdims=True, dtype=dtype)
            output[group * 8:(group + 1) * 8] = weights @ v[:, group, :]
        return output
    def errors(actual, expected):
        delta = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
        return dict(max_abs=float(delta.max()), mean_abs=float(delta.mean()),
            rms_abs=float(np.sqrt(np.mean(delta * delta))),
            max_relative_clamp_1e_6=float(np.max(delta / np.maximum(np.abs(expected), 1e-6))),
            per_head_max_abs=delta.max(axis=1).tolist(), per_head_mean_abs=delta.mean(axis=1).tolist())
    fp32 = reference(np.float32)
    result = dict(status='independent_CPU_reference_computed_no_pass_threshold', pid=meta['pid'],
        original_request_row=meta['original_request_row'], seq_len=length,
        context_payload_sha256=meta['payload_sha256'], numpy_version=np.__version__,
        reference='per8Qheads/oneKVhead; FP32 QK*actualscale, stable_softmax, FP32 PV',
        original_vs_fp32=errors(original, fp32), permuted_vs_fp32=errors(permuted, fp32),
        actual_outputs_difference=errors(permuted, original),
        original_phase_KV_separately_snapshotted=False, shared_context_basis=meta['shared_context_basis'],
        no_numerical_tolerance_or_accuracy_claim=True, no_performance_claim=True)
    fp64 = None
    if include_float64:
        fp64 = reference(np.float64)
        result.update(fp32_vs_fp64=errors(fp32, fp64), original_vs_fp64=errors(original, fp64),
            permuted_vs_fp64=errors(permuted, fp64))
    return result, fp32, fp64


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--float64', action='store_true', help='同一实际输入加CPU FP64 reference稳定性检查')
    args = parser.parse_args()
    fp32_path = args.output.with_name(args.output.stem + '-fp32.npy')
    fp64_path = args.output.with_name(args.output.stem + '-fp64.npy')
    if args.output.exists() or fp32_path.exists() or fp64_path.exists():
        raise ValueError('不覆盖已有结果')
    result, fp32, fp64 = read(args.artifact_dir.resolve(strict=True), args.float64)
    import numpy as np
    np.save(fp32_path, fp32, allow_pickle=False)
    result['fp32_reference_file'] = str(fp32_path)
    if fp64 is not None:
        np.save(fp64_path, fp64, allow_pickle=False)
        result['fp64_reference_file'] = str(fp64_path)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
