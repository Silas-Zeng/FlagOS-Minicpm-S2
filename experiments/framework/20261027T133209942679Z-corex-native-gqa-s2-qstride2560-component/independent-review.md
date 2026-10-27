# 夹具 v2 独立增量复核

主线复核包 `e02c50afa6c3afd418fd6f5b3d5fa286c80c704c6bca133f097131fb87c33730`，29 pins与tar原字节一致。相对已审父包，仅worker和README变化；逆去CPU全+0构造、执行前guard及证据保存后，worker与父包逐字一致。CU、bridge、owner、编译证明、原数值门和ABBA保持。

隔离诊断132510在不调用GQA时复现zero_越过view写guard，B32/B64数量分别12800/26112。v2使用CPU精确+0再copy到原view；前guard失败立即保存并停止，原执行后guard保留。可执行既定单组件；此审阅不提供设备数值、性能或模型资格。
