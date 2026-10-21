# 天数 BI-V150 完整官方实验对比与复算

原版 `20261021T122607Z-original-baseline` 与 SQL+C3 候选 `20261021T092944Z-sql-mixed-official` 均已完成并取回本地。最终只读比较退出 0，`status=compared`、`gain_computed=true`；结果保存为[最终比较 JSON](../analysis/2026-10-21-official-final-comparison.json)，SHA256 **`52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832`**。这是两档官方协议结果的描述性比较，不合成官方总分，也不宣称缓存完全匹配或稳定因果收益。

本文全部结果仅属于天数 BI-V150。沐曦－曦云 C500 由队友在实验分析库另存记录；团队共用的两个私有代码库不要求按平台拆分目录或分支。

## 最终分档结果

每档仍按原脚本运行 4 轮、丢弃第 1 轮，以下均来自原第 2–4 轮相应 raw 指标的算术均值。绝对值显示两位小数，比例与变化率由未再次舍入的均值计算；不从平均耗时反推吞吐。

| 输入 / 输出 / 并发 / 请求数 | 原版耗时 s | 候选耗时 s | 原版 total tok/s | 候选 total tok/s | 候选 / 原版 | 吞吐变化 |
|---|---:|---:|---:|---:|---:|---:|
| 4096 / 1024 / 64 / 256 | 687.94 | 355.88 | 1905.46 | 3683.65 | 1.933208× | +93.3208% |
| 16384 / 1024 / 64 / 128 | 2584.99 | 816.48 | 861.99 | 2729.07 | 3.166027× | +216.6027% |

| 档位 | 原版 Mean TTFT ms | 候选 Mean TTFT ms | Mean TTFT 变化 |
|---|---:|---:|---:|
| 4K / 1024 output | 12310.56 | 4781.64 | −61.1582% |
| 16K / 1024 output | 636429.44 | 185063.65 | −70.9216% |

TTFT 的负变化表示延迟降低，正变化表示延迟增加。16K total tok/s 的原版/候选未再次舍入均值为 `861.9866666666667` / `2729.0733333333333`，所以用表内显示值重新相除会有舍入差。原件：[原版 summary](../experiments/official/20261021T122607Z-original-baseline/benchmark_results/summary_20261021_202847.csv)、[候选 summary](../experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/summary_20261021_173039.csv)。每份原始 CSV 都保留 8 条 raw 和 2 条 summary，没有重写。

## 实际 KV、数据库与比较边界

| 状态 | 原版 | SQL+C3 候选 |
|---|---:|---:|
| 可见显存，MiB | 32768 | 32768 |
| 容器 CPU 配额，核 | 6 | 6 |
| KV 容量，tokens | 521840 | 521936（多 96） |
| DB before，表数 / 行数 | 512 / 19130 | 489 / 18384 |
| DB after，表数 / 行数 | 516 / 19270 | 501 / 18789 |
| 本次新增，表数 / 行数 | 4 / 140 | 12 / 405 |

两个 run 的 DB before/after 均从实际 SQLite 快照重算物理文件、schema 和逻辑内容三种 SHA256，完整值保存在最终比较 JSON 的 `baseline.database` 和 `candidate.database`。两次运行的初始 DB 指纹不同，未清空或人为统一缓存；真实 KV 容量也不同，不能称为 cache-matched。候选准确率的独立 **103/105（98.0952%）** 仅属于受测 SQL+C3 组合，比较脚本不代替准确率门。

每档仅三轮进入均值，且两份完整运行不等于多次独立重复实验。当前结果不分摊 SQL、Attention 与缓存状态各自的因果贡献，不外推到 C500，也不合成为跨档整体倍数或官方总分。

## 只读复算入口

`scripts/compare_official_runs.py`，最终SHA256 **e9dc056cee3b0db0f42c153d5321f4eb0d136396187c90acd70087cd4108481a**。在项目根目录，用新Python进程执行：

```text
python -X utf8 scripts/compare_official_runs.py experiments/official/20261021T122607Z-original-baseline experiments/official/20261021T092944Z-sql-mixed-official
```

第一个参数是原始 `13eb9be` 基线，第二个是已过准确率的 SQL+C3 候选。脚本只读两个 run 目录并向 stdout 输出 JSON，不写 CSV、修改源码、执行 driver main、查询设备或导入模型，不需要 SSH。复算输出应另存新文件，不能覆盖原始证据或上述已封存结果。

