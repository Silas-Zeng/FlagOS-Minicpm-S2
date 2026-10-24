<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# CPU metadata + async token 组合

两种CPU准备方法的组合；方法正确性与短服务性能分别记录。

相关代码：[model_runner.py](../../docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py)；[biv150_cpu_metadata.py](../../patches/framework/biv150_cpu_metadata.py)；[biv150_async_token_update.py](../../patches/framework/biv150_async_token_update.py)。

相关方法PR：[CPU metadata #1](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/1)；[异步token更新 #2](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/2)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T062205Z-cpu-combination-gate](../runs/bi-v150/20261022T062205Z-cpu-combination-gate.md)（登记#118）：五case各11字段全过 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T070004Z-cpu-combination-baseline-decode4k](../runs/bi-v150/20261022T070004Z-cpu-combination-baseline-decode4k.md)（登记#119）：39.225860193837434s/6891.780031441377total/TTFT20088.914546053275ms **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T070452Z-cpu-combination-combined-decode4k](../runs/bi-v150/20261022T070452Z-cpu-combination-combined-decode4k.md)（登记#120）：TPS+0.6986430312pct、耗时省0.6937958747pct即0.2721474s、TTFT-0.1250025609pct，仅单轮短筛信号非稳定因果/官方或accuracy，不相加单项收益/不继承103-105 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T100830Z-cpu-combination-combined-decode4k](../runs/bi-v150/20261022T100830Z-cpu-combination-combined-decode4k.md)（登记#123）：10:10:29Z exit0、后态68MiB/0%且端口闭 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T105839Z-cpu-combination-level3](../runs/bi-v150/20261022T105839Z-cpu-combination-level3.md)（登记#130）：干净6f918组合首次完整Math500 Level 3：102/105（97.1429%）通过95%门 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
