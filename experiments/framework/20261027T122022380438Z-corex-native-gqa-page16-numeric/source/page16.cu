// Single-page numerical diagnostic, not a complete Attention kernel.
#include <cstdint>
#include <type_traits>
#include <cmath>
#include <cuda_runtime.h>
#include <math_functions.h>
#include <cuda_bf16.h>
#include <mma.h>

#if defined(__IX_ARCH__) && (!defined(__ivcore11__) || __IVCORE_ARCH__ != 11)
#error "Bound to actual BI-V150/native14f ivcore11 target"
#endif

#if defined(__IX_ARCH__)
namespace {
using QKShape=nvcuda::wmma::MMBaseInfo<16,16,16,16,16,128>;
using PVShape=nvcuda::wmma::MMBaseInfo<16,16,16,16,128,16>;
template<class S>using A=nvcuda::wmma::FragmentA<S,__nv_bfloat16,nvcuda::wmma::row_major>;
template<class S>using BCol=nvcuda::wmma::FragmentB<S,__nv_bfloat16,nvcuda::wmma::col_major>;
template<class S>using BRow=nvcuda::wmma::FragmentB<S,__nv_bfloat16,nvcuda::wmma::row_major>;
template<class S>using C=nvcuda::wmma::FragmentC<S,float>;
using Desc=int __attribute__((ext_vector_type(4)));
static_assert(sizeof(A<QKShape>)==8 && sizeof(BCol<QKShape>)==8 && sizeof(C<QKShape>)==16,"SDK fragment changed");

__device__ __forceinline__ unsigned raw16(__nv_bfloat16 x){union{__nv_bfloat16 b;unsigned short u;}v;v.b=x;return v.u;}
__device__ __forceinline__ unsigned pair_bits(__nv_bfloat16 a,__nv_bfloat16 b){return raw16(a)|(raw16(b)<<16);}
__device__ __forceinline__ __nv_bfloat16 from_bits(unsigned x){union{__nv_bfloat16 b;unsigned short u;}v;v.u=static_cast<unsigned short>(x);return v.b;}
__device__ __forceinline__ Desc descriptor(const __nv_bfloat16* base,int page,unsigned head){
 const auto p=reinterpret_cast<std::uintptr_t>(base+static_cast<std::uint64_t>(page)*8192+head*128);
 return Desc{static_cast<int>(p),static_cast<int>(p>>32),-1,512};
}
__device__ __forceinline__ float shuffle(float x,unsigned index){return __shfl(x,index,64);}
__device__ __forceinline__ unsigned shuffle_bits(unsigned x,unsigned index){return static_cast<unsigned>(__shfl(static_cast<int>(x),index,64));}
}
#endif

