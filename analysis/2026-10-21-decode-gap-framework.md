# Decode graph 与服务 walltime 差距：框架归因

日期：2026-10-21。本文基于本地实际源码镜像、原始服务日志/结果和只读 SQLite 查询。该 agent 没有执行远端命令或 GPU 任务。所有 profiling 数据均为诊断证据，不能作为正式性能分数。

## 当前结论

新的8步host profile已把主要成本定位到 **FlagGems按形状创建索引wrapper时的SQL配置模型反射**，比“冷JIT”更精确。native trace先显示，同shape graph启动间隔约83 ms，62→61、61→60变化对应1.90 s、2.79 s间隔；随后host profile把约13.4 s指向SQL get_config/get_sql_model/build_sql_model_by_db及SQLAlchemy automap/schema.reflect，而不是GPU sampler算数。

实际安装的FlagGems `index.py` 对完整输入形状创建独立生成模块，runner在异步token行变化时执行gather，触发上述host配置查找路径。当前直接实现候选是语义精确的整数gather/scatter融合，以绕过该生成路径；更通用的框架候选是复用SQL配置模型。后者要等实际SQL源码审计后再设计，不能把缓存键或数据库schema直接删改。其他阶段不是零开销，但本窗口已有明确主因，不再以“可能是sampler”扩散设置扫描。

## 新host profile结果：SQL reflection为主因

唯一run为 `20261021T061506Z-host-gap`，由主负责人运行和读取。本 agent在写入此更新时收到主负责人的实时summary/pstats结果；完整本地归档与SQL源码尚待设备负责人在该run退出后取回，因此此处明确区分负责人提供的已观测结果与本 agent独立SQL分析过的旧native证据。

| 8步诊断窗口字段 | 主负责人提供的实测值 |
|---|---:|
| 完整窗口walltime | 13.947 s |
| 当前profile线程CPU时间 | 13.944 s |
| execute_model累计 | 13.710 s |
| `_prepare_input_ids`累计 | 13.446 s |
| libentry / SQL `get_config`路径 | 13.405 s |
| `get_sql_model` / `build_sql_model_by_db`，4次 | 10.780 s |
| `automap.prepare`累计 | 9.115 s |
| `schema.reflect`累计 | 6.229 s |

以上均为嵌套inclusive累计，不能相加；cProfile自身也增加开销。主负责人确认4个新index输入形状为63/62/61/60，每个新生成路径约3.34 s。`_prepare_input_ids`约占该诊断窗口96.4%，线程CPU时间几乎等于walltime，支持CPU侧SQL模型反射为主，不能再把这几秒笼统称为GPU同步或JIT编译器耗时。

这不意味着未插桩119 s负载中恰好有同样比例；该窗口只取8步。它足以确定下一改动应消除这些重复host工作。已有整数token融合候选仍有意义，因为它替换该次gather+scatter实际实现，避开生成新index wrapper及其配置查询；没有把浮点采样、RNG或全局packed顺序一起更改。

## 先统一数字的口径

`experiments/framework/20261021T050517Z-c2-decode-screen/decode-4k/results/decode-4k-infqps-concurrency64-minicpm-20261021-131008.json`：

| 字段 | 原始值 |
|---|---:|
| 完成 / 失败 | 64 / 0 |
| 输入 token | 262144，即 64×4096 |
| 输出 token | 8192，即 64×128 |
| 整个负载 duration | 119.224039 s |
| output throughput | 68.710975 tok/s |
| mean / median TTFT | 22.873468 / 22.396410 s |
| mean / median ITL | 599.912383 / 225.917219 ms |
| p99 ITL | 4103.096094 ms |

匹配 seed、请求量和官方 SERVER 的新 B0 `20261021T051639Z-b0-decode-screen` 为 120.671052 s、67.887036 output tok/s、mean ITL 606.959094 ms、median ITL 213.859562 ms、p99 ITL 4110.467932 ms。C2 单层 decode 的大改进尚未转化为这次负载的大 walltime 改进。

119 s 包含 prompt 排队、262144 个输入 token 的 chunked prefill/mixed 阶段和不断缩小的 decode 尾部，不能直接用 `128×80 ms` 相减。固定 2048-token 调度上限意味着输入本身相当于至少 128 个满 chunk 的工作量，而 8192 个输出也不等于恰好 128 次 batch64 graph。每请求首次输出不同步，实际 decode step 数和形状分布要由真实 step 记录确定。

同样不能把服务启动的 105.28 s 或启动 `torch.compile` 的 5.60 s 算进119 s。C2 日志显示上述初始化已在 API ready 之前完成；诊断 driver 在 ready 后执行 smoke，再调用负载脚本。TTFT 与 ITL 的巨大长尾仍然存在于运行期。

