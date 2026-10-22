<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 抢占请求选择与进展

抢占瞬间观察、请求选择及其对照；失配结果也保留。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T230548Z-preemption-snapshot-context16k-long](../runs/bi-v150/20261021T230548Z-preemption-snapshot-context16k-long.md)（登记#109）：失败：31running prompt均16384/max1024/output327..569，free0派生需1/failed index1/旧queued1各span1 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T015315Z-kv-progress-victim-context16k-long](../runs/bi-v150/20261022T015315Z-kv-progress-victim-context16k-long.md)（登记#110）：全bytespass/0ZERO/fast454/runner6/consumer9/host释放，原preempt0→1 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T020721Z-kv-progress-pair-full-context16k-long](../runs/bi-v150/20261022T020721Z-kv-progress-pair-full-context16k-long.md)（登记#111）：218.39959823712707s/2550.627402689529total/TTFT62408.937510466785ms **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T021658Z-kv-progress-pair-progress-context16k-long](../runs/bi-v150/20261022T021658Z-kv-progress-pair-progress-context16k-long.md)（登记#112）：218.51338428491727s/2549.299219464107total/TTFT62356.0446958727ms **是否保留：** 待确认；通过某项检查不自动等于优化保留。
