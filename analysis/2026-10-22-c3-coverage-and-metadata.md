# 天数 BI-V150：C3 覆盖审计与 CPU 元数据复用候选

本轮接续已通过 103/105 和完整官方吞吐的 SQL+C3，不重建基线。用户于
2026-10-21T16:40Z 重新授权持续探索，并要求小收益也进行最短上卡验证、保留原件；
此前冻结记录作为历史保留。本页全部实测与设计仅针对天数 BI-V150。
实验分析库分平台记录，两个私有源码库由团队共用，不要求平台目录或分支。

本 owner 只做本地 CPU 阅读、独立候选与门准备，不 SSH、不执行 GPU、不改稳定
080656 源、完整 4aba 补丁或旧 default。设备操作由 root 串行拥有。

## 1. 精确源码已经补齐：没有 decode-first 保证

来源为 root 只读取回的
`experiments/source-audits/20261021T170854Z-scheduler-kv-c3/manifest.json`。
归档当时设备 68 MiB / 0%，installed Attention 为原始 bab2；e155 / a129 没有变化。

| 实际源码 | SHA256 |
|---|---|
| `vllm/v1/attention/backend.py` | `c524988a2223ec556bdb128a31c255075f0d07e7643e803b447975cd9c30a6b8` |
| `vllm/v1/attention/backends/utils.py` | `f1375ec8e3a2d5c77ab15773eef2c00a4117826a3c238ceb5bcd4efe9fa55381` |
| `vllm/v1/worker/gpu_input_batch.py` | `de1ea4fc9d43fc6079dd375e407c2b6d93f5e1a11f49732d13654c41eaf30a65` |
| `vllm/v1/utils.py` | `4e4cda209e10d4477d251003779dec26ea5ef47541c3310995c007c7ee5fdcdb` |

`AttentionMetadataBuilder:572` 的类属性 `reorder_batch_threshold=None`，
`:582–589` 父构造只保存配置，不调用 `_init_reorder_batch_threshold`。
实际 Triton builder 1219 的构造调用这个父构造，但全文没有设置 threshold 或调用初始化函数。
e155 runner `calculate_reorder_batch_threshold:7025` 因而保留 None，
`_may_reorder_batch:1125` 不会调用排序 helper。

actual `InputBatch.condense:684–811` 只拿最后一个活动行填最小空位，并同步维护请求、
长度、KV 行、采样参数、generator 和 logits processor 更新；不按 query 长度或生成阶段排序。
因此**没有保证 C3 可拆的所有单 query 请求都在天然连续前缀**。
这是覆盖缺口的源码证据，不是“服务已出现大量遗漏”的实测证据。

即使未来调用 actual `reorder_batch_to_split_decodes_and_prefills:637`，它也分为
decode → short extend → long extend → fresh prefill 四区。
`num_computed==0` 的单 query fresh prefill 仍可能在较长 query 后面；不能仅设置阈值就
宣称所有 query_len=1 都前置，更不能无验证改变全局 RNG 对物理行的分配。

旧 D29/P2019 和其它单层测试是显式构造。原 a129 只有 INSTALLED 标记，没有服务 split
命中统计；C3 历史收益及准确率不能倒推出自然前缀覆盖率。现需一次真实服务计数，而非新的合成几何门。

## 2. 已冻结的只读覆盖诊断

文件 [`patches/framework/biv150_c3_coverage.py`](../patches/framework/biv150_c3_coverage.py)，
SHA256 **`29137c16ceb1d811b6b29b28782e2dcdf3463fce154917b16871d3157f7466b3`**。
纯 bytes transformer 只接受完整 e155 runner，在 EOF 追加显式 `enabled=True` 的安装 footer；
生成 runner SHA **`a39a894a67771e724fc198ea1c3720d1504806cc3d07723a2e3f36fe4d6e6675`**。
模块本身默认不启用，导入不加载 torch；安装时同时锁定上述三份 actual 基础源码、1219 backend 与 a129 C3。

- 仅真实 `execute_model` 的 ContextVar 作用域内观察；原 managed inference 包装、原调用、
  原返回与原异常保留，finally 复原 scope。
- `_build_attention_metadata` 先执行原方法，再读取 CPU `query_start_loc`，不读回 GPU 值。
  排除 capture；每步首个唯一 Triton metadata 只计一次，42 层共享对象不重复计步；
  多 build、padding 或不支持的组另计，不伪装为所有 engine 步的完整覆盖。
- 聚合 mixed 步数、single-query 总数 D1、天然连续前缀 Dprefix、原 plan 的 Dplanned，
  另统计 `computed>0 && computed>=prompt` 的 single-query decode 子集及其覆盖。
  D1 不等同真实 decode；**Dplanned 只说明 plan 创建，Impl.forward 仍有其它守卫**。
- 不包装 forward，不改排序、metadata、KV、采样或 RNG，不添加 GPU 同步。
  观察失败只记错误计数，不替换原结果或异常；不保存 prompt、token 或请求文本。
- 首步、每 64 个 execute 及 atexit 尝试输出累计快照。
  每条明确 `workload_complete=false`、`plan_is_forward_execution=false`。
  弱引用失效、信号退出或尾部不足 64 步可能没有最终快照，不能称完整负载计数。

本地最短静态门已过：语法、标准库导入不载 torch、精确 EOF append 可逆、扰动及二次变换拒绝；
三个 CPU offset fixture `[1,1,7]` / `[7,1,1]` / `[1,7,1]` 验证 D1/prefix/plan，
共享 layer 对象、第二次 build 去重和 capture 排除。fixture 不是完整 runner 或 forward 验证。
systems owner 独立只读互审无阻断。

