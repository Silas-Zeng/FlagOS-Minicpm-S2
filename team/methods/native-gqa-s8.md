<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# native GQA S8生产接入

PR105 producer新增N30/S8；仅BF16且Q stride=2048命中，其余fallback。16K官方四轮正向、4K官方观察略负且KV不匹配；本批KV16K/4K两档局部组件正向。原105为101/105通过，但batch8的S8为not_exercised；保持PR105基线，不作严格因果、长度分流或新基线。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T014250520820Z-native-gqa-s8-hotspot-component](../runs/bi-v150/20261029T014250520820Z-native-gqa-s8-hotspot-component.md)（登记#480）：Event 1.029299→0.766297ms（快25.5515%），wall 1.032342→0.768814ms（快25.5272%）；以原始results.json及本轮短记为准，registry中wall数值为误抄。 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T033802216533Z-native-gqa-s8-hotspot-component](../runs/bi-v150/20261029T033802216533Z-native-gqa-s8-hotspot-component.md)（登记#482）：Event 1.0282070041→0.7649875879ms，省25.59985% **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T035018Z-native-gqa-s8-official16k-entry](../runs/bi-v150/20261029T035018Z-native-gqa-s8-official16k-entry.md)（登记#483）：失败，benchmark未开始 **是否保留：** 未集成；失败或无收益记录保留。
- [20261029T035651Z-native-gqa-s8-official16k-entry](../runs/bi-v150/20261029T035651Z-native-gqa-s8-official16k-entry.md)（登记#484）：失败，benchmark未开始 **是否保留：** 未集成；失败或无收益记录保留。
- [20261029T040113Z-native-gqa-s8-official16k-entry](../runs/bi-v150/20261029T040113Z-native-gqa-s8-official16k-entry.md)（登记#485）：失败，benchmark未开始 **是否保留：** 未集成；失败或无收益记录保留。
- [20261029T041010Z-native-gqa-s8-official16k-ready](../runs/bi-v150/20261029T041010Z-native-gqa-s8-official16k-ready.md)（登记#486）：官方入口因旧ready-marker reader误识别VLLM环境变量警告而失败；0个benchmark请求、无吞吐计时，不是模型数值错误。 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T043401Z-native-gqa-s8-16k-four-rounds](../runs/bi-v150/20261029T043401Z-native-gqa-s8-16k-four-rounds.md)（登记#487）：相对PR105暖均4832.66为+1.1275%，但KV为548384对548288，不作严格因果或新基线 **是否保留：** 待确认；通过某项检查不自动等于优化保留。
- [20261029T054720Z-native-gqa-s8-4k-four-rounds](../runs/bi-v150/20261029T054720Z-native-gqa-s8-4k-four-rounds.md)（登记#488）：4K四轮6161.33/6506.76/6723.79/6552.71 tok/s；暖均6594.42，对PR105 6627.82低0.5039%，KV548384对548336不同。 **是否保留：** 保留4K完整实测观察；KV不匹配，不作严格因果或基线更新。
- [20261029T061308Z-native-gqa-s8-native14f-math500](../runs/bi-v150/20261029T061308Z-native-gqa-s8-native14f-math500.md)（登记#489）：原105题101/105（96.1905%），达到至少100正确门；S8库安装有效但N30/S8 selected/captured均未出现。 **是否保留：** 准确率门通过；batch8未覆盖S8 kernel执行，不能据此称S8分支正确性已验证。
- [20261029T071002153051Z-native-gqa-s8-short-kv-component](../runs/bi-v150/20261029T071002153051Z-native-gqa-s8-short-kv-component.md)（登记#495）：KV16K Event 1.02895→0.76604ms，KV4K 0.27377→0.21720ms；wall两档均同步下降。 **是否保留：** 保留N30/S8组件正向观察；不授官方、准确率或长度分流资格。
