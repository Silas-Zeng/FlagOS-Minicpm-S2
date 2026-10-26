# 当前实验状态

2026-10-26 16:44 UTC（北京时间10月27日00:44）。BI-V150由本方管理，C500由队友独立管理。本批339条登记／336个唯一run。

**SSH已恢复，正在补16K官方四轮。** 原main594控制组154111的4K四轮全部成功（1024请求），4909.31／5843.85／5767.56／5931.59 tok/s，弃首均值5847.6667；首轮16K中断、原因未确认，无完整16K成绩。原PID退出，原始日志与state保留，初始DB207f已恢复。执行路径读取器的CacheCompiledArtifact格式缺项已只读补证，不重测4K。[方法、四轮和恢复证据](team/methods/shape-gemm.md)。

唯一GPU任务：`20261026T164443Z-main594-control-16k-four-rounds`，owner314／driver317；远端 `/workspace/experiments/minicpm-s2/official/20261026T164443Z-main594-control-16k-four-rounds`，相邻`-control/state.json`，run内`server.log`、`benchmark.log`。完整main594/tree5a406f3，native14f/DB207f；仅用官方--test-cases选择16K，服务/benchmark内容和四轮弃首均值不变。不要重复启动。

M64固定寻址组件8类检查/RNG通过，单组完整MM省1.47792%，无额外权重；生产三文件候选已准备、上传但未启动。[差分与已测范围](analysis/m64-fixed-address-production-20261026/README.md)。候选4K/16K分别新服务匹配控制；尚无候选官方、105或代码合并，不认定新基线。

团队main594／PR59的队友native5cbb单评分与本方native14f四轮口径分开。旧main6971完整5656.77／4119.24、103/105为历史参考。历史负结果和组件局限保留，不为上传重复测试。

[实验总表](team/experiments.md)／[方法导航](team/README.md)。原始证据从方法记录链接；AI接续与后台入口只在本页维护。
