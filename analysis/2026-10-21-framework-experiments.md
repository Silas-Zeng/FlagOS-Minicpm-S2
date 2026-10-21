# 2026-10-21 框架实验记录

本轮按“优先大收益，小而稳定的收益也保留；先最短必要验证”推进。设备实验由唯一 device owner 串行执行；本记录作者只阅读本地证据。以下全部数据仅属天数BI-V150，沐曦－曦云C500由队友负责。官方服务参数和benchmark文件未修改，SQL+C2与SQL+C3分别以101/105、103/105通过独立math_500 Level 3门槛。原13eb与SQL+C3完整官方两档现均完成并独立终审，原第2–4轮均值的分档吞吐比为4K **1.933207729倍**、16K **3.166027317倍**；初始DB不同、KV差96tokens，不称cache-matched因果稳定收益，不合成官方总分。短诊断、metadata gate和单层计时不混入正式结果。

最新状态：原版122607于2026-10-21 **16:14:50.001906Z**由原driver以exit0完成，8raw/2summary原件本地终审通过；archive/live225项与最终Attention bab2一致，fullpost68MiB/0%/9031双栈闭/无GPU进程。runner166637为已退出的Z/PPid1，首次seal末/proc不存在断言失败与独立说明保留。用户16:40Z授权继续自主探索，root仍唯一GPUowner；新增173003 C3覆盖诊断、173921 CTA拒绝门及174115 CPUmetadata通过门均已独立审计，后两者都不能当服务性能。growth/hidden/bucket既有边界不变。下述running/等待/冻结段均为历史，最终原件和新研究见末节。

## B0/C1：集成可运行，不能认定端到端加速

B0 是保留的 attention/top-p 补丁；C1 在其上增加 zero-dirty block-table 提交跳过。两次 manifest 的服务命令相同，短负载命令保存在各自 `load-commands.json`。下表仅转录原始 benchmark JSON，不能跨行据此计算候选加速。

| run / 输入、输出、并发、请求数 | 完成 / 失败 | 耗时 s | total tok/s |
|---|---:|---:|---:|
| B0 / 4096、32、16、16 | 16 / 0 | 47.138132 | 1401.158607 |
| C1 / 4096、32、16、16 | 16 / 0 | 32.902975 | 2007.356500 |
| B0 / 16384、16、8、8 | 8 / 0 | 29.569240 | 4437.043372 |
| C1 / 16384、16、8、8 | 8 / 0 | 28.356858 | 4626.746799 |

两次各完成 24 个负载请求且零失败，但 C1 计时期间另有远端 CPU 导入检查，host 工作负载不一致；两次服务 KV 容量为 521840 与 521936 token，相差 96 token。B0/C1 的单请求 greedy 文本不同，随后 B0 自身也出现不稳定，故不能单独归因给 C1，也没有排除 C1 风险。C1 没有导出服务内 skip 统计，不能从更短耗时反推它的实际命中率。

来源：[B0 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T030349Z-b0/manifest.json>)、[C1 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T031102Z-c1/manifest.json>)；[B0 4K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T030349Z-b0/4k/results/4k-infqps-concurrency16-minicpm-20261021-110721.json>)、[B0 16K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T030349Z-b0/16k/results/16k-infqps-concurrency8-minicpm-20261021-110812.json>)、[C1 4K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T031102Z-c1/4k/results/4k-infqps-concurrency16-minicpm-20261021-111423.json>)、[C1 16K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T031102Z-c1/16k/results/16k-infqps-concurrency8-minicpm-20261021-111512.json>)。KV 容量直接见 [B0 服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T030349Z-b0/server.log:81>)与 [C1 服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T031102Z-c1/server.log:81>)。

源码身份保存在 manifest：B0 `plugin_revision=d60b02367a852826f653165953f31b6dc696658e`；C1 明确为同一 `plugin_base_revision` 加补丁，不把 base 冒充候选完整 commit。FlagGems 均为 `4df52d9168ac55c1c1061cefb4638c570292d896`。runner、runtime、top-p、block-table 和官方 benchmark 的 SHA256 均保留在上述原始 manifest；候选精确身份以文件 hash 为准。

## metadata gate 与 B0 自重复

[metadata 结果](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T032830Z-metadata-gate/result.json>)记录状态机 32 步、graph replay 3 次全部 pass；覆盖 append、move、swap、clear、active 范围变化和外部 device padding。scoped commit 共 35 次，其中 skip 21、copy 14；非 scoped commit 原路径 copy 1 次。它证明隔离 metadata/graph 行为，没有加载模型、scheduler 或 accuracy benchmark。

稳定表微计时保留了所有 outlier：batch64 原实现 wall 每 commit 为 1608.426、1557.953、176.045 微秒，对应 stream interval 为 136.336、154.117、135.882 微秒；候选 wall 为 11.035、9.755、5.813 微秒。稳定表本就是最有利场景，wall 包含 host 提交/被调度间隙，event interval 也不等于纯 DMA；这些值不能换算成百倍 DMA 或端到端加速。具体原始样本、限制和 source hashes 见 [metadata manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T032830Z-metadata-gate/manifest.json>)及结果 JSON。

[B0 repeat manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T033437Z-b0-repeat-smoke/manifest.json>)记录同服务重复 3 次。[请求 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T033437Z-b0-repeat-smoke/smoke-request.json>)固定 temperature=0、seed=71、max_tokens=32。结果 r1=r3、r2 不同；首个 token 分歧为零基 index11，r1 的 `understand` 高于 `make` 0.0625，而 r2 两词并列。来源：[r1](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T033437Z-b0-repeat-smoke/smoke.json>)、[r2](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T033437Z-b0-repeat-smoke/smoke-r2.json>)、[r3](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T033437Z-b0-repeat-smoke/smoke-r3.json>)。这说明本轮 greedy 比较基准自身不稳定，原因尚未归因。

## Attention 最短筛选

`20261021T035155Z-attention-dispatch` 因脚本对 `source/__pycache__` 目录执行 `read_bytes()` 而报 IsADirectoryError，results 为空、exit_code=1。这是实验脚本失败，不是候选正确性或性能失败；未完成的 hash 字段保持缺失。原错误与 source 仍保存在 [失败 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035155Z-attention-dispatch/manifest.json>)。

修复后的 `20261021T035322Z-attention-dispatch` 在 dense-4k、dense-16k、padded-tail、zero-middle、prefill-fallback 共 5 个 direct-decode case 上 finite 且 bitwise equal。单层 graph 计时：4K 从 1.699885 到 1.678350 ms，16K 从 3.020269 到 3.015108 ms。4K 约 1.3% 的单层小信号保留为候选，未建立整模型收益或 accuracy 结论。该 run 还包含两个 mixed 初筛，完整保留在 [结果 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035322Z-attention-dispatch/results.json>)与 [manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035322Z-attention-dispatch/manifest.json>)。

`20261021T035611Z-mixed-dispatch` 对更接近当前批次的 mixed 形状做了单层非 graph 筛选。metadata normalization 在计时外，结果对实际集成偏有利：

| KV / decode D / prefill P | whole ms | split ms | 延迟降低 |
|---|---:|---:|---:|
| 4096 / 63 / 1985 | 3.974296 | 3.955988 | 0.461% |
| 4096 / 63 / 127 | 2.039400 | 2.051873 | -0.612% |
| 16384 / 29 / 2019 | 13.718111 | 13.622354 | 0.698% |
| 16384 / 29 / 127 | 4.732004 | 4.408543 | 6.836% |

全部 prefill bitwise equal；decode 最大绝对差依次为 0.00244140625、0.001953125、0.00048828125、0.00048828125。数学 masked 比例不等于真实 latency：该旧 decode 实现下，满 chunk 的净收益不到 1%，4K 短尾倒退，当时仅保留 16K 小尾块条件候选。它不永久否定 mixed 分流，后文 051426 用更快 decode 路径重新筛选。来源：[mixed 结果](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035611Z-mixed-dispatch/results.json>)、[mixed manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035611Z-mixed-dispatch/manifest.json>)。本地 source 文件与两个成功 dispatch manifest 的全部 SHA256 已逐项核对一致；未列 source commit 的 run 不猜 commit。

三个 `*-control` 目录仅是 launcher 的 PID/log 附件，不是独立对照设备测量：[035155 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035155Z-attention-control/runner.log>)、[035322 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035322Z-attention-control/runner.log>)、[035611 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T035611Z-mixed-control/runner.log>)。

## native profiling：已获得有效窗口，图内热点仍未解析

首轮 `20261021T040856Z-native-decode` 因 ixsys 拆分 JSON argv 失败，不涉及模型/候选比较。原始证据已补取：[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T040856Z-native-decode/manifest.json>)记录 UTC 起始 `04:08:56.688070`、plugin base 与文件 SHA256；[server.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T040856Z-native-decode/server.log:42>)显示 `--compilation-config` 被截成 `{"cudagraph_mode":`，vllm 子进程 exit 2；[runner.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T040856Z-native-decode/runner.log>)显示服务未 ready，driver [exit-code](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T040856Z-native-decode/exit-code>)为 1。registry 已据 manifest 补全身份，负载字段留空，不把启动失败当候选失败。

修复后的 `20261021T041625Z-native-decode` 用 [server-entry.sh](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/server-entry.sh>)保留服务 argv，已结束，[exit-code](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/exit-code>)为 0，[GPU 最后采样](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/gpu.csv>)显存占用回到 68 MiB。服务参数、源码 SHA256、ixsys 包装和诊断负载分别保存在 [manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/manifest.json>)、[launch-command](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/launch-command.json>)、[load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/load-commands.json>)。

**没有有效 GPU 轨迹，不能用于热点或性能归因。** 没有 START/STOP 窗口记录；[native-trace.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/native-trace.json>)文件头实际为 `SQLite format 3`，并非 JSON。只读检查 `cu_api`、`cu_kernel`、`cuda_api_data`、`cuda_kernel_data`、`cuda_graph_data` 五表的行数均为 0。文件成功保存、进程退出成功都不能替代有效性检查。[server.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T041625Z-native-decode/server.log:233>)末尾的 EngineDeadError 出现在停服务阶段，保留记录，不据此判候选失败。

第三轮 `20261021T042609Z-native-decode` 已结束，[exit-code](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/exit-code>)为 0，[GPU 最后采样](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/gpu.csv>)回到 68 MiB。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/manifest.json>)的服务 argv 与上一轮完全一致；[诊断命令](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/load-commands.json>)仅把负载改为 64 请求、4096 输入、128 输出、并发 64，不构成性能成绩。[事件文件](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/native-events.jsonl>)确认指定 EngineCore 副本已加载，START/STOP 正常，5 个纯 decode 步的实际 batch 为 62、62、61、61、60，max query len 均为 1；[native-validation](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/native-validation.json>)为 `valid=true`。

对 [原始 SQLite trace](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T042609Z-native-decode/native-trace.json>)只读复核：`cuda_api_data` 3157 行、`cuda_kernel_data` 163 行、`cuda_graph_data` 5 行。5 个整 graph 的 `dur` 总计 401.683256 ms、中位数 80.322144 ms；外部 163 个 kernel 的 `dur` 总计 13.416306 ms（按原始纳秒值除以 10⁶）。轨迹仅显示整 graph，没有 graph 内部 MM/Attention 节点，因此有效采集不等于图内热点已解析；不能用外部 kernel 占比反推整图 GEMM 时间。以上均为 profiler 诊断值，不用于 B0/C1 加速或官方吞吐比较。

## graph event 最短能力门：当前方案失败

`20261021T044007Z-graph-events` 先用 tiny graph 验证当前 CoreX 环境的 `torch.cuda.Event(enable_timing=True, external=True)`。[probe.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T044007Z-graph-events/probe.py>)在 graph replay 与 synchronize 后调用 `elapsed_time`；[result.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T044007Z-graph-events/result.json>)记录 `ixErrorInvalidResourceHandle`、`passed=false`、exit 1，没有有效计时。它只否定这次 external timing-event 方案，不能推出所有 event 形式不支持，因此未扩成全模型插桩。device owner 另确认设备回到 68 MiB；现有两份附件未保存该采样。

执行命令为 `python3 /workspace/experiments/minicpm-s2/scripts/probe_graph_events.py /workspace/experiments/minicpm-s2/framework/20261021T044007Z-graph-events`；保留 probe 的本地 SHA256：`991d29b6ed82a7d6a98e07170912cde2737a0c9d1a86362c330a9c8747bc2f31`。无 manifest commit 的字段保持为空，不新增性能结论。

## decode launch：较大单层信号，尚无整模型结论

`20261021T044807Z-decode-launch` 的 [manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T044807Z-decode-launch/manifest.json>)与 [results.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T044807Z-decode-launch/results.json>)记录 exit 0。固定 BM16、T16、16 segments、grid/reducer 与算术路径，只改变 3D decode 的 warps/stages。C0 保留原始源码的隐式默认配置；backend options 实测为 4 warps、3 stages、warp_size=64，保留的编译记录支持该配置，但缓存记录未逐 case 对应，不能把所有缓存项当作同一配置。

C0 在 5 个 case 上自重复通过；4 个 variant 各 5 个 gate，以及 10 个计时后 graph check，均 finite、bitwise equal、max_abs_diff=0。只比较有效 packed query token；padding 未定义区域不纳入结论。case 包含 dense-4k、dense-16k、padded-tail、zero-middle、prefill-fallback。

下表为各 5 次 CUDA graph replay 计时的中位数，百分比统一按 `1−variant/C0` 计算：

| variant | 4K / 64 ms | 延迟降低 | 16K / 30 ms | 延迟降低 |
|---|---:|---:|---:|---:|
| C0 | 1.695558 | — | 3.024362 | — |
| w4s3 | 1.689942 | 0.33% | 3.025992 | -0.05% |
| w4s1 | 1.176388 | 30.62% | 2.122481 | 29.82% |
| w2s3 | 2.024185 | -19.38% | 3.616050 | -19.56% |
| w2s1 | 0.997373 | 41.18% | 1.803277 | 40.37% |

w2s1 是值得接入服务筛选的单层信号；w2s3 倒退，说明只减 warp 不能替代这组联合设置。该 run 没有新端到端或 accuracy 结论，也不是官方分数。原始时序样本完整保留，11 个本地 source 文件 SHA256 均与 manifest 一致；其中 transform 为 `b4f3698c2a1404d056f223d6ee0983dbd2f4c7be8d4677a93c18316132619708`，benchmark 为 `cfb07b0032a56491ed3c02022dd8f93934e3015a232646ec17510d1df5beaee5`。[control runner.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T044807Z-decode-launch-control/runner.log>)仅为 launcher 附件，不是独立对照测量。

服务接入使用另一个 [runtime 文件](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/biv150_decode_launch_runtime.py>)，本地 SHA256 为 `e5f68a303f991f1e5ce1145941d44350d280a85090db94045b653e3828c3ed5f`；它不属于上述微测 transform，服务内选中与负载结果单独记录如下，不能仅凭微测推定接入成功。

## mixed-fast：更快 decode 改变了分流收益

`20261021T051426Z-mixed-fast` 已 exit 0。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051426Z-mixed-fast/manifest.json>)明确对照为 whole retained 2D，候选为 w2s1 decode 前缀加 retained prefill 后缀。[results.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051426Z-mixed-fast/results.json>)的每条路径均为 2 次 warmup、5 个 eager CUDA event 样本；计时前后全部 prefill bitwise equal，decode 有限但不 bitwise：

| KV / D / P | whole 中位 ms | split 中位 ms | 延迟降低 | decode 最大绝对差 |
|---|---:|---:|---:|---:|
| 4096 / 63 / 1985 | 3.944012 | 3.249423 | 17.61% | 0.00244140625 |
| 4096 / 63 / 127 | 2.048785 | 1.361700 | 33.54% | 0.001953125 |
| 16384 / 29 / 2019 | 13.796485 | 12.391527 | 10.18% | 0.00048828125 |
| 16384 / 29 / 127 | 4.723950 | 3.181777 | 32.65% | 0.00048828125 |

旧慢 decode 的满 chunk `<1%` 不是永久否定：框架分流的收益取决于子路径实现，此轮 w2s1 使两个满 chunk 都出现更大单层信号。metadata view 和 cu-query normalization 在计时外，event interval 仍可能含 eager host 提交间隙；没有测模型、GEMM、scheduler、KV 写或 sampling，属于乐观筛选，不是 accuracy 或端到端收益。8 个 source 文件与 manifest SHA256 全部一致；[control 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051426Z-mixed-fast-control/runner.log>)仅为 launcher 附件。

## 短服务接入与持续 decode 筛选

`20261021T045834Z-b0-launch-pair` 已 exit 0，完成默认短接入负载；它不是当前主性能 pair 的 matched B0 baseline。两档原始结果为：

| B0 输入 / 输出 / 并发 / 请求数 | 完成 / 失败 | 耗时 s |
|---|---:|---:|
| 4096 / 32 / 16 / 16 | 16 / 0 | 33.412913 |
| 16384 / 16 / 8 / 8 | 8 / 0 | 28.237920 |

来源：[4K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T045834Z-b0-launch-pair/4k/results/4k-infqps-concurrency16-minicpm-20261021-130159.json>)、[16K JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T045834Z-b0-launch-pair/16k/results/16k-infqps-concurrency8-minicpm-20261021-130249.json>)、[B0 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T045834Z-b0-launch-pair/manifest.json>)与 [load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T045834Z-b0-launch-pair/load-commands.json>)；4K seed 为 721101，16K 为 721102。

`20261021T050517Z-c2-decode-screen` 已 exit 0。[C2 结果 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-131008.json>)记录 64 请求、4096 输入、128 输出、并发 64，完成 64、失败 0，耗时 119.224039 s。[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/server.log:62>)包含 `INSTALLED` 与 `FIRST_SELECTED` marker；后者出现在 graph capture 日志段，确认候选已接入选中路径，没有提供逐步命中率。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/postflight.json>)记录 68 MiB、9031 端口关闭。

