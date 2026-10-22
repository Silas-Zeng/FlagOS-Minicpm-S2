# CPU metadata + async token 组合门：062205 实际结果

**方法级组合正确性门通过。** 唯一 GPU run `20261022T062205Z-cpu-combination-gate` 的五种形状共55项字段检查、四步连续 event/固定地址 graph consumer、CPU/GPU RNG 检查均通过。两项 helper 确在同一次 `_prepare_inputs → _prepare_input_ids` 调用链中执行；本轮没有加载模型权重、启动服务、计时或测整模型准确率。

## 实际覆盖

| case | tokens / requests | 11项字段检查 | metadata / async 选择增量 |
| --- | --- | --- | --- |
| decode62 | 62 / 62 | 全过 | 1 / 1 |
| mixed259 | 259 / 32 | 全过 | 1 / 0 |
| mixed952 | 952 / 32 | 全过 | 1 / 1 |
| mixed2048 | 2048 / 30 | 全过 | 1 / 0 |
| prefill2048 | 2048 / 1 | 全过 | **1 / 1** |

字段为 positions、seq_lens、num_computed_tokens、input_ids、query_start_loc、discard_request_mask、num_accepted_tokens、logits_indices、slot mapping、CPU mirrors 和固定地址。两组 mixed case 的 fixture 没有 previous sampled tokens，因此 async 增量为0；`prefill2048` 的 fixture 有 previous sampled tokens，单请求的目标位置并非 identity slice，真实 async 增量为1，不能沿用“单请求必绕过”的推测。case 名称不是纯无历史 prefill 的证明。

随后四步连续改变 host 状态，保留原 `synchronize_input_prep` event 生命周期，以固定源地址的图消费 positions、seq_lens、slot_mapping、input_ids；每步两项增量均为1，baseline与组合消费结果一致，positions和input IDs确实随步骤改变，未读到旧值。全部调用累计 metadata=9、async=7。CPU/GPU RNG 前后 SHA分别相同；metadata 不支持范围的回退断言也通过。图只含固定地址 tensor copy consumer，不是整模型 CUDA graph 覆盖。

## 来源和运行证据

原件位于 `experiments/framework/20261022T062205Z-cpu-combination-gate` 及对应 `-control`。本agent对完整原件做一次本地 stdlib 审计，**55个seal项目、10个source文件全部SHA一致**，之后复核无变；没有重跑 GPU 门或旧测试。

- launcher `d50511c9a194b1dadad87498b22862641cbea9643eea94aa73f32b320a6abb2f`，gate `abfc7981a8d5a20ff32b80f42dd30148bbeb5d680c649bf892e2b3924ead0bad`。
- 原 runner `e155a166...`、组合 runner `6f918ae6...`，metadata `0e961524...`、async `1bb85e31...`，与双序组合材料/受测单项原字节相符；实际 InputBatch、utils、block_table 依赖同固定pin。
- launcher/controller/worker PID分别为270063/270069/270073。只有内层controller持设备锁并管理一个GPU worker、monitor和清理，外层没有第二设备owner。
- 外层06:22:05.830235Z开始，06:22:26.210821Z exit0；controller也exit0。这只是生命周期时间，没有方法性能数据。
- 原环境为单天数BI-V150/32GiB、CPU配额6核、host上限20GiB；Torch `2.10.0+corex.4.5.0`、NumPy `1.26.4`、vLLM `0.24.0+empty`、flag-gems `5.3.5`。controller里`FlagGems=unavailable`及外层`triton=null`保留为发行包metadata查询原值，不解释为运行库缺失。
- DB前后均523表/19474行，实体文件、schema与logical三种SHA一致；已用冻结stdlib helper以只读/query_only重新计算schema、内容与表行数。物理 `dc2c76463fc6c1ef0674b16ca4374125b3ee4551fa0b1886253093f310b237da`，schema `0dc7a465bf12e53e054381d9e865460e7e4fe70287cc8c3683a41b0a4914ab39`，logical `c05d7e3182d1837929b48d5699c6515786351eb8d22f73eb53227a39fb3c49c8`。DB快照在controller设备锁外，依赖root独占串行条件，不伪称另有锁保护。
- 后态06:22:26.205563Z：68MiB/0%、GPU空进程表、9031 IPv4/IPv6均关闭，源码未变。worker首次选择标记各1条；原有Triton benchmarker回退/弃用warning保留，无Traceback/ERROR。

归档 `20261022T062205Z-cpu-combination-gate.tgz` 为2035183字节，SHA256 `225a853904047c7770c9adb1cb284fcd2d9c389ca50cbb94be5ddc174e0b1852`；SCP session43608实际exit0后才核整包并读本地。启动/归档命令及收集回执为 `analysis/source/cpu-combination/062205-collection-receipt.json`。唯一系统后验为 `analysis/source/cpu-combination/062205-system-review.json`（SHA `07c12b13f6b99a0df3621be3c1c36b30f2d0ea36d20daa49492973c0721113bf`）。

## 可以用于 PR 的结论

组合 runner 的两处真实方法在上述 fixture/实际buffer及block-table条件下通过同链设备正确性和固定地址异步消费检查，补足之前只有文本合并/AST的证据。适用于两个CPU Draft PR的组合说明；不证明完整scheduler/service dispatch、所有shape、模型准确率、C500或性能提升。旧单项短筛的收益不相加，旧SQL+C3的103/105不继承；本轮 `accuracy/end_to_end=not evaluated`、`timing=not measured`，不宣称最终提交资格或组合已默认启用。

registry第118条及queue第91项已登记；不自动追加服务、收益pair或官方大测。下一步由root/团队评审决定。
