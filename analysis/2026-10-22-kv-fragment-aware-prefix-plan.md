# 按实际页连续段与调用预算选择保存前缀：仅设计，未实现

本方案来自天数 BI-V150 本实例的真实 `200957` SAVE，不外推沐曦 C500。只记录一个后继候选，不混入当前 protocol 暂态保留修复，不改 runtime、installed 源码、块大小、模型或比赛启动参数，未新增 GPU 门。当前优先级是先跑通真实 ZERO/RESTORE/消费/核验链路。

## 实证触发点与仍缺的证据

`20261021T200957Z-kv-protocol-context16k-long` 的原件已本地。真实1044页/16704token，SAVE685.125MiB，normal42 的24个连续段产生1008次 copy。前1024页恰分成4段，尾20页是20个单页；后者只有13.125MiB，却占840次调用。数值与页图独立计算见 [专项原件审计](source/kv-transaction/200957-save-hardware-review.json)。

这说明“保存更多有效 token”还会增加主机/传输发起工作，不只有字节增加。但本轮没有独立 RPC wall/event、pin 分配或 CPU 提交时间，且没有恢复。1008次调用不等于已经证明很慢，减少到168次也不等于已经省了多少毫秒；当前仍不知道收益符号。

## 一手资料只支持权衡方法

[vLLM v0.24.0 KV offloading 指南](https://docs.vllm.ai/en/v0.24.0/features/kv_offloading_usage/)区分 host 预算、块粒度和记账开销，也提供只保存 prompt 的选项。它是其它平台的现成实现说明，不能当本站性能保证，不能通过启用其 backend/改 block_size 代替本项目实现。本候选使用实际物理段连续性，而不是按 prompt/decode 标签硬切。

[CacheOPT v1 第3.5节](https://arxiv.org/html/2503.13773v1#S3.SS5)使用目标模型/硬件上的重算与 swap 成本选择策略；其 A100、OPT 模型及交点不适用于本站。本文只借用“同实例实测成本比较”这一方法，不引入论文的输出长度预测、SLO排序、预留策略或其框架分支。下面的部分前缀及调用数公式是基于本项目 actual 源码的推导，不冒称论文已经实现这一方案。

## 先保留真实安全上界，再选择更短前缀

当前 actual API 是 `patches/framework/biv150_kv_transaction.py` SHA `616040602c4ebcfc6b21ace693d193f09fb1bb95da2b874e0bf48039c14a1b13` 的 `plan_snapshot`：

```text
stable = min(真实 issued_tokens − 所有 queued frame 的该请求 scheduled tokens,
             len(真实 known_token_ids) − 1)
R0 = floor(stable / 16) × 16
```

它已经保留至少一个已知 token 来重新取得 logits，并只用真实存在的完整逻辑页。未来策略只能在取得这份安全 Snapshot 后选 `R=16k ≤ R0`；不能为了得到目标长度而伪造 issued、known IDs、queued 数量，或绕过 pending-frame fence。

令 `p[0:m]` 为该 Snapshot 原逻辑顺序的实际物理页号，`m=R0/16`。normal42 每层页16384B，host目的按逻辑次序连续：

```text
g(k) = 1 + sum(p[i] != p[i-1] + 1, i=1..k-1),  1 ≤ k ≤ m
Csave(k) = 42 × g(k)
B(k) = k × 42 × 16384 = 688128k
```

给定明确的 SAVE 调用预算 J、payload cap 和动态 host 余量，单次 O(m) 扫描可取最大合法 k。g(k) 单调，最大点通常是某一连续段末端，或 byte cap 截断处；不需要按长度扫 tile/配置，也不排序物理页。不声称只枚举段末端能全局优化任意非线性的重算成本：上述最大化只针对“给定调用/字节预算保留最多 token”。J 尚无时间测量支持，当前不指定推荐数值或调优扫描。

新 Snapshot 必须保留同一 Key 和完整 pending_frames，只替换为逻辑前 k 页、R、以及从原 token IDs 计算的 R 长 digest；其它事务证据保持真实。当前 Snapshot 校验、worker 字节约束、external-computed 分配和 cached-resume 计算均按 `snapshot.prefix_tokens` 参数化，源码上没有“必须等于最大 R0”的前提。因此具备接入位置，**不等于已经实现或实测过更短前缀**。

## 本例仅作几何演算

| 选择 | 保存 token | 页数 | SAVE 段/调用 | SAVE payload |
|---|---:|---:|---:|---:|
| 当前安全上界 | 16704 | 1044 | 24 / 1008 | 685.125MiB |
| 第4段末端 | 16384 | 1024 | 4 / 168 | 672MiB |
| 差额 | 少320 | 少20 | 少20 / 840 | 少13.125MiB |

此处16384来自本次页图的第4段末端，不是固定16K策略。其它请求若页图不同，候选点也必须不同。必须保留所有输入/已生成 token，普通计算恢复未保存的已知后缀；不能丢320 token、删输出或改请求顺序。320 token 的额外工作是带长上下文的已知后缀 prefill/recompute，不能按320次普通 decode 或总吞吐线性估计。

SAVE 的 host 目的连续已知，故 Csave 准确；RESTORE 的新目的页来自未来真实 allocator，段数尚未知。即使少存20页，也不能承诺恢复也正好少840调用。新分配容量/清零、再次抢占、等待时间和 batch 轨迹还可能改变，必须纳入实际服务测量。

## 可证伪的收益条件与最短后继

对同请求/同设备条件，较全安全前缀的收益须满足：

```text
省掉的 pin/主机记账 + SAVE成本 + ZERO/RESTORE成本
  > 额外后缀重算成本 + 因容量/batch/等待变化增加的代价
```

producer fence/事务固定费用未必随 k 变小；不能把它们也按字节比例算作节省。若新增后缀计算更贵、调用提交成本本来很小、恢复失败/取消使保存浪费，或没有真正恢复，方案就可能无收益；这些负结果都必须保留。KV bytes等价也不自动保证受 batch 轨迹影响的全局随机采样分配等价，仍需新 accuracy。

最短后继是先完成 root 当前独占设备的协议修复门，不再重复672MiB复制微测。仅当真实恢复链路已过、root另行决定实现时，独立加入上述选择器，先核 k≤m/完整页/原逻辑映射/digest/frame 保留，再做一次相同长输出真实服务匹配比较：全安全前缀与调用预算策略分开源码目录/结果，不叠其它候选。实际记录 R0/R、源/目的真实 runs、bytes/calls、稀疏 RPC wall、原调度实际多算的已知后缀、真实回读/消费/预算/清理；保留 CPU quota/host 干扰边界。没有 J 的成本依据时宁可保留设计，不报估算毫秒或虚构收益。

本 owner 只CPU研究和只读审查，无 SSH/GPU/远端导入/共享仓库写入。当前受测50375原件完整保留，暂态保留修复由 systems 独立维护并优先交叉审阅。

framework对本设计只读复核无数学阻断，补充：当前没有selector接口，必须显式构造新Snapshot，不能把参数化构造函数当作“已启用”。后继cached-resume仍须保原prompt/output/all_token_ids/count/generator；num_computed只等于真恢复R，普通scheduler按request.num_tokens−R处理已知suffix，原chunk/discard语义及async prev mapping仍须真实输入门和accuracy验证。APC容量也不能简单认为hit免费：22e把ref0可evict hit计入空闲需求；只有ref>0共享hit、或原chunk先分较小窗口等条件下，external一次分整R才可能更吃free，不能据此判定200957/202526的具体分配原因。
