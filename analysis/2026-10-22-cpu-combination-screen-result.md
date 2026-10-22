# CPU metadata + async token：单轮真实服务短筛

**同KV、同DB的本轮组合吞吐小正信号保留：total tok/s +0.698643%，平均TTFT −0.125003%。** 这是一次固定顺序 baseline→combined 的短筛，不是稳定因果、官方成绩或新的整模型准确率结果。

| 实际结果 | A：070004 baseline | B：070452 combined |
| --- | ---: | ---: |
| 成功 / 失败 | 64 / 0 | 64 / 0 |
| 输入 / 输出 tokens | 262144 / 8192 | 262144 / 8192 |
| 负载耗时 s | 39.225860193837434 | 38.95371279399842 |
| total tok/s | 6891.780031441377 | 6939.928972358459 |
| 平均TTFT ms | 20088.914546053275 | 20063.802888413193 |
| 实际KV池 tokens | 521936 | 521936 |
| 原preemption计数 | 0→0 | 0→0 |

本轮比率 `TPS_B/TPS_A=1.0069864303122589`；耗时少0.272147399839秒（−0.6937958747%）。两个单项既有短筛百分比不相加，也不能从这对组合结果拆分各项贡献。两 helper 的 `FIRST_SELECTED` 均真实出现在B的EngineCore273944；A无这两个标记。标记表示至少一次选择，不是全负载计数或同一步双命中证明；同链字节/元数据正确性另有062205真实方法门。

## 可比性与原件

两轮保持原 `bc51ac2d…` driver、原SERVER、`--decode-screen --seed 721201`、同一个load命令4096输入目标/128输出/64请求/concurrency64；没有profiler或新增serve参数。完整源码为A410/B412，逐项只差 runner `e155a166…→6f918ae6…` 和两个新增原helper `0e961524…`、`1bb85e31…`；init与其它基点源原字节保留。installed依赖、模型配置及packages相同，结束installed Attention为54c；两轮均单BI-V150物理32GiB、CPU配额6核。

DB四个同方式快照（A前/A后/B前/B后）均523表/19474行，物理`dc2c76463fc6c1ef0674b16ca4374125b3ee4551fa0b1886253093f310b237da`、schema `0dc7a465bf12e53e054381d9e865460e7e4fe70287cc8c3683a41b0a4914ab39`、logical `c05d7e3182d1837929b48d5699c6515786351eb8d22f73eb53227a39fb3c49c8` 全同，实际实体哈希及只读内容指纹已复算。此项不表示主机或Triton缓存所有状态相同，也不能将一次A→B解释为稳定因果。

root首次组合前置检查曾错误比较live SQLite文件与backup快照的物理SHA，CPU检查exit1，**未创建组合run、未启动GPU**。原件`A-control/combined-prelaunch-db-check.json`明确逻辑指纹相同，仅header偏移26/27/42/43/94/95六字节不同。后续改为逻辑指纹并核同方式快照四端；这不是DB内容变化或设备失败，失败记录保留。

A于07:02:04.087931Z、B于07:06:52.883664Z以exit0结束。封存后态分别07:02:34.294531Z、07:07:32.422604Z：68MiB/0%、9031双栈关闭、无GPU进程，server/Engine已消失，两个controller仅剩Z/PPid1，source/live校验均通过。

关停日志完整保留：A无ERROR，含forcekill/资源warning；B在测量完整结束后的abort/forcekill阶段有8条ERROR行组成的`AsyncLLM output_handler`/`EngineDeadError`尾栈，并有资源warning。不能写成B“无ERROR”，也不把关停尾栈改写为这64请求的测量失败。

SCP session14687实际exit0后才读取本地。A/B完整run/control/tgz在`experiments/framework/`，450/451项seal逐byte核同：

- A：`20261022T070004Z-cpu-combination-baseline-decode4k.tgz`，2477555B，SHA `0512d379eca1613e716a0c1314c55b3aa6ccdaf07d670034f31f2ce1f85e5150`。
- B：`20261022T070452Z-cpu-combination-combined-decode4k.tgz`，2480387B，SHA `508f74efc10997b39b7d3166b45bddbb5cce85908d47d0fe807724d8e3aeb764`。

唯一系统后验 `analysis/source/cpu-combination/screen-system-review.json`，SHA `89da4cbe8ae307ed797f2f663d4d247efd5fb3415a857036ccbd56af18e88b1e`，保完整动态字段、三处源码差异、原命令、四端DB、清理和异常分类。仅本地stdlib/hash/原字段与只读SQLite复算，没有重跑旧门或新增测试框架。

## 收口

registry第119/120条及queue第92项已登记。结果仅BI-V150，不代表C500；未做新accuracy或完整官方吞吐，不继承旧103/105，不宣称最终提交资格或默认启用。本轮不自动追加重复pair或大测；代码PR head与合并由root维护，本审计不操作GitHub。现已停写供root一致提交发布。