[C2 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/manifest.json>)与 B0 的官方 SERVER argv 逐项相同，均无 native profiler；两份 launch-command 亦与各自 manifest 相符。共同的 benchmark、Attention/helper、block-table、MM、模型配置与既有 runtime/top-p 的 hash 相同；C2 runner 与新增 decode-launch runtime 的精确身份保存在 manifest，后者与本地 `e5f68a…` 文件一致。[C2 load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/load-commands.json>)启用持续高并发 decode 诊断负载，seed 721101。

同负载 `20261021T051639Z-b0-decode-screen` 已 exit 0；[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/postflight.json>)为 68 MiB、9031 端口关闭。它与 C2 的 SERVER argv、seed 721101、负载参数和 driver SHA256 `fc351acfc8f579844f13fc8b61a1d8800512ff6a70eda9ef6a3ccb702a02fb97` 一致，均无 profiler。来源：[B0 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/manifest.json>)、[B0 load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/load-commands.json>)及两目录保存的 `screen-driver.py`。

`20261021T054922Z-c3-mixed-screen` 也已 exit 0。[C3 结果 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-135412.json>)为 64 完成、0 失败、输入 262144 / 输出 8192 token，与 B0/C2 相同。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/manifest.json>)、[load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/load-commands.json>)与本地 driver 核实 SERVER / 负载 / seed / driver 同前两次，均无 profiler。三份 manifest 共同的 9 项 source hash 一致；C3 runner、新增 mixed 模块的身份另存 manifest，runtime `e5f68a…` 与 mixed `a12936…` 均和本地候选一致。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/postflight.json>)为 68 MiB、9031 端口关闭。

| 同负载单次诊断 | 完成 / 失败 | 耗时 s | total tok/s | median ITL ms |
|---|---:|---:|---:|---:|
| B0 051639 | 64 / 0 | 120.671052 | 2240.272178 | 213.859562 |
| C2 050517 | 64 / 0 | 119.224039 | 2267.462181 | 225.917219 |
| C3 054922 | 64 / 0 | 117.259174 | 2305.457148 | 213.672963 |

B0/C2 数字来自 [B0 结果 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-132129.json>)与上述 C2 JSON，C3 见前述 C3 JSON。单 pair 吞吐比值为 `C2/B0−1=+1.21369%`，仅保留小而未确认的信号；C2 median ITL 反而更差。KV 容量仍有差异：[B0 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/server.log:84>)为 521936、[C2 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/server.log:85>)为 521840，少 96 token。CPU 各新增 4 次节流，但累计 `throttled_time` 增量分别为 20.871367 / 16.101544 s，不能因次数相同就认定 host 条件一致；该累计量也不是 GPU 耗时。原始差分来源：[B0 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T051639Z-b0-decode-screen/cpu-after-decode-4k.json>)、[C2 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T050517Z-c2-decode-screen/cpu-after-decode-4k.json>)。

C3 按原始值计算，相对 B0 / C2 的吞吐差为 **+2.909690% / +1.675660%**，耗时降低 **2.827421% / 1.648045%**。这仍是各配置仅一次的诊断，不构成稳定收益或显著性结论。C3 median ITL 接近 B0；[C3 KV 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/server.log:86>)为 521936，与 B0 相同、比 C2 多 96 token。[C3 CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/cpu-after-decode-4k.json>)新增 `nr_periods=1391`、`nr_throttled=4`、`throttled_time=17.182372 s`，host 差分仍不相同。[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054922Z-c3-mixed-screen/server.log:62>)包含 decode-launch 与 mixed 两个 installed marker，以及 capture 期 decode first-selected；没有导出真实服务内 mixed 分流命中次数或阶段耗时，不能把这次小差值全部归因于 mixed。

**尚不能宣称稳定收益，没有新增 accuracy 或官方性能成绩。** 不把单层约 40% 换算为整模型约 40%；这些诊断不与 045834 的短负载或任何 native profiling run 混比。

## mixed 真实 metadata gate：集成比较通过，accuracy 未测

此前 [框架模块](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/biv150_mixed_decode.py>)已交叉审查，[CPU tests](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tests/test_biv150_mixed_decode.py>)已有 10 项通过。`20261021T054501Z-mixed-gate` 另以真实 VllmConfig、FullAttentionSpec、Builder、Impl 运行 synthetic Q/K/V，已 exit 0，未加载模型权重。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054501Z-mixed-gate/manifest.json>)保存实际 API 签名、解析配置、安装结果、命令和 source hashes；安装顺序修正后的 [validation.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054501Z-mixed-gate/source/validation.py>) SHA256 为 `b6275ee86f4fb24824091e72fccd774d174247975f8189d360400f333a20351f`。12 个归档 source hash 逐项一致。

[results.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054501Z-mixed-gate/results.json>)记录 4 个 mixed case 的 `patched_vs_manual_entire_storage` 全部 finite、bitwise equal、max_abs_diff=0，返回 output alias 均保持，每个 case 有 1 次 fast decode launch。prefill 相对 whole 2D 仍 exact；decode 相对 whole 2D 均有限但不 bitwise，最大绝对差最高 0.00341796875。手工 split 相等证明 wrapper 接入一致，不证明 2D→3D decode 的模型 accuracy。

跨 stream 的 D63 / P127 / 4K case 记录 `consumer_registered=true`、`suffix_alive_while_plan_held=true`，删除 Python 引用后、consumer sync 前的 `suffix_python_released_before_consumer_sync=true`；`allocator_churn_reused_suffix_address=false`。这次验证了注册、持有和释放过程，没有实际观察到该地址被 churn 复用，不能声称穷尽所有 race/schedule。pure decode 的 `no_split_plan=true`，eager 与 1 次 graph replay 均 bitwise、finite、max_abs_diff=0。

该 gate 没有计时或模型 accuracy 结果；[control 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T054501Z-mixed-gate-control/runner.log>)仅为 launcher 附件。可审查增量为 [C2 decode-launch patch](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/candidates/vllm-plugin-FL-biv150-decode-launch.patch>)及其后应用的 [C3 mixed-decode patch](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/candidates/vllm-plugin-FL-biv150-mixed-decode.patch>)；两者仍为候选，未选为默认，也没有新增 accuracy 声明。

## host gap：定位到 SQL 配置查询与全库反射

`20261021T061506Z-host-gap` 已 exit 0，[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/postflight.json>)记录 68 MiB / 32700 MiB free / 0% 与 9031 端口关闭。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/manifest.json>)保留官方 SERVER argv、seed 721101、基础 revision 加 profiling footer 的 source hash；[诊断命令](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/load-commands.json>)为 64 请求 / 4K 输入 / 128 输出 / 并发 64。该 run 启用 host profiling，不与 B0/C2/C3 无 profiler 结果比较吞吐。[control 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap-control/runner.log>)只作 launcher 附件。

[validation](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-validation.json>)为 valid / complete，抓到 8 步纯 decode，active 为 62、62、61、61、60、60、59、59；均 pad 到 64。[窗口 summary](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-window-summary.json>)的 wall 为 13.947645 s、owner-thread CPU 为 13.944052 s、process CPU 为 14.058893 s。线程 CPU 几乎覆盖窗口 wall，支持本窗口主要存在 host 工作；这些值均为诊断值。

下表从 [原始 pstats](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-window.pstats>)只读提取，完整可读排序另见 [top-cumulative](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-top-cumulative.txt>)。**cumulative 是嵌套时间，不能逐行相加。**

| 调用 | 次数 | cumulative s |
|---|---:|---:|
| execute_model | 8 | 13.709609 |
| _prepare_input_ids | 8 | 13.445597 |
| SQL get_config | 24 | 13.405416 |
| get_sql_model | 24 | 10.781010 |
| build_sql_model_by_db | 4 | 10.780098 |
| SQLAlchemy automap.prepare | 4 | 9.114735 |
| schema.reflect | 4 | 6.228523 |

[原始 wall/CPU spans](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/host-walltime.jsonl>)中，各 active shape 首次观察时的 `_prepare_input_ids` wall 为 3.352364、3.366025、3.354633、3.370906 s，同 shape 下一步分别为 0.000962、0.000934、0.000964、0.000917 s。这里“首次”只指本次真实 execute 观察，不代表进程冷启动 JIT。cProfile 中 4 个 int32 index wrapper 输入 shape 为 63/62/61/60，各累计约 3.34 s，和上一轮 `prev_sampled_token_ids` 行数变化相符；相反，hidden `[64,2048]` gather 的 8 次累计仅 0.089264 s。当前证据定位到 SQL 配置/ORM 工作，尚未证明主要成本来自 Triton 编译。

[实际 sql.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/profiles/20261021T061506Z-host-gap/source/sql.py:140>)的 `build_sql_model_by_db(name, engine)` 每次新建 automap base、全库 prepare 后才取目标 class。该文件与 sidecar SHA256 `6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7` 相符；归档 runner/index/libentry/pointwise 四份文件也与 manifest 逐项一致。优先验证 SQLite 仅反射目标表的框架修复，保持 DB 行、key 与 tuning config 不变；不把 profile 中的累计时间直接当作可兑现端到端收益。

本窗口 cProfile 只覆盖 enabling thread；spans 含原有等待、没有新增同步。异步输出可能跨窗口或重叠，不能把 nested span 相加；`_model_forward` 的 host 提交时间也不是 GPU graph 耗时。没有新增 accuracy 或官方成绩。

## async token 整数 gate：通过真实方法对照，未测性能

`20261021T063353Z-async-token-gate` 已 exit 0。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T063353Z-async-token-gate/manifest.json>)保留命令、预检、worker PID 和 7 个 source hashes，归档文件逐项核实一致；validation SHA256 为 `607cd994db8e5c1d913907ac56cb316c26027dc9d011a71dcc66ddd051a8a9e0`。它从固定原版/变换后的 runner 抽取真实 `_prepare_input_ids`，用 stub config/buffers 比较，无模型权重或完整 scheduler/service。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T063353Z-async-token-gate/postflight.json>)在 worker 退出后于 UTC `06:34:08.498822` 记录 68 MiB、0%、9031 关闭。

[results.json](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T063353Z-async-token-gate/results.json>)的 12 个 case 全部通过：identity slice、无 previous、empty、无 common、删除/condense、reorder、新 prefill 空洞、正 stride、int64 回退、prompt-embed 回退、spec/draft 回退、cross-stream。所有 `input_ids`、`inputs_embeds`、`is_token_ids` 完整 storage 及原 H2D 调用记录一致，padding 与 stride 空洞不变，候选选中/回退次数符合预期。

5 组 invalid mapping 均在 launch 前拒绝且没有写入，包括源/目标负索引、上界和重复目标；未执行原版越界 GPU 操作，不能声称错误文本等价。固定地址、dtype、stride 下，previous rows 62/61/60（实际 N 为 61/60/59）全部选中且完整 storage exact，三次 cache 均为相同 key 的 1 entry，`no_new_entries_after_first_dynamic_shape=true`。这只是该序列的动态维度证据，不保证任意地址对齐或布局永远只有一个编译产物。

cross-stream case 由 caller 显式 wait 保证原有数据 ready；record_stream 仅管理分配器生命周期，不是同步，也不穷尽所有 race/allocator schedule。本 gate 无计时、不证明模型 accuracy 或端到端收益。[control 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T063353Z-async-token-gate-control/runner.log>)仅为 launcher 附件。该候选保留，当前优先独立验证 SQL 框架修复。

## SQL 目标表反射：较大信号已在短负载重复出现

`20261021T064632Z-sql-reflection-screen` 与新对照 `20261021T071554Z-b0-sql-pair` 均已 exit 0。SQL 候选独立基于保留 d60 加 `biv150_sql_reflection.py` 与安装 footer，没有叠加 C2/C3/整数 fused；官方 SERVER、benchmark、Attention、MM 和采样路径保持。原始身份见 [SQL manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/manifest.json>)、[B0 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/manifest.json>)；SQL runtime SHA256 `ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e` 与本地候选一致，实际 sql.py 仍为 `6dc19c…`，安装时替换静态方法。

本 pair 两个 manifest/launch-command 的 SERVER argv 逐项相同，[SQL load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/load-commands.json>)与 [B0 load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/load-commands.json>)除输出目录外相同，seed 721101，均无 host/native profiler。driver SHA256 均为 `22a076e79a486712ae5c0655b17a9ee986e51b987083bdcb64fdbc4840ea5603`；共同 10 项 source hash 与 package 版本一致。实际服务 SQLAlchemy 为 **2.0.48**，此前本地真实 SQLAlchemy CPU gate 为 2.0.43，版本差异保留，不能将 CPU 测试环境写成服务环境。

| 同负载短诊断 | 完成 / 失败 | 耗时 s | total tok/s | median ITL ms |
|---|---:|---:|---:|---:|
| B0 071554 | 64 / 0 | 120.471475 | 2243.983475 | 222.960422 |
| SQL 064632 | 64 / 0 | 43.198655 | 6257.972600 | 129.494255 |
| SQL 重复 072153 | 64 / 0 | 43.090572 | 6273.669276 | 124.503668 |

[B0 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-152045.json>)与 [SQL JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-144829.json>)的输入/输出总量均为 262144 / 8192 token。按未舍入原始值，SQL/B0 吞吐比为 **2.788778380 倍（+178.877838%）**、耗时降低 **64.142005%**。该首次 pair 各有一次样本，后续重复另列；这些均是短负载筛选，不是稳定因果结论、官方分数或新 accuracy 结果。

随后 `20261021T072153Z-sql-reflection-screen` 已 exit 0。[重复 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-152350.json>)仍为 64 / 0、262144 / 8192 token；[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/manifest.json>)的 source 文件 hash、packages、SERVER、seed 与首轮 SQL 一致，driver 亦为 `22a076e…`，[load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/load-commands.json>)仅目录不同。[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/server.log:62>)有 SQL installed，KV 仍为 521840。重复相对同一 B0 的吞吐比为 **2.795773385 倍（+179.577338%）**、耗时降低 **64.231722%**；相对首次 SQL，吞吐只高 **0.250827%**。两次候选相近，构成更强的重复筛选信号，但 B0 仍仅该次、请求 seed 也相同，不能升级为稳定因果、官方成绩或新 accuracy 声明。

[SQL 日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/server.log:62>)有安装 marker；[SQL KV](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/server.log:85>)与 [B0 KV](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/server.log:84>)均为 521840 token。CPU 前后 JSON 中两次各新增 4 次节流，但 SQL/B0 的 `nr_periods` 增量为 653 / 1426，累计 `throttled_time` 为 14.992383 / 19.151613 s；它既不能证明 host 负载完全相同，也不是 GPU 或单请求等待时间。来源：[SQL 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/cpu-after-decode-4k.json>)、[B0 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/cpu-after-decode-4k.json>)。

[SQL postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen/postflight.json>)于 UTC 07:15:47、[B0 postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair/postflight.json>)于 07:21:53 均记录 68 MiB / 0%、9031 关闭。两次持久 tuning DB 初态未做内容快照，不能额外宣称 DB 内容与命中状态逐字一致；复现应留存 schema/表数、目标配置和冷热状态，避免靠删库、清表或特定 warmup 制造差值。[SQL control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T064632Z-sql-reflection-screen-control/runner.log>)与 [B0 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T071554Z-b0-sql-pair-control/runner.log>)只作 launcher 附件。

[重复 CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/cpu-after-decode-4k.json>)增量为 646 periods、5 次节流、12.427074 s 累计 throttled time；同样不假定 host 条件完全相同。[重复 postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen/postflight.json>)于 UTC 07:24:45 记录 68 MiB / 0%、9031 关闭；[重复 control](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072153Z-sql-reflection-screen-control/runner.log>)仍只作 launcher 附件。

`20261021T072702Z-sql-cpu-gate` 另补齐与服务相同依赖版本的真实 SQLAlchemy CPU 门。[environment](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/environment.txt>)记录 Python 3.12.11 / SQLAlchemy 2.0.48，[command](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/command.txt>)运行原 6 项 unittest，[gate.log](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/gate.log>)为 6/6 OK、0.853 s、exit 0。覆盖真实配置读写/不覆盖已有值、缺表后新表可见、多表仅反射目标且列/PK/行一致、quoted name/默认 FK 闭包、两 engine 并发隔离及回退/hash/idempotence。此耗时为测试执行时间，不是反射加速基准；未启 GPU、未新增模型 accuracy 结果。[source.sha256](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T072702Z-sql-cpu-gate/source.sha256>)中的 runtime/test/fixture 三份归档文件逐项匹配原 hash；没有 manifest 或明确起始时刻的 registry 字段留空。

## SQL+C2 组合：短测完成，独立 accuracy 通过

`20261021T073309Z-sql-decode-screen` 已 exit 0，组合源为 d60 加 SQL 目标表反射与 C2 decode launch，未叠加 C3/整数 fused。[原始结果](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-153505.json>)为 64 完成 / 0 失败，262144 输入 / 8192 输出 token，耗时 **41.15406773984432 s**、total **6568.876780514884 tok/s**、median ITL **92.26066176779568 ms**。这是一次组合短筛选，没有新增官方性能成绩。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/manifest.json>)与 [control source hashes](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen-control/source.sha256>)一致：runner `7ddf885ac0fc95af291a67f7e6289224af00ccdde7cbf286deb5302780bd6953`、SQL runtime `ad84c9a…`、C2 runtime `e5f68a3…`；SERVER、seed 721101、4K/128/64/64 负载和 driver `22a076e…` 保持，未启 profiler。

[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/server.log:62>)有两个安装 marker，C2 `FIRST_SELECTED` 首次出现在 graph capture；没有服务实际命中次数统计。KV 容量为 **521936** token，比 SQL-only 的 521840 多 96，不据此计算可归因于 C2 的增量加速。[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/cpu-after-decode-4k.json>)仍为 quota/period 600000/100000，新增 630 periods、4 次节流、18.773013462 s 累计 throttled time；不等于 GPU 或请求等待时间。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen/postflight.json>)于 UTC 07:35:58.660801 记录 68 MiB、0%、9031 关闭。

