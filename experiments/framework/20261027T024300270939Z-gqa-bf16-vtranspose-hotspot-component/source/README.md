# 纯 BF16 V 页内转置：唯一完整 decode 组件

目的只针对真实原 GQA 的 V→shared 重排：原 SoA 负实验所保存的原 baseline TTGIR 是 V blocked `[1,2]` / order `[1,0]` → shared → dotB；实际 ASM 每完整页 V 有 16 条 `ml_byte_permute_b32`、8 条 `ml_slb_store_b32x2`，同页 K 没有这些 permute、只有4条 `b32x4` store。不是因 507/665 GB/s 理论差距立项，也不减少必要 BF16 字节。

K 仍原 NHD，V 从 `slot/head/dim` 改为同页 `head/dim/slot`，固定页仍16384B。V 元素绝对地址为 `page*8192+4096+head*2048+dim*16+slot`（BF16元素），没有 metadata、解码、压缩或额外常驻容量。候选从 main241 原 GQA 函数精确抽取，只改两处 V dim stride 为16，并传实际 V slot stride1/head stride2048；原 page16、while、8Q、split、FP/softmax/dot 顺序、原 reducer不变。希望编译器选择 K-contiguous 的 V load/原生 BF16 pair，少做 shared 前 halfword permute；是否成立只看实际 TTGIR/ASM，CPU不预认。

**代价必须一起测。** 完整页两个 head 的 V 集合恰覆盖原8192B，无洞/重复；若compiler按连续slot维分配lane，整页地址可连续，并不预证实际事务或指令。新token每head写128个2B值，地址间距32B、范围4096B，原来是连续256B；32/64/128B粒度敏感模型均可能覆盖完整4KiB，比原16倍，不能用总字节相同掩盖 scatter。B64两头逻辑 V 新写只有32KiB、最多约512KiB上述地址覆盖，相比旧组件约274.7MB KV读有摊销机会；这是地址模型，不是实测带宽/事务或可省时间。新writer每token一个CTA同时写原K及新V，直接落目标地址，不在每步做整池转置，也不读旧cache/配对RMW。

复用已验 main241/765 owner、实际生产 ABI 捕获、8类FP64/特殊值/Graph/输入/RNG/旁stream门、原真正 reducer，A direct baseline必须等于本次backend实际compiled hash。复用真实采样 `f4821117…`（一题256prompt/每层128token），页样本重复到容量、随机Q，不冒称真实16K输入。位型往返另核全部65536 BF16模式；新writer Graph的同址改值→邻slot→负slot，以CPU原始输入overlay、全分配位相等和邻行保留作门，先独立验证原cache后才使用FP64。有限输出跨臂逐位硬门不变，不能放宽救布局变化。

唯一 N64/S2 固定长度组，完整同流 Graph ABBA：A 原writer＋原GQA＋原reducer，B 新writer＋新GQA＋同原reducer。整池layout初始化只在门/输入切换，不计成每步操作；不隐藏每token writer。所有分配/view/Graph keepalive固定，不resize/free。保存两臂及writer真实IR/ASM/resource/静态指令数（全函数静态计数不当作每页计数）。编译/数值错误或完整负结果就停，不扫tile/for/SME或移load顺序。

**没有prefill/服务资格。** 原 prefill V reader 与 Q-hoist guard 依赖 D stride1，本包不把转置数据暴露给它们；生产若继续必须实际实现并验证 prefill、copy/SAVE/RESTORE、原容量/跨stream/Graph及模型准确率。旧 SoA 的4.56倍负结果保留，不以本包给codec换参数；本项是纯BF16物理布局，数学与必要读取字节不改。

2026-10-27已通过 GitHub API 核所有作者到 PR77：PR73/75/76为近似 V8/晚V/prefill，74为CTA倒序，77为unchanged-max rescale，70为constexpr stride，69为page pipeline，不重复。PR38 S18 是相关 producer-consumer 布局研究，未见这份精确 V-only 页内转置的已测实现；旧HND保持D连续，不是本布局。实际原 writer 源已有联合 head-major 的 V `[head,dim,slot]` 分支，但它还改变K，本包保K不变并新增 writer/实际GQA消费，不靠只切已有替代实现。

入口由 root 独占设备调度；本CPU准备不连接GPU：

```bash
python3 entry.py --source-dir <main241精确765源码> --native-library <native14f.so> --shape hotspot
```
