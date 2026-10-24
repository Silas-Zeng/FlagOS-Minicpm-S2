# 末层 tail 局部门 v2：真实单 rank 初始化

旧 `123334` 门已退出并 settle，但在任何数值 case／计时前失败：actual `ModelWeightParameter.__init__` 即使 `disable_tp=True` 仍调用 `get_tensor_model_parallel_rank/world_size`，原局部门未初始化 TP 组。旧 `tmp/next-last-layer-tail/` 四资产保留原字节，不能引用为数值或性能通过。

本目录仅修局部门生命周期。使用 root 取回的 actual `parallel_state.py`（`1feda9ac…`）和 `parameter.py`（`ff6054fb…`），在原 current VllmConfig 内、构造任何实际投影参数前，以 actual 平台 backend 和本轮独占 `file://.../world1-rendezvous` 调用原 `init_distributed_environment(world_size=1, rank=0, local_rank=0)`，再调用原 `ensure_model_parallel_initialized(TP=PP=PCP=DCP=1)`。没有 fake group、rank monkeypatch 或服务参数修改。拒绝已有组、非单 rank 配置及不可用 backend。

finally 先执行原设备 settle，成功后分别尝试原 `destroy_model_parallel` 和 `destroy_distributed_environment`，记录错误及两项实际初始化后态；部分初始化失败也走清理。若设备不能 settle，不销毁组或丢弃强引用，交唯一 owner 终止 child。真实组 API 的执行和销毁仍待本门验证。

`last_layer_tail.py` 保持 **99d5a8c86dac67b7a2c0029842576fbd1439060525d4c6789b0ddd32703fc9ec**。两份同 indices 的前置 gather、O projection／两次原 RMSNorm／MLP 顺序、局部容差、输入／RNG 检查、新指针非默认流、32-call ABBA 全部保持原样；删除新增块后 worker 逐字节逆回旧 25d3。它仍是随机 BF16 权重的 actual 类 eager 局部门，未接生产 Inductor／AOT、未验证整模型 KV／采样／准确率，也不能直接把 N 行结果接回原 M 行 runner。

冻结资产：

- worker `validate_last_layer_tail_v2.py`：`8e4903e37dedb423070bb33e506cc76c2de0b70c54a3412d14d651e6494b6bbf`
- outer `launch_last_layer_tail_v2_gate.py`：`510bd1623177d00a7bd5cd6f462dfccb439a0cab2e362cb107ce1a977297e206`
- 薄启动器 `launch_last_layer_tail_v2_gate.sh`：`d756898283f2c65db6a34dcdfe2964572ca7aeb2cd6538e7337fbdf7516f5a8b`
- helper：上述 99d5，未改。

四件上传 `ROOT/scripts` 后由 root 串行执行 `bash launch_last_layer_tail_v2_gate.sh`。outer 仍使用原干净 6f 完整 412 文件基点与唯一设备锁／双 idle／9031 双栈／超时进程组清理／DB 前后／source 和完整 seal；仅新增两实际安装源码归档、v2 worker pin 与唯一 `-last-layer-tail-v2-gate` 后缀。

上卡前 CPU `v2-check.json` 已保存语法、stdlib runpy／help 无 Torch/Triton/vLLM 导入、原字节逆回与旧 owner 函数 AST 一致性；Bash `-n` 通过。首次静态逆回检查多留一空行而断言失败，修的是检查器删除边界，未改 worker，已在记录中保留。hardware 已只读实际 API 和新增生命周期／外壳差分，无当时短门阻断；本 owner 没有重复旧套件或设备运行。

## 124358 实际结果：数值门未过，暂停

root 后续设备回执：真实 TP 初始化与清理成功；默认输入的 final hidden／residual 完全 bitwise。换值／新指针／非默认流 case 有限性、输入和 RNG 检查通过，但 hidden max abs 为 `0.0234375`、residual 为 `0.017578125`，原 `atol=0.01, rtol=0.01` 两项均未通过，故**没有运行计时窗口**。这是 root 回执，本 owner 尚未另行读取完整原件；原门和阈值保持不变，不把首次 bitwise 当全部数值正确。

源级尾段按行独立，但 M2048→N2 可能令实际 BF16 GEMM 选择不同 shape 配置／累加路径，误差也可能经过 MLP 和两次 norm 传播。当前第二 case 同时更换数值、指针与 stream，不能据此区分形状相关舍入和底层非默认流行为。Python 接线已有 ready record→side wait→同 side 两条尾段→done 的顺序；这不能替每个底层算子证明其 stream 实现。

如以后恢复本方向，最小诊断仅补“同新值在默认流”和“原值在 side 流”两项交叉条件，与已有两条件组成 2×2；使用同权重／相同 gather 和原阈值，若仍失败再记录 O／postnorm／MLP／finalnorm 的首个差异位置。**此计划未编码、未执行，不新增 v3 或设备测试，不阻塞当前 V-late/cache 主线。**
