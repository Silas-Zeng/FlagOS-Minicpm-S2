# 032653：实际2D单层字节门通过，计时只保小信号

`20261022T032653Z-kv-pitched-copy-gate` 实际设备子进程258707退出0。root原件包SHA `2ba3856fef63566c8a372818a2ae60e21c999d8022465d8d29ad13a7de99c55c`。本owner直接读结果、真实页数组、环境和计时，只做专项几何重建及算式解释，未重跑systems的完整验收或设备门。

## 真实API、完整字节与几何

实际BI-V150实例16SM／32GiB，桥`.so` SHA `9e33ecbf9cf57f52469db6b1d509a600cd1a8eeafe78a54095e88dc474c71fc0`；子进程maps确认实际Corex libcudart SHA d39d…，并非仅外层ldd。显式非0 native流handle为94118921500112，producer、新桥及完成事件使用该流。实际查询max pitch为2147483647B，两map需要的33570816B在范围内，无fallback。

| 实际输入页序 | 全部页／单层bytes | 原c95f方法调用 | 新实际原生API提交 | 已执行2D |
| --- | --- | ---: | ---: | ---: |
| 015315 | 1058／17334272 | 37 | 11＝2线性＋9二维 | 9 |
| 021658 | 1048／17170432 | 26 | 6＝2线性＋4二维 | 4 |

本owner逐段展开实际结果中的segments，精确还原各自冻结源数组及目的逻辑0…N−1；源pool分别32578／32572。两组case的CPU页号＋word偏移oracle、冻结c95f完整输出、新输出、双端basic guard、整源与双端源guard全部通过，真实source／host storageoffset都是16384B；计时后输出／guard／源检查和CPU/GPU RNG也通过。没有排序、截R、丢KV或重算。

这是单层两种实际页序的设备证明，不等于42层batch、worker完成ACK、服务或accuracy。37／26是旧`copy_`方法次数；11／6是新C桥实际成功提交的API次数，均不等于DMA描述符数量。API内部是否逐行搬运或占SM仍未知。

## 原8call ABBA计时与解释

仅015315的单层payload计时；双方plan和新descriptor准备在窗外，wall包含真实submit的Python/C检查、设备查询、event record及同流完成等待。

| 固定次序 | wall ms／call | 同流event ms／call | wall−event ms／call |
| --- | ---: | ---: | ---: |
| c95f A1 | 7.415286498 | 0.652491808 | 6.762794690 |
| C batch＋2D B1 | 0.672264665 | 0.628266811 | 0.043997854 |
| C batch＋2D B2 | 0.681895239 | 0.628109097 | 0.053786141 |
| c95f A2 | 1.454228535 | 0.652679801 | 0.801548734 |

基线wall首尾相差5.099倍，不能把wall均值差写成稳定收益。event均值0.652585804→0.628187954ms，组合窗口描述性差约3.73864%，作为小信号保留；不分离C batch与2D，不称稳定DMA带宽或服务收益。

实际Torch CPU线程56，cgroup额度600000／100000us，即6CPU；20GiB host上限，门前3.219GB、门后3.251GB，均非运行峰值。整个外层期间cpu.stat增加134个period、54个throttled period，比例约40.30%；`throttled_time`增236317938303ns是累计调度统计，不能当作236秒wall。门确实经历过节流，但没有各计时窗的cpu.stat，不能确定A1异常来自前处理、某次提交或等待。CPU全pool填值／比较是前处理事实，不是已证的异常根因。结果内memory_before/after为空，仅因该helper读取v2路径，本实例v1实际观测保存在外层原件中，不能解释成未占内存。

两case旧plan准备为1.342／2.400ms，新plan为1.443／2.264ms，新Tensor检查和ctypes descriptor准备另为0.759／0.891ms。它们均为单次受CPU状态影响的样本，不能视为免费，也不能乘42推成本。真实服务一次SAVE必须计入一次准备、原producer fence、host分配／生命周期和完成事件，不能直接采用这里的热submit差。

## root已采纳的唯一下一动作，尚未实现

先做一次短64call三路控制，再决定42层实际payload门。运行py818e／cpp0a4d保持不变；不改56线程、6CPU额度、官方参数或受测原件，不自动重跑。

三路固定为A＝冻结c95f；B＝同C桥C-linear，`prepare_save(max_pitch=16384)`仅在提交前把稀疏段拆成原单页，原生线性descriptor为37／26、二维0；C＝同C桥C2D，使用真实查询max pitch得11／6提交。B的拆段是显式控制，并非设备pitch不足。所有路保原页／bytes／stream／SDK。仅新增B路径的完整CPU oracle／c95f字节、source／pinned双guard及计数正确性，不扩形状或故障注入。

计时仍仅首case，**固定A／B／C／C／B／A，每窗64call**。全部分配、pattern、正确性、准备、event首record和submit预热在计时窗前完成；窗口之间不做整pool CPU比较或pattern填值。每窗前后记录实际v1 `/sys/fs/cgroup/cpu/cpu.stat` 原值／差值／单位，采样不放入wall或event窗；可单列进程CPU时间，不能把cgroup累计线程时间当wall。准备耗时继续单列，真实submit及同流完成仍计入。

结束条件：B正确性或异步错误就拒绝、不开始计时、不降级重试；六窗完成即收口，原始正／负／高波动全部保留。B与C相近则不把组合差归给2D合并；A与B差说明Torch方法路径与C batch路径的组合区别，不冒称只省某一个Python开销。若wall仍波动或对应窗口有节流，wall结论不确定，不继续追样本；事件没有正信号也保留负结果。

若三路信号值得继续，root已选 **直接合并一次原long／VERIFY1真实42层事务诊断**，不另造22GiB合成fixture。边界采用framework `2026-10-22-kv-pitched-save-worker-boundary.md`（574515e9…）：新SAVE完成后、SAVED／source free之前，复用已预算的单层verify_buffer，逐层通过冻结c95f从真实GPU源页回读，实际event完成后与新host逐byte比，42层全过才SAVED；此后仍原FULL回读和consumer。这样独立证明新SAVE源读正确，而非只用可能错误的host互相自证；不新增0.7GiB影子host或GPU buffer，原预算／fence／引用／错误settle不放宽。这仍只是已选后继设计，尚无新worker代码或部署；诊断时间不当性能。真实一次SAVE含准备、加载和生命周期成本，后续才考虑VERIFY0与accuracy。

专项JSON：`source/kv-pitched-copy/032653-hardware-review.json`。本轮无新runtime／启动脚本／GPU／SSH或外部写；root先固定032653、ABI和各owner记录的检查点，下一阶段从上述唯一门接续。
