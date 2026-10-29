<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# native GQA S8生产接入

在PR105既有producer上接入N30/S8容量路径；仅BF16且Q stride=2048命中，其余fallback。组件测试有正向信号，16K官方四轮观察正向但KV548384对548288不匹配；4K与accuracy-105待测，不作严格因果或更新基线。勘误：登记#480把wall数值误写成Event数值；原始results.json及本轮短记记录wall 1.032342→0.768814ms（快25.5272%），本视图按原件显示，不改registry或原始证据。

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
