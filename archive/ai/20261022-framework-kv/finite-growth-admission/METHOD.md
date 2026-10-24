# 有限窗口增长准入

**结论：保留默认关闭的研究候选与原始证据，不宣称确定收益。** 本轮真实服务抢占从 1 次降至 0 次；共同 DB 对照仍有 KV 容量失配，可比收益为 `null`。不放宽容量门、不为凑 KV 继续重跑、不新增准确率。

仅在已核 AsyncScheduler 的全新、无 APC 的 WAITING 准入处，估算 resident 最早 `max_tokens` 上限完成窗口的增长页数（另留 2 步相位余量）；不足则返回原 WAITING 的 None 等待。部分 prefill 保留完整已知输入预算，不作为释放 anchor。每次重算、不持久预留页，不承诺实际 EOS 或此后零抢占。原 Q/GQA 算术、FCFS 次序、总 token budget 与官方服务／负载参数不变。

| 轮次 | 耗时 / 总 TPS | KV / DB | 结果边界 |
|---|---:|---|---|
| 193302 原基线 | 169.797007s / 3280.717434 | 521840；529/19769 稳定 | 32/0，1 次抢占；旧 DB 起点 |
| 194020 冷候选 | 175.720694s / 3170.121791 | 521936；529/19769→532/19839 | 32/0，0 抢占；对旧基线 KV/DB 双失配，不认稳定负收益 |
| 194634 同源 warm | 168.133490s / 3313.176919 | 521936；532/19839 稳定 | 32/0，0 抢占；机制生效，仍未证明净收益 |
| 195213 共同 DB 原基线 | 169.815742s / 3280.355478 | 521840；532/19839 稳定 | 32/0，1 次抢占；原定唯一补基线后停止 |

warm 相对共同 DB 基线的**描述比率**为 TPS +1.000545%、TTFT +2.282034%、TPOT −3.552231%。24 项中仅 `same_KV=false`，其余源码、原参数／负载、环境、DB 四端和后态门通过；521936 对 521840 的容量差异阻止因果归因，不按策略收益发布。

两候选同 Engine 的首次真实延期均为 N30 / H791，free1664 < future2559；INSTALLED 仅安装预检。冷轮新增 3 表、70 行，旧行 typed 多重集保留；没有单独测量调优耗时。414→415 只改 init 并加 helper8f564，runnercc442／两算子不变。

CPU 原快照随比较 JSON 保留：metrics 时间窗含负载准备；exporter 进程 CPU 不代表 Engine 总 CPU；共享 cgroup 节流累计不能换算负载 wall 损失。没有本准入策略独立准确率，既有 Q/GQA 101/105 不自动继承。root 已核四包 seal／32 请求／清理，本记录不重跑 validator 或设备。

比较原件：[冷轮](../../../../analysis/finite-growth-service-pair.json)、[warm 对旧基线](../../../../analysis/finite-growth-warm-service-pair.json)、[共同 DB 最终对照](../../../../analysis/finite-growth-common-db-service-pair.json)。DB 内容核对：[194020](194020-db-delta.json)。四轮正式登记见 registry-final.json；registry-pending.json 是此前未落库草稿。
