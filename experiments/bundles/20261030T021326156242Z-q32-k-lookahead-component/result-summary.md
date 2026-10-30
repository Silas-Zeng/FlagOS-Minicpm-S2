# Q32 K-only 预取：数值通过，性能负，停止

尝试将下一 tile 的 K/K-scale 加载提前到当前 PV 前；Q 编码、score/softmax/PV 数学和 TILE64 保持不变。编译产物确认存在跨 PV 的加载窗口，VGPR135/shared57344不变，SGPR spill98→88，但这些静态指标没有转为净收益。

独占 BI-V150，BM256/BQ32/TILE64/w16/s1，主要计时形状 Q2018/context12108/KV14126。五例（含 changed-Q）全输出 A/B 逐位相等、CPU FP64 选定参考、只读、边界及重复稳定性通过；四组 ABBA×50 的均值 A 8.031193 ms、B 8.537401 ms，B 慢 6.3030%，四组均负。

停止此版，不跑官方长测、不更新基线。它增加了页表/掩码与跨轮状态，具体成本贡献未用新 profiling 分解；不把静态顺序当作已隐藏延迟。本次为合成 ABI 组件，实际 SME=3；暖态的额外 bits15–17 对应 dead segm 指针，占位差异已另记，未冒充服务实测。

编译60件、组件70件原始证据已完整回收。入口：[编译结果](validation/result.json)、[组件结果](component/result.json)、[终态审阅](component/terminal-review.json)。owner98495/child98497已退出，GPU与9031后检空。下一步优先减少实际热路径工作量，不扩展本候选组合。
