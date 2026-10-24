"""默认不运行；仅在隔离微测 warmup 后为独立 B 函数设置一次 cache 偏好。"""
from __future__ import annotations

import hashlib
import importlib
from pathlib import Path

PINS = {
    "triton.backends.iluvatar.driver": "5023c317de1c2f3370d254320849a2013f68b353fd35884c60d857823c424f50",
    "triton.compiler.compiler": "f9646f23963160af7856e6f725df7af01c2bf0fc0ee98afeb7987f552507e5fd",
    "triton.runtime.jit": "6e9ce85c877b84807d97191211e53fbc7547328dd22dc6b8d9185c7bafc67210",
}
DRIVER_C = "6d1b04ccaad92e4b513b79139a4d56980cf580f530cf134447e6840f3e98d847"
SDK_PINS = {
    "cuda.h": "63e390c14322db4dd404a099dc266b5d3f2cea42488efca346b2a8dc94e6faab",
    "IX/mapping_cudart.h": "ca962a4e5e051a6de6e8c84c89cf6ec9430d8fbb225a78708731b928662984fb",
    "IX/ixrt/ix.h": "cf0737bc295d0e7ed2b78635dba93b2cc81a5c4a1f43755429065e07a3fbde83",
}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


class _Capture:
    """只在 warmup 使用；每次仅调用原 launch 一次，返回值/异常原样。"""
    def __init__(self, jit):
        self.jit, self.compiled = jit, []

    def __getitem__(self, grid):
        launch = self.jit[grid]
        def invoke(*args, **kwargs):
            compiled = launch(*args, **kwargs)
            self.compiled.append(compiled)
            return compiled
        return invoke


def _handles(compiled):
    module, function = compiled.module, compiled.function
    if (type(module) is not int or type(function) is not int
            or module <= 0 or function <= 0):
        raise RuntimeError("requires initialized nonzero integer module/function handles")
    return {"module": module, "function": function, "compile_hash": compiled.hash,
            "binary_sha256": digest(compiled.kernel), "shared": compiled.metadata.shared,
            "n_regs": compiled.n_regs, "n_spills": compiled.n_spills}


def _independent(a, b, originals):
    ha, hb = _handles(a), _handles(b)
    if ha["module"] == hb["module"] or ha["function"] == hb["function"]:
        raise RuntimeError("A/B driver instances are not independent; no mutation permitted")
    if (a.kernel != b.kernel or a.hash != b.hash
            or a.metadata != b.metadata or a.packed_metadata != b.packed_metadata
            or a.n_regs != b.n_regs or a.n_spills != b.n_spills):
        raise RuntimeError("A/B compiled binaries/resources differ; no mutation permitted")
    if ha["shared"] != 49152:
        raise RuntimeError("expected measured V-late 49152-byte shared allocation")
    if not originals:
        raise RuntimeError("original loaded kernels were not observed")
    for compiled in originals:
        original = _handles(compiled)
        if (ha["function"] == original["function"] or hb["function"] == original["function"]
                or ha["module"] == original["module"] or hb["module"] == original["module"]):
            raise RuntimeError("isolated candidate aliases an original loaded kernel")
    return ha, hb


