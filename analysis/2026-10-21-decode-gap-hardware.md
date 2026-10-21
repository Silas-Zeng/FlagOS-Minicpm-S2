# Decode graph 与服务耗时差距：动态索引源码与缓存

2026-10-21。本轮仅本地 CPU/SQLite 阅读与官方一手源码检索，无远端或 GPU 操作。以下区分实测记录、源码机制和待验证假设。

## 当前判断

**061506 有界 CPU profile 已定位主要开销为配置缓存的 SQLAlchemy 全库反射。框架级按表反射候选优先，整数融合候选保留且不默认集成。** 动态索引形状变化仍是触发入口；此前把它推断成“首次 JIT 编译”的解释未获证实，不能继续作为结论。

原始记录位于 `experiments/profiles/20261021T061506Z-host-gap/host-window-summary.json`、`host-top-cumulative.txt`、`host-walltime.jsonl`。8个decode steps的wall为13.9476秒、所属线程CPU为13.9441秒，形状是62/62/61/61/60/60/59/59；所有执行均为FULL、padded64。cProfile记录：

| 范围 | 调用次数 | cumulative秒 |
|---|---:|---:|
| `_prepare_input_ids` |8|13.446|
| `SQLPersistantModel.get_config` |24|13.405|
| `get_sql_model` |24|10.781|
| `build_sql_model_by_db` |4|10.780|
| `automap.prepare` 内层 |4|9.115|
| `MetaData.reflect` |4|6.229|

这些时间是嵌套 inclusive 范围，不能相加。四个 `index_linearized_inp_shape_63/62/61/60...` wrapper 各约3.34–3.36秒。`sql.py:148` 每个新model运行 `AutoBase.prepare(engine)`；profile还记录1916次ORM map，大约每次model构建映射479张表，而调用者只需要一个配置表。这直接解释了图前主机线程忙碌的主要路径，**没有证明GPU编译器在这些秒数中占主导**。前述13.95秒是profiler诊断窗口，不能直接作为无profiler服务收益。

新的最小框架候选 `patches/framework/biv150_sql_reflection.py` 已由另一owner准备并经本owner独立交叉审查（SHA256 `ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e`）：仅在已审计SQLite `build_sql_model_by_db` 中反射请求的name表，缺表返回None，保持全部配置行、key、Config内容和原调优选择。`tests/test_biv150_sql_reflection.py` 六项真实SQLAlchemy CPU gate独立复跑1.118秒通过，覆盖多表仅target、缺表/新增、两个engine同名并发、列/PK/原get-put Config值与不覆盖、quoted名称、默认FK外向闭包、源码守卫及回退。非SQLite保留原行为；尚未据CPU门宣称服务提速或准确率通过。现有 `get_sql_model` 正命中已有model pool，不能把问题混称为“完全没有model缓存”。

下面保留先前native线索与源码解释，它们准确指出了动态索引入口，但将其等同于编译的初步归因已由上述栈证据收窄。

### 时间范围与反证

`experiments/profiles/20261021T042609Z-native-decode/native-events.jsonl` 记录执行形状依次为 `[62,62,1]`、`[62,62,1]`、`[61,61,1]`、`[61,61,1]`、`[60,60,1]`。SQLite `cuda_graph` 的五条记录都是 **CUDA Graph 25**，不是五个新图：

| active requests | graph duration ms | 与上一 graph 开始的间隔 ms |
|---:|---:|---:|
| 62 | 80.482 | — |
| 62 | 80.471 | 83.516 |
| 61 | 80.322 | 1898.496 |
| 61 | 80.322 | 83.317 |
| 60 | 80.086 | 2793.264 |

相同形状两次紧邻执行，改变 active requests 后出现秒级空白。原生 trace API 窗口 7.766 s，5 graph 合计401.683 ms，图外163 kernel合计13.416 ms，全部3157个CUDA API时长相加291.994 ms。API可能重叠，不能直接相减得到准确CPU占比；但 `cudaEventSynchronize` 合计133.157 ms、`cuModuleGetFunction` 合计153.463 ms，均不能解释数秒空白。