root 已独占运行 `20261021T173003Z-c3-coverage-context16k`，沿用独立 source、原 SERVER、
既有 `--context-screen --seed 721201`、16K / 32 请求 / 128 输出；exit 0，
17:33:27Z 结束后设备 68 MiB / 0%。本文作者没有执行设备操作，已实读本地原件
[`coverage-snapshots.json`](../experiments/framework/20261021T173003Z-c3-coverage-context16k/coverage-snapshots.json)，
SHA `f51c9981156d4fcaa1122030e719b8727d9428bc3d370e89a8bccf75d8747554`。

真实 EngineCore 191286 最后周期快照位于 execute 384：305 个 metadata 步、250 个 mixed 步，
single-query 与定义内 decode 均为 3000 请求次，天然前缀/plan 为 2241，前缀外 759（25.3%）。
另有 77 个 padding 或不支持的步骤，观察错误与多 metadata 均为 0。
这证明观察范围内存在真实遗漏，值得设计分区候选，但不说明 25.3% E2E 可省。
快照没有最终完整标记，也不是 forward 选中计数；总 execute 范围还含既有 driver smoke
（首快照 1 请求 / 8 tokens），不把总步数冒称纯 benchmark 计数，不手改原始统计。
计时不作性能基线，不提前承诺收益或继承准确率。

## 3. 性能候选一：直接复用已计算的 CPU positions / seq_lens

独立文件：
[`biv150_cpu_metadata.py`](../patches/framework/biv150_cpu_metadata.py) 和
[`biv150_cpu_metadata_source.py`](../patches/framework/biv150_cpu_metadata_source.py)。
它们不安装到 default，不与 coverage 混在一个性能 source 中。

e155 `_prepare_inputs:1984` 已在 CPU 计算 `positions_np`；`:2076–2082` 已用同一
computed 输入计算 int32 `optimistic_seq_lens_cpu` 并清零尾部。
但 `:2172–2187` 又上传 req_indices、query_pos、scheduled count，执行 GPU
gather、int64 转换、positions add、seq add 和尾部 fill。
actual InputBatch `:163–169` 明确 computed NumPy 是 CPU tensor 的 `.numpy()` 视图，
候选仍以 CPU pointer/stride 验证，不只依赖字段名字。

候选保留前面的 `num_computed_tokens` 原 copy，随后将已有 positions_np 复制到一次分配的
最多 16 KiB pinned staging，执行两份 H2D 到**原有** positions 与 seq_lens GPU storage。
seq 使用原 pinned optimistic buffer，整条上传包含原零尾；positions 只写真实 M，padding 保留原后续处理。
不改 block table、slot mapping、请求行、attention metadata 或采样。

严格限制 BF16 MiniCPM5-2B、单并行、text、无 spec/LoRA/MM/MRoPE/XDRoPE/mamba/共享KV、
原 async scheduling 与非空 prepare event；未知合同在提交任何 copy 前返回 False，走原表达式。
原 `synchronize_input_prep:3824` / `execute_model:4164` 已保护 pinned CPU 复用，新 staging
纳入同一生命周期，不新增 stream 或同步。实际 e155 全文件确认三个 private GPU 输入在此
scope 没有其它消费者；其 CPU 镜像仍照原刷新。保留原目标 pointer/stride，不能跨步缓存结果。

纯 bytes transformer 只接受完整 e155，原 16 行表达式保留为 fallback；可逐 byte 逆回原 runner。
模块导入仅标准库，首次选中校验 actual InputBatch 与 CpuGpuBuffer 来源 SHA。
systems owner 已只读审 runtime / transformer，无当前 scope 阻断。

这能删除具体重复工作，但**尚无 SQL 后 host 占比或 E2E 收益实测**。
不拿修 SQL 前的 13.4 秒或全部 prefill 时长当节省预算。
最短真实方法门已准备：抽取 exact 原/变换 `_prepare_inputs`，用 actual CpuGpuBuffer 与
BlockTable，检验 positions/seq/slots/logits/input IDs、零尾、固定地址、连续换值和原 event
复用生命周期；再测完整 host wall ABBA。它不含权重、模型、LM-head 或 sampler。
方法门没省就停；有小信号也保留，再由 root 做同来源 4K64req128out 短 pair，核实际 FIRST_SELECTED、
DB/KV/完整 tokens；只有正信号再考虑 accuracy/官方长验证。

| 冻结产物 | SHA256 |
|---|---|
| runtime | `0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f` |
| transformer | `0096cdac2c63544b5e3e62766168dc3df22f6ab63c09231bf9c6e93abaf29835` |
| transformed runner | `50493fb68b194ed935650a3a743d2f56696d7379b702f4d7717eecac0325a9de` |
| [`validate_cpu_metadata.py`](../scripts/remote/validate_cpu_metadata.py) | `b1240720b588dae25d92cc1c173d64c1ea5f6e34fcdcab5dd0156407ebbcb757` |

本地 7 份资产哈希、5 个真实方法的 AST 抽取、语法、精确反变换、`--help` 与控制器导入
不载 torch/numpy 均通过。门含 5 个形状、完整整数元数据/slot/输入/地址、
连续 4 次换 CPU 值且不逐步强同步、原 prepare event 复用与固定图消费者、原 scope fallback，
末尾为 32 calls 全方法 host wall ABBA（包含原 event 和最终 drain）。
fixture 不构造完整 ModelRunner/InputBatch，不含权重；不将这条计时当服务收益。
systems owner 全文互审未发现执行或生命周期阻断。

root 已串行执行 `20261021T174115Z-cpu-metadata-gate`，19 秒内 exit 0，
17:41:34.453023Z 完成，child 192970 已退出，postflight 空闲。
本 owner 独立重算归档 10 份 source SHA 全通过，实读 5 个 shape 全部字段检查为 true，
连续换值/原 event/图消费者通过，实际 selected=75。
[`results.json`](../experiments/framework/20261021T174115Z-cpu-metadata-gate/results.json) SHA 为
`50b631e28c83ea1861624bc51b2d23222470444ee5ed9bc99790add2ba15b99d`。

