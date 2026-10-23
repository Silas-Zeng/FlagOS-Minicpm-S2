# FULL 恢复的正等差目的页搬运：本轮结论

2026-10-22 22:46 UTC：独立单层 H2D（222047）与真实42层 FULL VERIFY1（222222）均通过。VERIFY0 服务配对（223056→223540）双方32成功0失败，耗时168.266376→168.202863秒，但KV容量521840→521936不一致，`gain=null`，不能据此认定性能收益。DB544四端、原参数、完整来源、真实恢复消费及清理等其余30项通过。代码与证据保留为候选，暂不默认集成或追加大测。分析见 `analysis/q-gqa-kv-restore-pitched-verify0-pair.json`。

下文为实现前保存的设计与验证计划，其中“未运行”描述历史准备状态；当前状态以上述实测结论为准。

# 后继独立候选：FULL 恢复的正等差目的页搬运

已按 root 授权形成独立 CPU 实现和纯整数几何检查；尚未编译 SDK、接入 worker、运行设备门或测量收益。**不得叠入第一轮仅重定两处 runner 身份的 QGQA+旧 pitched-SAVE/FULL 组合**，该轮仍使用原 RESTORE_FULL。

原件：`experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/server.log:215`，SHA256 `58cf312b903604c8c6200fb41d44b34c3175a8988d2b4271201047b9cf50fa50`。定位为 `BIV150_KV_PROTOCOL` 的 `event=RPC_ACK`、`command.kind=RESTORE_FULL`、`operation_serial=2`、Engine/worker PID262318；只取 `command.pages`，不将 SAVE 源数组混为目的数组。该数组按 `json.dumps(pages,separators=(',',':')).encode()` 的 SHA256 为 `96df643679671a337327a223fda9a0bb58104d72958a93998ce194a04dffa227`。

实录 R16688、1043页、717717504B，42层每页16384B，旧 ACK 为2772次 copy。原目的页序已严格升序且唯一；本离线计算**不再次排序、不更换任何页、不改原逻辑页映射**。保留原三个长连续段，只在 singleton 区按818e规则由左至右取最长正恒差，精确展开与原数组逐项相同：

| 逻辑起点 | 物理起页 | 页数/height | 物理步长 |
|---:|---:|---:|---:|
| 0 | 232 | 796 | 1 |
| 796 | 3076 | 2 | 2049 |
| 798 | 7173 | 3 | 2049 |
| 801 | 13319 | 2 | 2049 |
| 803 | 17416 | 3 | 2049 |
| 806 | 23562 | 3 | 2049 |
| 809 | 29708 | 1 | 1 |
| 810 | 30959 | 37 | 1 |
| 847 | 31000 | 147 | 1 |
| 994 | 31176 | 20 | 30 |
| 1014 | 31757 | 2 | 20 |
| 1016 | 31807 | 3 | 30 |
| 1019 | 31908 | 4 | 30 |
| 1023 | 32018 | 20 | 31 |

原66连续段可成为14段：4线性（796/37/147页与1单页）、10二维；理论42层提交2772→588，其中168线性、420二维，减少2184次。字节不变，最大目的 pitch 为2049×16384=`33570816B`。旧单层实际设备 maxpitch 报值2147483647B只是已有能力证据，新方向仍须真实查询/验证。**调用数下降不等于搬运耗时或 swap 端到端收益；不从旧单层时延线性外推。**

最小后继接口建议：独立 `prepare_restore(hosts, gpu_raw, plan, max_pitch=...)`，保所有 host/storage/view/offset/上下界及42层无 alias 检查、强引用；以逻辑页号定位连续 pinned host 源，以原物理页号定位 GPU 目的。连续段仍线性 memcpy；正等差段为 `width=16384,height=页数,spitch=16384,dpitch=物理步长×16384`。只写 selected rows，目的间隙、其他请求页与 padding 必须保持，不能拿大矩形线性覆盖 gap。

旧 `patches/framework/candidates/biv150_kv_pitched_copy.py`（818e788b…）的 `prepare_save` 只接受 CUDA 源与 pinned CPU 目的；旧 `biv150_kv_pitched_bridge.cpp`（0a4d44d8…）86–89行硬编码 SDK `cudaMemcpyDeviceToHost`。descriptor.kind=1/2是线性/二维而非方向，**不能交换指针复用旧.so冒称支持H2D**。若后续批准，应新 SDK H2D 入口/独立资产并保留旧 D2H 路径，不改已测文件。

FULL 原私有 fresh/ref1/unhashed/完整覆盖、页表绑定和已知 token 状态契约不变；所有 descriptor 在首提交前验完。真实 current stream 上完成事件后才允许发布，持有 host/destination/descriptor 至 settle；异步部分提交失败不得重试旧路、提前 DROP 或复用内存。独立单层正确性入口已按下节准备，但尚未执行。是否进一步接当前 QGQA，须由 root 在首个原 FULL 组合结果之后另行决定。

## 独立实现与最小接入边界

