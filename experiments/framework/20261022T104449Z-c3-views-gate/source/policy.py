"""默认关闭的 C3 重复 view 清理；数学/scale/两次 Attention 调用不变。"""
from __future__ import annotations

import ast
import copy
import functools
import hashlib
from pathlib import Path
import sys


EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_C3 = "a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42"


def _source(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError("未审计源码: " + str(path))
    return data.decode("utf-8")


def _backend_tree(source):
    cls, = [node for node in ast.parse(source).body
            if isinstance(node, ast.ClassDef) and node.name == "TritonAttentionImpl"]
    original, = [node for node in cls.body
                 if isinstance(node, ast.FunctionDef) and node.name == "forward"]
    if original.decorator_list or original.args.kwarg is not None:
        raise RuntimeError("原 backend forward 挂点改变")
    changed = copy.deepcopy(original)
    restored_nodes = []
    unbinds = []
    for node in ast.walk(changed):
        if (isinstance(node, ast.Assign) and isinstance(node.value, ast.Call)
                and ast.unparse(node.value) == "kv_cache.unbind(1)"):
            if ast.unparse(node.targets[0]) != "(key_cache, value_cache)":
                raise RuntimeError("未知 KV unbind 目标")
            unbinds.append(node)
            restored_nodes.append((node, "value", copy.deepcopy(node.value)))
            node.value = ast.Name("_biv_pair", ast.Load())
    calls = [node for node in ast.walk(changed)
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
             and node.func.id == "unified_attention"]
    if len(unbinds) != 2 or len(calls) != 1:
        raise RuntimeError("原 backend view 数量改变")
    for name, var in (("q", "query"), ("out", "output")):
        kw, = [node for node in calls[0].keywords if node.arg == name]
        if ast.unparse(kw.value) != var + "[:num_actual_tokens]":
            raise RuntimeError("原 backend 全段 slice 改变")
        restored_nodes.append((kw, "value", copy.deepcopy(kw.value)))
        kw.value = ast.Name(var, ast.Load())
    # 精确反向证明：除上述四个 AST 值，不改其余分支、scale 或 kwargs。
    forward_new = copy.deepcopy(changed)
    for node, attr, value in restored_nodes:
        setattr(node, attr, value)
    if ast.dump(changed, include_attributes=False) != ast.dump(original, include_attributes=False):
        raise RuntimeError("backend AST 反向恢复失败")
    forward_new.name = "_biv_forward_no_full_views"
    forward_new.args.kwonlyargs.append(ast.arg(arg="_biv_pair"))
    forward_new.args.kw_defaults.append(None)
    return ast.fix_missing_locations(ast.Module(body=[forward_new], type_ignores=[]))


def _compile_backend(source, globals_dict, filename):
    local = {}
    exec(compile(_backend_tree(source), filename, "exec"), globals_dict, local)
    result = local["_biv_forward_no_full_views"]
    if result.__globals__ is not globals_dict:
        raise RuntimeError("原 backend 动态 globals 没有保留")
    return result


class Manager:
    def __init__(self, attention, helpers, backend):
        source = _source(backend.__file__, EXPECTED_BACKEND)
        _source(attention.__file__, EXPECTED_ATTENTION)
        _source(helpers.__file__, EXPECTED_HELPERS)
        self.backend, self.attention = backend, attention
        self.original_forward = backend.TritonAttentionImpl.forward
        original = self.original_forward
        c3_globals = original.__globals__
        self.c3 = sys.modules.get(c3_globals.get("__name__"))
        if self.c3 is None or vars(self.c3) is not c3_globals:
            raise RuntimeError("未找到原 C3 模块")
        _source(self.c3.__file__, EXPECTED_C3)
        base = getattr(original, "__wrapped__", None)
        builder = backend.TritonAttentionMetadataBuilder.build
        if (not getattr(original, self.c3._MARKER, False)
                or builder.__globals__ is not c3_globals
                or not getattr(builder, self.c3._MARKER, False)
                or base is None or base.__globals__ is not vars(backend)
                or Path(base.__code__.co_filename).resolve() != Path(backend.__file__).resolve()
                or original.__closure__ is None
                or dict(zip(original.__code__.co_freevars,
                            (cell.cell_contents for cell in original.__closure__))).get("original_forward") is not base
                or backend.unified_attention is not attention.unified_attention
                or attention.unified_attention.__globals__ is not vars(attention)
                or attention.current_platform.vendor_name != "iluvatar"
                or attention.is_batch_invariant):
            raise RuntimeError("C3/backend 实际调用链不匹配")
        self.c3._require_fast_runtime(attention)
        if ("run" in vars(attention.kernel_unified_attention.original)
                or "run" in vars(attention.reduce_segments)):
            raise RuntimeError("C3 view 短门不叠加 JIT run 候选")
        self.torch = backend.torch
        self.fast_forward = _compile_backend(source, base.__globals__, base.__code__.co_filename)
        self.active = False
        self.counts = {"selected_calls": 0, "fallback_calls": 0}
        self.wrapper = self._make_wrapper()

    def _eligible(self, impl, layer, query, key, value, cache, metadata, output,
                  output_scale, output_block_scale):
        if (type(impl) is not self.backend.TritonAttentionImpl
                or not all(type(tensor) is self.torch.Tensor for tensor in (query, key, value, cache, output))
                or metadata is None):
            return False
        plan = getattr(metadata, self.c3._PLAN, None)
        if (type(plan) is not self.c3._SplitPlan
                or type(plan.prefix_tokens) is not int or type(plan.total_tokens) is not int
                or not 0 < plan.prefix_tokens < plan.total_tokens
                or plan.total_tokens != metadata.num_actual_tokens
                or plan.decode.num_actual_tokens != plan.prefix_tokens
                or plan.prefill.num_actual_tokens != plan.total_tokens - plan.prefix_tokens
                or not self.c3._metadata_eligible(plan.decode)
                or not self.c3._metadata_eligible(plan.prefill)):
            return False
        return (self.c3._impl_eligible(impl, self.backend, self.torch, query, key, value, cache,
                                       metadata, output, output_scale, output_block_scale)
                and not self.torch.cuda.is_current_stream_capturing())

    def _make_wrapper(self):
        manager = self

        @functools.wraps(self.original_forward)
        def forward(impl, layer, query, key, value, kv_cache, attn_metadata, output,
                    output_scale=None, output_block_scale=None):
            selected = False
            try:
                selected = manager._eligible(impl, layer, query, key, value, kv_cache, attn_metadata,
                                              output, output_scale, output_block_scale)
            except Exception:
                pass
            if not selected:
                manager.counts["fallback_calls"] += 1
                # 原方法必须在 guard except 外调用，保留原异常 context。
                return manager.original_forward(impl, layer, query, key, value, kv_cache,
                                                attn_metadata, output, output_scale=output_scale,
                                                output_block_scale=output_block_scale)
            plan = getattr(attn_metadata, manager.c3._PLAN)
            plan.prepare_consumer(manager.torch)
            boundary, total = plan.prefix_tokens, plan.total_tokens
            # 原调用顺序：先 decode 视图及调用，后创建 prefill 视图。
            # K/V tensor 在已审 decoder 分支不被读取，保持原对象无需切片。
            decode_q, decode_out = query[:boundary], output[:boundary]
            pair = kv_cache.unbind(1)
            manager.fast_forward(impl, layer, decode_q, key, value, kv_cache, plan.decode, decode_out,
                                 output_scale=output_scale, output_block_scale=output_block_scale,
                                 _biv_pair=pair)
            manager.fast_forward(impl, layer, query[boundary:total], key, value, kv_cache,
                                 plan.prefill, output[boundary:total], output_scale=output_scale,
                                 output_block_scale=output_block_scale, _biv_pair=pair)
            manager.counts["selected_calls"] += 1
            return output

        return forward

    def install(self):
        if self.active:
            return
        if self.backend.TritonAttentionImpl.forward is not self.original_forward:
            raise RuntimeError("不能覆盖其他 forward 改动")
        self.backend.TritonAttentionImpl.forward = self.wrapper
        self.active = True

    def restore(self):
        if not self.active:
            return
        if self.backend.TritonAttentionImpl.forward is not self.wrapper:
            raise RuntimeError("不能覆盖其他 forward 改动")
        self.backend.TritonAttentionImpl.forward = self.original_forward
        self.active = False

    def snapshot(self):
        return dict(self.counts)


def create(attention, helpers, backend):
    return Manager(attention, helpers, backend)
