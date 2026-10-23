"""固定422，仅普通Full/noSpec路径省accepted GPU fill；不启动设备。"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
BASE_MAP_SHA = '82514a24cebdb3ae8ce8eb1562049168fa158894364d1dd87ae4b4a724f66136'
RUNNER_PATH = 'vllm_fl/worker/model_runner.py'
INPUT_RUNNER = 'cc442e54e66c81f4375ac7b3311953441245f53bd0a576d27798528ce02e2663'
OUTPUT_RUNNER = '03a0e007e820644d55ac5eaf3331416da3fb0e58147a4f57928d363cc8ff6fb2'
PINS = {
    RUNNER_PATH: INPUT_RUNNER,
    'vllm_fl/patches/biv150_kv_worker.py': '2de7802d7b07d6f11c8e8f304df36d5503c1189cee9d4ad60f3fbc80fbb98a52',
    'vllm_fl/patches/biv150_kv_protocol.py': '91185a23dd56cc7b1d882e9b4b3ccbfdb0d491dce060e658b183ee563d04d3ab',
}

# 放在原initialize_kv_cache成功结束后；只读一次，异常保持原fill。
COLD_SCOPE = '''        # No accepted-count GPU consumer in this exact non-spec Full model.
        # Recompute after each cache initialization; profiling/unknown stays original.
        self._biv150_skip_accepted_gpu_fill = False
        try:
            import hashlib as _biv150_hashlib
            import sys as _biv150_sys
            from pathlib import Path as _biv150_Path
            _biv150_model = self.model_config
            _biv150_text = _biv150_model.hf_text_config
            _biv150_parallel = self.parallel_config
            _biv150_groups = self.kv_cache_config.kv_cache_groups
            _biv150_spec = (_biv150_groups[0].kv_cache_spec
                            if len(_biv150_groups) == 1 else None)
            _biv150_spec_module = _biv150_sys.modules.get(FullAttentionSpec.__module__)
            self._biv150_skip_accepted_gpu_fill = (
                is_profiling is False
                and getattr(current_platform, "vendor_name", None) == "iluvatar"
                and _biv150_Path(str(_biv150_model.model).rstrip("/\\\\")).name == "MiniCPM5-2B"
                and _biv150_model.dtype == torch.bfloat16
                and _biv150_model.quantization is None
                and (_biv150_text.hidden_size, _biv150_text.num_hidden_layers,
                     _biv150_text.num_attention_heads, _biv150_text.num_key_value_heads) == (2048, 42, 16, 2)
                and all(getattr(_biv150_parallel, _name, None) == 1 for _name in (
                    "tensor_parallel_size", "pipeline_parallel_size",
                    "decode_context_parallel_size", "data_parallel_size"))
                and _biv150_parallel.use_ubatching is False
                and self.speculative_config is None
                and self.vllm_config.speculative_config is None
                and _biv150_model.is_hybrid is False
                and _biv150_model.is_encoder_decoder is False
                and self.is_pooling_model is False and self.supports_mm_inputs is False
                and self.enable_prompt_embeds is False and self.lora_config is None
                and self.use_async_scheduling is True
                and self.use_async_spec_decode is False
                and self.num_spec_tokens == 0 and self.prev_num_spec_tokens == 0
                and self._draft_token_ids is None
                and self.valid_sampled_token_count_gpu is None
                and self.num_accepted_tokens_event is None
                and self.mamba_prev_last_scheduled_idx is None
                and self._mamba_bufs is None
                and type(_biv150_spec) is FullAttentionSpec
                and len(_biv150_groups[0].layer_names) == 42
                and (_biv150_spec.block_size, _biv150_spec.num_kv_heads,
                     _biv150_spec.head_size, _biv150_spec.dtype) == (16, 2, 128, torch.bfloat16)
                and self._kernel_block_sizes == [16]
                and _biv150_spec_module is not None
                and _biv150_spec_module.FullAttentionSpec is FullAttentionSpec
                and _biv150_hashlib.sha256(_biv150_Path(_biv150_spec_module.__file__).read_bytes()).hexdigest()
                    == "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003"
            )
            if self._biv150_skip_accepted_gpu_fill:
                print("BIV150_ACCEPTED_GPU_FILL_SKIP_ENABLED scope=non_spec_full cpu_fill_retained=1", flush=True)
        except Exception:
            self._biv150_skip_accepted_gpu_fill = False

'''


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def transform_runner(raw):
    if sha(raw) != INPUT_RUNNER:
        raise ValueError('只接受原422 cc442，不叠compute-order/H2D/425')
    edits = []
    def edit(old, new):
        nonlocal raw
        old, new = old.encode(), new.encode()
        if raw.count(old) != 1:
            raise ValueError('原422精确切口不唯一')
        raw = raw.replace(old, new, 1)
        edits.append((old, new))
    edit('        self.speculative_config = vllm_config.speculative_config\n',
         '        self.speculative_config = vllm_config.speculative_config\n'
         '        self._biv150_skip_accepted_gpu_fill = False\n')
    edit('            self.num_accepted_tokens.np.fill(1)\n'
         '            self.num_accepted_tokens.gpu.fill_(1)\n',
         '            self.num_accepted_tokens.np.fill(1)\n'
         '            if not self._biv150_skip_accepted_gpu_fill:\n'
         '                self.num_accepted_tokens.gpu.fill_(1)\n')
    edit('    def _get_attention_kv_cache_gid(self) -> int:\n',
         COLD_SCOPE + '    def _get_attention_kv_cache_gid(self) -> int:\n')
    original = raw
    for old, new in reversed(edits):
        if original.count(new) != 1:
            raise ValueError('逆回切口不唯一')
        original = original.replace(new, old, 1)
    if sha(original) != INPUT_RUNNER:
        raise ValueError('未精确逆回原runner')
    compile(raw, RUNNER_PATH, 'exec')
    return raw, edits


def mapping(folder):
    result = {}
    for p in sorted(folder.rglob('*')):
        rel = p.relative_to(folder)
        if any(x in ('.git', '__pycache__') for x in rel.parts) or p.suffix in ('.pyc', '.pyo'):
            continue
        if p.is_symlink() and (not p.resolve().is_file() or not p.resolve().is_relative_to(folder.resolve())):
            raise ValueError('拒绝外部/目录链接')
        if p.is_file():
            result[rel.as_posix()] = sha(p.read_bytes())
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--emit-only', action='store_true', help='仅三路径镜像，不可作为完整部署源')
    args = parser.parse_args()
    base, output = args.base.resolve(strict=True), args.output.resolve()
    map_raw = (HERE / 'base-source-sha256.json').read_bytes()
    expected = json.loads(map_raw)
    if sha(map_raw) != BASE_MAP_SHA or len(expected) != 422 or mapping(base) != expected:
        raise ValueError('固定422完整输入map变化')
    if output.exists() or output == base or output in base.parents or base in output.parents:
        raise ValueError('输出须新建且不与基点交叠')
    receipt = output.with_name(output.name + '-prepare.json')
    if receipt.exists():
        raise ValueError('禁止覆盖既有回执')
    originals = {name: (base / name).read_bytes() for name in PINS}
    if any(sha(originals[name]) != pin for name, pin in PINS.items()):
        raise ValueError('基点runner/worker/protocol身份变化')
    runner, edits = transform_runner(originals[RUNNER_PATH])
    if OUTPUT_RUNNER is None or sha(runner) != OUTPUT_RUNNER:
        raise ValueError('runner未冻结或输出身份变化')
    changes = {RUNNER_PATH: runner}
    for name in PINS:
        if name == RUNNER_PATH:
            continue
        raw = originals[name]
        if raw.count(INPUT_RUNNER.encode()) != 1:
            raise ValueError('worker/protocol原runner锁不唯一')
        changes[name] = raw.replace(INPUT_RUNNER.encode(), OUTPUT_RUNNER.encode(), 1)
        if changes[name].replace(OUTPUT_RUNNER.encode(), INPUT_RUNNER.encode(), 1) != raw:
            raise ValueError('runner身份锁逆回失败')
    for name, raw in changes.items():
        compile(raw, name, 'exec')
    if args.emit_only:
        output.mkdir(parents=True)
    else:
        shutil.copytree(base, output, ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc', '*.pyo'))
    for name, raw in changes.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
    after = {**expected, **{name: sha(raw) for name, raw in changes.items()}}
    if len(after) != 422 or mapping(base) != expected or mapping(output) != (
            {name: sha(raw) for name, raw in changes.items()} if args.emit_only else after):
        raise ValueError('完整输入/输出或三路径差异不符')
    info = dict(base_map_sha256=BASE_MAP_SHA, source_count=422, emit_only=args.emit_only,
        changed_paths={name: dict(before=expected[name], after=after[name]) for name in changes},
        runner_edits=[dict(before=a.decode(), after=b.decode()) for a, b in edits], output_map=after,
        limits='仅语法/完整map/精确逆回；未执行框架、GPU、数值或性能',
        new_gpu_storage_bytes=0, runtime_helper_added=False,
        observed_selection='ENABLED只为冷scope；实际prepare由同Engine既有CPU_METADATA_FIRST_SELECTED证明经过该处，不称GPU完成')
    with receipt.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'source_count': 422, 'runner': OUTPUT_RUNNER, 'receipt': str(receipt)}))


if __name__ == '__main__':
    main()
