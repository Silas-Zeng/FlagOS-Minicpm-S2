<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261029T063736Z-prefill-base2-cpu-compile

- **尝试了什么：** 编译base2换底A/B并检查ASM、寄存器与溢出。
- **改了什么：** 尝试将log2e并入score scale、P/alpha改用exp2；GPU kernel行为未测。
- **怎么测：** CPU-only A/B编译与静态ASM/resource检查。 见[逐文件manifest](../../../experiments/bundles/20261029T063736Z-prefill-base2-cpu-compile/manifest.json)和[压缩包分块索引](../../../experiments/bundles/20261029T063736Z-prefill-base2-cpu-compile/raw.tar.gz.storage.json)。
- **结果怎样：** spill 4→3、VGPR113→115、mul84→65，exp保持20。
- **是否保留：** 保留机制证据；不作GPU性能或生产资格结论。
