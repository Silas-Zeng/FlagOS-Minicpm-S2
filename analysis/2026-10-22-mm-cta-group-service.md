# gate-up CTA group8：严格服务入口与最短匹配验证

2026-10-22，hardware_innovation。本文只适用天数 BI-V150，沐曦－曦云 C500 由队友验证。设备始终由root单任务串行持有，本owner只在本地CPU准备。此项不与prefix-mask、metadata、async或mapped Attention候选混合。

## 设备依据及保留的负结果

原173921门因高级索引guard oracle失败停止，原件不改。180033诊断发现初始化尚未JIT时`storage[[0,-1]]`已读错，但七阶段正数basic D2H CPU guard bits全正确未变；不定位Torch/FlagGems具体责任。正式门b216改为正数basic CPU int16判据，原数学和32call预record Event ABBA未改。

root已串行完成`experiments/framework/20261021T180646Z-mm-cta-group-cpu-guard-gate`，exit0。本owner实际读results并核全部source SHA匹配；两shape完整bits/finite/inputs/RNG、八阶段guard和计时后检查均true。这里只是固定tile合成矩阵门，不是模型accuracy或服务收益。

| 形状 | baseline wall ms | group8 wall ms | wall变化 | baseline Event ms | group8 Event ms |
|---|---:|---:|---:|---:|---:|
| gate-up M2048/N12288/K2048 | 1.4179341875 | 1.1885717656249999 | 快16.1758% | 1.4043543934822083 | 1.174988865852356 |
| down M2048/N2048/K6144 | 0.735825265625 | 0.763840109375 | **慢3.8073%** | 0.7219997048377991 | 0.7500479817390442 |

down负结果完整保留，**服务候选绝不选择down**。单次ABBA没有误差区间，不外推E2E百分比。gate-up两binary均97regs/0spills/65536B shared，baseline hash3639b8c97b8a4342970c3964dbabb29a1242f519fa9ad59761253a59d4346b5a、group8 hash08afb5451fca98d698022dd9770db694d9e3786dbf3e4215e1a660a8b8e8305f。

## 实际调用入口和当前配置约束

actual Iluvatar mm4c2e的`mm`和`mm_out`经`_launch_mm`查询同模块globals中的`mm_kernel`。FlagGems先用SpecOpRegistrar把vendor函数放入公开namespace，`_FULL_CONFIG`保存实际函数对象，GeneralOpRegistrar再注册给aten。修改`flag_gems.mm`这个名字不能保证已注册函数跟着变化，因此候选保留注册函数，**只在其真实globals所属alias模块给mm_kernel加代理**。从`flag_gems.mm.__module__`查真实模块，避免另import一个同文件但未被dispatcher使用的canonical别名。

安装前实际核mm/mm_out globals、模块源SHA、公开函数及FULL_CONFIG对象identity，并要求FlagGems实际注册了mm；没有重新注册aten，也不改installed文件。严格模型为原config596、BF16 MiniCPM5-2B、2048/6144/42/16/2、单卡并行、无量化/spec/LoRA/MM/连接器/KVsharing、FULL_DECODE_ONLY。每次执行前仍检查跨层共享状态。

候选只有`(M,N,K)=(2048,12288,2048)`，A stride(2048,1)、B stride(1,2048)、out stride(12288,1)，三块storage分离、同device0 BF16、指针16字节对齐。其余包括down、其它M/stride/dtype、capture均走原LibEntry。ContextVar只在已审模型的`execute_model`和`_dummy_run`内启用，异常时finally reset；其它模型或作用域外调用原路。

使用exact LibEntry414e的key方法、原参数序重建实际cache key。只有已热entry的完整launch/TUNE/HEUR/prehook与**BM256/BN256/BK32/SK1、w16/s2/ctas1、EVEN_K true、所有UPGRADE false、无prehook**完全相同，且实际grid为(384,1)，才调用group8。cache miss先执行原路一次，让原调优/DB选C0；不强行覆盖当前best配置、不重新autotune、不改变原DB。entry清空、改变或C0不匹配都回原路。原source、LibEntry、Triton init和原JIT签名/特殊化规则均锁SHA/结构。

新kernel仍用06c7 policy实际变换，生成的30d0f046…逐byte等于受测group8，唯一实现变化是整数CTA PID映射；K循环/dot/归约/accumulator/原store全不动。编译结果按原cache key持有，**不持有任次A/B/C**；每次热调用按actual3.6 ABI传当前26实参，不能复用设备门`prepare`里捕获首批tensor的闭包。

## 文件、CPU合同与独立审阅

| 文件 | SHA256 |
|---|---|
| patches/framework/biv150_mm_cta_group_service.py | 44fc8e5c887340f245332635a245690946de38f201678b07212137d4c8a716f7 |
| patches/framework/biv150_mm_cta_group_service_source.py | 4ab31a9cb864af75be8ad891902b1433cf1bb007a05e18bbbc4310b6aa37016d |
| patches/framework/biv150_mm_cta_group.py（既有policy，未改） | 06c7cd9216907886e7d66a81d4fd5d9f78edef9daac2380ca263ce8c1770b8e1 |
| scripts/remote/prepare_mm_cta_group_source.py | e007cccf21f20ac3130cf1c0f414189ad4ea45687bac7167e3f8a29e68ff4a2c |
| 复用prepare_innovation_source.py helper（未改） | 0ecf7dc7536afddd853887ddc412b5f6ee330c7efa90ebd9e6904423501364ca |
| 派生runner | 787665d3cf6dabc1afc2bdf7069fab4802fd5f6bfb0baedd119229b5b8ce1775 |

