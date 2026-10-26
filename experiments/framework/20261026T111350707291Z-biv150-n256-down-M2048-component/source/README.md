# N256无损权重：先原BN256的大M

仅CPU准备，未GPU编译或数值/性能合格；不改冻结M64生产包。新格式是 `P[N/256,K,256]=[8,6144,256]`，不是已负的N/K双分块，也不是P128降低大M的BN。M2048原BM256/BN256/BK32、w16/s2在本候选全部保持；真实配置仍由原opaque→F.linear现场捕获，候选 `config_difference` 必须为空，不扫描参数。

P128的M2048在8数值门过后慢61.60%，其中BN256→128为显式差分，停止该实现和P128全M路线。P256允许BN64/128/256在同一个N256块内寻址，保留各M原tile和原dot/K顺序；每K步恒定 `BK*256`，不含旧微块select跳跃。三维contiguous descriptor的最后维256满足安装JIT前端SME门；固定源码中的for/load链与连续轴条件也有机制依据，但**实际B SME、资源及性能仍须实编译**，不把mask当生效或假称原B有通用转换瓶颈。

每次只跑一个M，默认2048；只有首项正，root才单独决定 `--rows 32`、`--rows 64`。原4eager/FP64/两换值毒化Graph/side/RNG/输入不变门全部保留，实际M输入独立分配并核storage字节，不用大M前缀backing。全部正确才唯一ABBA；错误或性能非正立即停，不自动其它M、权重环或模型。

root实查GPU/9031并安排独占，部署 `entry.tar.gz` 后：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/bf16-n256-down-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --rows 2048
```

A为原默认FlagGems真实完整调用，B为新输出＋N256消费者。计时只含完整GEMM Graph replay，不含加载pack/传输/每调用eager allocator；单层合成激活、原W/P双份，不授单份权重/全模型/官方资格。owner DB锁/恢复/清理沿用已核组件，只改run标签/说明/rows默认。配置、CPU合同、pins、包SHA见同目录JSON。
