"""默认关闭：仅复用 Attention 完成 binder 后的热 key 配方。

不跳过原参数绑定、FlagPrism、globals 校验、C2 或当前 stream 获取。
create 不安装；只供独立两形状门使用，尚无设备/服务收益结论。
"""
from __future__ import annotations

import ast
import copy
import hashlib
import inspect
from pathlib import Path
import types


EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_JIT = "66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775"
EXPECTED_COMPILER = "a97f067023873acf2e348c28f61494e59170ca84c3ee2314f20e491d3e833dfd"


def _require_file(path, expected):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError("未审计源码: " + str(path))
    return data.decode("utf-8")


def _method_tree(source):
    cls, = [node for node in ast.parse(source).body
            if isinstance(node, ast.ClassDef) and node.name == "JITFunction"]
    run, = [node for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name == "run"]
    if run.decorator_list:
        raise RuntimeError("run 出现未知 decorator")
    return run


def _factory_tree(source):
    """只插两处 callback；删除新增节点后 AST 必须精确回原 run。"""
    original = _method_tree(source)
    run = copy.deepcopy(original)
    binder_at = [i for i, node in enumerate(run.body)
                 if isinstance(node, ast.Assign)
                 and ast.unparse(node.targets[0]) == "(bound_args, specialization, options)"]
    if len(binder_at) != 1 or ast.unparse(run.body[-1]) != "return kernel":
        raise RuntimeError("原 run 挂点不匹配")
    if any(isinstance(node, ast.Name) and node.id.startswith("_biv_")
           for node in ast.walk(run)):
        raise RuntimeError("原 run 已含候选名字")
    inserted = ast.parse(
        "_biv_options = options\n"
        "_biv_kernel = _biv_probe(self, grid, warmup, device, stream, bound_args, specialization, options)\n"
        "if _biv_kernel is not None:\n    return _biv_kernel\n").body
    record = ast.parse(
        "_biv_record(self, kernel, device, warmup, bound_args, specialization, _biv_options, key)\n").body
    at = binder_at[0] + 1
    run.body[at:at] = inserted
    run.body[-1:-1] = record
    reversed_run = copy.deepcopy(run)
    del reversed_run.body[-2]
    del reversed_run.body[at:at + len(inserted)]
    if ast.dump(reversed_run, include_attributes=False) != ast.dump(original, include_attributes=False):
        raise RuntimeError("run 反向恢复失败")
    factory = ast.parse("def _biv_factory(_biv_probe, _biv_record):\n    pass\n").body[0]
    factory.body = [run, ast.Return(ast.Name("run", ast.Load()))]
    return ast.fix_missing_locations(ast.Module(body=[factory], type_ignores=[]))