必要CPU合同只做一次，`analysis/source/mm-cta-group/service-cpu-check.json`保留结果：完整e155前缀不变/逆去footer回原件、漂移拒绝、派生compile；提取真实LibEntry.key而不导入其模块，fake pointer/launcher两次调用验证hot使用第二批当前A/B/C，cachemiss/C0变化/capture/作用域外/tuplegrid回原路，ContextVar还原。它不是Torch/设备、浮点或stream证明。

`service-package-check.json`保存一次真实归档源码的本地打包：输入213文件（其中base-revision为归档额外文件）、输出215文件，只有runner footer改变和新增policy/runtime两个文件；其它逐项SHA相同、现有output拒绝。没有修改协作代码库工作树、原080656或installed文件。脚本和新runtime/source py_compile通过，builder --help通过。systems_innovation全文独立只读审44fc/4ab和e007均无当前阻断，未重复suite或设备工作。

## 提交启用、每PID证明与最短服务pair

新source变换只给exact e155 runner末尾SQL→C2→C3之后追加install footer。安装包装原init，原init返回后装代理，在load/capture前完成；不改原方法体、参数、返回行顺序、模型、请求/采样/RNG。提交时必须包含派生runner footer、policy和service runtime，单独上传分析报告不会启用优化。

`BIV150_MM_CTA_ARTIFACTS`必须指向本次`/workspace/experiments/minicpm-s2`下的目录；进程内各建唯一`pid-*`子目录，保存actual module alias、源/派生源码、policy/runtime/LibEntry、源码SHA与状态。READY证明安装；FIRST_SELECTED记录实际C0、编译hash/resources；**REAL_SELECTED必须来自真实execute_model中的selected增量**，不能只拿dummy预热的FIRST作生效证据。首次真实记录含CPU scheduler总token/请求数/最大单请求预算；shutdown/atexit尽量刷最终计数，若服务TERM没有执行它们，不能把旧status计数当最终总数。

root上传上表三个新素材和builder，复用原helper；纯CPU准备命令为：

```bash
root=/workspace/experiments/minicpm-s2
python3 "$root/scripts/prepare_mm_cta_group_source.py" \
  --base-source "$root/code/sql-mixed-20261021T080656Z" \
  --output "$root/code/mm-cta-gateup-<唯一UTC>" --asset-dir "$root/scripts"
```

原helper和builder会拒绝复用输出、叠加其它候选或素材SHA漂移。新副本的innovation-source.json含全部输入/输出及唯一三项差异，供root归档。

最短匹配服务pair建议复用已有`run_framework_screen.py --context-screen --seed 721201`：16K、32请求、128输出、concurrency64，原服务参数全部保持；这是短筛，不是官方计分。baseline仍原080656，candidate用上方隔离副本，同热DB快照/实际C0/KV容量、同请求seed/运行参数，串行执行，分别唯一UTC run/control；prefix-cache预热不能复用测量prompt。新kernel若已在startup dummy中FIRST_SELECTED并编译成功，则记录该时刻早于测量；否则需测量外真实形状预热，冷窗口另记，不能和热baseline因果比较。

每次候选在root自有control内设置环境并调用原driver，例如：

```bash
export BIV150_MM_CTA_ARTIFACTS="$control/mm-cta-artifacts"
python3 "$root/scripts/run_framework_screen.py" "$run" \
  --source-dir "$candidate" --context-screen --seed 721201 \
  --require-log-marker BIV150_MM_CTA_GROUP_READY
```

root现有外层launcher继续负责PID/stdout、唯一设备锁、DB before/after、pre/postflight和清理；不创建第二个服务。测后查真实benchmark期间REAL_SELECTED、完成数/token数、DB实际C0及原CSV/log，FIRST只dummy或REAL为0则判未启用，不能报性能收益。服务小/零/负结果都保留。原103/105不自动覆盖新入口，后续必要accuracy/reproducibility门由root安排。

## 182916 实际服务与编译缓存审计

root已完成 `20261021T182916Z-mm-cta-group-context16k`：32/0、118.41752643秒、KV521840，DB三项SHA不变。原件及control已本地归档，包SHA `96074323f386817d460bdefd0982c44ba5f58c3f760c07c0e81604364215ccac`。本owner核413份source SHA及每PID产物匹配；真实 `REAL_SELECTED delta42,total2048,requests1` 证明目标执行命中，group8编译hash与设备门同为08afb545…。status是首次真实命中快照，不能当最终总计；本文不凭单次时长声称E2E收益。

服务原compiled23d5fd…与门原3639b8…的差异已由实际cache逐层审计：编译参数相同，所有加载段和8,016-byte `.text` 完全相同，只调试段不同；实际spec JIT将源码起始行纳入cache key。完整证据、32文件SHA校验、可复核stdlib脚本及边界见 `analysis/2026-10-22-mm-cta-compile-cache.md`。未扩大scope或重新上卡。
