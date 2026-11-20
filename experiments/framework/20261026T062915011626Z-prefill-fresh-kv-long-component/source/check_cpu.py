"""检查生成核的整数地址与覆盖；不能替代GPU编译、数值或性能。"""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path
import sys
import prototype

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
source = (HERE / 'candidate.kernel.py').read_text(encoding='utf-8')
current = (HERE / 'current.kernel.py').read_text(encoding='utf-8')
assert source == prototype.transform(current)
writer = (ROOT / 'analysis/source/mixed-token-bucket/triton_reshape_and_cache_flash.py').read_bytes()
assert hashlib.sha256(writer).hexdigest() == 'f18224e51162e37c14a2e2b3045bca55baf0b207b1d203ad6ee7d8ed417139eb'
writer_text = writer.decode('utf-8')
assert 'else:\n        key_tile = key_load' in writer_text
assert 'else:\n        value_tile = value_load' in writer_text
tree = ast.parse(source)
fn = tree.body[0]
loop = next(x for x in ast.walk(fn) if isinstance(x, ast.For))
assigns = {x.targets[0].id: x.value for x in loop.body
           if isinstance(x, ast.Assign) and isinstance(x.targets[0], ast.Name)}


class Scalar(ast.NodeTransformer):
    """只去掉广播语法/.to；执行实际生成核的整数算式。"""
    def visit_Subscript(self, node):
        assert isinstance(node.slice, ast.Tuple)
        assert len(node.slice.elts) == 2
        assert all(isinstance(x, ast.Slice) or isinstance(x, ast.Constant) and x.value is None
                   for x in node.slice.elts)
        return self.visit(node.value)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Attribute) and node.func.attr == 'to':
            assert len(node.args) == 1
            return self.visit(node.func.value)
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            assert node.func.value.id == 'tl' and node.func.attr == 'maximum'
            return ast.Call(func=ast.Name(id='max', ctx=ast.Load()),
                            args=[self.visit(x) for x in node.args], keywords=[])
        raise AssertionError('非整数合同表达式')


codes = {}
for name in ('valid_key', 'fresh_lane', 'history_lane', 'fresh_row',
             'k_offset', 'v_offset', 'fresh_k_offset', 'fresh_v_offset'):
    node = Scalar().visit(ast.parse(ast.unparse(assigns[name]), mode='eval'))
    codes[name] = compile(ast.fix_missing_locations(node), '<generated-integer-' + name + '>', 'eval')
load = assigns['physical_block_idx'].func.value
assert isinstance(load, ast.Call) and isinstance(load.func, ast.Attribute) and load.func.attr == 'load'
assert ast.dump(next(x.value for x in load.keywords if x.arg == 'mask')) == ast.dump(ast.Name(id='history_lane', ctx=ast.Load()))
assert next(x.value.value for x in load.keywords if x.arg == 'other') == 0


def get(name, values):
    return eval(codes[name], {'__builtins__': {}, 'max': max}, values)


