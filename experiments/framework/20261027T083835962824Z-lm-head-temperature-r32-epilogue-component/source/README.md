# R32 LM-head温度epilogue组件（待排卡）

从已过R64组件独立派生，只改R32形状、FP64行索引0/1/15/31、per-request generator索引0/31与运行标签；原四种输入、FP64/全scaled/filtered/IDs/RNG、换值poisoned Graph、side、完整eager ABBA/分配/原DB与自有PID清理不变。原extreme倍数64不变，词表列索引不变。原R64/生产包均不修改。

首次调用真实UnquantizedLinearMethod.apply→default F.linear捕获**本次R32**实际kernel/config/grid/IR；候选复用捕获结果，不沿R64 tile/w16配置、不修改DB路由。受测candidate源码4c800693完全不变，其M/tile为运行实参；BF16round→FP32→原temperature除法外原dot/地址/循环不变。服务真实head为UnquantizedEmbeddingMethod，两apply已CPU证明同AST/同默认dispatch，组件仍不冒称构造完整模型。

R32预期只省47.8125MiB逻辑中间流量及两个launch，W仍510MiB、算术不减、无优化权重副本；共同W_guard clone仅验证输入未变。R32实际tile/资源未知，不能把R64的组件或官方收益迁来。首个数学/编译失败立即停，不调容差；门后唯一完整head+Sampler ABBA，Event/wall任一非正停，不扫其它R。

```bash
python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/main56f1838-pr66-20261027 --native-library /workspace/experiments/minicpm-s2/official/20261026T184110Z-main241-control-16k-four-rounds-control/native/biv150_native_w8a8.so
```

只CPU准备，不自动排卡，作为R64官方B判定后的备选；是否运行由root决定。既有检索只见R32预算、旧小M down/地址核，没有此R32 head epilogue实际结果，不重测同一R32旧实验。source仍原main56/807/native14f，不能以809生产候选当原控制。无105/官方/生产资格。
