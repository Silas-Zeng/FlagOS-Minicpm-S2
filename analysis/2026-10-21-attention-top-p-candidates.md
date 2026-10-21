# BI-V150 MiniCPM5-2B：通用 Attention 与 top-p 候选

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：以下状态和结果按当时证据保留；最新候选与验证状态以项目工作记录为准。

当时状态：候选通过微基准、端到端冒烟测试和官方 `math_500` Level 3 门禁。短验证已确定保留方向后，完整官方性能重复测试按用户指示停止。

本文所有测量均使用租用实例中唯一可见的 BI-V150。GPU 任务串行执行。

## 1. Top-p 采样器

官方模型的生成配置解析为：

```text
do_sample = true
temperature = 1.0
top_p = 0.95
top_k disabled
```

上游 Qrita 风格的 top-p-only kernel 在 130,560 个 token 的词表上重复进行有界搜索。在候选 decode profile 中，旧 `_topk_topp_kernel` 每个采样 decode 迭代占 5.301 ms。

替代实现先执行一次 split-parallel 在线 `max + sum(exp)`，随后进行两次 256-bin 加权直方图缩小范围和一次 mask。第一轮直方图将阈值缩小到一个 logit bin；第二轮利用该 bin 以上的累计概率质量定位保守阈值。在已测分布矩阵中，它从未过度裁剪概率质量。

### Kernel 耗时，`[64, 130560]` FP32

| Kernel 路径 | 中位数 |
|---|---:|
| 上游 top-p-only Triton kernel | 6.39 ms |
| 直方图候选，两轮、确定性单 split | 0.459 ms |
| 加速比 | 13.9x |

服务 profile 确认实际形状与微基准接近：

| 候选 kernel | 调用次数 | 总耗时 | 单次耗时 |
|---|---:|---:|---:|
| `_weighted_hist` | 8 | 1.108 ms | 0.138 ms |
| `_apply_mask` | 4 | 0.295 ms | 0.074 ms |
| `_row_stats_partial` | 4 | 0.291 ms | 0.073 ms |
| `_hist_walk` | 8 | 0.061 ms | 0.008 ms |
| `_row_max_reduce` | 4 | 0.020 ms | 0.005 ms |

早期四 split 诊断将每个 decode 迭代的 sampler 过滤总耗时降至约 0.444 ms，上游为 5.301 ms。该变体在 batch 16/64 暴露出浮点 atomic 顺序变化，因此提交策略改为每行一个 program。确定性候选在 64 行微基准中仍低于 0.46 ms。

### 正确性门禁

测试矩阵覆盖 logit scale 0.5、2.0、5.0 和 top-p 0.0、0.5、0.9、0.95、0.99、1.0，还包括重复最大值及全为 `-inf` 的行。

- 所有通过的用例均未丢弃应保留的概率质量。
- 在 `top_p=0.95` 时，额外保留概率质量的最大值为 `7.24e-5`。
- 所有已测 top-p 中最差用例额外保留 `3.30e-4` 的概率质量；未漏掉应保留的质量。
- `top_p=0` 时，两个重复最大值均被保留。
- 全 mask 行仍然全部被 mask。
- 最终单 split kernel 在 batch 1、8、16、64，logit scale 0.5、2.0、5.0 下重复调用 20 次，保留集合逐字节相同。

## 2. 通用 TRITON_ATTN prefill

活跃路径是 vLLM 通用 `unified_attention`。MiniCPM5-2B prefill 的形状为 16 个 query head、2 个 KV head、head size 128、GQA factor 8。

上游 launch 启发式选择 `BLOCK_M=16`、KV tile 32、4 warps、3 stages。扫描找到了 `BLOCK_M=128`、KV tile 64、8 warps、1 stage。

### `[query=2048, kv=16384, block=16, batch=1]`

