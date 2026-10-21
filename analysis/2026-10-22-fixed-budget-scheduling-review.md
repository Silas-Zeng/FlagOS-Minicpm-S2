# 固定2048预算的调度与chunk对齐：本轮研究结论

仅研究天数BI-V150 16SM/32GiB、6CPU、本项目MiniCPM5-2B；不实现、不改服务参数/bench/量化/采样，不启动SSH/GPU。root当前213016容量性能stable及后继213616的设备工作均由其拥有。本轮从精确安装源和已测记录出发，**没有找到足以支持立即实现的全新“大收益”调度方案**；只保留一个BQ16中间chunk向下对齐假设及其具体反证。不是把已有小信号淘汰，也不把资料中的其它GPU结果套成本机收益。

## 实际调度、混合执行与容量约束

actual df780 `Scheduler.schedule` 先按running顺序安排工作（435以后），再在剩余token budget中安排waiting（672以后）；running/waiting都用min裁到本步预算，分配失败则原FCFS尾部抢占（522–572），waiting的full-sequence-fit仍由原allocator决定（872–887）。`_preempt_request:1107–1128`释放请求块、重置computed并prepend waiting。不能把“实现chunked prefill/将decode与prefill混合”当尚未存在的新策略。

本轮按root确认的总预算2048分析；该值保持不变。e155以scheduler实际token数进入 `_determine_batch_execution_and_padding:3890`，FULL_DECODE_ONLY只对uniform decode使用完整图；普通mixed不能因此自动补到2048。单卡TP1/无sequence parallel额外对齐时，mixed减少调度token会改变backbone实际M。server的compile range上界2048是辅助记录，不能单凭它反推任意运行配置。

a129 C3只拆天然连续singleton前缀，将suffix query offsets减去prefix，分别调用原backend；它没有重排请求或把所有decode均拆出。173003真实计数已有prefix外singleton，因此下面模型**明确条件化为完整decode前缀+仅一个prefill suffix**，不是把D29/P2019旧构造当服务全程几何。

粗容量量级也不能替代实际峰值：无共享/无APC命中且全部32个16K prompt同时驻留时，需要524288 token，已超过521840池2448 token（105283584B）；若再让全部1024输出同时保留，则557056 token，超过35216 token（1514569728B）。真实请求会错峰完成、共享/命中和回收，故不是“必然需额外1.5GB”或具体抢占次数的证明。212106真正观察的是一次抢占/快拒462/之后恢复，不能把running数量直接换算成完整逐步KV峰值。

## 不重复的已测/已存在机制

- `experiments/queue.md` 第9项：batch4096/8192等短筛已慢；不能把改budget当本轮代码创新或重做参数扫描。
- full-output-growth115950已实际CHECKED/DEFERRED，消掉一次抢占却没有吞吐正信号、TTFT更差；不重新按所有未来输出预留。
- terminal181041在实际失败时没有确定终态/private可释放页，故不再做terminal-drain。
- zero-dirty block-table已有原实现、32次迁移/replay门和服务短筛边界，不重新“发现”未变表上传。
- native22e `free(reversed(req_blocks))`加3fc5 hashed页append保输入优先序，APC已经软保前缀/先牺牲尾部；“只释放尾页、把前缀硬pin住”会让其它running请求可用容量减少，且涉及旧frame/cache计数/runner resume，不能声称免费替代全抢占。没有新的实际收益证据，本轮不把它列新候选。

## 一手资料的适用边界

