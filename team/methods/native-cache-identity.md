<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# native 编译缓存身份与重启

PR25叠加native编译缓存身份修复，保留默认缓存目录和官方serve参数。135749完成49项组件门但checker误拒<think>格式，原失败保留；141536复用组件证据、4个语义请求全对（含4908token），同AOT与34层native图重启成功。原首启图证据由重启前首次补存，不能伪称首轮已归档。两轮均非官方准确率或吞吐，不继承前序PR24完整准确率。

相关代码：[failure.txt](../../experiments/framework/20261024T135749Z-pr25-cache-first-restart/failure.txt)；[gate-auto.json](../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/gate-auto.json)；[cached-dispatch.json](../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/cached-dispatch.json)；[archive-receipt.json](../../experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/archive-receipt.json)；[result.json](../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/result.json)；[audit.json](../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/prior-audit/audit.json)；[requests.json](../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/requests.json)；[graph-evidence.json](../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/graph-evidence.json)；[archive-receipt.json](../../experiments/framework/20261024T141536Z-pr25-cache-restart-recheck-control/archive-receipt.json)。

相关方法PR：[native编译缓存身份 #35](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/35)。

下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。

## 天数 BI-V150

- [20261024T135749Z-pr25-cache-first-restart](../runs/bi-v150/20261024T135749Z-pr25-cache-first-restart.md)（登记#217）：49项组件通过；首启答案85被checker的think格式解析误拒，原失败保留，不记模型算术失败。 **是否保留：** 保留49组件通过及checker失败原件；首启图为后续首次补存，不将本轮流程改判成功。
- [20261024T141536Z-pr25-cache-restart-recheck](../runs/bi-v150/20261024T141536Z-pr25-cache-restart-recheck.md)（登记#218）：默认缓存重启4/4语义正确（含4908token），同AOT与34层native图；仅服务验证，非官方准确率或性能。 **是否保留：** 保留缓存修复和重启语义通过证据；组件未重测，源码新版本的官方性能与完整准确率另验。