| 退出码 / status | 含义 |
|---|---|
| 2 / pending | 缺少结束文件或完整证据；`gain_computed=false`，列缺项，不输出cases或收益。 |
| 1 / invalid | 已有证据显示失败、身份/协议/哈希不符或原CSV校验失败；不计算收益。 |
| 0 / compared | 两份完整官方证据通过以下门；只给两个case的描述性对比。 |

仅两 run 都退出 0、`benchmark_completed=true` / `official_benchmark_completed`、benchmark 退出 0 且 `cleanup_errors` 为空才继续。复用**原 79119f driver 的 `validate_outputs()`**，保留其 8 raw / 2 summary、两档各 4 轮、原第 2–4 轮与 summary 均值校验，不复制 validator 或重排原行。脚本精确锁定本地 79119f driver、35d30d common helper 和 0f2a57 只读 SQLite helper；已审阅模块顶层与导入，仅含标准库和已锁定的 common。加载时 main guard 为 false、禁写 pyc，不调用设备、网络、锁或 retained 安装函数。SQLite 重用 readonly/query_only 指纹函数，全部 source SHA 逐项复核。

其他必要门包括原 SERVER / benchmark CLI 与 MiniCPM 模型配置、0813 benchmark SHA、已锁定的 Python / package / Triton / FlagGems 身份、无 profiler / smoke、32 GiB 单卡 BI-V150。物理与可见总内存来自每条 `gpu.csv` 的 `memory.total=32768 MiB`、index 0 和型号，不能只拿 `free_mib` 代替。非 Attention 的 installed 源码必须两边相同。

原版要求 13eb 基点、Attention=bab2、真实 worker=446f12c0…，且不存在 retained module / hook / marker；候选要求 d60 基点、Attention=54c、worker=e155，以及受测 init / SQL / C2 / C3 / top-p / retained runtime 核心哈希。完整源码、GPU 记录、DB 快照、结束检查或原 CSV 任一缺失都不能通过。真实 KV 容量从 `server.log` 读取，DB before/after 的实际 SQLite 实体重算表数、行数和三种 SHA 后输出。原版 225 项归档源码及结束后 live 文件、候选 230 项归档源码均已通过。[原版源码验收](../experiments/official/20261021T122607Z-original-baseline/source-review.json)

每档输出原第 2–4 轮 Total tok/s 的算术均值、candidate/baseline 比与百分比，以及 Mean TTFT 的均值与变化率。脚本不替代准确率、并发主机负载条件核验或最终提交复现审查。保留运行时会持久改写 installed Attention，不能只切换插件 checkout 就称原始环境；本次原版已按[依赖恢复记录](../analysis/2026-10-21-original-baseline-dependency-plan.md)先恢复 bab2，并通过归档、启动后与结束后身份检查。

## 完成与封存状态

原版 benchmark 的 UTC 起止为 `2026-10-21T12:28:47.784861Z` → `2026-10-21T16:14:45.731362Z`，driver 于 `16:14:50.001906Z` 完成；benchmark 与服务最终返回码均为 0，`cleanup_errors=[]`。monitor 在清理中收到停止信号，返回 −15。完整结束检查确认 9031 的 IPv4/IPv6 均关闭、68 MiB / 0%、无 GPU 进程，server / benchmark / EngineCore 均已退出。

runner `166637` 仍有 `/proc` 项，但实际状态为 `Z (zombie)`、`PPid=1`：进程已退出，容器 PID 1 未回收，不持有设备。首次封存只在末尾“runner 的 `/proc` 项应不存在”断言失败；该失败和后续[进程状态独立说明](../experiments/official/20261021T122607Z-original-baseline/postflight-process-review.json)保留，没有改写原 driver 结果或 CSV。双方 server 日志均有 shutdown 时清理 1 个剩余进程的警告，不能称完全无告警；原版没有 ERROR / Traceback。[完整结束检查](../experiments/official/20261021T122607Z-original-baseline/postflight-full.json)、[独立终审](../experiments/official/20261021T122607Z-original-baseline/independent-final-review.json)

## 历史 smoke 记录

比较脚本最初用完整真实候选与当时只有 manifest/startup 证据的真实原版目录执行过一次 CPU smoke，退出 2 / `pending`，准确列出缺少 `result.json`、`exit-code`，`gain_computed=false` 且没有 cases。原件保存在 [smoke JSON](../analysis/2026-10-21-official-comparison-smoke.json)。之后仅补精确 worker 身份守卫，没有重跑旧 smoke 或伪造完整结果。文档曾记录的 12:57Z“原版未结束”属于该历史阶段，已由本页最终完整比较取代；原实验文件保持原样。
