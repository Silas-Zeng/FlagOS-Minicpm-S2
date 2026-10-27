# R32＋R64 head温度epilogue：16K原官方四轮入口

仅CPU薄入口，生产源码固定8d1a3de4、809文件、默认启用R32/R64；不修改旧R6431094098或其16K原件。新生产只比R64增加已实测R32形状，精确身份见source-manifest及candidate-source-identity。原服务/common/benchmark、[[16384,1024,64,128]]、native14f与共同初始DB不改；A仍唯一 `20261027T075834Z-main56-control-16k-four-rounds` 完整四轮，首暖及暖均动态读取，不继承4K或旧R64成绩。

新head解析器要求各形状SELECTED与SAMPLED分别闭合：32对应grid2040×1，64对应510×1，未出现形状不冒充覆盖。无选择且无异常可记not_exercised_R32_R64；partial、错误shape/grid、解析错误、REJECTED/RAW_FALLBACK仍停止。原backbone/native/provider/Q32/compute-order源码与实际激活门保持，覆盖与准确率独立，本入口不继承105资格。

KV容量解析仍严格，须唯一正数。新增 `compare_kv_match` 独立记录：不匹配时仍按原首暖筛选、正后四轮，保留实际观测，但不能声称同显存条件下的严格因果收益；不会因96 tokens之类容量漂移反复重启。首冷回执、supervisor记录及完整owner的comparison-conditions均保存实际A/B容量。KV缺失/冲突、原栈缺项、原运行异常及清理失败仍严格处理，不改变官方参数来凑相同容量。

第2轮低于本A第2轮则保留已测轮次并停止；正则四轮完成，不因其后暖轮波动停止。原owner/supervisor command与finally清理AST保持。新增CPU只核逐shape回执、KV匹配/不匹配/缺失/冲突/零值、原stack失败及首暖状态机，详见cpu-check，未GPU/SSH/排队。

root审核、部署精确源码并确认设备可用后再手动决定执行：

```bash
python3 official_supervisor.py /workspace/experiments/minicpm-s2/code/main56-head-temperature-r32-r64-8d1a3de4 main56-head-temperature-r32-r64-16k
```

上例源码目录是建议部署入口；owner仍完整核809文件身份，不以名称代替证明。105入口未适配，等本16K有信号后单独处理。旧R64-only16KB因KV容量不同在首冷主动停止、128SUCCESS且head无覆盖无异常，不是本优化数值失败；该旧结果不覆盖R32资格。
