# CPU metadata与async token组合的框架语义审阅

本次只读审阅未发现两方法之间新增的共享缓冲区、事件或stream顺序冲突。async token不读取CPU metadata省去更新的三个私有GPU镜像；两方法在真实调用链中顺序执行，写入不同GPU缓冲区，并受原输入准备事件保护。**这支持进入一个最短组合正确性门，不代表组合已上卡、准确率通过或收益可以相加。**

本轮没有修改PR、候选代码、共享checkout或Git对象，没有重做文本合并、运行测试套件、加载Torch/Triton、SSH、GPU或网络操作。root负责设备与后续取舍。

## 固定审阅对象

| 对象 | 实际路径 | SHA256 |
| --- | --- | --- |
| 组合runner | `docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py` | `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141` |
| CPU metadata helper | `docs/pr-preparation/cpu-metadata/files/vllm_fl/patches/biv150_cpu_metadata.py` | `0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f` |
| async token helper | `docs/pr-preparation/async-token-update/files/vllm_fl/patches/biv150_async_token_update.py` | `1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc` |
| 可复用的174115原方法门 | `experiments/framework/20261021T174115Z-cpu-metadata-gate/source/gate.py` | `b1240720b588dae25d92cc1c173d64c1ea5f6e34fcdcab5dd0156407ebbcb757` |

以上SHA已在本轮实际重算。此前双向合并、逆变换及方法体字节相等的证明引用 `docs/pr-preparation/combination-review.json`；本轮不重复该工作。

## 真实顺序与依赖

以下行号均指固定6f918 runner。

`execute_model` 在4172–4222行进入原 `synchronize_input_prep()`，先 `_update_states`，再 `_prepare_inputs`。输入准备内部顺序为：

1. 1983–1995行用CPU scheduled数量生成 `req_indices`、`query_pos.np` 的局部位置、`cu_num_tokens` 与 `positions_np`；2019–2024行仍按原方式准备 `input_ids.cpu`。
2. 2073–2095行准备query起点、CPU optimistic seq长度及 `prev_positions.np` 映射。2175–2178行的computed计数H2D仍保留。
3. 2181行调用CPU metadata helper。成功时只新增/复用位置pinned staging，写 `positions` 与 `seq_lens` GPU缓冲，更新 `req_indices.np`、`num_scheduled_tokens.np` 两份CPU镜像。
4. 2199–2203行原 `compute_slot_mapping` 消费query起点与位置GPU值；2206–2211行随后调用真实 `_prepare_input_ids`，其1879行才可能调用async token helper。
5. 原preprocess范围还会构造Attention metadata和模型输入，4372行退出上下文；事件在 `finally` 中record。模型forward在其后沿原执行路径消费同一批输入。

async token的索引来源是 `_prepare_input_ids` 的局部 `cu_num_tokens`、`prev_positions.np`、请求ID映射及原 `scheduled_spec_decode_tokens`。`prev_positions.np` 来自 `_compute_prev_positions`，不是 `req_indices.gpu`。两份int64索引仍在1872–1877行由原CPU列表新建并H2D，然后才启动融合kernel。它的四个GPU操作数仅为上一批 `prev_sampled_token_ids`、本批 `input_ids.gpu` 和这两份新索引。

| 存储 | metadata成功路径 | async token路径 | 组合判断 |
| --- | --- | --- | --- |
| `positions`、`seq_lens` | H2D写入原固定地址 | 不读取/写入 | 无新增交叉写 |
| metadata持久pinned位置staging、`optimistic_seq_lens_cpu` | CPU写/H2D源 | 不使用 | 无索引staging复用 |
| `req_indices.np`、`query_pos.np`、`num_scheduled_tokens.np` | 前两阶段仍按原值生成/更新 | 使用独立的局部cumsum及prev映射，不读取其GPU镜像 | 省去H2D不切断依赖 |
| `req_indices.gpu`、`query_pos.gpu`、`num_scheduled_tokens.gpu` | 严格scope中允许保留旧值 | 完整方法与helper均不读 | 不能因名字相似误认索引依赖 |
| `input_ids.gpu` | 原公共逻辑准备CPU值；metadata helper不碰GPU值 | 原必要H2D后写采样token | 原H2D→覆盖次序保留 |
| `prev_sampled_token_ids`、两份新int64索引 | 不使用 | kernel只读 | 与metadata数据分离 |

固定runner初始化分别分配input IDs、positions、seq长度与辅助buffer（780–805行）；metadata的staging单独分配，async索引也每次单独分配。两helper各自的描述守卫保持原件：metadata要求三个主要GPU存储互不别名，async要求四个操作数存储互异、CPU目标唯一及索引合法。以上是固定真实对象/分配链的结论，不是对任意人为重绑runner成员的通用别名证明。

## 事件、stream与回退

原 `synchronize_input_prep` 在3842行先等待上一次prepare事件，才允许下一步修改复用CPU张量；3846行在 `finally` 中记录当前流事件。两helper都不切换stream，故位置/seq H2D、原slot计算、input IDs必要H2D、索引H2D和整数kernel按当前流次序提交。事件record在两helper之后，覆盖新pinned staging与原CPU源的本次H2D消费；将后一个kernel纳入此范围没有削弱保护。

async helper的 `record_stream` 只延长上一批采样token、目标及临时索引的分配器生命周期，不能当作producer就绪同步。原采样与输入准备沿原current stream；输出D2H另在copy stream通过 `wait_stream(default_stream)` 等待原采样生产（326–342行），没有把token生产移到该copy stream。组合不改变这些producer关系。若调用者另行换流，仍须保留原caller就绪约束；本组合不承诺支持无wait的任意跨流调用。

