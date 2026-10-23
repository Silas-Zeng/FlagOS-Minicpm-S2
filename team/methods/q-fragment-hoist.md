<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Q fragment 循环外保留

同一方法的KV16K/4K局部门与真实服务配对分别记录；保留单轮正信号，TTFT变化及准确率边界同时展示。

相关代码：[biv150_q_fragment_service.py](../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../analysis/q-fragment-service-pair.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T135941Z-q-fragment-hoist-gate](../runs/bi-v150/20261022T135941Z-q-fragment-hoist-gate.md)（登记#147）：wall11.028873859375→8.811432640625ms（缩短20.1058%），event10.930427551270→8.604556560516ms（缩短21.2789%），保留局部正信号待真实服务验证 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T152020Z-q-fragment-hoist-4k-gate](../runs/bi-v150/20261022T152020Z-q-fragment-hoist-4k-gate.md)（登记#148）：wall2.464499437500→2.067650000000ms（缩短16.1026%），event2.358253240585→1.871338784695ms（缩短20.6473%），保留短KV局部正信号待真实服务验证 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T153947Z-q-hoist-service-candidate-decode4k](../runs/bi-v150/20261022T153947Z-q-hoist-service-candidate-decode4k.md)（登记#149）：吞吐+1.711258%、wall缩短1.682467%、TTFT+1.318503%、TPOT-5.384107%；保留候选→基线一次配对的服务正信号，非稳定统计收益，不代表官方完整性能或模型准确率通过，TTFT本轮退化；不外推C500 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T154518Z-cpu-combination-combined-decode4k](../runs/bi-v150/20261022T154518Z-cpu-combination-combined-decode4k.md)（登记#150）：吞吐+1.711258%、wall缩短1.682467%，TTFT+1.318503%、TPOT−5.384107%，非稳定统计或官方/准确率结论 **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T155446Z-q-fragment-hoist](../runs/bi-v150/20261022T155446Z-q-fragment-hoist.md)（登记#151）：Q fragment已测413源码首次完整Math500 Level 3：101/105（96.1905%）通过95%门 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
