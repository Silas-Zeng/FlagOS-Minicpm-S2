> 后续070004/070452单轮真实短pair现也已完成并唯一验收：同KV521936/同DB四端，TPS+0.698643031%、TTFT−0.125002561%，仅小单轮信号；详见 `analysis/2026-10-22-cpu-combination-screen-result.md`。registry120/queue92收口，下方未开始/待结果均为历史计划，不自动继续设备。

> 最新收口：062205真实方法组合门已完成并唯一实际验收通过，见 `analysis/2026-10-22-cpu-combination-062205-result.md`。registry118/queue91已登记，性能和整模型accuracy未测。下文“待最终pin/未有原件”等为实施前计划，不是当前待办，服务/pair未自动启动。

# CPU metadata 与 async token 组合：最短验证的系统计划

## 当前决定与边界

root 已选择比模型服务更短的**真实方法组合正确性门**：hardware 从已验 metadata 门 b124 最小派生 `validate_cpu_combination.py`，在同一个 `_prepare_inputs → _prepare_input_ids` 调用链内执行两项原实现。只跑一个有界 GPU worker，不启动 vLLM 服务、不跑 decode-screen/官方大测或性能 pair。本文件保留下述服务定位供必要时复用，不能据此自动启动。

本次系统 owner 只写计划及另行授权的薄 launcher；不 SSH/GPU、不改正式服务/官方 benchmark/共享代码库，不更新 registry/queue 直到 root 确定并实际完成 run。所有设备由 root 唯一串行启动。四个 Draft 尚未合并，组合没有继承单方法准确率或收益。

## 精确来源与不能直接串接的地方

冻结源码基点为远端历史路径 `/workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z`。这里只读本地旧封存确认路径和身份；部署前 root 仍须重新核实际全部源 SHA，不能把历史路径存在当成当前 live 通过。原 runner e155 与 `main` 70d04/tree82e37 的 runner 相同；新候选目录不得覆盖该树。

| 用途 | 固定 SHA256 |
| --- | --- |
| 原 runner | `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1` |
| 双序合并后的 runner | `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141` |
| CPU metadata runtime | `0e96152454a9197f65a34c2fe8805bd5073e1fa473070d59d4ec4f20a6d8846f` |
| async runtime | `1bb85e31c7b3fefa81414a54b04a1f0b6cf949c0876f87149956c821bb483adc` |
| 原 init（服务方案保留） | `e043b7893bfac27aee4f96cf7201cd6227053a261498e121245c3e63f2f2ebff` |

组合 runner 的本地权威原件为 `docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py`；另见双序冲突/逆撤和可应用补丁 `docs/pr-preparation/combination-review.md`。不是依次对同一 runner 运行两个旧 transformer：两者均要求自己的 exact 原 runner，第二次会拒绝已改源码。新方法门应直接固定原 e155 与组合 6f918，固定两 runtime，不改 source guards。

历史服务隔离树 `/workspace/experiments/minicpm-s2/code/async-token-20261021T174741Z`、`.../cpu-metadata-20261021T175049Z` 各只含单项，不可冒称组合。其本地控制归档各 411 个 regular 文件映射；原 `174402-baseline` 的映射为410。若以后从完整410基点只改 runner、增两个 runtime，则不含额外 manifest 的映射应为412；最终以实际归档 map 为准，不能按数字代替逐项校验。

## 当前最短门的职责分界

hardware 的新门复用 b124 controller：唯一 `framework-device.lock`、idle、一个 device worker、monitor、300秒超时、信号/定向清理、后态及 exit/finished 均由该 controller 负责。系统薄层 `launch_cpu_combination_gate.py` 仅固定输入 SHA、创建独立 UTC control、保存命令/环境、DB-before、同步调用 controller、DB-after 与源码/封存结果。**不再持第二把设备锁或另起 GPU owner**；DB 快照位于 controller 锁外，依赖 root 当前唯一串行调度，不宣称该外层快照原子受锁保护。失败原件/exit 必须保留。

