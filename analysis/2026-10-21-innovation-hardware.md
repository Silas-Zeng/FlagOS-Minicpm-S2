# SQL 修复后的动态形状：两条可检验创新路线

2026-10-21。owner `/root/hardware_innovation`。本轮只读本地 actual 源码、原始证据及公开一手资料；无 SSH、GPU 或运行代码修改。中间工作及后续代码审阅见 `docs/agent-work/hardware_innovation.md`。当前官方吞吐由 root 独占，本文不报告新性能结果。

## 结论先行

先验证另一 owner 正在实现的 mixed token bucket；若它保留官方后三轮收益，优先理解收益来自首次调优还是持续计算。本文的两个后备是 **运行时行索引、无需按输入 M 生成 BF16 gather 源码**，以及 **真实 M 不变、配置按 tile 分组的投影 launch**。两者均针对动态 shape 的实现机制，而不升级框架或改变官方参数。第一项容易做逐位 gate，第二项改动和准确率风险较高。没有证据支持承诺数倍性能。

先前 `13.95s / 8 steps` 的 CPU profile 是修复前全库 SQL 反射的诊断；不能把它当新基线中仍可省的时间。SQL+C2+mixed 已独立通过 103/105；新 bucket 和本文两条方案均未继承此准确率。

## 已核实的源码与硬件边界

实际快照：

| 源码 | SHA256 | 挂点 |
|---|---|---|
| `experiments/profiles/20261021T061506Z-host-gap/source/libentry.py` | `414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025` | `ConfigCache` 213–228；`LibTuner.run` 986/1043；`LibEntry.run` 1611–1799 |
| `tmp/remote-source/decode-gap/index.py` | `47a7108bcf8424a96651021703f8731f1866a0e2eff88a1ac647e574ccf7e61d` | generator 412 起；overload key 619 起 |
| `tmp/remote-source/iluvatar_mm.py` | `4c2e23da2a6b65b89cbb8170967f14c5327d143e21137387f3907ccb4fcde090` | `mm_kernel` 50–203；`_launch_mm` 206 起 |
| `experiments/accuracy/20261021T090505Z-sql-mixed-level3/source/plugin/vllm_fl/worker/model_runner.py` | `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1` | `hidden_states[logits_indices]` 4435/4441 |