本次 control 留存 [DB 前快照 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen-control/db-before/manifest.json>)与 [DB 后快照 manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T073309Z-sql-decode-screen-control/db-after/manifest.json>)：两次均 479 表 / 17982 行，schema hash、logical content hash 及 snapshot file hash 均相同。它记录本 run 前后状态，不补证明此前 SQL/B0 的 DB 初态相同；快照 manifest 与 SQLite 本体均已保存在远端和本地；本地 `*.sqlite` 按既有 `.gitignore` 不进入 Git，不能把 Git/rg 列表未显示误认为未下载。组合源的模型 accuracy 仍待下面独立评测。

独立运行 `accuracy/20261021T073644Z-sql-decode-level3` 已 exit 0，使用同一 073309 SQL+C2 源与[官方 accuracy shell](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/run_math500_level3.sh>)；启动工具见 [launcher](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/launch_accuracy_gate.sh>)、[owned runner](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/run_accuracy_gate.py>)。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/manifest.json>)明确开始 UTC `07:36:44.831755`，base d60、FlagGems `4df52d…`，runner/SQL/C2 三个 hash 与 073309 一致，EvalScope 1.11.1 / SQLAlchemy 2.0.48。完整归档已到本地，**227 个 source 文件的 SHA256 逐项匹配**，其中数据集 test.jsonl 为 `35dc41080a3680858b27fa7e0533d2d547825316fc5dafe5d316f4ccc5a06132`、eval.yaml 为 `3b27aa1c196f11345dd75a1333fa47044605eced79bfa2cd770ccae65fe12621`。

对 [本次 report](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/math500-level3/20261021_153745/reports/minicpm/math_500.json>)、[predictions](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/math500-level3/20261021_153745/predictions/minicpm/math_500_Level 3.jsonl>)、[reviews](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/math500-level3/20261021_153745/reviews/minicpm/math_500_Level 3.jsonl>)运行现成只读 CLI，得到 **valid / pass，101/105 = 0.9619047619047619，超过 0.95 门槛**；report 舍入值为 0.9619。105 个官方 Level 3 question IDs、index 0..104 的预测/评分映射及原配置均完整，105 succeeded / 0 error、105 review status success；104 stop、1 max_tokens（index 101），空 final / 空 extracted answer 均为 0。本次仅证明这份 SQL+C2 组合通过该准确率门，不是新增官方性能分数；没有扩展到 C3/mixed 或整数 fused 的准确率结论。官方原始 score 与 runner result 均未改。

[runner result](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/result.json>)保留 `accuracy_gate=unassessed`，表示 runner 本身不替代结果复核；evaluation exit 0、cleanup_errors 为空，评测 UTC 07:37:39.693764–08:05:12.387305，driver 于 08:05:16.234653 确认 port free / free 32700 MiB。[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/server.log:62>)有 SQL/C2 installed 与 graph capture 时 FIRST_SELECTED，KV 521936。[DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/database-before/manifest.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/database-after/manifest.json>)仍为 479 表 / 17982 行，schema/logical/snapshot hashes 均相同，两个本地 SQLite 实体也逐文件匹配 manifest。[完整 postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3/postflight-full.json>)于 UTC 08:06:29.426225 记录 68 MiB / 0%、9031 关闭且无进程；与 driver 的较早 postflight 分开保留。[control 归档](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T073644Z-sql-decode-level3-control/evidence.tgz>)保留整份原始证据。

## SQL+C3 组合短测：单次增量信号，独立 accuracy 见后文

`20261021T080656Z-sql-mixed-screen` 已 exit 0，在 SQL+C2 上加入原 mixed Attention 补丁，形成 SQL+C3 组合。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/manifest.json>)仍为固定 base d60，runner SHA256 `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`、mixed runtime `a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42`；SQL/C2 runtime hash 保持。[source.sha256](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen-control/source.sha256>)留存组合源身份。[原始 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-160853.json>)为 64 完成 / 0 失败、262144 输入 / 8192 输出 token，耗时 **39.16018311912194 s**、total **6903.338505278714 tok/s**、median ITL **94.86219752579927 ms**。

与 073309 SQL+C2 的 SERVER、packages、seed 721101、4K/128/64/64 load、driver `22a076e…` 均一致，且两次 KV 同为 **521936**。[本次日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/server.log:62>)有 SQL/C2/mixed 三项 installed 与 C2 capture FIRST_SELECTED，但没有真实 mixed 服务命中计数。按两次原始数值，SQL+C3 相对 SQL+C2 吞吐 **+5.091612%**、耗时降低 **4.844927%**，median ITL 从 92.260662 升到 94.862198 ms。**这是一次未确认的增量筛选信号，不是稳定收益、官方分数或 mixed accuracy 通过。** 073644 的 101/105 属于 SQL+C2，不能移用于这个不同组合。

[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/cpu-before-decode-4k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/cpu-after-decode-4k.json>)同为 quota/period 600000/100000，本次新增 615 periods、4 次节流、16.487770594 s 累计 throttled time，不能据此保证外部 host 负载相同。[DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen-control/db-before/manifest.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen-control/db-after/manifest.json>)均为 479 表 / 17982 行；schema/logical/snapshot hashes 与 073309 相同，两个本地 SQLite 实体也已复算匹配。没有清库、换 tuning config 或 profiler。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T080656Z-sql-mixed-screen/postflight.json>)于 UTC 08:10:57.096925 记录 68 MiB、0%、9031 关闭且无进程。该时点 accuracy 待验证，后续 090505 独立通过见下；不把准确率结果混入这次性能计时。

## 只读 accuracy 验收

[review_accuracy_gate.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/review_accuracy_gate.py>)只读显式传入的 EvalScope timestamp 目录，JSON 输出到 stdout、简短结论到 stderr，不修改 report、predictions、reviews 或 config。SHA256 为 `ba22e1a337b8a62c7a385ae31e0a71af148cfd0a1cab8ff3b0f84e9bf36b1010`。检查配置与 Level 3 identity、105 个唯一问题及 index 0..104 的预测/评分映射、成功/错误/不完整统计、二值 score 与 report 舍入值一致性。准确率按整数比较，**至少 100/105 正确**；exit 0 为完整且通过，exit 1 为完整但未达阈值，exit 2 为证据不完整/异常。

实际只读旧 [a8 report](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/remote-evidence/a8-official-candidate/math500-level3/20261021_063351/reports/minicpm/math_500.json>)得到 **101/105 = 0.9619047619047619、pass / exit 0**；旧 [a9 report](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/remote-evidence/a9-final/math500-level3/20261021_071243/reports/minicpm/math_500.json>)得到 **88/105 = 0.8380952380952381、reject / exit 1**。a8/a9 的 `max_tokens` 分别 1/15 次，空 extracted answer 为 0/2；两个旧 run 均 105 succeeded、0 error，说明 exit 0 或请求全成功本身不足以判 accuracy。输出记录四份输入文件 SHA；截断/空答案只统计，不改官方分母或额外要求零截断。该工具不重跑官方答案判分，也不证明服务实际安装与清理，仍需核对本次 manifest、marker 与 postflight。已运行的 4 项本地检查通过，停止扩大 CPU 前置验证，后续直接读取真实 accuracy 结果。

运行方式：`python scripts/review_accuracy_gate.py <本次 math500-level3 下的唯一 timestamp 目录>`。不要传总目录后自动挑最新 report，避免混用历史结果。

## SQL 修复的规则与一手系统经验边界

本次在线访问 [官方赛题](https://flagos.io/race-detail-season2?id=539vlt2p&lang=cn)及 API 未成功，规则核对依据参考仓库保存的 [官方 API 原始响应快照](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/src/SOLECA794/minicpm5-2b-infer-opt-flagos-main/docs/competition/raw/race_539vlt2p.json>)（SHA256 `1f8b333bdc5778372ce993d8d5fd7f2b158d47457602736b944db8fa4f067df1`），不是本次实时重取或主办方最终审核。快照要求固定模型/框架、服务参数与基线一致、benchmark 不调优，禁止仅切已有算子或删主要算子选择逻辑、直接 merge 新框架；技术策略须由提交代码实际启用且可复现。按这些要求判断，SQL 补丁改变的是目标表反射实现，保留算子选择、DB 配置值、调优与模型数值路径，**具有框架层开发的合理合规依据；这是技术解释，不是最终合规认证**。

[SQLAlchemy 2.0.48 automap 源码](https://github.com/sqlalchemy/sqlalchemy/blob/rel_2_0_48/lib/sqlalchemy/ext/automap.py)与 [同版 MetaData 源码](https://github.com/sqlalchemy/sqlalchemy/blob/rel_2_0_48/lib/sqlalchemy/sql/schema.py)支持 `reflection_options` 传递给 reflect、用 callable `only` 过滤存在表；缺表时不应换成会抛错的 `[name]`，默认外键跟随仍保留。此依据与实际 2.0.48 对齐，但不把 FlagGems 配置表契约泛化为任意双向 ORM 图完全等价。提交复现说明须保存这个前提、源 hash、安装 marker 和配置读写等价门。

[vLLM 团队 2024-09-05 性能诊断](https://vllm.ai/blog/2024-09-05-perf-update)指出 host 调度/输入准备能使 GPU 等待；[2025-09-05 系统解析](https://vllm.ai/blog/2025-09-05-anatomy-of-vllm)把输入准备与 graph replay 分成不同阶段。可复用的方法是先定位暴露的 host 工作并减少重复元数据构建；不能移植其硬件、模型、版本的收益数字，也不需要 merge 新版框架。当前 host profile 已提供本机归因，短服务结果提供初步收益，两者应分开报告。

## 正式两档四轮的耗时预算与验收

[原官方 wrapper](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/run_official_benchmark.sh>)固定为 `[4096,1024,64,256]`、`[16384,1024,64,128]`。实际 hash 对应的 [官方 Python 脚本](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/tmp/src/vllm-plugin-FL-main/benchmarks/benchmark_throughput_serve.py>)为 SHA256 `0813eba574e9d1eb50c297c515baa426da1bcb61ce8c78a398b482f246005565`，`RUNS=4 / SKIP_FIRST=1`，每档都实际运行四轮、只用原始第 2–4 轮平均。另一个只读副本仅 CRLF 不同，不能把其不同文件 hash 当成本次实际身份。

本地 [历史原始 CSV](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/20261020T180049Z/raw-runs.csv>)只完整保留 4K 四轮：775.99、700.03、714.07、683.06 s，合计 **2873.15 s（47 分 53 秒）**；末三轮 mean 为 699.053333 s，[历史 summary](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/20261020T180049Z/summary-partial.csv>)舍入为 699.05 s。没有本地已完成 16K 四轮 CSV，不能声称两档历史总耗时已测得，也不能把短筛选约 2.79 倍直接外推为正式耗时缩短比例。

用于排设备时间的公式是 `T ≈ 2873.15 s + 4 × D16K + 进程/数据准备开销`，其中仅前项为历史实测；若 16K 每轮暂按 10 / 15 / 20 分钟，则两档约为 **1 小时 28 分 / 1 小时 48 分 / 2 小时 8 分**，另外留启动与收尾时间。约 1.5–2 小时是临时规划区间，不是候选预计性能；新 SQL+C2/C3 的 16K 短测和正式首轮到齐后再收窄，实际可能更快或更慢。四轮协议保持不变。

官方脚本的 `subprocess.run` 不检查 child returncode，case 异常会 catch 后只打印 `ERROR`，失败 case 也可能 skip summary 后整体 exit 0；raw `SUCCESS` 仅由 successful requests 判断。因此 **exit 0 不能验收完整成绩**。外层只读复核须至少检查：

- 从本次完整 log 的 `Raw CSV` / `Summary CSV` 明确路径取同一 timestamp 文件，保留 source/env/SERVER 与实际命令；不把 wrapper 的“最近 20 个文件”列表当成结果归属。
- raw 恰两档、每档原顺序四行，共 8 行；第 2–4 行均 SUCCESS，successful requests 分别 256 / 128。第一轮不论成功与否只按原位置排除，失败另记，不能先筛成功再移动丢弃位置。
- 保留轮的输入 token 总数分别 **1048576 / 2097152**，输出分别 **262144 / 131072**；duration 与计分吞吐/延迟字段完整、有限且合理，检查完整 log 中 fatal/server-death/解析异常。
- summary 恰两行。按原第 2–4 轮对每个指标做算术 mean、round 2，核对摘要；不使用 `token 总数 / 平均 duration` 替代平均 throughput。CSV 显示值已舍入，派生比率校验须考虑舍入误差。
- 缺 case/缺轮、保留轮失败、`ERROR` / `SKIP SUMMARY ROW` 或关键指标缺失都须显式拒绝完整正式成绩；CSV 不能补证明已被原脚本忽略的 child returncode，完整日志必须保留。

已有 [analyze_benchmark.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/analyze_benchmark.py>)是摘要工具，已最小修复为按 case 原位置先丢首轮再筛可用行，避免 failed warmup 误删第二轮；不足三行明确标 incomplete，CV 不可算时显示 N/A。helper SHA256 `adf1fd59181b4649fd20ff9565faef4d62119121f4ff6c4efeb9872950994c0d`；两项轻量内存核查通过，既有完整 4K CSV 的 JSON 数值与表格数值行 hash 保持不变。它未强制两档八行，仍不代替完整性门。新的 [run_official_gate.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/run_official_gate.py>)已补同 timestamp、固定 token 总量、16 个数值字段 finite/positive，以及按原第 2–4 轮 `round(mean,2)` 对官方 summary 逐项只读核对；没有重写 CSV 或改官方脚本。wrapper SHA256 为 `79119f1548b52e9fc1767ac66754272d046cb4bee8474315e9419606037ac579`。必要离线核查仅复用已完成历史 4K CSV，其 token/finite/均值校验通过且原文件 SHA 不变，没有新增测试框架。

## 16K 代表性短对照

`20261021T083031Z-sql-decode-context16k` 已 exit 0。[原始 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261021-163402.json>)为 **131.73937312606722 s / 4010.8282547721406 total tok/s**，32 完成 / 0 失败，524288 输入 / 4096 输出 token；median ITL 394.592467462644 ms。[load-commands](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/load-commands.json>)为 32 请求、16384 输入 / 128 输出、并发 64、seed 721201，属于诊断负载，未改变官方 SERVER 或 benchmark。

[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/manifest.json>)的 13 项 source hash、SERVER 与 packages 均和 073309 SQL+C2 一致；新 context-screen driver SHA256 为 `b7891958d4dafcc408237d6cb9fc225af4d2b6554ca7d818242ace525ff5b738`。[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/server.log:62>)有 SQL/C2 installed、capture 时 FIRST_SELECTED；KV **521840** token，不把它与 4K 时 521936 的差异忽略。SQL+C2 原协议 accuracy 已于 073644 **101/105 通过**，本短测没有新增 accuracy 或官方性能分数。

[DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k-control/db-before/manifest.json>)为 479 表 / 17982 行，[DB 后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k-control/db-after/manifest.json>)为 481 表 / 18052 行，新增 **2 表 / 70 行**；本地 SQLite 实体 SHA 均匹配各自 manifest，前后内容没有相同声明。这会影响后续顺序对照的配置初态，不能把之后的差值全归为 mixed。[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/cpu-before-context-16k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/cpu-after-context-16k.json>)quota/period 600000/100000，新增 1565 periods、4 次节流、13.903549083 s 累计 throttled time。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083031Z-sql-decode-context16k/postflight.json>)于 UTC 08:34:54.607214 记录 68 MiB、0%、9031 关闭且无进程。

后跑的 `20261021T083455Z-sql-mixed-context16k` 已 exit 0。[原始 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/context-16k/results/context-16k-infqps-concurrency64-minicpm-20261021-163812.json>)为 **120.67024365533143 s / 4378.7431266751655 total tok/s**，32 完成 / 0 失败，524288 输入 / 4096 输出 token，median ITL **348.88003719970584 ms**。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/manifest.json>)为 080656 SQL+C3 源；与前 run 的 SERVER、packages、seed 721201、context driver `b7891958…` 和负载一致。[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/server.log:62>)有三个 installed 与 capture FIRST_SELECTED，但 KV 为 **521936，比前 run 多 96 token**。

按原始值，本 pair 单次吞吐差 **+9.173040%**、耗时降低 **8.402294%**。该差值受两项明确边界约束：除了 KV 不同，后 run [DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k-control/db-before/manifest.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k-control/db-after/manifest.json>)均为 481 表 / 18052 行，三类 hash 全部等于 083031 的 **after**，而不等于它的 before；后跑任务已使用前者扩展过的配置初态。本地实体 SHA 已逐个匹配 manifest。**只保留有 DB/KV 混杂的单次筛选信号，不把 9.17% 全归为 mixed、也不外推官方得分。** 该阶段 accuracy 待验证；后续 090505 的同源 SQL+C3 已独立以 103/105 通过。

[C3 CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/cpu-before-context-16k.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/cpu-after-context-16k.json>)新增 1453 periods、5 次节流、18.809646986 s 累计 throttled time；不据此保证 host 负载相同。[C3 postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T083455Z-sql-mixed-context16k/postflight.json>)于 UTC 08:42:11.420636 记录 68 MiB、0%、9031 关闭且无进程。

`20261021T084659Z-sql-decode-context16k-long` 已 exit 0，仍用 073309 SQL+C2 原源。[JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-165213.json>)为 **236.02503280621022 s / 2360.156435005664 total tok/s**，32 完成 / 0 失败，524288 输入 / **32768 输出** token，median ITL **92.2509403899312 ms**。[负载命令](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/load-commands.json>)为 16384 输入 / 1024 输出、32 请求、并发 64、seed 721201；[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/manifest.json>)源与 SQL/C2 hash 保持，新诊断 driver SHA256 为 `28d6a03419c4f8bf3b4b50b79edc63343afd601912ef0fc9775957b1dba113b7`，官方 SERVER 不变、无 profiler。

[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/server.log:86>)的 KV 为 **521936**，未见 preempt 关键日志，但这不等同精确抢占计数为 0。[DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long-control/db-before/manifest.json>)为 481 表 / 18052 行，[后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long-control/db-after/manifest.json>)为 483 表 / 18119 行，**又新增 2 表 / 67 行**；本地实体分别匹配 snapshot SHA `a269d355…` / `a996189f…`。因此后跑 mixed 若承接 after，仍须把配置变暖与候选差异分开，按实际需要只补一次已暖 SQL+C2 控制，避免扩成无必要的重复。此处尚不确定后跑任务 DB 状态。

[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/cpu-before-context-16k-long.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/cpu-after-context-16k-long.json>)新增 2609 periods、4 次节流、19.990656130 s 累计 throttled time。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T084659Z-sql-decode-context16k-long/postflight.json>)于 UTC 08:53:02.500657 记录 68 MiB、0%、9031 关闭且无进程。这仍是 32 请求长输出筛选，不是官方 128 请求四轮结果。

