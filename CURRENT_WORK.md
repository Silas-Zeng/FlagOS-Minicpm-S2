# 当前实验与接续

更新：2026-10-27 08:05 UTC。BI-V150 当前唯一GPU任务是原main56/native14f的16K四轮控制；LM-head温度融合4K组已完成，本组暖均+0.3109%。C500由队友独立维护。

| 版本／方法 | 已完成结果 | 资格与决定 |
|---|---|---|
| main56/native14f 原官方4K | 5036.45／5749.08／5908.26／6050.97 tok/s，弃首均 **5902.77**；1024请求成功，KV548432 | 当前4K对照；尚无同版本16K/105资格 |
| main241/native14f 既有完整结果 | 4K弃首5850.053333、16K4487.49 tok/s；105题104/105（99.047619%） | 保留原版本成绩；不迁移到main56，Q32/C3精度覆盖另列 |
| LM-head温度epilogue组件 | R64真实W＋合成hidden，10组门通过；完整head+Sampler Event省17.3138%、wall省12.2401% | 保留；不是整模型吞吐收益或105资格 |
| LM-head温度epilogue实际服务 | 4K四轮5081.15／5778.04／5988.09／5997.24，暖均5921.12 tok/s，较同版本A **+0.3109%** | 1024请求成功、同KV548432、真实kernel/原栈及清理通过；单组小收益，16K/105待验证 |

main56为 `56f1838192abc940b3fb9accef490022ac125000`，来自团队PR66。本站native14f与队友native5cbb结果分别管理。相比旧main241，4K暖均观察+0.9011%，但KV548288→548432，不报严格因果收益。原官方请求成功也不能替代模型准确率。

**当前16K控制 A**：07:58:34 UTC启动，owner54135、driver54139；run `official/20261027T075834Z-main56-control-16k-four-rounds`，control同名加`-control`，入口 `scripts/main56-control-16k-d2ca829f/launcher.log`。启动前GPU/9031空闲，原官方负载 `[[16384,1024,64,128]]` 四轮。远端根目录 `/workspace/experiments/minicpm-s2/`。

已完成4K候选B：

- run：`official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds`；同名`-control/state.json`保存结果和清理状态。
- 入口：`scripts/head-temperature-official-23b56983`；06:10:37 UTC owner46616/supervisor46614退出0，完整四轮、源码/native/DB恢复和清理通过。340份原件逐SHA归档。
- 已完成A：`official/20261027T052425Z-main56-control-4k-four-rounds`，05:44:08结束，DB恢复、源码/native不变和清理通过。
- 候选仅809文件中的5项改动，生产包SHA `31094098…4825`，官方入口 `23b56983…2f46`，均独审通过；受测kernel字节不变，保持官方服务/benchmark参数。

候选只接已验证R64，显式传递本步采样状态；原stats/top-p/softmax/RNG不变，不适用条件走原路。真实模型ParallelLMHead已命中受测kernel及原采样链。4K首暖+0.50%后跑满，暖均+0.3109%；对应轮耗时−0.3241%、TTFT−0.4531%、TPOT−0.3088%，不外推组件收益或夸大为稳定提升。

**下一步**：完成同版本16K A/B与必要原105准确率验证；保留R32组件后备，不并发占卡。确认收益及正确性后按方法提中文代码PR，当前尚未合并本优化。负结果同样保留，不因上传重复已过检查。

[实验总表](team/experiments.md) · [当前对照及证据](team/methods/baseline-environment.md) · [LM-head方法](team/methods/lm-head-temperature.md) · [团队导航](team/README.md)。当前登记362条／359个唯一run。A的311份、组件的44份及4KB的340份原件均逐SHA核验。

采样统计融合（逐位门失败）、S2同CTA（首次编译失败）、KV SoA、V转置、Q32双流、SiLU LUT等已停止，原件沿总表保留。旧main6971轨迹已分析，不重复profiling；未覆盖间隙0.4260%，暂无大额跨步CPU提交空洞依据，旧轨迹不作main56性能预算。

105题旧owner的Q32覆盖检查失败标记原样保留；独立复核的官方104/105成绩有效，但不声称验证了未命中的分支。SSH使用用户确认的网关指纹，严格校验，禁止网页UI操作，不记录凭据。
