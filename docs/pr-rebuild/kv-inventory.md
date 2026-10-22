# KV、算子与实验代码：从原始框架重建PR的简表

2026-10-22；仅CPU只读盘点，不改共享checkout／远端／受测代码，不跑测试或设备。按用户新要求，**框架main应回到原始13eb，旧SQL+C3完整导入只作为历史快照保存**；本文件是迁移建议，不声称远端已完成恢复。历史manifest仍保留其原70d04／d5e2基点，不直接改成新的事实。

## 当前PR3、PR4究竟覆盖什么

| 方法 | 现有材料与精确实现 | 实际依赖／验证边界 |
|---|---|---|
| PR3：连续页合并复制 | `docs/pr-preparation/kv-contiguous-copy/`；新增`vllm_fl/patches/biv150_kv_page_copy.py`，原字节c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c；另中文doc | 仅stdlib dataclasses，无SQL／C2／C3／CPU两方法依赖。191545四构造case，每向672MiB完整字节／guard过；不是服务集成或吞吐收益。 |
| PR4：正等差二维SAVE | `docs/pr-preparation/kv-pitched-copy/`；Python818e788b282ba51017239fd9c505f9709c219a16024d4d56d1df750d3a61b4cd、C++0a4d44d8bd71488f57d5adaa7bdc80f8b16193b11884c167b8767b9e7d9c6d44；另中文doc | Python只用ctypes／dataclasses／hashlib／pathlib／sys，**不import PR3**；C++另需实际Corex SDK编译，不附SO／不改setup／不默认加载。035754同桥线性→二维单层热wall约3.62%信号；042225真实42层保存／恢复字节门过，不是E2E性能。 |

本轮实际只读`git ls-tree -r 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0 --`核上述三个代码路径及两个docs路径，均不存在；因此两项可分别以原13eb为共同base，任意先后，无需虚构SQL+C3或PR3→PR4依赖。现有PR材料的旧manifest不能充当新base验收；root重建分支时另产新tree／diff回执。两PR均**不包含worker、事务、allocator／scheduler、默认hook、准确率结论或失败Event实验**。

## 其余实际开发代码与状态

下表按独立机制归组；同名`*_source.py`／footer是隔离源码包装，不是另一项优化。路径均相对实验记录库，未列为现有PR覆盖的不能说已经入PR。

