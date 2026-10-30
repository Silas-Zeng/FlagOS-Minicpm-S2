# Q32 K-only lookahead

在当前QK MMA之后、PV之前发起下一KV tile的K/K-scale加载，尝试覆盖全局访存延迟；增加预取状态和活跃值。ASM确认跨PV候选窗口且编译资源未增加。组件五case数值门通过，但四组ABBA中B慢6.303%，停止，不进入服务/官方测试或更新基线。

- [20261030T015910809947Z-q32-k-lookahead-compile-probe](../runs/bi-v150/20261030T015910809947Z-q32-k-lookahead-compile-probe.md): 编译审阅在QK后、PV前定位到下一tile的页/K/scale加载，当前tile PV之后有完整vmcnt等待、下一轮才消费carry K，形成可能的重叠窗口；这只是机制窗口证据，未证明隐藏延迟或速度收益。VGPR135/shared57344均未上升，ASM SGPR spill计数98→88；仅writer与编译，无reader、数值或性能。
- [20261030T021326156242Z-q32-k-lookahead-component](../runs/bi-v150/20261030T021326156242Z-q32-k-lookahead-component.md): 五个case（含changed-Q）全输出A/B逐位一致，CPU FP64抽样、guard、只读输入/缓存/表及重复稳定性通过。四组ABBA Event A8.031193/B8.537401 ms，B慢6.303%；四组分别慢7.0392%、7.0048%、6.8048%、4.4104%。停止此版，不进服务或官方测试，不升级基线。
