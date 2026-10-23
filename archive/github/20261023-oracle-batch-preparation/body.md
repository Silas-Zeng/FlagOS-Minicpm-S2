本 PR 汇总 BI-V150 的框架、执行图、KV 管理与算子交接实验，沿用现有分支批量补充原始证据。每轮记录尝试、改动、测法、结果与保留判断。本批新增082246、085500两轮诊断及一项附属CPU负结果，总表195条登记、192个run。

- **团队入口**：[一张实验总表](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/team/experiments.md) 和 [按方法汇总](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/tree/codex/framework-experiments-20261022/team/methods) 负责导航，详细命令、源码身份、环境、原始日志及失败证据保留在各轮目录。
- **当前 422 组合准确率**：Math500 Level 3 完整 105 题，103/105（98.0952%），通过既定门。实际 Q/GQA 路径命中已核验；该结论只属于已验证组合，不能外推给后续候选。
- **官方完整实测**：`20261022T231746Z-q-gqa-kv-swap-official` 完成原两档各 4 轮，按原规则丢弃首轮、取第 2–4 轮均值；4K 总吞吐 **4957.95 tok/s**，16K 总吞吐 **3669.74 tok/s**。这些是候选的绝对实测值，DB/KV 条件不同的历史结果不用于归因收益，`gain=null`。
- **compute-order 数值差异定位**：082246 首层诊断确认两路实际 input IDs、positions、Q/K/V、slots、seq 与有效页表逐 bit 一致，而 Attention 输出不同。085500 采集最坏 outside 请求的真实 KV，用独立 CPU FP32/FP64 参考比较：原 2D 路径最大误差 **0.0083881**，P/GQA 路径 **0.0007672**，FP32 与 FP64 参考差 **5.63e-8**。这个首层单行样本中新路径更接近参考，不能仅因两路不同就认定 P 错误，也不能据此证明整模型正确；候选保留、暂不集成，不放宽准确率要求。单 P 相快照依赖已核 writer 不碰 prefix、当前 KV 相同、缓存无 alias 的共同上下文条件。[诊断摘要和原始证据](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/analysis/compute-order-oracle-summary.json)。
- **负结果与验证边界**：CPU 单变量分析未复现“仅逐 tile 将 P 转 BF16”足以解释原路径误差的假设，该解释停止。075210 和085500完整 logits仍有差异，额外 shadow forward/同步的诊断不计吞吐；32/0只说明服务完成。070816 辅助答案基线仅4/32符合预设答案，提示门无判别力，候选侧未运行。上述证据一起保留，避免以未命中测试或单层参考代替新路径的完整正确性验证。
- **此前候选的边界**：compute-order 短筛表观 +4.7989%，但 KV 521936→521840、`gain=null`。独立 Math500 为 101/105，通过既定门却未出现 COMPUTE_ORDER_FIRST_SELECTED，不能证明新排列路径正确，也不与旧 422 的 103/105 作精度升降统计。accepted GPU fill 表观−0.235046%，但 KV 521840→521936、`gain=null`，当前不集成。负结果、未命中与不可比证据一起保留，不为失败尝试另造优化代码 PR。

独立代码 [PR #15：省去冗余 computed H2D](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/15) 已建为 Draft，只引用已有方法门和单pair验证，没有为上传重跑设备；C500与新完整准确率边界见该PR。

本 PR 保留历史与原始测量；优化实现按方法在对应代码库提交 PR，结果上传不等待代码合并。两个平台分别记录，本页实测不代表 C500。