32-call host-wall ABBA 中位数 `0.712748078125 → 0.65646540625 ms`，
单次方法少约 `56.282672 μs`、约 7.8966%。这是无权重 fixture 的输入准备方法计时，
不是 E2E 百分比，尤其不能忽略与模型计算重叠的边界。root 已转同来源服务短 pair，
本页尚无该 pair 完整结果，未据方法门宣称服务加速。

门的可复现命令保留如下（已执行，不能在其它任务占卡时重跑），依赖既有
`validate_block_table_candidate.py` 和 `monitor_gpu.sh`：

```text
python3 validate_cpu_metadata.py --run-dir /workspace/experiments/minicpm-s2/framework/<唯一UTC>-cpu-metadata-gate --runtime-path <biv150_cpu_metadata.py> --transform-path <biv150_cpu_metadata_source.py> --runner-path <原080656的model_runner.py>
```

## 4. 性能候选二：已过门的 async token 整数融合

保留 `biv150_async_token_update.py`，SHA
`1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc`。
063353 真实方法 12 类 GPU 正确性门已通过，尚无服务性能，不属于已否定路线。
它只在非 identity 的请求 churn 路径将整数 gather + scatter 合为一次新实现，
保留两份 indices H2D、请求顺序与 RNG，预期可能很小。

旧 transformer 只接受 446f runner；root 已完成独立 e155 适配
`biv150_async_token_update_sql_mixed_source.py`，SHA
`cfd378a494c0ccbb5aece861527cdf59ccd148afbe53ac229a09bb43162bdb6f`，
生成 runner `f0d0bada4222038b69ed139d804622e27acd6aa4e19a37ff089b0ca35f393f41`；
实际原/变换方法与旧门字节相同、可精确逆回 e155，已由 hardware 审。
证据见 [`async-token-adaptation.json`](2026-10-22-async-token-adaptation.json)。

本 owner 在未获知 root 已适配时新增 `biv150_async_token_update_c3_source.py`（123d7f1d…），
只换精确 base hash 与说明，生成同一 f0d0 runner；它是**重复准备**，只留作交接，不作为另一候选，
后续统一 root cfd378 版本。不重复实现、原 runtime 与旧 adapter 未改。
不重复已过的 12 类设备门，不宣称它能消除 BF16 hidden gather 或 MM 新形状调优。
随后同基点短 pair 核选中次数、DB/KV、完成/token 数与原结果；波动标待确认并保留代码与原件。

当前本文记录的是源码审计、coverage 准备和两个性能候选计划。
除 root 后续明确回执的运行外，本 owner 没有执行任何新设备实验，不把准备完成写成收益。

## 5. 请求重排的实际反证：官方负载不是默认 greedy

不能直接把 `InputBatch.swap_states` 用于当前随机采样并声称每请求 RNG 不变。
该方法确实移动 request、KV 行、采样参数与 per-request generator，
但没有 per-request generator 时，随机噪声仍按物理行分配；行交换会改变噪声属于哪个请求。
为避免该问题，曾提出仅 `all_greedy=True` 做稳定分区、随机分支完全回原路。

root 随后只读取回精确安装源，位于
`experiments/source-audits/20261021T174453Z-benchmark-sampling/`：

| 实际来源 | SHA256 |
|---|---|
| `vllm/benchmarks/serve.py` | `b09e85eed6f5f7a9075b40a19fc1dd8e94a1c449665c2c6510f349e0409e77b7` |
| `vllm/benchmarks/lib/endpoint_request_func.py` | `5fd4b66d9ac6a88a278c2b7d65dcd17b8a9424279859ade14bddb69e342a312d` |
| `vllm/v1/sample/sampler.py` | `1a2f18ddc91c89f3744ab5a93624be056bf20b7a8b2e6e13d0236182718a2253` |

`serve.py:1726` 的 temperature 默认 None，`:2040–2074` 仅把非 None 参数写到请求，
并明确警告已经不再默认 greedy；endpoint `:175–188` payload 本身也不设置 temperature。
原官方脚本和短测脚本都没有覆盖 temperature，归档模型 `generation_config.json` 为
`do_sample=true / temperature=1.0 / top_p=0.95`。
真实 coverage 的 `server.log:96` 还明确确认这两个模型默认值覆盖了服务默认采样参数；
客户端 log 也记录 `temperature=None, extra_body=None` 和同一非 greedy 警告。
这不是基于旧版 vLLM 默认值的猜测。

actual sampler `:256–271` 证明 all-greedy 在随机 top-p 前返回，原 greedy 稳定分区机制可以
作为 CPU 策略边界保留；但本负载常态使用随机分支，只可能碰到 driver 的显式 greedy smoke。
**root 已取消 greedy 专用 GPU 排队，没有为它制作服务补丁或安排长 screen。**
不能改温度让候选命中，也不能把 smoke 命中当主负载优化。
后续转 Attention 内部的索引映射，保外部 request/token/RNG 行原样。

## 6. 下一项最小设计：3D 直接读取 request-index，原行写回

此节及 CPU proof 是设计，**没有新 GPU kernel、runtime、安装器、服务或性能门**。
它依据 exact 54c unified Attention 与 59d9 helper，而非更换 backend 或更新框架。
目标是覆盖真实的前缀外 single-query，不改整批 GEMM、RoPE、KV 写、请求顺序、采样或 RNG。

### 一次 CPU plan 与三种行号

builder 已持有 CPU query offsets。对正长度、真实非 padding mixed batch，建立完整且唯一的
`decode_req_indices = [i for i if query_len[i] == 1]`，原顺序保留。
只在确有前缀外 single-query 且 `0 < D <= seq_threshold_3D` 时选中；D 超容量、纯 decode、
没有遗漏或未知 feature 全部回原 C3。map 必须包含**所有** single-query，不能只选一部分后
让 2D 无条件跳过全部，否则会漏写。

