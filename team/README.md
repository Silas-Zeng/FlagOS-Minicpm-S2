<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 团队实验导航

先看[唯一实验总表](experiments.md)，再打开每轮短记和原始证据。登记源保持为registry，不另造成绩或补猜缺字段。

## 按平台

- [天数 BI-V150](platforms/bi-v150.md)
- [沐曦－曦云 C500](platforms/c500.md)
- [CPU](platforms/cpu.md)
- [设备字段未记录](platforms/unrecorded.md)

## 按方法

- [CPU metadata + async token 组合](methods/cpu-combination.md)
- [CPU metadata 复用](methods/cpu-metadata.md)
- [异步 token 更新](methods/async-token.md)
- [KV 二维 SAVE 复制](methods/kv-pitched.md)
- [KV 连续页复制](methods/kv-contiguous.md)
- [抢占请求选择与进展](methods/kv-progress.md)
- [KV 启动内存观察](methods/kv-memory.md)
- [KV 保存 / 恢复协议](methods/kv-protocol.md)
- [KV 生命周期观察](methods/kv-observation.md)
- [专用 GQA decode attention kernel](methods/gqa-decode-kernel.md)
- [int8 与 W8A8 决策测量](methods/int8-decision.md)
- [准入与输出增长](methods/admission.md)
- [非前缀 decode 映射](methods/mapped-attention.md)
- [矩阵乘 CTA 分组](methods/mm-cta.md)
- [缓冲区 gather 与 token bucket](methods/buffers.md)
- [Event / graph 能力与等待](methods/event.md)
- [SQLite 反射及 SQL+C2/C3 组合](methods/sql.md)
- [完整官方吞吐对照](methods/official.md)
- [Attention 分流与 launch](methods/attention.md)
- [早期集成、块表与 profile](methods/early.md)
- [其它登记与控制记录](methods/other.md)

[AI交接、详细SHA及过程稿归档入口](archive-index.md)

更新：`python scripts/build_team_view.py`。仅重建本目录自动视图，不修改登记和证据。
