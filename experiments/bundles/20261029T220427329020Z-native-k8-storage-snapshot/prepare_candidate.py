#!/usr/bin/env python3
"""Materialize an isolated, exact-source-pinned storage snapshot candidate."""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[0] / "framework-main899-shallow-20261029" / "vllm_fl" / "patches" / "biv150_konly_encoded_native.py"
SOURCE_SHA256 = "957bc4bca3262e76c419ccd6fb77592da4967338223fc602797332077fe85579"
SOURCE_BYTES = 12913

OLD_STORAGE = '''def storage(t):
    s=t.untyped_storage();return (int(s._cdata),int(s.data_ptr()),int(s.data_ptr())+int(s.nbytes()))


def overlaps(a,b):
    _,x,y=storage(a);_,u,v=storage(b);return x<v and u<y


def bounds(t):
    widths={'torch.bfloat16':2,'torch.int8':1,'torch.float32':4,'torch.int32':4,'torch.int64':8}
    need(str(t.dtype) in widths,'known operand dtype')
    width=widths[str(t.dtype)];shape=tuple(t.shape);strides=tuple(t.stride())
    need(len(shape)==len(strides) and all(type(n) is int and n>=0 for n in shape) and all(type(v) is int and v>0 for v in strides),'operand geometry')
    _,start,end=storage(t);pointer=int(t.data_ptr());offset=int(t.storage_offset())
    extent=0 if 0 in shape else 1+sum((n-1)*s for n,s in zip(shape,strides))
    need(pointer==start+offset*width and start<=pointer and pointer+extent*width<=end,'operand backing bounds')
'''

NEW_STORAGE = '''def storage(t):
    s=t.untyped_storage();return (int(s._cdata),int(s.data_ptr()),int(s.data_ptr())+int(s.nbytes()))


def storage_snapshot(t, cache):
    """Cache only the backing-storage range for this exact Tensor object."""
    key=id(t)
    cached=cache.get(key)
    if cached is not None and cached[0] is t:
        return cached[1]
    s=t.untyped_storage()
    start=int(s.data_ptr());value=(int(s._cdata),start,start+int(s.nbytes()))
    # Keep the Tensor alive and key by object identity, never by shared storage.
    cache[key]=(t,value)
    return value


def overlaps(a,b,cache=None):
    if cache is None:
        _,x,y=storage(a);_,u,v=storage(b)
    else:
        _,x,y=storage_snapshot(a,cache);_,u,v=storage_snapshot(b,cache)
    return x<v and u<y


def bounds(t,cache=None):
    widths={'torch.bfloat16':2,'torch.int8':1,'torch.float32':4,'torch.int32':4,'torch.int64':8}
    need(str(t.dtype) in widths,'known operand dtype')
    width=widths[str(t.dtype)];shape=tuple(t.shape);strides=tuple(t.stride())
    need(len(shape)==len(strides) and all(type(n) is int and n>=0 for n in shape) and all(type(v) is int and v>0 for v in strides),'operand geometry')
    _,start,end=(storage(t) if cache is None else storage_snapshot(t,cache));pointer=int(t.data_ptr());offset=int(t.storage_offset())
    extent=0 if 0 in shape else 1+sum((n-1)*s for n,s in zip(shape,strides))
    need(pointer==start+offset*width and start<=pointer and pointer+extent*width<=end,'operand backing bounds')
'''

OLD_BINDING = "('need','storage','overlaps','bounds','geometry')"
NEW_BINDING = "('need','storage_snapshot','storage','overlaps','bounds','geometry')"
OLD_VALIDATE = "        for t in tensors:bounds(t)\n"
NEW_VALIDATE = "        storage_snapshots={}\n        for t in tensors:bounds(t,storage_snapshots)\n"
OLD_ALIAS = "overlaps(src,k)"
NEW_ALIAS = "overlaps(src,k,storage_snapshots)"
OLD_OUT_ALIAS = "overlaps(out,src)"
NEW_OUT_ALIAS = "overlaps(out,src,storage_snapshots)"
OLD_OUT_PAIR = "overlaps(out,other)"
NEW_OUT_PAIR = "overlaps(out,other,storage_snapshots)"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count=text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one pinned {label} anchor, got {count}")
    return text.replace(old,new,1)


def main() -> None:
    if not SOURCE.is_file():
        raise RuntimeError(f"pinned source missing: {SOURCE}")
    raw=SOURCE.read_bytes()
    if len(raw)!=SOURCE_BYTES or sha(raw)!=SOURCE_SHA256:
        raise RuntimeError("main899 source bytes differ from the reviewed pin")
    original=raw.decode("utf-8")
    # The pinned Windows checkout is CRLF; transform normalized text, then
    # restore its original newline convention so the diff contains only logic.
    newline="\r\n" if b"\r\n" in raw else "\n"
    normalized=original.replace("\r\n","\n")
    candidate=replace_once(normalized,OLD_STORAGE,NEW_STORAGE,"storage helpers")
    binding_count=candidate.count(OLD_BINDING)
    if binding_count != 2:
        raise RuntimeError(f"expected two pinned helper binding anchors, got {binding_count}")
    candidate=candidate.replace(OLD_BINDING,NEW_BINDING)
    candidate=replace_once(candidate,OLD_VALIDATE,NEW_VALIDATE,"validate bounds loop")
    candidate=replace_once(candidate,OLD_ALIAS,NEW_ALIAS,"source/cache alias check")
    candidate=replace_once(candidate,OLD_OUT_ALIAS,NEW_OUT_ALIAS,"scratch/source alias check")
    candidate=replace_once(candidate,OLD_OUT_PAIR,NEW_OUT_PAIR,"scratch/scratch alias check")
    if newline != "\n":
        candidate=candidate.replace("\n",newline)
    compile(candidate,str(HERE/"candidate.py"),"exec")
    (HERE/"baseline.py").write_bytes(raw)
    cand_bytes=candidate.encode("utf-8")
    (HERE/"candidate.py").write_bytes(cand_bytes)
    diff="".join(difflib.unified_diff(original.splitlines(True),candidate.splitlines(True),
        fromfile="main899/biv150_konly_encoded_native.py",tofile="candidate/biv150_konly_encoded_native.py"))
    (HERE/"candidate.patch").write_text(diff,encoding="utf-8",newline="\n")
    receipt={"schema":"native-k8-storage-snapshot-candidate-v1","source":str(SOURCE),
        "source_commit":"899ce77470b0b539aebc108fd122f668c2d5894d",
        "source_bytes":len(raw),"source_sha256":sha(raw),"candidate_bytes":len(cand_bytes),
        "candidate_sha256":sha(cand_bytes),"patch_sha256":sha(diff.encode("utf-8")),
        "production_source_modified":False,"device_or_remote_action":False,
        "scope":"仅同一次Native Adapter.validate调用内按Tensor对象身份缓存storage identity与backing range；data_ptr/offset仍每次bounds读取，所有原检查保留。"}
    (HERE/"source-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")
    print(json.dumps(receipt,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
