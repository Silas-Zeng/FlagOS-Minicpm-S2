# 完整R等差SAVE：独立worker最小实现

2026-10-22，仅天数BI-V150。本owner只CPU实现/审阅，root独占设备。root报告035754唯一三路门字节/guard/stream/RNG通过、逐窗无节流后授权此实现；三路原件验收和计时归systems/hardware，本owner不重复执行或重算其结论。本候选尚未执行真实42层或服务，不能从一层三路门外推E2E收益。

## 文件与唯一改动

新 `patches/framework/candidates/biv150_kv_pitched_save_worker.py` 最终SHA：

`a662e478d20884c5b1d65e0ee3d270a62453d88166b28e092dcaf3b35a3df854`

从原FULL worker **5d9a082fa8a41d5f3b549bf3a2caf02a646da34095cc2b892a1df902946a4477** 显式复制，仅修改原 `rpc` 的SAVE调用和增加3个独立helper。原9个函数（包括 `_context/_finish/_copy/_full_restore_plan/_reply`）逐段不变；删除新helper/新pin并逆换SAVE调用、模块说明后逐字节回原5d9a。协议 **1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8**、事务 **84be2242656e6ae0a30d65c803c2ae5076e836e0d1b6686731c4197a85b21883**、原runtime818e/cpp0a4d/SO9e33均未改，不叠72942进展victim或其它策略。

SAVE仍先核runner真实prefix映射，原budget/42个pinned host/单层verify_buffer/headroom、producer全device fence均保留。仅原 `_copy(policy,raw,host,pages,range(count))` 改为 `_save_pitched(...)`；随后原 `_finish` 真Event完成，然后VERIFY1可核源字节，全部成功才SAVED/caps/成功ACK。旧FULL/RESTORE/回读仍调用原c95f `_copy`，没有省掉恢复或原围栏。

## 晚加载与强引用

`_pitched_assets` 仅在真实SAVE的helper内调用，模块导入/general注册/初始化/profile均不调用它。固定相邻py818e、regular SO9e33、模块实际文件路径和进程唯一已加载libcudart d39d57指纹。root发现/proc maps同一库有多个段后要求先按resolved path去重再各hash一次；最终仅这一块变化，保相同guard并减少首次SAVE重复读取8.39MB库的开销。加载/校验/plan/descriptor成本仍属于首次候选SAVE，没有额外预热请求。

原slot在首次可能提交前强持 `save_bridge/save_runtime/save_prepared/save_plan/save_stream`；PreparedSave再持全部42个raw/host和ctypes数组。提交取实际 `torch.cuda.current_stream(0).cuda_stream`，包括合法default handle0原样传入，不切换stream；原 `_finish` 在同一当前流record/synchronize，单层旧门只测非0流，实际服务handle/42字节仍须真门证明。

API部分提交/0成功返回后报错都沿原except真实device settle，失败强引用不随helper栈退出释放，不静默重试旧路；未settled不能DROP/发布/释放页。PreparedSave保到slot实际DROP，数据不复制或额外放大。提交返回仅提交统计，字段改名为 `save_submission_completion_ack=False`，不能混为worker已经completed；成功worker ACK仍只在原Event和诊断后产生。

## VERIFY1补齐SAVE本身的字节证据

原FULL回读只能证明“保存的host→恢复GPU目标”，无法独立检查新SAVE是否读对原42层。新 `_verify_saved_source` 在SAVE真完成且原源尚未free时，用**原已预算的单层verify_buffer**，逐层以冻结c95f按原pages回读source，每次原Event完成再CPU `torch.equal` 对该层新host；42层都过才允许SAVED。每次回读前slot置未settled，错误仍原except处理。没有新增0.7GiB影子host或GPU packing buffer。

SAVE验证结束仍保该buffer供原FULL诊断回读，原 `_VERIFIED_ONCE` 只由旧RESTORE成功路径推进；VERIFY0不新增源回读。没有改变R/原逻辑页序/所有权/协议、调度或随机采样代码；新实现是否影响完整准确率仍须后继相应门，不继承旧FULL资格。

