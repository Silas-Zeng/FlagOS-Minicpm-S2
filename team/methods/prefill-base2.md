<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill base2 CPU编译筛查

尝试将log2e并入score scale、将P/alpha改用exp2；本批两次入口/编译工具失败后，063736 CPU编译完成并显示乘法数减少，但exp条数未变、寄存器略增。仅机制/编译证据，没有GPU数值或性能结论；S8准确率与官方4K另列。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## CPU

- [20261029T051320Z-prefill-base2-cpu-compile](../runs/cpu/20261029T051320Z-prefill-base2-cpu-compile.md)（登记#490）：CPU入口引用的run_compile.py路径不存在；owner启动前失败，无编译产物或设备结果。 **是否保留：** 保留入口路径错误；不归为候选数值/性能失败。
- [20261029T051506Z-prefill-base2-cpu-compile](../runs/cpu/20261029T051506Z-prefill-base2-cpu-compile.md)（登记#491）：CPU编译器把源码字符串误交给Path.read_text作路径，触发文件名过长；B Q-hoisted未编译。 **是否保留：** 保留source-reader工具错误；非kernel失败，无GPU或性能结论。
- [20261029T063736Z-prefill-base2-cpu-compile](../runs/cpu/20261029T063736Z-prefill-base2-cpu-compile.md)（登记#492）：A/B CPU编译完成；SGPR spill 4→3、VGPR113→115、ASM乘法84→65而exp仍20。 **是否保留：** 保留为换底机制证据；未上GPU，无数值/性能或生产资格。
