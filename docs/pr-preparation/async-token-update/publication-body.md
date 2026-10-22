请求删除、压缩或重排后，原异步输入准备先 gather 上批采样 token，再 scatter 到当前 input IDs。本改动以新实现的 int32 Triton kernel 完成一次 gather/scatter，保留 CPU 请求映射、两份索引 H2D、原 stream 与回退路径；不改采样算法或 token 内容。提交包含受测 runner、独立模块与中文说明。

已有 BI-V150 验证：真实方法的 12 类 case 通过，覆盖重排、删除、新请求空洞、stride、跨 stream 与回退；同 KV 容量、同 DB 的单次 64 请求短对照全部完成，吞吐约 **+0.7037%**，平均 TTFT 约 **−0.8656%**。这是单轮小信号，尚无新整模型准确率或稳定收益结论，保留 Draft。C500 未验证。

共同基点为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`。与 CPU metadata PR 独立；双向组合仅在 helper import 位置冲突，保留两条 import 的解决补丁与后续次序见[合并说明](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/combination-review.md)。静态组合不等于组合上卡验证。

详见本分支的 [中文方法说明](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/codex/20261022-async-token-update/docs/async-token-update.md)及[源码与证据清单](https://github.com/Silas-Zeng/FlagOS-S2-Minicpm-throughput/blob/main/docs/pr-preparation/async-token-update/manifest.json)。不改官方服务参数、benchmark、模型或量化设置。
