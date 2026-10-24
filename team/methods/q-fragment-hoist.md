<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Q fragment 循环外保留

把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。

相关代码：[qfragment-pr15-pr21-final.json](../../analysis/qfragment-pr15-pr21-final.json)；[qfragment-adaptation.json](../../analysis/qfragment-adaptation.json)；[biv150_q_fragment_service.py](../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py)；[compare_q_service_pair.py](../../archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py)；[q-fragment-service-pair.json](../../analysis/q-fragment-service-pair.json)。

相关方法PR：[Q fragment #23](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/23)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261022T135941Z-q-fragment-hoist-gate](../runs/bi-v150/20261022T135941Z-q-fragment-hoist-gate.md)（登记#147）：wall11.028873859375→8.811432640625ms（缩短20.1058%），event10.930427551270→8.604556560516ms（缩短21.2789%），保留局部正信号待真实服务验证 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T152020Z-q-fragment-hoist-4k-gate](../runs/bi-v150/20261022T152020Z-q-fragment-hoist-4k-gate.md)（登记#148）：wall2.464499437500→2.067650000000ms（缩短16.1026%），event2.358253240585→1.871338784695ms（缩短20.6473%），保留短KV局部正信号待真实服务验证 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261022T153947Z-q-hoist-service-candidate-decode4k](../runs/bi-v150/20261022T153947Z-q-hoist-service-candidate-decode4k.md)（登记#149）：吞吐+1.711258%、wall缩短1.682467%、TTFT+1.318503%、TPOT-5.384107%；保留候选→基线一次配对的服务正信号，非稳定统计收益，不代表官方完整性能或模型准确率通过，TTFT本轮退化；不外推C500 **是否保留：** 保留作候选，仍待确认；不等于默认启用。
- [20261022T154518Z-cpu-combination-combined-decode4k](../runs/bi-v150/20261022T154518Z-cpu-combination-combined-decode4k.md)（登记#150）：吞吐+1.711258%、wall缩短1.682467%，TTFT+1.318503%、TPOT−5.384107%，非稳定统计或官方/准确率结论 **是否保留：** 保留作对照基线；不据此判断候选收益。
- [20261022T155446Z-q-fragment-hoist](../runs/bi-v150/20261022T155446Z-q-fragment-hoist.md)（登记#151）：Q fragment已测413源码首次完整Math500 Level 3：101/105（96.1905%）通过95%门 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261024T061556Z-pr15-pr21-qfragment-official](../runs/bi-v150/20261024T061556Z-pr15-pr21-qfragment-official.md)（登记#207）：第2–4轮均值4K5313.59、16K3764.67 total tok/s，较旧基线5118.99/3436.17为+3.80%/+9.56% **是否保留：** 保留并已合并PR23；确认为最新BI-V150基准，KV失配边界随结果保留。
- [20261024T071802Z-pr15-pr21-qfragment](../runs/bi-v150/20261024T071802Z-pr15-pr21-qfragment.md)（登记#208）：PR15+PR21+Q fragment完整Math500 Level3为100/105（95.2381%），满足>=100门 **是否保留：** 保留准确率通过证据及2题输出上限边界；组合已合并。
- [20261024T060209Z-qfragment-sourceproof-debug5-4k](../runs/bi-v150/20261024T060209Z-qfragment-sourceproof-debug5-4k.md)（登记#209）：前置debug3在normalized-over-gqa路径正确拒绝旧C2/源码行假设，fallback actual Q source location missing，候选未进入优化路径，不计性能负结果 **是否保留：** 保留适配失败/修复与选中证据；短诊断exit2，不作性能或准确率。