## Native trace 已证明的现象

证据目录：`experiments/profiles/20261021T042609Z-native-decode/`。`native-events.jsonl` 标明窗口中实际 scheduled shapes 为 `[62,62,1]`、`[62,62,1]`、`[61,61,1]`、`[61,61,1]`、`[60,60,1]`，即五步均纯 decode。`native-validation.json` 已确认有效；`native-trace.json` 实际是 SQLite，不能按 JSON 解析。主负责人另保存只读提取结果 `host-gaps.json`，其输入 trace SHA256 为 `7687061c4ba73b47d9edc50e78ae217ed125e990d6785285af41c3e3b9d89a9d`。

| 活动请求数 | graph duration ms | 与上一次 graph start 的间隔 ms |
|---:|---:|---:|
| 62 | 80.482152 | — |
| 62 | 80.471096 | 83.515930 |
| 61 | 80.322144 | 1898.495986 |
| 61 | 80.321648 | 83.317112 |
| 60 | 80.086216 | 2793.263616 |

五条记录均为 `CUDA Graph 25`。因此这两个活动请求数变化没有换成另一个 backbone graph，也没有令所记录的 graph 时长扩大几十倍。

本 agent 独立只读查询得到：

- `cuda_api_data` 覆盖 7.766152094 s；5 个 graph 的 duration 合计 401.683256 ms。
- 163 个图外 kernel 合计 13.416306 ms；52 次 memcpy 合计 0.522773 ms；无 memset 记录。合并已记录 GPU graph/kernel/memcpy 时间区间后的并集为 415.622335 ms，约为 API 窗口的 5.35%。这是当前 trace 的覆盖口径，不能直接当成整个服务 GPU 利用率。
- 最长的三段相邻 CUDA API 空隙为 2803.663176、2692.460048、1877.818608 ms，前后 API 名均为 `cudaGetDevice`；不是该 API 本身执行了数秒。
- API duration 合计约 291.994 ms。其中 `cuModuleGetFunction` 10 次合计153.463 ms（最大76.322 ms）、`cudaEventSynchronize` 10次合计133.157 ms（最大67.120 ms）。这些同步和模块操作值得保留，但不能解释数秒 API 空隙。
- 图外 `linear_kernel` 5 次合计5.598190 ms；温度除法、softmax、指数噪声、histogram top-p 和 argmax 等已记录 kernel 也都在毫秒或以下范围，不能把数秒空隙直接归因于 sampler GPU 算数。

此 trace 没有图内节点，不能据此判断 Attention 与 GEMM 在 graph 内的占比。native profiler 自身可能改变时序，以上是归因信号，不是未插桩性能承诺。

## 未插桩日志提供的独立佐证

C2 在13:08:48已显示64 running、0 waiting；13:09:08之后 prompt throughput为0，但 generation throughput仍只有32.7–58.5 tok/s，活动请求从56逐渐降到35，尾部不是还在消化大量 prompt。

新 B0 在13:20:29到13:21:09的多个10秒日志区间，prompt throughput均为0；活动请求数按56→52→48→44→40下降，generation throughput依次43.2、40.0、36.8、33.6 tok/s。以区间平均活动请求数粗估，这几段相当于约1.25 s/step，明显高于旧 native 五步 graph约80 ms；这只是基于10秒聚合的估计，不替代实际 step timeline。

5秒间隔 `gpu.csv` 在两个decode运行尾部也有大量0%采样，符合 bursty 执行。采样稀疏且可能错过短 GPU burst，不能把平均采样值当成精确忙碌时间积分。

CPU cgroup quota 为600000/100000，即6 CPU配额。C2负载前后 `nr_throttled` 增4、`throttled_time`增约16.10 s；新B0对应增4、约20.87 s。这是 cgroup 内跨线程累计节流统计，包含driver/客户端等 host workload，不能直接当成新增16–21 s服务walltime，也不足以单独认定是配额导致每次 shape 停顿。后续 profile 会同时记录进程与当前线程 CPU clock。

## 实际源码中的具体候选

### 1. 异步 token gather 与完整输入形状缓存键

