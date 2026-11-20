#!/usr/bin/env python3
"""Apply a pinned, exact-anchor K8 full-page SME lookahead transform."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE / "biv150_native_k8_klookahead_qk.base.cu"
OUT = HERE / "biv150_native_k8_klookahead_sme.cu"
BASE_GIT_BLOB = "3ae5112b5dee65cfd7b8fc9f506f163a4167e0ba"

def replace_once(src: bytes, old: bytes, new: bytes, label: str) -> bytes:
    count = src.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one exact anchor, found {count}")
    return src.replace(old, new, 1)

def transform(src: bytes) -> bytes:
    helper_anchor = b"__device__ __forceinline__ unsigned k_half_index(unsigned slot,unsigned dim){"
    helper = b"""__device__ __forceinline__ Desc key_i8_sme_descriptor(const signed char* base){
 const auto p=reinterpret_cast<std::uintptr_t>(base);
 return Desc{static_cast<int>(p),static_cast<int>(p>>32),-1,256};
}
__device__ __forceinline__ void issue_k_i8_sme(unsigned* stage,const signed char* key,int page,unsigned head){
 const auto* base=key+static_cast<std::int64_t>(page)*16384+head*128;
 const unsigned dst=static_cast<unsigned>(reinterpret_cast<std::uintptr_t>(stage));
 const Desc desc=key_i8_sme_descriptor(base);
 __ivcorex_sme_load_16x1b64_colxfb8(dst,desc,0,0);
 __ivcorex_sme_load_16x1b64_colxfb8(dst+1024,desc,64,0);
}
"""
    src = replace_once(src, helper_anchor, helper + helper_anchor, "insert SME issue helper")

    next_helpers = b"""// Only a later full page in this segment can enter this packed stage.
// Ordinary global reads start AFTER the current V wait8 + ready barrier.
struct PackedNextK { unsigned word[8]; };
__device__ __forceinline__ void read_next_k(PackedNextK& next,const signed char* key,int page,unsigned head,unsigned lane){
 const auto* base=key+static_cast<std::int64_t>(page)*16384+head*128;
 #pragma unroll
 for(unsigned i=0;i<8;++i){
  const unsigned word=lane+i*64,slot=word/32,dim=(word%32)*4;
  next.word[i]=*reinterpret_cast<const unsigned*>(base+slot*256+dim);
 }
}
__device__ __forceinline__ void publish_next_k(unsigned* stage,const PackedNextK& next,unsigned lane){
 #pragma unroll
 for(unsigned i=0;i<8;++i){
  const unsigned word=lane+i*64,slot=word/32,dim=(word%32)*4;
  stage[k_i8_index(slot,dim)/4]=next.word[i];
 }
}
"""
    src = replace_once(src, next_helpers, b"", "remove packed CPU next-K helpers")

    src = replace_once(
        src,
        b"issue_k_i8(stage,key,page,h,16,lane);__syncthreads(); // Prologue K0 ready.",
        b"issue_k_i8_sme(stage,key,page,h);__ivcorex_sl_waitcnt(8ULL);__syncthreads(); // Prologue K0 ready.",
        "full-page K0 prologue",
    )

    src = replace_once(
        src,
        b""" int next_page=0;
 PackedNextK next;
 if(has_next){
  next_page=next_row[next_position/16]; // Page-table read also follows V readiness.
  read_next_k(next,key,next_page,head,lane);
 }
""",
        b""" int next_page=0;
 if(has_next){
  next_page=next_row[next_position/16]; // Only a known full page; after V wait + ready barrier.
  issue_k_i8_sme(stage,key,next_page,head);
 }
""",
        "full-page lookahead issue after V readiness",
    )

    src = replace_once(
        src,
        b""" if(has_next)publish_next_k(stage,next,lane); // Current QK and PV readers have ended.
 __syncthreads(); // Publish dependent K stores; finish current PV before the next V issue.
""",
        b""" if(has_next)__ivcorex_sl_waitcnt(8ULL); // Finish next-page K SME after current PV.
 __syncthreads(); // Finish current PV and K transfer before the next V issue.
