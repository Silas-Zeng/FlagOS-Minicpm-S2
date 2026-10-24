# 原四题事件驱动覆盖诊断

本目录仅 CPU 准备，不是准确率或性能结果。基于冻结060425计算序423（map `6cf2e1d7`、runner `ea64a59c`），保原P和29b952 outside/原sample证明；新增CPU生命周期观察，不改算子、采样、InputBatch或调度。只用 `files-final/` 与 `files-final-prepare.json`；`files/` 是早期稿，不部署。

生成入口：`python -B prepare_event_gate.py --base <完整冻结423> --output <全新目录> [--emit-only]`。最终425文件、六路径变化：runner短接点、三个显式runner身份锁、原Math4 helper及新events helper。原423逆回/完整map/语法已核；未导入模型、运行设备或新mock。

- observer `7f929c0460a467cae5689be20e7bb8c6cf7f7160a31f35c1223c1944435c0e43`
- builder `4fb62b271bd98d7d9af1034129a33e9f9985189ac420d0d5be0b45e797f42f03`
- runner `7e1104d9604df654033a86504b51eb3ea6d82b4b09e76632a2c7d13311128402`
- receipt `c95d6dde4bad98d2bb8091c59d0d50c728537a51ef2fabc0a32e309c6d41035a`

服务保旧 `BIV150_COMPUTE_ORDER_MATH4_DIR=<control>/math4-artifacts`。新增 `BIV150_COMPUTE_ORDER_MATH4_EVENT_DIR=<control>/events`，须本次独立绝对目录；客户端把完整JSON关闭后原子发布 `background-request-ids.json`，唯一字段为 `engine_input_request_ids`，值为实际前两条背景的两个子请求ID。已核实际582b completion链：原HTTP头h → 顶层 `cmpl-h` → engine输入 `cmpl-h-0` → 最后追加8位十六进制随机串。此配置填 `cmpl-h-0`，不填原头、顶层响应或随机完整EngineID；完整32个payload/身份链由客户端另存，不按输出答案筛选。

observer在原 `_update_states`、`make_plan`之后、原 `_prepare_inputs`之前读原CPU批一次：

1. 两背景本步均q1且computed≥prompt，写 `background-both-q1.json`，供已预热原EvalScope放行四题。
2. 仅A已由finished字段确认并离开原批、当前row0是Math q1、B仍在k>0且当步q1/computed≥prompt、四Math均存活q1且至少一题row>k时，写一次 `release-background-tail.json`，供原其余30请求入队。
3. `observer-events.jsonl`只记首Math出现/首decode q1、背景结束、释放及首尾部prefill/最多8种后续plan状态，含实际完整RID、原row顺序、q、computed、prompt、monotonic及config SHA。可识别的几何拒因明确列出，其余只称actual_plan_none，不猜完整guard原因。

信号JSON完整关闭后rename发布。客户端核两信号同pid/配置SHA；出现 `observer-error.json` 或 `uncovered.json` 即未覆盖，不以超时继续放行。两背景先全退出或Math先结束导致几何丢失，写uncovered；条件从未出现则由客户端有界停止，不调秒数重试。原q1观察是乐观CPU调度状态，不是GPU完成；实际P与原sample返回仍必须取29b952原证据，题号/response→内部RID、token位置与原judge由既有reader后验。

源码依据：de1 InputBatch先填最小removed洞，再将最高活行condense到最小洞；ea64 runner先add再condense。Triton1219继承base c524的reorder阈值None，不会把q1全部重排到前缀。因此本信号限定可形成洞的实际行序，但不保证客户端能在B退出前送达尾请求；未覆盖照实保存。本诊断有CPU扫描/IO，不作性能成绩或全模型精度证明。

team已只读封口最终7f929c/7e1104及六路径，未运行套件/设备；原29b952未重复审测。客户端事件/原payload封包由另一owner单独实现审阅，只有root能启动设备。
