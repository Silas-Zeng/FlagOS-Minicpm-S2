<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Attention 分流与 launch

prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。

相关代码：[framework](../../patches/framework)。

相关方法PR：[prefill #6](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/6)；[3D decode #9](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/9)；[mixed Attention #10](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/10)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261021T035322Z-attention-dispatch](../runs/bi-v150/20261021T035322Z-attention-dispatch.md)（登记#11）：bitwise equal **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T035611Z-mixed-dispatch](../runs/bi-v150/20261021T035611Z-mixed-dispatch.md)（登记#12）：Original decode path: full-chunk latency reduction below 1 percent **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T044807Z-decode-launch](../runs/bi-v150/20261021T044807Z-decode-launch.md)（登记#17）：bitwise equal **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T050517Z-c2-decode-screen](../runs/bi-v150/20261021T050517Z-c2-decode-screen.md)（登记#21）：64 completed；no stable speedup or new accuracy **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T051426Z-mixed-fast](../runs/bi-v150/20261021T051426Z-mixed-fast.md)（登记#22）：bitwise before/after timing **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T054501Z-mixed-gate](../runs/bi-v150/20261021T054501Z-mixed-gate.md)（登记#25）：bitwise with maxdiff 0 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T054922Z-c3-mixed-screen](../runs/bi-v150/20261021T054922Z-c3-mixed-screen.md)（登记#27）：64 completed；no stable/official performance or accuracy claim **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T113727Z-mixed-attention-overlap-gate](../runs/bi-v150/20261021T113727Z-mixed-attention-overlap-gate.md)（登记#66）：bitwise/padding/KV/RNG pass fallbackpass **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261021T114553Z-mixed-attention-overlap-gate](../runs/bi-v150/20261021T114553Z-mixed-attention-overlap-gate.md)（登记#68）：Independent14sourceSHA **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T120226Z-prefill-w16-gate](../runs/bi-v150/20261022T120226Z-prefill-w16-gate.md)（登记#136）：wall11.089565→14.605917ms（慢31.7087%），event10.983371→14.497282ms（慢31.9930%） **是否保留：** 未集成；失败或无收益记录保留。

## 未记录

- [20261021T035155Z-attention-dispatch](../runs/unrecorded/20261021T035155Z-attention-dispatch.md)（登记#10）：IsADirectoryError hashing source/__pycache__ **是否保留：** 未集成；失败或无收益记录保留。
- [20261021T044807Z-decode-launch-control](../runs/unrecorded/20261021T044807Z-decode-launch-control.md)（登记#18）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T051426Z-mixed-fast-control](../runs/unrecorded/20261021T051426Z-mixed-fast-control.md)（登记#23）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
- [20261021T054501Z-mixed-gate-control](../runs/unrecorded/20261021T054501Z-mixed-gate-control.md)（登记#26）：启动或收集记录，实验结果见对应主run。 **是否保留：** 保留作过程记录。
