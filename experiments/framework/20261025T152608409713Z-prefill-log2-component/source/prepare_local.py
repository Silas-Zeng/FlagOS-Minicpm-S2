"""从已受测 head-major 组件复用真实 ABI/输入/数值/计时；仅在 CPU 生成新包。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / "head-major-paged-prefill-20261025"

def save(name, text):
    (HERE / name).write_bytes(text.encode("utf-8"))

def once(text, old, new):
    assert text.count(old) == 1, old[:100]
    return text.replace(old, new, 1)

def cut(text, start, end, replacement=""):
    assert text.count(start) == text.count(end) == 1
    a, b = text.index(start), text.index(end)
    return text[:a] + replacement + text[b:]

assets = ["base-source-manifest.json", "base-source-sha256.json", "dispatch_bootstrap.py",
    "distributed_bootstrap.py", "legacy_gate.py", "monitor_gpu.sh", "source_identity.py",
    "validate_block_table_candidate.py", "validate_hidden_row_gather.py", "validate_mixed_decode.py"]
for name in assets:
    (HERE / name).write_bytes((OLD / name).read_bytes())
owner_old = (OLD / "entry.py").read_text(encoding="utf-8")
owner = owner_old.replace("head-major-paged-prefill-component", "prefill-log2-component")
owner = owner.replace("固定三臂同一个", "固定两臂同一个")
save("entry.py", owner)
save("owner.diff", "".join(difflib.unified_diff(owner_old.splitlines(True), owner.splitlines(True),
    fromfile="受测head-major/entry.py", tofile="prefill-log2/entry.py")))

old = (OLD / "worker.py").read_text(encoding="utf-8")
w = once(old, '"""一个真实 M2047/KV16K 分页 Attention 三臂组件；只由设备 owner 启动。"""',
    '"""真实 M2047/KV16K normalized+Q-hoist 对 log2 同形状组件。"""')
w = once(w, 'ORIGINAL_SHA = "eef0202e6c0ed08bef8098adede1a603c63354c54b54a19414e210b675157265"\n', 'import prototype\n')
w = once(w, 'ARMS = ("current", "flaggems_original", "page16_rows_n64")', 'ARMS = ("current", "log2")')
w = cut(w, 'def fg_arguments(', 'def writer_exact(')
w = once(w, 'kind="真实三臂 kernel 组件；无模型权重/官方性能结论"',
    'kind="真实同形状 prefill kernel 组件；无模型权重/官方性能结论"')
w = once(w, 'candidate="FlagGems head-major：新 page16 行式 load＋N64；两个变化合并计为一个方法"',
    'candidate="原 normalized+Q-hoist 的 score/M 改 log2 域并直接 exp2；tile/地址/页序不变"')
w = once(w, '"原库/候选逆序分块与当前归约顺序不同，BF16 不要求跨臂逐位相同。"',
    '"换底改变 FP32 舍入，跨臂不要求逐位；BF16 P转换与原归约拓扑保留。"')
w = once(w, '"计时包括各臂实际 launch wrapper 与 LSE 写出；固定共同写KV/metadata成本未计入差额。"',
    '"计时两臂直接已暖 Q-hoist 私有 JIT 的完整2D输出；共同writer/metadata不计差额。"')
w = once(w, '"全臂同一输入缓存/进程；不声称省了8倍KV，M2047均约256 CTA。"',
    '"两臂同输入缓存/进程/ABI，既无affine/next-K，也不扩大tile或减少KV字节。"')
w = once(w, '    manager = capture = None', '    manager = capture = candidate_manager = None')
w = cut(w, '        original = importlib.import_module("flag_gems.ops.flash_kernel")',
    '        require(torch.cuda.device_count() == 1,',
    '''        helpers = importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
        raw_log2, source_log2 = prototype.build(attention, manager, helpers)
        require(source_log2 == Path(__file__).with_name("candidate.kernel.py").read_text(encoding="utf-8"),
                "运行时变换与封包的唯一候选源码不一致")
        candidate_manager = prototype.private_manager(raw_log2, attention, backend, qmod)
        (run / "candidate.kernel.py").write_text(source_log2, encoding="utf-8")
        import inspect
        (run / "current.kernel.py").write_text(inspect.getsource(manager.raw.fn), encoding="utf-8")
''')
w = cut(w, '        kw_b = fg_arguments(', '        torch.cuda.synchronize()\n        result.pop("compiling_arm", None)',
    '''        kw_b = dict(current_kwargs, output_ptr=outputs["log2"][:M])
        require(qmod._eligible(kw_a) and qmod._eligible(kw_b), "不属于已限定普通causal/BF16无sink等scope")
        # 先由原私有编译链生成并证明两臂Q-hoist，再直接调用同一已暖JIT；
        # Graph capture不经外层wrapper的保守fallback，避免回放另一套内核。
        compiled_a = manager.wrapper[grid](**kw_a)
        compiled_b = candidate_manager.wrapper[grid](**kw_b)
        require(compiled_a.hash in manager.optimized and compiled_b.hash in candidate_manager.optimized,
                "两臂必须真实命中Q-hoist；不能带fallback进入对照")
        calls = dict(current=lambda: manager.candidate[grid](**kw_a),
                     log2=lambda: candidate_manager.candidate[grid](**kw_b))
        result["configs"] = {name: dict(BLOCK_M=128, BLOCK_Q=16, TILE_SIZE=64,
            num_warps=8, num_stages=1) for name in ARMS}
        result["ir"]["current"] = preserve(compiled_a, run / "ir-current", qmod)
        result["ir"]["log2"] = preserve(compiled_b, run / "ir-log2", qmod)
        result["q_hoist"] = {"current": manager.optimized[compiled_a.hash]["mechanism"],
            "log2": candidate_manager.optimized[compiled_b.hash]["mechanism"]}
        result["machine_diagnostic"] = {"current": prototype.machine_summary(compiled_a),
            "log2": prototype.machine_summary(compiled_b)}
        active_arms = list(ARMS)
        expected_hashes = {"current": compiled_a.hash, "log2": compiled_b.hash}
        for name in active_arms:
            require(calls[name]().hash == expected_hashes[name], "直接JIT没有复用已核编译产物")
''')
w = once(w, '        result.pop("compiling_arm", None)\n', '')
w = once(w, '        initial = {name: out.clone() for name, out in outputs.items()}',
    '''        require(torch.equal(initial_output[:M].view(torch.int16), outputs["current"][:M].view(torch.int16)),
                "新直接基准调用与原生产forward结果不一致")
        initial = {name: out.clone() for name, out in outputs.items()}''')
w = once(w, '                calls[name]()\n            graphs[name] = graph',
    '''                captured = calls[name]()
            require(captured.hash == expected_hashes[name], "Graph capture使用了非指定Q-hoist产物")
            graphs[name] = graph''')
w = cut(w, '        # 原始N32/current、候选N64/current分别ABBA；',
    '        order = [(group, name)',
    '''        # 原同形状完整producer单ABBA；无独有的输入变换或计时外计算。
        groups = [("candidate", "log2")]
''')
w = w.replace('"三臂计时期间共同DB变化"', '"两臂计时期间共同DB变化"')
w = w.replace('decision="组件信号；是否进入模型集成由root按数值、资源、原库与当前双重差额决定"',
    'decision="组件信号；实际机器码仅诊断，净正才由root决定模型后继；负则收口"')
w = once(w, '        write(run / "results.json", result)\n    return 0',
    '''        if candidate_manager is not None:
            result["candidate_manager"] = candidate_manager.snapshot()
            candidate_manager.restore()
        write(run / "results.json", result)
    return 0''')
save("worker.py", w)
save("worker.diff", "".join(difflib.unified_diff(old.splitlines(True), w.splitlines(True),
    fromfile="受测head-major/worker.py", tofile="prefill-log2/worker.py")))

# 新增范围CPU检查；不重跑旧owner/原输入suite。
for name in ("prototype.py", "worker.py", "entry.py", "prepare_local.py"):
    ast.parse((HERE / name).read_text(encoding="utf-8"), filename=name)
original_ast, current_ast = ast.parse(old), ast.parse(w)
for name in ("sampled_oracle", "writer_exact", "preserve"):
    a = next(n for n in original_ast.body if isinstance(n, ast.FunctionDef) and n.name == name)
    b = next(n for n in current_ast.body if isinstance(n, ast.FunctionDef) and n.name == name)
    assert ast.dump(a, include_attributes=False) == ast.dump(b, include_attributes=False)
assert "affine_pages_ptr" not in w and "next_k" not in w
assert 'calls[name]().hash == expected_hashes[name]' in w
assert 'captured.hash == expected_hashes[name]' in w
import prototype
frozen = HERE.parent / "experiment-pr24-phase-20261024/experiments/accuracy/20261025T123523Z-team-main0915-math500/source/installed/vllm/v1/attention/ops"
def extract(path, name):
    text = path.read_text(encoding="utf-8")
    fn = next(n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef) and n.name == name)
    start = min([fn.lineno] + [n.lineno for n in fn.decorator_list])
    return "\n".join(text.splitlines()[start-1:fn.end_lineno]) + "\n"
assert hashlib.sha256((frozen / "triton_unified_attention.py").read_bytes()).hexdigest() == "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
assert hashlib.sha256((frozen / "triton_attention_helpers.py").read_bytes()).hexdigest() == prototype.HELPERS_SHA
kernel = extract(frozen / "triton_unified_attention.py", "kernel_unified_attention")
kernel = once(kernel, "def kernel_unified_attention(", "def kernel_biv150_prefill_normalized(")
kernel = once(kernel, "L = tl.full([BLOCK_M], 1.0, dtype=tl.float32)", "L = tl.zeros([BLOCK_M], dtype=tl.float32)")
helper = extract(frozen / "triton_attention_helpers.py", "softmax_step")
candidate = prototype.transform(kernel, helper)
save("current.kernel.py", kernel)
save("candidate.kernel.py", candidate)
save("kernel.diff", "".join(difflib.unified_diff((helper+"\n\n"+kernel).splitlines(True), candidate.splitlines(True),
    fromfile="current-normalized-plus-helper", tofile="log2-normalized-plus-helper")))
save("cpu-results.json", json.dumps(dict(status="CPU新增接线通过，未GPU",
    checks=["4文件AST", "原FP64/writer/preserve AST复用", "两臂Q-hoist与直接JIT及Graph哈希接线", "无affine/next-K", "原54c/59d9源身份", "数值变换逐字逆回原kernel/helper"],
    source="复用已受测head-major的原M2047/KV16K合成输入和5e-4/.01合同"), ensure_ascii=False, indent=2) + "\n")
print("CPU worker prepared")
