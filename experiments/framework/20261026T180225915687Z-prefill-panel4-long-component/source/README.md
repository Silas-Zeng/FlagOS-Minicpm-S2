# 长prefill 4个K panel：一次完整组件

纯CPU准备，未GPU。基线main594原stride+Q-hoist/BM128/Q16/T64/w8s1，候选保持相同单panel热body，只分4个绝对K范围、写split-major FP32 acc/M/L，并调用新增8-head reducer。不是启用原IS_3D路由，不叠LPT、SME、affine或旧错误history-tail。

只Q2047/KV16384/ctx14337、packed NHD/page16。同一K/V总量不变，原225–256次loop变每CTA最多64次；grid4倍、Q加载4次、增加部分写读/归约。每panel双head KV约4MiB是逻辑访问范围，不是实际L2命中证明或收益保证。partial67076096B＋max/sum1048064B＝68124160B（约64.968MiB），只一份组件workspace，不隐瞒容量或预称生产跨42层复用。完整B每call有producer+reducer两个launch，A一个；Graph只作独立换值/写覆盖正确性资格，性能为直接暖JIT完整ABBA，scratch分配在计时外但读取/写入在内。

原writer/非64对齐ctx/完整及末ragged query块、独立FP64 sampled max_abs5e-4/relativeL2.01、换Q/K/V/页表Graph、输入/RNG/输出哨兵保留。新增scratch NaN poison证明回放写覆盖。跨panel归约改变数值树，跨臂bitwise仅诊断；新增全输出atol5e-4/rtol.01 hard门，未放宽原FP64。候选仍必须实际命中原Q-hoist并保留实际LLVM循环Q读0，否则停止，不移植history-tail IR编辑器救过关。编译/数值错误即停，过门只一组完整ABBA，净负即停，无自动sweep或模型后继。

2026-10-27在线核所有作者PR，最新编号62；PR47新head2186704是BM256/Q32/w16并正在main594独立验收，非已合并；PR46为同Q32后缀，PR31为decode splits。PR38 71卡未见本split-major producer＋8-head reducer同构实测，旧splitKV只因缺并行证据未立项；增加CTA不自动少wave或少点积。本方法需用完整实测证伪，不以理论保证才允许测试。PR49三种INT8 KV完整链已负且未取得BF16精度资格，不复活该路线。

root唯一排卡，先独审kernel.diff/worker.diff/reducer.py/cpu-results.json：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/prefill-panel4-long-component-20261027/entry.py --source-dir /workspace/experiments/minicpm-s2/code/main594ae2-pr59-20261026 --native-library <已核14f原生库.so> --case long
```
