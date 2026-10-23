# 当前 Q/GQA 框架显存候选（仅 CPU）

本轮不实现、不上卡、不追加测试。已重读当前 runnercc442（核心6f）、workera8de、实际 CpuGpuBuffer 和旧 `analysis/2026-10-21-memory-lifecycle-feasibility.md`。旧图共享池、由大到小捕获、profiling finally 清理及一组42层共享的8.125MiB Attention scratch均已存在，不能重提为新增节省；Iluvatar是否执行图预估必须看实际平台guard，不能只看函数存在。

1. **NO-GO：strict text-only 不分配 inputs_embeds。** runner815无条件建立 `[max_num_tokens,inputs_embeds_size]` BF16 CpuGpuBuffer，actualutils121–131分别创建CPU zeros和GPU zeros_like。当前2048×2048时各8MiB。原1795/1844/1853/2025写入、3515/3539/3592正式消费者及5994–6007 dummy/capture消费者均由 MM 或 prompt-embeds 路径控制；`not supports_mm_inputs && not enable_prompt_embeds` 时正式和dummy都传 `inputs_embeds=None`，DP随机化也只在非None路径使用它。两flag要在真实ctor核实，不能只凭官方argv未出现该参数认false。保未知模型/flags原分配，不触合法embedding功能或算术。
   - 删除8MiB设备常驻及8MiB CPU/pinned初始化，不增加热路径GPU工作；不是首创，旧报告已列量级但未实施。本次新增的是具体consumer闭包与guard可落地证据。
   - **预算公式复核后直接否决，不另上卡。** a8de worker451先建init_snapshot、473才建runner并分配B；模型load的weights仅记其后增量。166/537 reset后before_profile peak已含B，565–567的`profile_peak-before_profile_peak`中B抵消；102–120的nonTorch为`(total-free)-memory_reserved`，同一Torch B也在两项抵消。595–599最终`available_KV=requested-(nonTorchIncrease+peakIncrease+weights)-graphEstimate`无直接B项。删8MiB仅减少实际占用与一次启动zeros，不删text热copy/kernel，不能兑现“多12KV块”；不将allocator舍入/噪声或调整预算公式当作优化收益。

2. **NO-GO：noSpec/no prompt-logprobs 的 full hidden-state 提早解除引用。** 原4445先索引出独立sample_hidden_states，4477仍把全 `[M,H]` hidden放ExecuteModelState并在sample4551采样期间强持；此scope的后续值消费者只有3818→5569立即返回空的prompt-logprobs路径。可理论缩短mixed M2048最多8MiB的寿命，保采样/event/快照而不裁模型计算。
   - 但纯decode graph的output引用及pool仍可能强持storage；sample函数闭包/spec/PP/pooling/aux都必须回原，profile_run又走独立dummy返回全hidden，所以只改真实state不会自动降低sizing峰值。无删除kernel或copy的证据，guard/状态改写反而有成本。不为此单独上GPU门；仅将来现有账本发现该storage确造成峰值重叠时再考虑一次mixed memory/alias验证。

**当前建议：无有据的大收益buffer实现可直接推进。** inputs_embeds与fullhidden两点均不追加设备门；root既定current两smoke只用于独立memory组成取证，这不是重开zeroing/KV capacity/图档位或旧swap。没有新service、accuracy、净吞吐或显存实测结论。
