"""默认关闭：仅已审计 MiniCPM BF16 2D BM128/T64/s1 的 warps 8→16。"""
from __future__ import annotations
import hashlib
from pathlib import Path

EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"

def _target(k):
    return (k.get("IS_3D") is False
        and all(k.get(n) == v for n, v in {
            "HEAD_SIZE":128,"HEAD_SIZE_PADDED":128,"num_query_heads":16,
            "num_queries_per_kv":8,"BLOCK_M":128,"BLOCK_Q":16,"BLOCK_SIZE":16,
            "TILE_SIZE":64,"NUM_SEGMENTS_PER_SEQ":1,"KV_QUANT_MODE":0,
            "SLIDING_WINDOW":0,"CHUNK_SIZE":-1,"CHUNK_LOOKBACK":-1,
            "num_warps":8,"num_stages":1}.items())
        and k.get("USE_CAUSAL") is True
        and not any(k.get(n) for n in ("USE_FP8","Q_IS_FP8","USE_TD","USE_TD_QO",
            "USE_ALIBI_SLOPES","USE_ALIBI_SQRT","USE_QQ_BIAS","USE_SOFTCAP",
            "USE_SINKS","USE_PER_SEQ_CAUSAL","USE_MM_PREFIX"))
        and all(str(getattr(k.get(n),"dtype",None)) == "torch.bfloat16"
                and getattr(getattr(k.get(n),"device",None),"type",None) == "cuda"
                for n in ("query_ptr","output_ptr","key_cache_ptr","value_cache_ptr")))

def _resources(compiled):
    meta = getattr(compiled,"metadata",None)
    result = {"compiled_type":type(compiled).__name__}
    for n in ("hash","n_regs","n_spills"):
        value = getattr(compiled,n,None)
        result[n] = value if isinstance(value,(str,int,float,bool,type(None))) else str(value)
    result["metadata"] = {}
    for n in ("num_warps","num_stages","shared","use_sme","warp_size"):
        value = meta.get(n) if isinstance(meta,dict) else getattr(meta,n,None)
        result["metadata"][n] = value if isinstance(value,(str,int,float,bool,type(None))) else str(value)
    return result

class _Launch:
    def __init__(self, manager): self.manager = manager
    def __getattr__(self,n): return getattr(self.manager.original_kernel,n)
    def __getitem__(self,grid):
        m = self.manager
        launch = m.original_kernel[grid]
        def invoke(*args,**kwargs):
            selected = not args and _target(kwargs)
            if selected:
                kwargs = dict(kwargs)
                kwargs["num_warps"] = 16
                m.selected_calls += 1
            elif kwargs.get("IS_3D") is True:
                m.original_3d_calls += 1
            else:
                m.fallback_calls += 1
            # Original callable once. A compile/launch failure is never retried.
            compiled = launch(*args,**kwargs)
            if selected and m.compiled_resources is None:
                m.compiled_resources = _resources(compiled)
            return compiled
        return invoke

class Manager:
    def __init__(self,attention,backend):
        self.attention,self.backend = attention,backend
        self.original_kernel = attention.kernel_unified_attention
        self.original_forward = backend.TritonAttentionImpl.forward
        self.wrapper = _Launch(self)
        self.selected_calls = self.fallback_calls = self.original_3d_calls = 0
        self.compiled_resources = None
        self.active = False
    def install(self):
        if self.attention.kernel_unified_attention not in (self.original_kernel,self.wrapper):
            raise RuntimeError("Attention kernel binding changed")
        self.attention.kernel_unified_attention = self.wrapper
        self.active = True
    def restore(self):
        if self.active:
            if self.attention.kernel_unified_attention is not self.wrapper:
                raise RuntimeError("Attention kernel binding changed before restore")
            self.attention.kernel_unified_attention = self.original_kernel
        self.active = False
    def snapshot(self):
        return {"selected_calls":self.selected_calls,"fallback_calls":self.fallback_calls,
                "original_3d_calls":self.original_3d_calls,"compiled_resources":self.compiled_resources}

def create(attention,helpers,backend):
    for module,expected in ((attention,EXPECTED_ATTENTION),(helpers,EXPECTED_HELPERS),(backend,EXPECTED_BACKEND)):
        if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != expected:
            raise RuntimeError("Unaudited source: " + str(module.__file__))
    if (attention.current_platform.vendor_name != "iluvatar"
        or backend.unified_attention is not attention.unified_attention
        or attention.unified_attention.__globals__ is not vars(attention)):
        raise RuntimeError("Unaudited platform/Attention binding")
    outer = attention.kernel_unified_attention
    source = getattr(type(outer).__getitem__,"__code__",None)
    if (source is None or hashlib.sha256(Path(source.co_filename).read_bytes()).hexdigest() != EXPECTED_C2):
        raise RuntimeError("Original C2 launch proxy required")
    raw = outer
    for _ in range(4):
        if "original" not in getattr(raw,"__dict__",{}): break
        raw = raw.original
    if "run" in getattr(raw,"__dict__",{}):
        raise RuntimeError("Stacked JIT.run candidate forbidden")
    return Manager(attention,backend)
