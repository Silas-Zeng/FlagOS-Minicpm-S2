"""默认关闭：exact2D TTGIR只外提Q dot fragment；不修改installed或全局compile状态。"""
from __future__ import annotations
import hashlib
import inspect
import re
from enum import IntEnum
from pathlib import Path

EXPECTED_ATTENTION = "54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f"
EXPECTED_HELPERS = "59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1"
EXPECTED_BACKEND = "1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605"
EXPECTED_C2 = "e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f"
EXPECTED_JIT = "66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775"
EXPECTED_COMPILER = "a97f067023873acf2e348c28f61494e59170ca84c3ee2314f20e491d3e833dfd"
EXPECTED_BACKEND_COMPILER = "a0d2bbda2f779b528147a238ff6fc558d026478f72d3d12d51d27f48f1aa570a"
EXPECTED_TTGIR = "ff6456f708cca1101909e7de6896d63bfcbe8ae1f4edafb2d1cda33d93c95766"
EXPECTED_KV_INTERFACE = "7e3c220998267190a622e216b2b125306807cf8be3ec1e9a8e84fe6e7a293003"

def _sha(raw): return hashlib.sha256(raw).hexdigest()

def transform_ir(raw):
    if _sha(raw) != EXPECTED_TTGIR:
        raise RuntimeError("only audited original2D TTGIR recipe is eligible")
    text=raw.decode("utf-8")
    lines=text.splitlines(keepends=True)
    at=[i for i,line in enumerate(lines) if "%Q_222 = ttg.local_load %Q_131" in line]
    loops=[i for i,line in enumerate(lines) if "= scf.for " in line]
    if len(at)!=1 or len(loops)!=1 or at[0]<=loops[0]:
        raise RuntimeError("Q local_load/main loop anchor changed")
    old=lines[at[0]]
    if not old.startswith("      ") or "dot_op<{opIdx = 0" not in old:
        raise RuntimeError("Q operand type/indent changed")
    moved=old[2:]
    changed=lines.copy()
    del changed[at[0]]
    changed.insert(loops[0],moved)
    # No Q allocation, mask, floating op, loop, or synchronization is deleted.
    restored=changed.copy()
    del restored[loops[0]]
    restored.insert(at[0],old)
    if restored!=lines or text.count("ttg.local_alloc %Q_130")!=1:
        raise RuntimeError("exact inverse/Q allocation proof failed")
    return "".join(changed).encode("utf-8")

def _freeze(value):
    if value is None or type(value) in (str,int,float,bool): return (type(value).__name__,value)
    if (isinstance(value,IntEnum) and type(value).__module__=="vllm.v1.kv_cache_interface"
        and type(value).__name__=="KVQuantMode"):
        return ("KVQuantMode",int(value))
    if type(value) in (tuple,list): return (type(value).__name__,tuple(_freeze(x) for x in value))
    if type(value) is dict: return ("dict",tuple(sorted((_freeze(k),_freeze(v)) for k,v in value.items())))
    raise ValueError("unknown specialization/options object")

def _descriptors(values):
    result=[]
    for name,value in sorted(values.items()):
        if hasattr(value,"data_ptr"):
            ptr=int(value.data_ptr())
            # Frozen IR has divisibility4. A 256-byte residue guard is stricter.
            if ptr%4: raise ValueError("IR pointer alignment incompatible")
            result.append((name,"tensor",type(value).__module__,type(value).__name__,str(value.dtype),
                           str(value.device),tuple(value.shape),tuple(value.stride()),ptr%256))
        else: result.append((name,_freeze(value)))
    return tuple(result)

def _binder_recipe(raw,values):
    device=values["query_ptr"].device.index
    entry=raw.device_caches.get(device)
    if entry is None or len(entry)!=5: raise ValueError("baseline binder is not initialized")
    _,_,target,_,binder=entry
    bound,specialization,options=binder(**values)
    # Include actual native specializations, not a guessed dtype/shape key.
    return (_freeze(specialization),_freeze(options),str(target),tuple(bound))

def _compile_state(raw):
    knobs=raw.run.__func__.__globals__["knobs"]
    return (knobs.compilation.override,knobs.compilation.instrumentation_mode,
            knobs.runtime.debug,id(knobs.runtime.add_stages_inspection_hook),
            knobs.language.default_fp_fusion)