identity-copy、无previous/common以及不支持的spec/embeds等路径仍可能不进入async helper。这不是组合失败，但上卡验收不能仅看安装或FIRST marker。metadata也可能先成功而async按原守卫回退；反过来亦可，两者没有共同开启条件或失败重试协议。已经提交后的异常仍传播，不在部分修改后重试旧路径。

两个helper遇到当前流capture都退原路；正常 `FULL_DECODE_ONLY` 模式下，preprocess在图消费之前运行。建议门中的graph只是从固定地址复制数据的consumer，不应捕获整个带CPU事件等待的输入准备方法，也不能称已验证完整模型图执行。

## 最短充分的下一设备门范围（尚未执行）

复用174115真实方法门的对象、五个真实方法抽取及实际 `CpuGpuBuffer` / `MultiGroupBlockTable`，固定原e155作oracle、6f918作候选，加载两份原helper。**不增加模型权重、服务、profiling或计时循环。**

- 旧fixture的 `model` 缺 `is_encoder_decoder`。必须仅补 `False` 使原async守卫可达；否则helper会抛属性错误，或人为绕过helper形成假门。保持其余配置/source身份守卫，不mock成“自动selected”。
- 可保留旧五形状及十一类字段检查。现有reverse prev映射在decode62、mixed等用例中可真实进入scatter分支；至少一个用例在同一次 `_prepare_inputs` 前后读取metadata的runner内 `selected` 与async模块 `selected_launches`，要求两者增量都为1。不能只要求累计大于0，更不能只依赖首次打印。
- 保留完整input IDs、padding、CPU镜像、query起点、computed计数、slot、logits索引和固定地址对照。原graph consumer的三份输入外补 `input_ids.gpu`，让位置/seq/slot与新token值在同次replay中被消费。
- 复用原连续四步换host值、原event保护、每步replay并clone、最后总sync的结构；不在每步另加全卡sync。除原positions非陈旧检查，再确认消费到的input IDs跨步确有变化且逐步等于oracle，防止两侧都读旧token而假通过。同一步的索引顺序/新prefill空洞应保留原fixture可生成的变化，不增造调度策略。
- snapshot比较与RNG检查可在最终drain后完成；去掉旧32call ABBA性能段。设备所有者仍保存固定源码、命令、输出、失败及idle后态。当前没有该门的实际结果。

若上述门通过，便补上两helper串联、固定地址消费与跨步staging生命周期的直接字节证据，足以决定这两个低风险整数/元数据方法能否进入下一评审。它不补全整模型准确率、服务可达率、任意跨流或性能稳定性；两个单方法短筛百分比不能相加。是否再做服务/准确率由root按合并目标决定，不能因本静态审阅自动扩大官方验证，也不能将Draft改写成已验组合。

## 最小fork已定稿：跨owner静态审阅无阻断

hardware独占的 `scripts/remote/validate_cpu_combination.py` 已冻结为 **abfc7981a8d5a20ff32b80f42dd30148bbeb5d680c649bf892e2b3924ead0bad**。本owner实际读全文，并用stdlib对固定b124旧门输出完整diff；未执行新脚本、导入候选或重跑套件。未发现进入本轮组合正确性短门的阻断。

其变更恰围绕上述范围：source集合固定e155/6f918/0e9615/1bb85及原三项vLLM依赖；真实五方法仍由原AST抽取，model fixture只补守卫所需字段。decode62和mixed952要求同次async delta1，所有case要求metadata delta1；no-previous轮要求async delta0，未通过修改源算法制造命中。四个连续graph轮在原prepare事件范围内每轮要求 `{"metadata": 1, "async_token": 1}`；退出范围后才replay/clone，末尾总sync逐步比较四份consumer。input IDs和positions各自另有非陈旧检查，四份源GPU指针也核稳定。

原两索引H2D、原CPU host更新和原event先等后record均保留；graph不捕获prepare本身。原两helper完整SHA没有变化，controller先固定源/compile组合runner，再启动唯一worker/monitor；原300秒、finally清理、源只取regular files等机制保持。RNG观测覆盖构造、五case和连续轮，不再保留原32call计时段，也没有把该门包装成吞吐测量。

systems的薄层 `scripts/remote/launch_cpu_combination_gate.py` 草稿 **cda5bbef1acfd49fd9f8d18881cefc0acc2602f5bdbd768bc911919f4c7f2ede** 也已全文只读轻审。它只补固定输入、双idle/端口、DB前后、环境、后态和seal，由内层gate唯一持设备锁并负责worker/monitor/清理，未增加第二设备owner；DB快照在锁外，明确要求root串行派发。该草稿的gate pin仍为UNREVIEWED，必须仅换成上述已冻结abfc pin并再核最终SHA后才能运行，不能把草稿审通过当可直接执行。没有新模型、服务或SDK编译。

硬件作者已确认abfc不再改。本报告此时没有真实组合设备结果；后续由root唯一派发、取回完整原件并指定owner验收。本文和own handoff是本owner仅有新增写入，四个Draft及其源码材料不动。

薄launcher最终定稿 **d50511c9a194b1dadad87498b22862641cbea9643eea94aa73f32b320a6abb2f** 已实际重算SHA，abfc pin恰出现一次、无UNREVIEWED；将这一值逆换为UNREVIEWED，逐byte精确回上述全文已审cda5。该最终定向核无新增机制阻断，已直接回root可唯一派发，无须为报告或重复套件等待。实际组合设备结果仍待。