class _Entry:
    def __init__(self, manager, jit, name, source):
        self.manager, self.jit, self.name = manager, jit, name
        self.original_run = jit.run
        self.class_run = type(jit).run
        if (self.original_run.__func__ is not self.class_run
                or self.class_run.__globals__.get("JITFunction") is not type(jit)
                or "run" in vars(jit)):
            raise RuntimeError("JIT run 不是原生未覆盖方法")
        namespace = {}
        # closure 捕获 callback，所有原 global 仍指向原来的动态模块字典。
        exec(compile(_factory_tree(source), self.class_run.__code__.co_filename,
                     "exec"), self.class_run.__globals__, namespace)
        transformed = namespace["_biv_factory"](self.probe, self.record)
        self.replacement = types.MethodType(transformed, jit)
        self.recipes = [None, None] if name == "kernel" else [None]

    def scope(self, bound, options, warmup):
        m = self.manager
        knobs = self.class_run.__globals__["knobs"]
        if (warmup or not m.active or self.jit.pre_run_hooks
                or m.torch.cuda.is_current_stream_capturing()
                or knobs.runtime.launch_enter_hook is not None
                or knobs.runtime.launch_exit_hook is not None
                or self.jit.launch_metadata is not None):
            return None
        if (type(options) is not dict
                or not set(options) <= {"num_warps", "num_stages", "debug", "instrumentation_mode"}
                or any(type(v) not in (str, bool, int, type(None)) for v in options.values())
                or options.get("debug") not in (None, False)
                or options.get("instrumentation_mode") not in (None, "")):
            return None
        if (bound.get("num_query_heads") != 16 or bound.get("HEAD_SIZE") != 128
                or bound.get("HEAD_SIZE_PADDED") != 128 or bound.get("USE_FP8") is not False):
            return None
        out = bound.get("output_ptr")
        if (not isinstance(out, m.torch.Tensor) or out.dtype != m.torch.bfloat16
                or out.device.type != "cuda" or out.device.index != 0):
            return None
        if self.name == "reducer":
            if (bound.get("TILE_SIZE"), bound.get("BLOCK_Q"), bound.get("NUM_SEGMENTS_PER_SEQ")) != (16, 2, 16):
                return None
            return 0
        mode = bound.get("IS_3D")
        if type(mode) is not bool:
            return None
        if (bound.get("num_queries_per_kv") != 8 or bound.get("BLOCK_SIZE") != 16
                or bound.get("KV_QUANT_MODE") != 0 or bound.get("USE_CAUSAL") is not True
                or bound.get("SLIDING_WINDOW") != 0 or bound.get("CHUNK_SIZE") != -1
                or bound.get("CHUNK_LOOKBACK") != -1
                or any(bound.get(k) for k in ("USE_ALIBI_SLOPES", "USE_ALIBI_SQRT", "USE_QQ_BIAS",
                                             "USE_SOFTCAP", "USE_SINKS", "USE_PER_SEQ_CAUSAL",
                                             "USE_MM_PREFIX", "Q_IS_FP8", "USE_TD", "USE_TD_QO"))):
            return None
        shape = (bound.get("BLOCK_M"), bound.get("BLOCK_Q"), bound.get("TILE_SIZE"),
                 bound.get("NUM_SEGMENTS_PER_SEQ"))
        if shape != ((16, 2, 16, 16) if mode else (128, 16, 64, 1)):
            return None
        q = bound.get("query_ptr")
        if (not isinstance(q, m.torch.Tensor) or q.dtype != m.torch.bfloat16
                or q.device != out.device):
            return None
        if mode and (options.get("num_warps"), options.get("num_stages")) != (2, 1):
            return None
        return int(mode)

    def probe(self, jit, grid, warmup, device, stream, bound, specialization, options):
        try:
            slot = self.scope(bound, options, warmup) if device == 0 else None
            recipe = self.recipes[slot] if slot is not None else None
            if recipe is None:
                return None
            cache_tuple = jit.device_caches[device]
            cache, compiled, key, spec, opts = recipe
            if (cache_tuple is not cache or tuple(specialization) != spec
                    or tuple(options.items()) != opts or cache_tuple[0].get(key) is not compiled
                    or type(compiled) is not self.manager.compiled_class
                    or type(compiled).__getitem__ is not self.manager.compiled_getitem
                    or type(compiled).launch_metadata is not self.manager.compiled_metadata
                    or self.manager.compiled_getitem.__globals__["knobs"] is not self.class_run.__globals__["knobs"]
                    or type(jit).run is not self.class_run):
                return None
            if callable(grid) or type(grid) is not tuple or not 1 <= len(grid) <= 3:
                return None
            if any(type(n) is not int or n <= 0 for n in grid):
                return None
            canonical_grid = grid + (1,) * (3 - len(grid))
        except Exception:
            # 仅资格读取失败回原 tail；不能重试已提交的 launch。
            return None
        # 原 globals 检查与异常文本保持一致，异常不能吞掉后再 launch。
        not_present = object()
        for (name, _), (val, globals_dict) in jit.used_global_vals.items():
            if (newVal := globals_dict.get(name, not_present)) != val:
                raise RuntimeError(
                    f"Global variable {name} has changed since we compiled this kernel, from {val} to {newVal}")
        compiled[canonical_grid](*bound.values(), stream=stream)
        self.manager.counts[self.name + "_hot"] += 1
        return compiled

    def record(self, jit, compiled, device, warmup, bound, specialization, options, key):
        # 原 launch 已完成提交，记录失败不能改变其返回值/异常。
        try:
            slot = self.scope(bound, options, warmup) if device == 0 else None
            if slot is None:
                self.manager.counts["fallbacks"] += 1
                return
            m = self.manager
            cls = jit.CompiledKernel
            if m.compiled_class is None:
                _require_file(inspect.getsourcefile(cls), EXPECTED_COMPILER)
                m.compiled_class = cls
                m.compiled_getitem = cls.__getitem__
                m.compiled_metadata = cls.launch_metadata
            cache = jit.device_caches[device]
            if type(compiled) is not m.compiled_class or cache[0].get(key) is not compiled:
                m.counts["fallbacks"] += 1
                return
            self.recipes[slot] = (cache, compiled, key, tuple(specialization), tuple(options.items()))
            m.counts[self.name + "_bootstrap"] += 1
        except Exception:
            self.manager.counts["fallbacks"] += 1


