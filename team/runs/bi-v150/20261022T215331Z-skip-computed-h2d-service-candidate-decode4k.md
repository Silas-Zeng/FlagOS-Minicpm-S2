<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T215331Z-skip-computed-h2d-service-candidate-decode4k

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #176 · 省去无消费者的 computed H2D

- **尝试**：CPU metadata成功时省略一次计数GPU副本提交，保留原回退和固定buffer/event；方法门与独立短服务单pair分别记录，不与KV组合收益相加。
- **改动**：相关实现 [framework](../../../patches/framework)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：4096 / 128 / 64 / 64。
- **结果**：吞吐+0.619291%、时长−0.615480%、TTFT−1.026463%、TPOT−0.053834%
- **是否保留**：保留作候选，仍待确认；不等于默认启用。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T215331Z-skip-computed-h2d-service-candidate-decode4k",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T21:53:31+00:00",
  "profile_id": "skip_computed_h2d",
  "phase": "service_candidate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "4096",
  "output_len": "128",
  "concurrency": "64",
  "num_prompts": "64",
  "profiler": "false",
  "status": "comparable_single_pair_positive_signal_retained",
  "artifacts": "experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k",
  "conclusion": "单H2D短服务pair吞吐+0.619291%、时长−0.615480%、TTFT−1.026463%、TPOT−0.053834%；保留单次正信号，不声明稳定收益，不与KV组合相加。本侧candidate为36.457831021s/7415.032447893 total tok/s、64成功0失败。30项门全过，同KV521840、DB540/20112四端三SHA、原bc51/参数/seed；完整414仅runner cc442→97f41，其余413同，实际metadata及Q/GQA同Engine首次命中。引用214819方法门；各477原件全核，新accuracy未跑。详analysis/skip-computed-h2d-service-pair.json。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T215331Z-skip-computed-h2d-service-candidate-decode4k](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/launch-command.json)；[command.txt](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k-control/source-sha256.json)
- 原始结果：[decode-4k-infqps-concurrency64-minicpm-20261023-055524.json](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261023-055524.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/server.log)；[gpu.csv](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/gpu.csv)；[exit-code](../../../experiments/framework/20261022T215331Z-skip-computed-h2d-service-candidate-decode4k/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
