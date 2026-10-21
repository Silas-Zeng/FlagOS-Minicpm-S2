# 候选安装与验证

本文的候选、补丁和全部已测数据仅适用于**天数 BI-V150**。
团队总仓库同时包含沐曦－曦云 C500 的协作工作，该平台由队友负责；本文不提供 C500 的安装或性能结论。
双平台分工与仓库入口见 [README](../README.md)。
只有实验分析库按平台分别记录环境、证据和报告；`FlagOS-S2-vllm-plugin-FL` 与 `FlagGems` 是团队共用的私有代码库，不要求按平台拆分目录或分支。

## 天数 BI-V150 的 SQL+C3 候选：一份完整补丁

团队审阅与复现请使用
[`vllm-plugin-FL-biv150-sql-mixed-decode-full.patch`](../patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch)，
在原始 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` 上仅应用一次。
其 SHA256 为 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`。
完整补丁已包含保留的 prefill/top-p、SQL 反射、decode launch 和 mixed-decode 改动，
不要再叠加下文任何历史增量。

使用比赛固定镜像和新建的实验 checkout。下例只读取原始参考 checkout，所有写入均发生在新 checkout；
`/workspace/minicpm-sql-c3` 必须是新目标目录。

每次复现都须先确认原版基线结束并释放设备，或使用独立、干净的复现环境，再安装并启动候选服务。
保留运行时在导入时会持久改写已安装的 Attention；仅切换插件 checkout 不能恢复原始依赖。
原版基线 Attention 应为 `bab2c0b9...`，候选使用 `54c495dc...`。
完整哈希和恢复流程见[依赖隔离记录](../analysis/2026-10-21-original-baseline-dependency-plan.md)。
测量原版基线期间禁止导入候选平台模块。

```bash
git clone --no-hardlinks /workspace/vllm-plugin-FL /workspace/minicpm-sql-c3
git -C /workspace/minicpm-sql-c3 checkout --detach 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
sha256sum /path/to/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch
git -C /workspace/minicpm-sql-c3 apply --check /path/to/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch
git -C /workspace/minicpm-sql-c3 apply /path/to/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch
python3 -m pip install --no-build-isolation --no-deps /workspace/minicpm-sql-c3
```

