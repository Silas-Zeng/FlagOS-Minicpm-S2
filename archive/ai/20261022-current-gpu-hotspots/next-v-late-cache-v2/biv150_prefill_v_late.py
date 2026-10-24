"""默认关闭：仅已审计 MiniCPM BF16 2D 的 V 地址/load/cast 延至 softmax 后。"""
from __future__ import annotations
import hashlib
import importlib.util
import sys
from pathlib import Path

EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"

_SIGNATURE = b"    Q_IS_FP8: tl.constexpr = False,\n"
_AFTER = b"        acc = acc * alpha[:, None]\n"
_FLAG = b"    BIV150_LATE_V: tl.constexpr = False,\n"
_V_OFFSET = b'            v_offset = (\n                physical_block_idx[:, None] * stride_v_cache_0\n                + kv_head_idx * stride_v_cache_2\n                + offs_d[None, :] * stride_v_cache_3\n                + (seq_offset % BLOCK_SIZE)[:, None] * stride_v_cache_1\n            )\n'
_V_LOAD = b'            V_load = tl.load(\n                value_cache_ptr + v_offset,\n                mask=dim_mask[None, :] & tile_mask[:, None],\n                other=0.0,\n            )\n'
_V_CAST = b'        V = _cast_kv_tile(V_load, Q, v_scale, KV_QUANT_MODE)\n'

def _indent(raw):
    return b"".join(b"    "+line if line.strip() else line for line in raw.splitlines(keepends=True))

def transform_source(source, helpers):
    for raw, expected in ((source,EXPECTED_ATTENTION),(helpers,EXPECTED_HELPERS)):
        if hashlib.sha256(raw).hexdigest()!=expected:
            raise RuntimeError("Unaudited late-V source")
    for anchor in (_SIGNATURE,_V_OFFSET,_V_LOAD,_V_CAST,_AFTER):
        if source.count(anchor)!=1: raise RuntimeError("Late-V source anchor changed")
    changed=source.replace(_SIGNATURE,_SIGNATURE+_FLAG,1)
    for block in (_V_OFFSET,_V_LOAD,_V_CAST):
        indent=block[:len(block)-len(block.lstrip(b" "))]
        changed=changed.replace(block,indent+b"if not BIV150_LATE_V:\n"+_indent(block),1)
    late=b"        if BIV150_LATE_V:\n"+_V_OFFSET+_V_LOAD+_indent(_V_CAST)
    changed=changed.replace(_AFTER,_AFTER+late,1)
    # Exact byte inverse proves no score/math/traversal/other-source edit.
    restored=changed.replace(_AFTER+late,_AFTER,1)
    for block in (_V_OFFSET,_V_LOAD,_V_CAST):
        indent=block[:len(block)-len(block.lstrip(b" "))]
        restored=restored.replace(indent+b"if not BIV150_LATE_V:\n"+_indent(block),block,1)
    restored=restored.replace(_SIGNATURE+_FLAG,_SIGNATURE,1)
    if restored!=source: raise RuntimeError("Late-V exact inverse failed")
    compile(changed,"<late-v-generated>","exec")
    return changed

def _eligible(values):
    """Descriptor-only checks. No D2H, .item(), RNG or metadata mutation."""
    exact = {"IS_3D": False, "HEAD_SIZE": 128, "HEAD_SIZE_PADDED": 128,
             "num_query_heads": 16, "num_queries_per_kv": 8,
             "BLOCK_M": 128, "BLOCK_Q": 16, "BLOCK_SIZE": 16, "TILE_SIZE": 64,
             "NUM_SEGMENTS_PER_SEQ": 1, "KV_QUANT_MODE": 0,
             "USE_CAUSAL": True, "SLIDING_WINDOW": 0,
             "CHUNK_LOOKBACK": -1, "CHUNK_SIZE": -1,
             "num_warps": 8, "num_stages": 1}
    if any(values.get(name) != expected for name, expected in exact.items()):
        return False
    if any(values.get(name, False) for name in (
            "USE_FP8", "Q_IS_FP8", "USE_TD", "USE_TD_QO", "USE_ALIBI_SLOPES",
            "USE_ALIBI_SQRT", "USE_QQ_BIAS", "USE_SOFTCAP", "USE_SINKS",
            "USE_PER_SEQ_CAUSAL", "USE_MM_PREFIX")):
        return False
    q, k, v, out = (values.get(name) for name in (
        "query_ptr", "key_cache_ptr", "value_cache_ptr", "output_ptr"))
    if any(x is None for x in (q, k, v, out)):
        return False
    if (str(q.dtype) != "torch.bfloat16" or not all(x.dtype == q.dtype for x in (k, v, out))
            or q.device.type != "cuda" or not all(x.device == q.device for x in (k, v, out))
            or q.ndim != 3 or out.ndim != 3 or q.shape != out.shape
            or tuple(q.shape[1:]) != (16, 128)
            or k.ndim != 4 or v.shape != k.shape or tuple(k.shape[1:]) != (16, 2, 128)
            or min(q.shape[0], k.shape[0]) <= 0):
        return False
    if any(x.stride(-1) != 1 or any(s <= 0 for s in x.stride()) for x in (q, k, v, out)):
        return False
    if (q.stride(1) != 128 or out.stride(1) != 128
            or q.stride(0) < 2048 or out.stride(0) < 2048
            or any(tuple(x.stride()[1:]) != (256, 128, 1) or x.stride(0) < 4096 for x in (k, v))):
        return False
    readers = {x.untyped_storage().data_ptr() for x in (q, k, v)}
    if out.untyped_storage().data_ptr() in readers:
        return False
    count = values.get("num_seqs")
    if not isinstance(count, int) or count <= 0:
        return False
    for name, length in (("query_start_len_ptr", count + 1), ("seq_lens_ptr", count)):
        tensor = values.get(name)
        if (tensor is None or tensor.device != q.device or str(tensor.dtype) != "torch.int32"
                or tensor.ndim != 1 or tensor.shape[0] != length or tensor.stride(0) != 1):
            return False
    table = values.get("block_tables_ptr")
    return (table is not None and table.device == q.device and str(table.dtype) == "torch.int32"
            and table.ndim == 2 and table.shape[0] == count and table.shape[1] > 0
            and table.stride(1) == 1 and table.stride(0) >= table.shape[1])

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
    asm=getattr(compiled,"asm",None)
    result["asm_sha256"]={}
    if isinstance(asm,dict):
        for name,value in asm.items():
            if isinstance(value,(str,bytes)):
                raw=value.encode() if isinstance(value,str) else value
                result["asm_sha256"][name]=hashlib.sha256(raw).hexdigest()
    return result

