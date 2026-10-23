# 当前446的单RID抢占／恢复CPU诊断

仅补“新栈是否有实际重复提交前缀”的因果元信息，不接 KV 保存／恢复策略，不启 profiler 或设备同步。基点固定 `141159` 受测446（tree `5c77e68c`）；仅 init 追加开关与新增 observer，产447/tree `cd50086e`。runner `183de0ab`、P `5bc850eb`、normalization `24a421fa` 均不变。

冻结 helper `0268b058`、owner `800a4fa8`。部署 `launch_resume_cpu.py`、`candidate-git-blobs.json`、`candidate-manifest.json`、`observer-manifest.json` 及 `files/` 两路径后，由 root 在原官方结束并清理后运行：

```sh
python3 <assets>/launch_resume_cpu.py
```

固定原446 live/control全map核对后只创建新副本；原 bc51 `--context-long-screen --seed 721201`、32×16K/1024、SERVER、请求到达、采样、设备锁、监控和清理不变。owner 沿旧 88b 的6CPU/严格空闲/DB-before；DB-after/完整源与后态仍由原 sealer 负责。唯一开关 `BIV150_RESUME_CPU_OBSERVE=1`，源码中不带 Qartifact/KV/finite/PR15。安装 marker 仅表示 bootstrap 接线；实际 `ARMED` 和以下同 PID/RID 链才是覆盖。

`BIV150_RESUME_CPU` JSON 行保存在原 `server.log`：

- `PREEMPT_BEFORE`：首个真实 `_preempt_request` 参数对象，issued computed、known/prompt/output、placeholder、抢占计数与现有队列各帧的 target q；不查询 Future。
- `RESUME_FIRST_ATTEMPT`／`RESUME_ADMITTED`：同对象、同抢占 epoch 的真实 APC local/external/cached 起点和原分配／准入结果，不受旧 N≥29 限制。
- `TARGET_EXECUTE`：同 RID 的实际 SchedulerOutput payload c、q、N/M与原 execute 一次成功返回，最多16条；`FINAL` 明示已到原 known 端点、partial/上限、再次抢占、退出或未发生抢占。

这些仅证明 CPU 提交与原方法返回，`gpu_completed_floor=null`；issued computed 可乐观，不是已完成 prefix，区间重叠不能直接叫 GPU 重算耗时或可省秒数。不记录 token 值、不根据元信息改变原策略。未覆盖、提前结束或再抢占一次收口，不追加补跑；诊断 wall 不作性能收益。

CPU仅语法、三调度 callback 剔除后逆回87a、init逆回e043及owner逆回c5ec；未执行服务、模型或旧套件。硬件负责人只读新增 actual-RID/epoch/APC/16返回、原callee一次、异常隔离与owned归还，以及447两路径／原bc51接线，未见当前诊断阻断。旧191047/192308证据不继承为新组合通过；此门也不直接批准 KV 集成。
# 本轮收尾状态

用户要求完成当前官方后切换API。447仅CPU准备和互审，本轮未部署、未执行、无run ID；以下命令只供以后明确继续时接续，不自动启动。

