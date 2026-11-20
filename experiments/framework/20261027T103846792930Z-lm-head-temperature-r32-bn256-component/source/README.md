# R32大词表head：唯一BN256组件

仅CPU准备，不SSH/GPU/排队，不改当前105、8d1a生产或旧R32冻结包。复用已测R32 epilogue的原kernel4c800693字节与原owner、main56/807源/native14f身份、FlagGems注册和原Sampler。真实W[130560,2048]一次加载，hidden为固定合成R32；没有新增持久权重副本，原验证W clone是两臂共用证据，不冒称KV收益。

性能A是已测R32温度epilogue＋完整原Sampler：BM32/BN64/BK64/w8/s1、grid2040×1，预期实际核hash bacf34cb。B只改BN256/grid510×1，其余配置、自然W descriptor、runtime K累计、BF16round→FP32→原温度除法、原stats/top-p/softmax/exponential/RNG全不动。初次原F.linear真实capture须仍为32/64/64w8s1/CTA1、EVEN_KTrue，随后只作为数值参考，不把它或手工MM当性能A。两臂各自实际分配同形状FP32输出、执行完整Sampler。

最短门：先真实原provider/config，再首组全scaled/filtered/IDs/RNG/finite/输入不变（三方F.linear参考、已测A、新B），保存三核IR/ASM/实际资源。A实际hash须与已测相同，A/B n_spills均0且资源非空，否则立即停、不计时。shared/寄存器/SME变化仅保存诊断，不认定occupancy或原因。其后沿原独立FP64抽样、changed/zero/extreme/每请求generator、side stream、同址换值poisoned确定性prefix Graph、计时后检查；失败不放宽容差、不救旧stats融合。通过后唯一ABBA，每臂每窗8次，完整eager head＋Sampler含实际输出分配、CPU提交及原RNG；Event和wall均正才记候选正，非正停止，不扫其它BN/warp/stage。

资源模型只是预测：BN加四倍令CTA2040→510，16SM仍平均31.875CTA/SM；单stage A+B有效payload12→36KiB，理想FP32 accumulator每线程4→16，不是实际shared/reg/occupancy。A逻辑tile重复加载255→63.75MiB，但A本身128KiB可驻L2，不能当191.25MiB实测HBM节省。W510MiB、输出15.9375MiB、CPU kernel launch数不变，不能称大突破。只有真资源与完整链实测能决定。

新增CPU见cpu-check：真实配置拒绝边界、同参数仅BN/grid差分、原记录不变、原kernel字节、完整ABBA/owner finally及资源门。旧W/模型/SDK/计时等原pins复用，不重新建立长矩阵。首门若原配置或A hash不同，保留原件停止，不临时弱化基线。

root独立审阅、确认唯一GPU/9031空闲后手动决定运行：

```bash
python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/main56f1838-pr66-20261027
```

entry原native14f默认路径保持，也可显式传已有已核`--native-library`；source_identity按原807源完整校验。此目录未上传/执行，原件按唯一UTC run保存，收益与数值资格尚未获得。
