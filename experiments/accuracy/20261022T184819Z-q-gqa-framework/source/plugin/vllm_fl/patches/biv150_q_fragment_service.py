"""默认关闭：exact54c/ff64 Q fragment服务候选；私有JIT compile包装，无全局hook。"""
from __future__ import annotations
import atexit
import hashlib
import importlib
import inspect
import json
import os
import re
import sys
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
EXPECTED_GQA = "1a81409ba23a149081f7fc257460ea1512cbfdceeb0af32a2698994958749b9a"

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


def _abi(src):
    return (_freeze(src.signature),_freeze(src.constants),_freeze(src.attrs))


class _Launch:
    def __init__(self,manager): self.manager=manager
    def __getattr__(self,name): return getattr(self.manager.original_kernel,name)
    def __getitem__(self,grid):
        m=self.manager
        original=m.original_kernel[grid]
        candidate=m.candidate[grid]
        def invoke(*args,**kwargs):
            selected=False
            try:
                selected=(not args and "ir_override" not in kwargs and _eligible(kwargs)
                          and m.async_mode.get() is None
                          and not m.raw.pre_run_hooks and not m.candidate.pre_run_hooks
                          and (m.device is None or kwargs["query_ptr"].device.index==m.device)
                          and not m.attention.torch.cuda.is_current_stream_capturing())
            except Exception:
                selected=False
            if selected:
                device=kwargs["query_ptr"].device.index
                # Binder initialization itself assigns self.compile. Initialize
                # only this private cache first, then replace its compile field.
                m._ensure(device)
                compiled=candidate(*args,**kwargs)
                try:
                    if compiled is not None and compiled.hash in m.optimized:
                        m.selected_calls+=1
                        if compiled.hash not in m.resource_observed:
                            m.resource_observed.add(compiled.hash)
                            m.optimized[compiled.hash]["loaded_resources"]=_resources(compiled)
                    else:
                        m.fallback_calls+=1
                except Exception as error:
                    # Diagnostic failure cannot turn a successful launch into a
                    # model error. Preserve the exact original return; no retry.
                    if len(m.record_errors)<m.MAX_RECORDS:
                        m.record_errors.append("post-launch:"+type(error).__name__)
                return compiled
            if kwargs.get("IS_3D") is True: m.original_3d_calls+=1
            else: m.fallback_calls+=1
            return original(*args,**kwargs)
        return invoke


