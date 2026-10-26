# BI-V150单项BF16连续流读参考

只准备CPU资产；不是优化、模型验证或官方成绩。复用已审owner的非阻塞设备锁、GPU/9031 preflight、source/native pin、DB保存/恢复和自有进程cleanup，仅将run标签改名、输出改至profiles。worker不导入模型/native。既有owner其余字节不变。

单一配置：512MiB BF16连续源，BLOCK8192、4warps/1stage，每CTA累加FP32 checksum并写4B。每次明确读536870912B、写131072B；只报告读取字节/Event的逻辑有效率，另列输出写字节。工作集远大于16MiB L2；无autotune、无tile矩阵、无计数器。checksum归约也有成本，因此这个数字是可达到的连续流读参考，不能当HBM物理上限或散页KV硬上限。

1和-0.5两种内容checksum校验，另一次device copy完整torch.equal校验（不报copy带宽）；3次预热，关闭profiler后单核完整Graph、3组固定16replay，保留全部Event/wall。总计时流量24GiB，预期设备耗时量级几十毫秒；编译/owner启动另计。IR/ASM用于确认真实load/小输出实现。没有自动后继。

root统一排唯一GPU，解包至scripts/biv150-stream-read-reference-20261026后：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/biv150-stream-read-reference-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official --native-library <已核14f原生库.so>
```

判定：若读参考显著高于当前GQA必要KV有效率507.60GB/s，说明不能把当前GQA当访存屋顶；若相近，只支持“缺少大带宽余量的证据”，归约/布局/指令成本仍使饱和结论不成立。不再为寻找峰值新增配置或重复微测。
