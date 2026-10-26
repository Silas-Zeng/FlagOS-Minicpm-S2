# M64 down：只按N128分块的BF16布局

仅CPU准备，未GPU编译/数值/计时，未改生产。新布局是 `P[N/128,K,128]=[16,6144,128]`，只移动BF16位、不量化、不改官方参数。与已负 `P[N/256,K/128,256,128]` 不同：本消费者每步固定 `BK*128=8192` 个元素，不含K128边界select跳跃；三维contiguous权重原样传入，未flatten成1D。

实际依据是本次main6971 Graph的down hash `15ef15aa299d507601ce6980ee4bd56928142529471fbb7e63ea9470df04af6f`：BM64/BN128/BK64、w8/s2、grid16、shared49152、SGPR39/VGPR31、spill0，原B dot useSme2。动态M/N/K未被逐参数直接截获；M64来自本Graph，down 64×2048×6144由模型几何/邻接与grid闭合，运行时仍必须沿原opaque调用捕获真实config。若不是固定64/128/64/w8/s2/SPLIT1就停，不换tile或扫描。

旧pack的1D P不满足安装JIT前端SME选择器的至少二维条件；因此旧B无SME不能主要归因select。新P最后两维6144×128自然满足row-major门，原K循环、GROUP8、`acc+=tl.dot(a,b,allow_tf32=False)`、最终BF16及尾M mask保持。预期是B物理tile由跨1560704字节地址窗变连续16384字节，并可能改用SME row方向；原col SME已有效，不存在已证实的通用B转换瓶颈，也不保证HBM流量减少。实际B SSA到useSme1或2及SME指令只作诊断，不作为数学门。

仅真实layer0 down、合成M64输入，完整调用A=原 `torch.ops.biv150_stable_small_o.linear→F.linear→FlagGems`，B=新输出＋N-only消费者；原默认FlagGems上下文和已装linear SHA固定。保留4种eager逐位/有限性/输入不变、独立FP64、两次换值毒化Graph、side-stream、RNG门，并加尾M63逐位。任何错误立即停，不放宽容差。全部通过才唯一ABBA；非正停止，不自动跑权重环/模型或改基线。

输出buffer按实际调用在Graph capture时分配；Event是完整GEMM Graph replay，不含每次eager CPU allocator、加载pack、主机view成本。原W和packed各24MiB同时保留，不能报KV容量收益；单层热态也未包含42层权重/Attention/KV交织，正信号仍需主线决定下一步。

root实查GPU与9031并安排独占后，解 `entry.tar.gz` 到独立脚本目录，入口：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/bf16-nonly-down-component-20261026/entry.py --source-dir /workspace/experiments/minicpm-s2/code/20261026T013104Z-main34942f7-prefill-stride-official
```

owner、DB锁/恢复和清理复用已测组件，只改run标签与scope；本包不导入native。CPU合同/源码版本见 `cpu-result.json`、`preparation.json`、`asset-pins.json`，精确包SHA见 `package-receipt.json`。负结果包和原件不覆盖。
