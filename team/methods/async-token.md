<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 异步 token 更新

整数gather/scatter更新；既有索引、stream和回退条件保留。

相关代码：[biv150_async_token_update.py](../../patches/framework/biv150_async_token_update.py)。

相关方法PR：[异步token更新 #2](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/2)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T063353Z-async-token-gate](../runs/bi-v150/20261021T063353Z-async-token-gate.md)（登记#30）：Exit 0 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T174741Z-async-token-decode4k](../runs/bi-v150/20261021T174741Z-async-token-decode4k.md)（登记#78）：post2026-10-21T17:50:48.770684+00:0068MiB0%双栈闭无GPU进程，owned退出或Z；FIRST_SELECTED，保留待确认，非稳定因果/未默认或新accuracy **是否保留：** 保留作候选，仍待确认；不等于默认启用。

## 未记录

- [20261021T063353Z-async-token-gate-control](../runs/unrecorded/20261021T063353Z-async-token-gate-control.md)（登记#31）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