SAVE ACK新增实际字段：

- `save_implementation="C_batch_positive_stride_full_R"`、`save_layers=42`、`save_segments_per_layer`。
- `save_runtime_sha256`、`save_bridge_sha256`、`save_max_pitch_bytes`、`save_current_stream_handle`。
- 原`submitted_bytes/copy_calls`及`linear_calls/pitched_calls/fallback_pitched_segments/original_c95f_calls`；`save_submission_completion_ack=False`。
- VERIFY1：`save_verification_performed/passed=True`、`save_verification_layers=42`、`save_verification_bytes=nbytes`、`save_verification_copy_calls`。后者是源原c95f连续runs×42，不写死旧R或run数。VERIFY0仅`save_verification_performed=False`。

原caps、worker真实completed/host状态、FULL `verification_*` 字段保持。验收须分别核SAVE源→host和FULL host→目标两组证明，不能用其中一组替另一组。

## 唯一CPU合同与最终小修

唯一 `tests/test_biv150_kv_pitched_save_worker.py` SHA **38de41e794a85d258acc11c113e2f9d7b912197a689694b661634c245f6c4997**，首次实际执行：

```text
python -X utf8 -m unittest discover -s tests -p test_biv150_kv_pitched_save_worker.py -v
1 test / 0.122s / exit0
```

测试时worker为首稿 **4f1dd74c9dd6c4b558a5a0c3749b569c31cea5a8794e394f25ab3de7a997c77e**，其完整字节另存 `source/kv-pitched-copy/biv150_kv_pitched_save_worker.4f1dd74c.py`。合同走实际rpc/helper控制流，stub验证VERIFY1原buffer42次核验和保留、VERIFY0无回读、currentstream/首次submit前引用、partial已settle/未settle保持slot与拒DROP、源比较失败不ACK/不重试、settled后DROP、逆换精确回5d9a。**Tensor/loader/SDK/event/实际字节是CPU替身，不能当真实GPU证明。**

原CPU记录 `source/kv-pitched-copy/worker-cpu-check.json` **9df0b498d9ed218ad56f799e3fc6d1117a6afd0d4feccc0611c294dafa0b7823** 保留实际测试源身份。随后root仅要求/proc maps去重，完成单块逆换精确回4f1和compile，不重跑合同/旧suite；最终记录 `source/kv-pitched-copy/worker-final-check.json` **43968a8827fb8a6abc370ad75d5dea15b1c560a3e8ef02cbe3eb0764b6c2ea8b**。不存在失败重跑、SDK编译或设备执行。

## 精确部署字段与下一唯一门

systems负责独立包装；本owner不改其文件。输入固定原FULL416树，映射新worker到canonical `vllm_fl/patches/biv150_kv_worker.py`，同时必须放入以下普通相邻文件：

| 文件 | SHA256 |
|---|---|
| biv150_kv_pitched_copy.py | 818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd |
| biv150_kv_pitched_bridge.so | 9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0 |
| biv150_kv_pitched_bridge.cpp（仅归档） | 0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44 |

SO实际实体取自已验032653编译物并核hash；不能让运行worker编译、任意换SO或只依赖远端scripts。原innovation作为输入基点原样保留，新增独立manifest完整锁新差异；基点416只替一个worker，新增py/cpp/SO/manifest预计420，实际数由builder核，不把预计当实际。init791c/协议1aff/txn84be/e155/c95f保持，不叠6a/c6/72942。

hardware与root已终审a662最终去重delta，无本轮唯一真实VERIFY1门阻断，systems已获正式锁pin通知；代码不再因文字变化。下一由root唯一执行原bc51/context-long/seed721201/原SERVER/VERIFY1诊断，合并真实42层SAVE对照、FULL42回读、原runner六checks/原consumer、32-0/真实DB与KV/全部source后态。该门不能作性能比较；本owner未SSH/GPU、未改共享代码仓或默认候选。用户最新明确确定收益可不做大测试：完成必要42层正确性后不自动开展大官方或重复长pair，后续由root依最短可比证据决定并准确保留scope；失败保原件，不扩大形状或预先增加扫描。
