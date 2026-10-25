# 当前 main526 热点诊断准备

登记到249条及本地已有trace中，未找到 main526/0bf9＋native14f 的有效完整kernel/API轨迹。114500已因旧AOT/native0失效，192308属于旧414源码；两者都不能给当前版本预算。现有34native图、GQA调用频数和组件时长不能替代服务时间线。

拟用原官方服务CLI，在独立诊断源码仅追加观察模块，保留runner/P/Q/native原文件。不能沿旧footer直接追加runner：当前compute-order严格核runner SHA，追加会改变实际路径。旧Core一次安装与managed_inference_mode守卫可复用，外加真实图/指纹/AOT绑定，避免仅核Python绑定。

先跑一次16384输入、1024输出、c64、64请求，seed721201，复用原诊断load脚本；这是少量请求诊断，不是官方成绩。此前出现2个普通mixed M2048后取mixed4步，随后稳定同IDs的2个decode暖步后取FULL8步。记录自然N/M变化；边界sync扰动首两步，CPU时间仅作关联，设备预算取trace时钟。没有目标窗则保留缺口，不强制改调度或关闭Graph。4K是否补测由16K证据决定。

本机ixsys已核语法为 `ixsys -t cuda --profile-from-start off --print-kernel-args -o <独立trace> <原服务命令>`。混合窗能拆可见Attention/native GEMM/搬运；FULL仅确认整图与图外活动，当前没有已验证图内节点采集命令。CPU gap需CPU提交/API与设备活动共同支持，不能直接把未覆盖区间叫CPU瓶颈。同步/日志/profiler开销单列，不进官方基线。

入口复用已通过的baseline owner/资格/真实图门/6秒清组；先TERM本次ixsys的vLLM子进程，等待45秒flush，再走清理、DB恢复。基线真实来源为`/workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official`。诊断527源只追加observer及init接线，指纹随之变化，实际新backbone/AOT仍须34 native。CPU检查及独立窄审随包保存；这些不是设备资格或数值成绩。

主智能体将entry解压到独立入口目录，再将source.tar解压到新的code目录；禁止覆盖既有源码。最短运行命令：

```bash
python3 verify_service.py --source-dir /workspace/experiments/minicpm-s2/code/current-main-hotspot-20261025 --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control --input-len 16384
```

结果位于`/workspace/experiments/minicpm-s2/profiles/<UTC>-current-main-hotspot-16384`及其`-control`。先看`result.json`、`trace-validation.json`、`hotspot-events.jsonl`、`model-path/evidence.json`及原始`native-trace.sqlite`。服务PID为`service.pid`，ixsys为`server.pid`，owner/state给出全部所属PID。owner已执行finally后不再启动负载。分析可见kernel/API/搬运与整图跨度；GPU空白只能在相关CPU/API证据支持时归因CPU等待，不能直接作吞吐收益。

来源与能力依据：`../pr25-fullsize-screen/next-hotspot-diagnostic-plan.json`、`../pr24-resume-native-v2`、`../q-gqa-puredecode-native`。旧PR24 owner/旧AOT轨迹不直接复用。
