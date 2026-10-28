<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T164809092948Z-native-q32-m16-mapping-diagnostic

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #386 · CoreX原生Prefill Attention：Q32／Q64

- **尝试**：Q32双KV槽原长组件Event省2.50544%只属Q2047/KV16384局部证据；后继三臂同轮旧双槽仍省2.434356%。Q64共享KV的两个Q32 cohort虽通过原数值/Graph/side与Q33边界门，但完整Event6.880203ms，对原Q32慢4.862870%、对旧双槽慢7.479299%，停止，不进模型/官方。此前GPU metadata ABI的pure2048 Event慢9.30069%，mixed未测，原FP64诊断两臂false仍保留；不同组件与负载结果不互相替代。
- **改动**：相关实现 [summary.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json)；[compile-backend-barrier-review.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json)；[review-compile-160904.py](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py)；[summary.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T091802Z-native-q32-metadata-abi/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T091802Z-native-q32-metadata-abi/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/summary.json)；[review.json](../../../experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/review.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T100025Z-native-q64-cohort-compile/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T100025Z-native-q64-cohort-compile/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/summary.json)；[review.json](../../../experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/review.json)；[raw-evidence.json](../../../experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T101658850160Z-native-q64-cohort-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T101658850160Z-native-q64-cohort-long-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：70原件；无softmax/Graph/模型准确率资格。
- **结果**：两次launch固定映射，换值QK16384/PV32768值对CPU FP64 cast FP32逐位通过。
- **是否保留**：保留M16映射依据；非完整Attention或性能资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T164809092948Z-native-q32-m16-mapping-diagnostic",
  "local_date": "2026-10-27",
  "utc_start": "20261027T164809092948Z",
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
  "status": "native_q32_m16_mapping_diagnostic_pass",
  "artifacts": "experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic",
  "conclusion": "原生Q32 M16片段映射两次launch，第二组同形换值沿首组固定坐标、未重新拟合。QK16384值与PV32768值均对独立CPU FP64 cast FP32逐位一致；Q/KV回读及输入/RNG守卫通过。仅矩阵坐标映射诊断，无softmax、Graph、完整Attention、性能或模型准确率资格；保留下一阶段依据。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T164809092948Z-native-q32-m16-mapping-diagnostic](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