更具体的邻接关系：首个 graph 前，`_compute_slot_mapping_kernel` 后到 `cuModuleLoadData` 约2811 ms；下一档约1810 ms，第三档约2700 ms。每次随后首个可见kernel是 `_index_linearized_jit_function`，两次module load间只隔数ms。这曾是源码生成/JIT的排查线索；061506现已证明其中主要开销来自该动态索引调用内的SQL model反射，不能因下一个可见API是module load就认定为编译。`cuModuleGetFunction` 的两次约76 ms还与GPU工作重叠，不可把它们全部解释为编译。

原始细节由主负责人另存 `host-gaps.json`。graph内部节点不可见，所以13.416 ms图外kernel占比不代表整步或图内GEMM/attention占比。不能根据此trace把图内MM判为很小。

## 服务记录支持主机侧尾部问题，但119秒不是128次80ms

三次同参数诊断均64请求、每请求4096输入/128输出，输入262144 tokens、输出8192 tokens：

| run | duration s | mean TTFT ms | median ITL ms | p99 ITL ms |
|---|---:|---:|---:|---:|
| 050517 C2 |119.224|22873|225.917|4103.096|
| 051639 B0 |120.671|22903|213.860|4110.468|
| 054922 C3 |117.259|22265|213.673|4060.429|

这包含约40秒请求逐批进入的prefill/混合阶段，以及起止时间不同的decode请求；不能用119/128当固定B64单步延迟。三次中后段prompt吞吐已为0，但active从约60降至35时，日志generation吞吐仅约30–60tokens/s；不是稳定64请求的80ms graph。B0每5秒GPU样本在prefill阶段多次94–100%，进入tail后多数0%、功耗约33–39W。采样稀疏不能积分成精确利用率，但支持“GPU间歇等待主机”的方向。

三个服务启动都明确从同一 `torch_compile_cache/f7af72be36/...` 读取 `(1,2048)` compiled graph及同一AOT model，载入约1.8秒；35个decode图也在ready前捕获完成。没有日志证明请求每减1就再次触发整模型TorchDynamo编译。不能将启动编译5.6秒计入119秒负载，也不能以“暖Inductor缓存”替代图外动态源码诊断。

CPU quota为6核。B0本次窗口 `nr_periods` 增1423、`nr_throttled`增4、累计 `throttled_time` 增20.87秒；该时间为cgroup累计等待，可能包含并行线程，不能当作20.87秒服务串行损失。应与诊断栈、进程CPU使用关联，不能直接转入线程参数扫描。

## 已核实 installed 源码：四层缓存不能混为一谈

本地快照在 `tmp/remote-source/decode-gap/`，主负责人只读取回：

| 文件 | SHA256 |
|---|---|
| index.py |47a7108bcf8424a96651021703f8731f1866a0e2eff88a1ac647e574ccf7e61d|
| libentry.py |414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025|
| code_cache.py |fc7c50a8372fb103db427bcb421c9fc2c38714a9d9bd883bcc87df93eb41b101|
| pointwise_dynamic.py |6a4f88e227ed566de05729c0ab3ac89457e0cbdcdbea31b12319908f4ee33290|
| sql.py（061506/source） |6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7|