def lowered_proof(ttgir,llir):
    alloc=re.findall(r"(%[A-Za-z0-9_]+) = ttg.local_alloc .*tensor<128x128xbf16",ttgir)
    if len(alloc)!=1: raise RuntimeError("cannot identify actual Q allocation")
    loads=list(re.finditer(r"ttg.local_load "+re.escape(alloc[0])+r"(?=\s| :)",ttgir))
    loops=list(re.finditer(r"= scf.for ",ttgir))
    if len(loads)!=1 or len(loops)!=1: raise RuntimeError("actual Q load/loop changed")
    # Native LLVM may rematerialize reads. Inspect its real cyclic CFG as well.
    q_debug=set(re.findall(r"^!(\d+) = !DILocation\(line: 352, column: 12,",llir,re.M))
    if len(q_debug)!=1: raise RuntimeError("actual Q source location missing")
    blocks={"entry":[]}; current="entry"
    for line in llir.splitlines():
        match=re.match(r"^([A-Za-z0-9_.-]+):",line)
        if match: current=match.group(1);blocks[current]=[]
        blocks[current].append(line)
    edges={k:set(re.findall(r"label %([A-Za-z0-9_.-]+)","\n".join(v))) for k,v in blocks.items()}
    cyclic=set()
    for node in blocks:
        pending=list(edges[node]);seen=set()
        while pending:
            nxt=pending.pop()
            if nxt==node: cyclic.add(node);break
            if nxt in seen:continue
            seen.add(nxt);pending.extend(edges.get(nxt,()))
    accesses=[]
    for block,lines in blocks.items():
        for line in lines:
            if any(re.search(r"!dbg !"+x+r"(?![0-9])",line) for x in q_debug) and (
                (" = load " in line and "addrspace(3)" in line) or "@llvm.bi.load.kop" in line):
                accesses.append({"block":block,"in_loop":block in cyclic,"instruction":line.strip()})
    in_loop=sum(x["in_loop"] for x in accesses)
    return {"ttgir_q_load_outside_loop":loads[0].start()<loops[0].start(),
            "llvm_q_memory_reads_in_loop":in_loop,"llvm_q_memory_reads_total":len(accesses),
            "q_read_blocks":sorted({x["block"] for x in accesses}),
            "barrier_calls":llir.count("call void @llvm.nvvm.barrier.cta.sync.aligned.all"),
            "mechanism_pass":loads[0].start()<loops[0].start() and in_loop==0 and bool(accesses),
            "limits":"barrier presence/count is recorded, not a complete synchronization/occupancy proof"}


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

def _resources(compiled, artifact_dir=None, label=None):
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
    result["asm_files"]={}
    if isinstance(asm,dict):
        for name,value in asm.items():
            if isinstance(value,(str,bytes)):
                raw=value.encode() if isinstance(value,str) else value
                result["asm_sha256"][name]=hashlib.sha256(raw).hexdigest()
                if artifact_dir is not None and label is not None and name.replace("_", "").isalnum():
                    path=Path(artifact_dir)/(label+"."+name+(".txt" if isinstance(value,str) else ".bin"))
                    with path.open("xb") as stream: stream.write(raw)
                    result["asm_files"][name]=path.name
    return result


