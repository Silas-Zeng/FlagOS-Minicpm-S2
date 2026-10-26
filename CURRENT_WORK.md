# 当前实验与接续

更新：2026-10-26 18:48 UTC。团队框架已合并 [PR47](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/47)，固定 main 为 [2412207](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/tree/241220723a09061c182764f8f738e5ec01190367)，765文件/tree4e068333690d1712134801f6522962755804b3b9。默认Q32/w16作为后续研究基础。

## 当前唯一设备任务

BI-V150 原官方16K四轮控制于18:41 UTC启动，run为 `/workspace/experiments/minicpm-s2/official/20261026T184110Z-main241-control-16k-four-rounds`，相邻 `-control/state.json`。owner18174、driver18177、server18191于18:42实查仍在，入口GPU/9031空闲、无错误。

入口与日志在 `scripts/main241-control-16k-500a7230/`。维持原官方服务/benchmark、本站native14f、初始DB207f，四轮弃首。约19:18–19:22 UTC看完整结果；不频繁查询，不重复启动。当前仍未取得本站新main四轮或105结果，原main594的4K冷暖两轮复查已排在本轮成功清理之后。

## 本批结论

本批新增3轮、427份原件，累计**346条登记／343个唯一run**。

| 方法 | 结果 | 决定 |
|---|---|---|
| 旧main594 Q16＋panel4 | 完整组件8.304069→8.119503ms，省2.2226%，数值门通过 | 保留历史证据；不能覆盖新Q32 |
| main594 M32固定寻址 | 16K首暖4184.26对4194.03低0.23295%，两轮256请求全部成功 | 按约定停止，无完整四轮/4K/105或合并资格 |
| 新main241 Q32＋panel4 | 完整组件6.559704→7.375296ms，慢12.43337%，数值门通过 | 停止生产接入，不扫参数；旧Q16边界未运行且不再排队 |

M32的SIGTERM由性能监督器发起，不是框架数值错误。三轮源码/native/DB及设备清理均通过。小差异不写成稳定效果；原件和当时结论完整保留，方法页更新当前决定。

原件：[Q16组件](experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/archive-receipt.json) · [M32官方](experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds/archive-receipt.json) · [Q32组件](experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/archive-receipt.json)。

队友PR47的单对16K +7.2015%、103/105使用native5cbb及其预热口径，独立保留，不冒充本站native14f四轮成绩。历史main594控制4K暖均5847.6667、16K4192.49也不拼成main241结果。

## 下一步

先回收当前main241控制并执行原main594的4K冷暖两轮复查。CPU并行准备一次原accuracy题目输入的真实KV位分布采样，判断逐位无损压缩是否值得写算子；尚无真实样本、压缩收益或GPU诊断资格，不能把合成随机数据当生产分布。

入口：[实验总表](team/experiments.md) · [GEMM方法](team/methods/shape-gemm.md) · [prefill分段方法](team/methods/prefill-panel4.md)。AI详细接续及子智能体产物保留在本地CURRENT_WORK与Git历史，团队阅读以上短表和证据即可。

## 4K 环境复查（19:00 UTC 接续）

新增环境限制：旧4K控制15:41早于当前PID1约16:11:13 UTC起点，M64于17:25在其后；相同6核配额但cgroup计数重置，跨容器/进程环境，不能把−1.70966%单独归因于候选。原main594重启后4K冷暖两轮已排在main241 16K清理之后，尚无新结果。

串行入口 `/workspace/experiments/minicpm-s2/scripts/main594-postrestart-4k-6f2c5274/`；等待器 PID **25181**，`queue-state.json` / `queue.log` / `launch.log`。每60秒只读前项终态，成功且DB/设备清理后才启动一组两轮；前项失败则不启动。源码/native/DB与旧4K固定相同，原benchmark不改，两次原run_once，无四轮summary。比较旧冷4909.31与首暖5843.85，不把单暖当稳定均值。
