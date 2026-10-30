# Q32 K-scale 与 TILE128实验记录

本批新增4条 BI-V150组件/编译登记，历史534行/531run前缀保持不变，候选登记为538行/535run。

K-scale每tile尺度融合：TTGIR循环内score乘法3→2，但组件Event B慢0.872%，且full-output helper与CPU回读存在数值门矛盾，按负结果停止、不重测。TILE128：五case数值门通过，但组件Event B慢5.358%，停止候选。两项均为合成ABI单Attention组件或编译探针，不是服务成绩、官方吞吐或新基线。

原恢复包以256KiB字节分块，按每轮bundle-index中的偏移和SHA256重组。
