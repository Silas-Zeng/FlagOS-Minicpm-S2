# BI-V150 单层真实页序的 C batch＋2D 拷贝门

本阶段只准备独立设备门，尚无设备结果。保留015315和021658实际SAVE的全部KV、物理源页和逻辑顺序，不改R、不排序、不重算、不接worker或服务。范围仅天数BI-V150实例；不外推沐曦－曦云C500。

## 固定输入与实现

冻结几何见 `source/kv-pitched-copy/save-arithmetic-evidence.json`，SHA `489f1468956ff96e86188feeb89933df0ab5d35458b8d184b6adbb2729497dbc`。各层页宽16384B：

| 实际SAVE来源 | 完整逻辑页 | 单层字节 | 原连续段 | 新计划段 | 若实际pitch支持，线性／2D提交 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 015315 | 1058 | 17334272 | 37 | 11 | 2／9 |
| 021658 | 1048 | 17170432 | 26 | 6 | 2／4 |

源pool仅取实际最大页号＋1：32578／32572；每个case只有一层raw存储。单层门不能直接证明42层真实SAVE或E2E收益。最大正步长2049，所需source pitch为33570816B；门由SDK桥查询实际设备max pitch。超出max pitch的段在任何提交前拆为单页线性拷贝，实际结果必须注明fallback，不能把未执行2D的段算成已验证。

新实现为 `patches/framework/candidates/biv150_kv_pitched_copy.py`（`818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd`）和 `biv150_kv_pitched_bridge.cpp`（`0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44`）。原对照为 `biv150_kv_page_copy.py` 的c95f冻结版本。新桥按实际SDK头编译，连续段用SDK `cudaMemcpyAsync`、稀疏段用 `cudaMemcpy2DAsync`；Python一次调用C batch。

因此两路ABBA比较的是 **C批量提交＋2D合并的组合候选**，不能把全部变化归给2D。原c95f计数是`copy_`方法次数；新桥计数是成功提交的原生API次数。两者均不是DMA描述符数量或时间占比。

## 实际ABI证据及尚未证明的内容

root纯CPU取证 `experiments/source-audits/20261022T030314Z-memcpy2d-abi/result.json`（`f9c348a60fa34469377fda671d2d57a42c108fca2554fd59963b6b7033ffb576`）已核：Corex D2H枚举为2、stream为不透明struct指针、Linux IXRTAPI为空；mapping把CUDA名称映至IX；实际Torch `Stream._as_parameter_`返回`c_void_p(cuda_stream)`。库d39d…有两组实际导出。证据只确认声明与ABI，不确认设备复制正确或更快。

外层按相同实际SDK头编译并保存编译命令、输出、`.so` SHA、ldd/readelf和头／库SHA。设备子进程在导入Torch和桥后还核 `/proc/self/maps`：实际唯一libcudart须为SHA `d39d579627d19ddb903855ebc4859661579633a7ecc4d1ad51866d79296ba527`；未知或不同库拒绝。没有手写未经核实的CUDA枚举或调用约定。

## 最短正确性与异步边界

`scripts/remote/validate_kv_pitched_copy.py`只有设备worker，导入及`--help`不导Torch、不载库。外层 `launch_kv_pitched_copy_gate.py`独占flock、双栈idle、CPU编译、DB前后、单子进程timeout定向清理及完整封存；不存在第二把锁或第二个controller。

源和两份pinned目的均为带正storage offset的view，两端guard使用正数basic narrow读取。每4字节编码16bit物理页号和页内word号，区别大步长页及页内偏移；不使用GPU高级索引作oracle。新桥紧随同一个显式非0 Torch stream上的H2D producer；传该流的真实handle，并只等待同流event，然后立即和CPU oracle比较。此时旧拷贝尚未提交，避免旧路等待掩盖新桥stream错误。

随后原c95f复制同一全部页，做新旧与CPU oracle三方全字节比较、host双guard、源整存储及双guard回读不变；两case都通过后才计时。CPU/GPU RNG前后不变也需通过。所有tensor、view、pinned host、descriptor、stream和event在异步开始前强持有。submit返回不是ACK；中途错误不能静默改走旧路。仅失败清理可尝试device-wide settle，不能settle时保引用直至外层终止设备子进程。

## 计时边界与最短命令

首case固定8次调用的ABBA；event对象先创建并record/sync、两条真实submit函数先预热。wall包含每条真实submit的Python/C检查、SDK查询、event record与完成等待。双方planner与新Tensor验证／ctypes descriptor构建在窗外，准备耗时单列；分配、填值、producer、CPU全字节比较也在窗外。没有第三路控制、形状扫描或长轮次。结果不代表整个SAVE；有信号后才决定是否独立区分C batch与2D。

外层归档后的设备命令为：

```text
python RUN/source/gate.py --device-worker --output-dir RUN --source-dir RUN/source --bridge-sha256 <本轮实际编译.so SHA>
```

`RUN/results.json`或`RUN/failed.json`独占创建，不覆盖历史。外层保存精确命令、全部source、环境、监控、DB、postflight及seal；运行由root唯一设备owner负责。本owner只做本地准备／只读交叉审，没有SSH、SDK编译、载库或GPU执行。

## CPU准备状态

候选owner唯一planner合同 `tests/test_biv150_kv_pitched_copy.py` 一次1test／0.013s通过，核两真实map逐页重建、保原连续run、非正步长／重复／越界／overflow拒绝；本owner只读合同及结果，没有重跑。门仅做必要语法、导入无Torch与`--help`检查。CPU合同不执行桥、GPU或事件，不能替代真设备门。最终脚本／外层SHA及交叉审回执见本owner handoff和各owner记录；任何后续改动须更新pin后交root。
