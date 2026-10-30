# Q32 K-scale每tile尺度融合

每个KV tile读取K尺度后与score scale合并，再乘到整数QK分数；尝试减少循环内一组256×64 score乘法，代价是新增64元素逐token尺度运算并改变FP32结合顺序。TTGIR显示循环内score乘法3→2，ASM SGPR spill计数98→99。四组组件ABBA中B慢0.872%；全量AB数值门因GPU摘要与CPU回读矛盾未闭合，停止且不重测，不称数值通过或已确认错误。

- [20261030T005910507361Z-q32-key-scale-compile-probe](../runs/bi-v150/20261030T005910507361Z-q32-key-scale-compile-probe.md): TTGIR循环内score乘法由3次降至2次，ASM SGPR spill计数98→99；runtime regs135/shared57344，runtime spills0、VGPR spills0、ScratchSize0。仅编译探针，无attention reader数值或性能，不是收益或生产资格。
- [20261030T011120000584Z-q32-key-scale-component](../runs/bi-v150/20261030T011120000584Z-q32-key-scale-component.md): 四组ABBA Event A7.9743986/B8.0439349 ms，B慢0.872%，性能负向并停止、不重测。五例各臂选定FP64抽样通过；full-output helper报告AB非逐位却max-abs=0，CPU回读五份均见非零差且均在点式门内，全量AB数值门未闭合。不能称全数值通过，也不是已确认候选错误；原summary保持不变，附posthoc CPU脚本与JSON。
