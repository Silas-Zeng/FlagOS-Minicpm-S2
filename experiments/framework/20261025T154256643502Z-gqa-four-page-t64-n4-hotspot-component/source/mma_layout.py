"""固定 T64/W4 的私有 JIT MMA N 方向布局；仅组件，无生产 hook。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import re


OLD = '#mma = #ttg.iluvatar_mma<{versionMajor = 1, versionMinor = 0, warpsPerCTA = [4, 1], instrShape = [16, 16, 16]}>'
NEW = OLD.replace('[4, 1]', '[1, 4]')


def layout_proof(ir, wanted):
    """只认本次真实 W4 的唯一 MMA；保留两处 P→opA 转换和全部 dot。"""
    aliases = re.findall(r'^#\w+ = #ttg\.iluvatar_mma<[^\n]+$', ir, re.M)
    dots = [line for line in ir.splitlines() if ' = tt.dot ' in line]
    conversions = [line for line in ir.splitlines() if ' = ttg.convert_layout ' in line
                   and 'tensor<8x64xbf16, #mma> -> tensor<8x64xbf16, #ttg.dot_op<' in line]
    valid = (aliases == [wanted] and '"ttg.num-warps" = 4 : i32' in ir
             and len(dots) == 4 and len(conversions) == 2
             and sum('-> tensor<8x64xf32, #mma>' in line for line in dots) == 2
             and sum('-> tensor<8x128xf32, #mma>' in line for line in dots) == 2
             and all('parent = #mma' in line for line in dots + conversions))
    if not valid:
        raise ValueError('不符唯一 8-row/T64/W4 MMA 与 P 转换闭合结构')
    return dict(mma_alias=aliases[0], num_warps=4, dot_count=len(dots),
                probability_layout_conversions=len(conversions), mechanism_pass=True)


def transform_ir(ir):
    layout_proof(ir, OLD)
    changed = ir.replace(OLD, NEW, 1)
    if changed.replace(NEW, OLD, 1) != ir:
        raise AssertionError('除 MMA warp 别名外 IR 发生变化')
    layout_proof(changed, NEW)
    return changed


class PrivateOverride:
    """复用 QFragment 的实例 compile/ir_override 链；任何失败直接向外抛出。"""
    def __init__(self, kernel, device, folder):
        self.kernel, self.folder = kernel, Path(folder)
        self.folder.mkdir(exist_ok=False)
        self.entry = kernel.device_caches[device]  # 先建立真实 binder，再读取 compile。
        self.original_compile = kernel.compile
        self.selected = {}
        self.records = []
        kernel.compile = self.compile

    def compile(self, src, target=None, options=None, _env_vars=None):
        record = dict(status='preparing', target=str(target))
        self.records.append(record)
        try:
            if (src.fn is not self.kernel or options.get('ir_override') is not None
                    or (options.get('num_warps'), options.get('num_stages')) != (4, 1)):
                raise ValueError('仅允许候选私有 W4/S1 原编译入口')
            normal = self.original_compile(src, target=target, options=options, _env_vars=_env_vars)
            original = normal.asm['ttgir']
            changed = transform_ir(original)
            sha = hashlib.sha256(changed.encode()).hexdigest()
            override = self.folder / ('mma-n4-' + sha + '.ttgir')
            override.write_text(changed, encoding='utf-8', newline='\n')
            (self.folder / ('normal-' + sha + '.ttgir')).write_text(original, encoding='utf-8', newline='\n')
            record.update(normal_hash=normal.hash, original_ir_sha256=hashlib.sha256(original.encode()).hexdigest(),
                          override_sha256=sha, override_file=override.name)
            replacement = dict(options, ir_override=str(override))
            compiled = self.original_compile(src, target=target, options=replacement, _env_vars=_env_vars)
            proof = layout_proof(compiled.asm['ttgir'], NEW)
            if (compiled.hash == normal.hash or compiled.src.signature != src.signature
                    or compiled.src.constants != src.constants or compiled.src.attrs != src.attrs):
                raise ValueError('候选编译身份或 ABI 不符')
            if hashlib.sha256(override.read_bytes()).hexdigest() != sha:
                raise ValueError('编译期间 override 内容变化')
            record.update(status='selected', compiled_hash=compiled.hash, proof=proof)
            self.selected[compiled.hash] = record
            return compiled
        except BaseException as error:
            record.update(status='failed', error=repr(error))
            raise
        finally:
            (self.folder / 'evidence.json').write_text(json.dumps(self.records, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    def verify(self, compiled):
        if compiled.hash not in self.selected:
            raise RuntimeError('实际 eager/Graph launch 未使用本次选中的 MMA N4 产物')

    def restore(self):
        self.kernel.compile = self.original_compile
