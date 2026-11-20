# B32 空 padding 验证器修复

v2 的热点档 N33/bucket40/S16 已真实通过8组数值/Graph检查，event 1.280913→1.310480ms，耗时回退2.308%，wall回退2.224%；资源同为93 VGPR/shared8192/零spill，SGPR64→63。此结果是负组件信号，不接生产。

随后 B32/S4 互补对照在2026-10-25 09:06:03 UTC因验证器调用空切片 `.all()`，触发FlagGems `n_elements=0` 的除零异常；尚未登记首case、未进入计时，不能归因候选数学。原v2包9e6e及失败原件保留。

v3只把两项padding专用检查放到 `active < B` 分支，`active == B` 时直接记True，禁止空切片归约。其它正确性、完整partial位比较、Graph、KV/RNG、ABBA、候选数学7bc22、原reducer、原生产路由、FlagGems与owner全部不改。CPU直接执行实际新增if，B32零次all、B40八次非空all、损坏padding仍拒绝；其余worker恢复该if后完整AST与v2一致。

```bash
python entry.py --shape b32 \
  --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official \
  --native-library /已核native14f原生库.so
```

这是最后一个互补短测：B32/S4每split约256页，较热点S16约64页可能有更多稳定max页，仍以逐位正确性与Graph ABBA判定，不能外推完整官方收益。原owner字节复用，run后缀仍写v2，使用run内资产SHA区分本v3验证器；唯一UTC目录不覆盖任何旧结果。420秒超时、PID/日志、设备锁、9031、DB及进程清理复用。root统一上卡，子智能体仅CPU准备；[v2说明](../gqa-identity-rescale-v2-20261025/README.md)保留完整范围与已知限制。
