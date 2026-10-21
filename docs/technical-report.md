# MiniCPM5-2B 天数 BI-V150 优化技术报告

本报告对应冻结的 SQL+C3 候选及原始 `13eb9be` 对照。候选通过独立官方准确率测试 **103/105**；双方完整官方吞吐原件均已验收。按每档原第 2–4 轮均值，候选总吞吐分别为原版的 **1.933208 倍（4K）**、**3.166027 倍（16K）**。两次运行的调优数据库初始状态与实际 KV 容量不同，以下结果是按官方协议得到的分档描述性比较，不声称缓存完全匹配、稳定因果收益或官方总分。

全部实测仅属于**天数 BI-V150**。沐曦－曦云 C500 由队友在实验分析库中另存环境、证据和报告；本报告不能外推到 C500。团队共用 `FlagOS-S2-vllm-plugin-FL` 与 `FlagGems` 两个私有代码库，不要求按平台拆分目录或分支。

## 1. 固定环境与测试方法

模型为 MiniCPM5-2B；设备为一张可见显存 32768 MiB 的 Iluvatar BI-V150。容器 CPU 配额为 6 核，不能把宿主机可见 CPU 数当作配额。PyTorch 为 `2.10.0+corex.4.5.0`，vLLM 为 `0.24.0+empty`，Triton 源版本为 `3.6.0`，FlagGems 为 `v5.3.5` / `4df52d9168ac55c1c1061cefb4638c570292d896`，SQLAlchemy 为 `2.0.48`。

