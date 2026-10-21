# SQL+C3基点上的两项小收益短筛

systems_innovation，2026-10-22；仅天数BI-V150。本agent只读本地原件，未SSH、启动设备或导入torch/vllm。用户要求小收益同样上卡并保留；下列是单次服务信号，不是已确认稳定收益、比赛总分或最终集成。

| 运行 | 秒 | total tok/s | mean TTFT ms | 实际KV tokens |
|---|---:|---:|---:|---:|
| A1 baseline174402 | 39.41004079859704 | 6859.571685843667 | 20301.98434733029 | 521840 |
| async174741 | 39.13466700166464 | 6907.8395374745605 | 20126.242607628228 | 521840 |
| metadata175049 | 39.07324847811833 | 6918.697843907006 | 20123.110001033638 | 521936 |
| A2 baseline175441 | 39.185280642006546 | 6898.917031366118 | 20076.04560076288 | 521936 |

按各自容量匹配：async/A1吞吐比 **1.0070365693138692**，即 **+0.7036569313869201%**；耗时省0.6987401976%，TTFT−0.8656382386%。metadata/A2吞吐比 **1.0028672344443272**，即 **+0.2867234444327238%**；耗时省0.2859036915%，TTFT+0.2344306304%。这些百分比用原JSON未舍入值计算；同tokens时TPS比等于baseline秒/candidate秒，耗时省百分比则为1−candidate秒/baseline秒，两者不能混用。

四次均64成功0失败、262144输入/8192输出，原SERVER参数、bc51 driver、0813 benchmark、4K/128out/c64/64req/seed721201、包版本一致，无profiler。CPU测前后quota600000/period100000即6核，gpu.csv均为BI-V150/32768MiB。async和metadata原server.log各有真实EngineCore FIRST_SELECTED；它不是每步完整计数。其余installed源身份全相同。独立逐文件核对两基线各410项、两候选各411项归档SHA，原封存live失败列表为空；每组仅runner与新增各runtime两项差异：e155→f0d0/1bb85（async），e155→50493/0e9615（metadata）。原稳定实现不覆盖。

八份前后SQLite实体物理SHA均`1593d60cda1b2ed9a70df9fc4cebe3217e863f9fcb428000dea19fe21c8d6352`，schema `a0a590080bc570c73c1a25337faa1097038bcc6d755fe379a29066aefff7c5b2`，logical `90e9a86870767253d7a2f43483f9ddd431f577d9da6516f3a6bac555478a9ade`；复用只读query_only helper实体复算为516表19270行，前后不变。四次preempt0→0，postflight为68MiB/0%、双栈9031关闭/无GPU进程，owned进程仅退出或Z；Attention前后54c。所检查日志无ERROR或shutdown-kill行。

运行次序是A1→async→metadata→A2，每个候选只有一次。A1/A2的KV差96tokens，时间变化只能描述，不能量化成严格匹配的漂移；同DB不保证Triton/主机缓存、其他CPU负载完全相同。metadata不能对A1声称0.86%严格收益。两项保留为小正信号，未新增准确率或正式两档重复，也不因百分比小就丢弃；达到默认集成仍需后继相称的确认与准确率资格。

原件位于`experiments/framework/`四个对应run及`-control`目录。机器可读审计在`analysis/2026-10-22-small-framework-comparison.json`；下列命令可只用本地stdlib重新生成stdout JSON，不改原始证据：

```powershell
python -X utf8 analysis/source/small-framework-pairs/recompute.py
```

同轮CTA边界：180033七阶段28份positive basic int16守卫文件均为−15992（BF16−17.0）、hash恒定；高级索引初始化尚未JIT就有12288异常，定位旧guard读法问题，不算correctness pass。180646修后正式两shape门11源SHA/64basic文件、8阶段/输出/输入/RNG/计时后均通过；gate-up单ABBA wall省16.17581577%、event省16.33245345%，down反而wall慢3.80726853%/event慢3.88480448%。仅固定tile synthetic fixture信号，旧失败和diagnostic保留；不能同时默认改两shape，也不是E2E/模型准确率证明。