extern "C" __global__ void corex_native_page16(
 const __nv_bfloat16* query,const __nv_bfloat16* key,const __nv_bfloat16* value,
 const int* block_table,float scale,float* acc_out,float* max_out,float* sum_out,
 float* score_out,float* probability_out,__nv_bfloat16* pbf16_out,unsigned* shared_out){
#if defined(__IX_ARCH__)
 const unsigned lane=__ivcorex_lane_id(),h=blockIdx.x,g=lane/16,col=lane%16;
 // Inverse of production Q-stage stores/loads, verified symbolically on CPU.
 A<QKShape> q[8];
 #pragma unroll
 for(unsigned k=0;k<8;++k){
  unsigned pair=pair_bits(query[(h*8+2*g)*128+16*k+col],query[(h*8+2*g+1)*128+16*k+col]);
  q[k][0]=pair;q[k][1]=pair;
 }
 __shared__ __align__(16) unsigned stage[2048];
 const unsigned dst=static_cast<unsigned>(reinterpret_cast<std::uintptr_t>(stage));
 const auto kd=descriptor(key,block_table[0],h),vd=descriptor(value,block_table[0],h);
 __ivcorex_sme_load_16x1b64_colxfb16(dst,kd,0,0);
 __ivcorex_sme_load_16x1b64_colxfb16(dst+1024,kd,64,0);
 __ivcorex_sme_load_16x1b64_colxfb16(dst+2048,kd,128,0);
 __ivcorex_sme_load_16x1b64_colxfb16(dst+3072,kd,192,0);
 __ivcorex_sl_waitcnt(8ULL);
 __ivcorex_sme_load_16x1b64_rowxfb16(dst+4096,vd,0,0);
 __ivcorex_sme_load_16x1b64_rowxfb16(dst+5120,vd,64,0);
 __ivcorex_sme_load_16x1b64_rowxfb16(dst+6144,vd,128,0);
 __ivcorex_sme_load_16x1b64_rowxfb16(dst+7168,vd,192,0);
 __ivcorex_sl_waitcnt(8ULL);__syncthreads();
 // Raw shared copy is diagnostic output, never part of a future timing claim.
 for(unsigned i=lane;i<2048;i+=64)shared_out[h*2048+i]=stage[i];
 C<QKShape> score;
 #pragma unroll
 for(unsigned k=0;k<8;++k){
  BCol<QKShape> b;nvcuda::wmma::load_matrix_sync_tcu(b,stage,0,k);
  nvcuda::wmma::mma_sync_tcu(score,q[k],b,score);
 }
 const float s0=score[0]*scale,s1=score[1]*scale;
 float m0=s0,m1=s1;
 #pragma unroll
 for(unsigned mask=8;mask;mask>>=1){m0=fmaxf(m0,shuffle(m0,lane^mask));m1=fmaxf(m1,shuffle(m1,lane^mask));}
 // Actual LLVM must lower these to original ex2.approx.ftz before GPU admission.
 const float p0=exp2f(s0-m0),p1=exp2f(s1-m1);
 float l0=p0,l1=p1;
 #pragma unroll
 for(unsigned mask=8;mask;mask>>=1){l0=l0+shuffle(l0,lane^mask);l1=l1+shuffle(l1,lane^mask);}
 const auto pb0=__float2bfloat16_rn(p0),pb1=__float2bfloat16_rn(p1);
 const unsigned row0=h*8+g,row1=row0+4;
 score_out[row0*16+col]=s0;score_out[row1*16+col]=s1;
 probability_out[row0*16+col]=p0;probability_out[row1*16+col]=p1;
 pbf16_out[row0*16+col]=pb0;pbf16_out[row1*16+col]=pb1;
 if(col==0){max_out[row0]=m0*0.6931471805599453f;max_out[row1]=m1*0.6931471805599453f;sum_out[row0]=l0;sum_out[row1]=l1;}
 // Exact production LLVM 594–609: source selects, lane bit4/5 permutation,
 // xor16 peer, then bit5 select. No inferred independence of MMA components.
 const unsigned pa=(lane&16)?raw16(pb1):raw16(pb0),pb=(lane&16)?raw16(pb0):raw16(pb1);
 const unsigned index=((lane&16)<<1)|((lane&32)>>1)|(lane&15);
 const unsigned u=shuffle_bits(pa,index),v=shuffle_bits(pb,index^16);
 A<PVShape> p;
 const unsigned packed=(lane&32)?pair_bits(from_bits(v),from_bits(u)):pair_bits(from_bits(u),from_bits(v));
 p[0]=packed;p[1]=packed;
 #pragma unroll
 for(unsigned n=0;n<8;++n){
  BRow<PVShape> b;C<PVShape> output;
  nvcuda::wmma::load_matrix_sync_tcu(b,stage+1024,n,0);
  nvcuda::wmma::mma_sync_tcu(output,p,b,output);
  // Current producer stores components 0/2 and 1/3 to the same locations,
  // with 2/3 last. Keep its observable final store, not an assumed alias.
  acc_out[row0*128+n*16+col]=output[2];
  acc_out[row1*128+n*16+col]=output[3];
 }
#endif
}

extern "C" void launch_corex_native_page16(
 const void* q,const void* k,const void* v,const int* table,float scale,
 float* acc,float* maximum,float* sum,float* score,float* probability,void* pbf16,
 unsigned* shared,cudaStream_t stream){
 corex_native_page16<<<2,64,0,stream>>>(static_cast<const __nv_bfloat16*>(q),
  static_cast<const __nv_bfloat16*>(k),static_cast<const __nv_bfloat16*>(v),table,
  scale,acc,maximum,sum,score,probability,static_cast<__nv_bfloat16*>(pbf16),shared);
}
