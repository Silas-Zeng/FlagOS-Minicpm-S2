# unbacked末层选行v3：保留AOT，移除图内重复shape断言

062040真实首个S1请求在vLLM原autograd_cache_key中失败：BypassAOTAutogradCache / Unsupported call_function target torch._check。本后继只从DenseFinalRows.forward移除三条torch._check，不绕过或关闭编译缓存，不改算术、索引、unbacked注解或日志。

唯一生产入口仍先由原_cpu_plan限制1<=S<=64、S<M<=2048，原_can_forward强等实际Tensor的M/S。4项新增CPU检查覆盖这些边界与来源；旧已过检查复用。编译器失去图内范围断言后可能出现新的unbacked lowering/guard限制，必须由首S1真实门判断，不能预称成功。

服务门v3复用v2的跨分段parser，只有候选tree/manifest身份变化，原六请求和清理不动。若首S1出现错误立即终止，旧062040失败保留；未运行GPU、未验证模型准确率/性能或AOT重载。
