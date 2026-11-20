<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# Prefill base2 CPU编译筛查

CPU机制证据之外，M2048/KV16K单层入口因ABI参数名KeyError未计时，exp2换底局部ABBA为负（Event慢0.8052%、wall慢0.7673%）。保留入口失败与负结果，不作生产或官方资格。

相关代码：[framework](../../patches/framework)。

相关方法PR：未记录。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261029T064712064303Z-prefill-base2-m2048-kv16k-component](../runs/bi-v150/20261029T064712064303Z-prefill-base2-m2048-kv16k-component.md)（登记#493）：M2048/KV16K组件worker引用不存在kw_a[key_ptr]，实际ABI为key_cache_ptr/value_cache_ptr；selected_calls=0，无timings。 **是否保留：** 保留入口接线失败；不归为候选数值或性能失败。
- [20261029T065347035247Z-prefill-base2-m2048-kv16k-component](../runs/bi-v150/20261029T065347035247Z-prefill-base2-m2048-kv16k-component.md)（登记#494）：ABBA Event 6.5530→6.6058ms（慢0.8052%），wall 6.6458→6.6968ms（慢0.7673%）。 **是否保留：** 保留负结果并停止；无生产或官方资格。

## CPU

- [20261029T051320Z-prefill-base2-cpu-compile](../runs/cpu/20261029T051320Z-prefill-base2-cpu-compile.md)（登记#490）：CPU入口引用的run_compile.py路径不存在；owner启动前失败，无编译产物或设备结果。 **是否保留：** 保留入口路径错误；不归为候选数值/性能失败。
- [20261029T051506Z-prefill-base2-cpu-compile](../runs/cpu/20261029T051506Z-prefill-base2-cpu-compile.md)（登记#491）：CPU编译器把源码字符串误交给Path.read_text作路径，触发文件名过长；B Q-hoisted未编译。 **是否保留：** 保留source-reader工具错误；非kernel失败，无GPU或性能结论。
- [20261029T063736Z-prefill-base2-cpu-compile](../runs/cpu/20261029T063736Z-prefill-base2-cpu-compile.md)（登记#492）：A/B CPU编译完成；SGPR spill 4→3、VGPR113→115、ASM乘法84→65而exp仍20。 **是否保留：** 保留为换底机制证据；未上GPU，无数值/性能或生产资格。
