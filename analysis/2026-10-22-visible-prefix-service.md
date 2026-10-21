# 已过门 prefix-mask 的独立服务入口

本文仅适用天数 BI-V150 的 MiniCPM5-2B；沐曦－曦云 C500 由队友验证。主负责人 root 串行持有设备，本 owner 只做本地源码、CPU 合同、交叉审阅和原件验收。root 已完成190206独立短服务，结果负面，保留候选但暂不合并到稳定 SQL+C3；未与 CTA、mapped、metadata 或 async 候选叠加。

## 保留小信号，测试实际服务

原 `20261021T121838Z-prefill-visible-prefix-gate` 已通过 C3 的 D29+P2019/16K 与单 Q2048/16K 两形状，完整 BF16 bits、KV、RNG、padding、2D 命中与 3D C2 回退均通过。原 32-call、预 record Event ABBA 的 wall 为 `12.594359734375→12.559617125 ms`，下降约 `0.275858%`；Event 为 `12.491010189→12.434306145 ms`，下降约 `0.453959%`。这是单层小信号，不能报成服务收益。用户明确小收益也要上卡和保留，因此准备最短独立服务筛选。

策略和派生 kernel 完全不变，仍为 2D BM128/T64/w8/s1、BF16 GQA16/2/h128。只在全部有效 128 行且完整 KV tile 对首 query 已可见时省恒真 causal mask；partial query block、边界 tile 和未知功能仍按原 mask。cached prefix 不对齐时可能保留两个 masked tile，不能概称只剩最后一个。原 3D/C2、dot、softmax/PV、K 遍历、KV 写、位置、请求顺序、采样和 RNG 都沿用原实现。

## 冻结文件与实际安装顺序

| 文件 | SHA256 |
|---|---|
| 原 policy：patches/framework/biv150_prefill_visible_prefix.py | `87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6` |
| 原派生 kernel | `a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2` |
| patches/framework/biv150_visible_prefix_service.py | `7258ad7929ad22676201fec045184f0038be4689f2eef3a51b21e30c658029da` |
| patches/framework/biv150_visible_prefix_service_source.py | `464b9ea73f6961097c1cde2c92d97bdf9ed50909e9da1ecbb65f1dd437bccaba` |
| scripts/remote/prepare_visible_prefix_source.py | `a4e978770e98aa3c5a245de96470916aae570ef63a55083534465309ceaf615f` |
| 复用 prepare_innovation_source.py（未改） | `0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca` |
| 派生 runner | `4467ac262bb22edca90c106ae2361efe5e8917ec7115d51c07d4d3e35245703a` |

transformer 只接受原 e155 runner，完整保留原 bytes 前缀，在现有 SQL→C2→C3 footer 后追加安装器。包装构造函数，在原 `__init__` 返回后启用，先于 `worker.load_model` 和 graph capture；保留 C3 metadata/forward 包装顺序。policy 实际绑定原 C2 对象，而非再切换已存在后端。只在模型的 execute/dummy ContextVar 内启用原 policy，finally 恢复，capture 直接原 C2。严格原模型 config596、BF16/2048/6144/42/16/2、单卡并行、FULL_DECODE_ONLY，无 quant/spec/LoRA/MM/连接器/跨层共享 KV；其它配置原路。

`BIV150_VISIBLE_PREFIX_ARTIFACTS` 必须位于本次实验根目录下，每进程建唯一 `pid-*` 子目录。原 policy 的 `create(xb)` 只写该 PID 的新派生文件，不覆盖 installed attention 或稳定代码。保存 policy/service/C3/SQL、actual attention/helper/backend 与派生 a6d 的 SHA，进程内幂等，不嵌套多个代理。

本 kernel 只新增 constexpr 开关，没有添加真实 tensor operand，未发生 mapped 旧版本 dummy `out` 导致的 SME 第 36 位问题；没有覆盖 `use_sme` 或改变编译选项。此项说明有 actual spec JIT 源码与 owner CPU operand 复算支持，不构成新 GPU 通过。

## 最必要 CPU 验证与互审

`analysis/source/prefill-visible-prefix/service-cpu-check.json` 保存已执行的一次合同：原 e155 完整前缀/逆去 footer、源码漂移拒绝、派生 compile、原 policy 仍生成 exact a6d；fake inner/runner 验证 dummy 与真实大 query 分离、小 query 不当整 tile 证明、capture/unsafe KV/作用域外回退、原返回值和异常 finally 还原。未导入 Torch/Triton、未做浮点或 stream 模拟。

`service-package-check.json` 保存一次真实归档源码复制：213→215 文件，唯一变化为 runner footer 与新增 policy/runtime；其它 SHA 全同，已有 output 拒绝。builder/source/runtime 的语法和 builder `--help` 通过。framework_innovation 已全文只读审 runtime7258/source464b/buildera4e，无当前阻断，未重跑 suite 或设备。复用代理只检查本类型的非阻断建议已记录；本次 exact 新副本不叠其它候选，不据此扩大通用安装能力。

## root 最短串行方案与启用证明

上传上表 policy、runtime、transformer、builder，复用固定 helper。仅 CPU 准备：

```bash
root=/workspace/experiments/minicpm-s2
python3 "$root/scripts/prepare_visible_prefix_source.py" \
  --base-source "$root/code/sql-mixed-20261021T080656Z" \
  --output "$root/code/visible-prefix-<唯一UTC>" --asset-dir "$root/scripts"
```

builder 拒绝原输出、素材漂移或已有创新 manifest，复制完整 source 后校验输入/输出 SHA；只改 runner、加入两个所需模块。派生 kernel 在进程内生成并核 a6d，不安装到 site-packages。