class _Launch:
    def __init__(self, manager): self.manager=manager
    def __getattr__(self, name): return getattr(self.manager.original_kernel,name)
    def __getitem__(self, grid):
        m=self.manager
        original=m.original_kernel[grid]
        candidate=m.candidate[grid]
        def invoke(*args, **kwargs):
            eligible=not args and "ir_override" not in kwargs and _eligible(kwargs)
            if m.observe_only:
                compiled=original(*args,**kwargs)
                if eligible and m.baseline_resources is None:
                    # The original call initialized its native binder/cache.
                    descriptors=_descriptors(kwargs)
                    recipe=_binder_recipe(m.raw,kwargs)
                    m._capture(compiled,descriptors,recipe)
                return compiled
            # Native binder is read-only here; actual JIT.run still executes its
            # complete standard prefix/tail, launch hooks and current stream.
            descriptors=recipe=None
            selected=False
            if eligible:
                try:
                    descriptors=_descriptors(kwargs)
                    recipe=_binder_recipe(m.raw,kwargs)
                    selected=(m.recipe is not None and recipe==m.recipe
                              and _compile_state(m.raw)==m.compile_state
                              and descriptors==m.descriptors)
                except Exception:
                    eligible=False
            if selected:
                if m.raw.pre_run_hooks or m.candidate.pre_run_hooks:
                    raise RuntimeError("pre-run hook changed after audited clone")
                if m.compiled_resources is None:
                    m.verify_ir()
                m.selected_calls+=1
                # Never cache tensors/bound_args or touch original JIT caches.
                compiled=candidate(**kwargs,ir_override=str(m.ir_path))
                if m.compiled_resources is None:
                    if compiled is m.baseline_compiled or compiled.hash==m.baseline_compiled.hash:
                        raise RuntimeError("candidate aliases baseline compiler cache")
                    if _freeze(compiled.src.signature)!=m.source_abi[0] or _freeze(compiled.src.constants)!=m.source_abi[1] or _freeze(compiled.src.attrs)!=m.source_abi[2]:
                        raise RuntimeError("candidate ABI/constants/attrs differ from captured baseline")
                    if m._original_cache()!=m.original_cache_state:
                        raise RuntimeError("candidate modified original JIT cache")
                    m.compiled_resources=_resources(compiled,m.artifact_dir,"candidate")
                    m.mechanism=lowered_proof(compiled.asm["ttgir"],compiled.asm["llir"])
                return compiled
            if kwargs.get("IS_3D") is True: m.original_3d_calls+=1
            else: m.fallback_calls+=1
            return original(*args,**kwargs)
        return invoke


class Manager:
    def __init__(self,attention,backend,raw,candidate,artifact_dir):
        self.attention,self.backend,self.raw,self.candidate=attention,backend,raw,candidate
        self.original_kernel=attention.kernel_unified_attention
        self.original_forward=backend.TritonAttentionImpl.forward
        self.artifact_dir=Path(artifact_dir)
        self.wrapper=_Launch(self)
        self.selected_calls=self.fallback_calls=self.original_3d_calls=0
        self.compiled_resources=self.baseline_resources=self.mechanism=None
        self.baseline_compiled=self.ir_path=self.ir_sha256=None
        self.recipe=self.descriptors=self.source_abi=None
        self.original_cache_state=None
        self.compile_state=None
        self.active=self.observe_only=False
    def _capture(self,compiled,descriptors,recipe):
        if _sha(Path(inspect.getsourcefile(type(compiled))).read_bytes())!=EXPECTED_COMPILER:
            raise RuntimeError("unaudited CompiledKernel source")
        changed=transform_ir(compiled.asm["ttgir"].encode("utf-8"))
        sha=_sha(changed)
        path=self.artifact_dir/("q-fragment-"+sha+".ttgir")
        with path.open("xb") as stream: stream.write(changed)
        if _sha(path.read_bytes())!=sha: raise RuntimeError("IR write verification failed")
        self.ir_path,self.ir_sha256=path,sha
        self.recipe,self.descriptors=recipe,descriptors
        self.compile_state=_compile_state(self.raw)
        self.source_abi=(_freeze(compiled.src.signature),_freeze(compiled.src.constants),_freeze(compiled.src.attrs))
        self.baseline_compiled=compiled
        self.baseline_resources=_resources(compiled,self.artifact_dir,"baseline")
        self.original_cache_state=self._original_cache()
    def _original_cache(self):
        return tuple(sorted((device,tuple(sorted((repr(key),id(value)) for key,value in entry[0].items())),
                             tuple(sorted((repr(key),repr(value)) for key,value in entry[1].items())))
                            for device,entry in self.raw.device_caches.items()))
    def verify_ir(self):
        if self.ir_path is None or _sha(self.ir_path.read_bytes())!=self.ir_sha256:
            raise RuntimeError("immutable Q-hoist override content changed")
        return True
    def _install(self,observe_only):
        if self.attention.kernel_unified_attention not in (self.original_kernel,self.wrapper):
            raise RuntimeError("Attention binding changed")
        if not observe_only and self.recipe is None:
            raise RuntimeError("audited baseline compile recipe must be captured first")
        self.observe_only=observe_only
        self.attention.kernel_unified_attention=self.wrapper
        self.active=True
    def install(self): self._install(False)
    def install_baseline_observer(self): self._install(True)
    def restore(self):
        if self.active:
            if self.attention.kernel_unified_attention is not self.wrapper:
                raise RuntimeError("Attention binding changed before restore")
            self.attention.kernel_unified_attention=self.original_kernel
        self.active=self.observe_only=False
    def snapshot(self):
        return {"selected_calls":self.selected_calls,"fallback_calls":self.fallback_calls,
                "original_3d_calls":self.original_3d_calls,"compiled_resources":self.compiled_resources,
                "baseline_compiled_resources":self.baseline_resources,"mechanism":self.mechanism,
                "ir_sha256":self.ir_sha256,"ir_filename":self.ir_path.name if self.ir_path else None,
                "independent_jit_caches":self.raw.device_caches is not self.candidate.device_caches,
                "baseline_cache_unmodified":self.original_cache_state is None or self._original_cache()==self.original_cache_state}


