# 下一 K 寄存器预取：资源作为成本的 v2 入口

纯 CPU 封包，尚未编译/上卡。原 v1 包 `d6bc61b2…` 保留。

相对 v1 **只修改 worker 两处资源判据**：private/runtime spill、SGPR/VGPR/shared 增加均记录为成本，随后只要数值、Q-hoist、当前页段条件和实际 next-K→首PV窗口成立，就进行原有几秒 ABBA。静态资源不能代替净收益判断；128 VGPR只保留为原始粗界字段，既不表示小于它安全，也不表示超过它必然退化。记录逐项资源增量，`actual_occupancy_proven=false`。

kernel、helper、真实 TP1/FlagGems 安装、main526/native14f 身份、owner/锁/9031检查与DB清理逐字复用。基准仍是实际受测 affine+Q，候选只增加 next-K；单16K连续页、逐位/KV/guard/RNG、换页重新提交、16-call ABBA保持。没有为了这一策略调整重跑已通过的168组CPU地址门。

Q-hoist失败、实际预取窗口消失或数值错误仍停止。结构门在首PV停止，不证明全部32条MAD都在等待前；真实ASM需审首wait位置，不能把结构通过解释为完整延迟隐藏。计时失败或无正信号保留原件，不自动扩case或接服务。

入口与v1相同，由主线程在官方任务结束、设备独占且审阅通过后安排：

```bash
python entry.py --source-dir /workspace/experiments/minicpm-s2/code/已冻结main526 --native-library /已核14f原生库.so
```

`worker.diff` 只展示本次两处资源策略变化；`kernel.diff`、`cpu-check.json`是原v1证据，未改名为新验证。`resource-policy-check.json`记录两处精确逆回、新增private/spill不误拒与Q-hoist缺失仍拒，以及全部复用资产SHA。`prepare.py`只在本目录复制/封包，不触及设备或原v1。

方法、硬件依据、PR38去重与未确认项继续见 `docs/agent-work/hardware_innovation.md`；最新GPU状态由主线程记录。
