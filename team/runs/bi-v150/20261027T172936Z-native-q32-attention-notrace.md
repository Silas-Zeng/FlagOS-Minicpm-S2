<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T172936Z-native-q32-attention-notrace

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #388 · CoreX原生Q32 Attention：编译、映射与组件

- **尝试**：旧shared-P组件数值正确但慢21.56%；direct-P近持平停止。独立双KV槽保持64KiB与原FPbody，191803实编存在预取/当前计算窗口且双spill0（非实际重叠证明）；194147完整长组件全部位型/FP64/Graph/尾NaN等门过，Event省2.50544%、wall省3.34544%。保留局部正候选，未接模型/官方，不与其它组件幅度相加。
- **改动**：相关实现 [summary.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json)；[compile-backend-barrier-review.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json)；[review-compile-160904.py](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py)；[summary.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：23原件；不凭资源减少宣称收益。
- **结果**：CPU no-trace实编通过，七诊断参数无访问/FP32trace store为0；VGPR105、SGPRspill49。
- **是否保留**：保留编译变体；仍有spill，无数值或性能资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T172936Z-native-q32-attention-notrace",
  "local_date": "2026-10-27",
  "utc_start": "20261027T172936Z",
  "profile_id": "native-q32-transfer",
  "phase": "diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "dac1b8fb48e7983e48283032efeee9b592c5fbe5",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_attention_notrace_compile_only",
  "artifacts": "experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace",
  "conclusion": "同Q32/T64 CPU no-trace变体，7诊断参数无body访问、FP32trace store为0；原机制与no-trace编译检查通过。VGPR122→105、SGPRspill89→49，64KiB/SGPR104保持；仍有spill，不凭资源减少宣称收益。未GPU执行、无数值/性能或模型资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T172936Z-native-q32-attention-notrace](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