cases = lanes = mixed = address_samples = invalid = 0
qstarts = (0, 1, 18, 99)
for ctx in (0, 1, 15, 16, 17, 31, 63, 64, 65, 127, 14337):
    for q in (1, 15, 16, 17, 63, 64, 65, 2047, 2048):
        length = ctx + q
        start = qstarts[cases % len(qstarts)]
        # 逐序列页号均不连续；原writer的真实slot等于table[t//16]*16+t%16。
        page_count = (length + 15) // 16
        pages = [1009 + (page_count - i) * 7 for i in range(page_count)]
        assert min(pages) >= 0 and len(set(pages)) == page_count
        tile_count = (length + 63) // 64
        for tile in range(tile_count):
            tile_sources = set()
            for t in range(tile * 64, tile * 64 + 64):
                env = dict(seq_offset=t, seq_len=length, context_len=ctx,
                           cur_batch_in_all_start_index=start, tile_mask=t < length)
                for name in ('valid_key', 'fresh_lane', 'history_lane', 'fresh_row'):
                    env[name] = get(name, env)
                valid, fresh, history = (env[n] for n in ('valid_key', 'fresh_lane', 'history_lane'))
                assert (int(fresh) + int(history)) == int(valid)
                assert not (fresh and history)
                if not valid:
                    invalid += 1
                    assert not history and not fresh
                    continue
                lanes += 1
                tile_sources.add('fresh' if fresh else 'history')
                page = pages[t // 16]
                if fresh:
                    row = start + t - ctx
                    assert env['fresh_row'] == row and start <= row < start + q
                    # 当前页的旧prefix与新slot可以共存，来源按token而非整页选择。
                    original_written_source_row = start + ((page * 16 + t % 16) - page * 16 + (t // 16) * 16) - ctx
                    assert original_written_source_row == row
                else:
                    assert t < ctx
                # 每个tile首/末有效lane和ctx边界邻域，执行实际生成offset算式。
                if t % 64 not in (0, 63) and t not in (ctx - 1, ctx, ctx + 1, length - 1):
                    continue
                for token_stride in (256, 2560):
                    for head in (0, 1):
                        for dim in (0, 63, 127):
                            e = dict(env, physical_block_idx=page if history else 0,
                                kv_head_idx=head, offs_d=dim, BLOCK_SIZE=16,
                                stride_k_cache_0_i64=8192, stride_k_cache_1_i64=256,
                                stride_k_cache_2_i64=128, stride_k_cache_3=1,
                                stride_v_cache_0_i64=8192, stride_v_cache_1_i64=256,
                                stride_v_cache_2_i64=128, stride_v_cache_3=1,
                                fresh_k_stride_0_i64=token_stride, fresh_k_stride_1_i64=128,
                                fresh_k_stride_2_i64=1, fresh_v_stride_0_i64=token_stride + 256,
                                fresh_v_stride_1_i64=128, fresh_v_stride_2_i64=1)
                            if history:
                                expected = page * 8192 + (t % 16) * 256 + head * 128 + dim
                                assert get('k_offset', e) == expected
                                assert get('v_offset', e) == expected
                            else:
                                row = start + t - ctx
                                assert get('fresh_k_offset', e) == row * token_stride + head * 128 + dim
                                assert get('fresh_v_offset', e) == row * (token_stride + 256) + head * 128 + dim
                            address_samples += 1
            mixed += int(len(tile_sources) == 2)
        # 原绝对tile下每个query都读到其causal上界，没有重锚定fresh块。
        for row in range(q):
            block = row // 16
            prefix = min(length, ctx + block * 16 + 16)
            assert ctx + row + 1 <= prefix <= length
            assert row % 16 in range(16)
            assert (ctx + row) // 64 < (prefix + 63) // 64
        cases += 1

# ragged三序列的raw行以自己的cu为原点；零长度虚拟CTA应沿原早退。
lengths, contexts = (17, 1, 65), (1, 14337, 63)
cu = [0]
for length in lengths:
    cu.append(cu[-1] + length)
for i, (q, ctx) in enumerate(zip(lengths, contexts)):
    assert [cu[i] + t - ctx for t in range(ctx, ctx + q)] == list(range(cu[i], cu[i + 1]))
assert 'if q_block_local_idx * BLOCK_Q >= cur_batch_query_len:\n        return' in source
assert not ({'torch', 'triton', 'vllm'} & set(sys.modules))
result = dict(status='CPU整数/源码合同通过；未GPU', cases=cases, valid_lanes=lanes,
    invalid_masked_lanes=invalid, mixed_source_tiles=mixed, actual_offset_samples=address_samples,
    ragged_sequences=3, raw_token_strides=[256,2560], original_KV_page=16, original_compute_tile=64,
    source_exact_inverse=True, no_LPT=True, original_FP_body_unchanged=True,
    gpu_compile=False, gpu_numerics=False, performance=None,
    candidate_sha256=hashlib.sha256(source.encode()).hexdigest(),
    BF16_writer_source_sha256=hashlib.sha256(writer).hexdigest(),
    BF16_writer_non_FP8_branch='原值load/store，无scale或反量化；实际writer逐位门仍待GPU')
(HERE / 'cpu-check.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
