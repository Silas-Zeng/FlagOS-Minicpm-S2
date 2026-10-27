# 当前实验与接续

更新：2026-10-27 05:56 UTC。BI-V150 当前唯一GPU任务是 LM-head温度融合候选的原官方4K对照；C500由队友独立维护。

| 版本／方法 | 已完成结果 | 资格与决定 |
|---|---|---|
| main56/native14f 原官方4K | 5036.45／5749.08／5908.26／6050.97 tok/s，弃首均 **5902.77**；1024请求成功，KV548432 | 当前4K对照；尚无同版本16K/105资格 |
| main241/native14f 既有完整结果 | 4K弃首5850.053333、16K4487.49 tok/s；105题104/105（99.047619%） | 保留原版本成绩；不迁移到main56，Q32/C3精度覆盖另列 |
| LM-head温度epilogue组件 | R64真实W＋合成hidden，10组门通过；完整head+Sampler Event省17.3138%、wall省12.2401% | 保留；不是整模型吞吐收益或105资格 |

main56为 `56f1838192abc940b3fb9accef490022ac125000`，来自团队PR66。本站native14f与队友native5cbb结果分别管理。相比旧main241，4K暖均观察+0.9011%，但KV548288→548432，不报严格因果收益。原官方请求成功也不能替代模型准确率。

**当前候选 B**：05:50:58 UTC启动，supervisor46614、owner46616。远端根目录 `/workspace/experiments/minicpm-s2/`：

- run：`official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds`；同名`-control/state.json`保存结果和清理状态。
- 入口：`scripts/head-temperature-official-23b56983`，读取`supervisor-launch.json`、最终`supervisor-final.json`与`launcher.log`；未确认结束前不另占GPU。
- 已完成A：`official/20261027T052425Z-main56-control-4k-four-rounds`，05:44:08结束，DB恢复、源码/native不变和清理通过。
- 候选仅809文件中的5项改动，生产包SHA `31094098…4825`，官方入口 `23b56983…2f46`，均独审通过；受测kernel字节不变，保持官方服务/benchmark参数。

候选只接已验证R64，显式传递本步采样状态；原stats/top-p/softmax/RNG不变，不适用条件走原路。组件A用UnquantizedLinearMethod，真实模型head为EmbeddingMethod；同底层F.linear已通过实际SDK源码核对，实际服务命中仍由日志确认。首暖低于本次A的5749.08可提前收尾；首暖正则跑满四轮，错误立即停止。当前尚无B性能结论，不发布为可合并收益。

**下一步**：回收B原结果；有收益再完成必要模型准确率/另一负载验证，按方法提中文代码PR。负结果同样保留，不因上传或合并重复已过检查。

[实验总表](team/experiments.md) · [当前对照及证据](team/methods/baseline-environment.md) · [LM-head方法](team/methods/lm-head-temperature.md) · [团队导航](team/README.md)。当前登记361条／358个唯一run。A的311份原件和组件的44份原件均逐SHA核验。

采样统计融合（逐位门失败）、S2同CTA（首次编译失败）、KV SoA、V转置、Q32双流、SiLU LUT等已停止，原件沿总表保留。旧main6971轨迹已分析，不重复profiling；未覆盖间隙0.4260%，暂无大额跨步CPU提交空洞依据，旧轨迹不作main56性能预算。

105题旧owner的Q32覆盖检查失败标记原样保留；独立复核的官方104/105成绩有效，但不声称验证了未命中的分支。SSH使用用户确认的网关指纹，严格校验，禁止网页UI操作，不记录凭据。
