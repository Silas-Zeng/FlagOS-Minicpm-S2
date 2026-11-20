# 同一N128权重：M32优先，M2048独立后继

仅CPU准备，未GPU资格，不改当前M64生产候选。P仍是已测正M64的 `[16,6144,128]`，只换消费者适用M；每次入口仅一个M，默认32，显式 `--rows 2048` 才跑大M，不自动连跑。输入CUDA tensor从实际M行CPU tensor独立创建，并核storage字节数，避免用更大M backing的前缀view掩盖越界。

A是真实原opaque→F.linear默认FlagGems，运行时捕获本M真实配置；不能假定M32等于M64。B保留实际BM/BK/warps/stages及GROUP8/SPLIT1，原BN≤128时保持；只有原BN256时明确改为128以不跨N128物理分块。此时结果记录 `config_difference`，不是“只换M”。固定该唯一必要差分，不扫描tile。K次序、每步 `acc+=dot` 和最终BF16不改。

完整4eager、独立FP64、2换值毒化Graph、side/RNG/输入不变门保留；通过才一次完整Graph ABBA。负即停止本次，不自动权重环/模型/另一个M。组件仍保留原W和P两份，不能称已消除1008MiB；只有未来全适用M消费者验证完整才能讨论释放原W，当前不在fallback里临时解包。

root独占安排后部署 `entry.tar.gz`，优先命令：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/bf16-nonly-down-other-rows-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --rows 32
```

M2048仅将最后参数改为 `--rows 2048`，由root单独决定。计时是完整GEMM Graph replay，不含CPU pack/传输/每调用eager allocator，不代表42层或官方性能。精确SHA、CPU合同和配置边界见同目录receipt/preparation/cpu-result。