一次 H2D 传 int32 request-index map；D<=64 时最多 256 字节。继续使用原 query offsets、
seq_lens、block table、slot mapping 与 Q/output，避免每层 gather/scatter 整张量。
正式实现须强持有 pinned CPU map、GPU map 与 plan 到消费完成，建立 producer → 实际
forward current stream 的 wait，并独立 record_stream 保护分配器生命周期；不能用后者代替
readiness，也不能跨步复写仍在消费的 map。首版每步独立 map，capture、共享 KV、量化、
TD/未知 feature 等均回原 C3，不因 H2D 很小而放宽生命周期或语义守卫。
必须严格分开三种行：

| 行号 | 来源 | 允许用途 |
|---|---|---|
| `d`，compact ordinal | 3D/reducer program_id(0)，0..D−1 | 三份 softmax scratch 的全部读写 |
| `r`，原 request row | `map[d]` | 原 seq_lens、block table、原 query offsets |
| `t`，原 token row | `cu[r]`，已证明 query_len[r]==1 | Q 读取与最终 output 写回 |

### actual kernel 的必要改动位置

- 54c unified kernel `:287–300` 增加仅 3D 生效的 constexpr 分支：由 d 读取 r，
  从原 cu 取 t、原 seq_lens 取 seq_len，local q block 为 0；不再用全 batch 的 virtual CTA
  binary search 定位 decode。其余 FP tile/softmax/segment 遍历顺序保持原 C2 配置。
- GQA8 / BM16 的 `query_pos=offs_m//8` 仍有第二个无效 query 槽。
  Q 和因果位置继续用 `t+query_pos`，scratch 地址另用 `d+query_pos`，并保留
  `query_mask_0=(query_pos<1)`。不能把全局 `query_offset_0` 直接改为 d。
- `:596` segm_output 与 `:608` `store_segm_reduce_scalars` 都必须使用 compact scratch 向量；
  否则全局 token t 可能接近 2048，而 scratch 只有 64 行，会越界。
  首版严格关闭 TD/TD_QO，不能漏改另一个 descriptor 写分支后还让其启用。
- reducer `:686–749` grid 为 `(D, num_query_heads)`：按 d 读 scratch，由 r 取 seq_len，
  最终用 t 写回原 out。segment reduction 数学与顺序不变。
- 原 metadata 的 `num_seqs=N` 仍是 request row 的边界，`num_decode=D` 只用于新 grid 和
  compact scratch；不能把 N 改成 D 后再用原 r 索引 seq_lens/table，也不能把整批
  `max_query_len` 假设为 1、直接调用原 3D driver，那会保留错误的全 M grid/scratch 地址。
  新 mapped launch 必须明确设置 C2 的 BM16 / TILE16 / w2 / s1 / 16 segments。
  原 `DecodeLaunch` 仅包装原 JIT kernel 且锁 54c，派生 JIT 不自动继承该代理，
  不能拿旧 C2 FIRST_SELECTED 标记证明 mapped launch 采用了正确配置。
- 2D 仍接收**原完整 metadata 和 Q/output**，保 BM128/T64/w8/s1。
  完成原 resolve 和原无效 virtual CTA early-return 后，`query_len==1` 的 CTA uniform return；
  多 query 的 FP 循环完全原样。这样 2D 与 mapped 3D 不重复写、也不漏任何有效 token。

下文的独立首稿已实现这些地址改动，但尚未执行设备门，不宣称已正确。即使 FP 表达式保持，Triton 控制流/布局也可能变化。
新走 3D 的非前缀请求原来走 2D，归约次序不同，现有 103/105 不自动覆盖新路径。

### 成本与反证

新开销为每步一次很小 map H2D、每个 3D/reducer CTA 一次 map load 与 CPU plan，
不是 42 层重复搬运 Q。D=64 时每层约 `D*(2KVheads*16segments+16Qheads)=3072` 个
int32 map load 的逻辑访问（约 12 KiB），同一 256B map 可能被缓存；这不是实测带宽。
mapped 分支还替代了原 3D virtual CTA 搜索，净地址成本不能只数新增 load。
scratch 仍使用原 builder 容量，不增加 42 份工作区。

若原 C3 forward 的 impl 守卫通过，已有 prefix 的 mixed 步按源码本来就是
3D + reducer + 2D 三个 kernel；mapped 设计仍为三个。prefix=0 时会由一个 2D 增至三个，
需把新增 launch 算入。coverage 有 248/250 个 mixed 步创建了非空 prefix plan，
**但没有测 forward 选中，所以不能把该数当作实际三 launch 占比**。
2D 跳过的 CTA 仍会被调度并执行整数定位/early-return；不把全部 masked FLOPs 当时间收益。

对比方案保留：按 maximal single/multi-query runs 做 view 分解不需 tensor copy，
但 run 数增加会带来每层多次 attention/reducer/准备开销；全 Q gather/scatter 则每层重复
读写 Q 和 output（每份 tensor 为 `D*16*128*2` 字节，计 gather/scatter 双向流量约 4 倍，
例如 D32 合计约 512 KiB/层，未计 metadata）。现有聚合统计没有 run 长度分布，不能声称哪种
真实几何占优；direct map 是当前较低搬运成本的优先设计，仍待实际门否定。

CPU proof [`check_address_contract.py`](source/c3-mapped-decode/check_address_contract.py)，SHA
`4c4fe093f2f7e4b2c38c4025d404ce8931d1cb1c84f4a044c87afbdd89dd4a0c`，已执行通过：
锁定 54c/59d9，按 actual virtual-CTA 整数规则检查 11 个定向形状和 600 个随机/逆序形状，
验证 2D 原覆盖、跳 single 后与 mapped 输出不交不漏、map 唯一、compact scratch 上界、
N256但D64/全single/全prefill/自然前缀/D65回退。该数学模型不是 Triton 解释器，
不证明 FP、异步、编译布局或性能。

