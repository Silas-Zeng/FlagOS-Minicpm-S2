<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 早期集成、块表与 profile

早期基点、块表提交、集成短筛和profile，不自动作为诊断开关或top-p单项性能。

相关代码：[framework](../../patches/framework)。

相关方法PR：[诊断配置 #5](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/5)；[top-p #7](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/7)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T032830Z-metadata-gate](../runs/bi-v150/20261021T032830Z-metadata-gate.md)（登记#5）：32 state steps and 3 graph replays pass **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T040856Z-native-decode](../runs/bi-v150/20261021T040856Z-native-decode.md)（登记#13）：JSON argv split by ixsys；service never ready；no model or candidate comparison **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T041625Z-native-decode](../runs/bi-v150/20261021T041625Z-native-decode.md)（登记#14）：Exit 0 and shutdown memory 68 MiB **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T042609Z-native-decode](../runs/bi-v150/20261021T042609Z-native-decode.md)（登记#15）：Exit 0 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T045834Z-b0-launch-pair](../runs/bi-v150/20261021T045834Z-b0-launch-pair.md)（登记#19）：16 completed；no speedup comparison to C2 decode-screen **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T045834Z-b0-launch-pair](../runs/bi-v150/20261021T045834Z-b0-launch-pair.md)（登记#20）：8 completed；no speedup comparison to C2 decode-screen **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T051639Z-b0-decode-screen](../runs/bi-v150/20261021T051639Z-b0-decode-screen.md)（登记#24）：64 completed；no stable speedup or official score **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T061506Z-host-gap](../runs/bi-v150/20261021T061506Z-host-gap.md)（登记#28）：Exit 0；no throughput comparison or accuracy claim **是否保留：** 待确认；通过某项检查不自动等于优化保留。

## 未记录

- [20261021T030349Z-b0](../runs/unrecorded/20261021T030349Z-b0.md)（登记#1）：16 completed **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T030349Z-b0](../runs/unrecorded/20261021T030349Z-b0.md)（登记#2）：8 completed **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T031102Z-c1](../runs/unrecorded/20261021T031102Z-c1.md)（登记#3）：16 completed **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T031102Z-c1](../runs/unrecorded/20261021T031102Z-c1.md)（登记#4）：8 completed **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T033437Z-b0-repeat-smoke](../runs/unrecorded/20261021T033437Z-b0-repeat-smoke.md)（登记#6）：Same temperature 0 seed 71 request **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T061506Z-host-gap-control](../runs/unrecorded/20261021T061506Z-host-gap-control.md)（登记#29）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
