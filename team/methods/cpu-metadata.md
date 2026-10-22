<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# CPU metadata 复用

复用已计算的CPU视图，写回原GPU缓冲区；回退和事件边界见原报告。

相关代码：[biv150_cpu_metadata.py](../../patches/framework/biv150_cpu_metadata.py)。

相关方法PR：[CPU metadata #1](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/1)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T174115Z-cpu-metadata-gate](../runs/bi-v150/20261021T174115Z-cpu-metadata-gate.md)（登记#76）：wallABBA原0.712748078125到0.65646540625ms省7.89657294%约56.282672us，仅method fixture非E2E/服务/accuracy **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T175049Z-cpu-metadata-decode4k](../runs/bi-v150/20261021T175049Z-cpu-metadata-decode4k.md)（登记#79）：post2026-10-21T17:54:39.866651+00:0068MiB0%双栈闭无GPU进程，owned退出或Z **是否保留：** 保留作候选，仍待确认；不等于默认启用。
