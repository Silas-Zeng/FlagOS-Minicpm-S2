# KV页序候选成对短测准备（天数BI-V150）

本文件只记录本地启动包装与复现边界，不代表已经运行性能对照。204159已通过单次真实恢复、42层整字节回读、runner状态与原输出消费；该门VERIFY1，不能拿227.55秒与其它run做收益结论。当前稳定080656/103/105未被新协议替换，新协议准确率仍待。

独立新文件 [`scripts/remote/launch_kv_pair_screen.py`](../scripts/remote/launch_kv_pair_screen.py)，最终跨owner审阅通过SHA **11917a047c3c3f5fadebca3898b5720224e075e3ca93bb610c258a4ef70776ad**。它不改8d7诊断launcher/0e2115协议/31cc worker/616事务，不重建候选，只复用固定两个远端目录：

- stable：`/workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z`。
- page-order：`/workspace/experiments/minicpm-s2/code/kv-page-order-20261021T204159Z`。

204159 control/source-sha256.json固定SHA **98a72844e77eee9e07d6c70050003bd121bb61404c507189dd663a320651f240** 锚定候选416完整文件；其innovation-source.json经同清单核SHA后提供stable410完整input清单。source路径、基线/产物路径、4c8 preparer与0e2115协议和output map均核，不接受任意路径/source或未固定清单。只用已pin的纯stdlib source_files/SQLite辅助，不导入候选、torch或vllm。

原bc51 driver、context-long-screen/seed721201、原SERVER保持；唯一新增进程环境为 `BIV150_KV_VERIFY_RESTORE=0`。两variant分别要求原SQL安装marker/协议安装marker；marker不是实际restore命中，结果仍要独立读事件。准备阶段持原framework-device.lock、核68MiB/0%、单卡32GiB无进程与9031双栈关闭、复制全source/control/hash/命令并快照DBbefore。释放准备锁后原bc51自行重新拿同锁，root仍为唯一owner，不能并行启动其它任务。DBafter/live/fullpost继续复用root既有封存步骤，本文件不新增第二套服务流程。

只有root在204159完成清理后执行以下命令；本owner未执行远端或主流程：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/launch_kv_pair_screen.py --variant stable
```

stable结束后先由root封存DBafter和postflight，再传它实际输出的control路径：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/launch_kv_pair_screen.py \
  --variant page-order \
  --match-baseline-control /workspace/experiments/minicpm-s2/framework/实际stable运行ID-control
```

可选match分支只接受同一最终wrapper正常完成的stable、正确完整source清单与source/live/idle封存。它重新计算baseline db-before/db-after三指纹，**baseline自身前后不等则拒绝启动候选**；再要求候选DBbefore与baseline after三个SHA全同，不同也不启动。失败保留新control/DBbefore和包装命令，不回写DB，不清cache，不把新DB起点伪装成匹配。没有match参数时不会宣称匹配；本轮计划应传它。

这些门只固定SQLite三指纹。KV容量、CPU限制、原请求/输入输出数、服务参数和系统源码仍要运行后逐项验收；若不等，就不能称配对有效。SQLite相同也不能证明编译cache全热。VERIFY0只移除诊断回读，既有protocol稀疏日志/设备fence/显式ZERO等保留。性能pair与后续准确率分开，当前没有官方总分或C500结论。

验证仅本地compile/CLI help通过。root只读review后要求补baseline自身DB前后门，已完成并重新compile；hardware独立全文审最终11917a无阻断，额外在本地实际重算98a728→3b134→410/416/preparer4c8a信任链一致，没有执行主流程或重复suite。代码冻结。root已上传精确11917并启动唯一 `20261021T205219Z-kv-pair-stable-context16k-long` / runner221074；基线尚在途，未有结果。须其结束并封存后才启动匹配候选。本owner没有SSH/GPU/共享代码库推送，不扩启动器套件。

## 205219稳定基线已独立验收，205819启动容量失配已知

上述“基线在途”仅历史。完整205219原件取回后，新纯只读 [`review_pair_screen.py`](source/kv-worker/review_pair_screen.py) 首版 **1b2434ed50d52824bda0d8d6a254c792b0f46bd71a9a0ea545fa9ea4a78b71b5** 实际运行stable审阅通过，结果 [`pair-stable-review.json`](source/kv-worker/pair-stable-review.json) **1f223b259be1354c00c22f902eb3978480818bdfc2d3d520f3dc61f90d65061b**。完整410源由固定98a728/3b134的input清单逐SHA核，11917 wrapper/bc51/原SERVER/contextlong/seed/VERIFY0一致，source/live410与post54c通过。基线没有协议事件，不能对它硬套“verification_passed=True”的诊断断言。

实际32/0、524288输入/32768输出、CPU6/32GiB、KV **521936**、preempt0→1；**220.40704781701788s/2527.3964944282015总tok/s/TTFT62508.42458468105ms**。DB518表19337行的三SHA在before/after重算一致（d9351095/a5ca71a5/a180ecc5），不是沿用前次assert。finish20:57:23.397901Z exit0；post20:57:56.258707Z68MiB0%、9031双栈闭/无GPU、owned controller仅Z。原shutdown AsyncLLM/EngineDeadError完整保留，不改exit0或称全程无错误。