| 方法／文件族 | PR3/4覆盖 | 证据及重建建议 |
|---|---|---|
| 保留prefill：`patches/plugin/biv150_runtime.py`及platform／iluvatar接入；top-p：`patches/plugin/biv150_top_p_triton.py`、`patches/runtime/`副本；原完整performance.patch | 否 | 原导入五方法中的两个，交framework按历史字节拆PR；prefill会改已安装Attention源码，隔离／恢复依赖风险须保留。不能把组合103/105分给单项。 |
| C2：`patches/framework/biv150_decode_launch{,_runtime}.py`／footer；C3：`biv150_mixed_decode.py` | 否 | 原导入中的两个方法，另有SQL由framework拆；C2真数值门、C3真实层门及组合accuracy边界各自保留。新PR安装顺序和实际基点须重新说明，不能重复全包。 |
| KV基本事务：`biv150_kv_transaction.py`／`biv150_kv_worker.py`／`biv150_kv_protocol.py` | 否 | 200957先SAVE后DROP、没有RESTORE的失败保留；202526暂态保留版首次完整42层回读／消费者通过。真实提交完成ACK／先SAVE再释放／私有目的页／取消epoch是不可拆掉的正确性整体；作为显式实验方法PR，不默认启用。依赖PR3。 |
| 私有目的页排序：canonical protocol0e2115；旧a1b副本在`analysis/source/kv-transaction/` | 否 | 204159目的1044段→66，ZERO／RESTORE／回读各43848→2772调用且全字节过；未来free顺序变化已知。可作基本事务的独立增量PR，不等同请求重排或TPS提升。 |
| 容量必要下界早退：`candidates/biv150_kv_capacity_protocol.py`（67e4） | 否 | 212106真实fast462／R16688／42层回读通过；只F<P必要下界，不能F>=P就批准。依赖前述事务／排序历史版本，guard外原路径；可独立增量。 |
| 完整覆盖省ZERO：`candidates/biv150_kv_full_restore_{transaction,worker,protocol}.py`（84be／5d9a／1aff） | 否 | 214400 FULL真ACK／0ZERO／42层718405632B／消费者通过；新显式状态转换，不伪ZERO_ACK。依赖已审事务／容量版本，作为独立增量PR。首VERIFY0 pair有约0.20%小信号，后继复核有容量失配；不能称稳定收益。 |
| 二维SAVE服务接入：`candidates/biv150_kv_pitched_save_worker.py`（a662） | **仅底层工具在PR4** | 042225源free前42层c95f对照、原FULL回读及consumer16通过。另一个实验接入PR应依赖PR3、PR4及FULL事务；先保留SDK／SO身份和失败settle职责。未有服务性能pair／模型accuracy，不改wheel默认启用。 |
| 进展victim选择：`candidates/biv150_kv_progress_victim_protocol.py`（72942） | 否 | 015315真选择／FULL42bytes／consumer9通过；020721／021658性能pair因KV521936／521840及4MiB分项差失配，不报收益。依赖FULL；单独实验PR，不能声称FCFS公平性／采样输出等价。 |
| KV／抢占观察：`biv150_kv_runtime_descriptor.py`、`biv150_kv_memory_observer.py`、`biv150_kv_completion_probe.py`、`biv150_preemption_snapshot.py` | 否 | 默认关闭的诊断，不混成生产优化；6a内存观察实际定位部分run的4MiB残差和6块差，但未定位allocator根因。230548真实31running／queued前缀用于策略依据。留实验库或独立诊断PR。 |
| MLP CTA分组：`biv150_mm_cta_group{,_service,_service_source}.py` | 否 | 180646固定gate-up单层约16.18%正信号、down约3.81%负；只gate-up182916真实42层命中。无稳定E2E／accuracy；独立算子候选，不能宣称FlagGems库已合入。 |
| 2D完整可见prefix免mask：`biv150_prefill_visible_prefix.py`、`biv150_visible_prefix_service{,_source}.py` | 否 | 121838真实层bitwise过、单层wall约0.276%；190206服务READY／REAL_LARGE命中却没有正服务信号，保留负结果。只能实验候选，勿混C2/C3历史accuracy。 |
| BF16 hidden行gather：`biv150_hidden_row_gather{,_source}.py`；旧`biv150_decode_hidden_view.py` | 否 | 111804 copy bits／RNG／动态cache等门过；112021服务约0.06%且KV失配，无归因收益。旧view是另一草案，不能冒充该copy已部署；暂留实验库。 |
| 映射3D decode：`biv150_mapped_{attention,decode,decode_source}.py` | 否 | 183421 dummy BF16新operand令SME bit36溢出失败，最小修复后4case／后继decode通过；单层约13.31%，两服务一负一正且KV失配，不认稳定收益。独立实验PR需原C2/C3基点与SME修复，不整搬新框架。 |
| mixed token bucket：`biv150_mixed_token_bucket.py`／footer | 否 | 105930有效Attention／整KV／next32decode逐位过；113208冷新增DB，113946 warm恢复时间但基点DB／KV不同，没有确认性能收益，未默认集成。 |
| 双流Attention：`biv150_mixed_attention_overlap.py` | 否 | 4call墙钟信号经64call摊销仅约0.349%，device窗口持平略慢；保留正确性原件，不服务集成。 |
| 早期direct decode／dirty block table：`biv150_direct_decode.py`、`biv150_block_table.py`及对应delta | 否 | direct真实5case过及约1.3%单层小信号；dirty metadata／graph门过，但服务有并发CPU／KV混杂和greedy不稳定，未排除风险，不默认集成。 |
| fused sampler：`patches/candidates/*fused-sampler.patch`及bench／validate；deterministic top-p见上方 | 否 | fused独立采样尾约2.38×但服务4K回退、16K改善，不进默认；不能把其尾部性能给保留top-p方法。 |
| growth准入：`biv150_growth_admission{,_source}.py`、`*_v2{,_source}.py`、`biv150_growth_descriptor_once.py` | 否 | V1没进入scope；V2 warm无正吞吐、TTFT约+7.51%，保留不集成。terminal／短R／waiting runway目前仅诊断或设计，不包装成已实现收益。 |
| Event实验：`candidates/biv150_native_blocking_event.py`、`scripts/remote/biv150_event_bridge.cpp`及两个Event gate | 否 | 045818 typed及051336 direct SDK blocking均字节／RNG过，thread CPU仍约9.44ms，无下降；停止，不建生产优化PR。 |

另外两CPU方法现有PR1／PR2由framework／root重排依赖：`biv150_cpu_metadata{,_source}.py`、`biv150_async_token_update*.py`不属于本KV工具依赖；062205组合方法门通过也不意味着它们与完整KV事务组合已验。

## FlagGems没有实际新增库内算子

本轮只读本地`collaboration/FlagGems`，HEAD为`6ddb4c4cd12790cfc7b1203bdca2ed7a131f7dd6`，工作树clean。相对固定upstream `4df52d9168ac55c1c1061cefb4638c570292d896` 的完整`git diff --name-status`只有`M README.md`与`A README.upstream.md`，**src／配置／原docs均无差异**，不应捏造FlagGems算子PR。

实验库确有`patches/FlagGems-biv150-gqa8-decode-draft.patch`（flash_api配置选择及新配置草案），它没有进入该代码库；早期GQA8／随机Attention测试记录不证明这个草案已默认部署。新增Triton kernel／派生Attention／MM重映射在插件实验实现中，与“FlagGems库源码已修改”是两件事。若未来决定正式迁移，才以真实diff和独立启用／正确性证据建PR。

## 最少整理方式

先恢复原13eb并保存旧组合快照；PR3／PR4直接重建原字节新增文件，独立合入／单独撤回。五个旧方法分别建PR，由framework核真实源与安装依赖。**完整KV链暂以实验PR依赖图表达，不把全部历史快照混入工具PR，也不为每个wrapper／负门单开PR。** 仍未证明收益／accuracy的候选保留在实验库；若需审源码，可建明确标“实验、默认关闭”的独立PR，不冒称已可生产启用。

各方法的CPU tests、`scripts/remote/{validate,bench,prepare,launch,collect,audit}_*`、`scripts/review_*`以及`analysis/source/`冻结源／失败／原测量均为复现材料，留专用实验库，不复制所有历史source／SO／日志进入框架PR。原`*sql-decode*`／`*sql-mixed*`／full.patch是历史组合包装，不能作为另一项新方法重复合入。只复用必要合同和直接证据链接，不新跑设备或旧套件。
