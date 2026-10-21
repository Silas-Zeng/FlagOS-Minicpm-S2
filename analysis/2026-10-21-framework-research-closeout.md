# 框架研究收尾：C3覆盖证据与未执行诊断草案

2026-10-21，owner `/root/framework_innovation`。用户要求停止探索、完成已开始工作后转GitHub协作。
本轮止于本地源码审计与本文，不新增运行模块/诊断脚本，不改冻结080656候选/default，
不SSH、远端import或GPU。root的original13eb official122607仍独占设备；retained远端import禁令继续有效。

**结论：没有SQL后剩余host大收益的实测证据。C3自然前缀是否遗漏了大量可分流请求也尚未测量。**
保留一个明确的覆盖诊断设计；其实现、上卡和任何完整decode分流均未执行。

## 冻结来源与已完成阅读

| 实际来源 | SHA256 |
|---|---|
| 092944 `source/plugin/vllm_fl/worker/model_runner.py` | `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1` |
| 同归档 `patches/biv150_mixed_decode.py` | `a129361f1ef1babe1ce1e6238f6b1a725050612c235201064ddeba676b420c42` |
| 同归档 `patches/biv150_sql_reflection.py` | `ad84c9affe0c3f4b9a4432dd2cbb3861306726f07d53328e129af41c74ea8e8e` |
| 同归档 `installed/vllm/v1/attention/backends/triton_attn.py` | `1219c4d1820b56e99ef6686de8a49c8c5aa57707794bcabf3322023799a03605` |
| 同归档 `installed/vllm/v1/attention/ops/triton_unified_attention.py` | `54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f` |
| 同归档 `installed/flag_gems/utils/models/sql.py` | `6dc19cb581d70154f14b95ed9112d682c6b5919b6cf3f8dea01a78a75ec0efd7` |
| 061506 host-gap `source/libentry.py` | `414e8a3f74e2522e40659e7fccd84e301f4517220837a87af0311f050bbf3025` |

已读既有decode-gap、SQL后研究、系统创新、内存生命周期、hidden-view、large-gain、
innovation-hardware、framework-review、bottleneck-profile、attention-top-p负结果与queue。
block64、更大batch、关prefix、sampler compile已负；bucket/gather/growth/overlap后续证据不支持继续扩大，
prefix-mask只保留小单层信号。这些方向没有重做。

061506 profile是修SQL之前：172次LibEntry仅12次进入LibTuner，24次SQL get包含4次全库反射。
LibEntry `run:1682–1742` 的kernel-cache热命中直接走compiled launch，绕过LibTuner/SQL。
旧13.4s不能继续作为SQL后可省预算；没有新profile证明每层每步双SQL查询。
新建SQL model用pool[name]、读取short_name的问题也已在旧
[`innovation-hardware.md:55`](2026-10-21-innovation-hardware.md)与hardware handoff记载，
本轮只是重新确认。曾先向root称其为未提新点，完整反查后已立即纠正；不以它重复包装新发现或原型。

## 已开始的C3覆盖源码审计

准确runner的顺序为：

1. `:1499–1502` 新增/恢复请求先填较小空位；
2. `:1505` `input_batch.condense()`；
3. `:1507` `_may_reorder_batch(scheduler_output)`；
4. `:1509` `refresh_metadata()`；随后才按最终物理行顺序准备输入和attention metadata。

`_may_reorder_batch:1125–1148` 只有在 `self.reorder_batch_threshold is not None` 时才调用
`reorder_batch_to_split_decodes_and_prefills`。`calculate_reorder_batch_threshold:7025–7043`
从所有builder的threshold取最小值，全部None时保留None；runner没有硬设decode-first。
准确1219的Triton builder本体没有设置 `reorder_batch_threshold`，C3 install也没有赋该属性或重排请求。

**完整installed父类`AttentionMetadataBuilder`、`InputBatch.condense`和reorder helper没有在本次本地归档中取得。**
所以不能把旧公开同版的默认None/condense内部算法冒充精确安装源码已核对，
也不能只看方法名就声称实际runtime保证decode-first，或反过来断言它必定遗漏大量请求。
此缺口按用户停止要求原样交接，不再取远端源码。

C3 `_prefix:86–114` 只看CPU query offsets：正长度、总M/最大Q一致后，
从第一个请求起数连续query_len==1，遇到第一个非1即停。
还要求 `0 < prefix < count` 且prefix不超过3D阈值；forward仅消费builder已存plan。
因此 `[1,1,P]` 可拆2个，`[P,1,1]` 没有自然前缀，`[1,P,1]` 仅拆1个。
这是源码条件示例，**不是这三个形状已在真实服务出现的证据**。

