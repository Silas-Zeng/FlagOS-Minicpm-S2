<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 完整官方吞吐对照

原版与完整候选的原始官方结果；保留DB、KV和计分边界。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T092944Z-sql-mixed-official](../runs/bi-v150/20261021T092944Z-sql-mixed-official.md)（登记#57）：原2-4均值分档totalTPS比4K1.933207729x/16K3.166027317x，TTFT变化-61.15818754%/-70.92157564% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T122607Z-original-baseline](../runs/bi-v150/20261021T122607Z-original-baseline.md)（登记#72）：fullpost16:17:27.184712Z68MiB0%IPv4IPv6端口闭无GPU进程，server/benchmark/EngineCore退出；最终分档候选/原版1.933207729x和3.166027317x，初始DB不同且KV候选+96，不作cache-matched因果稳定或官方总分 **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261028T160148Z-native-direct-q-v2-4k-four-rounds](../runs/bi-v150/20261028T160148Z-native-direct-q-v2-4k-four-rounds.md)（登记#442）：官方4K四轮完整、1024请求成功；弃首暖均6537.81，对基线6627.816667为−1.358014%；首暖+0.424135%，故跑满。 **是否保留：** 保留完整负结果并停止direct-Q；KV548432对548336不匹配，不作严格因果，不跑16K/105、不改基线。
