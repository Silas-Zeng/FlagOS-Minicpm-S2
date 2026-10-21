# BI-V150 硬件适配记录

本地实测与源码适配仅覆盖天数 BI-V150。沐曦－曦云 C500 由队友负责，本文数据不外推到该平台或团队总分。

> 历史记录：以下硬件信息、当时配置和短筛结果按原始证据保留；后续状态以项目工作记录为准。

## 已验证的硬件事实

所引厂商文档将 BI-V150 描述为 ivcore11、7 nm 加速器，配有 HBM2e、PCIe 4.0 x16，板卡功耗上限为 350 W：

<https://moark.com/docs/compute/clusters_gpu/iluvatar/iluvatar_BI-V150_gpu>

该页面列出的关键适配信息：

- 原生 warp size 为 64 个线程，不同于 CUDA 常见的 32 线程；
- global-memory 访问应按 128 字节对齐；
- 支持 FP32、FP16 和 BF16 推理；
- INT/FP8 路径有特殊工具链要求，不在本候选范围内。

租用实例可见 32 GiB 和 16 个计算单元。厂商页面描述的是 64 GiB 完整板卡配置，因此本次比赛运行实际受本地 32 GiB 切分实例容量限制。

## 固定版本中观察到的 vLLM 默认值

- 启用 chunked prefill；
- 启用 virtual/async scheduling；
- 启用 prefix caching；
- 默认 `max_num_batched_tokens` 为 2,048；
- 捕获 35 种 decode CUDA-graph size，最大到 512 个请求。

源码路径：

```text
/usr/local/lib/python3.12/site-packages/vllm/config/scheduler.py
/usr/local/lib/python3.12/site-packages/vllm/v1/core/sched/scheduler.py
/usr/local/lib/python3.12/site-packages/vllm/v1/attention/backends/triton_attn.py
```

## 非算子短筛

所有候选采用同一组并发冒烟：4K 为 16 请求/16 输出 token，16K 为 8 请求/8 输出 token。

| 设置 | 4K tok/s | 16K tok/s | 决策 |
|---|---:|---:|---|
| 默认（`block16`、batch2048、prefix 开启） | 5045.59 | 3554.45 | 保留 |
| KV block 64 | 3154.38 | 3400.29 | 否决 |
| batched tokens 4096 | 1192.89 | 1628.14 | 否决 |
| batched tokens 8192 | 887.23 | 1729.07 | 否决 |
| prefix cache 关闭 | 3170.73 | 3329.03 | 否决 |
| sampler `torch.compile` 开启 | 3131.36 | 3330.25 | 否决 |
| 同上，使用预热后的 compile cache | 3144.42 | 3535.92 | 否决 |

以上为配对集成测量，不是官方四轮分数。

## 解读

BI-V150 切分实例表现为一个计算单元相对较少、KV 容量约束显著的 16-SM 设备。给 scheduler 更大的 token batch 会降低交互性，也未改善总吞吐；原生 2,048-token scheduler window 更适合该条件。128 字节对齐要求不代表更大的 KV page 更快：64-token page 在两个短负载中都更慢。

Prefix-cache 命中率为 0% 不代表应关闭 cache。关闭后配对冒烟更慢，说明 hashing/metadata 的节省未抵消 cache 路径优化的损失。

当时剩余的非算子候选证据较弱：

- 将捕获 graph size 缩减到官方最大并发 64；主要减少启动成本和 graph 内存，尚未测得 token 工作量收益；
- 只有定向 profile 证明占比显著后，才研究页表及 host-device metadata copy；
- 只有 profiling 出现 host throttling 后，才测试其他 CPU 线程上限。

上述五组配对筛查后，未继续参数扫描。
