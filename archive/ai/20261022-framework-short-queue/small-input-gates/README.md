# 短输入局部门：D29 / P128 / KV1024

测试动机是短输入中 CPU 提交成本可能占比更高，不预设收益。仅新增一个混合shape，29个单token decode＋一个128-token prefill，共157 token，KV长度1024；不重跑已验P2019/KV16K及纯Q2048/KV16K，也不把旧正确性结果冒充短shape结果。

两个policy按原字节复制，互不叠加。完整保留各自门的新Q/输出指针、非默认流producer→consumer、padding、KV全字节及RNG检查；C3views还保留scale身份与不支持scale的原异常/回退门。显式要求C3 plan的prefix=29、total=157、prefill=128，实际scope未命中则失败。16个共享旧prefix block覆盖位置[0,256)，新token最早位置896，不发生重叠。32次/窗ABBA与原计时、配额、单卡锁、空闲检查及清理均复用。

上传两个gate、两个policy、一个launcher到同一远端目录；root在当前作业退出并核空闲后选择一个方法：

```bash
bash /path/to/small-input-gates/launch_small_input_gate.sh hot-key-v2 /workspace/experiments/minicpm-s2/code/<实际源码目录>
# 上个controller/worker全部退出、完成清理后，才能运行第二项：
bash /path/to/small-input-gates/launch_small_input_gate.sh c3views /workspace/experiments/minicpm-s2/code/<实际源码目录>
```

`PYTHONPATH`补充原scripts目录，仅供沿用已封存的gate依赖；模型包仍优先来自指定source。原run/source会留完整gate、policy、C2/C3及依赖身份。

准备命令：`python tmp/small-input-gates/build_small_gates.py`。精确源/产物SHA与最小静态检查见[preparation.json](preparation.json)：仅新增shape及描述/plan断言；policy未变，计时和物理页构造函数AST相同，语法通过。未SSH、未GPU。实际命中/指针/流/KV/RNG及收益均待本次上卡验证；局部结果不能外推服务吞吐、42层或准确率。
