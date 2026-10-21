# MiniCPM5-2B KV框架阶段交接

更新时间：2026-10-21 21:06 UTC。范围仅天数BI-V150；沐曦C500由队友负责。当前设备作业均已结束，root是唯一设备owner；持续优化目标仍有效，阶段归档不表示停止探索。

## 已经实际做到了什么

在原服务参数下实现并上卡验证了单victim KV保存恢复：真实writer完成后SAVE确认，再释放GPU源页；暂态容量不足保留host副本；私有目的页分配后ZERO、RESTORE完成，再交原调度和runner继续生成。主机仅保存一个受预算约束的前缀，未作超过20GiB主机限制的整池镜像。没有修改模型、量化/投机参数或引入新版框架。

真实目的页原序存在大量下降邻接。0e2115候选只在严格独占、未hash、未发布且真实list别名成立时重排Block对象，再用同一新表恢复逻辑KV。204159的1044页实际由1044段变66段，42层清零、恢复、诊断回读各2772次调用，718405632B逐字节验证及原输出消费通过。这里证明的是机制和调用数，尚未证明端到端吞吐收益。

## 保留的实验

所有运行ID均以20261021T开头，完整原件在 `experiments/framework/` 的同名run/control中；忽略的SQLite及tgz另有本地完整工作ZIP。

| UTC运行简称 | 变化/用途 | 真实结果 | 解释边界 |
|---|---|---|---|
| 200957-kv-protocol | 初版真实抢占 | SAVE成功后丢失恢复机会，无RESTORE | 原skip原因没记录，保留负例；不能后来补写为容量 |
| 202526-kv-retain | 暂态保留修正，VERIFY1 | SAVE→恢复→全42层回读→原消费者通过；43848次恢复调用 | 240.93秒诊断；DB新增2表67行，非收益成绩 |
| 204159-kv-page-order | 私有页重排，VERIFY1 | 1044→66段，恢复/回读各2772次，全字节通过 | 227.55秒诊断；DB本轮不变，不与不同起点旧诊断比较收益 |
| 205219-kv-pair-stable | 原稳定源码，VERIFY0 | 32/0，220.407047817秒，KV521936，DB518/19337不变 | 一次短服务基线，非官方完整成绩 |
| 205819-kv-pair-page-order | 原页序候选，VERIFY0 | 32/0，220.921083583秒，真实恢复及16token原消费 | KV521840；DB变519/19340。双失配，不计算可归因收益 |

最后一轮R16688/1043页/717717504B、SAVE966calls，排序后仍66段；不要复用204159的R16704、1044页、1008SAVEcalls和8token消费者字段。VERIFY0不执行逐字节回读，但之前相同0e代码的VERIFY1门已做；两者证据分开。

6个KV块的差异约3.94MiB，不能据此反推出具体显存profile分项。当前没有直接记录给出其原因，不改官方util/KV大小去凑一致。发现DB新增后，单补stable不能修复旧候选起点，所以先保留双失配结果，后继从新的已记录起点做必要对照。所有原件和shutdown告警均保留，不挑最好结果。

## 下一项已准备的真实代码

容量必要条件早退候选在 `patches/framework/candidates/biv150_kv_capacity_protocol.py`，SHA67e4c07566ee3e52f84d6a96a494b8976d858420dadd5f833e66c3291e32fb73。它只在已审Request真实类、封闭非streaming输入、无owned页/缓存占用、整页前缀且可用块F少于所需前缀页P时，避免反复复制token、计算digest和复制历史列表。其余条件走原完整检查/allocator；取消、epoch、长度失效仍及时处理。不能用F>=P代替真实准入，也不改变FCFS。

唯一必要CPU合同1test/0.021秒通过，删除新增代码可精确逆回受测0e；framework与hardware分别审生命周期和allocator必要下界。新builder a79b69与launcher0ae8把新asset映到全新source的canonical模块名，原0e/worker31cc/事务616/copyc95f与旧包装全部冻结。**该候选尚未上卡，不能继承页序结果。** 下一最短门需真实fast_rejects>0、恢复回读及原消费完整，再讨论不回读的性能对照。

## 研究留痕与协作边界

- [容量早退源码证明与反例](2026-10-22-kv-restore-capacity-fast-reject.md)及[独立审阅](2026-10-22-kv-transaction-independent-review.md)。
- [完整覆盖时省ZERO](2026-10-22-kv-full-overwrite-no-zero-plan.md)：仅设计；须新真实状态机和ACK，不能伪造清零完成。
- [碎片感知保存前缀](2026-10-22-kv-fragment-aware-prefix-plan.md)：仅设计，传输成本与额外重算须实测。
- [跨层布局与传输粒度](2026-10-22-kv-layout-transfer-research.md)：仅研究，不能牺牲正常Attention访存或绕过storage guard。
- [三角色交接索引](../docs/agent-work-index.md)保留实现、否定意见、审计和下一操作。两共享代码库只改本地；只有专用私有实验库持续发布。精确最新GitHub/ZIP覆盖范围以CURRENT顶端及发布回执为准。

新KV协议尚未通过完整模型accuracy门，未合入默认稳定版本。稳定路径既有小收益和103/105结果保留，但不能外推给新KV代码。