| 配置 | 中位数 | 相对参考的差异 |
|---|---:|---:|
| BM16 / tile32 / 4w / 3s | 75.43 ms | 参考 |
| BM128 / tile32 / 4w / 1s | 18.66 ms | 0 |
| BM128 / tile32 / 8w / 1s | 12.13 ms | 0 |
| **BM128 / tile64 / 8w / 1s** | **10.66 ms** | **4.88e-4** |
| BM128 / tile64 / 8w / 2s | 10.98 ms | 4.88e-4 |
| BM256 / tile128 / 8w / 1s | 13.27 ms | 4.88e-4 |

最优候选加速比为 7.08x。

### `[query=16384, kv=16384, block=16, batch=1]`

| 配置 | 中位数 |
|---|---:|
| BM16 / tile32 / 4w / 3s | 318.24 ms |
| BM128 / tile32 / 8w / 1s | 50.43 ms |
| **BM128 / tile64 / 8w / 1s** | **44.70 ms** |
| BM128 / tile64 / 8w / 2s | 45.32 ms |
| BM256 / tile128 / 8w / 1s | 56.58 ms |

最优候选加速比为 7.12x。相对参考 launch 的最大 BF16 输出差异为 `3.91e-3`。

### `[batch=8, query=2048, kv=16384, block=16]`

| 配置 | 中位数 |
|---|---:|
| BM16 / tile32 / 4w / 3s | 593.18 ms |
| BM128 / tile64 / 8w / 1s | 83.37 ms |

在 batch 8 下，最优候选加速比为 7.12x。

### Decode 实验（已否决）

真实 decode 路径使用 3D 分段 softmax。对于 MiniCPM 的 GQA factor 8 和两个 KV head，launch 阈值在 batch 64 选择 3D kernel。

| 形状 | 上游 BM16 / tile16 / 4w / 3s | 候选 BM16 / tile32 / 4w / 1s | 加速比 |
|---|---:|---:|---:|
| batch64, kv4096 | 1.705 ms | 1.128 ms | 1.51x |
| batch30, kv16384 | 3.021 ms | 1.955 ms | 1.55x |

16K decode 候选的最大 BF16 输出差异为 `1.46e-3`。

该 kernel 级收益未获端到端接纳。严格使用组织方命令的 `math_500 Level 3` 测试降至 **83.8%**，平均输出长度从约 3,345 增至 10,996 token。因此，最终默认补丁不包含该 decode launch 策略。它作为 A/B 对比保留在 `patches/candidates/vllm-plugin-FL-biv150-a-plus-b-rejected.patch`。

选中的 prefill 策略限于：

```text
vendor == iluvatar
head_size == 128
num_queries_per_kv == 8
```

Decode 保持上游策略。

## 3. 端到端候选结果

### 16K 诊断

负载：16,384 输入 token、64 输出 token、并发 64、64 个 prompt。

| 候选组合 | 总时长 | 总 tok/s | 平均 TTFT |
|---|---:|---:|---:|
| 仅直方图 top-p，早期完整 prefill 服务 | 253.46 s | 4153.15 | 126.16 s |
| 由提交源码补丁路径启用 Attention + top-p | 228.29 s | 4611.14 | 113.42 s |

该形状是诊断负载，并非官方 128-prompt/1024-output 用例。更早的 16K 官方基线在 128 个 prompt、128 输出 token 下，总吞吐约 858-862 tok/s，平均 TTFT 约 637 s。由于 prompt 数和输出长度不同，该对比只能说明方向。

### 4K 诊断

负载：4,096 输入 token、256 输出 token、并发 64、64 个 prompt，seed 为 20261021。

| 候选 | 总时长 | 总 tok/s | 平均 TTFT | 平均 TPOT |
|---|---:|---:|---:|---:|
| 仅 top-p | 138.00 s | 2018.34 | 38.68 s | 321.99 ms |
| Attention + top-p | 118.73 s | 2345.80 | 15.15 s | 333.18 ms |