插件基点为官方 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`。所有性能与准确率门保持原官方服务参数；官方吞吐脚本 SHA256 为 `0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565`。每档运行 4 次，按原脚本丢弃第 1 次，取第 2–4 次对应指标的算术均值。两档输入/输出/并发/请求数分别为 `[4096,1024,64,256]` 和 `[16384,1024,64,128]`。吞吐比用未再次舍入的 raw 指标均值计算，不用平均耗时反推吞吐。正式吞吐目录没有 profiler 或额外 smoke 请求。

准确率使用官方 `math_500` Level 3 的 105 道题，`temperature=1.0`、`top_p=0.95`、`max_tokens=32768`，batch size 8。准确率与性能分开运行。一张设备上的实验始终串行，原始 CSV 不重写。

## 2. 优化机制及证据

| 改动 | 解决的问题 | 实现范围与验证边界 |
|---|---|---|
| SQLite 目标表反射 | 新形状配置查询反复反射无关表，造成显著主机停顿 | 只为实际请求表构建 ORM 模型，保留外键依赖、键、缓存值、缺表语义和调优决定；反射改动不主动改写配置库，正常调优仍可新增配置 |
| 3D decode launch | BI-V150 上原 launch 的 warp/stage 配置使单层 decode 耗时偏高 | 严格限制 BF16、16/2 heads、head size 128 的已审计路径；仅 warps 4→2、stages 3→1，计算与归约保持；单层逐位门通过 |
| mixed Attention 分流 | 混合 batch 的单 token decode 前缀沿用面向 prefill 的 2D 路径，计算利用率低 | 仅拆分天然连续的 decode 前缀；一次建立可复用 metadata，GEMM、KV 写、请求与采样顺序保持；decode 改为 3D，归约不同，单独通过整模型准确率 |
| 保留的 prefill 策略 | 长上下文 Attention 吞吐受原 launch 配置限制 | GQA8 的 generic Triton prefill 使用 BM128/T64/warps8/stages1；精确源码与形状限制，其余路径回退 |
| 保留的 top-p 实现 | 大词表采样中的可见主机/设备开销 | 对 130560 词表、FP32 logits、仅 top-p 条件使用确定性两轮加权 histogram 实现；未加入融合 Gumbel 的实验候选 |

最直接的框架瓶颈证据来自已保存的 8 步 host profile：SQL 配置查询 13.405 秒，其中构建模型约 10.780 秒。因而采用目标表反射，而没有将所有主机空档笼统归为 JIT。重复短测中 SQL 独立候选从 120.471 秒对照降到 43.199 / 43.091 秒；这些是相同短负载的诊断证据，不能代替官方两档提升。

单层 decode launch 测得约 40% 的耗时下降，但最初端到端对照只出现约 1.2% 的单次吞吐信号，说明单层收益不能直接外推整模型。加入 SQL 后，已热的 16K / 32 请求 / 1024 输出短测中，SQL+C2 为 231.322 秒，SQL+C3 为 220.368 秒；该对照 KV 均为 521840 tokens、DB 表行数及三种指纹相同，提供约 4.97% 单次吞吐信号。正式结果仍以完整官方对照为准。

详细实现、原始时间线和失败记录见[框架实验记录](../analysis/2026-10-21-framework-experiments.md)与[实验登记表](../experiments/registry.csv)。

## 3. 准确率与完整官方对照

准确率 run `20261021T090505Z-sql-mixed-level3`：**103/105，98.0952%**，105 次请求和评估成功，零传输错误、零 token-cap 截断、零空结果。原始报告、预测、评审与命令均保存。随机采样下，103/105 相对于先前 101/105 不构成模型质量提升证据。[只读验收结果](../experiments/accuracy/20261021T090505Z-sql-mixed-level3/accuracy-review.json)

原版 run 为 `20261021T122607Z-original-baseline`，候选 run 为 `20261021T092944Z-sql-mixed-official`。两者各有 8 条 raw、2 条 summary；原第 2–4 轮、请求/token 数、汇总均值均通过原 driver 的只读校验。原版 225 项归档源码及对应 live 文件、候选 230 项归档源码 SHA 已逐项核验。双方实际可见显存均为 32768 MiB，容器 CPU 配额均为 6 核。

| 官方档位 | 原版耗时 s | 候选耗时 s | 原版 total tok/s | 候选 total tok/s | 吞吐比 | 吞吐变化 |
|---|---:|---:|---:|---:|---:|---:|
| 4K / 1024 output | 687.94 | 355.88 | 1905.46 | 3683.65 | 1.933208× | +93.3208% |
| 16K / 1024 output | 2584.99 | 816.48 | 861.99 | 2729.07 | 3.166027× | +216.6027% |

| 官方档位 | 原版 output tok/s | 候选 output tok/s | 原版 Mean TTFT ms | 候选 Mean TTFT ms | Mean TTFT 变化 |
|---|---:|---:|---:|---:|---:|
| 4K / 1024 output | 381.09 | 736.73 | 12310.56 | 4781.64 | −61.1582% |
| 16K / 1024 output | 50.70 | 160.53 | 636429.44 | 185063.65 | −70.9216% |

表内绝对值显示到两位小数；比值由 raw 均值计算，16K 原版/候选 total 均值分别为 `861.9866666666667` / `2729.0733333333333`。TTFT 负变化表示首 token 延迟降低。原件见[原版 summary](../experiments/official/20261021T122607Z-original-baseline/benchmark_results/summary_20261021_202847.csv)、[候选 summary](../experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/summary_20261021_173039.csv)；计算与全部指纹见[最终比较 JSON](../analysis/2026-10-21-official-final-comparison.json)，SHA256 为 `52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832`。[比较方法与命令](official-comparison.md)

| 实际资源与调优库状态 | 原版 | SQL+C3 候选 |
|---|---:|---:|
| KV 容量，tokens | 521840 | 521936（多 96） |
| DB before，表数 / 行数 | 512 / 19130 | 489 / 18384 |
| DB after，表数 / 行数 | 516 / 19270 | 501 / 18789 |
| 本次新增，表数 / 行数 | 4 / 140 | 12 / 405 |

两边 DB 快照的物理、schema 和逻辑内容 SHA 均已从实际 SQLite 重算；初始指纹不同，未清空或人为统一缓存。KV 容量也不同，不能把这组结果称为 cache-matched 对照，或把全部差异归因于某一项优化。每档仅保留三轮，候选 4K 第 2–4 轮耗时仍有约 3.05% 首末漂移；现有证据不证明多次独立重复的稳定性，也不用于宣称低于该波动的其他单次收益。未计算跨档总体倍数或官方总分。

原版 benchmark 于 `2026-10-21T16:14:45.731362Z` 完成，driver 于 `16:14:50.001906Z` 结束；benchmark 与服务返回码均为 0，`cleanup_errors=[]`，monitor 按清理流程停止，返回 −15。封存检查确认 9031 的 IPv4/IPv6 均关闭、无 GPU 进程、显存占用 68 MiB、利用率 0%，server、benchmark、EngineCore 均已退出。runner `166637` 已为 `Z (zombie)`、`PPid=1`，是 PID 1 未回收的进程表项，不持有设备资源。首次封存末尾要求 `/proc` 项不存在的断言因此失败；失败原件和后续[进程状态说明](../experiments/official/20261021T122607Z-original-baseline/postflight-process-review.json)一并保留，没有改写 driver 退出码或 CSV。双方 server 日志均保留 shutdown 时清理 1 个剩余进程的警告，不能称完全无告警。[原版独立终审](../experiments/official/20261021T122607Z-original-baseline/independent-final-review.json)

## 4. 保留的负结果和小收益方向

| 方向 | 实际发现 | 当前决定 |
|---|---|---|
| mixed token bucket | 冷轮新增配置后变慢，已热轮约 220.390 秒，未证实超过约 220.250 秒控制；KV 容量还存在差异 | 原型与逐位门保留，未集成 |
| BF16 hidden row gather | 真实服务启用，约 220.357 秒；与控制接近且 KV 差 96 tokens | 保留，未扩大准确率 |
| output-growth admission V2 | 控制观测到一次抢占，候选为零；warm 221.234 秒，TTFT 约增加 7.51%，跨 DB 状态比较边界另记 | 无吞吐提升，不集成 |
| 双 stream Attention overlap | 4-call wall 表面约 2.50%，64-call 仅约 0.35%，device event 持平略慢 | 计时不足以证明并行收益，不接服务 |
| full-visible-prefix mask | 正确性通过；单层 wall 约 0.276%、event 约 0.454% 的小信号 | 代码保留，尚无 E2E/准确率结论 |
| 早期更快 decode tile | 官方准确率仅 88/105 | 拒绝，未进入当前候选 |

小收益值得保留，但单层计时、安装标记和整模型收益是不同证据。实际执行标记、输出/状态正确性、热缓存与端到端对照缺一不可；验证按最短可否定门推进，未显示收益的方向不扩大为大规模准确率测试。

## 5. 复现与交付状态

完整候选补丁为 [sql-mixed-decode-full.patch](../patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch)，SHA256 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`。它在原 `13eb9be` 上一次应用，生成的候选 Git tree 为 `5c14cfb8d3a452e97a67758873bf18039e1bf989`。独立 CPU 审阅确认 212 份归档仓库文件、核心源码、文件模式和 MoE symlink 一致，逆向应用精确恢复原始 tree。该包装证明代码与受测候选一致，不新增性能或准确率证据。[完整补丁说明](../analysis/2026-10-21-sql-mixed-full-package.md)

