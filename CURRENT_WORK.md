# 当前实验与接续

更新：2026-10-27 02:11 UTC。本地353条登记／350个唯一run，原件已回收，正在批量发布本组结果。

| 方法 | 已得结果 | 是否保留 |
|---|---|---|
| main241/native14f 原官方4K | 四轮5632.05／5833.56／6000.87／5715.73，暖均5850.05 tok/s；相对旧main594观察+0.0408%，KV548432→548288 | 保留控制，基本持平 |
| main241/native14f 原官方16K | 四轮3791.43／4489.43／4487.31／4485.73，暖均4487.49 tok/s；相对旧main594观察+7.0364%，KV548288→548432 | 保留控制，非严格等KV单项因果 |
| main594重启后4K诊断 | 冷轮+14.32%、首暖−2.0098%；频率一致，KV少48tokens | 保留诊断，不能证明容器导致持续退化 |
| 真实KV位样本 | 42层各128tokens，5.25MiB，writer/cache逐位一致；原题prompt256tokens | 保留样本，不能当16K性能成绩 |
| SiLU精确查表 | 完整gate慢10.3747%，有限域/Graph/独立INT64等通过 | 停止 |
| 无损KV页内SoA | 首包编译类型失败；v2组件正确性通过，完整链路慢355.5121% | 停止，不进生产 |

**当前唯一GPU任务**：main241/native14f原官方105题，owner34568，02:10:15 UTC启动。入口`/workspace/experiments/minicpm-s2/scripts/main241-accuracy-20261027/launch.log`；先查日志给出的真实run及同名`-control/state.json`，避免重复。765文件、native14f、DB207f及原评测/服务参数固定。结束后回收预测和报告，按既有105审阅判定；目前准确率尚无结论，请求SUCCESS不能代替。

[实验总表](team/experiments.md) · [基线与环境](team/methods/baseline-environment.md) · [KV方法及原件](team/methods/kv-lossless.md) · [SiLU方法及原件](team/methods/native-silu-lut.md)。旧Q16局部正不继承新Q32；新Q32+panel4、M32固定寻址均已有负结果，不重复。

用户禁止网页UI操作。SSH公钥认证与Git只读连接已恢复；本批经PR批量推送，原始测量未改写，源码优化另按方法PR维护。