未来最短设备门须先比一个独立 oracle：原 2D 全 batch 输出中，只将 single-query 行
替换为同配置原 C2 的 compact decode 结果，按原 token t 回填。
mapped 应与这个目标逐位一致，且 prefill 行保持原结果；另核极少量 FP32 causal reference、
随机物理页、KV/RNG全哨兵、padding NaN 与连续换 map/stream 生命周期。
正确后只做一个真实形状 32/64-call、预热事件的 ABBA，包含 map 创建/传输及整层调用成本。
只有正信号才进入服务和独立 accuracy，不从合成门外推 E2E。

### 独立 mapped 首稿与最短设备门（本地 CPU 已准备，未执行 GPU）

root 已授权最小实现，四件均独立于 stable SQL+C3、default 和完整4aba补丁：

| 文件 | 当前 SHA256 |
|---|---|
| `patches/framework/biv150_mapped_decode_source.py` | `0433a8de0d1e42962d8c8c1ef671f2937107dfb5ae144447cd5f13df9b10811e` |
| `patches/framework/biv150_mapped_attention.py` | `67a9830eaa976e79d9d21f5f34ec4bbfe0215d3082d6571d415c1c8f33a85f47` |
| `patches/framework/biv150_mapped_decode.py` | `7bf4e1337b0afe7a425204a4424ff76e05ebd143feed9d00d809daf9c5d61d47` |
| `scripts/remote/validate_mapped_decode.py` | `c2ded9b854608aedb15b6279d5c84195f0a0698b49117d2b05d155216b4e98bd` |

纯 bytes transformer 只接受 exact e155 runner 与54c/59d9，runner仅追加默认关闭模块的显式启用 footer，生成 `3566099b2f336f3e7ae768adeca5b0da169748324fec26fc00b150b26b246a73`。派生 Attention 是同一 transformer 的精确产物。运行时另外锁 c524父类/1219backend/e5f C2/a129 C3；必须已装原C3 wrapper、原base forward和unified绑定，未知额外wrapper/源码拒绝。builder 使用原C3 build的返回对象，再建立完整single-query索引。原C3创建的suffix_cu仍会存在，不把这份准备开销声称已省掉。

原请求/token/采样行、KV writer及全批GEMM完全不改。实际1219 `forward`只读取cache并调用unified，writer是独立 `do_kv_cache_update`；mapped base forward调用一次不能宣称减少KV writer launch。ContextVar只影响该次base forward内的unified调用，finally复原；原始返回或异常不重试。首个成功入队forward打印 `BIV150_MAPPED_DECODE_FIRST_SELECTED real_execute=...`；plan、入队计数仍不冒充已完成的GPU工作。无权重门预期 `real_execute=0`，服务才应另见1。

plan强持有pinned CPU map和GPU map，按每步独立分配；跨stream forward先wait producer、再为GPU map record_stream。metadata正常生命周期内保留这些对象；释放后的设备物理分配由record_stream保护，pinned H2D沿用PyTorch non_blocking拷贝的allocator生命周期。capture一律原C3路径，没有为capture专设新动态映射。首版量化、TD、连接器、共享KV层、未知layout/feature、D>64和无遗漏均不选中。

`check_source_contract.py` SHA `57d4a866c386c6f2e365c3226c23d4abaacf119be4bfff3048894687063d1266` 已实际执行exit0：exact派生/runner追加、四种源码扰动或二次transform拒绝、32份FP调用/累积表达式AST不变、三个候选asset与gate pin一致、syntax及纯stdlib导入无torch/triton。最终qualname guard与pin更改后仅必要重跑这一小合同，stdout已存 `source/c3-mapped-decode/source-contract.log`。该门和此前整数地址proof都不模拟Triton，不证明设备数值或异步正确性。hardware已独立逐字核runtime7bf4/source0433/derived67a/gatec2ded9，全文只读审未见进入最短correctness设备门的阻断，未重复测试或操作GPU。以上四件现已冻结，完整依赖SHA、精确runner产物及审阅结论位于 `source/c3-mapped-decode/packaging-manifest.json`。

新设备门默认只做正确性：`[1]*10+[2019]+[1]*19`、`[127,1]`、`[7,1,9]`、`[1984]+[1]*64`。全部实际Builder/Impl、16K KV、随机物理页、共享16页旧prefix、writer整cache逐位oracle与负slot/NaN尾；比较原2D、原C3以及独立原2D+compact原C2回填oracle。显式先跑skip2D，要求single行保持哨兵且所有prefill逐位原样，再核mapped整输出逐位oracle与三行FP32容差（atol/rtol均3e-2，不能代替accuracy）。D1中间另核跨stream/释放/churn和mixed capture原2D回退；每形状同cache真实append到16385后pure-decode走原路并核只有新slot改变。所有数值比较均设备同步后执行。

可选 `--timing` 才在第一形状附一轮32-call ABBA；四对Events全部先record/sync，真实builder+mapH2D+单层forward计入窗口。baseline使用原C3 build/forward，candidate仍包含旧C3 suffix准备。没有默认扩大服务/长跑，也不把方法时延外推E2E。controller沿已审单child/互斥锁/9031+ixsmi pre/postflight/300秒/完整source归档流程，hash仅普通文件，未启用profiler。下一步仅root在唯一设备空闲时执行：

```bash
python /workspace/experiments/minicpm-s2/scripts/validate_mapped_decode.py \
  --run-dir /workspace/experiments/minicpm-s2/framework/<UTC>-mapped-decode-gate \
  --runtime-path /workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z/vllm_fl/patches/biv150_decode_launch_runtime.py \
  --mixed-path /workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z/vllm_fl/patches/biv150_mixed_decode.py \
  --policy-path /workspace/experiments/minicpm-s2/scripts/biv150_mapped_decode.py \
  --transform-path /workspace/experiments/minicpm-s2/scripts/biv150_mapped_decode_source.py \
  --derived-path /workspace/experiments/minicpm-s2/scripts/biv150_mapped_attention.py
```

