# 2D SAVE API短门：外层包装与证据边界

本轮只在天数BI-V150验证单层、两组真实SAVE页序对应的构造张量，不启动服务、模型或现有KV协议。上一进展victim A/B因KV池和启动内存项失配已收口，三个收益字段为null，不追加第三轮。本门没有沿用其性能结论。

外层入口为 `scripts/remote/launch_kv_pitched_copy_gate.py`，SHA `3ffe8efe643a5c280a85217299bcb0adb6349c66f499659d2de9b5167dcce7da`。root在远端无参执行：

```bash
python /workspace/experiments/minicpm-s2/scripts/launch_kv_pitched_copy_gate.py
```

入口新建唯一UTC的 `framework/<UTC>-kv-pitched-copy-gate` 和同名 `-control`，返回run、control、runner PID。归档的controller独占 `framework-device.lock`，准备前和worker前分别检查单BI-V150/32768MiB、68MiB/0%、无GPU进程、9031双栈未开放。全过程只有hardware的一个device-worker及只读ixsmi监测；外层不导入Torch、候选模块或CDLL。300秒超时只清理本轮child/monitor进程组，失败也保存DB-after、源码复核和postflight，不使用服务专用seal。

`RUN/source`保存gate、候选Python、C++桥、原c95f基点、实际页序JSON、030314实际ABI JSON，以及本轮编译的 `bridge.so`。g++用实际Corex头/库和rpath，C++源码位于 `-lcudart` 之前。compiler版本、精确编译命令、stdout/stderr/exit、实际.so大小/SHA、ldd、readelf动态段/符号均独立保存；编译失败保留原输出且不启动设备worker。ABI源指纹及libcudart `d39d5796…` 先验核对，设备worker还须核自身 `/proc/self/maps` 真正加载的库。

worker命令固定如下，`.soSHA`只能来自本轮远端编译：

```bash
python RUN/source/gate.py --device-worker --output-dir RUN --source-dir RUN/source --bridge-sha256 SO_SHA
```

冻结输入为runtime `818e788b…`、桥 `0a4d44d8…`、gate `c8c0f64e…`，c95f完整SHA及八个素材的本地/远端映射保存在 `analysis/source/kv-pitched-copy/outer-wrapper-check.json`（`f8723f7cf8a88cadd6859c0f1abb434f263975ecd1389c6e09264f05eb0e35a2`）。本agent只做AST/compile和pin检查，未执行controller、g++、设备或旧测试；实际编译和设备门由root串行负责。

两组真实原始页数组来自015315和021658；源页逻辑次序与全部KV字节保留，不排序、不截断、不增加packing buffer。两组字节门均通过后，仅第一组做8call ABBA（共32次）微计时，比较旧c95f与C batch加2D的组合，不分离2D贡献。非零Torch stream、native handle及同流event必须一致；提交不是完成，任何partial失败必须settle且不得静默从旧路重试。完整正确性、guard、输入不变、RNG、实际pitch/调用计数与计时均待本轮原件，不能预写通过或服务收益。

root最小收集方式是取回完整run和control两目录。`control/seal.json`列所有已封存regular-file字节SHA/大小（不自引用）；封存前flush controller stdout/stderr，避免runner.log退出刷新造成哈希变化。两端DB用既有只读snapshot保存物理/schema/logical三SHA和表/行数，变化如实报告；不清缓存、不覆盖原始CSV或旧源树。API结果独立于官方baseline，不能作为完整42层服务、准确率、稳定DMA带宽或E2E收益。