`20261021T085302Z-sql-mixed-context16k-long` 已 exit 0，源为原 080656 SQL+C3，同 driver、seed、shape。[原始 JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-165759.json>)为 **220.3681204696186 s / 2527.8429512076336 total tok/s**，32 完成 / 0 失败、524288 输入 / 32768 输出 token，median ITL **92.2634385060519 ms**。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/manifest.json>)保持 SQL+C3 源与共同 SERVER/packages；[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/server.log:87>)的 KV 为 **521840，比前 SQL+C2 长测少 96**，与 128 输出那组的容量差方向相反。

[C3 DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long-control/db-before/manifest.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long-control/db-after/manifest.json>)均为 483 表 / 18119 行，schema/logical/snapshot 三类 hash 都等于 084659 **after**，没有再扩展；本地实体也匹配 manifest。因此两长测原始差值 **+7.104890% 吞吐 / −6.633581% 耗时**仍受 DB 初态与 KV 差异约束，median ITL 则几乎相同，不作稳定或归因收益声明；该阶段 accuracy 待验证；后续 090505 的同源 SQL+C3 已独立以 103/105 通过。[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/cpu-before-context-16k-long.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/cpu-after-context-16k-long.json>)新增 2443 periods、5 次节流、19.853238032 s 累计 throttled time。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085302Z-sql-mixed-context16k-long/postflight.json>)于 UTC 08:58:55.088723 记录 68 MiB、0%、9031 关闭且无进程。

已暖配置控制 `20261021T085855Z-sql-decode-repeat-context16k-long` 已 exit 0，源为原 073309 SQL+C2，同 driver `28d6a034…`、seed 721201、16K/1024/32 请求/并发 64。[JSON](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261021-170404.json>)为 **231.32209699694067 s / 2408.140023075129 total tok/s**，32 完成 / 0 失败，524288 输入 / 32768 输出 token，median ITL **92.23801782354712 ms**。[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/manifest.json>)保持原 source、SERVER 与 packages；[日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/server.log:86>)的 **KV 521840，现与 mixed 同容量**。

[warm DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long-control/db-before/manifest.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long-control/db-after/manifest.json>)均为 483 表 / 18119 行，schema/logical/snapshot hash 与 mixed 的 before/after 全部相同，本地实体 SHA 也已匹配。这个必要控制消除了此前已知的 DB/KV 初态差异。mixed 相对 warm SQL+C2 的单次吞吐差仍为 **+4.970763%**、耗时降低 **4.735378%**；两者 median ITL 几乎相同。它保留为更可信的单次增量筛选信号，尚不是重复稳定因果、官方性能成绩或 mixed accuracy 通过。

[metrics 一次观测](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/metrics-observed.prom>)与[观测时刻](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/metrics-observed-utc.txt>)记录 UTC **09:03:34.629064**、服务 `vllm:num_preemptions_total=1.0`，说明该时点已有累计抢占；它不是最终完整计数，也不能把计数范围限定为本次 benchmark 或据此推断 mixed 为 0。[CPU 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/cpu-before-context-16k-long.json>) / [后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/cpu-after-context-16k-long.json>)新增 2568 periods、4 次节流、14.794389534 s 累计 throttled time，不据此保证 host 条件相同。[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T085855Z-sql-decode-repeat-context16k-long/postflight.json>)于 UTC 09:05:05.260646 记录 68 MiB、0%、9031 关闭且无进程。

## SQL+C3 独立 accuracy 通过，官方吞吐运行中

`accuracy/20261021T090505Z-sql-mixed-level3` 已 exit 0。本地直接对[原 report](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/math500-level3/20261021_170606/reports/minicpm/math_500.json>)、[predictions](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/math500-level3/20261021_170606/predictions/minicpm/math_500_Level 3.jsonl>)、[reviews](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/math500-level3/20261021_170606/reviews/minicpm/math_500_Level 3.jsonl>)及[task config](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/math500-level3/20261021_170606/configs/task_config.yaml>)运行现成只读 reviewer，独立得到 **valid / pass，103/105 = 0.9809523809523809**，超过 0.95 门槛，report 舍入值 0.981。105 个官方 Level 3 question IDs、index 0..104 和原配置完整；105 success / 0 error、105 stop / 0 max_tokens，空 final / 空 extracted / 缺 usage 均为 0。没有修改原 score 或以 root 派生摘要替代复核；本地结果与归档 [accuracy-review](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/accuracy-review.json>)一致。

[manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/manifest.json>)为固定 d60 base、原 080656 SQL+C3 源。**228 个 source 归档 SHA256 逐文件匹配**；runner、SQL runtime、C2 runtime、mixed runtime 四核心的实际 hash 各自与 080656 相同。EvalScope 1.11.1 / SQLAlchemy 2.0.48、官方服务与采样参数保持；[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/server.log:62>)含三个 installed 与 capture FIRST_SELECTED，KV **521840**。本次通过属于 SQL+C3 组合；SQL+C2 的 101/105 独立通过记录保持，不据此宣称准确率统计上提升。

[result](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/result.json>)记录评测 UTC **09:06:00.651727–09:22:12.738286**，runner **09:22:16.581155** 退出，cleanup_errors 为空；其中原 `accuracy_gate=unassessed` 保持，最终通过来自只读 reviewer。[完整 postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/postflight-full.json>)于 UTC **09:29:01.800600** 记录 68 MiB、0%、9031 关闭且无进程。[DB 前](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/database-before/manifest.json>)为 483 表 / 18119 行，[后](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/accuracy/20261021T090505Z-sql-mixed-level3/database-after/manifest.json>)为 489 表 / 18384 行，新增 **6 表 / 265 行**，本地 SQLite 实体均匹配各自 snapshot hash；不声称前后配置库相同，不从这次准确率耗时推性能。

device owner 当前唯一 GPU 任务是 `official/20261021T092944Z-sql-mixed-official`，runner PID **141987**，原 080656 SQL+C3 源、official driver `79119f…`、launcher `a4fac…`，原两档四轮协议。owner 于 UTC **09:31:35** 从远端 log 确认 `RUNS=4 / SKIP_FIRST=1 / TOTAL_CASES=2`，当前为 **4K 第 1/4**；benchmark PID 142458、APIServer 142001、EngineCore 142169。这里只记录启动与进度回执，**尚无完成吞吐结果或官方增益**，本地初始 manifest 尚待归档。原 13eb baseline 已隔离到 `official-base-20261021T091033Z` 源目录，只能待当前任务结束并清理后串行启动。

## 官方增益的最小对照安排

