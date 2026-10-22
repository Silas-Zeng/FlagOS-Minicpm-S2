# 方法 PR 协作安排

本轮已建立四个独立中文 Draft PR，全部尚未合并。最后设备实验于2026-10-22 05:13:44 UTC结束，随后没有启动新GPU工作。主分支仍是此前完整 SQL+C3 快照；现有多项优化没有分别经过多个历史PR合并。

| 方法 | PR | 受测范围 | 合并关系 |
|---|---|---|---|
| CPU metadata 复用 | [#1](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/1) | 真实方法门通过；单轮同KV/同DB短筛吞吐约+0.2867%，TTFT约+0.2344%（变慢） | 与#2共享runner，只在新增import处冲突 |
| async token update | [#2](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/2) | 12类方法case通过；单轮同KV/同DB短筛吞吐约+0.7037% | 与#1独立，后合者保留两条import |
| KV连续页复制工具 | [#3](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/3) | normal/packed等字节门；无默认服务接入 | 独占新增路径，与其余PR无代码依赖 |
| KV二维SAVE工具 | [#4](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/4) | 单层热wall约3.62%小信号；独立42层诊断字节门通过，不是E2E收益 | 不依赖#3；不交付完整KV事务或SO |

共同远端基点为 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，tree为 `82e37f8f263eeb09563a4790359ec95a0de1ca17`。四个head/tree、创建时间和最终中文正文见[发布回执](pr-preparation/publication-receipt.json)。回读均为open、draft=true、merged=false，各自对当前main可文本合并；这是GitHub当前文本状态，不代表组合运行资格。

## 已经准备好的合并方式

建议先评审#1，再评审#2；反过来也可以。两种顺序已经实际执行三方文本合并，均只有同位置helper import的一处冲突。最小解决是同时保留两条原import；两方法体各自逐字节保留，逆撤能精确回到单方法或基线。解决后的runner SHA256为 `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`。

[组合审阅与指令](pr-preparation/combination-review.md)包含冲突原件、完整解决文件、两方向可应用补丁及哈希。只有一个方法的分支可先核SHA再用对应补丁；已经处于merge冲突状态时按文档保留两条import，并保留两PR各自新增的模块。不要把整份runner直接覆盖到已被队友另外修改的版本。

#3和#4只有独占新增文件，可任意顺序审阅。调用方仍负责producer依赖、stream、完成事件、引用生命周期与失败后的等待；两工具尚未默认挂接服务。

没有自动合并。2026-10-22已补固定组合runner的最短真实方法上卡门：五形状数据检查、四轮图读取、同次双快路与RNG均通过，见[062205报告](../analysis/2026-10-22-cpu-combination-062205-result.md)。该门使用fixture状态，未加载模型；组合服务吞吐和整模型准确率仍未验证。各自短测小信号保留，不相加、不继承旧103/105准确率，也不将局部成本改善写成官方吞吐。合并为正式提交候选前，按实际缺项安排必要的最短组合验证与比赛最终门槛。

## 仓库与证据范围

实验记录库按BI-V150和C500分开，两个共享代码库按方法组织。已有设备证据都来自BI-V150；C500由队友独立补证。PR标题、描述、我们新增的README与说明用中文，英文专有名词保留。

完整KV事务、调度候选、大小收益、失配与负结果继续保留在实验库。两轮blocking Event虽正确性通过，却没有等待CPU下降，不建立生产优化PR。FlagGems本轮没有新的代码变更，因此保持原版本。原公开fork、官方上游及其他参考仓库只读。

root负责GitHub发布；framework、hardware、systems的源码整理、独立核验、组合审阅与失败记录均在[子智能体交接索引](agent-work-index.md)。实验库完整同步身份见[本轮发布回执](github-publications/20261022-pr-maintenance.json)。
