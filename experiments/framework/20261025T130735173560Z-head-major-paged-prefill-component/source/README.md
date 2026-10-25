# Head-major 长 prefill：一个分页读取组件

只测试 M2047、KV16384、Q16/KV2/D128、BF16、page16。三臂分别为当前 main526 normalized＋Q-fragment、原 FlagGems v5.3.5 的 BM128/N32/w4s3，以及新 page16 行式分页读取＋N64/w4s3。新 loader 按 `[页,16 token,128 channel]` 读取 K/V，再将 K 片段变为 dot 布局；原反向循环、softmax、causal 和输出保持。N64 同时改变分块和归约顺序，收益只能归属整个候选方法。

原件 `flash_kernel_original.py` SHA256 为 `eef0202e6c0ed08bef8098adede1a603c63354c54b54a19414e210b675157265`，已与上游 v5.3.5 Git blob `134075b148126a010734e49effedc554da801b68` 核对；设备实际安装文件须逐字相同。`candidate.diff` 只增加 helper、替换 varlen 的两个分页 load 调用。不会修改安装文件或开启已有替代 backend。

当前 BM128=16 query×8 head，新/原 FlagGems BM128=128 query×1 head；M2047 时主要 CTA 数均约256，不声称8倍KV复用。预期减少页号/地址计算重复，并研究 Q 行局部性；成本包括 head 间缓存竞争、更多因果边界工作、N64 与 reshape/transpose 的寄存器或 shared-memory 成本。设备 IR、机器码和资源原样保存，不凭设计宣称收益。

入口复用已受测 affine-v2 owner、main526身份、实际 TP初始化、FlagGems dispatch、原 writer、DB备份恢复与 ABBA。真实 Builder/Impl 捕获当前 kernel 参数，核实际 NHD stride `(8192,256,128,1)`、K/V storage offset、8192列页表，前8物理页倒序。各臂读同一写后 KV。用独立 NumPy FP64 dense causal 参考抽样7行×4头；合成数值门固定 max_abs≤5e-4 且 relative_l2≤0.01，不能代替模型正确率。随后同址更换 Q/K/V、历史cache和页表值，原 writer再写新KV；每臂 CUDA Graph重放须逐位等于该臂fresh eager，输入/guard/RNG检查通过才计时。

原 FlagGems helper 对标量 k_len 的二维索引可能暴露原有编译限制。先编译原件；若是 Triton CompilationError，保存原异常并将该臂标为不可测，随后仅比较当前实现和独立新loader，不声称相对原FlagGems收益，不修原件来凑三臂。原库若出现设备运行错误则全组停止。候选编译/tile约束/数值门失败也立即停止，不调整模型或框架让候选过关。

计时为原库/current、候选/current各一组16调用ABBA，GPU event与wall/CPU提交分别保存，包含各自真实launch wrapper及原库/候选LSE写出。预分配临时小张量，原writer和共同metadata准备不计入Attention差额；没有额外大KV整理或复制。这个测量只能形成组件信号，不是生产全栈或官方吞吐结果。

```text
python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/实际已核main526目录 --native-library /实际已核native/biv150_native_w8a8.so
```

root 唯一调卡。入口持 `framework-device.lock` 并检查9031/ixsmi，记录新UTC目录、owner/worker/monitor PID、命令、环境和原件；worker最长420秒，只清理自有进程，恢复本次起点DB。此包不启动模型服务，不把native-on历史准确率继承给组件或新基线。

CPU 仅 AST、原件SHA、分页地址推导与 `entry.py --help`/无加速器import检查；尚无GPU编译、精度或性能结论。原始输入、输出、FP64样本、实际ABI、IR/资源、计时及失败均由设备worker自动落盘。
