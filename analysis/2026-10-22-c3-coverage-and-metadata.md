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

没有实现时不宣称这些修改已正确。即使 FP 表达式保持，Triton 控制流/布局也可能变化。
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
