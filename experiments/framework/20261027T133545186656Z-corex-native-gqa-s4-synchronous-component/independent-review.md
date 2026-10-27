# 夹具 v2 独立增量复核

主线复核包 `88c11416de9c66a22981e9f740c3e68971d668123fe0ac1be6e7e022a6f102a4`，30 pins与tar原字节一致。相对已审父包，仅worker和README变化；逆去CPU全+0构造、执行前guard及证据保存后，worker与父包逐字一致。CU、bridge、owner、编译证明、原数值门和ABBA保持。

隔离诊断132510在不调用GQA时复现zero_越过view写guard，B32/B64数量分别12800/26112。v2使用CPU精确+0再copy到原view；前guard失败立即保存并停止，原执行后guard保留。可执行既定单组件；此审阅不提供设备数值、性能或模型资格。
