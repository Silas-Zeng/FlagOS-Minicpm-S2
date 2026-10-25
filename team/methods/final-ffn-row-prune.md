<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 最后层FFN前精确选行

仅在末层FFN前按原GPU logits_indices同步选择hidden与residual，保留全部Attention/KV并dense回填供原runner采样。组件有逐bit与局部耗时信号，但527真实mixed已出现语义失败，不进入性能或代码PR；失败后FX只读取回，不追溯恢复资格。o_proj、pure-prefill与S1派生原型只封存，未上卡。

相关代码：[results.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/results.json)；[state.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/state.json)；[archive-receipt.json](../../experiments/framework/20261024T204020Z-final-ffn-row-prune/archive-receipt.json)；[results.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/results.json)；[state.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/state.json)；[archive-receipt.json](../../experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/archive-receipt.json)；[state.json](../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/state.json)；[archive-receipt.json](../../experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/archive-receipt.json)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T204020Z-final-ffn-row-prune](../runs/bi-v150/20261024T204020Z-final-ffn-row-prune.md)（登记#235）：实际mm_out logger未挂入记录链，守卫停止，无有效case；清理/DB恢复通过，不是数值或性能负结果。 **是否保留：** 保留首次失败；独立v2仅修日志，等待新run。
- [20261024T211402Z-final-ffn-row-prune-logger-v2](../runs/bi-v150/20261024T211402Z-final-ffn-row-prune-logger-v2.md)（登记#237）：四shape逐bit/变输入Graph通过；M2048→S32/64 Graph总wall约2.386→0.170/2.397→0.183ms，仅组件，不含dense回填。 **是否保留：** 保留局部正信号供模型接线，实际模型准确率/端到端收益待。
- [20261024T223346Z-final-ffn-row-model-verify](../runs/bi-v150/20261024T223346Z-final-ffn-row-model-verify.md)（登记#241）：FFN527四串行语义均正确但均fallback，随后真实mixed已选择M2048/S2；并发长prefill响应只见未闭合think，1024输出token耗尽/finish_reason=length，未得到85，模型门失败。22:37:26 UTCsource/native未变、DB恢复和清 **是否保留：** 保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。