1. **生成源码/进程overload缓存。** installed `index.py:619` 的 `LinearizedAdjacentIndexFunction.arg_key` 包含完整 `inp_shape`、start_dim、dtype、index数量及M/N bucket。`M align32`并没有消掉input shape：对实际方法做纯CPU AST提取，63→62、62→61、61→60的输入row变化分别得到 `inp_shape_63/...m_64_n_32`、`inp_shape_62/...m_64_n_32`、`inp_shape_61/...m_64_n_32`，三个不同key。miss会生成/写文件/exec新module。
2. **源码实际改变。** `index.py:412` 的生成器把indexed dims、索引stride、indexed volume、suffix size直接写入Triton函数，包含负数索引修正和bounds判断。不能仅删除shape key来复用旧函数；那可能沿用错误边界。每个新module又带 `libtuner(key=M,strategy=align32,warmup=5,rep=10)`。官方 [index源码](https://github.com/flagos-ai/FlagGems/blob/master/src/flag_gems/ops/index.py)公开了相同机制；当前安装代码以本地SHA为准，不据此合并master。
3. **LibEntry与调优缓存。** installed `libentry.py:1580`：tensor key是dtype与指针对齐，普通scalar key保留实际值，do_not_specialize保留类型，constexpr原值进key；miss在锁内重新进入内层JIT/调优路径。它与持久调优SQLite、生成源码目录是不同对象。公开 [v5.3.5 libentry](https://github.com/flagos-ai/FlagGems/blob/v5.3.5/src/flag_gems/utils/libentry.py)支持该机制。源码已变时，不能假设旧二进制/旧调优key仍命中。
4. **Triton/FlagTree编译缓存。** 官方 [FlagTree JIT源码](https://github.com/flagos-ai/FlagTree/blob/main/python/triton/runtime/jit.py)区分设备内存kernel缓存、specialization/options key与编译路径；源码/依赖又影响hash。此公开main仅是机制参考，不能证明本实例确切FlagTree版本行为，更不能凭目录mtime认定“编译”而不是读缓存。短profile应保留实际jit/compiler文件及耗时。

反例：installed `pointwise_dynamic.py:1652` 的源码生成overload按rank和配置缓存，文件名含scalar_fn hash/rank；**它的上层源码生成本身并非逐M生成**。下层scalar参数仍可能造成新dispatch/JIT specializations，但不能因true_div grid变化就断言其每B生成新Python代码。

## 优先检查框架中的哪两处

1. `model_runner.py:1879`：`prev_sampled_token_ids[prev_common_req_indices_tensor,0]`，再scatter至input_ids。当请求退出/重排时走此路径，上一批token tensor的row数随active改变；这与图前slot_mapping后的长空白位置吻合。原有unchanged快路径已直接slice copy，不能把它也当作每步advanced index。`select(1,0)`后再按dim0选择的结果形状与原表达式一致；单纯路由到现有 `index_select/gather` 不满足比赛的实现变更要求，也不能保证避开其自身JIT。
2. `model_runner.py:4435`：`hidden_states[logits_indices]`，再LM-head。62/61/60都重放同一padded64图，hidden输入通常保持64rows，index长度M仍同一64 bucket；因此它不应天然每减1生成新Python源码，但下层LibEntry/调优仍须诊断。不能未经栈证据就把这处列为第一候选。

## 两个可实现方向，先诊断后集成

以下是profile前准备的两个实现方向；当前优先顺序已让位于直接修复SQL反射的框架候选。

**保留候选：在原 `_prepare_input_ids` 边界实现整数 gather+scatter 融合。** 保留CPU请求映射、原两份indices异步H2D、所有无common/unchanged/prefill/spec分支；只在受审模型、dtype、shape、device、无spec/embeds且无alias时，把“读取prev token临时tensor→scatter”改为一个新实现的动态尺寸int32拷贝kernel。num_common/源stride/目标stride用runtime参数，避免active B作为constexpr、生成源码key或autotune key。源地址由已有prev_indices、目标地址由sample_flattened_indices给出；同请求/目标顺序保持不变，无FP/RNG改变。目标indices唯一性由现有CPU映射证明；若通用重复目标未定义，不得用并行store声称保持last-writer语义。另一owner负责交叉审源和最短real gate；不因微kernel实现已准备而优先集成它。

**第二候选：固定容量source buffer/框架padding只覆盖图外元数据。** 给该gather准备私有固定容量prev-token source，原active count仍独立保留，避免改整个sampler或RNG行数。它多一次很小D2D copy，需处理跨流与生命周期。不得把padded tensor直接替换全局prev_sampled_token_ids，因为很多现有逻辑把shape[0]当实际请求数。它是融合kernel若遇集成阻力时的后备。

不优先扩大全模型graph capture：官方 [v0.24 dispatcher](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/cudagraph_dispatcher.py)已按bucket映射BatchDescriptor；这里62/61/60确实同图，额外覆盖精确B不能消除图外新source shape。也不扩充sampler padding，因为多余随机行会改变RNG消耗；已有sampler compile on/warm-cache负结果保留，不重跑同一开关。

原最短证伪已由061506完成：有界CPU profile覆盖了B变化和相同B，明确给出主要SQL反射栈。下一步先做按表反射的真实SQLAlchemy CPU gate，再由设备owner串行验证短服务，并核对原Config返回值/服务准确率。若SQL优化后仍残留秒级空白，再根据新profile区分SQLAlchemy query compilation、真正Triton编译或其他路径；不以预热掩盖。整模型收益仍按 `被消除的miss次数 × 每次关键路径损失 / 任务时间` 估值；例如30次×1秒/119秒≈25%只是历史条件预算，尚不是已测收益。最终仍需准确率与同参数端到端复现。
