<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# native GQA S8与shared4k组件

PR105原S8官方观察与本批局部组件结果分开：已有官方16K暖均相对PR105观察+1.1275%、4K−0.5039%，两档KV条件均不匹配；原105为101/105，S8分支未被batch8触发。本批N30/S8 short-KV与shared4k组件局部正向，live-acc不同候选负向，shared4k另有入口失败和CPU compile-only；这些组件不授官方、模型或新生产资格。

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
- [20261029T071002153051Z-native-gqa-s8-short-kv-component](../runs/bi-v150/20261029T071002153051Z-native-gqa-s8-short-kv-component.md)（登记#495）：两档组件Event均有明显下降；本结果不等同端到端官方吞吐。 **是否保留：** 保留局部正信号；不授生产、官方或完整S8准确率资格。
- [20261029T081824131260Z-native-gqa-s8-short-kv-component](../runs/bi-v150/20261029T081824131260Z-native-gqa-s8-short-kv-component.md)（登记#497）：两档组件Event均有明显下降；本结果不等同端到端官方吞吐。 **是否保留：** 保留局部正信号；不授生产、官方或完整S8准确率资格。
- [20261029T101441Z-linear-n64-short-capture](../runs/bi-v150/20261029T101441Z-linear-n64-short-capture.md)（登记#501）：本次采集未观察到可用目标调用；不是全局不存在该调用的证明。 **是否保留：** 保留无观察诊断；不转为性能或实现结论。
- [20261029T102212246584Z-native-gqa-s8-shared4k-short-kv-component](../runs/bi-v150/20261029T102212246584Z-native-gqa-s8-shared4k-short-kv-component.md)（登记#502）：两档Event与wall均正向；这是局部组件信号。 **是否保留：** 保留组件候选观察；不声称官方收益/模型资格，不修改生产代码。

## CPU

- [20261029T075911Z-native-gqa-s8-source-build](../runs/cpu/20261029T075911Z-native-gqa-s8-source-build.md)（登记#496）：CPU build-only完成；产物身份可供后续组件参考，不含GPU验证。 **是否保留：** 保留为构建/身份记录，不视为性能或生产资格。
- [20261029T095247685623Z-s8-shared4k-compile-entry-failed](../runs/cpu/20261029T095247685623Z-s8-shared4k-compile-entry-failed.md)（登记#499）：入口工具失败，不代表候选源码编译/数值/性能失败。 **是否保留：** 保留失败原件，后续LF修复后独立重试。
- [20261029T095425907993Z-s8-shared4k-compile](../runs/cpu/20261029T095425907993Z-s8-shared4k-compile.md)（登记#500）：编译成功、spill为0；这只是compile-only机制证据。 **是否保留：** 保留编译产物，等待独立组件数值与性能结果。