已与 hardware 对齐 CLI：

```text
python3 validate_cpu_combination.py --run-dir RUN \
  --runtime-path ROOT/scripts/biv150_cpu_metadata.py \
  --async-runtime-path ROOT/scripts/biv150_async_token_update.py \
  --runner-path ROOT/code/sql-mixed-20261021T080656Z/vllm_fl/worker/model_runner.py \
  --candidate-runner-path ROOT/scripts/cpu-combination-model_runner.py
```

这里 ROOT=`/workspace/experiments/minicpm-s2`。此为接口方案，不是已执行命令。source 归档原/组合 runner、两 runtime、gate 与实际 `utils.py`/`gpu_input_batch.py`/`block_table.py`/owner/monitor，不拷整套服务插件。只复用真实方法与实际 buffer/block-table 类，runner/config/InputBatch 部分为 fixture，不是完整模型或真实请求调度。

必要后验是：组合调用链两个 helper 都实际选择；原方法与组合在相同合法输入、原 event 保护下的输入 IDs/positions/seq/computed/slot/CPU镜像和返回结果一致，连续改 host 值/固定地址 consumer 及非支持条件回退检查如实记录，RNG 不变。helper 首次标记只能证明至少一次选择，不是完整覆盖计数。不得用各旧门分别通过替代同链实际组合，也不能把两处 CPU 静态 AST 相同说成 GPU 正确性。

原 metadata fixture 的 model 缺 `is_encoder_decoder`，而 async scope 直接读此字段；已告 hardware 必须按合法模型值 False 补齐 fixture。它已有反序 prev 映射，可触发非 identity 的 async 更新。新 fixture/计数实际覆盖由 hardware 最终稿和原件决定，本方案不提前写通过。

## 现成服务入口的精确定位（目前不执行）

`launch_small_framework_screen.sh` SHA `d259b7c04dd4a105bdfa1e6755a8416ee23b6d4c25f6e86b9dfd845a34d693d4` 目前只接受 `baseline|async-token|cpu-metadata`，没有组合 variant。原 driver `run_framework_screen.py` SHA `bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9`；load helper SHA `621dedfc11ce21d35bdcffc9918ab4ac8bf63adc0e277fe7c2117e5f7e4ec378`；sealer SHA `eab7f787b321e2755f8f511622de440e6c15e73dbac6b280fa69e815f385dca9`。复用的是锁/生命周期和原命令，不能直接以旧 launcher 参数伪启组合。

原 SERVER 必须逐项保持：

```bash
vllm serve /workspace/MiniCPM5-2B --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm --gpu-memory-utilization 0.85 --max-model-len 131072
```

原 driver 的 `--smoke-only` 发单条 prompt `Explain what an inference engine does.`，temperature0/seed71/max_tokens32，加 logprobs2/return_token_ids；顺序重复最多4次仍非并发。e155 `_prepare_input_ids` 1857–1868 的 unchanged identity 分支会直接 slice-copy 返回，绕过新 gather/scatter。因而单条成功不能证明 async 组合真命中，不能只看安装标记或一段文字判通过。

若未来确需最短**已知真实服务覆盖**，现成可复用 `--decode-screen --seed 721201 --require-log-marker BIV150_SQL_REFLECTION_INSTALLED`。它先发原单条 smoke，然后仅一份4096输入目标/128输出/64请求/concurrency64负载，helper 实际参数为 `decode-4k 4096 128 64 64 721201`。174741与175049单项原件均真实 FIRST_SELECTED，负载约39秒；完整启动至退出约119秒，并非“总共39秒”。该负载只是已有覆盖证据最充分的现成选项，不声称64是理论最小请求数。

