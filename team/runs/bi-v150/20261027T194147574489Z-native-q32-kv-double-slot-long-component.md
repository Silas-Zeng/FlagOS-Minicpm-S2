<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T194147574489Z-native-q32-kv-double-slot-long-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #404 · CoreX原生Q32 Attention：编译、映射与组件

- **尝试**：原长组件双KV槽Event省2.50544%只属Q2047/KV16384组件。新GPU metadata ABI实编通过，但actual Manager pure2048完整Event慢9.30069%，wall省8.92290%；14硬门过，FP64原诊断两臂均false且误差一致。按冻结Event负筛选停止，mixed1987未测，无生产资格，不外推长组件小收益。
- **改动**：相关实现 [summary.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json)；[compile-backend-barrier-review.json](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json)；[review-compile-160904.py](../../../experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py)；[summary.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T171059Z-native-q32-attention/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T171059Z-native-q32-attention/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T172936Z-native-q32-attention-notrace/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T175958Z-native-q32-direct-p/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw.tar.gz.storage.json)；[summary.json](../../../experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/summary.json)；[raw-evidence.json](../../../experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T091802Z-native-q32-metadata-abi/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T091802Z-native-q32-metadata-abi/raw.tar.gz.storage.json)；[summary.json](../../../experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/summary.json)；[raw-evidence.json](../../../experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw-evidence.json)；[manifest.json](../../../experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/manifest.json)；[raw.tar.gz.storage.json](../../../experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw.tar.gz.storage.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：完整原件与manifest逐SHA核验，不为发布重复上卡。
- **结果**：Q32双KV槽保持64KiB与原数学，只将下一页copy放当前QK／softmax／PV之间。初始／恢复／换值／side全输出位型、原独立FP64／尾NaN／输入／RNG及Graph门全部通过；完整Q32长组件Event6.571181774→6.406544447ms省2.5054447%，wall省3.34544%。保留局部正候选，非模型／官方或新准确率；不与direct-
- **是否保留**：保留正观察；不继承模型／准确率或新基线。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T194147574489Z-native-q32-kv-double-slot-long-component",
  "local_date": "2026-10-27",
  "utc_start": "20261027T194147574489Z",
  "profile_id": "native-q32-transfer",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "b3b87d2a1c13448bd8c6bc24e8045c0458b8b9dd",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_q32_double_slot_component_positive",
  "artifacts": "experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component",
  "conclusion": "Q32双KV槽保持64KiB与原数学，只将下一页copy放当前QK／softmax／PV之间。初始／恢复／换值／side全输出位型、原独立FP64／尾NaN／输入／RNG及Graph门全部通过；完整Q32长组件Event6.571181774→6.406544447ms省2.5054447%，wall省3.34544%。保留局部正候选，非模型／官方或新准确率；不与direct-P及GQA宏1收益相加，不继承生产资格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T194147574489Z-native-q32-kv-double-slot-long-component](../../../experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：未单列，见原始目录
- 原始结果：未单列，见原始目录
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
