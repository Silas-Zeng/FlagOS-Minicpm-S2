# 夜间 prefill 单核硬件计数

仅准备，未执行；复用已测组件 c0fc8d88，worker/内核/输入/原数值门不变。
入口只改 profiles 输出目录、ixkn 包装和 wrapper 提前退出时的所属进程组清理。
过滤 `kernel_biv150_prefill_normalized`，skip=2，count=1，只采原 baseline launch。
prefill 的前两次实际调用后采第3次；GQA 第一次真实 impl.forward 捕获的是原 page16 内核。
命令来自本机 ixkn 的 help/list-sections；不保证计数权限与 replay 可用。
单次420秒上限。失败一次就保存并跳过，不扫参数、不修驱动，不重复负候选研究。

报告和所有原件进入 `profiles/<UTC>-prefill-one-kernel-counters`。
整个 run 的 wall/Event 时间均受 profiler 影响，禁止作为性能收益、官方成绩或新的组件资格。
复用的 worker 仍包含旧组件候选；其计时只为保持已测入口，不能重新解释为候选复测。
核对报告实际 kernel/grid/resources 与本 run 原 baseline IR；无法匹配则标未取得可归属计数。
计数可帮助选择访存/计算/发射方向，不能直接证明整模收益或 SIMT 优于 TCU。

参数：
```
python entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official --native-library /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control/native/biv150_native_w8a8.so
```
运行前确认唯一 BI-V150 与9031空闲，创建 profiles 父目录；同一时间只运行本入口一个实验。
入口完成且清理、DB/source/native 回执通过后，才能开始下一任务。
