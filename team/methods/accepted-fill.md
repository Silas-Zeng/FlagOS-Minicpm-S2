<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 省去无消费者的 accepted GPU fill

固定非推测Full路径保留CPU fill，省略无消费者的accepted-count GPU fill。064838→065325两侧32成功0失败，吞吐表观−0.235046%，但KV521840→521936不同，31门仅same_KV失败、gain=null；当前不集成，保留小负及失配证据。冷ENABLED后同Engine原CPU_METADATA_FIRST_SELECTED只证明首次prepare，不证明全程/GPU数值或新准确率。

相关代码：[accepted-fill-service-pair.json](../../analysis/accepted-fill-service-pair.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261023T064838Z-accepted-fill-baseline-context16k](../runs/bi-v150/20261023T064838Z-accepted-fill-baseline-context16k.md)（登记#190）：32成功0失败、exit0，104.147864725s、5073.402142188 total tok/s；与065325候选四端DB三SHA相同，但KV521840→521936不同，31门仅same_KV失败、gain=null **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261023T065325Z-accepted-fill-candidate-context16k](../runs/bi-v150/20261023T065325Z-accepted-fill-candidate-context16k.md)（登记#191）：吞吐表观−0.235046%、耗时表观增加0.235600%；KV521840→521936不同，31门仅same_KV失败、gain=null，不归因收益；不继承422准确率，保留代码与小负/失配证据 **是否保留：** 未集成；失败或无收益记录保留。
