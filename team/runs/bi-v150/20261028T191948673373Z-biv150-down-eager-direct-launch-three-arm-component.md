<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #455 · BI-V150特定形状GEMM

- **尝试**：比较原SDK GROUP_M8、GROUP_M4 normal-JIT与同一已编译核direct launch的42层down组件。
- **改动**：C仅省掉已选kernel的host wrapper路径；数学/kernel/真实权重不变，两种输入各一次ABCCBA。 版本、命令和源码见下方原件；[方法记录](../../methods/shape-gemm.md)。
- **怎么测**：原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。
- **结果**：42层真实down组件：C对B两种pattern wall均值分别快2.802766%/2.798879%；GPU Event近似持平；Graph仅三臂互比、side仅layer0；非整模收益。原Bhost>A假说不成立，保留组件观察并等待官方验证。
- **是否保留**：保留为host提交组件信号；不外推整模或官方收益，原“Bhost>A”假说被否决。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component",
  "local_date": "2026-10-29",
  "utc_start": "2026-10-28T19:19:48.673373+00:00",
  "profile_id": "shape-gemm",
  "phase": "component",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "",
  "status": "shape_gemm_direct_launch_component_positive",
  "artifacts": "experiments/bundles/20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component",
  "conclusion": "42层真实down组件：C对B两种pattern wall均值分别快2.802766%/2.798879%；GPU Event近似持平；Graph仅三臂互比、side仅layer0；非整模收益。原Bhost>A假说不成立，保留组件观察并等待官方验证。"
}
```

</details>

## 原件与说明

- 原始目录：[20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component](../../../experiments/bundles/20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/bundles/20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component/manifest.json)
- 原始结果：[result.json](../../../experiments/bundles/20261028T191948673373Z-biv150-down-eager-direct-launch-three-arm-component/result.json)
- 日志 / 采样：未单列，见原始目录
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
