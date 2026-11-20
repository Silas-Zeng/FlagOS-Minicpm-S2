<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T143942955934Z-native-silu-vec2-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #275 · native SiLU相邻两列访存

- **尝试**：用相邻两列向量读取和packed BF16写回减少native SiLU尾处理成本。
- **改动**：原量化/GEMM及舍入顺序保留；只有私有测试库，独立组件不补造框架commit/native_unchanged。源码基点引用0915，实测身份见原source与library SHA。 版本、命令和源码见下方原件；[方法记录](../../methods/native-silu-vec2.md)。
- **怎么测**：独立随机M2048/N12288/K2048、同编译器私有库；32-call Graph ABBA，原15case、独立CPU参考、变指针/同址换输入、inputs/RNG；生产native未加载/替换，DB207f未变。
- **结果**：15case逐位/finite/guard与Graph通过；隔离Event0.216360→0.231472ms慢6.9849%，完整gate0.712861→0.730258ms慢2.4404%。
- **是否保留**：停止模型推进；实验PR52已关闭、未合并，不改生产csrc，不授模型/官方资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T143942955934Z-native-silu-vec2-component",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T14:39:42.955934+00:00",
  "profile_id": "native-silu-vec2",
  "phase": "相邻两列SiLU独立组件",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "native_silu_vec2_negative",
  "artifacts": "experiments/framework/20261025T143942955934Z-native-silu-vec2-component",
  "conclusion": "独立随机M2048/N12288/K2048 native组件，仅私有重编测试库；相邻int2/float2读取和packed BF16写回，原量化/GEMM/舍入顺序保持。15case逐位/finite/guard、变指针与换输入Graph、独立CPU参考、inputs/RNG均通过。隔离尾处理Event0.216360→0.231472ms慢6.9849%，wall慢6.5243%；完整gate Event0.712861→0.730258ms慢2.4404%，wall慢2.6352%。14:40:00 exit0、DB207f未变及清理通过。无净收益，停止模型推进；不授整模/官方资格，框架commit/native_unchanged不补造。按用户新约定准备简短实验Draft PR后关闭留痕，不改生产csrc。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T143942955934Z-native-silu-vec2-component](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/manifest.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/result.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T143942955934Z-native-silu-vec2-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