如需同一正确性门通过后立即计时才加 `--timing`。远端具体Python/环境由root沿原已审门设置；本owner没有运行上面命令。尚未通过设备门、服务、整模型误差/accuracy，不能混入最终候选。

loader/复用边界：controller先复制本门、C2、C3、policy、transform、derived，以及既有 `validate_hidden_row_gather.py`（仅digest/load/utc/write）、`validate_mixed_decode.py`（make_data）、`bench_attention_dispatch.py`、`validate_block_table_candidate.py`（ROOT/preflight）和 `monitor_gpu.sh` 到新run/source；child从该目录import。原installed backend/helpers/writer再复制真实bytes，hash过滤目录。policy仅由绝对路径加载并调用私有 `_wrap_backend` 实际后端挂点，**不执行生产runner的install**；C2/C3独立归档模块由controller精确e5/a129 pin且原C3再次核installed源码/已装C2类型。derived绝对路径hash与exact54c/59d9产物双重核对。完整helper SHA在manifest，未依赖tmp或未知已导入对象。parent仍独占设备，先运行上面不带timing的命令；任何失败原样留存。

## 7. 两个小收益候选已各完成一次服务短筛，继续保留

systems 独立比较 `analysis/2026-10-22-small-framework-comparison.json`（SHA `38f3170c5c0b47edac7af285553abc1d29b00b7f5bb02b027fa4e7e4f0ec849a`）已读，结果仅4K/64请求/128输出短筛，不是official：

| 独立候选 / matched基线 | 耗时：基线→候选 | total TPS变化 | mean TTFT变化 | 两侧KV tokens |
|---|---:|---:|---:|---:|
| async174741 / A1 174402 | 39.4100407986→39.1346670017s | +0.7036569% | −0.8656382% | 521840 |
| CPUmetadata175049 / A2 175441 | 39.1852806420→39.0732484781s | +0.2867234% | +0.2344306% | 521936 |

四run均64成功/0失败、262144输入/8192输出、CPU6/32GiB、preempt0→0，DB三fingerprint相同且均516表/19270行，源码410/411逐项核过，候选各有真实EngineCore FIRST_SELECTED，结束设备idle。A1/A2容量不同不能跨pair称matched漂移；只一轮、固定顺序未随机，DB相同不保证其它cache/热状态相同。按用户要求保留源码与小信号，不据幅度淘汰，也不报稳定因果收益、不合并final、不继承accuracy。

## 8. mapped 首次设备门：首个派生 kernel 编译失败

上文第6节“未上卡”为准备时状态；root随后运行 `experiments/framework/20261021T183421Z-mapped-decode-gate`，controller203015、child203018，18:34:44Z结束exit1。该run的results `eb13f26629f950ca3df9c7ebbf6fd9870d814f1ae95352869c52677739f7366c`、manifest `eba56dbf6f642aa988e611f289ebe8bae99b5b1d7a682af3ce5410c919daad8a`，本owner独立复算17份归档source全符。`cases=[]`：原2D/C3/compact原C2调用后，首次 `derived.unified_attention(..., biv150_skip_single_query=True)` 在JIT编译阶段失败，未完成任何correctness case，不归类成数值失败或性能回退。

实际栈指向 `triton/backends/iluvatar/compiler.py:294` 的 `add_accelerate_matmul(pm, opt.use_sme)`，pybind报告SupportsInt参数不匹配，值68954357763（0x100e000003，37bit）。retained a0c和C2 e5源码未处理use_sme；新derived也未显式传此选项。仅凭该栈不能判定是backend默认/ABI不兼容、原kernel命中cache，或新JIT形参解析问题，不能猜use_sme=0绕过。

postflight 9031free、free32700MiB，root封存原件并转baseline183543唯一GPU；本owner无设备操作。并行准备的CPU servicebuilder尚未写即暂停。下一步等待baseline结束后root只读取actualcompiler/JIT/cache，再做最小有依据修复和交叉审；四候选与失败原件保持原样。独立只读复核记录 `source/c3-mapped-decode/first-gate-compile-failure-review.json`。

### 精确根因与两行修复（设备重试待执行）

root后取回 `experiments/source-audits/20261021T183920Z-compiler-cache`。actual spec JIT SHA `66a168ae959e719186771e66815e807f1e449e66c5283ef596ec3eb0e35cb775` 的 `get_corex_sme`（31–71）按**非constexpr operand位置**对满足SME layout的tensor置bit，fresh compile在761行自动覆盖use_sme。新kernel的未用decode-map dummy在2D调用中传了out：它是第36个实际operand，BF16/多维/contiguous符合条件，故新增bit36。错误值恰为 `0x100e000003 = 0x0e000003 + 2^36`。backend `CorexOptions.use_sme=0` 默认不是实际值；直接传0也会被上述路径覆盖。没有证据称所有ABI/编译默认整体错误。

最小改动是两个launch里未mapped的dummy指针改为已有 `cu_seqlens_q`（1D int32）。constexpr为false时kernel不读取该指针，mapped为true时仍传真实map。没有新GPUbuffer、禁SME、数学改动、模型超参或全局编译选项改动；全部原eligible operand位保留。旧prefix-mask派生只多constexpr，没新增真实operand，因此其旧设备pass不冲突。hardware已独立读actual JIT/backend确认该机制。

新四件身份如下，旧版仍原样保在183421/source和 `packaging-manifest-pre-sme-fix.json`，不改失败：