若只报告候选本身两档官方吞吐，一次原四轮协议可以给出绝对结果；要声称本机加速比，则还需要同一 reviewed runner 的完整 baseline。现有 [历史 baseline manifest](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/20261020T180049Z/manifest.yaml>)为原 plugin `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，当前保留 B0 已为 d60，且历史只完整保留 4K，不能替代新两档 matched 增益对照。

本轮已选定最小安排为 **最终 candidate vs 原 13eb，各一次两档四轮，报告整体优化增益**，不另加 d60 的正式增量 baseline。两者保持同 SERVER、物理32GiB、pinned框架/package、runner/benchmark SHA、无profiler；源码身份明确区分提交优化与原始实现，其中installed Attention候选54c、原baseline必须bab2（后文已独立恢复审计），其他依赖须逐项核对。分别留存原CSV、源码与DB before/after；不清库或改参数。实际KV容量仍须列出；首轮按原协议丢弃，不先过滤失败再移动位置。若配置初态扩展明显影响比较，再按实际需要只复核受影响一侧。SQL+C3现已自身103/105通过，不复用SQL+C2的101/105；新候选仍需自身accuracy。

## 下一步

SQL+C2 与 SQL+C3 的独立原协议 accuracy 已分别通过 101/105、103/105。必要的已暖 SQL+C2 控制消除了已知 DB/KV 初态差异，长输出保留约 4.97% 单次吞吐信号。当前 SQL+C3 原两档四轮官方吞吐运行中；完成并清理后，再串行跑原 13eb baseline 两档四轮以评估整体增益，不把未完成进度或旧单档历史当最终分数。保留 DB/schema 和启动条件的复现边界，不继续扩大 CPU 前置准备。整数 fused 候选保留、非默认；[hidden-view 方案](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-hidden-view-plan.md>)维持低优先未验证草案。官方参数与 benchmark 保持原样。


## 官方两档运行中：4K 原四轮已经完成（live1004Z）

root 提供的 [live1004Z 原始快照](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/>)包含 raw、summary、manifest；本记录 owner 仅 CPU 独立复算，没有额外设备负载。四个原始 4K 行均 SUCCESS，各256请求、1048576输入/262144输出 token；时长依次372.63、361.08、356.17、350.38秒。按原协议丢弃第1轮，原第2–4轮 Total tok/s 为3630.04、3680.04、3740.87，summary **3683.65 total tok/s、736.73 output tok/s、355.88秒**。Mean TTFT **4781.64ms**、Mean TPOT **81.79ms**；所有 numeric summary 列均与原第2–4轮均值舍入两位一致，详见 [独立局部审计](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/live-20261021T1004Z/independent-partial-4k-review.json>)。原 CSV 未改写。

manifest 记录真实启动 UTC09:29:44.531166、source080656、plugin base d60b023、FlagGems4df52d9、原 SERVER/benchmark argv、无profiler/无smoke、RUNS4/SKIP_FIRST1。root 当前回执为16K第1/4轮，live快照没有16K结果，故**这只是完整4K case的绝对结果；整个官方任务仍运行，尚无两档整体完成或 matched 加速比**。还需保存8raw/2summary、exit/result、DB-after和真实清理；原13eb baseline继续等待独占任务结束。


## 10:17:06Z owner回执与独立growth准入候选

root回执正式任务已进入16K第2/4轮，首轮128成功/0失败、816.56s/2728.78total tok/s；一次metrics服务累计preemptions6、KV97.6885%、waiting34，远端保存在本run的`observations/20261021T101706Z`。本记录owner尚未拿该observations实体做独立复核，故这里只记录明确owner回执，**它不是最终/分档完整抢占计数，也不是完整官方结果**。当前任务继续，不开第二GPU。

root授权最小CPU候选后，新增 [growth admission实现](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/patches/framework/biv150_growth_admission.py>)，默认关闭、未集成冻结source。已核实际五份scheduler/KV源hash，包装只在waiting准入增加真实future-output/free-page预算；复用actual predictor计已有页/共享prefix/ref0触碰且禁admission cap，无持久ledger，empty/超长/非审计状态回原。六个必要CPU合同通过；详细 [设计/风险/安装进程与下一步](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-growth-admission-implementation.md>)。准入保守可能使31降29驻留而伤TTFT/吞吐，必须短测；没有设备、accuracy或性能收益结论。根owner交叉审查后才可隔离新source串行上卡。


## 正式两档已完成：独立审计通过（092944）

本地完整run/control已归档；本记录owner独立读取原CSV、source、DB实体和postflight，未使用root派生review代替复核，也未改原CSV。结果保存在 [独立完整审计](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/independent-official-review.json>)；本节覆盖之前该run的running历史状态。

| 原官方case | 每轮成功请求 | 丢原首轮后的total tok/s | output tok/s | duration s | mean TTFT ms | mean TPOT ms | retained total-throughput sample CV |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4096/1024/c64/256 | 256/256，四轮均成功 | **3683.65** | 736.73 | **355.88** | 4781.64 | 81.79 | 1.506742% |
| 16384/1024/c64/128 | 128/128，四轮均成功 | **2729.07** | 160.53 | **816.48** | 185063.65 | 166.71 | 0.023917% |

[原raw CSV](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/raw_runs_20261021_173039.csv>)准确8行且4K/16K次序各4行；每行SUCCESS，4K各1048576输入/262144输出、16K各2097152输入/131072输出token，numeric皆有限正数。[原summary](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/summary_20261021_173039.csv>)准确2行，每个numeric列均复算匹配原第2–4轮均值舍入两位；不是先过滤后移动首轮。raw SHA55d66218…、summary SHAe913ef2e…匹配run验证。4K三轮仍有单调变快，不能仅因原四轮完成称完全无漂移稳态；16K三轮非常接近。

**230个source归档SHA逐项匹配**，其中原benchmark0813eba…保持RUNS4/SKIP_FIRST1；SERVER与benchmark argv逐项核对同原命令，profiler=false、smoke=0。runner e155a166、SQLad84、C2e5f68、mixeda129四核心与已过103/105的090505归档逐byte同源；plugin base d60b023、FlagGems4df52d9。实际[服务日志](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/server.log:84>) **KV521936tokens**，不能误抄先前warm短测或accuracy的521840。安装marker来自EngineCore142169。

DB前后实体均只读重算，snapshot/schema/logical均匹配各manifest，但本次前后不相等：**489表18384行→501表18789行（+12表405行）**。物理SHA `dc6a07db6d31ab210aede0ae92dce0378440729e7c91a0183c269111b3c0ad5e`→`e90b666d97547ef35ebc5e2a01d24d56a5d16a38d49fcb3908ddb7fc62cad342`；逻辑SHA `ee28e6f306cd5af77c4dc00ad78693cf2f57c20ee118e1d64ff98a2717f8382b`→`3fb6abadfdcdb78f8b2eb2f90c950aca80bb61fd2703856b5a81740375b80fa9`。完整schema指纹和字节数见独立review。此为真实cache状态变化，不抹平或预设原13eb将与它相同。

[result](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/result.json>)与exit-code为0，benchmark UTC **09:30:39.405817→10:53:36.070467**（上海17:30:39→18:53:36），cleanup_errors为空。完整[postflight](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/official/20261021T092944Z-sql-mixed-official/postflight-full.json>)于UTC **10:55:26.276614**记录68MiB/0%、9031closed且无进程。结论是候选两档绝对官方吞吐结果通过完整证据门；**原13eb matched整体增益/官方分数尚未计算**，不拿旧单档或d60短测替代对照。

root在封存该run并确认实际设备释放后，启动当前唯一GPU `framework/20261021T105526Z-mixed-bucket-row-kv-gate`，controller151230。本记录只登记明确owner回执，尚无本地该gate的manifest/result供独立审计，故仍running、不预判正确性或收益。后继原13eb baseline与其他候选按root单卡队列串行。


## 后继真实gate的归档错误与最小修复（owner回执）

root报告`20261021T105526Z-mixed-bucket-row-kv-gate` exit1、cases=[]：归档hash误把`__pycache__`目录当文件而发生IsADirectoryError，未执行候选case，**不归类为bucket/row-gather正确性失败**。raw已封存远端control/evidence.tgz，root下载中；本记录尚未拿到本地完整实体独立审，明确属于owner回执。root仅过滤regular-file，确认68MiB/0%/9031closed后重跑当前唯一GPU **`20261021T105930Z-mixed-bucket-row-kv-gate`、controller151669**，尚无结果。

另一次候选源码打包预检遇合法仓库内部JSON symlink，root改为仅解引用解析后仍在源root内的regular-file并记录metadata，避免拒绝合法内部引用或读取外部目标。三个隔离源`code/{bucket,growth,hidden-gather}-20261021T105930Z`已准备，没有默认集成或新的服务/accuracy结论。此为流程修正，不改候选计算、原benchmark或冻结080656源码；不因此新增重复测试。


## Token-bucket行/KV最短门已过，继续独立策略基点

105526/105930完整本地raw现已独立审完。[失败review](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T105526Z-mixed-bucket-row-kv-gate/independent-gate-review.json>)核8个已记录源SHA、exit1/cases[]及实际__pycache__归档错误；两次gate脚本diff仅两个hash comprehension增加`if p.is_file()`，无候选计算修改。

[成功review](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/framework/20261021T105930Z-mixed-bucket-row-kv-gate/independent-gate-review.json>)核13源SHA与两个原始case：**M259→384、M952→1024，32请求/31decode-prefix**。两者有效Attention及整KV bitwise/maxdiff0，复用同cache的下一32token decode亦逐位相同；尾output毒值保持、输入ID/positions padding清零、padding操作不消耗RNG及下步未用output不变均通过。真实Builder/Impl/KV writer使用已审C2+C3；bucket padding在CUDA Harness上调用实际`_wrap_runner`。exit0，10:59:45.512516Z完成；postflight11:01:49.406136Z为68MiB/0%/9031closed。

**证据边界明确：** 未创建ModelRunnerFL或模型权重，未验证其完整H2D/event生命周期或backbone GEMM、hidden/logits/LM-head、真实sampler；只核padding操作的RNG，而非采样RNG。`row`指bucket padding行隔离，**没有导入/测试hidden-row gather候选**；先前标题容易混淆处已在queue/registry纠正。此门不等于整模型正确性、accuracy或性能通过，不为hidden-gather背书。

root确认gate清理后，当前唯一GPU转为`framework/20261021T110149Z-sql-mixed-innovation-base-context16k-long`、runner151990，原080656 C3源、16K/1024/32请求/c64/seed721201。新driver bc51ac2d…保存测前后原metrics与scheduler源SHA，准备growth策略的匹配对照；本记录尚无其本地manifest/result，登记running无结果。不得拿与旧driver的差值直接归因新策略；当前不新增CPU测试或重复大验证。


## 新driver匹配控制、growth未启用与hidden-copy门

110149/110747本地各存独立screen-review：声明的21/22源SHA、同bc51ac2d driver、真实32成功/0失败和524288输入/32768输出均核实。原C3基点 **220.494323s/2526.396110total tok/s**，growth **220.369000s/2527.832862total tok/s**；四份DB实体全部501表18789行且schema/logical/physical相同，但KV **521840→521936，相差96**。测前后原metrics两run均preemptions0→1。growth EngineCore有INSTALLED，完整日志无FIRST_CHECKED/DEFERRED，结论 **not activated / inconclusive，不报微小收益**。清理分别11:07:46.868216Z、11:18:03.698898Z为68MiB0%closed。

没有证据准确点名失败guard，不放宽scope。独立[一次诊断模块与方案](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-growth-admission-diagnostic.md>)已完成并由framework owner审：新隔离source的base constructor返回后，只读原29项可信AST guard与实际描述符，准确记录每个false/异常；constructor全部true才补首个非空running waiting allocation的一条kwargs/stats。原runtime和在途source不变，只诊断不入性能。

111804 hidden-row gate已独立核 **8源SHA**；四形状259/952/2048/64（62真实token）BF16完整bits、shape、fresh storage和RNG均过；int32动态shape共1cache entry，int64另过，8个fallback、private重复/反序copy及跨stream过。**这是fixture配置的copy门，没有构造完整ModelRunner或权重/LM-head/sampler，不是accuracy/性能成绩**；详情见同run的independent-gate-review.json。11:20:21.548652Z fullpost68MiB0%closed。root后继唯一GPU为112021 hidden-gather16Klong、runner155377、hidden-gather105930源，同bc51/shape/seed；本记录只有running回执，等待实际结果。


## 实际V2原因已定位，独立修订通过跨owner审查

112603 constructor-only smoke本地独立核23声明源SHA、真实EngineCore JSON、DB实体和postflight。29项guard唯一false是 `not scheduler.use_v2_model_runner`，实际builtin AsyncScheduler的V2=True；其余28项true、setup_errors为空。这解释110747的INSTALLED-only；不重复猜reserve/default字段，不把未启用时间归因策略。本smoke实际seed721001，非long负载，无性能意义。详细原件及独立结果见该run的`independent-diagnostic-review.json`。

独立 [growth-v2审计与实现](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-growth-admission-v2.md>)只接受exact内置Scheduler/AsyncScheduler，新增actual async第6源SHA、继承及3原method身份、defer_block_free=False守卫，允许bool V2；预算、allocate、FCFS与kwargs保持旧实现。actual V2 payload重组发生在分配之后，实际Base/Async computed/placeholder/PP1 cadence用1必要合同直接抽取原源码验证。framework owner独立终审72d6/e5ba无阻断，只复跑该1合同0.017s通过。旧9245和105930不改，新hook仅接受e043原080656 init，输出830ff580…，默认off、独立source显式启用。不改变参数或关闭V2。

后继真实负载必须看到EngineCore FIRST_CHECKED和FIRST_DEFERRED，不能以INSTALLED代替策略运行；这些marker应在负载开始后验收。新revision没有accuracy或性能结果，不继承旧C3门槛。root已准备`code/growth-v2-20261021T114249Z`，未执行；必须接新506表DB basis的匹配基点。

## Hidden保留，bucket必要warm复核与overlap摊销门

下列本地审计全部直接读原JSON/log、逐源hash、只读SQLite实体和fullpostflight，独立review JSON分别落run目录，没有SSH/GPU操作。

| run | 实际结果 | 证据与解释 |
|---|---|---|
| 112021 hidden | 220.357327429s、2527.966764total、32/0 | 22源SHA，真实FIRST_SELECTED；KV521936，DB501表18789行三hash不变，preempt0→1。相对110149约0.06%且KV多96，不报归因收益；保留候选。 |
| 113208 bucket冷轮 | 231.619268445s、2405.050339total、32/0 | 22源SHA，FIRST_SELECTED1696→1792；KV521936/preempt0→1。DB501/18789→506/18926，新增5表137行，不能判候选回退。 |
| 113946 bucket必要warm | 220.390441753s、2527.586930total、32/0 | 22源SHA，真实FIRST_SELECTED；KV521936/preempt0→1。DB506/18926三hash前后相同。时间恢复，旧110149却DB501/KV521840不同；不报性能收益，保留。 |
| 113727 overlap首门 | 1层真实backend输出/KV/RNG/different-Q join/fallback全过 | 14源SHA，4calls/窗口ABBA，wall中位12.883671→12.561840ms约省2.498%；event中位12.421241→12.517388ms反慢，pending峰4/清理0。仅短窗口信号。 |
| 114553 overlap摊销 | 64calls/窗口ABBA，methodv2将Event构造放wall起点外 | 14源SHA，相同正确性全true，pending峰9/清理0；wall12.460649→12.417108ms省0.349429%，event12.409186→12.414136ms基本持平略慢。不支持hardware并发或E2E收益，不服务集成，保留小prototype。 |

bucket after/warm三hash：physical `5f35abdd89aa0f1d0f541b4d4e97568787962a359d02a3d48ef4a8defecdf8f6`，schema `f4e745cc502d0896d0a92ae3f10472ecffd94615e4879d4ccdcc1a74cef40028`，logical `2750d813c18c2b37c61c821f57528044ef7a39dcafa32a516a5badf897fc4294`。这是新增basis，不能以旧501表快照作相同环境声明。所有screen同bc51driver/16K/1024/32请求/c64/seed721201；overlap均fixture单层，不含模型权重/服务/accuracy。

完整postflight依次11:26:02.786329Z、11:32:08.170110Z、11:37:27.415623Z、11:39:46.229205Z、11:45:52.843157Z、11:47:13.030618Z，均68MiB/0%/9031closed。root随后启动当前唯一GPU **114713-growth-v2-matched-base-context16k-long，runner161064**，原080656/newbc51/同long shape+seed/DB506，准备growth-v2匹配基点；本记录只有running回执，没有完成结果。queue/registry已同步，69数据行各16列完整。原13eb matched官方增益仍未计算。

## DB506匹配基点完成，V2真实CHECKED但延后准入待验

114713完整本地原件已独立核21声明源SHA、bc51driver、原SERVER/seed721201、16K/1024/32请求/c64；原结果 **220.24970296164975s /2529.202048898997total tok/s**，32完成/0失败、524288输入/32768输出，meanTTFT **62440.319728528266ms**。KV **521840**，metrics preempt0→1。DB before/after实体只读重算均506表18926行，schema/logical/physical三hash相同且等于113946 after；没有新表扩展。11:52:46.493627Z完整清理68MiB/0%/9031closed。该run的`independent-screen-review.json`已落盘，是新V2的真实基点，不能省略后继KV容量差。

root清理后当前唯一GPU是 **115247-growth-v2-innovation-context16k-long runner162380**，新sourcegrowth-v2-114249/runtime72d6/init830ff58，同bc51/shape/seed。root已从真实远端log确认EngineCore162561 `FIRST_CHECKED free=31595 future=1151`，实际KV521936；11:54:11Z为2running/30waiting。这里明确是device owner回执，**本记录尚无该run本地完整原件；尚未见FIRST_DEFERRED或完整结果，不提前归因收益/accuracy**。不再做V1/fake诊断，等待本轮真实延后准入、总耗时/TTFT/preempt/tokens/DB/源及清理证据。ownedregistry70行各16列，queue46同步。

## V2已真实延后准入，首轮调优库扩展待warm

115247完整本地原件现已独立审22源SHA、bc51/shape/seed/原SERVER和DB实体。真实EngineCore162561 CHECKED free31595/future1151，随后DEFERRED free2702/future2722。原结果 **238.11336583085358s/2339.4570819502455total tok/s**，32/0、524288/32768tokens、meanTTFT68405.78491348424ms；KV521936、preempt0→0，对照114713的0→1。策略确已启用并延后准入，不再是INSTALLED-only。

DB before等于114713after，但本轮 **506表18926行→512表19130行，新增6表204行**，三hash变化。after physical `29fb47cbfdaa445875e8962dc1bc3f6eb36bffaee7006c2472d59947c5179074`、schema `2d7d232ee4918b7ed4d854d009c8906aa229dd0460ba6534254ae00a520461bf`、logical `4c78431bbd93eb584672f3d57d3aa0e24f622cdab0203d587ea61db1323bc458`；本地实体全复算匹配。较慢首轮受新增形状编译/调优初态约束，不能直接判策略最终回退。只补一次必要warm：最后明确root唯一GPU回执为 **115950-growth-v2-warm-repeat-context16k-long runner163945**，同V2/bc51/long shape+seed；暂无本地完整结果。不新增诊断或CPU合同。

115247 fullpost11:59:21.132870Z68MiB/0%/9031closed已核；独立review JSON已落run。queue47、registry71行各16列更新，等待warm原件。没有新accuracy或官方gain结论。

## 原13eb baseline必须恢复installed原字节：提前发现并纠正

root发现retained a0c `_patch_generic_attention`直接写installed Attention。本记录独立读完整runtime及平台调用点、抽取可信literal做反变换：54c41796字节仅撤 `_LAUNCH_TUNED`/`_DECODE_TILE_TUNED`及exact末marker，得到 **bab2 41176字节**，与a4早先独立保存`.orig`逐byte完全相同。原回执41166为长度转录差，已按实际纠正。详见 [独立身份审计](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-original-baseline-dependency-review.json>)。

runtime唯一显式site-packages源写入是line120的Attention，另line123删除parent整个`__pycache__`；top-p只进程内重绑，没有第二个持久源码写入。`iluvatar.py` module-level line258调用该runtime，不限GPU runner，所以任何retained平台导入都可能写回。d60/SQL/C2/C3已有pair本来共享54c，此发现不新增它们的污染；DB/KV/单轮等原边界仍需保留。092944候选绝对官方结果有效。**091033原13eb source尚未运行**，现提前纠正前置，没有把受污染的“原baseline”拿来计算整体收益。

必要恢复方案及完整未来命令已写 [original-baseline plan](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/analysis/2026-10-21-original-baseline-dependency-plan.md>)。新stdlib helper8b3337默认inspect仅读字节/AST，已本地通过与pycompile；framework owner独立全文终审无阻断，**--apply未执行，无SSH/依赖mutation**。后继只有GPU完全空闲、shared flock+9031+ixsmi单卡<=68MiB0%且无进程、备份先核后才精确原子54c→bab2；不动SQLite/Tritoncache/pycache，不撤当前source。恢复helper释放锁后official driver再取得同一锁；原13eb全树/无retained及archive/启动后/封存后installed bab2必须验收，不能单凭base-revision.txt或插件隔离。未来candidate按原a0c逻辑写回54c后也须核真实身份。尚无原13eb完整matched官方增益。

## Warm终审关闭growth服务集成，保留省mask单层小信号

115950 warm完整本地原件独立核22源SHA、bc51/原SERVER/shape/seed及SQLite实体。EngineCore164138 CHECKED+DEFERRED2696free/2722future，**221.23383624106646s/2517.95118443368total tok/s**，32/0、524288/32768tokens，meanTTFT **67130.2737761871ms**，KV521840/preempt0→0。DB前后512表19130行三hash完全相同且等于115247after，fullpost12:18:37.889080Z68MiB/0%/9031closed。对114713同KV基点的描述差为吞吐−0.4448385%、TTFT+7.5110987%，但DB506→512依然限制因果比较。没有正吞吐信号，按root决策不集成、不大accuracy、不继续补轮；代码defaultoff和negative保留。详见该run的independent-screen-review.json，不再写warm等待。

121838 actual2D full-visible-prefix省mask门已独立核 **15源SHA**，policy87c6/gated3db/candidatea6d3。同原tile/math，两case为C3-P2019/KV16K与Q2048/KV16K；实际backend/builder/KVwriter、随机物理页、Pcase复用16旧prefix block、3个−1 slot且Q/K/V padding带NaN。输出bits/finite/padding、整KV、RNG、一次prefill命中/C2decode回退皆true；原proxy最终恢复，selected68/fallback67。只P2019计时、Q2048仅correctness；不是权重/ModelRunner、graph replay、服务或accuracy门。

原32calls/窗口ABBA复算wall中位 **12.594359734375→12.559617125ms，省0.27585848%**；event **12.491010189056396→12.434306144714355ms，省0.45395884%**。两种计时方向一致但差值小，只保留单层机会，不报E2E收益或在baseline期间集成。internal gate12:19:02Z退出0，后续完整postflight12:25:01.258460Z68/0/closed；independent-gate-review.json落该run。

## 依赖恢复已实际执行并独立审通过，原13eb官方baseline运行中

root在12:26:07Z实际执行helper8b3337，record完整镜像及 [独立恢复审计](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/experiments/dependency-restores/20261021T122607Z-original-baseline/independent-restore-review.json>)已核：status=restored/mode=apply/真实argv；before54c41796B、original-reference bab241176B、runtimea0c与helper8b33四份SHA均正确，三个备份字节核实，独立AST反变换仍逐byte等于a4早先原件。双idle检查12:26:07.432605/07.533529Z及post07.632596Z都68MiB/0%/9031closed/无进程，manifest installed readback=bab2。原mode/root:root与所有源/命令留档，不再是未执行方案。

本文作者没有SSH、改live源或导入retained；actual installed启动后身份另由root于12:29Z只读核 **live与official manifest均bab2**。当前唯一GPU **official/20261021T122607Z-original-baseline runner166637**，source091033原13eb、原791driver/a4falauncher/benchmark两case各4轮/第三marker显式空串；benchmark167244/server166651，原脚本4K1/4，无BIVmarkers。这里是启动后真实owner回执，完整source数量与逐项SHA还待root核实，**没有完成吞吐结果或原13eb整体增益**。

原baseline期间严禁任何retained/C3 import、SSH/GPU或重跑restore，以免写回54c；后续等待原CSV/source/DB/最终bab2/清理再审，不把启动命令当完整成绩。plan、CPU身份JSON、handoff顶端与queue/registry均改实际状态；registry现73数据行各16列，queue49。之前未执行/等待段仅为按时间保留的历史。

## 原13eb完整结束，最终分档比较独立终审通过

2026-10-22（Asia/Shanghai）本地取回原版122607完整run/control后，仅用现有e9dc比较入口和stdlib读字节审计。比较执行exit0，原样输出保存于`analysis/2026-10-21-official-final-comparison.json`，SHA256为`52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832`；独立补充审计见该run的`independent-final-review.json`。没有远端命令、框架导入或新设备测试。

双方均为原官方两档、各四轮、每档只丢原首轮，8raw/2summary全部SUCCESS且请求数、输入/输出tokens及原均值核对通过。下表按原CSV第2–4轮计算，保留更多位数只是避免先舍入summary再求比率：

| 负载 | 原版total tok/s | SQL+C3 total tok/s | 候选/原版 | 吞吐变化 | 原版mean TTFT ms | 候选mean TTFT ms | TTFT变化 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 4K，4096/1024/c64/256请求 | 1905.460000 | 3683.650000 | 1.933207729 | +93.32077294% | 12310.556667 | 4781.643333 | −61.15818754% |
| 16K，16384/1024/c64/128请求 | 861.986667 | 2729.073333 | 3.166027317 | +216.60273167% | 636429.440000 | 185063.653333 | −70.92157564% |

原版summary对应4K1905.46total/381.09output tok/s、687.94s，16K861.99total/50.70output tok/s、2584.99s。原第2–4轮吞吐样本CV为4K1.12956568%、16K0.02406589%；候选分别1.50674249%、0.02391699%。这是本次完整run内的分档观测，不替代独立重复或稳定性归因。

原版225项archive逐byte SHA及封存捕获的live225项都匹配manifest，source-review与process-review引用的actual文件hash一致；Attention archive/live/postcopy均bab2，worker446f，插件原13eb无retained模块/挂钩/marker，服务日志无BIV150执行标记。候选230项archive、54c/e155及SQL+C3核心身份也通过。双方原CLI、模型config、benchmark0813、driver791、包版本、BI-V15032768MiB一致；CPU before/after均quota600000/period100000即6核。原版benchmark真实12:28:47.784861至16:14:45.731362Z，driver16:14:50.001906Z完成，finished-at与result一致，原CSV hash与原driver记录相符。

限制保留：真实KV来自各自server.log，原版521840、候选521936（+96tokens）。SQLite快照实体物理/schema/logical指纹分别复算匹配；原版512表19130行→516表19270行，候选489表18384行→501表18789行，**初始DB不同，不是cache-matched对照**。以上仅分档完整官方流程的描述比率，不声称已分离各优化贡献，不合成未知官方总分，也不代表C500或团队整体成绩。

退出与警告：原driver exit0/benchmark0/server0、cleanup_errors=[]，monitor正常停止为−15；16:17:27.184712Z完整postflight为68MiB/0%、9031 IPv4/IPv6均关闭、ixsmi无设备进程，server/benchmark/EngineCore均不在proc。runner166637仍有proc条目，但独立实际status为Z（zombie）、PPid1，表示已退出而容器PID1未回收；首次seal仅末尾“proc必须不存在”断言失败，原记录和补充`postflight-process-review.json`均保存，没有改写原结果。双方server.log结束时均有同一条“force killing remaining processes count=1”警告；原版无ERROR或Traceback，不能将此写成“没有任何警告”，也不将该警告改标官方benchmark失败。

本次仅更新registry已有122607/092944行，仍73数据行×16列，queue仍49项；所有未开始性能探索继续冻结。

## 用户继续探索后的最短门：覆盖缺口、CTA拒绝及CPUmetadata

上述“冻结”是16:40Z前的历史状态。用户随后明确继续以硬件和输入特点探索框架、调度/KV，小收益也上卡保留，不设最低百分比；root单卡串行，稳定官方原件不覆盖。

173003 C3计数诊断已独立核plugin完整411项SHA、e155精确append到a39a、coverage29137及bc51 driver。32成功/0失败、524288输入/4096输出，120.483993092s仅作负载完成记录；KV521936，DB前后516表19270行实体physical/schema/logical全相同，preempt0→0，CPU6。原server.log八个JSON与封存snapshots完全一致；最后周期384 execute calls中305个受支持metadata步、250 mixed，累计3000个single-query decode **请求步观测**，2241在自然前缀且建plan、759在前缀外（所观察请求步的25.3%），另77 padding/unsupported单列，execute/observation错误0。**这不是独立请求数、全负载覆盖率或forward执行计数。** D29/P2019仍只是旧单层构造，不能用此统计倒推出某个真实精确几何。17:38:31.137125Z完整清理68MiB/0%/双栈端口闭/无GPU进程；runner为Z/PPid1，server/EngineCore退出。startup manifest记录的Attention bab2随后由retained按提交逻辑写回54c，postflight实际字节已核；原13eb正式基线此前单独封存，不能混淆两个阶段。

173921 CTA门独立核11项源SHA及06c7/4b44/原4c2e。只执行首个gate-up M2048/N12288/K2048：baseline与candidate的输出bits、finite、输入、RNG均true，但guard_rows_untouched=false，因此exit1；没有timing，down尚未执行。当前**正确性门拒绝，不启用**，也没有足够证据在kernel越界与guard检查误报之间下结论；原negative全部保留，待最短分阶段正索引CPU原字节诊断。17:39:31结束时68MiB/0%/9031空闲、无设备进程。

174115 CPUmetadata实际方法门独立核10项源SHA及b124/0e9615/0096/e155→50493。AST抽出的actual五方法及真实CpuGpuBuffer/BlockTable在五个fixture（decode62、M259、M952、M2048、纯prefill2048）各11项检查全true；连续四次host改值在原prepare event内，固定GPU地址graph consumer及非陈旧检查通过，selected75，strictscope回退与计时RNG检查通过。32call完整方法wall ABBA复算0.712748078125→0.65646540625ms，省7.89657294%、约56.282671875微秒/调用。**这是方法fixture小信号，未测模型/E2E/accuracy，不将7.9%写作服务收益。** 17:41:34 exit0，post表68MiB/0%、端口空闲、无GPU进程。各run补充独立review JSON已保存。

registry现76数据行×16列、queue52项；新调度/KV研究见`analysis/2026-10-22-scheduler-kv-innovation.md`，继续优先小计数门，不复用旧growth的性能假设。

## 两项小收益服务短筛及CTA守卫诊断收口（2026-10-22）

完整四run本地独立审计与可复算数据见`analysis/2026-10-22-small-framework-comparison.{json,md}`。A1 baseline174402/async174741同KV521840，39.4100407986→39.1346670017s，TPS+0.7036569314%、TTFT−0.8656382386%；metadata175049/A2 baseline175441同KV521936，39.0732484781对39.1852806420s，TPS+0.2867234444%、TTFT+0.2344306304%。四次均64/0、262144in8192out，原SERVER/bc51/0813/seed721201/CPU6/32GiB/包与installed源一致；410/411完整源码SHA核实，源差严格只有runner及各新增runtime。八份实体DB三hash同516表19270行且不变，preempt全0→0，实际FIRST_SELECTED命中，postflight68/0/双栈闭/无GPU进程。保留两项单次小正信号待确认，不集成/不冒称新accuracy或正式成绩；A1/A2容量不同，其时间变化不是严格matched漂移，metadata对A1约0.86%不能归因。

180033独立复算11源SHA、28份basic守卫文件：7阶段均−15992即BF16−17.0，hash不变、advanced读取未改storage；advanced初始化尚无JIT就有12288异常，真C identity/24576byte offset正常。它定位旧guard读法问题，status明确`not_a_correctness_pass`，无timing/down。旧173921失败原件不改。

180646使用b216正式门将oracle改为positive basic CPU完整bits/初值SHA，旧advanced仅旁证。11源SHA/两形状各8阶段共64basic文件、输出/finite/输入/RNG/计时后全通过，exit0清理。32call单ABBA gate-up wall1.4179341875→1.188571765625ms，省16.17581577%；event1.40435439348→1.17498886585ms，省16.33245345%。down wall0.735825265625→0.763840109375ms慢3.80726853%，event0.721999704838→0.750047981739ms慢3.88480448%。保留gate-up微测机会和down负结果，不能同时默认更改两形状，未证明E2E或模型accuracy。两run独立review JSON均在原run旁补充保存。

KV只观察模块a4de与e043→b3b7独立init已获framework全文互审；181041真实16K/1024/32请求门现已完整独立验收，411源SHA/32成功0失败/524288in32768out/220.345997615717s仅诊断、KV521840；35原log快照匹配，末周期2112core/2109schedule、1fail/preempt/resume、obs0。free0需要1页、queue1但terminal/private0，所以**不实现完成输出drain**。resume cache2944/floor16702/gap13758仅prefix exposure，非实际GPU重算token/时间或全程计数；原metrics preempt0→1。DB前后实体三hash同51619270、CPU6及18:17:30.243359Z68/0/双栈闭无设备进程均核，补充review在run旁。registry现83数据行×16列（历史同run多phase保留）、queue59项，仅维护CSV/队列行尾统一LF，raw/source不动。

后继CPU设计已落`analysis/2026-10-22-scheduler-kv-innovation.md`：短期准入需包含prefill债、FCFS进展与首完成后的峰值反证，不能把min剩余输出当保证；offload数据量16K672MiB，但真实copy带宽/worker同步及restore协议未知。当前无新策略代码/accuracy或预报收益。CTA gate-up-only服务44fc/source4ab/builder e007与root launcher已跨owner只读互审，严格热C0/当前指针/真实scope/capture和down回退；后续须REAL_SELECTED证明模型命中，不只dummy，root负责唯一设备任务。


## 182916 CTA服务及两次干净基线：描述信号与容量边界

三run完整本地独立stdlib终审，原SERVER/bc51/0813、16K/128/32req/c64/seed721201、CPU6/BI-V15032768MiB均同，32成功0失败/524288in4096out。CTA182916为118.417526429985s/4462.042199total/KV521840；干净183543为120.48498157598s/4385.476041total/KV521936；第二184244为120.763262667693s/4375.370360total/KV521936。三run的六份DB实体同516表19270行、physical1593/schemaa0a590/logical90e9未变，413/410/410源与5artifact SHA、postidle均核实。

首对照描述TPS+1.745903%，但KV池差96token，不能称严格容量因果；同物理32GiB满足平台约束，潜在实现启动/容量成本未分离，不为凑容量改参数或假buffer。两基线同KV耗时跨度0.23096745%仅观察，非噪声分布。Engine201873首次REAL_SELECTED证明真实2048/1req单步42次新launch，不是全负载覆盖计数。down关闭。原32/0后SIGTERM/abort/forcekill期间EngineDeadError及警告保留，不能写无ERROR或抹掉日志。单次正信号留存待确认，未默认/新accuracy；不拿coverage诊断作性能基线。可复算 `analysis/source/mm-cta-service-pair/recompute.py`，结果 `analysis/2026-10-22-mm-cta-service-comparison.{json,md}`；三run旁independent-service-review.json。

## mapped编译门到真实服务：层收益未转化

183421首derived skip2D JIT的use_sme68954357763 binding失败，exit1/cases[]/无计时，17源已核，negative不改；后继只修编译选项传播并保留原件。184809 correctness与185023 timing均17源SHA/四case各13checks及nextdecode/crossstream/capture回退通过，非整模型accuracy。185023的32callABBA构造D29/P2019 wall14.344921375→12.435507453125ms省13.31073118%，event14.216219902039→12.401883125305ms省12.76244170%；D29/P2019是构造，不能说是实际服务逐步geometry或命中覆盖。

185627真实服务完整414SHA/原SERVER/driver/seed/CPU6/32GiB及DB实体三hash同51619270核实，32成功0失败/524288in4096out/121.790163835976s/4338.478439947034total/TTFT62258.128146859235ms，KV521840/preempt0→0；Engine207423真实FIRST_SELECTED D15但首次marker非全程。相对183543描述TPS−1.07166475%，KV仍不同，不归因孤立算法；真实服务无正信号，未默认/新accuracy。post19:00:37.354668Z68MiB0双栈闭无GPU进程，shutdown错误分类保留。源/退出/DB/KV独立记录见run/independent-service-review.json；层13%不外推端到端。

## 42层KV复制成本门：CPU准备已冻结，尚无设备结果

实际184108的13份executor/worker/outputs/reshape等源完整核对，布局NHD `(blocks,2,16,2,128)`；normal/packed均由actual helper构造，不冒充已观测服务tensor。copy模块c95f、gate最终d841及一项CPU mapping合同已备妥并跨hardware owner互审；normal42/packed42×1run/8run、每方向672MiB，save event完成才毒化，restore event后consumer逐bit/guard/RNG。末delta只毒化内部页、不重置guard，SHA已同步并冻结；无SSH/GPU、无服务offload协议/accuracy。完整设计/命令/身份见 `analysis/2026-10-22-kv-page-copy-gate.md`。root下步按唯一设备串行队列执行，不能提前填结果。


## 191017 KV门归档导入失败：非复制结果

首个d841设备门在19:10:18Z exit1/cases[]，8源SHA独立核实；source/copy.py遮蔽stdlib copy，使dataclasses循环导入，尚未import torch或初始化copy，无byte/event正确性与成本结果。原worker traceback/failed results/8源和19:11:31.638525Z owner完整idle均封存，controller仅Z/worker退出，independent-gate-review.json已落；不是页复制算法失败。

按root授权最小修四归档/hash/load字面量名为biv150_kv_page_copy.py；policyc95f不改，新gate93eb02c7…/launcherba3336…已hardware定向终审。真实source子目录独立Python进程旧名重现循环fail、新名成功加载stdlib copy与policy（无torch/numpy/vllm）；加载检查首次Windowsstderr编码收集失败，显式-Xutf8后必要核查完成，未重复mapping suite。新稿冻结，待root另run串行重测；不能提前填四case成功或带宽。


## 191131 mapped必要重复：首负后正并列，不取最好

原件全本地，独立核414源SHA：413文件同185627，仅innovation-source.json的时间/command/output不同；DB三hash实体/原SERVER/bc51/seed/CPU6/32GiB一致；32/0同524288in4096out，117.028659570962s/4514.996599440720total/TTFT59836.11785736866ms/KV521840/preempt0→0/完整postidle。Engine210483首次真实D15与首轮相同，但都非全负载计数。首轮121.790163835976s及本轮117.028659570962s均保留，不挑最好、不凭时间反推cold编译/coverage。干净对照KV521936不同，仍不能称严格容量matched或稳定因果，无新accuracy/默认。独立结果在run/systems-independent-service-review.json，framework owner另做机制与独立终审。初审全414相同断言触发，未写记录；逐项核仅包装字段差后修正，本agent无设备。ownedregistry92×16/queue68均LF。root下一唯一KV191545 PID211570已19:15:45Z启用93eb，此为owner回执，尚无本地完成原件。


## 191545修正版KV门完成：四case正确，成本仅单样本

`experiments/framework/20261021T191545Z-kv-page-copy-gate{,-control}` 已完整本地，包SHA **7b491c525759e3320ecac8cd385d31fd1f434784ade63eef16bb2ab02a554316**。独立仅读8源SHA与93eb/c95f/1219/a351固定身份一致，19:16:59.928412Z exit0；normal42/packed42各contiguous与fragmented8四case，各untimed/timed两pass，40项checks与4项RNG均true。保存/恢复全byte、两guard不重写、未选页poison、42 actual-factory view消费者全部通过；shape(1058,2,16,2,128)、normal stride0=8192/offset41=0、packed stride0=344064/offset41=335872符合源码，每方向704643072B，copy调用分别42/336/1/8。原191017导入失败及修复加载证据保留；不是隐藏失败后只挑通过。

| 构造布局/页映射 | save wall ms | restore wall ms | roundtrip wall ms | save event ms | restore event ms |
|---|---:|---:|---:|---:|---:|
| normal42/contiguous | 25.946121 | 196.106984 | 222.053105 | 24.756731 | 26.488735 |
| normal42/fragmented8 | 27.699296 | 207.570993 | 235.270289 | 25.073376 | 194.106018 |
| packed42/contiguous | 24.943508 | 95.012686 | 119.956194 | 24.734741 | 26.496109 |
| packed42/fragmented8 | 25.027936 | 95.688994 | 120.716930 | 24.747791 | 26.758972 |

方向wall是host提交至事件同步返回，timing Event已预初始化，producer设置/poison/consumerclone/分配与CPUoracle窗外；保存事件完成后才读pinned/毒化，恢复事件后consumer才读取。每geometry仅一组warm成本，normal连续restore wall196ms/event26ms，而normal8run event194ms，host提交/调度混杂尚未分离，copy gate没有CPU quota或并行host工作负载记录。**不称稳定DMA带宽、packed因果加速或服务收益，不将event直接作纯硬件传输时间。** 各case显式host1432682496B、raw GPU728039424B；GPUallocated peak1456078848B含测试consumerclone，cgroup仅时点/20GiB限额非host峰值。

owner19:18:05.738516Z后态单卡68MiB/0%、9031双栈闭/无GPU进程，owned退出或Z、8源无failures核实。全量tensor没有另存binary；本地独立检查冻结代码的完整oracle和原结果，不重新运行GPU。结果保存 `run/independent-gate-review.json` 和 `analysis/2026-10-22-kv-page-copy-result.json`；registry93数据行×16列/queue69均LF。

这一门本身仍没有权重/真实runner tensor布局/Attention数学/请求allocator/跨进程恢复protocol/模型accuracy。后继服务入口若继续，须先证明actual executor与持有KV view的worker生命周期、save完成前不free、zero后restore且Attention前ack、host pinned强引用/epoch/cancel及失败回退；这是191545时的历史边界，后续195012/200957进展见下。181041 gap13758依旧只是exposure，不能把约0.12–0.24秒copywall替换成假定GPU重算节省；不能开启现成connector模式冒充实现。

## 200957单victim协议首门：SAVE/free发生，恢复未发生

195012已由framework独立验收真实normal42/UniProc同进程descriptor；此后新隔离Core/scheduler50375+事务616+worker31cc在 `20261021T200957Z-kv-protocol-context16k-long` 启用，原SERVER/bc51/16K输入1024输出/32req/c64/seed721201，VERIFY1仅诊断。原件包SHA **6b2abf4554bfdd3e2fc705a4b8d4a5555a033d764d17b35782296977821e253d**，本地独立核416源、installed attention54c/e155、DB前后实体/逻辑/schema三SHA不变（516表19270行）、CPU配额6、BI-V150物理32768MiB。raw32成功0失败、524288in32768out，221.1178005039692s/2519.2725268176705total/TTFT62550.40631070733ms，KV521936/preempt0→1；这一轮不能作性能对照。

Engine/worker215606实际FIRST eligible，SAVE R16704/1044pages/718405632B/1008copy_calls completed+successful后才原free；接着DROP serial2成功释放host。最终saved1/restore_skips1、restored/published0；没有ZERO/RESTORE、42层回读、runner恢复或消费证据。旧50375将复合precheck与allocateNone记为同一个skip，不能从日志确定哪一条件阻断；保存正确和恢复正确是两个门，不能把部分路径称全协议通过。host前后5596479488→7045218304B是时点不是峰值，20GiB限额/17104896B诊断额外预算保留。原raw完成后shutdown ERROR/force-kill警告按时序保留；20:15:43.088172Z单卡68MiB0%、9031双栈闭且无GPU进程，controller仅Z、服务/worker退出，source_failures空。详 `analysis/source/kv-transaction/200957-independent-review.json`。

根据该反例只改新的protocol候选：历史50375逐byte保 `analysis/source/kv-transaction/biv150_kv_protocol.50375.py`；当前 **a1b691f52f3724b95bbcb11f5702611a17103161001bb929096c71ab4fa74751** 暂态pending/placeholders/tokenbudget/allocateNone保HOST并继续原FCFS。本victim首次记录原因和cheap状态，不逐步日志、不提前consume/future、不park/重排。仅原本次output真有rid的num_scheduled_tokens>0且仍HOST时，dispatch前DROP普通重算不再需要的副本；非仅status判断，也不是forward执行证明。身份/epoch/终止/状态/digest失效仍释放；未改worker31cc、事务616、init footer、zero/restore/RPC/resume本体。

唯一新增CPU合同1test/0.002s通过：暂态重复仅一reason，原FIFO后清pending，placeholder及capacityNone保留，无work保持、普通工作计划后释放，身份/attempt/digest/terminal失效释放；源差分锁定3函数和1新helper，原footer/worker/txn不变。framework与hardware均对冻结a1b691独立只读终审无阻断；**尚无此修订GPU结果**，交root独立新run走原最短VERIFY门，不重测copy。新CPU证据 `analysis/source/kv-transaction/defer-cpu-check.json`，具体调用序和边界见 `analysis/2026-10-22-kv-transaction-protocol.md`。registry94数据行×16列/queue71项均LF，原正式成绩和负例未覆盖。

## 202526暂态保留通过真实单victim恢复链路

上一节“尚无GPU结果”为修订交付时的历史状态。实际新run为 `20261021T202526Z-kv-retain-context16k-long`（不是kv-protocol后缀），20:30:51.274086Z exit0，包 **430d2f7c211d2f52211e05cc29dca8505e840a3f6b1ec930c6410dca3a5f6c73**。独立仅读本地416源SHA/原SERVER/bc51/seed、CPU6/物理32768MiB、raw32-0/524288in32768out、KV521936/preempt0→1及后态；`analysis/source/kv-transaction/202526-independent-review.json`保留全部11条协议事件。240.92993535706773s、2312.1078714208797total、TTFT63227.1205921279ms仅原始诊断绝对值，不计算性能gain。

Engine/worker217577同一key、serial1–4、命令回显/真实completed+successful均过。SAVE R16704/1044页/718405632B后原free；首RESTORE_DEFERRED明确allocation_none，free1030/prefix1044/request_tokens16712/reserveTrue/pending0/placeholders0/tokenbudget2018/保HOST。最终454个skip后ZERO目的页→RESTORE完成，逐42层回读718405632B与host全byte相等，verification_performed/passed均true。随后RESUME_PUBLISHED→DROP成功释放host→RUNNER_RESUME_STATE_CHECKED六项均true（原CachedState/generator、computed、output token、完整block替换、CPUcomputed）→原update完成该output8个scheduled token。没有额外future消费/采样，restored/published各1、rollback0。该证据证明一个实际恢复链路；beforeAttention状态marker本身不是GPU完成，后续原output消费提供独立阶段证据，也不等于完整模型accuracy、取消/错误/多victim覆盖或随机输出逐字相同。

**DB发生变化**：before516表19270行、physical1593/schemaa0a5/logical90e9；after518表19337行，physical `d93510959a35313ec5331067cca3c496f817e96375ee398e52fb3cc1cbf6741d`、schema `a5ca71a552e35c3465fdfb85c1f74691a9e455aace1640ab5cafbddb22460d65`、logical `a180ecc5d609bf746af4c3a9a04d013c4fc6251b864d06317ce1faaf9da010f8`，全部实体复算。不能称cache-matched或用200957作性能对照；VERIFY额外copy/zero/回读都在本次诊断。20:31:52.483652Z source416无变化、68MiB0/双栈端口闭/无GPU进程，原shutdown错误及controller Z保留分类。200957的具体skip原因仍未知，不用本轮allocation_none回填。

后继两点分开：454次拒绝中存在每次prefix_digest/list历史复制成本，但只首条有free/reason，不能推断454次都可由free下界挡住，也没有计时证明该CPU成本。strict PREEMPTED/computed0/no-owned FullAttention下，完整R私有页需至少R/16个free，`free < saved_prefix_pages`可仅作安全快速拒绝；实际准入/digest/allocator仍保留，未知watermark不推导，**只研究未实现/上卡**。root选的唯一下一实现是已分配私有Block对象按block_id排序以减少restore页run，不混这条CPU早退或prefix截断；后续源/互审另记。registry现95数据行×16/queue71均LF。


202526后继唯一排序候选已CPU准备并双职责终审：protocol **0e2115d0fbdedea64d1b911c0d6ae3b359f178004d844a8dd8088dfa4388fb86**，旧a1b字节保历史，worker31cc/事务616/c95f/footer未变；只对完整、ref1/unhash/numcached0、未bind/publish的实际req_to_blocks同list原地升序，重新derive dest统一ZERO/RESTORE/新payload，guard外旧路。1项CPU映射合同0.001s通过，去helper+单call精确逆回a1b；研究见analysis/2026-10-22-kv-private-page-order.md。旧1044页集合升序66run只是CPU推导，actual worker31cc ZERO同样按plan.runs合并，因此ZERO/RESTORE/回读对旧集合均可43848→2772调用；初稿误称ZERO固定逐页已按root源反证纠正，代码和原件未变。未来free归还物理序会变化；新服务尚待root唯一门实际ordered marker/42byteeq/runner及原消费，不混454早退/截断，不预报收益。registry95/queue72均LF。

## 204159目的页排序真实激活：1044→66run，协议诊断通过

上一段是候选交付时快照；新 `20261021T204159Z-kv-page-order-context16k-long` 已20:47:11.313241Z exit0，包SHA **588886979857dc1eab16dcfa8ed8b8a76751741f3b21825cfa62fa8219872336**。独立本地验416源/原SERVER/bc51/seed/CPU6/BI-V15032768MiB、DB实体前后518表19337行三SHA均同d935/a5ca/a180、源post未变及20:47:45.919662Z68MiB0双栈闭无GPU进程。原32成功0失败、524288in32768out、KV521936/preempt0→1；227.54834548803046s/2448.0775670122475total/TTFT62799.9383899587ms仅VERIFY诊断绝对值，**不与202526增长DB诊断比收益**。

Engine/worker219639完整12事件同key/serial1–4：SAVE16704tokens/718405632B后原free，暂态保HOST454skip，PRIVATE_PAGES_ORDERED实际1044页同set/对象/list从1044run变66，再ZERO/RESTORE；RPC目的页ID全量独立重算升序且唯一、相邻66run。ZERO/RESTORE/诊断回读各2772调用、42层718405632B全byte相等，SAVE仍1008copy；随后publish/drop/runner六项检查全true、原output处理8token。saved/restored/published各1、rollback0，host释放成功。现在66/2772是本run设备原件事实，非仅旧集合推导；但没有不回读性能/完整模型accuracy，future free/LRU顺序与单victim覆盖限制不变。原shutdown错误保留。详 `analysis/source/kv-transaction/204159-independent-review.json`、更新的私有页研究；registry96数据×16/queue72均LF。

容量必要下界早退下一方向只完成源码研究 `analysis/2026-10-22-kv-restore-capacity-fast-reject.md`，未改0e/runtime/测试或设备。FullAttention no-owned下F<P能安全判失败，水位仅取源保证非负、不猜实际值；关键反例是延后digest可能延迟失效host释放，故未来最小快路还须closed-input/nonresumable/Request源身份与长度失效等守卫，其他走旧路。454总skip无逐次free/hash计数，不能说全部可省CPU或已证收益，不混本次页排序原件。

## 205219不回读stable基点完成；67e4容量候选仅CPU准备

`20261021T205219Z-kv-pair-stable-context16k-long` 完整本地，包 **3ac6fc894e72d8ba4d0f96aa5e48c25d07e442f23d909f7d2f121c8e902700d3**。独立410源/stable080656/e155/bc51/原SERVER/seed/CPU6/32GiB、0协议marker、DB前后51819337三SHA同d935/a5ca/a180实体复算；32-0同524288in32768out，220.40704781701788s/2527.3964944282015total/TTFT62508.42458468105ms/KV521936/preempt0→1，VERIFY回读未启。20:57:56.258707Z410源post无变/68MiB0/9031双栈closed无GPU进程，退出错误分类保留，审计 `analysis/source/kv-transaction/205219-independent-review.json`。wrapper11917检查DB起点的候选205819仍在途；root已实际观察candidate KV521840与base521936失配，不先报gain/严格容量matched，不改参数凑容量。

root后来接受容量早退最小实现，覆盖上一段“只研究”状态，但**只在新文件** `patches/framework/candidates/biv150_kv_capacity_protocol.py` 67e4，不动canonical0e或在途pair。Request06b1实际类/源码及原方法file守卫仅控制快路，失败走旧协议；nonresumable/no streaming、长度即时失效、noowned/cached无或0/R整页maxlen内/F<P才defer+fast_rejects，F=P及其它原tokens/digest/history/allocator保持。唯一CPU合同e9c/1test0.021s过，去新增完整bytes逆回0e，framework/hardware均终审，无新设备或性能证据。具体反例/验证在早退研究和capacity-cpu-check.json。

独立新builder `prepare_kv_capacity_source.py` a79b69d8… / launcher `launch_kv_capacity.sh` 0ae8ced5… 已按root请求准备并送最终包装审。新asset容量文件67e4只映射新隔离source canonical协议名，base080656/init791c/worker31cc/tx616/c95f不变，新kv-capacity标签VERIFY1；compile+heredoc/diff通过，旧4c8/8d7完全不变，没有整copy/旧suite/设备，尚未启动。registry97数据×16/queue74均LF，不将0e已测迁移为67e4结果。

## 205819不回读候选完成：KV+DB双失配，保留结果但不报gain

`20261021T205819Z-kv-pair-page-order-context16k-long` 于21:03:25.435830Z exit0，包 **5e0873334997c59899d9dad5653d80529729eb508b8ce7c93e74587311b86e82**。独立416源/0e、原SERVER/bc51/seed/packages/installed-source与基点同，CPU6/物理32768MiB；32-0同524288in32768out，220.92108358303085s/2521.515787290788total/TTFT62648.45590684854ms。候选KV521840，基点521936；DB before51819337三SHA确等baseafter，但候选after51919340，实体 `89743b20d842c8f6067f6e1b917dec0f9f9b4eae19d93e3ebf02e168f4aea605` /schema `29d740d5351d1372df2bb6317a651c70b682d2d855b51e717afd576cfe78c078` /logical `71ac19899ea28dda8cb94b517a8f598c487bbd19f392a9b285ff5ab660355c29` 全实体复算。**容量及DB双失配，不报吞吐收益或严格matched，不通过补stable/改参数凑容量抹除这轮状态。** 原始绝对数值和不利可比性均保留。

真实链仍完整，但本轮不同于204159：Engine222629，R16688/1043页/717717504B，SAVE966copy，首defer free1039/prefix1043/request_tokens16704/reserveTrue/pending0/placeholders0，final skips462；PRIVATE1043→66run，ZERO/RESTORE各2772调用，completed/successful；publish/drop/runner六checks和原output16token消费通过。VERIFY0，extra_pinned0/diagnostic_verify_requested=False，**没有verification/readback字段，不能套用前诊断全byte回读或8token/1044页**。saved/restored/published各1、rollback0、preempt0→1。21:03:56.715618Z416源post不变、68MiB0/9031双栈closed无GPU进程，controller为Z；本run未命中ERROR，原shutdown日志保留，与205219的ERROR分开记录。完整审计 `analysis/source/kv-transaction/205819-independent-review.json`；baseline派生review已更新pair完成双失配状态，未改raw。

容量67e4/e9c唯一CPU合同及a79b/0ae包装已两职责/root终审接受，**保持独立冻结、不上传执行**，没有迁移本轮0e证据。registry98数据×16/queue75均LF，研究/中文交接齐。按root一致归档要求，本批收尾后暂停文件写入，goal仍持续；解锁后再按root后继顺序推进，不自行设备/推送。

## 212106容量快拒真实命中；后继FULL仅CPU与包装准备

归档写锁已解除，以下覆盖前节“本批暂停写/67e4未执行”的历史状态。`20261021T212106Z-kv-capacity-context16k-long` 已21:26:17.768468Z exit0，32-0/524288in32768out，227.19113439507782s/2451.9266629097337total/TTFT62762.77446313179ms，只作VERIFY1诊断绝对值。独立416源/67e4+616+31cc+c95f/e155/bc51/原SERVER/seed721201、CPU6/物理32768MiB/KV521840/preempt0→1核实；DBbeforeafter51919340三SHA同89743b20/29d740d5/71ac1989实体复算。21:27:50.103577Z416源post无变/68MiB0双栈closed无GPU进程，未命中ERROR、forcekill WARN原样保留。包8e04b0b6301c724741759d3a2926e17726b011448ec28b8a14a7ac2ce50af537；详细独立审计source/kv-transaction/212106-independent-review.json。

实际fast_rejects462、首free1039<P1043、R16688/717717504B，保HOST后恢复；计数能证明本次462条未走快路后面的hash/history/allocator，不能换算CPU时间/性能收益。PRIVATE1043→66run，ZERO/RESTORE/42层回读各2772调用全bytepass，随后publish/drop/runner六check/原output16token消费完成。该次仍有ZERO，不能继承为新的RESTORE_FULL证明；不混205819 VERIFY0或历史双失配轮。

root授权新独立累计候选：candidates/biv150_kv_full_restore_transaction.py 84be2242…、protocol.py 1aff952a…（基于67e4）、worker.py 5d9a082f…；旧0e/67e4/616/31cc/c95f全冻结。真ALLOCATED提交RESTORE_FULL，真实同operation完成ACK到RESTORE_DONE，无伪ZERO；SAVE真ACK携normal42完整页caps，adapter私有映射proof及worker全覆盖plan齐才进入新模式，缺资格仅提交前走原ZERO。成功ACK缺coverage/destbound/zero_calls0证明在Receipt前failclosed，提交后失败不降级，settled才回滚释放。保producer device围栏/H2D事件/VERIFY回读和原消费顺序。

唯一联合CPU合同tests/test_biv150_kv_full_restore.py 0035b97…实跑1项0.002s，通过actual parser/plan元数据与adapter/transaction ACK stub/失败取消回滚；不调用worker GPU RPC/copy/event，不是字节或完成证明。framework/hardware/root三方终审无最短新VERIFY1门阻断。新prepare_kv_full_restore_source.py b4e04e50…和launch_kv_full_restore.sh 63947c7f…仅沿a79b/0ae改三asset映射、标签/目的和pins，080656/init791c/e155/原bc51命令/seed721201/VERIFY1不变；只compile/heredoc/diff/pin检查，hardware最终只读审已无阻断，未执行shell/整copy/suite/设备。完整设计见2026-10-22-kv-restore-full-transaction.md。root当前213016容量性能stable独占设备，FULL未启动、不预报收益/完整accuracy。registry99数据×16/queue76均LF。

## 213016容量性能stable完成；213616候选尚在途

`20261021T213016Z-kv-capacity-pair-stable-context16k-long` 独立本地410源/同stable080656字节、e155/bc51/原SERVER/packages/seed721201、CPU6/物理32768MiB、0协议marker验收通过。32-0/524288in32768out，220.5050202300772s/2526.2735488686926total/TTFT62602.81379344815ms/KV521936/preempt0→1；DBbeforeafter51919340三SHA897/29d/71ac实体复算同。21:35:42.054721Z410源post无变/68MiB0双栈closed无GPU进程；测前ERROR空，raw完成后shutdown EngineDeadError和forcekill WARN原样保留。包5b45a043eb5e6c85ab144270fe21cce560b3f3dfa355352cbb0840c51966de6e，审计source/kv-transaction/213016-independent-review.json。

root唯一新213616-kv-capacity-pair-capacity-context16k-long runner227753、参考212106 source/67e4、VERIFY0，起点DB已由wrapper核；完整候选原件尚无，不预报KV容量/DB终态/吞吐收益。新FULL包装b4e/6394已root+hardware最终接受，尚未上传执行；旧67e4和FULL三资产冻结不变。registry100数据×16/queue77均LF。

213616在途启动最新证据：root已读真实KV521840，基点213016为521936，相差96tokens/6blocks，当前已判容量失配；candidateafter DB与最终raw仍待。该判定在TPS结果之前落盘，不补stable或改参数凑容量，正常完成后保留结果，不报严格matched gain；后继由root先排FULL真实门。

## 213616容量VERIFY0配对完成：DB相同，KV失配不归因

`20261021T213616Z-kv-capacity-pair-capacity-context16k-long` 已21:41:20.878752Z exit0，独立416源与212106完全一致、67e4/616/31cc/e155、原bc51/SERVER/packages/installed/seed与213016同，CPU6/32768MiB。32-0/524288in32768out，218.9170063282363s/2544.599021077285total/TTFT62573.5605845548ms；基点220.5050202300772s/2526.2735488686926total/TTFT62602.81379344815ms。**候选KV521840，基点521936，少96tokens/6blocks；该失配已在结果前记录，保持不归因收益、不补stable或改参数凑容量。** 本次DB after已实体复算，不再是待项：双方before/after519表19340行、physical89743b20/schema29d740d5/logical71ac1989三SHA相同。DB匹配不能抹去KV失配或证明主机/Triton所有cache状态相同。

实际R16688/P1043/717717504B、source23run/SAVE966copy；fast_rejects462，首capacity_lower_bound free1039<P1043/pending0/placeholders0、保HOST。PRIVATE1043→66run，ZERO/RESTORE各2772真实completed/successful ACK，host最终DROP，runner六checks/原output16token消费。VERIFY0/extra_pinned0/diagnostic_requestedFalse，**没有全byte回读字段**，不能套212106或新FULL。21:41:59.079650Z416源post无变、68MiB0/9031双栈closed无GPU进程；测前ERROR空、raw完成后shutdown EngineDeadError/forcekill WARN保留。包49e79345ccc94f442c3ab46277691dfa0101882d4914ff7d5737f1782cc26d4d，详细source/kv-transaction/213616-independent-review.json。

当前root唯一214400-kv-full-restore-context16k-long runner229261，b4e/6394及1aff/84be/5d9a冻结源、VERIFY1原bc51。FULL尚未完成/取回，不生成通过结果；2071本地验收入口仅语法准备，待真实原件后执行。registry101数据×16/queue78均LF，旧官方/根README/CURRENT和所有raw未改。

## 214400显式FULL真实验收：零ZERO，完整42层回读与原消费通过

已实际执行固定SHA2071的 `scripts/review_kv_full_restore_run.py 20261021T214400Z-kv-full-restore-context16k-long --output analysis/source/kv-transaction/214400-independent-review.json`，exit0，状态passed_full_restore_verify1_diagnostic。新JSON SHA **aa16dc31f430230db6c1c0ed69f55b88b3d036b3822bf59e2b9a8ddd9d97ea45**；原件包owner SHA **21ae6e302795fba5d6b09b6597d26cd0e58d95c3805cffe079ded2934ca981ea**。入口及81f2依赖已由framework只读终审，无阻断；此次才有FULL实际证据。

独立416源/1aff协议+84be事务+5d9a worker/c95f/e155/init791c/原080656、b4e builder/63947 launcher/原bc51-SERVER-seed721201/CPU6/32768MiB，32-0同524288in32768out。21:49:12.117141Z exit0；226.79482778999954s/2456.2112171085555total/TTFT62775.54467374284ms，KV521936/preempt0→1。DBbeforeafter51919340、physical89743b20/schema29d740d5/logical71ac1989实体复算相同。21:49:38.171431Z416源post无变、68MiB0/双栈9031closed/无GPU进程；测前ERROR空，raw完成后shutdown EngineDeadError/forcekill WARN原样分类保留。

真实命令恰 **SAVE1→RESTORE_FULL2→DROP3，没有ZERO/旧RESTORE命令**；同key、operation serial、PID、页和字节回显/settled/success齐。实际R16704/P1044/718405632B，SAVE源24run/1008copy；私有目的66run，FULL2772copy、42层718405632B逐byte回读2772copy全相等。成功ACK明确zero_stage_executedFalse/zero_calls0/full_coverageTrue/destination_boundTrue/full_coverage_bytes匹配；完整SAVE能力字段齐。fast454、原HOST等待后发布、host DROP释放、runner六项全true、原output消费**8token**。入口动态计算真实几何与consumer，不能套213616的R16688/P1043/16token。

这证明省ZERO的新事务已在actual normal42服务中完成一次保存→恢复→发布→原消费；没有伪ZERO ACK或只CPU状态假通过。**VERIFY1含额外42层回读，严格不作性能收益/与213616 VERIFY0比较、不证明完整accuracy、异常取消/多victim覆盖或默认集成资格。** 没有ZERO阶段独立计时，不从省718405632B写入推导TPS。root后继设备/匹配性能/准确率门仍独占排程，本agent仅本地审计与记录，未修改任何运行资产。registry102数据×16/queue78均LF。

## 启动组成观察最短包装：同6a附stable410/capacity416，仅CPU三方终审

新prepare_kv_memory_observer_source.py **0ab0ce3ab3d8cde4a8e725d9fdfd3e62726fcf95613fbc1e55b850b3e48a9029**、launch_kv_memory_observer_smoke.sh **5bdb67afe573d9ffc803e40bafcaee2e7e7fd85e8b831bb94137516e85c060fd**冻结；root/hardware/framework最终全文只读审无阻断。固定73e5/5bef从完整manifest信任链取stable410/capacity416原树，只完整init末尾append同6a observer→00e8/39fb并新memory-observer-source.json，原innovation/a8de/e155/协议guards字节不变，预期source412/418。原bc51 smoke-only/seed721201/VERIFY0，不跑long或改SERVER；require实际DETERMINE_RETURN，后验仍须同PID/profile1/完整标量/PARENT原list/三hook恢复。只compile/heredoc/pin/读取两原init，无整copy/新suite/设备或fake结果。root随后两次串行并既有seal收after/live/post，非性能pair，不报6块差因果。详2026-10-22-kv-memory-observer-packaging.md及source/kv-memory-observer/wrapper-check.json，queue79待设备，registry102数据保持。

## 215849/220122两次启动观察验收：相同组成，未复现历史6块

两run/control已由root fullseal取回，本agent仅本地stdlib审计，原bc51 smoke-only/原SERVER/seed721201/VERIFY0及全部source/args/DB/post逐项通过。215849 stable412源、实际PID231345，21:59:48.409778Z exit0，post22:01:02.902726Z；220122 capacity418源、PID231998，22:02:21.679911Z exit0，post22:03:14.114658Z。完整410/416输入由73e5/5bef锁定，只完整init尾append00e8/39fb+同6a module+独立manifest，capacity原innovation5bef字节保持。原smoke请求8in32out/32tokenIDs/logprobs/finish_length均完整；**不是吞吐或accuracy测量**。

两轮各有同PID唯一DETERMINE_RETURN与PARENT_RETURN、原profile_context_calls1、原worker int22447777996→父真list[同值]、worker/profile/parent三个hook恢复全True；无REJECTED/NOT_ACTIVATED/OBSERVATION_INCOMPLETE，原已有快照/worker/profile内存标量完整。全部内存数值（排除timestamp/profile_time）双方相同：requested29205777612.8B、weights5101233152B、torch_peak_increase656424960B、non_torch_increase1000341504B、nonKV6757999616B、cudagraph estimate0、available22447777996.8B。KV均521936，CPU6/物理32768MiB；DB双方before/after51919340三SHA897/29d/71ac实体复算同。post全源无变/68MiB0/双栈9031closed无GPU进程，测前及shutdown ERROR皆空，forcekill WARN原样保留；logger/rootWARN由hardware另审，不泛称ERROR。

机器审计source/kv-memory-observer/{215849,220122}-independent-review.json，SHA分别8164fb2845d3bd00d63706c6e5ba6e9740815200c22612576910c12a910776cc、ec40d7649cbec086bf1c8c2068b1b9c56002b85da17f9a3b12a77ec2fe150701；复算入口review_smoke.py SHA8508b2fef60425981808eb9755a0063c75dc2046e440bd32f7d2452217d5eb9e，只读取已封存原件/DB，不运行框架/设备/新套件。实际memory相等比较在systems-startup-comparison.json，package owner SHA stablef9e37bd5…/capacityb2bab46a…完整保存。

**本次两startup未复现历史96token/6blocks差，不能倒补213016/213616或其它旧run的分项/原因，不能解释成实现零成本/长期稳定或性能收益。** 新采样为零，原context自身已有采样不因本门重复调用；时间字段不作内存相等/性能指标。未来最短VERIFY0对照可共用此observer同时记录真实启动组成，不追加盲目boot样本或改参数凑容量。registry104数据×16/queue80均LF；本阶段所有收尾完成后暂时停写供root一致发布/ZIP，goal仍active，设备当前空闲只root排程。

## 写锁解除后的共同观察器VERIFY0包装：CPU终审，未新设备

root完成一致发布/ZIP221629后允许接续。新prepare_kv_observed_pair_source.py fc937baf… / launch_kv_observed_pair_screen.py d768860b…固定212106与214400两完整416源/旧manifest，原init791c同6a末尾append→39fb/最终418；三实现模块不改。capacity先、FULL必须本launcher同SHA前件exit0/post/完整启动receipt和DBbefore=after=新before三SHA，准备锁释放后原bc51long/seed721201/VERIFY0，require实际DETERMINE_RETURN。三方最终全文审无阻断；只compile/AST唯一名/scalar/真实map/append/pins，root对旧两log observer_receipt兼容核已记且未重复，无新prepare/copy/suite/GPU。草稿旧dict残留已删、未部署，最终AST检查专门覆盖。新研究2026-10-22-kv-observed-pair-packaging.md与observed-pair-wrapper-check.json齐，queue81/registry104不增设备假结果。后验动态R/KV/DB/内存/consumer/各自操作链，VERIFY0不继承回读，总差不冒称纯ZERO耗时或收益；不自动继承accuracy/默认资格。

共同观察器新pair启动回执：root已唯一GPU启动222731-kv-observed-pair-capacity-context16k-long runner233765/source code/kv-observed-pair-capacity-20261021T222731Z，新远端路径absent→上传逐SHA fc937/d768/compile、418源新建成功。原bc51long/seed/VERIFY0，当前没有raw/启动分项/KV或DBafter结果，FULL未启动，等待root seal原件；queue81在途/registry104不增假行。本agent无SSH/GPU或运行源修改。

## 222731共同观察器capacity基点完成：真实组成已记录，FULL结果待

framework已唯一实跑最终c0c80dcf…验收入口，222731-capacity-review.json SHA **ece929aef6d788658b7482ff5d22052cea7694cf5aa4e24f664e207327646f27**通过。首a5b7版本对EXPECTED_LOADED的Name静态解析失败，旧脚本/first-attempt已原样保留，修解析器后唯一实际通过；不是GPU候选失败或重跑设备。本agent按root分工只读该报告后独立核原raw、选定六角色源/原events、DB物理字节与fingerprint metadata、post字段，**没有重跑同入口/套件**。字段复核在source/kv-memory-observer/222731-registration-crosscheck.json，418全源/live/SQLite语义指纹仍由framework全审负责。

22:32:35.393293Z exit0，32-0/524288in32768out，218.81890873378143s/2545.7397773504263total/TTFT62472.47070692538ms，KV521840/CPU6/物理32768MiB/preempt0→1。418/init39fb/同6a/原67e4-616-31cc/e155/fc937-d768/bc51原SERVER/context-long/seed721201/VERIFY0核同；DBbeforeafter51919340三SHA89743b20/29d740d5/71ac1989同。22:33:26.459826Z418源post无变/68MiB0/双栈closed/无GPU进程；测前ERROR空，raw完成后shutdown ERROR与forcekill WARN原样保留。包owner SHA8ded4126824d40bac5869cbb254238b9de9dbcceaa67907a7e73b926030f991b。

实际Core/Worker233942，同PID profile1、原int22443583692→PARENT真list同值、三个hook restoredTrue。原profile non_torch_increase1004535808B、nonKV6762193920B、available22443583692.8B，其它分项与完整原快照保留；hardware另做4MiB专项，不由此倒填未观测历史或预判FULL。真实SAVE-ZERO-RESTORE-DROP serial1–4，R16688/P1043/717717504B，SAVE23run/966copy，目的66run/ZERO与RESTORE各2772，fast462/host释放/runner六checks/原consumer16，VERIFY0无回读。

当前只有此侧完整结果，FULL身份/原件及最终DB/KV/组成匹配以root后继回执为准；不把既有FULL214400 VERIFY1或旧smoke的相等移植过来，不计算pair收益。registry105数据×16/queue81均LF，原官方/冻结资产/根文件未改；本agent继续只CPU，等FULL实际报告后独立字段复核登记。

root随后确认FULL223613-kv-observed-pair-full-context16k-long已唯一GPU启动runner235307/source code/kv-observed-pair-full-20261021T223613Z，fc937/d768不变；launcher实际222731 before=after=新before三hash及源后态/observer receipt门通过。当前FULL KV/内存/raw结果未知，不提前填值或gain；queue81在途/registry105，等唯一实际审计再复核。

## 首组共同观察器VERIFY0完成：FULL约+0.199%单次小信号保留

223613 FULL已由framework唯一c0审计通过（4fb9b2ca…），本agent只独立原字段复核，不重复c0/套件。32-0/524288in32768out/218.3848344660364s/2550.799836270839TPS/TTFT62338.00159151724ms。相对222731 capacity218.81890873378143s/2545.7397773504263TPS，原raw独立复算TPS+0.19876575624233617%、duration−0.1983714617063148%少0.434074267745018s、TTFT−0.21524539350935568%；保留单次小信号，不当稳定收益/纯ZERO阶段时间。

两侧418/init39fb/共同6a、原SERVER-bc51-load-seed-packages-installed、CPU6/32GiB/KV521840、启动非时间内存项/DB四快照51919340三SHA同；实际R16688/P1043/717717504B/SAVE23run966/目的66run2772/fast462/consumer16/runner6/host释放一致。hardware独立核源和目的实际page_ids逐项相同（9f319d02…），本人没重复数组专项。FULL真SAVE-FULL-DROP serial123/0ZERO/caps覆盖ACK，无VERIFY0回读；旧VERIFY1单列不移植。FULLpost22:42:01.143516Z418源/68-0/双栈closed/无GPU进程，测前/shutdown ERROR都空，WARN留；capacityshutdownERROR分别记录。

新比较source/kv-memory-observer/observed-pair-first-comparison.json和中文2026-10-22-kv-observed-pair-first-result.md齐，registry106/queue82均LF。root在复核数据前决定仅一组必要A2/B2，无论正负/失配结束该性能重复，不追容量/不改参数/不取最好。A2 224411-capacity runner236809正在唯一GPU，同runtime/fc937-d768完全冻结；本agent将在新原件到齐后唯一执行c0，framework暂专注victim观察。当前A2/B2结果未知，不计算第二组或总体均值，不新增accuracy/默认资格。

## 唯一必要复核A2：224411实际c0通过，B2待

root取回A2原件后，本agent按新分工**唯一实跑**c0 capacity，exit0/pass，生成224411-capacity-review.json SHA **e52a572e7ccbb577acf882934bf8ef06f42a0fe8f01d13efc0cb17442a2a5d45**；actual执行回执224411-audit-execution.json，没有重复旧入口或套件/设备。原包owner SHAd899801ffdf287cfadd061f36f6f242a8f62a5bba6d44d251e03e79adb0f08ad。418/同6a-init39fb/原fc937-d768/原SERVER-bc51long-seed721201/VERIFY0，32-0同524288in32768out，218.84790462488309s/2545.402483769829TPS/TTFT62497.66085240117ms，CPU6/物理32GiB，DB51919340三SHA89729d71ac前后同，post22:50:43.051813Z418源/68-0/双栈闭无GPU进程。测前及shutdown ERROR皆空，forcekill WARN原样保留。

本轮真实KV **521936**，R16704/P1044/718405632B/SAVE24run1008/目的66run、ZERO与RESTORE各2772，fast454/consumer**8**/host释放/runner6；不能套首组521840、R16688/P1043/fast462/consumer16。startup实际PID236995/profile1/原int22447777996→父真list/三恢复，profile非TorchIncrease1000341504/available22447777996.8B。与首组容量层级不同，不合并A1/A2绝对TPS或整体平均；B2当前未齐，不能预报匹配/复核方向。必要前件验收状态已先回root，后由原launcher真核DB/source/post/observer接B2。

registry107数据×16/queue82均LF；首组小信号仍原样保留，第二组只等对应B2。按预先决定，本组后无论正负/失配都结束此性能重复，不追容量/调参数/择最好，不新增accuracy/默认资格。


## 两组分层总结已准备；唯一复核B2 225501在途

root已串行启动225501 FULL/runner238456，match完整A2 224411 control；runtime/fc937-d768/VERIFY0/原负载冻结。新中文总结2026-10-22-kv-observed-pair-two-pairs.md先列首组521840与A2的521936，B2完整指标/比率待原件，不跨层级合并均值。下一仅本agent唯一c0 full引用224411报告；无论正负失配均按预定结束性能重复，不追加盲样本。registry107保持、queue82明确在途；当前没有新运行/源码修改/SSH/GPU。random dataset实现本地缺件，actual serve.py仅证add_dataset_parser/get_samples入口，默认range_ratio及逐请求同长仍待root取实际实现，不由总token反推。


## 唯一必要B2 225501完整实审：两组小差均保留，本项重复结束

本agent唯一执行固定c0 full并引用A2 e52a，225501-full-review.json SHA **62b07a8cabef0cf5d9259abb433e83e55ccfb553b121de4e4e0df7ae62af9b2f**，实际exit0/pass；225501-audit-execution.json保存唯一命令/exit0/pins，另只读两raw字段与token/duration算术，不重复完整入口或旧suite。32-0/524288in32768out，218.7160065015778s/2546.937505444904TPS/TTFT62627.150716711185ms。418/共同6a-init39fb/原fc937-d768/bc51-SERVER-long-seed721201/VERIFY0；A2B2 CPU6/物理32768MiB/DB四端51919340三SHA89729d71ac/KV521936/启动非时间分项/原args包installed均匹配。实际PID238635/profile1/int22447777996→父真list/三hook恢复；R16704/P1044/718405632B/source24run1008copy/目的66run2772/fast454/consumer8/runner6/host释放，真SAVE-FULL-DROP serial123/0ZERO/完整覆盖ACK，无回读。23:01:06.003547Z418源post无变/68MiB0/双栈闭无GPU进程；测前与shutdown ERROR空，forcekill WARN保留。

组内FULL TPS+0.06030565636920837%、duration−0.0602693105658747%少0.13189812330529094s，TTFT+0.20719153732142725%，小正TPS及负向TTFT均保留。首组KV521840另列TPS+0.198765756%；不跨容量/几何合均值、不当纯ZERO计时/稳定因果/新accuracy。新observed-pair-two-pairs-comparison.json SHAc7f7ffa9…与中文2026-10-22-kv-observed-pair-two-pairs.md齐；registry108×16/queue82均LF，旧未涉及行逐byte保持。本项按结果前预定规则结束重复，不追样本/调参数/取最好；后继victim观察分开，不动CURRENT/冻结资产/SSH/GPU。


## 230548真实抢占瞬间snapshot完成：只观察与后继最小路线

framework唯一6eb45实际验收pass，230548-review.json SHA06c16d26e8eee184269d46d09f488da5b63867f90e57900eaaf1484c23ae53e4；本agent只读报告/精确df780-pool-single源，未重跑入口/raw全审。32-0/413/220.41899300506338s仅诊断/KV521936/DB51919340三SHA同，23:11:57.075293Zsource-live/68-0/双栈闭通过；测前ERROR空，shutdown ERROR/WARN原样保留。实际Engine240315 completeTrue，首次失败31running prompt均16384/output327..569，free0/exact派生需1/failed index1/旧queued1；index0为最小remaining455且本轮已排1token，tailindex30 output327/rem697/1045私有页中1044hashed。29个排除protected/failed且可释放够页的结构候选含原tail，不是评分或已选新策略。该31请求prompt同长是本次快照实值，不由aggregate倒推全部32。

新中文2026-10-22-victim-scheduling-minimal-route.md精确核PRIORITY已scheduled撤销/返预算/映射清理、按移除前index处理前方skip未scheduled反例、原free/prepend/preempted列表/本轮禁waiting与queuedFIFO；不改policy参数、不碰运行源。最强反证：保护minremaining当前已被原tail策略满足，可能零变化；free后hashed页留APC，need1或先消耗无hash页，不可把owned全算重算；改变victim无FCFS公平/逐token等价保证，单快照无makespan预测。未选评分或实现controller，旧reserve/terminaldrain不重做。registry109×16/queue83均LF，后继动作仅root决定；本批记录齐后暂时停写供统一publish/ZIP，goal持续。
