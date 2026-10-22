# [Draft] 实验配置与诊断开关

默认关闭的CPU线程cap、sampler compile诊断开关、batch/prefix/block覆盖通道，以及原等价block16分支日志。不能把它们记成SQL或Attention收益；正式评测未借这些通道改参数。

基于重建堆叠的`root-restored-baseline-R`；最初所有代码来自比赛原始13eb。与性能方法算法独立；为逐byte复建历史retained tree先单列。默认无环境变量时不启用覆盖；不建议借本PR修改比赛参数。

本PR只含manifest列出的增量与独占中文说明，不把其它方法算入本方法。代码为已留存实现的字节拆包；不能把本次重新打包当成新设备/准确率验证。逐项字节身份和父版本见manifest；完整方法之间的依赖与历史证据范围见实验库framework-inventory。请保留Draft并按团队评审决定合入，不把六个PR分别宣称为已独立通过完整官方成绩。
