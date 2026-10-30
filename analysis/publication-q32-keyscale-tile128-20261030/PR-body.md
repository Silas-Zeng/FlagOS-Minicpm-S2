本批增补4条实验登记，前缀534条逐字保留。

- **Q32 K-scale每tile尺度融合 / 20261030T005910507361Z-q32-key-scale-compile-probe**：TTGIR循环内score乘法由3次降至2次，ASM SGPR spill计数98→99；runtime regs135/shared57344，runtime spills0、VGPR spills0、ScratchSize0。仅编译探针，无attention reader数值或性能，不是收益或生产资格。
- **Q32 K-scale每tile尺度融合 / 20261030T011120000584Z-q32-key-scale-component**：四组ABBA Event A7.9743986/B8.0439349 ms，B慢0.872%，性能负向并停止、不重测。五例各臂选定FP64抽样通过；full-output helper报告AB非逐位却max-abs=0，CPU回读五份均见非零差且均在点式门内，全量AB数值门未闭合。不能称全数值通过，也不是已确认候选错误；原summary保持不变，附posthoc CPU脚本与JSON。
- **Q32 TILE128 / 20261030T010749147245Z-q32-tile128-compile-probe**：固定合成ABI编译成功；B TILE128相对A TILE64的VGPR 135→164、shared 57,344→81,920 B、ASM SGPR spill计数98→128。runtime spill、ASM VGPR spill与ScratchSize均为0；有效SME均3。仅writer和编译，无Attention reader/数值/性能测试；保留待数值与组件门，不由资源数据单独宣判。
- **Q32 TILE128 / 20261030T012148540966Z-q32-tile128-component**：五个合成ABI case 的A/B逐点门、FP64抽样、guard/readonly/changed-Q及同臂稳定检查均通过。四组ABBA Event A7.9793690/B8.4068933 ms，B慢5.358%；停止TILE128候选，不进官方/生产资格，不更新基线。

本批包含编译探针及组件研究；不据局部结果更新官方基线或准确率资格。恢复包以256KiB分块保存，可从bundle索引按偏移和SHA256重组。

[实验总表](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/team/experiments.md) · [本批证据索引](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/analysis/publication-q32-keyscale-tile128-20261030/evidence-index.json)
