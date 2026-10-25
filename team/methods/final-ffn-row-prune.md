<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 末层FFN/o_proj选行与模型对照

原FFN527及unbacked v3均遇mixed长题不完成；原main526同mixed也失败、精确同请求serial通过，不能归因选行，根因未确认。v3解决S1的AOT检查节点问题并通过三语义；不恢复模型资格、不进性能。原失败保留，不为通过候选强改框架。

相关代码：[results.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/results.json)；[state.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/state.json)；[archive-receipt.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/archive-receipt.json)；[results.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/results.json)；[state.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/state.json)；[archive-receipt.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/archive-receipt.json)；[state.json](../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/state.json)；[archive-receipt.json](../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T204020Z-final-ffn-row-prune](../runs/bi-v150/20261024T204020Z-final-ffn-row-prune.md)（登记#235）：实际mm_out logger未挂入记录链，守卫停止，无有效case；清理/DB恢复通过，不是数值或性能负结果。 **是否保留：** 保留首次失败；独立v2仅修日志，等待新run。
- [20261024T211402Z-final-ffn-row-prune-logger-v2](../runs/bi-v150/20261024T211402Z-final-ffn-row-prune-logger-v2.md)（登记#237）：四shape逐bit/变输入Graph通过；M2048→S32/64 Graph总wall约2.386→0.170/2.397→0.183ms，仅组件，不含dense回填。 **是否保留：** 保留局部正信号供模型接线，实际模型准确率/端到端收益待。
- [20261024T223346Z-final-ffn-row-model-verify](../runs/bi-v150/20261024T223346Z-final-ffn-row-model-verify.md)（登记#241）：FFN527四串行语义均正确但均fallback，随后真实mixed已选择M2048/S2；并发长prefill响应只见未闭合think，1024输出token耗尽/finish_reason=length，未得到85，模型门失败。22:37:26 UTCsource/native未变、DB恢复和清 **是否保留：** 保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。
- [20261025T062040Z-final-oproj-ffn-unbacked-model-verify](../runs/bi-v150/20261025T062040Z-final-oproj-ffn-unbacked-model-verify.md)（登记#246）：o_proj/FFN选行+S1 unbacked候选c09d8b93，原六请求门首个S1在AOT缓存检查因torch._check节点不支持而HTTP500；无模型/性能资格。原失败、FX保留，源/native未变、DB恢复/清理成功。仅移除图内重复约束的独立v3另测。 **是否保留：** 保留原始结果；模型门失败不进入性能验证，对照结论与候选收益分开。
- [20261025T063030Z-final-oproj-ffn-unbacked-model-verify](../runs/bi-v150/20261025T063030Z-final-oproj-ffn-unbacked-model-verify.md)（登记#247）：v3 tree1efc53c2仅去掉三条图内重复torch._check，保留模型外范围校验/AOT开启；S1长prefill95、加85、乘323及实际新图通过。真实mixed M2048/S2命中后长题仅<think>且1024token耗尽，复现旧527症状；未走最终S1回访，不进吞吐/105 **是否保留：** 保留原始结果；模型门失败不进入性能验证，对照结论与候选收益分开。
- [20261025T064055Z-final-row-main526-mixed-control](../runs/bi-v150/20261025T064055Z-final-row-main526-mixed-control.md)（登记#248）：原main526/tree8671、native14f及实际34native/backbone/AOT，原同mixed双请求未改；长题同样仅<think>且1024token耗尽。旧FFN527与新v3失败不能据此归因选行，仍无候选模型资格；源/native不变、DB恢复/清理成功。下一项仅将同长题 **是否保留：** 保留原始结果；模型门失败不进入性能验证，对照结论与候选收益分开。
- [20261025T064733Z-final-row-main526-exact-serial-control](../runs/bi-v150/20261025T064733Z-final-row-main526-exact-serial-control.md)（登记#249）：原main526/native14f单独提交同一个原始长请求（SHA b863ee85），4652输入/61输出token，答案85正确，原请求与采样不变；实际backbone/34native/AOT及源/native/DB/清理通过。结合064055同mixed失败，问题限于已测并发场景，根因未 **是否保留：** 保留原始结果；模型门失败不进入性能验证，对照结论与候选收益分开。
