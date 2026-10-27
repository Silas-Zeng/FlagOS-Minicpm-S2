<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261027T120655436062Z-corex-native-gqa-page16-numeric

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #372 · CoreX原生GQA单page16数值诊断

- **尝试**：v3仅修CPU coverage两行，CU8545与原数学未变。122022实际7组全位型/独立FP64、Graph poison、side stream、underflow三范围均通过；只取得单page16数值资格，没有计时/历史loop/tail/empty/reducer/模型资格。120655旧failed_stop与coverage false仍保留，事后CPU覆盖补证不冒充未执行门。113301编译失败和114038前端exp名字门/机器码补证限制见链接。
- **改动**：相关实现 [comparison.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)；[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json)；[recompute.py](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py)；[llvm-build.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log)；[compile-check.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json)；[backend-equivalence.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json)；[archive-receipt.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json)；[comparison.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json)；[result.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json)；[independent-review.md](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md)；[archive-receipt.json](../../../experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json)；本轮准确变体以原件源码清单为准。
- **怎么测**：原main56/807/native14f单page16合成诊断；80原件逐SHA，exit1但清理通过。
- **结果**：4组已执行数值均逐位；第四覆盖检查false停止，Graph/side未到。
- **是否保留**：保存原failed_stop，CPU事后仅补输入覆盖解释；不接生产、不报性能。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261027T120655436062Z-corex-native-gqa-page16-numeric",
  "local_date": "2026-10-27",
  "utc_start": "20261027T120655436062Z",
  "profile_id": "corex-native-gqa-page16",
  "phase": "numeric_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "56f1838192abc940b3fb9accef490022ac125000",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "corex_native_gqa_page16_coverage_check_stopped",
  "artifacts": "experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric",
  "conclusion": "原生CoreX单page16/D128、每KV头8Q数值诊断，非完整历史loop/reducer。4组实际GPU的shared BF16、FP32/BF16 P、partial/max/sum均跨臂逐位，finite/输入只读/RNG通过；前三组独立FP64通过。第四underflow覆盖检查原false触发failed_stop，Graph/side未到、timings空，不称全门passed或性能/准确率资格。事后只读已存score的CPU float64证明normal/subnormal/低于最小subnormal输入均覆盖，原false/result保留；非数值不等证据，亦不能补授未执行门。113301先因device __exp2f声明失败；114038实际编译成功但原compile-check唯一exp2前端名字门false，backend补证同float_mode12/无修饰机器exp，其限制保留。owner72850于12:07:14 exit1，DB/source/native恢复及9031清理通过。80原件逐SHA复制，不接生产、不报吞吐。"
}
```

</details>

## 原件与说明

- 原始目录：[20261027T120655436062Z-corex-native-gqa-page16-numeric](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/worker.log)；[gpu.csv](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/gpu.csv)；[exit-code](../../../experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