关键复现经验：retained runtime 会持久修改已安装的 Attention，单独切换插件 checkout 不能还原原版。本次原版基线前已在设备空闲、锁内备份并精确恢复 Attention 至原始 SHA `bab2c0b9f9a7793ca411796b48ebb4734433160e7e99eabf46ddb7f1c30cb6e0`；启动后、归档与结束后 live 文件均通过此身份校验。候选对应 SHA 为 `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f`。原版测量期间禁止导入 retained/C3 平台模块。[依赖恢复记录](../analysis/2026-10-21-original-baseline-dependency-plan.md)

原版完整对照验收已完成，冻结候选与证据用于团队独立复现；团队复现与最终提交选择仍待团队推进。两个私有源码库已上传并核验，精确版本与协作入口见[GitHub 协作记录](github-collaboration.md)。既有默认 `vllm-plugin-FL-biv150-performance.patch` 未被覆盖，新的探索候选均未混入此受测 SQL+C3 完整补丁。规则中不完整的计分边界仍按[官方核实记录](official-verification.md)标注，不能自创公式。本报告封存本轮已完成的稳定基点；后续持续优化另建实验记录，不覆盖此处原始证据。既有参考仓库只读，仅向获授权的本实验协作仓库发布。阶段状态和子智能体工作见 [CURRENT_WORK](../CURRENT_WORK.md) 与[交接索引](agent-work-index.md)。