root已通过DB共同起点门启动 `20261021T205819Z-kv-pair-page-order-context16k-long` / runner222435；候选尚在途时，实际启动日志已显示 **KV521840，比基线少96**。这不满足可归因pair条件。不能调整原服务参数硬凑容量、拿204159的227秒诊断作替代对照，或把同源0e/VERIFY0直接解释成全部profile/cache条件相同。当前只有容量不同这一事实，原因需实际memory profiling日志，未归因为某个候选改动。

首版审阅脚本逐byte保存为 `review_pair_screen.initial_1b2434.py`；当前仅将候选分支改为“完整服务验收”与 `valid_for_e2e_pair_attribution` 分离，不再因KV不同而断言中止/丢失整个run结果。现版 **b8fdacf075b7db086554faca144d2a10d8d440d57022f0fda6cf8384058eb40b** 已语法检查，未执行候选分支/未生成候选成功JSON。后继完整原件到齐后实际核容量、DB变化、真实协议命中与VERIFY0无回读、退出清理，失配就如实记录为capacity_mismatch，不提前报收益。

## 205819完整运行验收：服务链通过，KV与运行中DB双失配

上段“候选在途/未运行审阅”是历史。root封存完整205819 run/control后，审阅脚本再仅补候选DB变化/新增表分类，最终 [`review_pair_screen.py`](source/kv-worker/review_pair_screen.py) **6f05112436465a891a41e07fd97e6944f81413757b46d55cbc111a825e1639b5** 实际运行page-order分支一次，4.4s exit0。结果 [`pair-page-order-review.json`](source/kv-worker/pair-page-order-review.json) **dea87425c140d98656d72ef712865a86bc4a26e12ad8d20de24d044a9d39dbce**；原始baseline JSON与初版脚本保留，没有因DB变化而硬assert失败、删除结果或补伪造匹配。

416份source逐SHA与固定204159源树一致，11917 wrapper/bc51 driver/原SERVER/contextlong/seed721201、command env VERIFY0、source/live416/post54c、32/0与输入输出数全部通过。实际worker222629保存 **R16688/1043页/717717504B**、966calls；排序marker1043→66，目的表实际升序且ZERO/RESTORE相同，二者各2772calls。各ACK diagnostic_verify_requested=False、额外校验pin0、无verification回读记录；这是本轮VERIFY0真实链，不冒称本轮又做了全字节核验。runner六检查全true、原update消费16个scheduled token、host DROP释放，restore_skips462/preempt0→1。204159的全字节证据另存，不继承为整模型accuracy。

| 完整运行原值 | stable205219 | page-order205819 |
|---|---:|---:|
| 成功/失败请求 | 32/0 | 32/0 |
| 输入/输出token | 524288/32768 | 524288/32768 |
| 时长秒 | 220.40704781701788 | 220.92108358303085 |
| 总tok/s | 2527.3964944282015 | 2521.515787290788 |
| TTFT均值ms | 62508.42458468105 | 62648.45590685 |
| 实际KV token容量 | **521936** | **521840** |
| DB before表/行 | 518/19337 | 518/19337 |
| DB after表/行 | 518/19337 | **519/19340** |

双方初始DB与baseline自身前后相同，启动器共同起点门本身有效；但**实际KV容量不同，候选测量中DB也改变**。候选after实体/schema/logical三指纹实际重算为 `89743b20d842c8f6067f6e1b917dec0f9f9b4eae19d93e3ebf02e168f4aea605` / `29d740d5351d1372df2bb6317a651c70b682d2d855b51e717afd576cfe78c078` / `71ac19899ea28dda8cb94b517a8f598c487bbd19f392a9b285ff5ab660355c29`。精确新增不是“一个新表3行”：新 `_index_linearized_jit_function_9a237b62d77bcd3e0f0833dfde750886-9924b48a7525689bfbd1343251dd73a2` 表1行，既有 `_index_linearized_jit_function_c19f39cdc804f088a2631f8fecaae5eb5960a4c725a573e894f264fb410e0996_benchmark_v2-be4075f355600487930f16fe2a2e2b52` 由2→4行，总+3。

因此JSON明确 `valid_for_e2e_pair_attribution=False`，两条原因分别为启动KV容量不同、候选调优DB运行中变化。只能保存两个原值，不能归因页排序的正/负收益、宣称全热、用227秒诊断比较或改服务参数硬凑容量。单补一条stable不能追溯修复本组测量期间DB差异。后续若root选择新起点重测，应先封存本组，最多再一轮必要baseline，并独立核容量/DB/参数；本批不立即补跑。

205819 finish **21:03:25.435830Z exit0**；post **21:03:56.715618Z** 为68MiB/0%、9031双栈闭、无GPU进程、416live无失败。该run原log无ERROR/EngineDeadError命中，205219的原shutdown错误仍保留。无新accuracy、官方成绩或默认集成。root准备阶段发布/ZIP，本owner完成本JSON/文档/handoff后暂停文件写入，等待解除；目标继续有效，容量候选仍只是独立local后继。
