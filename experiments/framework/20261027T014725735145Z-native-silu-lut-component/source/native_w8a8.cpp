#include <ATen/ATen.h>
#include <ATen/ops/_int_mm.h>
#include <c10/cuda/CUDAGuard.h>
#include <c10/cuda/CUDAStream.h>
#include <c10/cuda/CUDAException.h>
#include <torch/library.h>
extern "C" void private_lut_make(float*,cudaStream_t);
extern "C" void private_lut_epilogue(const int32_t*,const float*,const float*,const float*,void*,int,int,cudaStream_t);
extern "C" void private_lut_domain(const float*,const float*,void*,void*,int,cudaStream_t);
extern "C" void biv150_lut_private_quantize_cached(const void*,int8_t*,float*,int,int,int,int,cudaStream_t);
namespace {
void check_table(const at::Tensor& lut,const at::Tensor& like){
  TORCH_CHECK(lut.is_cuda() && lut.scalar_type()==at::kFloat && lut.is_contiguous() && lut.dim()==1 && lut.numel()==65536 && lut.device()==like.device());
}
at::Tensor make_lut(const at::Tensor& like){
  TORCH_CHECK(like.is_cuda());c10::cuda::CUDAGuard guard(like.device());
  auto table=at::empty({65536},like.options().dtype(at::kFloat));
  private_lut_make(table.data_ptr<float>(),c10::cuda::getCurrentCUDAStream());C10_CUDA_KERNEL_LAUNCH_CHECK();return table;
}
at::Tensor gate_lut(const at::Tensor& x,const at::Tensor& wq,const at::Tensor& scales,const at::Tensor& marker,const at::Tensor& lut){
  TORCH_CHECK(x.is_cuda() && x.scalar_type()==at::kBFloat16 && x.is_contiguous() && x.sizes()==at::IntArrayRef({2048,2048}));
  TORCH_CHECK(wq.is_cuda() && wq.scalar_type()==at::kChar && wq.is_contiguous() && wq.sizes()==at::IntArrayRef({2048,12288}));
  TORCH_CHECK(scales.is_cuda() && scales.scalar_type()==at::kFloat && scales.is_contiguous() && scales.sizes()==at::IntArrayRef({12288}));
  TORCH_CHECK(marker.is_cuda() && marker.scalar_type()==at::kBFloat16 && marker.sizes()==at::IntArrayRef({12288,2048}) && marker.stride(0)==0 && marker.stride(1)==0);
  TORCH_CHECK(x.device()==wq.device() && x.device()==scales.device() && x.device()==marker.device());check_table(lut,x);
  c10::cuda::CUDAGuard guard(x.device());
  // Identical M2048 branch of production linear_impl: no padding/chunks/fallback.
  auto input=x.contiguous();auto output=at::empty({2048,6144},x.options());
  auto aq=at::empty({2048,2048},x.options().dtype(at::kChar));auto sa=at::empty({2048},x.options().dtype(at::kFloat));
  const auto stream=c10::cuda::getCurrentCUDAStream();
  biv150_lut_private_quantize_cached(input.data_ptr<at::BFloat16>(),aq.data_ptr<int8_t>(),sa.data_ptr<float>(),2048,2048,2048,256,stream);
  C10_CUDA_KERNEL_LAUNCH_CHECK();auto acc=at::_int_mm(aq,wq);
  private_lut_epilogue(acc.data_ptr<int32_t>(),sa.data_ptr<float>(),scales.data_ptr<float>(),lut.data_ptr<float>(),output.data_ptr<at::BFloat16>(),2048,12288,stream);
  C10_CUDA_KERNEL_LAUNCH_CHECK();return output;
}
std::vector<at::Tensor> domain(const at::Tensor& lut,const at::Tensor& up){
  check_table(lut,up);TORCH_CHECK(up.is_cuda() && up.scalar_type()==at::kFloat && up.is_contiguous() && up.dim()==1 && up.numel()>=1 && up.numel()<=32);
  c10::cuda::CUDAGuard guard(up.device());auto a=at::empty({up.numel(),65536},up.options().dtype(at::kBFloat16));auto b=at::empty_like(a);
  private_lut_domain(lut.data_ptr<float>(),up.data_ptr<float>(),a.data_ptr<at::BFloat16>(),b.data_ptr<at::BFloat16>(),int(up.numel()),c10::cuda::getCurrentCUDAStream());
  C10_CUDA_KERNEL_LAUNCH_CHECK();return {a,b};
}
}
TORCH_LIBRARY(biv150_silu_lut_component,m){
  m.def("make_lut(Tensor like) -> Tensor");m.def("gate_lut(Tensor x, Tensor wq, Tensor scales, Tensor marker, Tensor lut) -> Tensor");m.def("domain(Tensor lut, Tensor up) -> Tensor[]");
}
TORCH_LIBRARY_IMPL(biv150_silu_lut_component,CUDA,m){m.impl("make_lut",&make_lut);m.impl("gate_lut",&gate_lut);m.impl("domain",&domain);}
