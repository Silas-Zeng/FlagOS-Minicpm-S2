# 旧 467/a42 关闭 native 的原 mixed 隔离诊断

旧467/a42开启native已复现同mixed异常。本轮只在freshserver启动前设置已有开关 `VLLM_FL_BIV150_NATIVE_W8A8=0`，隔离该路径；不是合规优化、性能测试或新基线。原 33392 请求模块、两份请求、lifecycle 和 cache_gate 逐字复用；仅返回 token IDs，原采样和首内容同步不改。原 main526 的 99/105 与 mixed 故障分开判断。

- 来源：131603 的 commit 1ad9a708、tree d1a96e3f、467 文件、native a42f71e2，原完整准确率 100/105。使用原件固定 SHA 和 Git blob；旧 SHA 对 symlink 跟随目标，Git blob 仍核链接文本。
- 源码 `/workspace/experiments/minicpm-s2/code/20261024T131603Z-pr24-isolated-cache`；SO 从对应 accuracy control 的 `native/biv150_native_w8a8.so` 复制，原文件不改、不编译。
- 保留 `VLLM_DISABLE_COMPILE_CACHE=1`，每轮新私有 VLLM/Inductor cache，原 common35d SERVER 和服务参数。禁用缓存不要求默认 cache/AOT/COMPILE_SEMANTICS，保存本次私有根唯一 backbone，要求安装日志installed=False且实际图0个biv150_native调用；不套34native门。
- 当前 DB 只备份、运行后恢复，不播种 131603 的历史 DB；因此本轮是旧整套代码在当前 DB 的正确性诊断，不是完全复刻旧环境或吞吐对照。原设备锁、卡/9031 空闲检查、所属进程清理与失败原件保持。
- 仅3项语法/窄差分核对，原受测入口及8项请求边界测试复用。没有 GPU/网络或生产代码改动。

将包解到独立 scripts 目录后：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/pr24-467-native-off-mixed-20261025/verify_service.py --source-dir /workspace/experiments/minicpm-s2/code/20261024T131603Z-pr24-isolated-cache --reference-control /workspace/experiments/minicpm-s2/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control
```

run 自动落 `framework/<UTC>-pr24-467-native-disabled-mixed-token-diagnostic`；旁边 `-control/state.json` 记录 PID、原件身份、DB 与清理。必须读取 `model-path/evidence.json`、`diagnostic-summary.json` 以及 mixed 原始 JSON/SSE/token IDs；语义失败仍收齐双请求后退出 1。不得以 105 未达标直接归因 mixed 或任何 PR。原先 131603 accuracy owner 不能直接启动，否则会重跑 105。

冻结93e原包不变；只在owner清洗环境后明确设置开关，原源/SO只做身份核查，不加载或改写native。关闭会恢复原BF16权重及常规MLP/UnquantizedLinearMethod路径，显存/KV容量可能随之改变，结果不能单独归因某条native指令。
