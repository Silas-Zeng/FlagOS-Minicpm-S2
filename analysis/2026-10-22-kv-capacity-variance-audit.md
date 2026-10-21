# KV池相差6块的专项审计：已知差额，来源仍未知

本地CPU只读审计，范围仅天数 BI-V150 16SM/32GiB 本实例。没有SSH、GPU、新测试、利用率/固定KV设置或服务参数修改。三轮完整原件与冻结源码优先，不用A100或其它平台经验补原因；完整source/DB/official验收由root和framework负责。

## 三轮事实与205819实际执行

| 运行 | 模型source | VERIFY | KV token / 单组块 | 结果用途 |
|---|---|---:|---:|---|
| 204159页序 | 固定0e/31cc/616/c95f | 1 | 521936 / 32621 | 全42层恢复回读诊断 |
| 205219 stable | 冻结080656 | 0 | 521936 / 32621 | 32/0，220.407047817秒；root回执DB518/19337三SHA不变 |
| 205819页序 | 与204159同四件 | 0 | 521840 / 32615 | 32/0，220.921083583秒；root回执DB518/19337→519/19340 |

完整205819 run/control在 `experiments/framework/20261021T205819Z-kv-pair-page-order-context16k-long{,-control}`，root包 SHA `5e0873334997c59899d9dad5653d80529729eb508b8ce7c93e74587311b86e82`。专项 [JSON](source/kv-transaction/205819-page-order-hardware-review.json) SHA `05905a3589997903e09425b1aebcef57c9d310a906a30f1e3c49dc03be332090` 保实际control四SHA、三轮启动日志/source SHA、原命令、页段、ACK及边界；205819 server.log SHA `1e31c258940f9dfae4a5b9c64bff8434da6ae912cabc2d9d3a7d2a92768c8e03`。

这轮SAVE实际R16688、1043页、717717504B=684.46875MiB、23段×42=966calls，不能照抄前两诊断的16704/1044/1008。PRIVATE marker1043→66；真实ZERO/RESTORE同一1043正数唯一升序页，独立66段：232..1027（796页）、30959..30995（37页）、31000..31146（147页）加63个单页；ZERO/RESTORE均2772次且真实done成功。6runner检查全True，原后继输出消费16个scheduled token，DROP成功hostheld=False。

VERIFY0有实际双重证据：control command明确环境0，SAVE/ZERO/RESTORE ACK均diagnostic_verify_requested=False、extra_pinned_bytes=0，RESTORE没有verification回读字段。它不是本轮bitwise门；旧VERIFY1字节结果保持独立。首defer及462总skips只按本轮记录，不把历史454或其原因复制过来。

## 精确差额与缺失的内存证据

每单组完整逻辑块为 `42层×2KV×16token×2head×128×2B=688128B`，已实证normal42布局与scope不变。因此：

```text
(521936−521840)/16 = 6块
6×688128 = 4128768B = 3.9375MiB
```

这是**KV池payload差额**，不是某个profile项恰好改变了这些字节。实际KV配置生成器的available值/取整余数没有在本批日志给出，不能用池差倒算出某个Torch分配、4MiB chunk或图池就是原因。

实际三轮control中的 `vllm_fl/worker/worker.py` 均SHA `a8de1780d1b41bf4889c26f3d593e6ec54e91a5f61996ce64b4d79f2a97efa24`，`platform.py`均 `e6f231af2c90f93116ebed7a8a2ce640bcc2d4c31ba5fde2e0fa0cbd8236ea36`。原SERVER均util0.85/maxlen131072/FULL_DECODE_ONLY、32GiB可见设备；这些条件相同不等于所有profile实测中间值相同。

冻结WorkerFL `determine_available_memory` 495–652的常规路径是：

```text
requested_memory = init_snapshot.total_memory × gpu_memory_utilization
available = requested_memory − weights_memory − non_torch_increase
            − torch_peak_increase − cudagraph_memory_estimate_applied
```

