<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T071453655585Z-attention-affine-pages-component

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #250 · Attention连续页段寻址

- **尝试**：保持原KV分配与数学，仅对已存在连续物理页段用仿射寻址。真实组件四布局逐位通过，16K耗时下降约6.9%、4K约5.0–5.5%；保留为候选，真实服务覆盖和官方吞吐尚待。
- **改动**：相关实现 [prototype.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py)；[worker.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：event耗时下降6.95%/6.93%，4K下降4.99%/5.50%
- **是否保留**：保留候选；真实服务页段覆盖、P索引接入及模型准确率待验，组件收益不代替官方吞吐。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T071453655585Z-attention-affine-pages-component",
  "local_date": "2026-10-25",
  "utc_start": "20261025T071453655585Z",
  "profile_id": "attention-affine-pages",
  "phase": "真实Attention组件ABBA",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "affine_component_positive_signal",
  "artifacts": "experiments/framework/20261025T071453655585Z-attention-affine-pages-component",
  "conclusion": "保持当前main526/native14f/Q-hoist和原数学，利用现有连续页段减少页表寻址；M2048/P2019，16K及4K各连续/带碎片布局四case，逐位输出、KV/guard/RNG、换页重提交均通过。16K event耗时下降6.95%/6.93%，4K下降4.99%/5.50%；计入一次CPU描述符与H2D的42层估算为正，非服务/官方吞吐。真实生产页段覆盖、P索引接入及准确率未验证，保留候选；源/native未变、DB恢复/清理通过。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T071453655585Z-attention-affine-pages-component](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/manifest.json)
- 原始结果：[results.json](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/worker.log)；[gpu.csv](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/gpu.csv)；[exit-code](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