def create(attention,helpers,backend):
    import importlib
    for module,expected in ((attention,EXPECTED_ATTENTION),(helpers,EXPECTED_HELPERS),(backend,EXPECTED_BACKEND)):
        if _sha(Path(module.__file__).read_bytes())!=expected:
            raise RuntimeError("unaudited Attention/helper/backend source")
    if (attention.current_platform.vendor_name!="iluvatar"
        or backend.unified_attention is not attention.unified_attention
        or attention.unified_attention.__globals__ is not vars(attention)):
        raise RuntimeError("unaudited platform/Attention binding")
    quant=attention.KVQuantMode
    if (quant.__module__!="vllm.v1.kv_cache_interface" or quant.__name__!="KVQuantMode"
        or not issubclass(quant,IntEnum)
        or _sha(Path(quant.is_per_token_head.fget.__code__.co_filename).read_bytes())!=EXPECTED_KV_INTERFACE):
        raise RuntimeError("unaudited KVQuantMode class")
    outer=attention.kernel_unified_attention
    code=getattr(type(outer).__getitem__,"__code__",None)
    if code is None or _sha(Path(code.co_filename).read_bytes())!=EXPECTED_C2:
        raise RuntimeError("original C2 launch proxy required")
    raw=outer
    for _ in range(4):
        if "original" not in getattr(raw,"__dict__",{}): break
        raw=raw.original
    if "run" in getattr(raw,"__dict__",{}) or raw.pre_run_hooks:
        raise RuntimeError("stacked JIT.run/pre-run hooks forbidden")
    jit=importlib.import_module("triton.runtime.jit")
    compiler=importlib.import_module("triton.compiler.compiler")
    iluvatar=importlib.import_module("triton.backends.iluvatar.compiler")
    for module,expected in ((jit,EXPECTED_JIT),(compiler,EXPECTED_COMPILER),(iluvatar,EXPECTED_BACKEND_COMPILER)):
        if _sha(Path(module.__file__).read_bytes())!=expected:
            raise RuntimeError("unaudited actual compiler/JIT source")
    if (type(raw) is not jit.JITFunction
        or _sha(Path(raw.run.__func__.__code__.co_filename).read_bytes())!=EXPECTED_JIT):
        raise RuntimeError("actual spec JIT method required")
    for method,expected in ((jit.JITFunction.__init__,EXPECTED_JIT),
                            (compiler.CompiledKernel.__init__,EXPECTED_COMPILER),
                            (compiler.CompiledKernel._init_handles,EXPECTED_COMPILER)):
        if _sha(Path(method.__code__.co_filename).read_bytes())!=expected:
            raise RuntimeError("actual spec class implementation changed")
    knobs=raw.run.__func__.__globals__["knobs"]
    if knobs.compilation.override or knobs.runtime.add_stages_inspection_hook is not None:
        raise RuntimeError("global compiler override/inspection hook forbidden")
    candidate=jit.JITFunction(raw.fn,version=raw.version,
        do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),
        debug=raw.debug,noinline=raw.noinline,repr=raw._repr,launch_metadata=raw.launch_metadata)
    if candidate.device_caches is raw.device_caches:
        raise RuntimeError("candidate JIT cache is not independent")
    return Manager(attention,backend,raw,candidate,Path(__file__).parent)
