# 计算序方法的最小 Draft PR 迁移方案

只读核对时，私有 framework main 已为 `3283672b92fa30f93f652b242193999836a95f88`（PR16 normalization 合并），并非9a43；PR15仍open Draft、未合并，head638c4ac0。`main-observation.json`保存本次GitHub读取身份；不发布、不创建分支、不导入运行框架。

建议独立方法分支 `codex/compute-order`，不依赖PR15。最小生产范围仅两文件：`vllm_fl/worker/model_runner.py`与新增`vllm_fl/patches/biv150_compute_order.py`。P从CPU计数构建compute序和私有metadata，保原N logits/采样行；PR15只省metadata成功时的冗余computed H2D，既不是P的依赖，也不能将其收益相加。两者重叠`_prepare_inputs`，未来合并须保PR15的pending-copy位于P/CPUmetadata都未采用的原GPU分支、async-spec原路；本Draft不捎带这三处改动或借其100/105作为P资格。

`runner-core-preview.patch`只将冻结ea64的14处生产切口精确应用到当前main runner，尚非可部署PR。当前main runner整blob03d86ca175befbb0d9928f3b0b7fcffa9a4f8197已核（SHA97c78bde），其全部类方法AST等于9a43/旧cc442；preview仅改`_prepare_inputs`、`_build_attention_metadata`、`execute_model`，原`_sample`不变，所有SQL/C2/C3/GQA/normalization footer逐byte保留。撤14处后精确回当前main，compile通过。`static-migration.json`记录preview SHA183de0ab与NOT_DEPLOYABLE，不能拿preview或旧helper直接启动。

明确阻断及所需兼容增量：旧helper5ce6的`EXPECTED_RUNNER`仍ea64，`SOURCES:20`要求自然加载实验Qservice51fc；当前main runner没有安装Qservice，而已在GQA后安装normalization。直接搬helper会scope拒绝。需另做**显式current-main profile**：锁新runner、核当前normalized helper24a421fa/48717c43及真实统一入口绑定，取代旧Q自然加载前提；不能泛化unwrap、仅删来源guard或把Q优化偷带入本方法。当前CPUmetadata/C3/GQA Git blobs仍与9a43相同，已保存读取证据；无须改这些实现或normalization算术。迁移最终PR必须以当时最新main整tree为底，不用旧432/423树覆盖队友文件。

旧423中的KV worker/protocol两处runner SHA重定仅为实验KV闭包，main9a43树无这些文件、当前生产P不需要它们；不提交KV事务、桥、so。也不带Math4/event/shadow/structure、capture/client、owner/launcher或诊断env。保原BI-V150/16SM、BF16 MiniCPM16Q/2KV/128、normal FullAttention、text/noSpec/noMM/noLoRA、FULL_DECODE_ONLY、mixed NONE无padding等边界，未知写前回退、写后错误不重试。C500保原代码/安装footer，不能将metadata helper的通用scope当本P的跨平台验证；平台快速拒绝的新适配仍需窄审。

可引用的历史证据均来自旧Q/GQA/KV423组合，不是本次main迁移成绩：

- 120949→121541：同KV521936、DB561/20721及31门通过，32/0，104.492952367→99.398900815s、total tok/s +5.124857%，单pair；`analysis/compute-order-service-retest-pair.json`。
- 100604：实际N17/M2048/outside14，全M IDs/positions、实际logits indices及原sample一次的结构证明；CPU异步映射合同复用，非数值等价。
- 130351：原固定四题4/4，index0/1/2实际outside且真实token94在首完整boxed闭合前，index3 row0未outside；只小样本新路径质量信号，非105题/实质答案内容全受P影响或全请求覆盖；`analysis/compute-order-math4-event-130351.json`。
- 061500完整101/105为0P fallback兼容；085500单行独立FP32/64定位也不能拼成完整P准确率。

缺项：当前main profile的显式来源/绑定实现与增量互审；不同normalization基础上的真实P命中、必要质量和可比性能验证。没有新的main准确率、官方性能、稳定收益或C500结论。本轮仅小材料/局部diff/compile与AST核对，不重跑旧门或设备；若当前绑定不能严格闭合，保持Draft方案未就绪，先不宽放guard。