080656与054922服务日志只保存 `BIV150_MIXED_DECODE_INSTALLED`，原a129没有split命中计数。
054501实际Builder/Impl gate的synthetic输入、manual split equality和puredecode graph通过，
只证明构造好的自然前缀可工作，不提供服务中D/prefix比例。
现有单层门的D29/P2019也属显式构造。当前未发现服务raw里的真实natural-prefix命中数量，
所以旧C3收益、103/105 accuracy和official绝对成绩都不能反推出覆盖率。

## 最短隔离诊断设计：仅草案，尚未编码/运行

未来只有用户重新授权继续研究后才考虑；当前不生成脚本或执行命令。

- 复制冻结080656到新的隔离source，严格pin a129/e155/1219；原build先调用且返回原对象。
  诊断只观察其CPU `query_start_loc_cpu` 和已生成plan，不改变metadata、顺序、调度、采样/RNG、KV或数学路径。
- 每个真实`execute_model`分配CPU step序号，在其作用域内对首个目标builder计一次。
  多builder另记group/build调用数，不能把42层forward当42步；dummy/capture不混入真实步。
  原method参数/返回/异常保持，观察失败只计diagnostic_error，不能覆盖原异常。
- 对正长度CPU offsets，记录N、M、最大Q、`D1=sum(query_len==1)`、
  `Dprefix=连续1token前缀长度`、`Dselected=原plan.prefix_tokens或0`。
  `mixed_with_single_query`明确指最大Q>1且D1>0；另分pureprefill与puredecode。
  D1是符合C3切分形状的单query请求数，**不能未经prompt/computed阶段审计就声称全是真实生成阶段decode**。
- 聚合mixed步数、sum(D1)、sum(Dprefix)、sum(Dselected)、
  sum(D1-Dprefix)、D1>0且prefix0的步数、raw-prefix存在但无plan的次数。
  后者单列以免把其它scope/threshold回退误当排序遗漏；不记录prompt、token值或request文本。
- 在稀疏CPU边界落聚合快照，附覆盖step范围/是否完整；正常终止再落最终快照。
  若清理信号导致最终快照缺失，使用已落范围并标incomplete，不能冒充全负载计数。
  不每层/每步写长日志，不新增GPU查询、同步、profiler或计时分数。
- 若未来获准执行，仅复用原SERVER/来源及既有4K、64req、128out、同seed短负载，
  单一GPU owner在原official结束并清理后串行执行一次。
  它是诊断，不把约40s预计时长当成功承诺或性能pair；原080656约39.16s只是历史参考。

**最短否定条件：** 所有观察到的mixed步D1==Dprefix，或遗漏数量/所在步骤极少，
或没有可用真实mixed窗口，则直接关闭这条大改路线，不实现全decode gather/scatter。
只有实测存在明显遗漏才讨论Attention内部重新打包；届时Q/output回填、行语义、KV只读、
3D归约精度与RNG分配均须另审，现103/105不能自动继承。
覆盖计数本身仍不证明遗漏部分具有性能收益。

## 另一项已开工想法：C3重复view清理，保留且未实现

C3 `forward:221–225` 产生Q/K/V/out共8个slice；原backend每次再slice Q/out、
unbind KV并expand两scale。一个split layer合计12个slice、2次unbind产生4个view、
4个expand，约20个view对象；42层约840个对象/步。准确backend `:565–573`也提醒eager piecewise路径view/slice有CPU开销。

最小保留方案为每层只做一次公共decoder参数准备、4个Q/out子视图、一次KV unbind，
两个子批的scale.expand仍原样，按原顺序调用同一个unified_attention两次。
理论少4个未消费的K/V slice、4个重复Q/out slice和一次unbind的2个view，共10个view对象/层。
不跨步缓存、不改图、不做overlap、不把scale指针改None、不换kernel/配置/FP顺序。
长kwargs、fallback、stream/alias/生命周期仍须核对，工作量减少并不等于暴露延迟减少。

root已明确：没有关键路径占比，只保存，不实现。未来最短否定应先看同配置host前端/提交时间是否有可见比例，
再决定是否值得原一层bitwise/KV/RNG与预热event ABBA；不能直接上整模型或大accuracy。
**没有该方案的代码、CPU计时、GPU结果或收益声明。**

本轮收尾只新增本文与owner handoff。所有未执行步骤保持未执行；现有完整fallback补丁4aba的
CPU包装通过不变，源码/默认补丁不变，不以这些草案延迟GitHub交接。
