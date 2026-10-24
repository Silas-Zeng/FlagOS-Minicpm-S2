# 末层 FFN 按 logits_indices 提前选行：独立组件

来源是成功 main526 官测的实际末层 wrapper `source/wrapper-subgraph-42-0.py`（32458fbd），保留原件。`prepare.py` 只用 AST 提取实际三个 Triton kernel 和第597–624行 suffix，逆回检查数学与 launch 语句不变；不执行文件首历史 docstring。`exact_suffix.py`（22354a39）保留 FP32 融合残差、SiLU 与最终 norm，不能换成按 FX 注释逐步 BF16 舍入的 eager oracle。

组件按实际 worker 启用 FlagGems 的 enable-all 分支，vendor 默认排除仍由原库处理；两臂使用 runner4474 原来的 `[indices]`，而不是不同 dispatch 的 index_select。设备结果须同时记录实际 registrar 函数绑定、BI mm_out 源SHA4c2e23da、两份 CUDA dispatch 表及 warm 后真实 mm_out/index 的 op 日志；未实际启用就拒绝，不把纯 Torch/cuBLAS 测量当成服务路径。配置来源 worker/iluvatar YAML、161030实测 mm.py 原件已保留。

比较起点是 self_attn 已经返回的 o_proj 输出及残差，二者都是 BF16 `[M,2048]`、stride `(2048,1)`。基线计算完整 suffix 后按 indices 选行；候选先分别选两份输入，再执行相同 suffix。两次 gather 全部计入 wall 与 Event，不计算也不宣称省去 o_proj。所有行序与重复行均原样保留。真实模型必须传原 logits_indices（包括部分 prefill 的临时采样行），不能自行推算“每请求最后一行”。

`component.py:run(run_dir, model_path)` 是设备组件函数，导入本文件不导入 Torch。`run_component.py` 是独立薄 owner：复用原35d helper，在实查 GPU/9031 空闲并持锁后启动唯一子进程，300秒上限，记录 PID/日志/GPU采样；结束按原6秒清理并核空闲，保留DB前后快照后恢复原DB。异常不重试、不开服务。此处只完成 CPU 准备，未调用 run。

设备执行命令（仅 root 安排空档后显式运行）：`python3 run_component.py --run-dir /workspace/experiments/minicpm-s2/diagnostics/<唯一UTC>-final-ffn-row-prune`。结果 `results.json` 的 completed 只说明组件执行完整；数值差异与模型准确率另判，不因 exit0 自动批准模型集成。

未来调用从 `/workspace/MiniCPM5-2B` 的 safetensors 加载 layer41 的 postnorm、gate/up/down 和 model.norm，逐项记录真实 BF16 hash、shape、stride。gate/up 拼接顺序按同实例 Llama loader 的 shard0/1；设备权重布局严格匹配实际 wrapper。激活是明确标识的合成 BF16，不冒充已回收模型激活。

- 四组：M2048/S32、M2048/S64、M32/S32、M64/S64。后两组只在明确 identity 合同下保留原路径，不能仅因 S=M 便跳过选择。
- 每组先热编译，两臂保留实际 generated heuristic；记录 eager 与 CUDA Graph 三组 AB/BA/AB，总 wall 包括两 gather、分配/调用及末端等待。Graph 固定 M/S，另两次改变投影输入、残差、GPU indices（含非单调和重复）再与新鲜原 suffix 对照。
- 预填充改变 GEMM 的 M 可能改变 BLAS 算法/舍入，原样记录 BF16 位差、max/rms 绝对差与 relative L2，未设置随意“准确率通过”阈值；decode 原路径必须逐位一致。后续模型接线和完整105题由 root 决定，组件不替代它们。

量级：两个 GEMM 原 M2048 合计约154.62 GFLOP，S32/64分别约2.42/4.83 GFLOP，仅是末层的运算量。新增两输入 gather 输出合计256/512 KiB，实际读写加倍；两臂仍读取约72 MiB FFN 权重，小 M 在16SM上的利用率必须实测。两臂原末尾选择的成本也保留，不能只扣算术量预测吞吐。若包含 gather 的总 wall 无改善，或数值差异需不可接受的数学改动，则停止；有改善才接模型精确 logits_indices/残差/图合同，不扩大到其它层。

CPU 入口：`python -B prepare.py` 后 `python -B check_cpu.py`。它们只做源码提取、逆回、语法和输入合同，不加载权重、Torch 或 GPU。冻结资产及独立审核见本目录 manifest/回执；原535/538/RoPE未修改。

CPU六项通过；teammate已独立审阅新数学提取、权重/stride、两条 Graph 同路径 fresh 门、双 gather 计时与薄 owner/DB恢复。新增 FlagGems dispatch 接线另做窄审；root回收的三份真实 installed API 与所读参考逐字一致，绑定/日志字段已核。尚无 GPU 数值或性能结果，不把代码审阅写成设备通过。
