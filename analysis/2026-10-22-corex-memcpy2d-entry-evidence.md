# Corex二维复制入口的实际存在证据

2026-10-22，root在三轮服务作业全部结束后，仅执行CPU文件与ELF读取。没有导入torch/CUDA、加载运行库、创建context或调用设备API；这不是性能或正确性实验。

`experiments/source-audits/20261022T023826Z-memcpy2d-exports/result.json` 的SHA256为 `2334a167fbf0fb3a3131aa2ae7d8c7b9320dd903b1c05a227e9fda3b566f7a40`，目录内保存实际检查脚本。lib64与lib别名解析到同一实库 `/usr/local/corex-4.5.0/lib64/libcudart.so.10.2.89`，8,390,352字节，SHA256 `d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527`。readelf显示cudaMemcpy2DAsync、cudaMemcpy2DAsync_ptsz、cudaMemcpy2D以及错误文本接口为GLOBAL FUNC导出。

顶层cuda_runtime_api.h/runtime.h只是包含IX头文件，不能由其未命中声明断言API不存在。后继 `experiments/source-audits/20261022T024142Z-memcpy2d-header-contract/result.json` SHA256 `e29cd7a7683c93d4071e29341299e4dedde9d5835e71ba0acf632c43d7129438` 保存了定向摘录与头文件哈希，同目录read_headers.py保存实际读取命令：

- `IX/mapping_cudart.h`（ca962a4e…）将cudaMemcpy2DAsync映射为ixMemcpy2DAsync，同时有_ptsz映射。
- `IX/ixrt/ix_runtime_api.h`（7dca9b91…）在457/1046行声明参数为dst、dpitch、src、spitch、width、height、ixMemcpyKind和ixStream_t；尺寸参数为size_t。头文件还包含PTSZ宏路径，不能忽略其stream语义。

存在导出与声明不证明设备上实现完整。下一若实现，需要明确真实枚举值/stream类型、运行时库与PyTorch当前设备及stream兼容、pitch上限、host pinned范围和GPU范围、异步错误后的真实完成处理。禁止仅凭函数返回成功就释放旧页或host缓冲区，也不能把NVIDIA文档当成本机Corex实际验证。

这条候选保持全部安全前缀、每页字节和原逻辑次序，只考虑对真实正等差页段减少SAVE提交；不截短R，不以重算换调用数，不修改victim策略。具体实际几何与一手契约由hardware的后继报告给出。尚无新runtime或GPU门，不能承诺收益。

回传原件均逐SHA验证。首次本地JSON读取使用Windows默认GBK失败，随后改为显式UTF-8读取通过，原件没有改动；后续Python读取本项目中文JSON应明确encoding。该失败与修正仅影响本地读取，不是设备失败。

## 03:03 UTC追加：真实ABI证据

`experiments/source-audits/20261022T030314Z-memcpy2d-abi/result.json`（`f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576`）保存实际文件哈希和行号片段：`ixMemcpyDeviceToHost=2`，`ixStream_t`为`IXDRVstream_st*`，GNU平台`IXRTAPI`为空，`ixDevAttrMaxPitch=11`。Torch 2.10实际`torch/cuda/streams.py`的`_as_parameter_`将`cuda_stream`转为`ctypes.c_void_p`；这给Python到自定义C接口的传参依据。

同一Corex库确有`ixMemcpyAsync`、`ixMemcpy2DAsync`和`ixDeviceGetAttribute`导出，本机g++为13.3。后继桥使用实际`cuda_runtime_api.h`编译，让头文件负责cuda→ix映射与枚举，避免手工定义SDK ABI。新脚本SHA `6de7944a0e0f5593d9ed66a8af0eb2cf23b147bf39cba8d2e4204e69399ed53a`，本地和远端相同。此追加仍只读CPU文件，没有加载库或运行API；设备pitch值、真实stream完成和全字节结果仍由下一短门判断。
