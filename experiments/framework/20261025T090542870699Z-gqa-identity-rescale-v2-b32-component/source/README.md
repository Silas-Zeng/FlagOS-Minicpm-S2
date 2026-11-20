# 当前 FULL 热点：N33／bucket40／S16

此 v2 保留原 c62 包不动，候选数学 `7bc22d3b`、基线 `2596cc09`、原 reducer、页序和官方参数均未改。只补当前实例真实 FULL 桶的输入接线，默认 `--shape hotspot`；原 B32/S4 可显式 `--shape b32`，每次由独立 owner 管理，root 串行决定是否运行，不无条件扩大矩阵。

072151 的实际 FULL 八步均为 N33、bucket40、每请求一个 token；max_seq_len 为16646–16653。同 main526 的 `_pick_segments(40,2,16)` 本来就返回 S16，B32 则返回 S4；不是候选修改分割。该组件用 33 条16K随机 KV 和 7 条 padding 对应其桶结构，未采集这些请求的真实激活或完整长度分布，因此不能声称精确重放官方请求。其余完整模型层不在组件 Graph 内。

按实际 runner 构造 metadata：query_start_loc 是 `0..33` 后持续33，seq_lens 是33条16384后7条0；num_reqs/num_actual_tokens均40，max_query_len=1；补齐页表为 null block0，预留真实 block0，padding slot=-1。使用原 Builder/Impl 与 KV writer，要求捕获生产 GQA `(40,2,16)` 和原 reducer `(40,16)`，不会强制替换生产选档。新证据门还核 padding 输出为0、partial保持poison、null block不被 writer改写；来源行与SHA见 `padding-source.json`。

仍使用原严格数值门、同指针变输入 Graph 和16-call ABBA，所有 partial/max/sum及最终 BF16 输出逐位一致；NaN/Inf、负零、subnormal、0长、尾页失败不放宽。S16 的边界长度调整为256/736/739，保证实际存在多个完整页能进入快支；S4原边界64/160/163不变。变输入场景对 ragged 后仍长的 row15 修改实际会读取的 KV/页表；原 v1 修改 row0后恰好把其长度设0，这个覆盖缺口在本独立v2修正。Q/长度变化门继续保留。

原owner、TP1/FlagGems/native14f安装、526源码身份、设备锁、9031检查、420秒有界清理、DB恢复均复用；owner只新增shape参数及透传和run后缀。资源全部保存但只作诊断，真实分支/数值通过后再用Graph净性能取舍。完整验证流程沿用 [v1说明](../gqa-identity-rescale-20261025/README.md)，相关资产逐字包含在此包中。

```bash
python entry.py --shape hotspot \
  --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official \
  --native-library /已核native14f原生库.so
```

只有root启动。CPU增量检查只验证新增padding/分割边界与继承接线；不重复旧数学或已过CPU suite，也不能代替实际编译、Graph或性能。真实原件保存在新 `framework/<UTC>-gqa-identity-rescale-v2-hotspot-component`；通过组件也不自动成为模型/官方资格。
