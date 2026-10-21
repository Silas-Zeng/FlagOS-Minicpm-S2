# CTA gate-up服务短筛：正信号保留，KV池差单列

2026-10-22，systems_innovation；只读本地原件，设备由root串行负责。三次均为BI-V150物理32768MiB、CPU6、原服务参数/bc51/0813、16K输入/128输出/32请求/c64/seed721201，32成功0失败、524288in4096out。不是正式比赛吞吐或新准确率。

| 运行 | 秒 | total tok/s | mean TTFT ms | 实际KV tokens |
|---|---:|---:|---:|---:|
| CTA候选182916 | 118.41752642998472 | 4462.042198731546 | 59983.97987510543 | 521840 |
| 干净基线183543 | 120.48498157598 | 4385.476040985142 | 60874.43063224782 | 521936 |
| 第二干净基线184244 | 120.7632626676932 | 4375.370359560136 | 61145.73857927462 | 521936 |

第一对照描述TPS比1.0174590299960238，即+1.7459029996%；耗时省1.7159442770%，TTFT−1.4627664652%。同物理32GiB满足平台容量要求，但候选KV池比基线少96tokens，可能含实现启动成本/分配波动，尚未分离其贡献；不能称KV池严格相同。第二基线仍521936，仅补充两基线同容量耗时观察范围120.484981576–120.763262668秒，相对跨度0.2309674518%，不是噪声分布的统计估计。没有为凑96tokens改参数、加假buffer或无限刷新容量。

候选413项源SHA、两基线各410项及所有installed源/包身份核对；差异仅e155→7876 runner、06c7 policy、44fc runtime及包装manifest。六份前后DB实体均为516表19270行，三SHA1593/a0a590/90e9不变；三次preempt0→0，CPU测前后6核，结束68MiB/0%/双栈9031闭/无GPU进程，owned退出或Z。

EngineCore201873注册alias `_iluvatar.ops.mm`和5份artifact源SHA核实，真实C0是BM256/BN256/BK32/SK1/w16/s2/ctas1，grid384×1×1，97regs/0spill/65536shared。FIRST_SELECTED发生在startup profiling；REAL_SELECTED证明首个真实2048-token、1request execute中至少42次新launch。status文件是首次real flush（real_calls35、real_steps1），不是全负载计数，也不能声称只有42次实际调用。down不启用，capture/非scope/非C0/miss保原。

退出原件保留：候选load32/0完成、after metrics之后，driver SIGTERM触发abort/forcekill teardown，随后有AsyncLLM output_handler EngineDeadError及资源清理警告；运行阶段ERROR为空。不能删日志或写“无ERROR”，也不将关停时序错误改作已成功的请求失败。两基线原日志/对应独立review也保留。

此次运行顺序为候选→mapped编译失败门→基线→第二基线，未随机交替，同DB不排除Triton/CPU缓存和主机负载差异。小正信号保留待确认，不对覆盖诊断作性能比较，不继承已有SQL+C3的accuracy资格。

机器可读数据：`analysis/2026-10-22-mm-cta-service-comparison.json`；本地stdlib重算入口：

```powershell
python -X utf8 analysis/source/mm-cta-service-pair/recompute.py
```

每份run旁保存`independent-service-review.json`。183421 mapped首门17源SHA虽核实，但首个derived skip2D JIT在backend `add_accelerate_matmul(use_sme=68954357763)` binding失败，exit1/cases[]/无timing，不作数学或性能结论；负面和原wrapper恢复证据保留，根因由framework审实际compiler hook。
