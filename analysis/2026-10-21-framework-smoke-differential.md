# 尚未解决的 greedy 冒烟差异：B0 与 C1

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：本文保留当时的差异调查和后续证据；不代表当前候选是否已集成。

本文仅为 CPU 调查，不能证明候选正确，也不能将端到端性能变化归因于 block-table 补丁。

## 已记录观察

- 对照：`experiments/framework/20261021T030349Z-b0/`。
- 候选：`experiments/framework/20261021T031102Z-c1/`。
- 两次冒烟响应均报告 8 个 prompt token、32 个 completion token，system fingerprint 同为 `vllm-0.24.0-3e22f227`。文本有较长公共前缀，在 "make predictions" 后分歧。未保存 token ID 或 logprobs，因此未知首个不同 token 及其概率 margin。System fingerprint 相同不能证明执行相同。
- Runner 脚本在任一诊断负载前，明确向 `/v1/completions` 发送 temperature 0、seed 71、max_tokens 32 和相同 prompt。两个 manifest 的 serving arguments 和包版本相同。
- 两个 server 均记录模型默认 temperature 1.0、top_p 0.95；这不能证明请求显式 temperature 0 被替换。
- 两份日志加载相同 torch.compile cache key `f7af72be36` 和以 `7a51652d906b8f2b40c1383c44ed1e7ec` 开头的 AOT 路径，均捕获 35 个 decode graph；可见启动配置一致。
- KV 容量略有差异：B0 报告 521,840 token，C1 为 521,936 token，相差 96 token / 6 block。物理内存及 serving utilization 相同。性能对比应记录此分配差异；它本身不能解释一个极小请求的损坏或容量压力，也不能证明输出应确定。

## Sampling 路径

官方 vLLM 0.24 completion 转换只在请求参数为 `None` 时使用模型默认值，保留显式零温度。
[Completion protocol](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/entrypoints/openai/completion/protocol.py)

零温度下，SamplingParams 先禁用 top-p/top-k/min-p 过滤，并在考虑 seed 之前将请求分类为 GREEDY。
[SamplingParams](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/sampling_params.py)

纯 greedy sampler 在随机 top-k/top-p 路径之前直接返回 argmax token。因此直方图 top-p 优化应不参与这个隔离冒烟。这是基于官方源码的推断；若仍怀疑 sampling，需要确认实际安装的 protocol 和 sampler 文件与所引源码匹配。
[V1 sampler](https://github.com/vllm-project/vllm/blob/v0.24.0/vllm/v1/sample/sampler.py)

## Manifest 能证明的范围

实际 B0 runner 哈希为 `446f12c0653131c9a4f5ff7783e52e1a3882d2b20cdd50a6899d218a2dc0bd64`，本地下载的 `tmp/remote-source/model_runner.py` 与其完全相同。C1 runner 哈希为 `1a969b0e7f058cd1f529a307547f7549203f8198f9e39eed36ef68767aa9aab0`；其 base-revision 指向 `d60b02367a852826f653165953f31b6dc696658e`，与 B0 干净 Git checkout 相同。负责人报告该 base 的归档附带安装 footer。随后实际 C1 runner 下载到 `tmp/remote-source/c1-model_runner.py`，完整字节以精确 B0 源码为前缀，仅追加 17 行，安装受 vendor guard 限定的候选，并包裹 shutdown 输出统计日志。这一仅 footer 的 runner 差异已独立逐字节验证。

两个 manifest 中选定 runtime patch、top-p source、安装的 block-table source、官方 benchmark 的哈希相同。全局修改的 `triton_unified_attention.py`、安装的 protocol/sampler 文件、model config、generation config 和 model weight 哈希未记录。这些缺口不能证明存在差异，也不能悄悄当作独立的相同证明。候选归档缺少 `.git` 也可能影响版本 metadata；尽管如此，两次响应仍报告相同 serving fingerprint。

## Dirty-skip 审计

未找到能明确解释首个单请求冒烟的漏跟踪修改。候选跟踪 initial/add/append/clear-row/move-destination/swap；`_update_states` 通过受跟踪方法 append 已分配 block。已有 event 协议在状态修改前等待，在准备后记录，保留 host-buffer lifetime 保护。

Runner 中识别出的直接 device-table 写入为 graph-padding zero fill。对于持续活跃的单请求，graph size 1 意味着范围 `[num_reqs:num_reqs_padded]` 为 `[1:1]`，不会覆盖 row 0。首个隔离冒烟之前预期没有请求 churn。Padded 非活跃行变为活跃时，应经过跟踪的 add/move 操作。Dummy/capture commit 不在候选 scope 内，始终执行原 copy。

条件不变量是：每个未变化活跃行等于最近一次成功上传后的 host 行；活跃 host 修改均受跟踪，没有未跟踪消费者写该活跃 device 行。只有这些前提成立，跳过才保持相等。仅 metadata oracle 可测试直接状态转换，但不能证明完整 serving graph 没有外部写入、alias、stream 依赖或其他竞争。移除本来冗余的 DMA 也可能暴露其他组件潜在的时序依赖。

## 随后的短验证证据

负责人报告真实 metadata 门禁全部通过 32 个状态机 step 和三次预热 graph replay，包含 35 次 scope 内 commit、21 次跳过上传。这减少了已测转换的不确定性，不能覆盖全部 serving 行为。原始证据仍由框架负责人管理。

之后，在同一服务中，用三个相同的 temperature-0、seed-71、32-token 请求测试未修改对照：`experiments/framework/20261021T033437Z-b0-repeat-smoke/`。请求 1 和 3 相同，请求 2 不同。Token ID 在 index 10 及之前相同，首次在 index 11 分歧（"understand" 与 "make"）。负责人报告请求 1 的 top-two logprobs 为 -1.8654984/-1.9279984（gap 0.0625），请求 2 则为精确 -1.8986071 平局。原始 ID 和 logprobs 保存在本地。

因此，基线自身在极小 greedy 探针下已表现不稳定。单凭文本不相等，不能将 B0/C1 差异归因于 dirty-upload 补丁；该发现也不排除补丁缺陷。无需仅为这个较弱的纯文本信号再启动 C0 服务；当时用户优先推进更大的 direct-decode launch 候选。

## 可证伪解释与当时的后续建议

1. 真实 H2D/slot-mapping oracle 的 32 个 step 与三次 graph replay 已通过。这只验证所测 metadata 转换；未来若失败，可先定位具体 step，再启动模型测试。
2. 所要求的 control-repeat 检查已如上完成。未来差异探针应重复相同隔离 greedy prompt，并保存 `return_token_ids: true`，最好再保存 `logprobs: 2`。若 B0 自身不同，跨实现文本相等不足以单独作为补丁门禁。自身不稳定的数值原因仍是假设。
3. 若未来对照稳定，C0 消融可使用同一 C1 归档、subclass、wrapper 和计数器，仅禁用 skip。重复极小 greedy 请求可区分原因。稳定 B0=C0 而 C1 不同，则 skip 行为具有因果性，应否决或调试到解决。若 C0 也不同，应检查源码/环境是否相同、基线数值敏感性，或跳过传输之外的影响。
4. 在首个不同 token 处，对相同强制输入前缀比较 top-two logprobs。极小 margin 支持数值敏感解释；较大分歧或 metadata 不匹配支持正确性缺陷。Margin 单独不能证明框架补丁安全。

问题解决前，将 C1 保留为有未解决 greedy 输出差异的诊断候选。请求零失败和 metadata 微测成功，不能替代输出/精度验证。不设百分比性能门槛：正确性与可复现性建立后，小而稳定的收益仍值得保留。