实际 runner `tmp/remote-source/model_runner.py`（完整SHA256 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`）的 `_prepare_input_ids`（1773行起）有两条不同路径：

- batch不变且行号相同，直接从 `prev_sampled_token_ids[:num_common_tokens,0]` 拷贝到 input_ids。
- 请求退出/行变化时，上传当前与前一步行映射，使用 `prev_sampled_token_ids[prev_common_req_indices_tensor,0]` gather，再 scatter 到原 input_ids（约1877–1882行）。来源 tensor 的第一维会随上一轮活动请求数改变。

实际安装的 `flag_gems/ops/index.py` 只读镜像已由设备负责人下载到 `tmp/remote-source/decode-gap/index.py`，SHA256为 `47a7108bcf8424a96651021703f8731f1866a0e2eff88a1ac647e574ccf7e61d`。其中 `LinearizedAdjacentIndexFunction.arg_key`（619行起）除 M/N bucket之外还保留完整 `inp_shape`；因此输入 `(63,1)`、`(62,1)`、`(61,1)` 会得到不同 overload key，不能因 index length处于同一bucket就复用一个 overload。

cache miss分支（587–617行）执行 `generate_linearized_code`、写生成文件、`module_from_spec`、`exec_module`、取生成wrapper再存入进程内 `self.overloads`。生成的Triton kernel带 `libentry` 与 `libtuner` 装饰；实际 `libentry.py` 的cache miss会进入配置查找及底层JIT函数。旧native本身只能证明存在额外host路径；新的8步host profile进一步把主要时间定位到SQL模型反射，并未证明完整Triton编译或GPU调优是主要耗时。

native窗口有13条 `_index_linearized_jit_function`；三段大空隙之后、下一graph之前也出现该kernel。相同名字对应多个index调用点，仅凭kernel名字还不能唯一定位到上述token gather：`self.num_computed_tokens[req_indices_gpu]`、`hidden_states[logits_indices]`也是候选。后者通常从 padded64 hidden_states读取，完整源形状可能不随62/61/60改变；前者源buffer也可能固定。`_prepare_input_ids`是优先核查点，但需调用栈而不是靠名字定案。

`tmp/`为ignored辅助镜像。新诊断run须把实际runner、index、libentry、pointwise源码及hash归档；不能把本地镜像当唯一复现依赖。

### 2. Sampler：已有负结果约束，不能凭猜测重新开compile

实际 `topk_topp_sampler.py` 的 native路径会调用 top-p过滤，再调用随机sample或softmax/指数噪声；runner `_sample`还会执行 `input_batch.update_async_output_token_ids()`，后者可能包含原有异步数据就绪等待。实际 `_bookkeeping_sync` 和 `AsyncGPUModelRunnerOutput.get_output`也分别涉及不同输出/同步路径。

服务日志明确显示插件已经 unwrap `topk_topp_sampler.compiled_random_sample` 与 `logprobs.batched_count_greater_than`。对应实际镜像分别为 `tmp/remote-source/decode-gap/topk_topp_sampler.py`（SHA256 `35b9a1ffeb1e50b73b0ddd1ffc0f968910ee21cf9cc5455dd879fde547b6ddc1`）与 `sampler.py`（`1a2f18ddc91c89f3744ab5a93624be056bf20b7a8b2e6e13d0236182718a2253`）。unwrap不意味着没有FlagGems/Triton自己的按形状生成、调优或cache miss。

旧 `a16-sampler-compile` 与 `a17-sampler-compile-warm` 的匹配短测试均为负结果：4K total throughput从默认5045.59降到3131.36/3144.42 tok/s；16K从3554.45变3330.25/3535.92 tok/s，详情见 `analysis/2026-10-21-attention-top-p-candidates.md` 的负结果表与 `experiments/remote-evidence/a16-sampler-compile/`、`a17-sampler-compile-warm/` 原始JSON/日志。

这些运行是旧的4K/16K短混合负载，不能与新的8192输出服务直接比较；也不能据此证明当前采样开销不存在。它们足以反对没有新证据就重跑“开启sampler compile”的设置扫描。

### 3. graph之外的 logits 和输出转换

runner 在 `_model_forward` 返回后取 `hidden_states[logits_indices]` 并调用 `self.model.compute_logits`（约4434–4435行），随后才存入 `execute_model_state`。所以单个80 ms backbone graph不包含这段 LM head/索引，也不包含 `sample_tokens`。

异步输出类在构造时启动D2H，`get_output`在342行起等待已有 `async_copy_ready_event`、转换Python列表并返回原 output。该等待可以与其他工作重叠，不能把它和执行方法inclusive时长直接相加。它也可能由不同线程调用，因此需要thread ID与同一step标签。

## 最短无数学改动诊断：已准备的独立 footer

文件：`scripts/remote/decode_gap_profile_footer.py`，SHA256 `f1ca51128d771963a989f97e96c9883a24af25077283b764de6163f2eb2dfaf0`。CPU proof：`tests/test_decode_gap_profile.py`，SHA256 `7e7bb2ba278ea982a2a95b5dcd7759cedc96e80a9d5ee487acc4e0799fa93faf`。

footer只能追加到精确保留runner（允许一个额外LF分隔），通过上述446f12源码前缀hash才安装。必须指定 `MINICPM_DECODE_GAP_RUN_DIR=<ROOT/profiles/唯一UTC-run>` 且目录存在；拒绝score/official目录和缺失env。安装后打印 `MINICPM_DECODE_GAP_INSTALLED`供driver gate。

它跳过前两个 `n>=16且所有scheduled值为1` 的真实execute调用，在随后8个连续纯decode step启用cProfile；下一execute入口停止并落盘，窗口中出现mixed/其他runner则停止标记incomplete。execute/sample异常仍传播原异常，先保存不完整profile。既不全程profile，也不依赖shutdown钩子。

记录方法级wall spans：`execute_model`、`_update_states`、`_prepare_inputs`、`_prepare_input_ids`、`_build_attention_metadata`、`_determine_batch_execution_and_padding`、`_preprocess`、`_model_forward`、`_update_states_after_model_execute`、`sample_tokens`、`_sample`、`_bookkeeping_sync`，以及选中输出的 `AsyncGPUModelRunnerOutput.get_output`。不在42层逐层插桩。

记录的shape与logits尺寸只读CPU scheduler和tensor descriptor；记录actual shape出现次数、graph mode、padded token数。每条记录包含 `perf_counter_ns`、进程CPU时间、当前线程CPU时间与thread ID。没有新增torch/CUDA调用、tensor内容回读、同步、warmup、采样、RNG调用或调度修改；原参数和返回对象透传。

输出固定为：

- `host-walltime.jsonl`：line-buffered边界日志，保留晚到的async output span。
- `host-window.pstats`：原始cProfile统计，可追到index codegen、exec_module、libentry/libtuner/Triton/subprocess/cache调用栈。
- `host-top-cumulative.txt`：前80个累计时间项，便于先找主路径。
- `host-window-summary.json`：8步/shape窗口、clock增量、是否完整及限制。

4项纯stdlib CPU proof通过（0.041s），覆盖8步边界与shape首次/重复、参数/返回对象透传、异常传播/incomplete、sourcehash与目录隔离；无torch/GPU。它们验证诊断包装器，不证明CUDA性能或模型精度。

主负责人已独立审查 `scripts/remote/launch_decode_gap.sh` 和 `run_framework_screen.py --host-profile`：精确gitarchive d60基线加footer、沿用官方SERVER/seed、同device lock、日志marker和归档，结束检查完整8步summary及非空pstats，否则status2。唯一诊断 `20261021T061506Z-host-gap` 已由主负责人完成有效8步窗口并给出上述SQL反射归因；写入此更新时服务/负载尚待负责人完成退出和完整归档。本 agent不并发运行设备任务，也没有自行取回远端数据。

## 如何判定假设与决定下一步

1. 当前窗口已经命中 `_prepare_input_ids`的新index shape→SQL模型反射路径。先交叉评审并用真实入口gate验证整数token融合；修改必须保留精确gather/scatter语义，不能只删cache key里的维度而忽略生成代码中的shape常量。
2. 若 `_prepare_inputs`慢、`_prepare_input_ids`不慢，检查positions/seq-lens indexing、slot mapping或其他其子调用。若 `_model_forward`外的execute尾部慢，检查hidden-state gather和compute_logits。
3. 若 `_sample`或bookkeeping/output慢，先分辨已有GPU等待、FlagGems按形状host路径与Python处理；不因函数名包含sample就重开torch.compile，也不以GPU kernel小就排除host生成路径。
4. 如果profile累计时间主要为锁、文件/子进程等待或线程CPU时间很小，继续定位等待对象；process CPU和thread CPU不是纯粹GPU/CPU利用率，不能直接把差值称作GPU耗时。

方法spans是inclusive且可能重叠；cProfile仅覆盖启动它的线程，跨thread输出只有wall日志。`first_shape_in_observed_requests`表示真实execute阶段首次观察，不证明该形状在startup/dummy/历史cache中未出现。profiling会增加Python开销，不能把该run与C0/C2 walltime当性能pair。

更通用的后续框架点是SQL模型复用：以实际数据库身份和schema生命周期为边界，避免每个新Triton wrapper重复automap/schema reflection，同时保留原配置选择和读写语义。必须先审计实际SQL实现的模型所有权、表创建/变更、进程/线程边界、失效条件和已有cache；当前不实施全局SQL cache，也不通过删除数据库或强制重新调优来改变证据。
