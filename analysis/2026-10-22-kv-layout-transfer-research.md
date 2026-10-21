# KV布局与传输粒度：后续研究备忘

2026-10-21 20:55 UTC，root在205219基线唯一上卡期间查阅。仅研究，没有改当前0e2115页序、31cc worker、616事务或实际KV分配。当前验证和性能结论仍以独立原件为准。

195012实际布局为42个独立storage，每层normal BF16 `[32621,2,16,2,128]`；全池约20.9058GiB，而主机cgroup上限20GiB。这个事实排除了未经预算的整池host镜像。204159单victim约685MiB可容纳，页排序后每层66段、合计2772次恢复调用。它没有消除层之间的分散。191545的packed复制样本与normal样本是微测布局，不代表服务实际已经采用packed，也不能把其时间直接移植到端到端。

[vLLM v0.24.0 offloading文档](https://docs.vllm.ai/en/v0.24.0/features/kv_offloading_usage/)讨论host预算和块粒度权衡，但其现成connector配置不作为本比赛的实现方案；当前维持原服务参数、自有实际代码改动，不合并新版框架。[同版本backend接口说明](https://docs.vllm.ai/en/v0.24.0/api/vllm/v1/attention/backend/)说明逻辑形状与物理stride顺序可以分别表达。网页的接口与本实例实际源码仍需逐项对齐，不能凭文档宣称后端兼容任意布局。

可证伪的后继问题：若以实际代码把同一逻辑块的42层存储安排在相邻区域，并向每层Attention/writer暴露正确stride的view，是否能减少offload的分段提交？这只是推测。需要同时检查allocator原容量计算、KV共享/alias、storage offset、writer和Attention是否真正尊重block stride、CUDA Graph地址稳定性以及全部消费者。跨层相邻可能增大单层相邻块的跨度，损害访存局部性或地址转换效率，不能只优化复制而忽略正常decode。

当前决定：放入后继研究，不立即实现或增加设备门。先完成当前原布局的VERIFY0配对、容量早退独立候选，再评估更改实际KV存储的复杂度和收益机会。若以后推进，须先从冻结e155/实际backend/writer源码证明可表达，再做最短全字节/实际消费者门；现有42独立storage的worker guard不得绕过或假装新布局仍是旧布局。任何正常decode回退和准确率变化都要记录，不能用复制微测收益抵消服务负结果。
