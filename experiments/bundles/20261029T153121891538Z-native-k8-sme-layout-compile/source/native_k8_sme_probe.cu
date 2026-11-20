// Isolated layout equivalence probe only. No attention math or timing.
#include <cstdint>
#include <cuda_runtime.h>

#if defined(__IX_ARCH__) && (!defined(__ivcore11__) || __IVCORE_ARCH__ != 11)
#error "This probe is pinned to BI-V150 / ivcore11."
#endif

using Desc = int __attribute__((ext_vector_type(4)));

__device__ __forceinline__ unsigned k_i8_index(unsigned slot, unsigned dim) {
  const unsigned panel = dim / 64, within = dim % 64;
  const unsigned quartet = within / 4, byte = within % 4;
  const unsigned bank = slot / 4, subslot = slot % 4;
  return panel * 1024 + bank * 256 + (quartet % 4) * 64 +
         ((quartet / 4) ^ bank) * 16 + subslot * 4 + byte;
}

__device__ __forceinline__ const signed char* key_base(
    const signed char* key, unsigned page, unsigned head) {
  return key + static_cast<std::uint64_t>(page) * 16384 + head * 128;
}

__device__ __forceinline__ Desc key_descriptor(const signed char* base) {
  const auto p = reinterpret_cast<std::uintptr_t>(base);
  // Utility.h's descriptor lane 3 is strideBytes; the selected K head has
  // sixteen 128-byte rows interleaved at a 256-byte row pitch.
  return Desc{static_cast<int>(p), static_cast<int>(p >> 32), -1, 256};
}

__device__ __forceinline__ void dump_stage(const unsigned* stage,
                                            unsigned* out, unsigned lane) {
  for (unsigned i = lane; i < 512; i += 64) out[i] = stage[i];
}

__global__ void k_i8_copy_probe(const signed char* key, unsigned page,
                                unsigned head, unsigned* out) {
  __shared__ __align__(16) unsigned stage[512];
  const unsigned lane = threadIdx.x;
  const signed char* base = key_base(key, page, head);
  // Same full-page word reads and swizzled shared layout as NativeK8.
  for (unsigned word = lane; word < 512; word += 64) {
    const unsigned slot = word / 32, dim = (word % 32) * 4;
    const unsigned bits = *reinterpret_cast<const unsigned*>(base + slot * 256 + dim);
    stage[k_i8_index(slot, dim) / 4] = bits;
  }
  __syncthreads();
  dump_stage(stage, out, lane);
}

__global__ void k_i8_sme_probe(const signed char* key, unsigned page,
                               unsigned head, unsigned* out) {
  __shared__ __align__(16) unsigned stage[512];
  const signed char* base = key_base(key, page, head);
  const unsigned dst = static_cast<unsigned>(reinterpret_cast<std::uintptr_t>(stage));
  const Desc desc = key_descriptor(base);
  // Each colxfb8 tile covers 16 slots by 64 contiguous K bytes. The two
  // contiguous K halves fill exactly the 16 x 128-byte head page (2048 B).
  __ivcorex_sme_load_16x1b64_colxfb8(dst, desc, 0, 0);
  __ivcorex_sme_load_16x1b64_colxfb8(dst + 1024, desc, 64, 0);
  __ivcorex_sl_waitcnt(8ULL);
  __syncthreads();
  dump_stage(stage, out, threadIdx.x);
}

extern "C" void launch_k_i8_copy_probe(const signed char* key,
                                        unsigned page, unsigned head,
                                        unsigned* out, cudaStream_t stream) {
  k_i8_copy_probe<<<1, 64, 0, stream>>>(key, page, head, out);
}

extern "C" void launch_k_i8_sme_probe(const signed char* key,
                                       unsigned page, unsigned head,
                                       unsigned* out, cudaStream_t stream) {
  k_i8_sme_probe<<<1, 64, 0, stream>>>(key, page, head, out);
}
