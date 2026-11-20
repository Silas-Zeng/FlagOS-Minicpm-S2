<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T075732Z-main0bf9-affine-affine-official-four-rounds

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #253 · Attention连续页段寻址

- **尝试**：保持原KV分配与数学，对现存连续物理页段用仿射寻址。组件四布局逐位通过、局部耗时下降约5.0–6.9%；原四语义及三个串行prefill页表绑定通过，仅P恒等/C3prefix0。完整官方两档各四轮1536成功，弃首轮4K5741.68/16K4050.10 tok/s，相对main526观察−0.30%/+0.12%；KV546432对547536，不确认净收益、不定基线、不追加105。
- **改动**：相关实现 [biv150_attention_affine_pages.py](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify-control/plugin-source/vllm_fl/patches/biv150_attention_affine_pages.py)；[prototype.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py)；[worker.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：原官方4K/16K各四轮、弃首轮；输入4096/16384、输出1024、并发64、每轮256/128请求；官方脚本与服务参数不变。
- **结果**：官方两档各4轮、1536成功；弃首轮5741.68/4050.10 tok/s，观察−0.30%/+0.12%。KV失配，不确认净收益。
- **是否保留**：保留完整结果及局部正信号；未确认净收益，不定新基线、不追加105。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T075732Z-main0bf9-affine-affine-official-four-rounds",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T07:57:32+00:00",
  "profile_id": "attention-affine-pages",
  "phase": "原官方4K/16K各四轮",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "affine_official_no_confirmed_gain",
  "artifacts": "experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds",
  "conclusion": "Affine原官方4K/16K各四轮完成，1536请求全成功。弃首轮4K5741.68、16K4050.10 total tok/s，相对main526的5758.72/4045.20仅作观察为−0.30%/+0.12%；KV546432对547536，比较器仅actual_kv失配、gain_calculated=false，原差值null，不确认净收益。4K四轮5211.79/5788.20/5650.46/5786.39；16K3645.45/4053.83/4050.12/4046.34。源码tree41449b98，官方脚本与服务参数不改；08:56:26 UTC源/native未变、DB恢复及清理通过。保留组件正信号与完整模型观察，不定新基线，不追加105；短模型门只覆盖P恒等/C3prefix0，不能称最终准确率合格。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T075732Z-main0bf9-affine-affine-official-four-rounds](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds)
- 原命令：[benchmark-command.json](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/benchmark-command.json)；[command.txt](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds-control/command.txt)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/manifest.json)；[source-sha256.json](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds-control/source-sha256.json)
- 原始结果：[raw_runs_20261025_155829.csv](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/benchmark_results/raw_runs_20261025_155829.csv)；[summary_20261025_155829.csv](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/benchmark_results/summary_20261025_155829.csv)；[result.json](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/result.json)
- 日志 / 采样：[server.log](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/server.log)；[gpu.csv](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/gpu.csv)；[exit-code](../../../experiments/official/20261025T075732Z-main0bf9-affine-affine-official-four-rounds/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
