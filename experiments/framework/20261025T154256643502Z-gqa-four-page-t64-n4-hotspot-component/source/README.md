# BF16 GQA T64/W4：固定 MMA 沿 N 分 warp

唯一后继：基线仍为原生产 T16/W1；候选保留受测 T64/W4 的全部 Triton 源、地址、page16/S16、输入和 reducer，仅在候选私有 JIT 的实际 TTGIR 中将唯一 `#mma` 的 `warpsPerCTA=[4,1]` 改为 `[1,4]`。其他 IR 字节可精确逆回；blocked/shared 布局和显式 P→opA 转换保持，交给原编译器完成合法 lowering。无生产 hook、全局 compiler patch 或数学修补。

依据：实测 W4 `20261025T152940014266Z` 数值通过，Event 1.278072→2.105123 ms，仍慢 64.71%；VGPR113、SGPR spill92、shared32KiB。实际 MMA `[4,1]` 沿 8 行分 warp，尚未检验预想的列分摊。当前 QK 8×64 的四个 16 列块和 PV 8×128 的八个块可沿 N 分配，八个逻辑行仍位于同一个16行MMA块；同后端已有 M2/N128 的 MMA `[1,8]` 产物。不能据此预判性能：Q广播、P布局转换和跨warp softmax成本可能抵消片段节省。

复用已测私有 compile→TTGIR `ir_override` 机制，冷编译先存原件、仅变一条别名，再要求实际编译的 MMA `[1,4]`/warp4、新 hash 与原 ABI。每次 eager/Graph launch 检查实际 hash 属于本次选中产物；编译拒绝、重写回旧布局、数值错误立即停止，不 fallback 成原核冒充候选。原八类数值、独立 CPU FP64、padding/Graph/guard/RNG 与完整 producer＋reducer 单组 ABBA 不改，不扫 T32/w2/w8/其他形状。

入口仍 `python3 entry.py --source-dir <冻结main526> --native-library <原14f库>`，仅 root 调卡。`mma-layout/` 自动保留原/变换 IR 与编译证据，`ir-candidate/` 保存实际产物。`wiring-check.json` 仅本轮新增 CPU 检查；旧 `cpu-check.json` 是原组件回执，未重跑旧门。组件不授予模型/官方准确率或收益资格，原 W1/W4 负结果不变。
