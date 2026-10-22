输入准备已在 CPU 算出 positions 和 sequence lengths，原路径仍通过小型 GPU 操作重新生成这些 metadata。本改动复用 CPU 结果和持久 pinned buffer，异步写回原 GPU 地址；配置或张量条件不满足时沿用原表达式。提交包含受测 runner、独立模块与中文方法说明。

已有 BI-V150 验证：五种形状的真实方法门、buffer 地址、事件生命周期和 graph consumer 检查通过；同 KV 容量、同 DB 的单次 64 请求短对照全部完成，吞吐约 **+0.2867%**，平均 TTFT 约 **+0.2344%（变慢）**。这是单轮小信号，尚无新整模型准确率或稳定收益结论，保留 Draft。C500 未验证，runtime 没有按硬件型号自动禁用。

共同基点为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`。与 async token PR 独立；两者合并仅在 helper import 位置发生文本冲突，解决时必须保留两条 import。双向静态组合及解决补丁见[合并说明](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/combination-review.md)，不代表组合已上卡。

详见本分支的 [中文方法说明](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/codex/20261022-cpu-metadata-reuse/docs/cpu-metadata-reuse.md)及实验库的[源码与证据清单](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/cpu-metadata/manifest.json)。不改官方服务参数、benchmark、模型或量化设置。

2026-10-22 补充组合验证：固定组合 runner `6f918ae6…` 已在 BI-V150 完成 `20261022T062205Z-cpu-combination-gate` 真实方法门。五种形状的 55 项数据/地址检查、四轮包含 input IDs 的图读取、同次双快路径计数与 RNG 检查通过；两 helper 累计分别命中 9 / 7 次，DB 前后相同，结束后设备空闲。该门使用真实方法与缓冲区、fixture 状态，不加载模型权重，尚不代表组合服务吞吐或整模型准确率。详见[组合上卡记录](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/analysis/2026-10-22-cpu-combination-062205-result.md)。