[vLLM v0.24优化文档](https://docs.vllm.ai/en/v0.24.0/configuration/optimization/#chunked-prefill)解释了decode优先、剩余预算chunked prefill的权衡；它的更大budget建议有模型/GPU条件，不是本机16SM或比赛原参数的调参授权。实际installed分支仍以df780为准，不合并公开更新代码。

[Sarathi-Serve论文页面与论文](https://www.usenix.org/conference/osdi24/presentation/agrawal)说明混合批可摊薄decode的线性层权重开销，也指出chunk过小的固定开销风险。因此把现有mixed强行拆成prefill-only/decode-only两次forward，不能仅凭阶段分离声称更快。其pipeline收益亦不能套给本机TP1/PP1。

[Elastic KV Cache原论文](https://arxiv.org/html/2608.23658v1)报告了激活reserve借给KV的实现及受限收益/负结果，提醒先证明实际reserve/成本。该论文使用A100/CUDA VMM；本机CoreX VMM能力、可借内存和切换成本未被取证，本轮不据此提出扩大池/静态偷用activation内存或宣称容量差96 token是某分项原因。

## 唯一小候选：仅中间prefill chunk按BQ16向下对齐

假设原本给某prefill的q大于0且尚有更多输入，则改为 `floor(q/16)*16`；末尾原样、总cap2048/请求内容/FCFS不动。它把少数token留到后一步，不是删除计算。scope还必须排除q<16、encoder/spec/特殊attention等，且不能改已排队SchedulerOutput。**当前只有研究模型，未写runtime或安装候选。**

实际54c在该模型上使用BM128、GQA8，因此BQ16；T64、w8、s1不变。重要区别：valid query块数为 `ceil(q/16)`，但实际launch上界是 `floor(q/16)+num_seqs`，多出的CTA会在原resolve后early-return。对C3单prefill suffix `num_seqs=1`：

```text
P2019: 127个launch/head，127个有效q块
P2016: 127个launch/head，126个有效q块 + 1个早退
```

因此“少一个partial块”不等于少一个launch，更不等于16SM网格变整齐。2个KV head合计仍254个CTA。若D29/剩余P2019强求总CTA为16的倍数，向下取下一120 q块/head，P最多1919（若同时BQ对齐则1904），要额外空耗100或115个token预算，而不是3个；没有证据表明它能补回代价。16SM也不等于每SM只能驻留一个CTA，不能把整除当性能定理。

满预算原线性层M为 `D+(2048-D)=2048`。向下对齐后对D1..31有 **M2033..2048共16种满chunk形状**，反而比恒M2048增加调优/编译形状，不能声称减少GEMM shape多样性。给定BM256不变，M2033..2048仍是8个M tile，不能省大GEMM主体；新M是否命中相同autotune配置也尚未证明。

## 可复现整数模型与反证

纯整数脚本 [`geometry.py`](source/chunked-prefill-alignment/geometry.py) SHA **9183047e99ee86e28c03a4488d407989db2cfb2ea196041abc651deb86cf4121**，结果 [`geometry.json`](source/chunked-prefill-alignment/geometry.json) SHA **a9c1def472d1afd0061bce7f8ab0168089459e978c3a8dcb9097f61b7aa43a37**。它固定16K prompt、D恒定的构造假设，从ctx0开始按原q与对齐q分chunk；不导入Torch/Triton、不实现调度、不做服务模拟。真实D会改变、C3可能有prefix外singleton，所以不能把模型数值叫实测。

每chunk的有效q块为ceil(q/16)，launch块为floor(q/16)+1；对第b个有效q块，actual59d9 causal/no-window公式为：

```text
max_prefix = min(ctx + 16*b + 16, ctx + q)
KV_tile_loops = ceil(max_prefix / 64)
```

累加所有chunk/b得到每KV head的QK tile对数。host query分块对齐时，ctx+局部位置恢复相同绝对位置；不能把chunk数粗暴乘进KV重读倍数。下面只列构造成本，不是字节/带宽/latency：

| 构造D | forward数 原/对齐 | 有效q块 原/对齐 | launch块 原/对齐 | QK tile对数减少 | 固定BM256总M tile 原/对齐 |
|---:|---:|---:|---:|---:|---:|
| 1 | 9/9 | 1025/1024 | 1025/1033 | 0.1942% | 65/65 |
| 15 | 9/9 | 1032/1024 | 1032/1033 | 1.0319% | 65/65 |
| 16 | 9/9 | 1024/1024 | 1033/1033 | 0% | 65/65 |
| 17 | 9/9 | 1025/1024 | 1025/1033 | 0.1942% | **65/66** |
| 29 | 9/9 | 1031/1024 | 1031/1033 | 0.8843% | 66/66 |
| 31 | 9/9 | 1032/1024 | 1032/1033 | 1.0260% | 66/66 |

因此有效q块可省不足0.8%的计数，不代表所有Attention成本严格小于1%：加权KV循环的部分构造略过1%，但这不是全层/全模型加速。launch数可反增，D17的尾步还多一个条件MM M tile。更多/不同输入、cached起点、D变化或16SM大粒度对齐可能多一次forward，额外CPU/MLP权重成本要另算，不能从这个固定9步模型排除。

源码身份在结果中固定：actual54c来自212106 postflight归档；helper59d9已由tmp复制到本目录持久保存，SHA核同；C3 a129、runner e155。没有只依赖临时路径。

## 是否值得下一门

当前证据只支持“有效partial CTA少量冗余”这一小机会，同时已反证减少launch、减少shape、显著省GEMM三项常见收益叙述。**本轮不建议为它立即写新调度器或在当前容量/FULL门间插队，也没有新增大收益路线。** 小机会保留，不作为永久否定。

如果后续root明确选择实测，最短反证应先在**一项隔离原参数context-screen**记录真实选中次数、unused budget/forward数、真实M形状/原输出成功，再看DB/容量/时间是否可比；未命中/新增形状成本或无净信号都保留，不扫tile/不改budget。改变chunk边界会改变batch GEMM/Attention归约和全局非seed RNG轨迹，不能以逻辑token不变继承103/105；进入默认前仍独立accuracy。当前没有该实现、设备门或收益结果。