先复用当前最短 `run_framework_screen.py --context-screen --seed 721201` 的 16K/32req/128out/concurrency64，与原080656 baseline 匹配原服务参数、DB 三项 SHA、KV 容量、seed、冷热条件；此短筛替代早先优先1024out的计划。是否随后增加1024out由 root 根据结果决定，不预先追加。每端唯一 UTC run/control、同一卡串行。不同 seed 的测外预热避免共享测量 prompt 的 prefix cache；新 compiled variant 的首次命中若落入测量期须按冷窗口记录，不能当热 pair。

候选外层 launcher 设置：

```bash
export BIV150_VISIBLE_PREFIX_ARTIFACTS="$control/prefix-artifacts"
python3 "$root/scripts/run_framework_screen.py" "$run" \
  --source-dir "$candidate" --context-screen --seed 721201 \
  --require-log-marker BIV150_VISIBLE_PREFIX_READY
```

READY 只证明安装，FIRST_SELECTED 保存每个编译 hash 的首次时间、scope 和配置。必须在真实 benchmark 的 `execute_model` 中出现 `BIV150_VISIBLE_PREFIX_REAL_LARGE_SELECTED`：selected 增量大于0，且**单请求**最大 scheduled query≥128。不能用总 token≥128、dummy、8-token smoke 代替；该标记只证明有完整 tile 几何机会，不声称直接统计 GPU 免 mask 次数。每 PID `status.json` 与源码一起归档，服务 TERM 未运行 shutdown/atexit 时旧快照不当最终总数。

root 原 launcher/driver 继续负责唯一设备锁、DB before/after、PID、采样、pre/postflight 和清理。本 owner 没有设备作业。服务小、零、负或噪声结果都保存；父基点103/105准确率不会自动覆盖新入口，后续最终 accuracy/reproducibility 由 root 按实际服务信号安排。

## 190206 原件独立验收：首次接入短服务为负，保留而暂不集成

root 串行执行 `20261021T190206Z-visible-prefix-context16k`，实际归档 tgz SHA256 经本 owner 重算为 `5f79f583a41af027c4c5c7a51de968657465353d1127c1300555a8ef7425662c`。原 run/control 不改。已直接读取三份原 result JSON、全部 source/DB 快照与日志，分析产物为 `analysis/source/prefill-visible-prefix/190206-service-review.json`，不借用候选输出摘要替代原始结果。

两次 baseline 183543、184244 与候选均是相同16K/32req/128out、concurrency64、seed721201、driverbc51、原 server command、包版本及 installed/model/generation hashes，CPU quota均6核，KV均 **521936**。source分别410/410/413份实际逐项SHA通过；candidate相对base只有runner4467、policy87c6、service7258和打包manifest，原runner为完整前缀，每PID七份源码和派生a6d全符。三run各自DB before=after且跨run完全同一：snapshot `1593d60cda1b2ed9a70df9fc4cebe3217e863f9fcb428000dea19fe21c8d6352`、schema `a0a590080bc570c73c1a25337faa1097038bcc6d755fe379a29066aefff7c5b2`、logical `90e9a86870767253d7a2f43483f9ddd431f577d9da6516f3a6bac555478a9ade`；实际六份snapshot文件SHA均核过。preemption与APC hit前后均0，无通过不同KV容量解释本次差异的空间。

| 原始短服务 | duration s | total token/s | mean TTFT ms |
|---|---:|---:|---:|
| baseline183543 | 120.48498157598078 | 4385.476040985142 | 60874.43063224782 |
| baseline184244 | 120.7632626676932 | 4375.370359560136 | 61145.73857927462 |
| prefix190206 | 123.55798832001165 | 4276.4050077563625 | 63199.166325692204 |

三端均32/0、524288输入/4096输出token。相对两次baseline各指标算术均值，候选duration增加 **2.432238%**、TPS下降 **2.374615%**、TTFT增加 **3.588065%**。相对单次baseline的TPS分别下降2.487097%和2.261874%。这是负的首次接入短筛结果，没有服务收益证据，不依据原小层正信号强行集成。

真实启用由源码和日志共同确认。READY为进程208869；REAL_LARGE记录selected_delta42/max_query2048，但它可能先发生于bench的初始单prompt test，不能单凭第一条宣称正式32请求计时段命中。另有真实 `num_seqs=2/query_rows=2047` 和 `16/2048` 的FIRST，证明多请求主负载确实用了派生kernel。三编译hash依次为ef393b84…（8token smoke）、cac38024…（2/2047）、15bda8ff…（16/2048），均101regs/0spills/65536B shared。status的selected5713/real_selected5712/real_large_steps135是第三个新hash首次出现时快照，不是最终计数，更不是GPU实际省mask次数。

**该轮不满足“已证明全部变体预热”的判据。** 客户端原配置 `num_warmups=0`，只附初始单prompt test；2/2047、16/2048变体在主负载中才首次选中。FIRST本身不区分磁盘cache命中与fresh编译，也没有编译时长证据，因此既不能断言回归全由冷编译造成，也不能把本结果称为完全预热后稳态kernel退化。保留这一限制，不新增GPU窗口或改参数来改写负结果。

三端首次shutdown前均无ERROR。候选正常完成benchmark后，shutdown有forcekill及8行EngineDeadError/traceback，原件完整保留；这属于结束阶段，不能写成全日志无error。root完整postflight于19:10:00.366683Z确认68MiB/0%、两栈9031关闭、413源无漂移。结论为服务完成及真实启用通过、首次短筛负面、准确率未测；保持小层prototype和全部失败/负结果，不提升到默认实现。
