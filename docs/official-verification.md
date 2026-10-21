# 官方页面核对记录

平台范围：本页规则核对及本轮实测对应天数BI-V150；沐曦－曦云C500由队友负责。实验分析库按平台归档，两个私有代码库共用；BI-V150数据不代表C500或团队整体成绩。

本页记录2026-10-20（Asia/Shanghai）对<https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn>的历史核对。后续无法再次读取页面的边界见末节，不能据此补造计分公式。

## 固定输入

- 模型：`MiniCPM5-2B`。
- 框架：`vllm-plugin-FL`，分支`flagos-2026-s2`。
- 算子库：`FlagGems`，tag `v5.3.5`。
- 4K负载：`[4096, 1024, 64, 256]`。
- 16K负载：`[16384, 1024, 64, 128]`。
- 准确率：`math_500` Level 3，至少`0.95`，公开参考`0.962`。
- 官方采样配置：`temperature=1.0`、`top_p=0.95`、`max_tokens=32768`。
- 官方准确率endpoint：`http://127.0.0.1:9031/v1/chat/completions`。
- 官方dataset参数：`{"math_500":{"dataset_id":"/workspace/evalscope-datasets/math_500","subset_list":["Level 3"]}}`。
- 服务参数：严格使用归档官方页面对应平台的命令。

## 允许修改（归档规则）

- KV Cache、内存管理及动态batching。
- 计算与内核，包括融合及重写。
- 集成到框架的自研量化；不等于可以通过参数开启已有量化。
- 调度、metadata、缓冲、主机/设备交互及其他端到端开销。

## 禁止修改（归档规则）

- 通过超参数启用已有量化或推测解码。
- 调优benchmark脚本。
- 只换算子而不改变实现。
- 删除框架主要算子选择逻辑。
- 合并更新的FlagOS框架分支以提速。
- 更换模型或使行为不可比。

## 提交要求（归档规则）

- 必须包含`vllm-plugin-FL`源码与构建脚本。
- 无算子修改时FlagGems可选；有算子修改时必须包含。
- 必须有`report.pdf`和`readme.md`。
- 最终压缩包以团队命名。

## 官方准确率原命令

```bash
evalscope eval \
  --model minicpm \
  --api-url http://127.0.0.1:9031/v1/chat/completions \
  --api-key EMPTY \
  --eval-type openai_api \
  --datasets math_500 \
  --dataset-args '{"math_500":{"dataset_id":"/workspace/evalscope-datasets/math_500","subset_list":["Level 3"]}}' \
  --eval-batch-size 8 \
  --timeout 3600 \
  --generation-config '{"temperature":1.0,"top_p":0.95,"max_tokens":32768}' \
  --work-dir /workspace/evalscope-datasets/level3 \
  --ignore-errors
```

当前SQL+C3已由090505原件独立核验103/105，通过95%门槛。此结果不自动属于其他原型；命令、参数保持原文。

## 尚未确认的计分问题

归档页面的区间文字不完整，以下保留原文：

```text
total tokens/s 限制 (baseline-1%~, )
ttft限制 ( , ~baseline+1%)
```

可参考`compliance-checklist.md`中的工程核对，但不能称为精确官方公式。仅一个硬件平台是否导致另一平台性能分计零，也仍需主办方确认；不自行补全。

## 2026-10-21继续实验期间的来源复查（历史记录）

当时对同一比赛URL的只读网页复查返回页面不可访问。主要赞助方的[2026-10-16公告](https://www.metax-tech.com/en/ndetail/12669.html)确认MiniCPM5-2B/FlagOS框架及FlagGems吞吐任务并链接同一比赛页，但没有补齐计分区间；这不构成新的边界核验。

继续以归档主办方说明、固定安装分支/脚本/原参数为准，不拿main分支示例、新依赖说明或其他部署栈替代比赛配置。原版完整对照仍待结束，不从已完成候选绝对值合成比赛总分。