公开 [FlagGems 固定 revision 的 libentry](https://github.com/flagos-ai/FlagGems/blob/4df52d9168ac55c1c1061cefb4638c570292d896/src/flag_gems/utils/libentry.py) 支持相同的多层 dispatch 机制；本项目实际身份仍以上表快照为准。**SQL config、LibEntry kernel、generated Python module、Triton binary 是四层缓存**。ConfigCache 正命中会查两次 SQL，但 LibEntry 热命中直接 launch 编译后的 kernel，不再进入 LibTuner。不能据此主张每层每步都有两次 SQL。

[BI-V150 平台一手说明](https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu)给出 warp64、建议128字节对齐和平台租赁单卡32GB。当前实际 slice 为16SM/32GiB，适合避免无意义的小 kernel/metadata 工作，但这些规格没有证明服务现在是 launch-bound。原图内工具仍无法拆 graph 节点，不补写推测占比。

[Triton JIT 官方接口](https://triton-lang.org/main/python-api/generated/triton.jit.html)提供 `do_not_specialize`。本地 `LibEntry.key` 又确实对该类整数保留 i32/i64 类型而非数值，为下面运行时边界提供实现切口。官方 main 文档只证明接口机制，不冒充本机编译器能力门；本机版本仍为既有 Triton 3.6/CoreX。

## 方向一：只对最终 hidden gather 使用运行时行边界

runner 每步在模型输出后执行 `sample_hidden_states = hidden_states[logits_indices]`，随后才计算 LM head；这是 BF16 行拷贝，和已门验的 int32 sampled-token gather→scatter 不是同一位置。实际 index generator 把输入各维大小写进 Python/Triton 源码，overload key 也包含完整 `inp_shape`。因此 mixed partial chunk 的 M952、M259，以及其他新 M，都可能生成新的 BF16 索引模块；现有 DB 差分与此相符，但没有当步 stack/生成模块映射，仍属强机制推断。

候选在 runner 这一个明确边界提供 `gather_hidden_rows(hidden_states, logits_indices)`。首版只接单卡 BF16 二维 contiguous hidden、合法 GPU int32/int64 一维 logits_indices、无 spec/PP/aux/model feature；其他情况回原表达式。真正实现一个行 gather kernel，feature width 作为 constexpr，输入 row count 与输出 row count 用 `do_not_specialize` runtime 整数，保持输出 N×hidden_size 及原行顺序。输入边界用于合法索引修正/检查，不能沿用上次 M 的常量，也不能仅删除现有 arg_key。它不额外 padding 模型，不改变投影配置、Attention、KV、RNG 或采样行数。

这是“框架选定语义边界 + 实际新拷贝实现”，符合必须有实现变更的要求；不能只是改路由到现有 `index_select`。布局64/128线程等不先穷举，按128字节连续列取值设计一个版本即可。BF16 按原元素载入/存储，无浮点归约，正确实现应逐位相同，包括重复行、反序和边缘行。负索引若首版不支持应明确回退，不能静默截断或读错。

**最短设备门：** 在真实已有 runner 边界或独立实际 kernel 对 M259/952/2048、N16/29/64 的少量形状，比较全部元素 bitwise；另测重复/非排序 index、输入变化、跨 stream 生命周期，以及 shape259→952→259时单一 runtime specialization entry。随后只做同一进程两次匹配短负载，第二次看暖后是否仍有 wall/CPU 信号。不要先实现通用任意 rank indexing 框架。GPU owner 串行执行；本轮未写实现。

**反证和预算：** 当前 SQL 反射已修正，这里每步只调用一次。若新 M 代价只发生一次且首轮已覆盖，official skip1 后可能几乎零收益；热 gather 本身很小，不能把旧 int32 index 的秒级 SQL停顿套在这里。最多先保留低成本候选，只有真实暖后证据支持才扩大。

## 方向二：不扩大模型 M 的 tile 配置分组与运行时投影

另一 owner 的 bucket 会把模型真实计算 B 扩大，从而减少 M 形状。一个更难但可能避免额外逐行工作的后备，是模型和 Attention 仍执行原 M，仅投影 launch 的**配置选择**使用通用 tile-footprint 分组，kernel 接收原 M 运行时边界。实际 Iluvatar MM 普通 M 参数在 LibEntry key 中被精确特化；只粗化 `LibTuner.get_key` 并不能复用 Entry，且原 MM 有 `rm % M` 与真实 store mask，不能把传入 M 直接伪造为 bucket。

实现必须有一份受源码 guard 保护的新 launch/kernel：`M` 运行时、K/N/布局/accumulator和固定选定的编译 tile 为 specialization；grid 与 `rm%M`、mask 全部用真实 M。配置分组由模型无关的 M 范围和 kernel tile 定义，不能查询 benchmark 标签、并发64、是否某配置已暖或修改持久 DB行来选路。可先在两个已观察尾块区间各一个配置试验，不扫描整空间。实际改 launch/key 的代码才是候选，单纯导流至现有库不算实现。

**为什么仍有机会：** 同一个 tile配置下，259→384 或952→1024可能不减少 M 方向CTA数，而模型 bucket仍额外执行 embedding、RMSNorm、Silu、RoPE等行工作。真实M方案可保留减少配置数量的好处而省去这些额外行。相反，配置固定会丢掉原精确M的 autotune优势，拆分 K 或不同 BK 的选择又可能改变BF16输出。即使数学等价也不能承诺 bitwise或 accuracy继承。

**最短设备门：** 只对实际四投影 `(K,N)` 的 M259/952及同分组另一 M，原实现与候选同 dtype/权重/输入比较输出、有限性、峰值与计时；其中保留原配置时先证明真实行算术无回归。若局部结果不足以抵消新 launch/配置损失则停。若 mixed bucket 的官方后三轮本来无收益，也不为此投入新实现。只有本项接续后才需要新官方准确率。

**优先级：条件后备。** 当前已有16K长输出 mixed暖pair约4.97%信号，但没有证明剩余瓶颈是MM首次配置。先等新 bucket 同条件短测/暖后统计，比直接做第二套算子更便宜；本轮只留明确实现边界和反证。

## 不扩展的三个方向

- 不重复 prefill 编译开关、global graph pool、hidden prefix view；这些已存在或证据否定大收益。官方参数 FULL_DECODE_ONLY 原样。
- 不给 SQL 增加永久正/负配置缓存：数据库外部变化可见性会改变；最简单“单 get”也受 Entry热命中反证限制。SQL新建model写 `pool[name]`、读取 `pool[short_name]` 是一次冷反射可修的点，值得保留小修，但目前不是最大杠杆。
- 不删 `synchronize_input_prep` event。它保护复用的 pinned staging；[PyTorch2.10异步内存与图语义](https://docs.pytorch.org/docs/2.10/notes/cuda.html)要求保持正确的 stream/lifetime关系。尚无证据可安全省掉这个等待。

官方每档四轮丢第一轮，后续三轮仍可能遇到新shape，但“首次新shape快”绝不等价可计分收益。原DB快照、原始每轮CSV和运行source必须一起保留；不清库，不挑只暖候选的状态。本报告截至写入时无新设备验证、无新默认补丁、无新accuracy或official分数。

## 同轮 bucket 独立代码审阅

已对另一owner最终 `patches/framework/biv150_mixed_token_bucket.py` SHA `86b24f729cbb078cdd285e6b5aeccd503df190837e898883434f01915ada999d`、精确footer21074c…及 actual KV writer f18224…进行CPU独立审阅。determine只换物理backbone行数，metadata真实M、原slot尾-1、采样N保持；ContextVar finally恢复与原input-prep event生命周期均未被破坏。scope表述已明确包括纯prefill尾步。完整冻结前缀和footer都做hash，拒绝边界后任意suffix。没有发现阻断最短真实设备门的问题。

独立复跑轻量 `python analysis/source/mixed-token-bucket/check_contract.py` 的最终8项通过，包含wrapper合同及真实source/footer通过与扰动拒绝；它仍使用fake Buffer、_eligible=True，不能替代真实vLLM配置/Tensor/KV/accuracy/性能。逐项审阅、源码身份、两条已处理意见和验证局限全部保存在 `docs/agent-work/hardware_innovation.md`。通过CPU审阅仅授权准备隔离source的最短设备门，不是提交默认资格。

后续作者最终补一项`shared_kv_cache_layers`排除，模块SHA成为`d2620ff750beb3fab97f372d64a1ec0e5550ee133cc6ca33adb8ba3f43de4605`；本owner对照实际runner确认该单一guard补强正确，审阅结论延续到此最终版。

## 后继实现状态

root在本报告之后明确委派实现方向一。独立runtime/byte transformer/无权重GPU门已准备并经另一owner CPU审阅；详见 `analysis/2026-10-21-hidden-row-gather-implementation.md`。runtime109905…、transformer881f…，只在新隔离080656源中opt-in；尚未设备验证、未接默认或当前source。前文“未实现”描述研究时点，不能误读为后继文件不存在。方向二仍只有条件设计，未实现。