服务通过只能写“真实接入、两个 helper 至少选择一次、请求全部完成、无运行时失败、source/DB/post证据齐”，不是完整准确率。正常 benchmark 不请求逐 token IDs/metadata 全量，不能假设已有逐字节输出或 RNG 证明；原 seeded smoke 的历史文字也并非两候选与基线完全相同，不能用文字样例证明 token 恒等。输入/输出实际 totals 读 raw usage；旧64请求为262144/8192，不从目标输入长度直接证明逐请求 retokenize 后同长。`--require-log-marker` 是启动前安装预检，两个 FIRST_SELECTED 应在负载结束后另外检查。

## 只有未来明确需要收益时的短 pair 边界

当前不排 pair。若方法门通过、root另行决定需要收益证据，才用冻结同410源基点的 baseline 与同一组合版本，串行相同 bc51/原 SERVER/原 decode helper/seed721201，均先跑同一 smoke，不 profiler、不改采样/serve参数、不叠 KV 协议/观察器或任何别的优化。

必须同时满足原 packages/installed Attention54c 与其它依赖、单BI-V150物理32GiB、CPU6配额及线程/host负载、driver/helper、模型/原命令/请求数/tokens、基点与仅两方法差分均一致。实际 KV池 tokens 必须相同；同物理32GiB不意味着KV相同，旧6blocks/96tokens启动波动不能忽略。DB `/root/.flaggems/config_cache/TunedConfig_iluvatar_triton_3_6.db` 的物理snapshot/schema/logical三SHA应 `A_before=A_after=B_before=B_after`；不清库/不倒灌/不为凑KV刷启动。记录BIV150 CPU分项时须双方同观察器；不临时只给一侧增加观察器而污染源和内存。

DB或KV或参数任一不满足即保留原件、收益null/不可归因；不看TPS择优。满足也只给该轮描述比率 `TPS_B/TPS_A-1`、`TTFT_B/TTFT_A-1`，不自动稳定因果、不把两个单项百分比相加、不算比赛总分、不继承原103/105。正确性失败不启用，负例仍保留。无需因本方案自动追加完整官方大测/重复长pair。

旧 sealer 可复用 source/live/54c/DB-after/两个 FIRST_SELECTED 的只读取证，但它要求exit0、没有替失败run封存；新任务仍须保留失败/清理证据。controller退出后再取后态，68MiB/0%、GPU空进程表、9031双栈关闭、owned进程消失或明确Z，不能把shutdown尾ERROR与测量阶段故障混写。

本文件仅来源阅读和计划；新 gate 尚待最终 pin/真实原件，registry/queue保持117/90不动。当前以root选择的方法门为准，以上服务与pair均不是已授权启动项。


## 后续单轮短服务pair已另行授权：0519静态终审

root在062205通过后另行决定只跑一对原bc51 decode短筛；framework拥有`launch_cpu_combination_screen.sh`（0519e554…）及完整基点map `cpu-combination-base-sha256.json`（cd506fa2…）。本owner只做定向diff，embedded Python AST/compile，不执行副本/旧门或服务；map逐byte原174402完整410，新baseline410/combined412只替runner6f918并增加两个原helper。其余init/所有基点字节及原decode-screen/seed721201/SQL安装预检/唯一driver启动不变。双栈预检、完整source/live/归档map与合法内部file alias解引用均已审，无本轮阻断。静态回执`analysis/source/cpu-combination/screen-launcher-system-review.json`。

结束原样调用`python3 /workspace/experiments/minicpm-s2/scripts/seal_framework_screen.py <RID>`，脚本eab7f787补DB-after/live-source/installed54c/双栈68-0空进程与ownedPID消失或Z/选择标记；它只收成功exit0，不自动tar/全目录seal，root复用原收集命令即可。launcher不自动保证paired身份，root须先核A前后=B前DB三hash，最终核B后及实际同KV；后验不匹配只记null收益，不凑容量/看TPS择优，不新大accuracy或重复062205。此段覆盖上文“当前不排pair”，并未声称已有run或结果；registry/queue暂不新增。
