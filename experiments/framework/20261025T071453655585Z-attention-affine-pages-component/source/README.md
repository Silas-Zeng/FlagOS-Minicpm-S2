# 现存连续页段：一次有界组件入口

v2 只修 source identity：首次 owner215154 在建 run/启 GPU 前被一条 symlink 误拒。Git mode120000 的 `E=256,N=512,device_name=nvidia.json` 在已受测 manifest 中 SHA 为 `c978f595…`（62 字节链接文本），被 `Path.read_bytes()` 跟随后却读到了 SHA `97ccbad3…` 的 3242 字节目标 JSON；不是换行或生产源码变化。现在原样复用成功 v3 的 `source_identity.py` 与 main526 manifest，按链接文本核 Git 源码，目标 JSON 在清单中的独立条目继续核字节；没有改期望哈希或放宽断言。原02f包保持不动，v2 kernel/worker/dispatch/bootstrap/数据/计时逻辑均不变。

仅 CPU 准备，设备由 root 启动。固定 main0bf9/526 文件、既有 native SO；无模型权重、无服务、无官方收益或模型合格声明。root 正在核查 main 的 mixed 语义问题，本门结果不能取代它。

入口复用旧 Q-fragment 门的 `make_data`、`timed_batch`、`preflight` 原件；当前 main 安装完整 C2/C3/GQA/正常化/Q-hoist/native 链，从真实 backend 捕获 P2019、M2048、page16、stride8192 的 kernel kwargs。候选独立 JIT 使用当前 `Manager`/IR 变换，保留 GQA 16Q/2KV/head128 的原计算。实际源和 SHA 均封包，安装源码不改。

顺序：KV16K 连续页先判上限，后单大段加碎片，再 KV4K 同组；每组先严格 output bits、KV/RNG/guard、同一 JIT 换页重新提交、Q-hoist/无 spill/实际条件页表 load 的 TTGIR 分支，过门才 16 调用 ABBA。连续页 `42 × 单层 GPU 差额 − 一次计划与 H2D` 非正即早停余下项；所有已做轮次保留。描述符 CPU 计划＋pinned fill、H2D、kernel event/wall 分开记录，42 层摊销只是筛选估算。这里没有 CUDA Graph capture/replay 的生命周期结论，也不以旧 SAVE 页表替代当前生产覆盖。

```text
python3 entry.py --source-dir /workspace/experiments/minicpm-s2/code/实际冻结main526目录 --native-library /实际已核native/biv150_native_w8a8.so
```

控制器持 `framework-device.lock`、查 9031/ixsmi；新 UTC run 位于 `framework/`，记录 owner/worker/monitor PID、命令、环境、原件、DB 前后与原始日志。worker 最长 420 秒；仅清理自己的进程组，保存并恢复自己启动前的 DB。两臂同一 worker/native/FlagGems/DB，ABBA 期间 DB 变化则失败，不给收益结论。入口可先 `--help`，不导入加速器。

CPU 尚不能确认真实编译器是否保留 affine 分支、Q-hoist 是否兼容新 CFG、descriptor 的 SGPR 成本；任一门失败立即停止计时，保留真实 TTGIR/LLVM/ASM。初次设备编译失败也是实验结果，不自动放宽断言或换别的内核。最终由 root 审阅后冻结此目录再上传；本子智能体不启动 GPU。

CPU 已通过全部 Python AST、`entry.py --help` 和 `import worker`；最后一项确认 `torch/triton/vllm` 均未导入。无设计占位或后台任务。机器码的条件执行仍由 root 在保存的 ASM 中复核；自动门确认的是真实 TTGIR 分支，不将静态分支等同于已证明的 stall 降低。

root/独立审阅指出缺少真实 TP group 后，已原样复用 `final-query-row-component-v3/distributed_bootstrap.py`：在实际 EngineArgs config 下建立 world1/TP1、独立 file URI rendezvous；外层 execute 在 finally 同步设备并销毁 model/world 两组，失败保留 `distributed.json`。不伪造 `_TP`，不复用其它 worker 的组。

最后接线已完成：先 `import vllm_fl` 保证 dtype 兼容，在同一 config context 内依次 bootstrap → `register_oot_ops()` → 成功 v3 原样提取的 `enable_dispatch()` → `model_runner`。只提取该函数、`INDEX_SHA` 及两个小 helper，保存 `flaggems-oplist.txt`/真实 index dispatch 证据；两臂共用注册状态，没有“以后再决定是否开启”的待办。其它 kernel、数据、分组与门限不变。