class Manager:
    MAX_RECORDS=8
    def __init__(self,attention,backend,raw,candidate,artifact_dir):
        self.attention,self.backend,self.raw,self.candidate=attention,backend,raw,candidate
        self.original_kernel=attention.kernel_unified_attention
        self.original_forward=backend.TritonAttentionImpl.forward
        self.wrapper=_Launch(self)
        self.artifact_dir=Path(artifact_dir)
        self.artifact_dir.mkdir(parents=True,exist_ok=False)
        self.async_mode=raw.run.__func__.__globals__["_async_compile"].active_mode
        self.original_compile=self.device=self.entry=None
        self.active=False
        self.selected_calls=self.fallback_calls=self.original_3d_calls=0
        self.selected_compiles=self.fallback_compiles=0
        self.records=[];self.optimized={};self.resource_observed=set()
        self.record_errors=[];self.omitted_records=0
    def _ensure(self,device):
        if self.device is None:
            entry=self.candidate.device_caches[device]
            compile_fn=self.candidate.compile
            if _sha(Path(compile_fn.__code__.co_filename).read_bytes())!=EXPECTED_COMPILER:
                raise RuntimeError("actual private compile callable changed")
            self.original_compile=compile_fn
            self.device,self.entry=device,entry
            self.candidate.compile=self._compile
        elif device!=self.device or self.candidate.device_caches.get(device) is not self.entry:
            raise RuntimeError("private candidate device/binder changed")
        if self.candidate.compile!=self._compile:
            raise RuntimeError("private compile wrapper overwritten")
    def _record(self,record,normal):
        if len(self.records)>=self.MAX_RECORDS:
            self.omitted_records+=1
            return
        self.records.append(record)
        try:
            number=len(self.records)
            path=self.artifact_dir/("recipe-%02d-original.ttgir"%number)
            with path.open("x",encoding="utf-8") as stream:stream.write(normal.asm["ttgir"])
            record["original_ttgir_filename"]=path.name
            with (self.artifact_dir/("recipe-%02d.json"%number)).open("x",encoding="utf-8") as stream:
                json.dump(record,stream,ensure_ascii=False,indent=2)
            print("BIV150_Q_FRAGMENT_RECIPE "+json.dumps(record,ensure_ascii=False),flush=True)
        except Exception as error:
            self.record_errors.append(type(error).__name__)
    def _compile(self,src,target=None,options=None,_env_vars=None):
        # Native binder/prefix already supplied true ASTSource and full options.
        if self.async_mode.get() is not None:
            raise RuntimeError("async compilation must use original Attention route")
        # This original failure is propagated without candidate handling.
        normal=self.original_compile(src,target=target,options=options,_env_vars=_env_vars)
        record={"normal_hash":normal.hash,"mode":"fallback","reason":"unknown IR"}
        try:
            record.update(ttgir_sha256=_sha(normal.asm["ttgir"].encode()),target=str(target),
                          abi=_abi(src),options=_freeze(options),normal_resources=_resources(normal))
            if (src.fn is not self.candidate or record["ttgir_sha256"]!=EXPECTED_TTGIR
                or options.get("ir_override") is not None
                or (options.get("num_warps"),options.get("num_stages"))!=(8,1)):
                self.fallback_compiles+=1
                self._record(record,normal)
                return normal
            changed=transform_ir(normal.asm["ttgir"].encode())
            sha=_sha(changed)
            path=self.artifact_dir/("q-fragment-"+sha+".ttgir")
            if path.exists():
                if _sha(path.read_bytes())!=sha:raise RuntimeError("existing override content changed")
            else:
                with path.open("xb") as stream:stream.write(changed)
                if _sha(path.read_bytes())!=sha:raise RuntimeError("override write verification failed")
            replacement=dict(options)
            replacement["ir_override"]=str(path)
            # No src/options mutation, global hook, or kernel launch in this call.
            compiled=self.original_compile(src,target=target,options=replacement,_env_vars=_env_vars)
            if compiled.hash==normal.hash or _abi(compiled.src)!=_abi(src):
                raise RuntimeError("Q-hoist ABI/constants/attrs/cache identity mismatch")
            proof=lowered_proof(compiled.asm["ttgir"],compiled.asm["llir"])
            if not proof["mechanism_pass"]:
                record.update(reason="compiler did not retain Q-read removal",mechanism=proof)
                self.fallback_compiles+=1
                self._record(record,normal)
                return normal
            if _sha(path.read_bytes())!=sha:raise RuntimeError("override changed during compile")
            record.update(mode="selected",reason="exact audited Q fragment transform",candidate_hash=compiled.hash,
                          override_sha256=sha,override_filename=path.name,mechanism=proof,
                          candidate_resources=_resources(compiled))
        except Exception as error:
            # Only cold candidate preparation failed. Normal is already compiled,
            # and neither route has launched; do not compile/launch normal again.
            record.update(mode="fallback",reason="candidate preparation failed",
                          candidate_error_type=type(error).__name__,candidate_error=str(error))
            self.fallback_compiles+=1
            self._record(record,normal)
            return normal
        self.selected_compiles+=1
        self.optimized[compiled.hash]=record
        self._record(record,normal)
        if any(record is item for item in self.records):
            try:_resources(compiled,self.artifact_dir,"candidate-"+compiled.hash[:16])
            except Exception as error:self.record_errors.append(type(error).__name__)
        return compiled
    def install(self):
        if self.attention.kernel_unified_attention is not self.original_kernel:
            raise RuntimeError("Attention binding changed before install")
        self.attention.kernel_unified_attention=self.wrapper
        self.active=True
        return self
    def restore(self):
        if self.active:
            if self.attention.kernel_unified_attention is not self.wrapper:
                raise RuntimeError("Attention binding changed before restore")
            self.attention.kernel_unified_attention=self.original_kernel
        self.active=False
    def snapshot(self):
        return {"selected_calls":self.selected_calls,"fallback_calls":self.fallback_calls,
                "original_3d_calls":self.original_3d_calls,"selected_compiles":self.selected_compiles,
                "fallback_compiles":self.fallback_compiles,"compile_records":self.records,
                "record_errors":self.record_errors,"omitted_records":self.omitted_records,
                "private_jit_cache":self.raw.device_caches is not self.candidate.device_caches,
                "active":self.active,"pid":os.getpid()}
    def save_summary(self):
        try:
            temp=self.artifact_dir/"summary.tmp"
            temp.write_text(json.dumps(self.snapshot(),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            os.replace(temp,self.artifact_dir/"summary.json")
        except Exception:pass



def _audited_unified_binding(attention, backend):
    """安装时识别exact GQA；不unwrap调用、不重绑任何统一入口。"""
    wrapper = attention.unified_attention
    if backend.unified_attention is not wrapper:
        return False
    if inspect.isfunction(wrapper) and wrapper.__globals__ is vars(attention):
        return True  # 原77b canonical资格分支保持。
    gqa = sys.modules.get("vllm_fl.patches.biv150_gqa_decode")
    if (gqa is None or not inspect.isfunction(wrapper)
            or wrapper.__globals__ is not vars(gqa)
            or _sha(Path(gqa.__file__).read_bytes()) != EXPECTED_GQA
            or Path(wrapper.__code__.co_filename).resolve() != Path(gqa.__file__).resolve()
            or wrapper.__code__.co_name != "patched"
            or wrapper.__code__.co_freevars != ("original",)
            or not getattr(attention, "_biv150_gqa_decode_installed", False)):
        return False
    cells = dict(zip(wrapper.__code__.co_freevars, wrapper.__closure__ or ()))
    original = cells["original"].cell_contents
    return (inspect.isfunction(original) and getattr(wrapper, "__wrapped__", None) is original
            and original.__globals__ is vars(attention)
            and original.__code__.co_name == "unified_attention"
            and Path(original.__code__.co_filename).resolve() == Path(attention.__file__).resolve())


_MANAGER=None
def install(*,artifact_dir):
    """显式调用才启用；由runner在MiniCPM严格scope、原C2/C3之后调用。"""
    global _MANAGER
    attention=importlib.import_module("vllm.v1.attention.ops.triton_unified_attention")
    if _MANAGER is not None:
        if _MANAGER.active and attention.kernel_unified_attention is _MANAGER.wrapper:return _MANAGER
        raise RuntimeError("Q fragment manager identity changed")
    helpers=importlib.import_module("vllm.v1.attention.ops.triton_attention_helpers")
    backend=importlib.import_module("vllm.v1.attention.backends.triton_attn")
    for module,expected in ((attention,EXPECTED_ATTENTION),(helpers,EXPECTED_HELPERS),(backend,EXPECTED_BACKEND)):
        if _sha(Path(module.__file__).read_bytes())!=expected:raise RuntimeError("unaudited Attention source")
    if (attention.current_platform.vendor_name!="iluvatar"
        or not _audited_unified_binding(attention, backend)):
        raise RuntimeError("unaudited platform/Attention binding")
    quant=attention.KVQuantMode
    if (quant.__module__!="vllm.v1.kv_cache_interface" or quant.__name__!="KVQuantMode" or not issubclass(quant,IntEnum)
        or _sha(Path(quant.is_per_token_head.fget.__code__.co_filename).read_bytes())!=EXPECTED_KV_INTERFACE):
        raise RuntimeError("unaudited KVQuantMode")
    outer=attention.kernel_unified_attention
    code=getattr(type(outer).__getitem__,"__code__",None)
    if code is None or _sha(Path(code.co_filename).read_bytes())!=EXPECTED_C2:raise RuntimeError("original C2 required")
    raw=outer
    for _ in range(4):
        if "original" not in getattr(raw,"__dict__",{}):break
        raw=raw.original
    jit=importlib.import_module("triton.runtime.jit")
    compiler=importlib.import_module("triton.compiler.compiler")
    iluvatar=importlib.import_module("triton.backends.iluvatar.compiler")
    for module,sha in ((jit,EXPECTED_JIT),(compiler,EXPECTED_COMPILER),(iluvatar,EXPECTED_BACKEND_COMPILER)):
        if _sha(Path(module.__file__).read_bytes())!=sha:raise RuntimeError("unaudited compiler module")
    for method,sha in ((jit.JITFunction.__init__,EXPECTED_JIT),(jit.JITFunction.run,EXPECTED_JIT),
                       (compiler.CompiledKernel.__init__,EXPECTED_COMPILER),(compiler.CompiledKernel._init_handles,EXPECTED_COMPILER)):
        if _sha(Path(method.__code__.co_filename).read_bytes())!=sha:raise RuntimeError("unaudited actual class")
    if type(raw) is not jit.JITFunction or "run" in vars(raw) or raw.pre_run_hooks:
        raise RuntimeError("plain original JIT required")
    knobs=raw.run.__func__.__globals__["knobs"]
    if knobs.compilation.override or knobs.runtime.add_stages_inspection_hook is not None:
        raise RuntimeError("global compiler override/hook forbidden")
    candidate=jit.JITFunction(raw.fn,version=raw.version,do_not_specialize=list(raw.do_not_specialize),
        do_not_specialize_on_alignment=list(raw.do_not_specialize_on_alignment),debug=raw.debug,
        noinline=raw.noinline,repr=raw._repr,launch_metadata=raw.launch_metadata)
    manager=Manager(attention,backend,raw,candidate,artifact_dir)
    if candidate.device_caches is raw.device_caches:raise RuntimeError("private cache unexpectedly aliases")
    try:
        manager.install()
        atexit.register(manager.save_summary)
    except BaseException:
        manager.restore()
        raise
    _MANAGER=manager
    return manager