相对同 seed 的短 top-p-only 测试，组合候选使总吞吐提升 16.2%、总时长下降 14.1%。两者使用不同服务实例，因此属于配对诊断，不是官方分数。

### 精度

从提交的 plugin 源码路径启动，保留 prefill Attention 和确定性 top-p 补丁，严格使用组织方命令，在全部 105 个 Level 3 样本上得到 **96.2%**，高于要求的 0.95 阈值。

### Fused sampler 候选

独立候选将 top-p 阈值与 Gumbel-Max sampling 融合，在 64 行微基准中将完整采样尾部从 `1.695 ms` 降至 `0.712 ms`（2.38x）。稀疏分布 TV distance 为 0.022，所有采样 token 都在精确 top-p 支持集内。

服务级短配对结果有正有负：16K 总吞吐从 3554.45 提升至 3983.53 tok/s，但 4K 从 5045.59 降至 3879.54 tok/s。因此仅保留为独立候选，默认未启用：

```text
branch: codex/biv150-fused-sampler
commit: 40c1f1e
```

该候选补丁是保留的最终补丁之上的增量。

## 4. 已否决或无效的测量

非算子设置采用相同的两组并发短冒烟筛查：4K 为 16 个请求、16 输出 token，16K 为 8 个请求、8 输出 token。这些绝对值是集成测量，并非官方吞吐分数，但每个候选都直接与默认服务配对。

| 设置 | 4K tok/s | 16K tok/s | 决策 |
|---|---:|---:|---|
| 默认：block16、batched tokens 2048、prefix cache 开启 | 5045.59 | 3554.45 | 参考 |
| KV block size 64 | 3154.38 | 3400.29 | 否决 |
| `max_num_batched_tokens=4096` | 1192.89 | 1628.14 | 否决 |
| `max_num_batched_tokens=8192` | 887.23 | 1729.07 | 否决 |
| Prefix cache 关闭 | 3170.73 | 3329.03 | 否决 |
| Sampler `torch.compile` 开启 | 3131.36 | 3330.25 | 否决 |
| 同上，使用预热后的 compile cache | 3144.42 | 3535.92 | 否决 |

- 更大的 KV block 在两种形状的短测试中吞吐均更差。
- 将 scheduler token cap 提高到 8192，在两个混合并发客户端下造成严重退化；设备的 16-SM 容量使默认的 2,048-token chunk 更有效。
- 随机 benchmark 报告 prefix-cache 命中率为 0%，但关闭 cache 的配对冒烟仍更慢，因此保持开启。
- 首次 `math_500` 使用零温度、2,048-token 限制，以及 `/v1`，未使用组织方明确的 chat-completions endpoint。结果为 72.4%，仅保留为协议不匹配记录，不作为候选精度结果。
- FlagGems paged FA2 在自身 tile 调优后，端到端仍慢于通用 Triton，因此未选用。
- 重复使用相同诊断 seed 会预热 prefix cache，将名义 167 s 的测试缩短至 44 s；这些预热 cache 结果从对比中排除。
- 更早一次 16K/32-prompt 测试使用上游 Attention launch，在高 GPU 利用率下停滞数小时。优化路径完成了 64-prompt 诊断，未出现该停滞。

## 5. 源码集成

提交的 plugin 新增：

- `vllm_fl/patches/biv150_top_p_triton.py`
- `vllm_fl/patches/biv150_runtime.py`
- Iluvatar 后端模块中的幂等调用。

从恢复的上游 vLLM 文件出发，将 `PYTHONPATH` 设置为 plugin worktree 后，plugin 会：

1. 将 top-p-only dispatch monkey-patch 到新的 Triton 模块；
2. 应用固定的 vLLM 0.24 源码挂点，修改通用 Attention launch 策略；
3. 刷新已导入的 `TRITON_ATTN` 函数引用；
4. 在可修改的 Attention 源码中记录幂等标记。

源码补丁服务成功启动，完成 8 请求冒烟，失败数为零。