MemorySnapshot84–130以Torch mem_get_info、memory_reserved、allocated peak构造数据，156–192 profiling取前后差；数值需要当次观测，不能从源码猜。本批三份启动日志只有最终 `GPU KV cache size`（205219:87、205819:89、204159:89），没有Initial/Requested/Free after profiling、nonTorch、torch peak、weights的可用明细；连预期INFO `Available KV cache memory`也未出现。**缺日志原因同样未知**，不猜logger/路径或环境状态。

两个范围有限的源码排除项：

- 同一冻结PlatformFL的 `is_cuda()`只对vendor nvidia返回True，iluvatar为False；所以在这份WorkerFL方法中受该条件控制的显式 `profile_cudagraph_memory()`估计扣减分支不会执行。它只是固定源码推论，不是采得了所有内存项；不能扩大成“所有与图相关的间接内存变化均排除”。
- worker31cc只在实际SAVE分支读取VERIFY环境并分配额外pinned CPU核验buffer。SAVE的实际负载发生在KV池已确定之后；没有 env0 在sizing前走另一buffer分配分支的代码证据。因此不能拿VERIFY1的后置核验buffer解释这6块启动差异。

**结论：当前没有6块差额来源的直接证据，原因未知。** 既不归因于页序候选，也不归因于cache/allocator/NCCL/其它进程或显存“波动”；这些名词不是本次观测到的因果事实。历史同一基点多次出现两种容量已记录，不能据此挑一轮解释为确定原因。

## 比较和后继边界

205219与205819容量不同，且候选DB运行中改变，两轮不满足归因pair条件。保留全部32/0和原始时长，不给“页序提升/退化百分比”，不拿204159的227秒VERIFY1诊断替换对照，不挑最好。DB共同起点门只保证启动前指纹条件，不能保证启动后无调参或容量相同。

root若选择仅一次原参数stable复核寻共同容量，仍须新run/完整原件、DB/容量/CPU/源与实际协议命中全部重核；没有共同条件就记录无法配对，不能修改util、限制KV或加假buffer凑容量。以后若有必要的原值诊断，应只在具体批准的新run保存实际profile项，不改当前冻结候选或开启额外GPU工作。本owner本批到此完成写入后暂停，等待root一致发布/ZIP及解锁。

## 后续事实与已批准的最短标量诊断

归档写锁已解除。root回执213016 stable再次521936、213616 capacity再次521840；214400 FULL完整原件则直接记录521936（server.log SHA6f3a0eec…）。FULL三件是新额外protocol模块，VERIFY1真实整页恢复通过，故“只要多protocol模块必定固定少6块”没有事实支持；仍不能归因FULL、VERIFY或缓存，更不能补造旧profile值。214400诊断不是共同容量性能pair。

root批准单次纯标量观察器及未来两个最短原参数启动，详细 [观察器说明](2026-10-22-kv-memory-startup-observer.md)。最终observer6a772a、唯一合同0bec，已获framework只读终审。它不提前import WorkerFL，在自然已加载父Executor显存入口接入已创建worker，原父RPC只一次；用原CM现成result读取snapshot/nonTorch/peak/available，finally恢复三hook。无新增GPU采样/同步/MemorySnapshot，原返回/异常不变，derived单列。当前仍无该观察器设备结果；原因保持未知。

后续两个观察器启动已完成：215849 stable与220122 capacity均KV521936；本owner独立比较全部profile字节组成、worker值、4snapshot非时间字段、derived和原返回/logger，完全相同，仅profile_time与timestamp变化。详见 [两启动专项JSON](source/kv-memory-observer/startup-pair-review.json) SHA `0fc5509022de9d376996f11fcc8342800fc04c1410e11097a2ad9c1c4fff794a`。weights5101233152、nonTorch1000341504、peak656424960、nonKV6757999616、requested29205777612.8、available22447777996.8→原int22447777996，graph0，两轮均一致；所有hook实际恢复成功。

因此本次**未复现六块差异**，没有贡献项变化可用于定位历史来源。当前INFO/DEBUG缺失有当次root WARNING30继承链支持，仍不能倒补旧轮logger现场或字节值。root决定不追加startup样本，下一计划将同一观察器纳入原参数VERIFY0对照；本阶段只保存，不变更源/参数或扩大实验。历史原因仍未知。
