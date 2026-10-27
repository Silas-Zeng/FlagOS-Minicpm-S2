#include <ATen/ATen.h>
#include <c10/cuda/CUDAGuard.h>
#include <c10/cuda/CUDAStream.h>
#include <c10/cuda/CUDAException.h>
#include <torch/library.h>
extern "C" void launch_corex_native_page16(const void*,const void*,const void*,const int*,float,float*,float*,float*,float*,float*,void*,unsigned*,cudaStream_t);
std::vector<at::Tensor> page16(const at::Tensor& q,const at::Tensor& cache,const at::Tensor& table,double scale){
 TORCH_CHECK(q.is_cuda() && cache.is_cuda() && table.is_cuda() && q.device()==cache.device() && q.device()==table.device());
 TORCH_CHECK(q.scalar_type()==at::kBFloat16 && q.sizes()==at::IntArrayRef({1,16,128}) && q.is_contiguous());
 TORCH_CHECK(cache.scalar_type()==at::kBFloat16 && cache.sizes()==at::IntArrayRef({4,2,16,2,128}) && cache.is_contiguous());
 TORCH_CHECK(table.scalar_type()==at::kInt && table.sizes()==at::IntArrayRef({1,1}) && table.is_contiguous());
 c10::cuda::CUDAGuard guard(q.device());
 auto options=q.options().dtype(at::kFloat);
 auto acc=at::empty({1,16,128},options),maximum=at::empty({1,16},options),sum=at::empty({1,16},options);
 auto score=at::empty({16,16},options),prob=at::empty({16,16},options),pbf16=at::empty({16,16},q.options());
 auto shared=at::empty({2,2048},q.options().dtype(at::kInt));
 const auto* base=cache.data_ptr<at::BFloat16>();
 launch_corex_native_page16(q.data_ptr(),base,base+4096,table.data_ptr<int>(),static_cast<float>(scale),
  acc.data_ptr<float>(),maximum.data_ptr<float>(),sum.data_ptr<float>(),score.data_ptr<float>(),prob.data_ptr<float>(),pbf16.data_ptr(),reinterpret_cast<unsigned*>(shared.data_ptr<int>()),c10::cuda::getCurrentCUDAStream());
 C10_CUDA_KERNEL_LAUNCH_CHECK();
 return {acc,maximum,sum,score,prob,pbf16,shared};
}
TORCH_LIBRARY(corex_native_page16_probe,m){m.def("page16(Tensor query, Tensor cache, Tensor table, float scale) -> Tensor[]");}
TORCH_LIBRARY_IMPL(corex_native_page16_probe,CUDA,m){m.impl("page16",&page16);}
