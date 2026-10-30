# Q32 历史块掩码精简

尝试将完整历史tile与因果边界tile分为两个保持升序的循环，减少历史tile的load/causal mask。第一次入口仅有helper SHA抄写错误；修正入口后，首个组件样例A/B逐位不一致。finite、guard和输入只读通过，但未进入计时；停止候选。此结果不等于团队main已确认错误。

- [20261029T233910926379Z-q32-causal-interior-component](../runs/bi-v150/20261029T233910926379Z-q32-causal-interior-component.md)：入口helper SHA与冻结身份不匹配，benchmark/编译前停止，无性能样本；保留失败记录。
- [20261029T234221231370Z-q32-causal-interior-component](../runs/bi-v150/20261029T234221231370Z-q32-causal-interior-component.md)：step1048的A/B逐位不等，finite/readonly/guard通过；未计时，候选停止且不修救。保留源码和编译证据，约41MB失败张量留在原件库。
