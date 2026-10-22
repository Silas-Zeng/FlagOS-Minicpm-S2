# 三路拷贝门：唯一下一短验证的准备与审阅

本owner独占此文档及 `scripts/remote/validate_kv_pitched_threeway.py`。从干净2746e01b接续；032653实际门已通过的事实见独占 `2026-10-22-kv-pitched-copy-032653-hardware.md`。本轮目前仅本地准备与交叉审，未运行设备。原c8c0门、818e runtime、0a4d C++桥及全部旧原件保持不变。

## 唯一变化及解释

新脚本从c8c0字节复制，仅新增C-linear控制和每窗CPU观测，首case计时改64call固定镜像次序。CLI、source资产名及results／failed独占写入保持原样；外层只需小fork并改gate输入／pin及run suffix，不重新搭控制器。

| 路径 | 实际提交方式 | 015315／021658每层提交 | 解释 |
| --- | --- | --- | --- |
| A | 冻结c95f的Torch `copy_` | 37／26方法调用 | 原实现 |
| B | 同818e／0a4d桥，`prepare_save(max_pitch=PAGE)` | 37／26原生线性API、0二维 | 提交前受控展开，不是设备pitch不足 |
| C | 同桥，真实查询max pitch | 若仍支持33570816B，则11／6原生API | 2线性＋9／4二维；不假设设备能力 |

B不改变R、源页顺序、目的逻辑、bytes、stream或SDK；没有新kernel、GPU packing或worker。仍是同两个冻结实际SAVE数组，source pool32578／32572，单层bytes17334272／17170432。仅给B新增独立pinned host、双guard及PreparedSave；首次任何异步copy前将它们写入fixture强引用。CPU oracle／c95f全字节、source与host双端basic guard、计数均需通过；C仍紧随原非0流producer并先比CPU oracle，避免后续路径掩盖流错误。原失败settle、不settle保引用、无旧路重试边界沿用。

新增B的约34.5MB目的buffer只用于两case门，不是服务host预算变化。只有全部正确性通过才计首case；结束后仍三路payload、guard、整源回读及CPU/GPU RNG核验。单层门不证明42层batch／worker ACK、accuracy或服务收益。

## 固定计时与CPU证据

唯一顺序为 **A／B／C／C／B／A，每窗64call**，没有扫描、sleep或自动repeat。event创建／首record、三路submit预热、分配、准备、pattern和CPU整池比较均在计时前；六窗之间只作小量统计，不做CPU整池比较／填值。wall包含真实submit检查、SDK查询及同流event完成；双方plan和B／C descriptor准备耗时另列。

每窗前后读取实际v1路径：`/sys/fs/cgroup/cpu/cpu.stat`、`cpu.cfs_quota_us`、`cpu.cfs_period_us`，保存原文本、解析计数及delta。读取均在wall／event窗外，覆盖窗及小量前后采样边界；不能定位某一次API或把累计`throttled_time` ns当精确wall损失。进程CPU时间另用`process_time_ns`记录，也不是wall或仅主线程执行时间。

保持已观测56个Torch CPU线程与600000／100000us额度，只检查、不设置；不改官方参数、进程亲和性或资源限制。若线程／额度不同、统计缺失或计数重置，明确拒绝当前不可比观测，不偷偷适配。存在节流／wall仍波动时保留原值和不确定结论，不追样本。六窗完成即收口，正负均保留。

A／B只区分Torch方法与C batch传输路径的组合，不能声称只省某一个Python操作；B／C比较同桥线性拆段与2D合并相关变化，不直接解释为DMA机制或设备带宽。准备和加载成本仍不是免费；本轮不改变真实服务代码。

## 当前固定资产与审阅状态

- 新gate：`9b16aec69ecc6e2bf59de7fd0f323ae543a1a32eda15486aa294e2f49c645dd9`。
- runtime：`818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd`。
- C++：`0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44`。
- baseline：`c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c`。
- 外层小fork：`launch_kv_pitched_threeway_gate.py`，`b2c65963f621f83b0d093353e7135b3434d4c49bb9402c05bb2a3363aa6f5a88`；仅gate输入／pin及两处run suffix变化，逆换后逐byte等于旧3ffe。

必要CPU检查仅源码compile、runpy导入不加载Torch和`--help`成功；未运行新旧suite、planner合同、SDK编译、CDLL或设备。framework已对c8c0→9b16完整delta只读终审，无当前短门阻断；systems也只读了CLI／生命周期增量。原实际SDK／maps库SHA／storageoffset／非0 native stream／真实事件、外层唯一锁和清理机制继续使用上一门已审边界。

本owner静态核现有函数AST仅correctness_case、timing、device_worker发生计划内变化，新函数仅cpu_snapshot；其它原函数一致。外层最终pin已实核并回root无阻断。专项准备记录 `source/kv-pitched-copy/threeway-hardware-preparation.json`；运行四件资产冻结，不为文字报告改代码。B报告内fallback_pitched_segments为9／4是显式控制展开；C是否真实fallback按设备maxpitch判，二者不能混用。

启动仍为外层归档后：

```text
python RUN/source/gate.py --device-worker --output-dir RUN --source-dir RUN/source --bridge-sha256 <actual .so SHA>
```

只有root唯一设备owner可执行。实际三路结果目前尚无。若值得继续，下一步已选一次原long／VERIFY1真实42层事务：SAVE完成且源free前复用单层verify_buffer按c95f逐层读真源核新host，42层全过才SAVED，再原FULL回读和consumer；不另造22GiB合成fixture。目前尚无对应新worker或服务部署。
