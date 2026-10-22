<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 非前缀 decode 映射

单层构造、服务实际命中与重复结果分开记录。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T183421Z-mapped-decode-gate](../runs/bi-v150/20261021T183421Z-mapped-decode-gate.md)（登记#86）：18:34:44.773036Z完成/post68MiB0%无GPU进程/9031free **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T184809Z-mapped-decode-sme-fix-gate](../runs/bi-v150/20261021T184809Z-mapped-decode-sme-fix-gate.md)（登记#88）：四case各13checks全true/nextdecode及crossstream-capture回退原件 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T185023Z-mapped-decode-sme-fix-timing](../runs/bi-v150/20261021T185023Z-mapped-decode-sme-fix-timing.md)（登记#89）：wall14.344921375→12.435507453125ms省13.31073118%，event14.216219902039→12.401883125305ms省12.76244170% **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T185627Z-mapped-decode-context16k](../runs/bi-v150/20261021T185627Z-mapped-decode-context16k.md)（登记#90）：TPS−1.07166475%，基线KV521936不同，不归因单算法；post19:00:37.354668Z68MiB0双栈闭无GPU进程，未默认/新accuracy **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261021T191131Z-mapped-decode-context16k](../runs/bi-v150/20261021T191131Z-mapped-decode-context16k.md)（登记#92）：32成功0失败/524288in4096out/117.028659570962s/4514.996599440720total/TTFT59836.11785736866ms/KV521840；对干净基线KV仍差96，未accuracy默认 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
