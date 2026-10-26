# 主线增量审阅

2026-10-26。审阅main594到候选的三项差分及真实callback：仅精确BF16 contiguous M64/N2048/K6144、无grad、独立storage进入已测kernel；位于原M1–8分支之后、原provided/MM之前。不适用时沿原路，直接写caller out并返回同对象。无权重重排、额外常驻权重或workspace，runner/compute-order身份不变。

新flag默认1，installer状态不允许安装后切换；未设与显式1同指纹、0隔离的新增CPU合同已核。BI-V150 16SM原安装范围保留；kernel SHA4c5c5bb7为153134受测原字节，继续使用W.t()自然view及原K/dot序。未见本次新增数值、生命周期或跨平台阻断。

复用组件8门，不重复跑42权重环。下一步在官方首轮确认新callback实际选中、kernel身份、编译绑定及原prefill/native栈；仅首次selected不代表全负载命中率。新main594/native14f同源对照后才判断净收益，正向再完成原105；当前没有模型或正式收益资格。固定候选包3b14a0a04c78c7e04b91e052ad73f18c76aa00328c672528603f30bb6a9e494f不因记录而改写。
