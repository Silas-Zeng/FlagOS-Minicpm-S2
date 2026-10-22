# 社区机制：有依据的 A＋B 候选

2026-10-22，team_view_final_check；仅本地源码与公开资料研究，未安装、未上卡。当前 BI-V150 的 2D Attention 60.2339%、GEMM 31.7161% 是三步可见 kernel 时长占比，不能当全程吞吐占比。w16、V-late 及既有 tile/stage 单点负结果只否定各自已测配置。

## 1. 优先：V-late＋显式保留原 cache 偏好

**机制与出处：** [FlagTree iluvatar driver.c](https://github.com/flagos-ai/FlagTree/blob/main/third_party/iluvatar/backend/driver.c) 的 `loadBinary` 仅在 `shared > 49152 && shared_optin > 49152` 时设置 `CU_FUNC_CACHE_PREFER_SHARED` 及动态 shared 上限。因此 64→恰好 48 KiB 可能同时改变资源用量与装载设置，现有 V-late 慢 1.45% 尚未隔离这两个因素。此线索由 hardware owner 提出，本次独立核到了同一源码条件。

**最短验证：** 先核实际安装后端及真实函数属性。只有现场分支相同且 cache 设置确实可控，才在同一 V-late binary 上单独恢复 baseline 的 cache 偏好，复用当前 D1/P2047 门及可比基线；不改变 tile/stage，不重新宽扫。若 installed 分支不同、属性不可观测/无法可靠复原，或设置后编译/正确性异常，停止本分支。

**证据边界：** 这是同后端源码机制；尚不能证明 Corex 对该枚举的实际效果，更不能由 shared 48 KiB 推导常驻 CTA 翻倍。实施与资源核验由 hardware owner 维护，避免重复准备。

## 2. 框架备用：按 context 成本分配 prefill＋保持总 M

**机制与出处：** [vLLM 当前 scheduler](https://github.com/vllm-project/vllm/blob/main/vllm/v1/core/sched/scheduler.py) 已有单请求不限额、多人时按 fair share 给长 prefill 上限设下界的逻辑；[SGLang 动态 chunking](https://github.com/sgl-project/sglang/blob/main/docs/docs/advanced_features/pipeline_parallelism.mdx) 用 prefix 长度预测下一 chunk 成本，并按页/执行粒度对齐。后者针对多卡 PP 消除流水气泡，不能将其收益外推到单卡 BI-V150；仅借鉴“相同 token 数不代表相同 Attention 成本”。

**拟改动：** 保持官方总预算 2048、请求输出参数与原 KV 准入/释放不变。至少两个 prefill 可合法参与时，以 CPU 已有 `num_computed_tokens` 和剩余输入估计 `q*c+q*(q+1)/2`，在当前总预算内分配 chunk；余量回填，避免 GEMM 的总 M 缩小。保留自然 decode 前缀与现有 C3 分流；只有一个 prefill 或无法填足预算时走原策略。改变的是框架分配算法，不是改 CLI threshold、启用量化/spec 或更新框架分支。

**挂点与已有边界：** 现场保存的 `experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/sched/scheduler.py`，SHA256 `df78076164fe02a63876d7690cefac810f1ba4d8fb58afc15e786c1608064090`：`schedule` 的 running/waiting 两处 `num_new_tokens` 计算，均在 `allocate_slots` 前。须在 EngineCore 初始化前挂接；当前 `AsyncSchedulerFL` 只服务 MTP=1，不能把改动放进去后误认为无 spec 的真实服务会命中。现有 C3 `_prefix` 已支持 decode 前缀后多个 prefill，需复用其 scope，而非再造一个路由。此策略不同于已失败的 future-output growth admission；后者保留 FCFS 并按未来输出页数延缓准入。

**最短判别与停止条件：** 先对实际调度对象做 CPU 回放，确认出现至少两个 eligible prefill；逐步核总预算、无 token 遗漏/重算、异步 placeholder、FCFS 有界等待和原 KV 分配失败路径。若真实负载无此机会，直接停止。通过后用既有 16K/1024 输出/32 请求完整短 screen，记录完整完成时间、重算/抢占、KV 容量与 DB；不可用单层较快冒充全部任务更快。

**关键风险：** 总 causal Attention 工作量不会凭分块减少；多 chunk 还可能重复读取旧 KV，提前准入增加 KV 压力。它只可能改善执行分布与混合批次效率，不保证吞吐。若只改善 TTFT、总完成时间不改善，或引入饥饿/额外抢占，则不集成；6 CPU 下新增调度遍历也须计入。当前只有调研结论，未形成可部署实现，优先级低于第 1 项及在测 GPU 主线。

## 后续筛选：本轮无推荐上卡项

2026-10-22，按“先判断能否省掉真实工作，再决定实现”的最新要求收束。第 1 项已由 `20261022T130457Z` 三臂门否定当前点：cache B 比原版 wall 慢 1.49883%，比 V-late A 慢 0.27180%；API 接受设置不等于硬件生效。第 2 项只重分配相同 causal 工作，当前没有足以预测净收益的依据，暂不实现或组合。

唯一深入核过的框架候选是**跳过未完成 chunked prefill 的 LM-head 与采样行**。当前 `model_runner.py`（SHA256 `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`）第 2234–2241 行明确为每请求取一行，即使该请求未完成 prefill；第 4445–4446 行仍计算 logits，随后丢弃无效输出。理论上可删除无消费者的词表投影及采样，不改模型、输入、输出参数或 Attention/KV 计算。

但**本轮不推荐实现**。既有 native 窗口仅见三步 D1/P2047：保留 decode 时，删一行不会省掉整个 LM-head 权重读取与 kernel launch，2→1 行是否降低设备时间未知；6 CPU 上还会增加筛选与异步行映射成本。三次 `linear_kernel` 共 2.529487 ms（可见 kernel 时间的 0.2379%）尚未完成调用归属，不能据名字认作可全部删除的 LM-head。已有 sampler 分类 0.0426% 也不是全部采样成本的上界。当前源码还会回退被丢弃行的请求专用 RNG offset；直接压缩行可能改变全局 RNG 消耗、有效请求采样和 `prev_req_id_to_index`，并非安全删除一个索引即可。

社区一手核实：[vLLM GPU sampler](https://github.com/vllm-project/vllm/blob/main/vllm/v1/worker/gpu/sample/sampler.py) 的 `Sampler.__call__` 仍先 `sample`，再按 prefill 是否完成生成 `num_sampled`，没有提供可直接回移的“跳过整行”实现；[SGLang result processor](https://github.com/sgl-project/sglang/blob/main/python/sglang/srt/managers/scheduler_components/batch_result_processor.py) 的 `_validate_pp_skip_output_comm` 只核全中间 chunk 时省去 PP 输出通信，不能当作单卡计算收益证据。

最低成本否决条件：只读既有调度/采样状态，若不能证明存在可整段省去 LM-head/采样的纯中间 prefill，或不能在不新增 GPU 同步、保留原 RNG 与异步行映射的前提下给出删除路径，就不进入实现与上卡队列。当前只有 mixed 窗口，尚不足以证明这一正收益前提；这是否决当前投入，不是宣称所有负载绝无收益。本轮未写实现、未运行 GPU、未新增性能结论。
