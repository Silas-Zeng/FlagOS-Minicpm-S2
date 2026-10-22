# 64call三路SAVE短门：系统包装与实际状态

本轮从本地checkpoint `2746e01b` 继续，只准备一次独立单层API门。原032653组合门已通过，但wall波动较大；该结果不改写，不重跑旧测试或模型服务。

本agent独占 `scripts/remote/launch_kv_pitched_threeway_gate.py` 和本系统报告；hardware独占新设备gate及其计时解释，framework审阅候选/桥与包装。各owner使用独占文档路径，不覆盖其他职责报告。

外层从冻结3ffe逐byte小fork，只有三行差异：`gate.py` 的输入文件/pin改为 `validate_kv_pitched_threeway.py`；controller允许的后缀与新建run后缀改为 `-kv-pitched-threeway-gate`。其余单GPU锁、双idle、实际SDK编译/so SHA/ldd/readelf、唯一device-worker、300秒超时定向清理、DB前后、source前后和完整seal全部不变。原outer与原032653原件均不覆盖，不增加新的生命周期层或验收器。

入口无参：

```bash
python /workspace/experiments/minicpm-s2/scripts/launch_kv_pitched_threeway_gate.py
```

返回新UTC run/control/runner PID，设备child CLI与所有source文件名沿原门，root取回完整两目录。runtime `818e788b…`、SDK桥 `0a4d44d8…`、基点c95f、两真实页序JSON、实际ABI、DB/helper/监测pin均不变，不更改线程/CPU额度/服务参数。新outer冻结候选SHA `b2c65963f621f83b0d093353e7135b3434d4c49bb9402c05bb2a3363aa6f5a88`，gate pin `9b16aec69ecc6e2bf59de7fd0f323ae543a1a32eda15486aa294e2f49c645dd9`；相对旧3ffe只三行diff，逆替换逐byte精确重建旧文件。`threeway-wrapper-check.json` SHA `ba72ed698d71e9e63e70413a88732ce1f4bc7c40276d93c75040d6ec4cb08cf0` 保存唯一必要CPU静态核对。未执行controller、g++、设备或旧测试。

设备脚本固定两组真实SAVE页序的单层构造，先补同一桥的C-linear完整字节/guard/输入检查。三路为A原c95f、B同桥线性拆段、C同桥2D合并；全部正确性通过后，仅首case按64call `A/B/C/C/B/A` 计时。B在提交前以受控max_pitch=PAGE拆回原线性run，仍由同一真实SDK桥执行，不把受控拆段称为实际设备pitch不足；runtime/桥字节不改。

逐窗口真实v1 cpu.stat/quota/period在wall/event窗外读取，保留原值、差值和进程CPU时间。quota6与56Torch线程保持原值，不调用线程设置。累计线程 `throttled_time` 不当作wall时间；单层信号、节流或波动均保留不确定性，不自动复跑或推广到42层服务/E2E。当前没有新run ID、实际.so、字节或性能结果，registry仍113，实际门须root唯一GPU串行启动后再登记。

framework与hardware已定向终审最终b2c6/9b16无最短门阻断，framework回执 `analysis/source/kv-pitched-copy/threeway-framework-review.json`（3c86dd5e…）。没有执行旧测试/复制/设备；运行资产冻结，后续实际run由root串行启动并取回，本报告不预填通过。
