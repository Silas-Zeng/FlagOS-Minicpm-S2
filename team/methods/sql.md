<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# SQLite 反射及 SQL+C2/C3 组合

目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。

相关代码：[biv150_sql_reflection.py](../../patches/framework/biv150_sql_reflection.py)。

相关方法PR：[SQL反射 #8](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/8)；[3D decode #9](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/9)；[mixed Attention #10](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/10)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T064632Z-sql-reflection-screen](../runs/bi-v150/20261021T064632Z-sql-reflection-screen.md)（登记#32）：SQL/B0 single-pair throughput factor 2.788778380 and duration reduction 64.142005 percent；persistent tuning DB initial contents not snapshotted；no stable/official performance or new accuracy claim；其余限制见完整原登记 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T071554Z-b0-sql-pair](../runs/bi-v150/20261021T071554Z-b0-sql-pair.md)（登记#34）：SQL/B0 single-pair throughput factor 2.788778380 and duration reduction 64.142005 percent；persistent tuning DB initial contents not snapshotted；no stable/official performance or new accuracy claim；其余限制见完整原登记 **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T072153Z-sql-reflection-screen](../runs/bi-v150/20261021T072153Z-sql-reflection-screen.md)（登记#36）：versus B0 071554 throughput factor 2.795773385 duration reduction 64.231722 percent **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T073309Z-sql-decode-screen](../runs/bi-v150/20261021T073309Z-sql-decode-screen.md)（登记#39）：SQL+C2 only **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T073644Z-sql-decode-level3](../runs/bi-v150/20261021T073644Z-sql-decode-level3.md)（登记#41）：Exit 0 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T080656Z-sql-mixed-screen](../runs/bi-v150/20261021T080656Z-sql-mixed-screen.md)（登记#43）：SQL+C2+mixed original implementation **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T083031Z-sql-decode-context16k](../runs/bi-v150/20261021T083031Z-sql-decode-context16k.md)（登记#45）：SQL+C2 source073309；short screen only no new accuracy or official performance **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T083455Z-sql-mixed-context16k](../runs/bi-v150/20261021T083455Z-sql-mixed-context16k.md)（登记#47）：SQL+C3 source080656 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T084659Z-sql-decode-context16k-long](../runs/bi-v150/20261021T084659Z-sql-decode-context16k-long.md)（登记#49）：SQL+C2 source073309；not128request official fourround result/no new accuracy **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T085302Z-sql-mixed-context16k-long](../runs/bi-v150/20261021T085302Z-sql-mixed-context16k-long.md)（登记#51）：SQL+C3 source080656 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T085855Z-sql-decode-repeat-context16k-long](../runs/bi-v150/20261021T085855Z-sql-decode-repeat-context16k-long.md)（登记#53）：SQL+C2 source073309 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T090505Z-sql-mixed-level3](../runs/bi-v150/20261021T090505Z-sql-mixed-level3.md)（登记#55）：Exit0 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T110149Z-sql-mixed-innovation-base-context16k-long](../runs/bi-v150/20261021T110149Z-sql-mixed-innovation-base-context16k-long.md)（登记#60）：Exit0/32completed0failed524288in32768out **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T173003Z-c3-coverage-context16k](../runs/bi-v150/20261021T173003Z-c3-coverage-context16k.md)（登记#74）：EngineCore191286八周期快照与原log逐项匹配，末384calls/305metadata/250mixed/3000single-query-decode request-step/2241prefix及plan/759outside=25.3%，77unsupported单列，ob… **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T174402Z-baseline-decode4k](../runs/bi-v150/20261021T174402Z-baseline-decode4k.md)（登记#77）：post2026-10-21T17:47:39.922604+00:0068MiB0%双栈闭无GPU进程，owned退出或Z **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T175441Z-baseline-decode4k](../runs/bi-v150/20261021T175441Z-baseline-decode4k.md)（登记#80）：post2026-10-21T17:58:40.426636+00:0068MiB0%双栈闭无GPU进程，owned退出或Z **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T183543Z-baseline-context16k](../runs/bi-v150/20261021T183543Z-baseline-context16k.md)（登记#85）：32成功0失败/524288in4096out/120.484981575981s/4385.476040985142total/TTFT60874.430632247822ms；供CTA对照，KV521936不同于候选521840，描述比率不作严格容量归因，无新accuracy **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261021T184244Z-baseline-context16k](../runs/bi-v150/20261021T184244Z-baseline-context16k.md)（登记#87）：耗时观察范围120.48498157598到120.763262667693秒，相对跨度约0.23096745%，非稳定噪声统计估计；KV521936仍不同于CTA候选521840 **是否保留：** 保留作对照基线；不据此判断候选收益。

## CPU

- [20261021T072702Z-sql-cpu-gate](../runs/cpu/20261021T072702Z-sql-cpu-gate.md)（登记#38）：CPU only Python 3.12.11 and SQLAlchemy 2.0.48 **是否保留：** 待确认；通过某项检查不自动等于优化保留。

## 未记录

- [20261021T064632Z-sql-reflection-screen-control](../runs/unrecorded/20261021T064632Z-sql-reflection-screen-control.md)（登记#33）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T071554Z-b0-sql-pair-control](../runs/unrecorded/20261021T071554Z-b0-sql-pair-control.md)（登记#35）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T072153Z-sql-reflection-screen-control](../runs/unrecorded/20261021T072153Z-sql-reflection-screen-control.md)（登记#37）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T073309Z-sql-decode-screen-control](../runs/unrecorded/20261021T073309Z-sql-decode-screen-control.md)（登记#40）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T073644Z-sql-decode-level3-control](../runs/unrecorded/20261021T073644Z-sql-decode-level3-control.md)（登记#42）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T080656Z-sql-mixed-screen-control](../runs/unrecorded/20261021T080656Z-sql-mixed-screen-control.md)（登记#44）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T083031Z-sql-decode-context16k-control](../runs/unrecorded/20261021T083031Z-sql-decode-context16k-control.md)（登记#46）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T083455Z-sql-mixed-context16k-control](../runs/unrecorded/20261021T083455Z-sql-mixed-context16k-control.md)（登记#48）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T084659Z-sql-decode-context16k-long-control](../runs/unrecorded/20261021T084659Z-sql-decode-context16k-long-control.md)（登记#50）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T085302Z-sql-mixed-context16k-long-control](../runs/unrecorded/20261021T085302Z-sql-mixed-context16k-long-control.md)（登记#52）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T085855Z-sql-decode-repeat-context16k-long-control](../runs/unrecorded/20261021T085855Z-sql-decode-repeat-context16k-long-control.md)（登记#54）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T090505Z-sql-mixed-level3-control](../runs/unrecorded/20261021T090505Z-sql-mixed-level3-control.md)（登记#56）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
