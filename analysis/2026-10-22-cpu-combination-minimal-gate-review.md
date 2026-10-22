# 两个 CPU 方法的组合：复用旧门，补最短缺口

本次只读审阅后，由 root 明确追加授权实施一个正确性门；没有 SSH/GPU、新 web 研究、代码仓改动或重复单方法套件。范围限天数 BI-V150，组合 runner SHA 为 `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`；不能把文本合并通过当作设备或准确率通过。

## 现有两门实际覆盖什么

| 既有门 | 可直接复用的实质 | 对组合仍缺的部分 |
| --- | --- | --- |
| [validate_cpu_metadata.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_cpu_metadata.py:64>)，SHA `b1240720b588dae25d92cc1c173d64c1ea5f6e34fcdcab5dd0156407ebbcb757` | AST 提取真实 `_prepare_inputs`、`_prepare_input_ids`、CPU 映射及原事件 CM；实际 CpuGpuBuffer/BlockTable。五种形状、11 项比较；逆序 prev 映射能走原 async gather/scatter；四轮重复 event/graph consumer 已有 | 候选锁单 metadata 的50493，不是6f组合；没有绑定融合 token helper。fixture缺 `model.is_encoder_decoder=False`，直接套组合会触及 async guard 缺字段。graph只消费positions/seq/slots，没有input_ids；只看metadata总计数不能证明两个方法同次命中 |
| [validate_async_token_update.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_async_token_update.py:72>)，SHA `607cd994db8e5c1d913907ac56cb316c26027dc9d011a71dcc66ddd051a8a9e0` | 真实 `_prepare_input_ids` 单方法；12类映射、删除/重排、新请求空洞、stride、回退和显式跨流等待；整storage及实际selected计数。还有动态N缓存观察 | Buffer/runner为独立stub，未运行整个 `_prepare_inputs` 或metadata helper，没有原prepare事件连续复用和graph消费。不能将其12类结果拼成组合证明；本轮不重复这12类 |

两门都不是实际 scheduler/InputBatch swap/condense 生命周期。其请求重排证据是给定 reqID→旧行映射后执行真实方法，不等于完整服务里的请求增删、异步输出队列或采样已经联测。旧 async 门的446f源与后续e155适配之间已有单方法静态同一证明；这也不能代替组合执行。

## 源码交叉关系

组合 [实际 runner](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py:1775>) 保留原事件作用域。`_prepare_inputs` 调用真实 `_prepare_input_ids`，其融合分支先用原两次索引 H2D，再发整数 kernel；后面 metadata helper 将已有 CPU positions/seq 写回原 GPU 地址。async helper 读的是 CPU `prev_positions.np`/cumsum 和局部上传的索引，**不读 metadata 方法省掉上传的 req/query/scheduled GPU scratch**。目前未见这两处存在互相缺输入的静态冲突。

但选中计数只证明 host 提交了候选，不代表设备完成；还须原 event、graph 消费及字节比较。不能删除原同步、改 helper guard 或伪造 platform vendor 来制造命中。

## 最短实现与判定

root已选择只从 b124 小fork [validate_cpu_combination.py](<C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化/scripts/remote/validate_cpu_combination.py>)，SHA **abfc7981a8d5a20ff32b80f42dd30148bbeb5d680c649bf892e2b3924ead0bad**：

- 固定原e155、组合6f、metadata `0e961524…`、async `1bb85e31…`及原三依赖完整SHA。controller直接归档原字节，不再调用单方法transformer，原helper/runner文件不改。
- 仅补合法fixture字段和两个实际helper namespace。五case不变、11个原比较保留；记录每次before/after/delta，decode62/mixed952强制同一次metadata=1、async=1；no-previous轮async必须0，不强迫所有形状命中。
- 原四轮event复用/graph阶段只加第四个consumer `input_ids`；每轮同次双delta1，四项GPU指针固定；原/组合逐轮输出相同，positions与input_ids都必须跨轮更新。四轮之间没有整卡同步，只在最终比较前drain，保持CM内改host状态的原顺序。
- 删去所有timing与32call循环。RNG从正确性流程前后比较并保存hash；不以单方法性能相加预测组合性能。原spec scope负例只检查metadata不提交，未扩新回退套件。
- 原controller独占锁/idle/child/monitor/timeout/进程组清理保留；systems薄层仅做资产pin、DB前后和封存，不再取得第二把设备锁。

必要CPU compile、`--help`、导入不加载Torch/Triton均过；AST核仅make_runner/worker/main改变，五case常量与原门相同。framework全文delta审无当前正确性门阻断。本报告时尚未上卡，**没有组合pass、吞吐或整模型准确率结论**。

后继仅一次上述最短设备门：任一原11项失败、应命中却未同次双命中、图读到旧input_ids、RNG变化或source身份不符就保存失败并停止，不先扩12类/服务/长pair。该门若通过，只补齐提取方法链与事件/图消费风险；完整执行循环、真实请求生命周期和组合收益仍另论。

## 后续实际回执：062205

root已回执唯一组合门exit0：五case字段、四graph步骤每次双delta1、四consumer及RNG检查通过，累计metadata9/async7。前面“尚未上卡”描述的是准备时状态；当前实际结果已取得，完整原件由systems唯一验收，本owner不重复validator或设备。

实际 `prefill2048` 的async delta为1，不是identity slice：该fixture的旧sample行0需写到2048-token块的末位置2047，原方法的common_indices_match条件不成立。两个no-previous case为async0；decode62/mixed952/prefill2048共3次，再加四graph步，合计7。此前不强制prefill命中只是设计门槛，不能写成实测可能为0。此结果仍是提取真实方法与fixture的组合正确性，不是服务性能或全模型准确率。