重建源码已与受测候选归档中的全部 212 个仓库文件独立核对。
完整补丁应用后的 Git tree 为 `5c14cfb8d3a452e97a67758873bf18039e1bf989`。
runner SHA 为 `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`；
各模块哈希、文件模式和逆向应用检查见[完整补丁记录](../analysis/2026-10-21-sql-mixed-full-package.md)。
使用下文的[官方服务命令](#official-serving-command)，再分别进行[准确率](#accuracy)与[性能](#performance)验证。
保留日志，同时检查候选安装/启动标记及实际安装源码身份：

```text
BIV150_SQL_REFLECTION_INSTALLED
BIV150_DECODE_LAUNCH_FIRST_SELECTED
BIV150_MIXED_DECODE_INSTALLED
```

mixed 标记只证明已安装，不证明每个 batch 都分流；
是否选中还取决于自然前缀形状守卫。正确性与吞吐结论以保存的验证和完整实验为准。

该候选已按官方准确率要求通过 103/105，并完成两档各四轮官方吞吐测试。
原始 `13eb9be` 的完整官方对照也已结束并验收，按原第 2–4 轮均值，4K / 16K 总吞吐分别为原版的 1.933208 / 3.166027 倍。
实际 KV 容量和调优数据库初始状态不同，不能称缓存完全匹配或稳定因果收益，也未计算官方总分。
完整数字与封存说明见下文、[比较说明](official-comparison.md)及[技术报告](technical-report.md)；独立团队复现与最终提交选择仍是后续工作。
仓库中较早的默认补丁单独保留，没有被此候选覆盖。

## 历史保留补丁与独立增量

以下各节记录较早的默认方案和独立实验，安装流程是复现各历史实验的不同选项，
不是在上述完整 SQL+C3 补丁之后继续执行的步骤。
独立增量的结果不能自动用于另一种组合；文中的历史“待验证”不覆盖上文 SQL+C3 已完成的验证。

历史补丁基于：

```text
vllm-plugin-FL: flagos-2026-s2
基础提交: 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
vLLM: 0.24.0+empty
FlagGems: v5.3.5
```

按当时的流程应用插件补丁。下例中的 `vllm-plugin-FL` 应是新建、可写的复现实验 checkout，
不能直接改写只读参考仓库：

```bash
git -C vllm-plugin-FL checkout 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
git -C vllm-plugin-FL am /path/to/vllm-plugin-FL-biv150-performance.patch
pip install --no-build-isolation ./vllm-plugin-FL
```

补丁引入的运行时安装逻辑可重复调用；Git 补丁本身仍只应用一次。
它安装两项按形状启用的策略：

- 通用 `TRITON_ATTN` prefill：`BM128 / KV tile64 / 8 warps / 1 stage`。
- 针对 130,560 词表的 top-p-only 采样：使用确定性的单程序、两轮加权直方图 kernel。

被否决的 A+B 候选在此基础上增加了更快的 decode tile 策略，保留在 `patches/candidates/` 供比较。
其组织方准确率结果为 83.8%，不得用于最终提交。

融合 top-p/Gumbel sampler 也作为独立候选保留。其独立采样尾部快 2.38 倍，
但服务短测中 16K 改善、4K 回退，因此没有启用到默认补丁。
这个历史增量接在当时保留的插件补丁之后，不与本页完整 SQL+C3 补丁叠加。

另有两个独立实验增量：

- `patches/candidates/vllm-plugin-FL-biv150-decode-launch.patch` 接在保留 performance 补丁之后，
  只将已审计 BF16 3D decode 的启动配置改为 2 warps / 1 stage。
  单层输出验证通过；首次匹配服务对照只有尚未确认的小信号，不是官方成绩。
- `patches/candidates/vllm-plugin-FL-biv150-mixed-decode.patch` 接在 decode-launch 增量之后，
  只在 Attention 内拆分天然连续的单 token 前缀。真实 backend/metadata 验证通过；
  decode 归约与原 mixed 2D 路径不同，因此在当时需要单独准确率验证。

以上是两个独立实验当时的状态，均未加入较早的默认提交补丁。
后续 SQL+C3 联合版已经完成其自身 103/105 准确率验证，不能再把早期“待准确率”误读为当前联合版未验证。
当前服务结果、源码身份与设备归属见 [`CURRENT_WORK.md`](../CURRENT_WORK.md)。
这两个增量本身不写已安装的 vLLM 源码，并以严格源码哈希拒绝未审计依赖；
其前置保留运行时的 Attention 改写行为仍须遵守本页开头的隔离要求。

## SQL 反射框架候选

独立增量
[`vllm-plugin-FL-biv150-sql-reflection.patch`](../patches/candidates/vllm-plugin-FL-biv150-sql-reflection.patch)
直接接在保留 performance 补丁之后，即 `d60b02367a852826f653165953f31b6dc696658e` 所代表的 tree。
它增加已审阅模块和 runner 末尾三行安装代码。在独立实验 checkout 中应用，然后安装该 checkout：

```bash
# 先按上文应用 vllm-plugin-FL-biv150-performance.patch。
git -C vllm-plugin-FL apply --check /path/to/vllm-plugin-FL-biv150-sql-reflection.patch
git -C vllm-plugin-FL apply /path/to/vllm-plugin-FL-biv150-sql-reflection.patch
pip install --no-build-isolation ./vllm-plugin-FL
```

它在 Iluvatar 上自动启用，不增加服务参数或启用环境变量。
启动标记为 `BIV150_SQL_REFLECTION_INSTALLED sqlite_targeted_only=1`。
替换静态反射方法前，会校验已安装 `flag_gems.utils.models.sql` 字节的 SHA256：
`6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7`；
未审计版本直接报错。SQLite 反射只加载请求的配置表，避免映射全部无关表；
其它数据库引擎和平台保留原路径。
配置键、缓存值、数据库行、模型缓存及调优决策不变，不对缺失表做负缓存。

CPU 验证使用 SQLAlchemy 2.0.43 并已通过。
文档中的
[`reflection_options`](https://docs.sqlalchemy.org/en/20/orm/extensions/automap.html#sqlalchemy.ext.automap.AutomapBase.prepare)
API 从 1.4 起可用，但这不意味着可以升级比赛固定环境。
可调用的
[`only` 过滤器](https://docs.sqlalchemy.org/en/20/core/metadata.html#sqlalchemy.schema.MetaData.reflect)
筛选已存在的表，保留缺失表返回 `None` 的行为；直接传入包含缺失名称的列表会报错。
默认外键依赖反射仍启用。Automap 仍要求主键；此候选针对 FlagGems 配置表，
不承诺对任意 ORM 关系图都完全等价。

这个独立增量不依赖 decode-launch、mixed-decode 或融合 sampler；首次 SQL 短测只启用它。
较早的默认 `vllm-plugin-FL-biv150-performance.patch` 没有改动。
独立 SQL 增量在当时只有 CPU 等价检查和短测，它们不是新的准确率结果或官方分数；
后续联合版的准确率结果只属于对应组合。源码、测试与范围见
[SQL 反射计划](../analysis/2026-10-21-sql-reflection-plan.md)。

SQL + decode-launch 联合候选为
[`vllm-plugin-FL-biv150-sql-decode.patch`](../patches/candidates/vllm-plugin-FL-biv150-sql-decode.patch)。
在新的实验 checkout 中，将它直接应用到保留 performance 补丁之后（`d60b023`）。
不要先叠加独立 SQL 和 decode-launch 增量，因为它们的 runner 末尾上下文重叠：

```bash
git -C vllm-plugin-FL apply --check /path/to/vllm-plugin-FL-biv150-sql-decode.patch
git -C vllm-plugin-FL apply /path/to/vllm-plugin-FL-biv150-sql-decode.patch
```

安装顺序为先 SQL、再 decode launch，与 `20261021T073309Z` 短测的模块及 runner 哈希相同。
该组合的准确率已完成：101/105（96.19%）；本页没有记录该 SQL+C2 组合的完整两档官方吞吐结果。
较早的默认 performance 补丁保持不变。

另一个三部分联合候选为
[`vllm-plugin-FL-biv150-sql-mixed-decode.patch`](../patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode.patch)。
它同样直接接在保留 `d60b023` 之后，用它替代上一份 SQL + decode-launch 联合增量。
它按 SQL、decode-launch、mixed 的安装顺序，复现 `20261021T080656Z` 的模块与 runner 字节。

其 mixed 归约改动已在独立 `20261021T090505Z` 官方准确率验证中通过：
103/105（98.10%），105 个请求成功、0 错误、105 个正常 stop 结束、0 个触及 token 上限。
全部 228 个归档源码哈希已核对，核心模块与 runner 字节均匹配 `20261021T080656Z`。
这一次使用随机采样；103/105 高于 SQL + decode 的 101/105，不代表模型质量提高。

官方两档、每档四轮的 `20261021T092944Z-sql-mixed-official` 已完成，
官方脚本与服务参数未改。8 条原始行、2 条汇总行及 230 个归档源码哈希全部核验。
原版 `20261021T122607Z-original-baseline` 现已完整结束，225 项归档源码及对应 live 源码、原始 8 条 raw / 2 条 summary 均通过验收。
按原脚本丢弃首轮，对每档原第 2–4 轮相应指标取算术均值：

| 输入 / 输出 token | 并发 / 请求数 | 原版耗时 s | 候选耗时 s | 原版 total tok/s | 候选 total tok/s | 吞吐比 / 变化 |
|---|---|---:|---:|---:|---:|---:|
| 4096 / 1024 | 64 / 256 | 687.94 | 355.88 | 1905.46 | 3683.65 | 1.933208× / +93.3208% |
| 16384 / 1024 | 64 / 128 | 2584.99 | 816.48 | 861.99 | 2729.07 | 3.166027× / +216.6027% |

| 输入 / 输出 token | 原版 Mean TTFT ms | 候选 Mean TTFT ms | Mean TTFT 变化 |
|---|---:|---:|---:|
| 4096 / 1024 | 12310.56 | 4781.64 | −61.1582% |
| 16384 / 1024 | 636429.44 | 185063.65 | −70.9216% |

绝对值显示到两位小数；比例按未再次舍入的 raw 均值计算，TTFT 负变化表示延迟降低。
真实 KV 容量为原版 521840、候选 521936 tokens；DB 表数 / 行数分别为原版 `512 / 19130 → 516 / 19270`，候选 `489 / 18384 → 501 / 18789`。
两边实际 SQLite 的物理、schema、逻辑 SHA 已重算，初始库不同，未清空或人为统一缓存。因此这是分档描述性比较，不是 cache-matched 或稳定因果结论，不合成跨档倍数或官方总分。
原始数据见[原版汇总 CSV](../experiments/official/20261021T122607Z-original-baseline/benchmark_results/summary_20261021_202847.csv)、[候选汇总 CSV](../experiments/official/20261021T092944Z-sql-mixed-official/benchmark_results/summary_20261021_173039.csv)；
完整精度、DB 指纹与比较门见[最终比较 JSON](../analysis/2026-10-21-official-final-comparison.json)，SHA256 `52f8da4bea6ba7caf4f517edccb9c3c0ecbe85db89f79372b0e5c1c4fc74d832`。

原版 benchmark 和服务均返回 0，原结果的 `cleanup_errors=[]`；结束后 9031 的 IPv4/IPv6 均关闭，设备无进程、68 MiB / 0%。
runner `166637` 已退出但保留 `Z (zombie)` / `PPid=1` 表项，PID 1 尚未回收。首次封存仅因末尾要求 `/proc` 项不存在而断言失败，失败原件与[后续状态说明](../experiments/official/20261021T122607Z-original-baseline/postflight-process-review.json)均保留；不改写官方原始结果或 CSV。
双方 server 日志仍保留 shutdown 时清理 1 个剩余进程的警告，monitor 清理返回 −15，不把该状态说成完全无告警或仍在进行设备实验。
默认 performance 补丁没有覆盖；SQL+C3，以及较新的 token-bucket、输出增长准入、
hidden-row gather 创新均未启用到该默认补丁。

Attention 策略只在以下条件启用：

```text
Iluvatar 平台
头维度 128
16 个查询头 / 2 个 KV 头（GQA 倍率 8）
```

sampler 策略仅适用于 MiniCPM5-2B 词表、FP32 logits 的 top-p-only 情况。
其它路径保留上游实现。

<a id="official-serving-command"></a>

## 官方服务命令

```bash
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode": "FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072
```

<a id="accuracy"></a>

## 准确率

使用 [`official-verification.md`](official-verification.md) 记录的准确组织方命令。
最终验证须保留指定 endpoint、Level 3 子集、`temperature=1.0`、
`top_p=0.95` 和 `max_tokens=32768`。

<a id="performance"></a>

## 性能

使用未修改的官方 benchmark：

```bash
cd /workspace
python3 /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py \
  --model /workspace/MiniCPM5-2B \
  --served-model-name minicpm \
  --port 9031 \
  --test-cases '[[4096,1024,64,256],[16384,1024,64,128]]'
```

不能把复用相同 seed 的短诊断当比赛分数：prefix caching 曾使暖运行耗时降低超过 70%。

### 历史 SQL 与 decode 联合候选补充

`patches/candidates/vllm-plugin-FL-biv150-sql-decode.patch` 是直接接在保留 performance 补丁
（等价于 d60）之后的一份增量，不要先应用独立 SQL 或 decode 增量。
其 SQL/C2 模块及 runner 字节与真实 `20261021T073309Z-sql-decode-screen` 源码相同，
安装顺序也是先 SQL、后 decode。
它在 `20261021T073644Z-sql-decode-level3` 官方 Level 3 准确率中通过 101/105（96.19%），
105 次评测成功、请求错误为零。其 4K 短筛耗时 41.154s，同负载保留控制组为 120.471s；
组合多 96 个 KV token（521936 对 521840）。因此这是记录了容量差异的诊断证据，不是官方吞吐分数。

较早默认 performance 补丁继续保留。
再增加独立 mixed-decode 增量会成为不同候选：其 39.160s 短筛在当时不能继承此 101/105 准确率通过。
后来 SQL+C3 已完成自身 `20261021T090505Z` 的 103/105 准确率与 `20261021T092944Z` 的完整官方吞吐，
见上文；这些后续结果不改写当时的原始实验。
