本批增补2条实验登记，前缀538条逐字保留。

- **Q32 K-only lookahead / 20261030T015910809947Z-q32-k-lookahead-compile-probe**：编译审阅在QK后、PV前定位到下一tile的页/K/scale加载，当前tile PV之后有完整vmcnt等待、下一轮才消费carry K，形成可能的重叠窗口；这只是机制窗口证据，未证明隐藏延迟或速度收益。VGPR135/shared57344均未上升，ASM SGPR spill计数98→88；仅writer与编译，无reader、数值或性能。
- **Q32 K-only lookahead / 20261030T021326156242Z-q32-k-lookahead-component**：五个case（含changed-Q）全输出A/B逐位一致，CPU FP64抽样、guard、只读输入/缓存/表及重复稳定性通过。四组ABBA Event A8.031193/B8.537401 ms，B慢6.303%；四组分别慢7.0392%、7.0048%、6.8048%、4.4104%。停止此版，不进服务或官方测试，不升级基线。

本批包含编译探针及组件研究；不据局部结果更新官方基线或准确率资格。恢复包以256KiB分块保存，可从bundle索引按偏移和SHA256重组。

[实验总表](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/team/experiments.md) · [本批证据索引](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/codex/pr24-kv-verify-20261024/analysis/publication-q32-k-lookahead-20261030/evidence-index.json)