""",
        "wait next K after PV and retain page-end barrier",
    )
    return src

def inverse(src: bytes) -> bytes:
    src = replace_once(
        src,
        b"""__device__ __forceinline__ Desc key_i8_sme_descriptor(const signed char* base){
 const auto p=reinterpret_cast<std::uintptr_t>(base);
 return Desc{static_cast<int>(p),static_cast<int>(p>>32),-1,256};
}
__device__ __forceinline__ void issue_k_i8_sme(unsigned* stage,const signed char* key,int page,unsigned head){
 const auto* base=key+static_cast<std::int64_t>(page)*16384+head*128;
 const unsigned dst=static_cast<unsigned>(reinterpret_cast<std::uintptr_t>(stage));
 const Desc desc=key_i8_sme_descriptor(base);
 __ivcorex_sme_load_16x1b64_colxfb8(dst,desc,0,0);
 __ivcorex_sme_load_16x1b64_colxfb8(dst+1024,desc,64,0);
}
__device__ __forceinline__ unsigned k_half_index(unsigned slot,unsigned dim){""",
        b"__device__ __forceinline__ unsigned k_half_index(unsigned slot,unsigned dim){",
        "inverse inserted helper",
    )
    src = replace_once(src,
        b"issue_k_i8_sme(stage,key,page,h);__ivcorex_sl_waitcnt(8ULL);__syncthreads(); // Prologue K0 ready.",
        b"issue_k_i8(stage,key,page,h,16,lane);__syncthreads(); // Prologue K0 ready.",
        "inverse prologue")
    src = replace_once(src,
        b""" int next_page=0;
 if(has_next){
  next_page=next_row[next_position/16]; // Only a known full page; after V wait + ready barrier.
  issue_k_i8_sme(stage,key,next_page,head);
 }
""",
        b""" int next_page=0;
 PackedNextK next;
 if(has_next){
  next_page=next_row[next_position/16]; // Page-table read also follows V readiness.
  read_next_k(next,key,next_page,head,lane);
 }
""",
        "inverse lookahead issue")
    src = replace_once(src,
        b""" if(has_next)__ivcorex_sl_waitcnt(8ULL); // Finish next-page K SME after current PV.
 __syncthreads(); // Finish current PV and K transfer before the next V issue.
""",
        b""" if(has_next)publish_next_k(stage,next,lane); // Current QK and PV readers have ended.
 __syncthreads(); // Publish dependent K stores; finish current PV before the next V issue.
""",
        "inverse post-PV wait")
    original_helpers = b"""// Only a later full page in this segment can enter this packed stage.
// Ordinary global reads start AFTER the current V wait8 + ready barrier.
struct PackedNextK { unsigned word[8]; };
__device__ __forceinline__ void read_next_k(PackedNextK& next,const signed char* key,int page,unsigned head,unsigned lane){
 const auto* base=key+static_cast<std::int64_t>(page)*16384+head*128;
 #pragma unroll
 for(unsigned i=0;i<8;++i){
  const unsigned word=lane+i*64,slot=word/32,dim=(word%32)*4;
  next.word[i]=*reinterpret_cast<const unsigned*>(base+slot*256+dim);
 }
}
__device__ __forceinline__ void publish_next_k(unsigned* stage,const PackedNextK& next,unsigned lane){
 #pragma unroll
 for(unsigned i=0;i<8;++i){
  const unsigned word=lane+i*64,slot=word/32,dim=(word%32)*4;
  stage[k_i8_index(slot,dim)/4]=next.word[i];
 }
}
"""
    return replace_once(src, b"__device__ __forceinline__ int signed_i32_word", original_helpers + b"__device__ __forceinline__ int signed_i32_word", "inverse removed helpers")

def main() -> None:
    src = BASE.read_bytes()
    blob = hashlib.sha1(b"blob " + str(len(src)).encode() + b"\0" + src).hexdigest()
    if blob != BASE_GIT_BLOB:
        raise SystemExit(f"base blob mismatch: {blob}")
    out = transform(src)
    if inverse(out) != src:
        raise SystemExit("inverse transform did not reproduce exact main blob")
    OUT.write_bytes(out)
    pins = {
        "main": "899ce77470b0b539aebc108fd122f668c2d5894d",
        "qk_path": "tools/kernels/biv150_native_k8_klookahead_qk.cu",
        "qk_git_blob": blob,
        "codec_path": "tools/kernels/biv150_native_k8_codec.cuh",
        "codec_git_blob": "e9049826d213e80baf6eb5c3dfddd1598d5f3d35",
        "base_sha256": hashlib.sha256(src).hexdigest(),
        "variant_sha256": hashlib.sha256(out).hexdigest(),
        "inverse_byte_exact": True,
        "transform": ["insert key i8 SME descriptor/issue helper", "prologue full-page issue via two SME loads + wait8 + original barrier", "issue next full K page after current V wait+ready barrier", "remove PackedNextK/read/publish", "wait8 after current PV then retain original page-end barrier"],
        "partial_page": "original masked issue_k_i8 path unchanged; has_next is bounded by full_upper",
        "codec_sha256": hashlib.sha256((HERE / "biv150_native_k8_codec.base.cuh").read_bytes()).hexdigest(),
    }
    (HERE / "pins.json").write_text(json.dumps(pins, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(pins, indent=2))

if __name__ == "__main__":
    main()
