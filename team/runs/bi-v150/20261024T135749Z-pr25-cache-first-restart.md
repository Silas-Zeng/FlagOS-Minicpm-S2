<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T135749Z-pr25-cache-first-restart

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #217 · native 编译缓存身份与重启

- **尝试**：PR25叠加native编译缓存身份修复，保留默认缓存目录和官方serve参数。135749完成49项组件门但checker误拒<think>格式，原失败保留；141536复用组件证据、4个语义请求全对（含4908token），同AOT与34层native图重启成功。原首启图证据由重启前首次补存，不能伪称首轮已归档。两轮均非官方准确率或吞吐，不继承前序PR24完整准确率。
- **改动**：相关实现 [failure.txt](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart/failure.txt)；[gate-auto.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/gate-auto.json)；[cached-dispatch.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/cached-dispatch.json)；[archive-receipt.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/result.json)；[audit.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/prior-audit/audit.json)；[requests.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/requests.json)；[graph-evidence.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/graph-evidence.json)；[archive-receipt.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：启动或描述符诊断；输入 / 输出 / 并发 / 请求数：37 / 1024 / 1 / 1。
- **结果**：49项组件通过；首启答案85被checker的think格式解析误拒，原失败保留，不记模型算术失败。
- **是否保留**：保留49组件通过及checker失败原件；首启图为后续首次补存，不将本轮流程改判成功。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T135749Z-pr25-cache-first-restart",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T13:57:49.462019+00:00",
  "profile_id": "native-cache-identity",
  "phase": "startup_first_checker_failure",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93",
  "flaggems_commit": "",
  "input_len": "37",
  "output_len": "1024",
  "concurrency": "1",
  "num_prompts": "1",
  "profiler": "false",
  "status": "checker_failed_after_first_semantic_response",
  "artifacts": "experiments/framework/20261024T135749Z-pr25-cache-first-restart",
  "conclusion": "PR25与默认编译缓存身份修复首启：native gate 9项及cached-dispatch 40项组件检查通过；实际返回加法85，但自制checker未处理<think>与字面换行格式而误拒绝，driver/owner exit1，首启流程不记成功。服务日志产生新native图；该图在原失败前未归档，141536仅按原日志和结束时间只读核现存文件并首次保存哈希，不伪称首轮已保存图指纹。源码7596cc0/tree b37543af、487文件、SO14f4457a未变，DB恢复207f1b；原失败、原响应、49组件与清理原件保留。不是模型算术失败，不报性能或官方准确率；后续重启另登记，旧AOT失配六轮资格不恢复。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T135749Z-pr25-cache-first-restart](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