- `biv150_kv_pitched_restore.py` SHA256 `a7439c2c0b2b588dcd2af5c66b6eb62e562132ef8b5bc1d54ce54fc4b6e9804c`。纯 stdlib 导入；显式接收已经加载的原 `save_runtime` 模块并锁818e源码。`make_restore_plan(pages, pool, save_runtime=runtime)` 复用原 planner；`prepare_restore(hosts, gpu_raw, plan, max_pitch=...)` 先验完整1层或42层 raw/storage/pinned/offset/无跨层alias/1GiB上界。它只证明存储及几何，不替代 FULL 私有页和完整覆盖资格。
- `biv150_kv_pitched_restore_bridge.cpp` SHA256 `48295ffde897cce988d3a8460904ab4451669e1de2fbe2bd5257d3f75e35ab20`。旧0a4d整个文件逐字节保为前缀；只追加 `biv150_pitched_restore_batch`，沿旧 descriptor/全batch校验/实际device和maxpitch检查，将 SDK 调用方向固定为 `cudaMemcpyHostToDevice`。没有新 `.so`；旧9e33桥不含此符号，不可复用冒称已支持。
- `RestoreBridge(new_so, expected_sha256=..., save_runtime=runtime)` 显式构造时才载库，复用原 ABI/最大pitch查询，`submit(prepared, stream_handle=int(current_stream.cuda_stream))` 返回 `completion_ack=False`。任何 API/计数异常均抛 `RestoreSubmissionError`，记录已提交次数；无原路重试。调用者还须锁实际加载的 cudart 身份。

后继 worker 仅在原 `RESTORE_FULL` 分支的 `_full_restore_plan` 成功、目的页已绑定和原 producer fence之后，用此 prepare/submit 替换 `info = _copy(... host→raw ...)`；旧 RESTORE、D2H SAVE、事务 serial/phase、`_finish` 真事件、42层 c95f 回读和失败 settle 均保留。首提交前将新 bridge、plan、prepared 和实际 stream 存进原 slot，失败未 settle 时不得移除强引用；成功 ACK 仍只能由原 `_finish` 之后产生。**当前没有修改任何已部署 worker/protocol/transaction/服务launcher，也没有安装默认启用。** 当前 FULL reader假设连续段 copy_calls，若后继接入必须另行适配动态恢复几何，不能沿现有验收假称已覆盖。

`check_geometry.py` 已仅执行一次，结果保 `cpu-geometry-check.json`：实际原ACK行215/页面SHA核对、完整页序与逻辑页展开、14段=4线性+10二维、最大pitch33570816B、低pitch16384时66线性/10个段预拆；不排序下降页序，重复/越界仍拒绝。导入期间显式禁止 CDLL，并确认没有导入 Torch；旧 D2H 前缀及新增 H2D 函数相对方向替换精确校验。**未构造 Tensor/PreparedRestore/Bridge，未编译或执行 SDK，因此此回执不证明 pinned/DMA/事件或异步错误处理的设备正确性，更不证明时延收益。**

## 待 root 调度的单层设备正确性门

`validate_kv_pitched_restore.py` SHA256 `10e5ec18ea1a1ddc125362a9bf21063f59c6a196214a0873a455c1c8ed3d6df9`：仅上述一组真实目的数组和一层 normal raw；host/GPU backing 内部 view 均非零一页 offset。先新 H2D→同非0流 GPU selected-row consumer→compact D2H→真事件，立刻核 selected 全字节/guard；过后才读完整 pool（含所有非目标 gap/双 guard）核 CPU oracle，再做独立 c95f H2D 参考。源 host 全字节/双 guard 及 RNG 均须不变，不调用旧 SAVE/D2H 提交或任何计时矩阵。所有 native 异常包括 submitted=0 均须实际 device settle；未成功 settle 保全部引用至 owner 清理，禁止旧路重试。它不替代42层 FULL 事务或准确率门。

`launch_kv_pitched_restore_gate.py` SHA256 `ed7331a693719a5db950527812eac3072432d8bc4e6db2da1cd32fcbed6f4862`：原3ffe控制器最小fork，仅SOURCES/名称/说明变，原flock、双idle、ABI/SDK/cudart身份锁、g++、唯一child300秒、monitor、cleanup、DB和seal保持。8个输入均在固定隔离目录 `/workspace/experiments/minicpm-s2/scripts/kv-pitched-restore-gate/`；controller无参运行，归档仍为 `RUN/source`，child CLI仍 `--device-worker --output-dir RUN --source-dir RUN/source --bridge-sha256 <实际SO_SHA>`。HELPERS继续使用原ROOT/scripts，不能同已运行的准确率或其它设备任务并发。

上传映射和CPU静态回执见 `gate-static-check.json`（SHA256 `86e8469b97a102e2afdcd0d481fa2cc9fcaa938c04f085bf14456c08af7ce42d`）。仅syntax、纯stdlib定义导入/CLI help、8素材SHA、controller逆回与原owner函数字节相同；没有运行Tensor mock、SDK编译或设备。首次controller生成的本地字符串换行定位失败在写文件前退出，按原文件实际LF修正生成后才落此稿，不涉及实验或旧文件变化。team已对10e5/ed733新增风险只读互审无阻断；root仍是唯一部署/设备owner，当前只是可执行队列，尚无设备PASS或性能结论。
