# 按真实正等差页段做异步2D拷贝：保全KV的设计证据

仅天数BI-V150本实例、MiniCPM5-2B、actual normal42独立storage。本文只做本地页号计算、一手契约核对和可否定设计；**没有新runtime、API桥、worker改动、GPU门、SSH或加载运行库**。

## 与已有工作的区别

本轮先检索analysis/docs/patches/scripts中的memcpy2D、srcPitch、正等差段等确切关键词，未发现已有同一路线实现/实验。[旧布局备忘](2026-10-22-kv-layout-transfer-research.md)研究跨层存储布局；[旧前缀计划](2026-10-22-kv-fragment-aware-prefix-plan.md)减少保存R并重算已知后缀。当前c95f仅合并源/目的都连续的段。本设计保持原R、每个逻辑页和全部字节，不排序源页、不改布局，也不以重算换提交。

两次实际SAVE数组、原log SHA、全部分段与重建等式保存在[几何JSON](source/kv-pitched-copy/save-arithmetic-evidence.json)。这些是实际数组的离线算术，不是新设备结果。

## 一组明确可行的无重叠分段

保留原有height>1的连续段；对其余连续单页区间，按原逻辑顺序从左到右取最长正恒差段，末孤页保留原线性拷贝。这里“最长”只指该起点，不声称全局最优，也不枚举可以共享端点的所有最大等差区间。逐段展开后与原page_ids数组完全一致。

| 实际SAVE | R / 页数 / payload字节 | 原连续段/层 | 新可行段/层 | 假设每段提交一次的42层调用 |
|---|---|---:|---:|---:|
| 015315 | 16928 / 1058 / 728039424 | 37 | 11：2线性+9二维 | 1554→462 |
| 021658 | 16768 / 1048 / 721158144 | 26 | 6：2线性+4二维 | 1092→252 |

015315原2个长连续段为128、895页；剩35个单页可分9个正等差段。021658原2段为23、1001页；剩24单页可分4段。本组cover的最大步长2049页，所需source pitch为 **33570816B=32.015625MiB**。

两次真实最大尾部都有步长31的19页区间；上述左到右cover把其首行归入前一2行段，因此实际使用末18行步长31段。两种描述不要混为“全局最优分段”。段的实际起点/height/step全部见JSON，不能硬编码run ID、31、19或旧16K长度作为算法条件。

原`copy_calls`是c95f对PyTorch `copy_`的方法调用计数，不直接等于DMA描述符。462/252则是假设将每个新段落实为一次显式线性/2D API调用的设计数，**未实现、未计时**。API内部仍可能逐行处理，减少这些次数不等于相同倍数加速。

## 地址映射与必须保留的所有权

每层raw页宽B=16384字节，原逻辑页i开始的等差段满足 `p[i+j]=p[i]+j*d`，`d>0`、`j=0..h−1`。D2H概念参数为：

```text
src = raw逻辑page0地址 + p[i]×B
dst = 原pinned host逻辑page0地址 + i×B
spitch = d×B, dpitch = B, width = B, height = h
```

只传这些行的B字节；跨度中的其它请求页不能复制到host。所有源行须在同一层原raw storage内，目的行在原host条目内，指针包括真实tensor storage offset。每层独立处理，42因子没有消失。单行、非正步长、能力/布局不符在首次提交前走原线性计划；不能用负size_t pitch表达倒序。

当前worker5d9a的SAVE在243行做原producer fence，236–240行用slot强持raw/host，253–255行提交后记录并同步完成事件；异常316–333行真实settle、失败时保引用。未来只替SAVE的传输规划/提交，保原R/digest/Key/pending frames、host逻辑页序与FULL原恢复证明。**2D API返回不是ACK**，完成事件必须属于实际提交的同一PyTorch当前stream。中途API失败不能当未提交后静默切旧路并报成功；沿原真实settle/失败ACK路径处理。

不能仅将tensor改为as_strided后调用`copy_`就宣称用了真实2D API；必须有按actual头文件编译或等价严格核实的调用桥。它不得额外分配GPU packing buffer、扩大host slot或跨42层拼接storage。暂不实现这种桥。

## 一手契约与本实例的证据分层

[NVIDIA Runtime内存API](https://docs.nvidia.com/cuda/cuda-runtime-api/cuda_runtime_api/group__CUDART__MEMORY.html)定义width按字节、height按行、pitch包含行距，width不得超过任一pitch，区域不得重叠，方向须与指针类型相符，pitch存在上限。本文只取这些接口约束；**NVIDIA文档不是Corex功能/性能证明**。

[NVIDIA同步行为说明](https://docs.nvidia.com/cuda/cuda-runtime-api/api-sync-behavior.html)明确Async名称不保证任何条件下都不阻塞，资源争用可能导致等待。保留原pinned host，不承诺copy与计算重叠、copy engine实现或零SM占用。

公开[FlagOS Corex4.5发布清单](https://flagos-ai.github.io/release-info/base/iluvatar-corex4.5.0/)列出Corex Runtime4.5与CUDA headers，支持其兼容栈定位；[天数官方文档中心](https://developer.iluvatar.com/docs?role=%E6%96%B0%E6%89%8B%E5%BC%80%E5%8F%91%E8%80%85)提供软件栈资料。本轮公开检索未取得这个具体API的完整Corex限制说明，不把检索缺项解释为API不存在。

root已补两份**纯CPU、不加载库、不调用设备**的本实例原件：

- `experiments/source-audits/20261022T023826Z-memcpy2d-exports/result.json` SHA `2334a167fbf0fb3a3131aa2ae7d8c7b9320dd903b1c05a227e9fda3b566f7a40`。实库`/usr/local/corex-4.5.0/lib64/libcudart.so.10.2.89` SHA `d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527`，readelf证实`cudaMemcpy2DAsync`和`_ptsz`等GLOBAL FUNC导出。
- `experiments/source-audits/20261022T024142Z-memcpy2d-header-contract/result.json` SHA `e29cd7a7683c93d4071e29341299e4dedde9d5835e71ba0acf632c43d7129438`。mapping_cudart头SHA `ca962a4e5e051a6de6e8c84c89cf6ec9430d8fbb225a78708731b928662984fb` 实际将cuda入口映至ix入口；ix_runtime_api头SHA `7dca9b9187cf2f7dda5ff75760ae2d56d04007fb07eacc3c74242b63e6c90a5b` 第457/1046行声明`ixMemcpy2DAsync(void*,size_t,const void*,size_t,size_t,size_t,enum ixMemcpyKind,ixStream_t)`，有PTSZ宏路径。

因此已知“本实例有导出与实际声明”，不能再说只有NVIDIA假想API；仍**没有设备可用、真实异步、正确性或收益证明**。尚缺ixStream_t typedef/ixMemcpyKind数值与调用约定的完整核实、header宏选中的实际符号/链接库、PyTorch当前stream与PTSZ族对应、Corex pitch/对齐/height限制，以及33570816B pitch在实际设备上的正确性。

## 可否定判断与本轮决定

保全部KV可避免截短R新增的后缀重算语义风险；但它不改变完整请求准入容量，也不消除原454/462次等待。若Corex内部仍逐行提交、稀疏小行性能差、bridge/错误检查更贵，或SAVE只占极小总耗时，服务收益可为零或负。当前16SM、6CPU及42storage只给减少主机提交的动机，不给时间收益。

本轮已有证据足以保留此一设计，尚不足以服务集成。后继是否补CPU契约、实现独立桥和最短设备copy门由root下一阶段决定；当前停在文档/几何/已存在原件引用，不新增测试或设备工作，也不改已完成三run与冻结代码。