class _Launch:
    def __init__(self,manager): self.manager=manager
    def __getattr__(self,name): return getattr(self.manager.original_kernel,name)
    def __getitem__(self,grid):
        m=self.manager
        original=m.original_kernel[grid]
        candidate=m.candidate[grid]
        def invoke(*args,**kwargs):
            selected=not args and "BIV150_LATE_V" not in kwargs and _eligible(kwargs)
            if m.observe_only:
                compiled=original(*args,**kwargs)
                if selected and m.baseline_resources is None:
                    m.baseline_resources=_resources(compiled)
                return compiled
            if selected:
                m.selected_calls+=1
                # No changed dot, masks, softmax, accumulator, traversal or launch options.
                compiled=candidate(**kwargs,BIV150_LATE_V=True)
                if m.compiled_resources is None: m.compiled_resources=_resources(compiled)
                return compiled
            if kwargs.get("IS_3D") is True: m.original_3d_calls+=1
            else: m.fallback_calls+=1
            return original(*args,**kwargs)
        return invoke

class Manager:
    def __init__(self,attention,backend,candidate,generated_path):
        self.attention,self.backend=attention,backend
        self.original_kernel=attention.kernel_unified_attention
        self.original_forward=backend.TritonAttentionImpl.forward
        self.candidate=candidate
        self.generated_path=generated_path
        self.wrapper=_Launch(self)
        self.selected_calls=self.fallback_calls=self.original_3d_calls=0
        self.compiled_resources=self.baseline_resources=None
        self.active=self.observe_only=False
    def _install(self,observe_only):
        if self.attention.kernel_unified_attention not in (self.original_kernel,self.wrapper):
            raise RuntimeError("Attention kernel binding changed")
        self.observe_only=observe_only
        self.attention.kernel_unified_attention=self.wrapper
        self.active=True
    def install(self): self._install(False)
    def install_baseline_observer(self): self._install(True)
    def restore(self):
        if self.active:
            if self.attention.kernel_unified_attention is not self.wrapper:
                raise RuntimeError("Attention kernel binding changed before restore")
            self.attention.kernel_unified_attention=self.original_kernel
        self.active=self.observe_only=False
    def snapshot(self):
        return {"selected_calls":self.selected_calls,"fallback_calls":self.fallback_calls,
                "original_3d_calls":self.original_3d_calls,"compiled_resources":self.compiled_resources,
                "baseline_compiled_resources":self.baseline_resources,
                "generated_sha256":hashlib.sha256(self.generated_path.read_bytes()).hexdigest()}

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
    generated_path=Path(__file__).with_name("generated_attention.py")
    changed=transform_source(Path(attention.__file__).read_bytes(),Path(helpers.__file__).read_bytes())
    with generated_path.open("xb") as stream: stream.write(changed)
    name="_biv150_late_v_"+hashlib.sha256(changed).hexdigest()[:16]
    if name in sys.modules: raise RuntimeError("Late-V isolated module already loaded")
    spec=importlib.util.spec_from_file_location(name,generated_path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    try: spec.loader.exec_module(module)
    except BaseException:
        del sys.modules[name]
        raise
    return Manager(attention,backend,module.kernel_unified_attention,generated_path)