class Manager:
    def __init__(self, attention, helpers, backend):
        _require_file(attention.__file__, EXPECTED_ATTENTION)
        _require_file(helpers.__file__, EXPECTED_HELPERS)
        _require_file(backend.__file__, EXPECTED_BACKEND)
        if (attention.current_platform.vendor_name != "iluvatar"
                or backend.unified_attention is not attention.unified_attention
                or attention.unified_attention.__globals__ is not vars(attention)):
            raise RuntimeError("Attention backend/globals 不匹配")
        self.outer = attention.kernel_unified_attention
        if (type(self.outer).__name__ != "DecodeLaunch"
                or _require_file(inspect.getsourcefile(type(self.outer)), EXPECTED_C2) is None):
            raise RuntimeError("需要原 C2 DecodeLaunch")
        raw, reducer = self.outer.original, attention.reduce_segments
        if raw is reducer or type(raw) is not type(reducer):
            raise RuntimeError("两 JIT 对象身份不匹配")
        run_source = _require_file(type(raw).run.__code__.co_filename, EXPECTED_JIT)
        _require_file(type(reducer).run.__code__.co_filename, EXPECTED_JIT)
        self.torch = attention.torch
        self.compiled_class = None
        self.compiled_getitem = None
        self.compiled_metadata = None
        self.active = False
        self.attention, self.reducer = attention, reducer
        self.counts = {k: 0 for k in ("kernel_hot", "reducer_hot", "kernel_bootstrap",
                                     "reducer_bootstrap", "fallbacks")}
        self.entries = [_Entry(self, raw, "kernel", run_source), _Entry(self, reducer, "reducer", run_source)]

    def install(self):
        if self.active:
            return
        if (self.attention.kernel_unified_attention is not self.outer
                or self.attention.reduce_segments is not self.reducer):
            raise RuntimeError("Attention 外层引用被其他修改替换")
        for entry in self.entries:
            if "run" in vars(entry.jit) or type(entry.jit).run is not entry.class_run:
                raise RuntimeError("JIT run 已被其他修改替换")
        for entry in self.entries:
            entry.jit.run = entry.replacement
        self.active = True

    def restore(self):
        if not self.active:
            return
        if any(vars(entry.jit).get("run") is not entry.replacement for entry in self.entries):
            raise RuntimeError("不能覆盖其他修改的 JIT run")
        for entry in self.entries:
            del entry.jit.run
        self.active = False

    def snapshot(self):
        return dict(self.counts)


def create(attention, helpers, backend):
    return Manager(attention, helpers, backend)
