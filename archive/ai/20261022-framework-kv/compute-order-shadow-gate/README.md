# 一次真实 P 命中的 logits 诊断

只诊断，不计性能，不代替官方准确率或 token/RNG 逐位等价证明。开关为 `BIV150_COMPUTE_ORDER_SHADOW_DIR=<control>/shadow-artifacts`；每 Engine PID 子目录记录资格、完整原序/P logits `.npy`、原始误差/finite/top1 与 RNG 状态是否变化。不校准也不放宽容差；`strict_bits` 如实保存。

固定原422完整map，复用冻结计算序变换。仅首次自然 Plan：在原 event 域先原序 prepare，CPU证明当前写槽唯一、不与本批所有活动请求旧prefix相交，并实际D2H核原slot；原序 forward→原N logits 独立阻塞CPU快照，完成同流H2D后才重建P的inputs/metadata；原生产forward和原N logits之后再比较。第二次 dispatcher、状态更新、采样、历史追加均不存在。42层 writer 与 attention 的先后依赖来自已回收actual `Attention.forward` 3414faca，未知校准/量化/共享/连接器/训练或hook支路拒绝诊断。

构建入口：`python tmp/compute-order-shadow-gate/prepare_shadow.py --base <原422目录> --output <新目录> --emit-only`。生成五路径镜像与同级 `*-prepare.json` 的完整424输出map；不加 `--emit-only` 才复制完整源。原P helper自身runner锁、worker/protocol两处runner锁均显式重定。父任务owner负责唯一设备和原bc51短负载。

当前为CPU待互审稿：只计划compile/精确逆回/完整map，不运行模型或新增mock。`unsupported_before_shadow` 不是覆盖；`diagnostic_completed` 也不自动表示数值等价，须读取原始结果。shadow开始后任何失败直接终止服务，不重试原路。所有现场引用保留至进程退出。

跨职责新增只读审通过（team_view_final_check）：helper `90ad14d1b9696c6d8a801b7e30d3c2aec615ef40c7f76bc00bf42d0be906d705`、runner `f8b0a5212786d7d6f2cea1d84f1eaabce7ccea2b714c3b4454fc12f07236f8f8`、preparer3df35；root薄owner b5fc218f/部署76985匹配同424五路径。初稿两个属性名会令资格提前unsupported，已修为真实TritonAttentionBackend.forward_includes_kv_cache_update与impl._kv_quant_mode并锁backend身份。逐物理token mask排当前slot重复及任何旧prefix相交、两序实际slot D2H、42层非alias/非校准、shadow logits阻塞独立CPU快照后才P prepare、原event域与上一轮sample只读均已核；dispatcher/状态更新/采样/history没有第二次，生产异常不回原路重试。finish比较FP32快照的int32位模式并保存原始误差，发生在ExecuteModelState/采样前；原owner参数/锁/清理不变。可安排一次短诊断，但首次未命中或unsupported不算覆盖，completed不自动等价/accuracy，额外forward/同步不作性能。此次未执行任何新旧套件、模型、SSH或GPU。
