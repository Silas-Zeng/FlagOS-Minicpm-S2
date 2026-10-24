<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261024T141536Z-pr25-cache-restart-recheck

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #218 · native 编译缓存身份与重启

- **尝试**：PR25叠加native编译缓存身份修复，保留默认缓存目录和官方serve参数。135749完成49项组件门但checker误拒<think>格式，原失败保留；141536复用组件证据、4个语义请求全对（含4908token），同AOT与34层native图重启成功。原首启图证据由重启前首次补存，不能伪称首轮已归档。两轮均非官方准确率或吞吐，不继承前序PR24完整准确率。
- **改动**：相关实现 [failure.txt](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart/failure.txt)；[gate-auto.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/gate-auto.json)；[cached-dispatch.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/cached-dispatch.json)；[archive-receipt.json](../../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/archive-receipt.json)；[result.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/result.json)；[audit.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/prior-audit/audit.json)；[requests.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/requests.json)；[graph-evidence.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/graph-evidence.json)；[archive-receipt.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck-control/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：启动或描述符诊断；输入 / 输出 / 并发 / 请求数：37/4908 / 1024 / 1 / 4。
- **结果**：默认缓存重启4/4语义正确（含4908token），同AOT与34层native图；仅服务验证，非官方准确率或性能。
- **是否保留**：保留缓存修复和重启语义通过证据；组件未重测，源码新版本的官方性能与完整准确率另验。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261024T141536Z-pr25-cache-restart-recheck",
  "local_date": "2026-10-24",
  "utc_start": "2026-10-24T14:15:36.279439+00:00",
  "profile_id": "native-cache-identity",
  "phase": "startup_restart_semantic_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "7596cc0eb14fdbfc56e42eb1cd68d0f37b890d93",
  "flaggems_commit": "",
  "input_len": "37/4908",
  "output_len": "1024",
  "concurrency": "1",
  "num_prompts": "4",
  "profiler": "false",
  "status": "default_cache_restart_semantics_pass",
  "artifacts": "experiments/framework/20261024T141536Z-pr25-cache-restart-recheck",
  "conclusion": "同源码PR25与默认缓存修复重启通过：复用135749的49项组件原件，不重复测试；4个语义请求全部正确，含4908 prompt-token长prefill。默认/root/.cache/vllm且编译缓存开启，实际加载同一AOT 4d1f1ad5…f07b；图SHA8b7e654b…a0ff8仍含layer4..37共34个native调用，与重启前补存图字节一致。首启原加法答案85的只读解析得到纠正，但135749原失败保留。source7596cc0/tree b37543af、487文件、SO14f4457a不变，driver/owner exit0、DB恢复207f1b。仅服务语义与缓存复用验证，不报性能或完整准确率，不继承131603前序PR24的100/105到PR25版本；框架PR35 head35039443相对受测版本仅中文说明。"
}
```

</details>

## 原件与说明

- 原始目录：[20261024T141536Z-pr25-cache-restart-recheck](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
