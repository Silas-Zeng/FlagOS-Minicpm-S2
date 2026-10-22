# 当前组合版本的输入准备等待诊断

仅将原诊断适配到 `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141` 组合 runner；原 `tmp/input-prep-timing/` 保留。metadata/async helper 必须分别匹配 `0e961524…` / `1bb85e31…`，缺失或改变就拒绝准备。模型、官方短筛参数、原 scope/wait/Event 行为均不改，默认不安装。

主负责人上传以下三个文件至同一远端目录，再显式提供完整组合源码目录：

```bash
bash /path/to/input-prep-timing-combined/launch_input_prep_timing.sh /path/to/current-combined-source
```

启动器仍复用 bc51 原短筛、decode4k、seed721201、空闲检查、DB前快照与PID记录。不能把只含 runner 的 `resolved/` 当完整基点；准备器要求两个组合 helper。精确命令和全源码映射自动保存到 control；后置DB、清理、收集按原流程。

统计含义复用原包：只测真实 `execute_model()`，dummy不计数；preprocess包含原等待、准备区和原event.record，不含forward。第64/128/256……次稀疏快照写在计时区外，正常退出补最终；强停可能只有部分累计。首个 recorder 导入/建目录在时钟外可能扰动首等待。诊断本身有CPU成本，不能用其吞吐报告优化收益。

新增验证已完成：`python tmp/input-prep-timing-combined/check_combined.py`。原e155和6f918的被测context manager AST相同；新增诊断分支、计时helper与原已审版本逐字节相同；真实/dummy锚点唯一。实际412文件组合归档完成一次完整准备调用，得到413文件，只改变runner并增加诊断helper，原包未变。没有重跑旧异常/快照合同，没有SSH/GPU。

- 命令：[check-command.json](check-command.json)
- 结果与精确SHA：[cpu-check-combined.json](cpu-check-combined.json)
- 完整准备回执：[prepared-source-preparation.json](prepared-source-preparation.json)

新诊断runner SHA：`bda3ac44d81c9e0476799f03f189824cfb62a4b3081290a382a39c84b11cb4fc`。结论：CPU准备 ready；真实等待占比待root上卡诊断。