| 文件 | 修复后 SHA256 |
|---|---|
| source | `919e80abf5b95c55ea63aa8619fa3202cd78b0c4cc0e303df7b4197bf1898316` |
| derived | `72713a90584bc6567706fb881188afa04335230afc13e021c10f862f88d054a1` |
| runtime（只更新derived pin） | `d085ad6dcc0fd5dc26188d3e0f5801b8e394dc07a79c05a376192ec9e1e95b4b` |
| gate（只更新三asset pin） | `ede4519424d467bb4f47f52cb57429c5e489ee2324070c482225cc0499b0dc2f` |

`check_sme_operand_contract.py` SHA `cff7be424f9967f200a52f64b7b939b291ae2eb9268ac2565b5a472d7df940d3` 已运行exit0：从actual文件抽出selector AST，只有torch/os import用CPU descriptor替代，精确复现broken 68954357763，原/旧prefix/修复后均234881027，唯一差bit36。它不是native specializer/JIT/设备模拟，仍待真实编译数值门。新两行后原source合同必要复核exit0，FP32份表达式等全部不变。stdout和两行diff在同source目录；没有跑重复服务或accuracy。下一步沿第6节原命令、全部helper不变，使用新run/launcher、**不带--timing**，由root唯一owner串行上卡。

hardware已对183421原件逐字核新四件SHA和最小diff，确认source/derived只有两dummy变化、runtime/gate仅pins传播，未见修正版最短correctness门阻断；没有运行suite/GPU。四件已冻结发root，packaging manifest已更新终审/proof，旧manifest原字节另存。当前仍无任何correctness case完成；服务builder保持暂停、未新增。等待新门结果，不根据CPU复算宣布编译问题已在设备解决。

## 9. 修正版真实设备门通过，独立服务准备

root随后运行184809正确门及185023带timing门，原件在 `experiments/framework/20261021T184809Z-mapped-decode-sme-fix-gate` 和 `20261021T185023Z-mapped-decode-sme-fix-timing`。两者exit0，作者独立运行只读 `source/c3-mapped-decode/review_device_gates.py` 复核：每次17份source全SHA相符，4case全部correctness和nextdecode通过，D1中间crossstream释放/churn与mixedcapture回退通过，原C2 compactoracle逐位一致、prefill原样、显式skip哨兵、真实writer/cache/RNG/尾padding通过。runtime stats分别plans/selected=5/5和71/71，real_forward_selected均0（无模型runner预期），capturefallback各1。postflight均无GPU进程/9031free/free32700MiB。

原2D最大绝对差0.000732421875，所抽FP32行最大绝对差0.00031432509422302246。这确认单层地址和这组数值门，**不能继承整模型103/105**。首次183421失败仍完整保留，不以成功重试覆盖。

185023第一形状D29/16K、32calls ABBA（含原C3 builder及新增mapH2D、预record Events）独立复算：

| 窗口 | 原C3 | mapped | 耗时节省 |
|---|---:|---:|---:|
| host wall | 14.344921375ms | 12.435507453125ms | 13.31073118% |
| device event | 14.216219902038574ms | 12.401883125305176ms | 12.76244170% |

单形状一轮synthetic正信号，非服务收益或官方计分。`device-gates-review.json` 保存全部原件SHA和复算值，原raw只读。

独立CPU打包器 `scripts/remote/prepare_mapped_decode_source.py` SHA `a41c3858ac5d19ffbb385d9ad075635b560fb272af2c2d6b5c490f04713d2459` 已备，使用同一审阅过的 `prepare_innovation_source.py` 0ecf辅助函数。只允许原080656 code目录、全新直接code子目录、ROOT/scripts素材；核心7个SHA和既有5个BIV模块集合相符、无候选manifest才接受。修正版四件均hash pin，只有runtime/source/derived三module装入新package，gate仅前置证据；runner仍精确追加为3566。完整输入输出逐文件hash比较，内部普通文件alias解引用并记录、越界/目录symlink拒绝；不执行runtime/JIT/framework、模型或installed变更。

CPU实copy213→216、逆回runner、原base不变、拒绝现存输出/未知BIV模块/漂移asset，结果 `source/c3-mapped-decode/service-pack-cpu.json`；noTorch/Triton/framework import。本地archive已解引用MoE文件alias，没有冒称重新实测Windows symlink；远端沿已审0ecf规则。hardware已全文终审builder a41c及root launcher3455b8d，未见最短独立服务门阻断，未重跑suite或操作GPU。后续仅root在设备空闲时执行：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/prepare_mapped_decode_source.py \
  --base-source /workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z \
  --output /workspace/experiments/minicpm-s2/code/mapped-decode-<UTC> \
  --asset-dir /workspace/experiments/minicpm-s2/scripts
python3 /workspace/experiments/minicpm-s2/scripts/run_framework_screen.py \
  /workspace/experiments/minicpm-s2/framework/<UTC>-mapped-decode-context16k \
  --source-dir /workspace/experiments/minicpm-s2/code/mapped-decode-<UTC> \
  --context-screen --seed 721201 --require-log-marker BIV150_MAPPED_DECODE_INSTALLED
