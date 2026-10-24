# 省去 CPU metadata 成功分支的冗余 computed H2D

原 `_prepare_inputs` 每步先把 computed 计数复制到 GPU；随后 CPU metadata 路径直接从 CPU 结果生成 positions 和 seq_lens，不再读取这个 GPU 副本。本改动将该次 H2D 标记为待办，仅在现有 helper 返回 False 时执行原 copy，再运行原 GPU 表达式。async-spec 的 GPU 校正分支、固定 buffer、输入准备事件、请求与采样顺序均保持。

基于 main `9a43eb1e883a1ba986a4ae8052f1d00d8fd7aa5f`，已包含 GQA [#12](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/12) 和 C500 [#13](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/13)。只修改 `vllm_fl/worker/model_runner.py` 的三处控制流；依赖 main 已有的 CPU metadata helper，不改 GQA、C500 sampler、SQL 或异步 token helper，不涉及队友 #14 草稿。参数、模型、算子和 benchmark 不变。

已有证据均为天数 BI-V150，不是本次 main 迁移后的新测量：

| 验证 | 基线 | 候选 | 结论 |
|---|---:|---:|---|
| 4K 输入、128 输出、64 请求/c64，seed721201 | 36.683611192 s | 36.457831021 s | 时长减少0.615480% |
| 同一短服务的 total tok/s | 7369.394430201 | 7415.032447893 | 单pair增加0.619291% |
| 成功/失败 | 64/0 | 64/0 | 同KV521840；DB四端540表/20112行及三种哈希一致，30项可比门通过 |

原 [215040→215331 对照分析](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/framework-experiments-20261022/analysis/skip-computed-h2d-service-pair.json) 保留完整可比项与限制。[214819 方法门](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/tree/codex/framework-experiments-20261022/experiments/framework/20261022T214819Z-skip-computed-h2d-method) 已验证五种形状、未消费 computed GPU 副本的毒值、真实 helper 回退、连续 event/固定地址 graph 消费者和 RNG；不覆盖模型准确率或真实 async-spec 校正。服务原件：[基线](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/tree/codex/framework-experiments-20261022/experiments/framework/20261022T215040Z-skip-computed-h2d-service-baseline-decode4k)、[候选](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/tree/codex/framework-experiments-20261022/experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k)。

本次只做静态迁移：main 的 `_prepare_inputs` 与原基线方法 AST 一致，三处变换沿用受测版本；迁移后的方法 AST 与原候选一致，CPU metadata helper 字节相同，撤销这三处即可逐字节恢复 main。语法检查通过，没有为发布重跑已有测试或设备实验。历史实验使用 Q/GQA414 组合，不能将其吞吐直接当作当前 main 整树成绩，也不与其他方法收益相加。

保留为 Draft 方法候选：单pair小幅正信号不代表稳定收益或官方成绩，未做本方法的新完整准确率。本 helper 没有 vendor 开关，C500 若满足既有 scope 也可能采用该省略；这里没有 C500 验证，需该平台负责人确认后再合并。未知描述仍走原 helper 回退，helper/copy 异常保持原样传播，不进行提交后的重试。
