"""仅派生当前实际热点 N33/bucket40/S16；原 c62 包保持冻结。"""
import ast
import difflib
import hashlib
import json
from pathlib import Path
import shutil
import tarfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / "gqa-identity-rescale-20261025"


def replace(text, old, new):
    if text.count(old) != 1:
        raise ValueError("继承锚点不唯一：" + old[:70])
    return text.replace(old, new, 1)


def prepare():
    for name, expected in json.loads((BASE / "asset-pins.json").read_text()).items():
        if hashlib.sha256((BASE / name).read_bytes()).hexdigest() != expected:
            raise ValueError("冻结 v1 资产变化：" + name)
        if name not in ("prepare.py", "README.md", "check_cpu.py", "cpu-check.json", "branch-parser-check.json"):
            shutil.copyfile(BASE / name, HERE / name)
    entry = (BASE / "entry.py").read_text(encoding="utf-8")
    entry = replace(entry, '    parser.add_argument("--run-dir", type=Path)\n',
                    '    parser.add_argument("--run-dir", type=Path)\n'
                    '    parser.add_argument("--shape", choices=("hotspot", "b32"), default="hotspot")\n')
    entry = replace(entry, 'worker(args.run_dir, args.model)', 'worker(args.run_dir, args.model, args.shape)')
    entry = replace(entry, 'stamp + "-gqa-identity-rescale-component"',
                    'stamp + "-gqa-identity-rescale-v2-" + args.shape + "-component"')
    entry = replace(entry, '"--model", str(args.model)]', '"--model", str(args.model), "--shape", args.shape]')
    (HERE / "entry.py").write_bytes(entry.encode())
    old = (BASE / "worker.py").read_text(encoding="utf-8")
    text = replace(old, '"""真实 B32/16K GQA+原 reducer 组件；随机输入，非模型激活实采或官方成绩。"""',
                   '"""真实 N33/bucket40/S16 热点及原 B32/S4；每次独立组件，无模型激活或官方成绩。"""')
    text = replace(text, 'def worker(run, model):', 'def worker(run, model, shape="hotspot"):')
    text = replace(text, '"仅 B32/16K，split 仍由生产选择；不叠 affine/next-K"',
                   '"默认 N33/bucket40/S16，可显式选择原 B32/S4；split 由实际生产路由选择"')
    text = replace(text, '        B, L = 32, 16384\n', '''        if shape == "hotspot":
            B, active, segments = 40, 33, 16
        elif shape == "b32":
            B, active, segments = 32, 32, 4
        else:
            raise ValueError("未知 shape")
        L = 16384
''')
    text = replace(text, '        common.block_table_tensor = table.cuda()\n', '''        common.block_table_tensor = table.cuda()
        if active < B:
            # Actual runner: query_start_loc tail=last real token, lengths=0,
            # null block=0 (reserved), slot=-1, padded request/token counts=B.
            cache = torch.cat((torch.zeros_like(cache[:1]), cache), dim=0)
            common.block_table_tensor[:active, :L // 16].add_(1)
            common.block_table_tensor[active:].zero_()
            common.seq_lens[active:].zero_()
            common.query_start_loc_cpu.clamp_(max=active)
            common.query_start_loc.copy_(common.query_start_loc_cpu)
            common.slot_mapping[:active].add_(16)
            common.slot_mapping[active:].fill_(-1)
''')
    text = replace(text, '        impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)\n',
                   '''        impl.do_kv_cache_update(layer, key, value, cache, common.slot_mapping)
        if active < B and not bool((cache[0] == 0).all()):
            raise RuntimeError("padded slot=-1 或 null block 保留语义失配")
''')
    text = replace(text, '                    (32, 2, 4), (32, 16), 8, 4, 128, 16, 8192, 1, 1):',
                   '                    (B, 2, segments), (B, 16), 8, segments, 128, 16, 8192, 1, 1):')
    text = replace(text, 'raise RuntimeError("生产 B32/16K ABI 与已核 S4/page16/w1s1 不符")',
                   'raise RuntimeError("实际生产 ABI 未自然选中该 bucket 的 split/page16/w1s1")')
    text = replace(text, '        result["abi"] = dict(grid=grid, reducer_grid=rgrid, builder_segments=metadata.num_par_softmax_segments,',
                   '        result["abi"] = dict(shape=shape, active_requests=active, padded_bucket=B,\n'
                   '            grid=grid, reducer_grid=rgrid, builder_segments=metadata.num_par_softmax_segments,')
    text = replace(text, '            rows=8, segments=4, head_size=128, page_size=16, num_warps=1, num_stages=1)',
                   '            rows=8, segments=segments, head_size=128, page_size=16, num_warps=1, num_stages=1,\n'
                   '            query_start_loc=common.query_start_loc_cpu.tolist(), seq_lens=common.seq_lens.cpu().tolist(),\n'
                   '            padded_slot_values=common.slot_mapping[active:].cpu().tolist())')
    if text.count('.narrow(2, 0, 4)') != 3:
        raise ValueError("partial 前缀锚点数量不符")
    text = text.replace('.narrow(2, 0, 4)', '.narrow(2, 0, segments)')
    text = replace(text, '            failed_eager = [t.cpu() for t in b.tensors] if not checks["eager_bits"] else None\n',
                   '''            checks["padded_output_zero"] = all(bool((arm.out[active:B] == 0).all()) for arm in arms.values())
            checks["padded_partials_untouched"] = all(bool((t[active:B] == -17).all())
                for arm in arms.values() for t in (arm.partial, arm.maxima, arm.sums))
            failed_eager = [t.cpu() for t in b.tensors] if not checks["eager_bits"] else None
''')
    text = replace(text, '''        cache[0, 1].add_(0.5)
        common.block_table_tensor[0, :2].copy_(common.block_table_tensor[0, :2].flip(0))
''', '''        # row15 remains long in the ragged pattern; mutate pages it actually reads.
        changed_row = 15
        changed_page = changed_row * (L // 16) + (1 if active < B else 0)
        cache[changed_page, 1].add_(0.5)
        common.block_table_tensor[changed_row, :2].copy_(common.block_table_tensor[changed_row, :2].flip(0))
''')
    text = replace(text, '        ragged = [0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65, 4095, 4096, 4097, 16383, 16384] * 2\n',
                   '''        ragged_pattern = [0, 1, 15, 16, 17, 31, 32, 33, 63, 64, 65, 4095, 4096, 4097, 16383, 16384]
        ragged = [ragged_pattern[i % len(ragged_pattern)] for i in range(active)] + [0] * (B - active)
''')
    text = replace(text, '''        # 64=每split一页不能走skip；160=每split三页，其中最后一split只一页。
        # 以不同长度同时覆盖首轮/严格相等/尾页/空行，所有输入只在两臂之外更新。
        common.seq_lens.copy_(torch.tensor([0, 1, 15, 16, 17, 64, 160, 163] * 4,
                                           dtype=torch.int32, device="cuda"))
''', '''        # 按既定 split 造首页/三页/尾页边界，S16 也确实执行恒等快支。
        # B32/S4 的模式仍为原来的 0/1/15/16/17/64/160/163。
        boundary = [0, 1, 15, 16, 17, segments * 16, segments * 48 - 32, segments * 48 - 29]
        common.seq_lens.copy_(torch.tensor([boundary[i % 8] for i in range(active)] + [0] * (B - active),
                                           dtype=torch.int32, device="cuda"))
''')
    (HERE / "worker.py").write_bytes(text.encode())
    for name, before, after in (("owner", (BASE / "entry.py").read_text(encoding="utf-8"), entry),
                                ("worker", old, text)):
        (HERE / (name + ".diff")).write_bytes("".join(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
            fromfile="frozen-v1/" + name, tofile="hotspot-v2/" + name)).encode())
    for path in HERE.glob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def seal():
    names = sorted(p.name for p in HERE.iterdir() if p.is_file() and p.name not in ("entry.tar.gz", "asset-pins.json"))
    hashes = {n: hashlib.sha256((HERE / n).read_bytes()).hexdigest() for n in names}
    (HERE / "asset-pins.json").write_text(json.dumps(hashes, indent=2) + "\n")
    with tarfile.open(HERE / "entry.tar.gz", "w:gz") as tar:
        for name in [*names, "asset-pins.json"]:
            tar.add(HERE / name, arcname=name)
    print(json.dumps(dict(pins=len(names), bytes=(HERE / "entry.tar.gz").stat().st_size,
                         sha256=hashlib.sha256((HERE / "entry.tar.gz").read_bytes()).hexdigest())))


if __name__ == "__main__":
    prepare()
    seal()