```

沿现有driver/原SERVER，不增加服务参数或并行GPU。启动标记不是选中证明，服务后必须另见 `BIV150_MAPPED_DECODE_FIRST_SELECTED real_execute=1`，并核同DB/容量/CPU/负载/源码及实际输出/有限值/整模型误差门。新singletons的3D归约次序改变，有正E2E信号后仍需独立accuracy；本owner不运行上述远端命令。

## 10. mapped 首轮真实服务：小幅负结果保留，不能归因冷编译

`185627-mapped-decode-context16k` 已完成exit0，32成功/0失败、524288输入/4096输出；真实EngineCore207423打印 `FIRST_SELECTED real_execute=1 decode_requests=15 forward_selected=1`。作者已执行纯只读 `source/c3-mapped-decode/review_service.py`，重算414份归档source；remote live复核报告414/failures[]、post installed54c原bytes一致。对照184244归档410份同样重算，除新三module、runner3566与innovationmanifest外无其它源码变化；SERVER/负载/seed721201、安装源码、包版本均一致。

**这是同参数/同DB对照，KV容量不完全匹配**：对照521936、候选521840（−96tokens）。最初消息中“matched”简称已向root撤回。双方CPU6/32GiB、preempt0→0；before/after四个SQLite snapshot实体均复算为相同physical/schema/logical三SHA（516表19270行），但这不证明Triton/CPU缓存、温度和主机负载完全相同。

| 原始短服务 | 时长 | total TPS | mean TTFT |
|---|---:|---:|---:|
| 最近对照184244 | 120.7632626676932s | 4375.370359560136 | 61145.73857927462ms |
| mapped185627 | 121.79016383597627s | 4338.478439947034 | 62258.128146859235ms |

候选本轮多1.026901168283075s，耗时 **+0.8503423521%**、TPS **−0.8431724993%**、TTFT **+1.8192429978%**。更早对照183543为120.484981575981s，对它描述TPS约−1.07166%，两基线容量均不同于候选；不挑较好分母掩盖负结果，也不把单层13.31%外推。

原日志提供的机制证据有限：首个mapped marker没有独立时间戳，只能定位在本地日志02:58:42与02:58:52的两个周期报告之间；它仅证明至少一次真实选中，不提供全部计划/forward数或Dprefix/Doutside分布。没有新JIT的compile/cache-hit计时；启动torch.compile/AOT cache命中消息指向原模型图，不能证明后续mapped JIT也命中。双方各出现过一个约3276tok/s的prompt低窗，不能把候选的单窗单独解释成编译暂停。CPU额外CPU offsets转换、pinned map分配/H2D、42层descriptor/ContextVar/driver开销在源码存在，但未测其时长；实际几何和层外时间比例也未知。**当前不能区分冷编译、coverage限制、CPU开销或正常波动，更不能扣除推测开销后改报正收益。**

driver/请求完成与清理通过，post19:00:37.354668Z为68MiB0%、9031双栈闭、无GPU进程；runner207242处于Z/PPid1不持设备。候选在shutdown SIGTERM后有AsyncLLM output_handler/EngineDeadError堆栈及资源清理警告，原样保留，不写完全无ERROR；不能据此修改原exit0或32个请求成功数。没有新整模型accuracy/内部有限值证明。

按root最短验证决定，仅在prefix服务/KV短门完成后做一次**代码、runtime、参数都不改**的必要repeat，复用首轮已触发形状缓存；不新增observer或cache扫描脚本。无论repeat结果如何，121.79s这轮保留，cold假说仍按证据强弱说明。现候选保留为探索，不合并stable/default、不继承103/105。

## 11. mapped 一次原代码复核：正负信号并存，暂不认定稳定收益

`191131-mapped-decode-context16k` 于19:14:52.043463Z结束exit0，32/0、524288输入/4096输出。新只读脚本 [`review_repeat_service.py`](source/c3-mapped-decode/review_repeat_service.py) **9304a2f47513ae0360b98ee86714b78d0649a7092c188fc950643d2fe42e58e2** 实际exit0，结果 [`repeat-service-review.json`](source/c3-mapped-decode/repeat-service-review.json) **81b6cacfa34cfbb619cd7be77228e07941e91bf8ed21fdcc709ca0bcaf4603d5**。首轮review及raw未改。四run归档源码分别410/410/414/414份全部重新计算SHA；候选两轮413份非manifest文件相同，`innovation-source.json`仅created_utc/output/命令output路径变化，不将完整414文件误称逐byte相同。

| 同参数/同DB短服务 | 时长s | total TPS | mean TTFT ms | KV tokens |
|---|---:|---:|---:|---:|
| 183543基线 | 120.48498157598078 | 4385.476040985142 | 60874.43063224782 | 521936 |
| 184244基线 | 120.7632626676932 | 4375.370359560136 | 61145.73857927462 | 521936 |
| mapped185627首轮 | 121.79016383597627 | 4338.478439947034 | 62258.128146859235 | 521840 |
| mapped191131复核 | 117.02865957096219 | 4514.99659944072 | 59836.11785736866 | 521840 |

对最近184244，首轮TPS−0.8431724993%/TTFT+1.8192429978%，复核TPS+3.1911867661%/TTFT−2.1418021146%；对183543分别TPS−1.0716647543%与+2.9533979264%。两个基线与候选均相差96KV tokens，**全部只是同参数/同DB描述对比，不是容量完全matched**。同候选首轮→复核TPS+4.0686651308%，这也不能区分缓存、主机状态、实际batch轨迹与波动，不能证明全热或稳定因果。

四run SERVER/负载/seed/driver/包版本/安装源码均同，八份DB实体、schema/logical三hash均相同（516表19270行）；CPU6、32GiB、preempt0→0。复核EngineCore210483真实FIRST_SELECTED为D15，marker夹在本地03:13:46–56周期日志，仍不是全程计数或精确命中时间。没有per-derived-JIT cache/compile证据；不把启动AOT命中当全热，也不把第一次负结果解释掉。复核post19:15:44.582675Z为68MiB0%、9031双栈闭、无GPU进程、414 live-source无失败；controller210306为Z/PPid1，其他owned进程已退。复核未检出ERROR/EngineDeadError行，首轮shutdown堆栈仍原样保留。

本批按root决定只做这一次不改代码复核，不盲刷、不加observer、不调整runtime来追逐分数。mapped作为有单层正信号、服务正负并存的候选保留，未合并stable/default；新的归约次序尚未通过整模型accuracy，不能继承103/105。下一框架研究见 [`2026-10-22-next-framework-priority.md`](2026-10-22-next-framework-priority.md)，本批收尾后暂停写文件供主负责人checkpoint。