class CachePair:
    def __init__(self, manager, bridge_path):
        self.manager, self.bridge_path = manager, Path(bridge_path)
        self.default_jit = manager.candidate
        self.shared_jit = None
        self.ready = False
        self.report = {"status": "unprepared", "mutations": [],
                       "dynamic_shared_optin_changed": False,
                       "cache_preference_getter": "not available; context getter is not used",
                       "attributes_note": "carveout and max_dynamic_shared are not cache-preference getters"}

    def _load_bridge_and_clone(self):
        modules = {}
        for name, expected in PINS.items():
            module = importlib.import_module(name)
            actual = digest(Path(module.__file__).read_bytes())
            if actual != expected:
                raise RuntimeError("unaudited installed source: " + name + " " + actual)
            modules[name] = module
        driver = modules["triton.backends.iluvatar.driver"]
        if digest(Path(driver.__file__).with_name("driver.c").read_bytes()) != DRIVER_C:
            raise RuntimeError("installed loader C source changed")
        for name, expected in SDK_PINS.items():
            if digest((Path("/usr/local/corex/include") / name).read_bytes()) != expected:
                raise RuntimeError("installed SDK source changed: " + name)
        jit_type = modules["triton.runtime.jit"].JITFunction
        compiled_type = modules["triton.compiler.compiler"].CompiledKernel
        # FlagTree 导出模块与实际类实现可能分属 base/spec；按运行方法锁定已审 spec。
        actual_methods = (
            ("JITFunction.__init__", jit_type.__init__, "66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775"),
            ("JITFunction.run", jit_type.run, "66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775"),
            ("CompiledKernel.__init__", compiled_type.__init__, "a97f067023873acf2e348c28f61494e59170ca84c3ee2314f20e491d3e833dfd"),
            ("CompiledKernel._init_handles", compiled_type._init_handles, "a97f067023873acf2e348c28f61494e59170ca84c3ee2314f20e491d3e833dfd"),
        )
        self.report["actual_class_sources"] = {}
        for name, method, expected in actual_methods:
            path = Path(method.__code__.co_filename)
            if digest(path.read_bytes()) != expected:
                raise RuntimeError("unaudited actual class implementation: " + name)
            self.report["actual_class_sources"][name] = {"path": str(path), "sha256": expected}
        jit = self.default_jit
        if type(jit) is not jit_type or jit.pre_run_hooks:
            raise RuntimeError("expected plain private JITFunction with no pre-run hooks")
        self.shared_jit = jit_type(jit.fn, version=jit.version,
            do_not_specialize=list(jit.do_not_specialize),
            do_not_specialize_on_alignment=list(jit.do_not_specialize_on_alignment),
            debug=jit.debug, noinline=jit.noinline, repr=jit._repr,
            launch_metadata=jit.launch_metadata)
        if self.shared_jit.device_caches is jit.device_caches:
            raise RuntimeError("JIT instance cache unexpectedly shared")
        from triton.runtime.build import compile_module_from_src
        self.bridge = compile_module_from_src(
            src=self.bridge_path.read_text(encoding="utf-8"),
            name="biv150_cache_preference_probe", library_dirs=driver.library_dirs(),
            include_dirs=driver.include_dirs, libraries=driver.libraries)
        self.report.update(source_sha256=dict(PINS, driver_c=DRIVER_C), sdk_sha256=SDK_PINS,
                           bridge_sha256=digest(self.bridge_path.read_bytes()))

    def _originals(self):
        raw = self.manager.original_kernel
        for _ in range(4):
            if "original" not in getattr(raw, "__dict__", {}):
                break
            raw = raw.original
        found = []
        for state in raw.device_caches.values():
            for compiled in state[0].values():
                if getattr(compiled, "module", None) is not None:
                    found.append(compiled)
        expected = self.manager.baseline_resources["hash"]
        if not any(x.hash == expected for x in found):
            raise RuntimeError("original 2D observer hash missing from actual JIT cache")
        return found

    def prepare(self, torch, callback):
        if self.ready or self.shared_jit is not None:
            raise RuntimeError("cache experiment preparation is one-shot")
        self.report["status"] = "preparing"
        self._load_bridge_and_clone()
        captures = []
        try:
            for jit in (self.default_jit, self.shared_jit):
                capture = _Capture(jit)
                self.manager.candidate = capture
                self.manager.install()
                callback()
                torch.cuda.synchronize()
                if len(capture.compiled) != 1:
                    raise RuntimeError("warmup must observe exactly one eligible 2D kernel")
                captures.append(capture.compiled[0])
                self.manager.restore()
            self.a, self.b = captures
            originals = self._originals()
            ha, hb = _independent(self.a, self.b, originals)
            self.report.update(a=ha, b=hb, originals=[_handles(x) for x in originals],
                               a_attributes_before=self.bridge.attributes(ha["function"]),
                               b_attributes_before=self.bridge.attributes(hb["function"]))
            # All prior launches completed; this mutates only the independent B function.
            receipt = self.bridge.prefer_shared(hb["function"])
            self.report["mutations"].append(dict(action="function_cache_prefer_shared",
                function=hb["function"], **receipt))
            if receipt["return_code"] != receipt["success_code"]:
                raise RuntimeError("per-function cache API unsupported or failed: " + repr(receipt))
            self.report.update(a_attributes_after=self.bridge.attributes(ha["function"]),
                               b_attributes_after=self.bridge.attributes(hb["function"]))
            if any(_handles(x) != previous for x, previous in zip(originals, self.report["originals"])):
                raise RuntimeError("original kernel identities changed during setup")
            self.ready = True
            self.report["status"] = "cache_only_set_on_independent_B"
        finally:
            self.manager.restore()
            self.manager.candidate = self.shared_jit or self.default_jit

    def select(self, name):
        if not self.ready:
            raise RuntimeError("cache experiment is not ready")
        self.manager.restore()
        if name == "baseline":
            return
        if name not in ("late_v_default", "candidate"):
            raise ValueError(name)
        self.manager.candidate = self.default_jit if name == "late_v_default" else self.shared_jit
        self.manager.install()
