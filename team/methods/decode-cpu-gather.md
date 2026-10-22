<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 纯decode CPU gather跳过

严格纯decode省略无消费者的CPU输入整理；正确性门通过，当前服务候选负收益，不集成。

相关代码：[biv150_decode_cpu_gather.py](../../archive/ai/20261022-next-service-queue/next-decode-gather/biv150_decode_cpu_gather.py)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T112338Z-decode-cpu-gather-gate](../runs/bi-v150/20261022T112338Z-decode-cpu-gather-gate.md)（登记#131）：RNG门通过，selected metadata11/async16，gather skip6/fallback5 **是否保留：** 未集成；失败或无收益记录保留。
- [20261022T113627Z-decode-gather-service-candidate-decode4k](../runs/bi-v150/20261022T113627Z-decode-gather-service-candidate-decode4k.md)（登记#134）：吞吐-0.79831%，TTFT20339.6547ms **是否保留：** 未集成；失败或无收益记录保留。
