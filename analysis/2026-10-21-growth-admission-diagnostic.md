# growth未命中的最短描述符诊断

2026-10-21。本轮只本地CPU读源码/证据；不修改在途或冻结runtime，不SSH/GPU。

## 已证明与未知

110149原080656匹配基点220.494323s、32成功；110747 growth220.369000s、32成功。两者实际preemption均0→1，DB四份快照均501表18789行且三hash相同、同bc51ac2d driver；但KV521840与521936相差96tokens。growth EngineCore有INSTALLED而完整日志没有FIRST_CHECKED或FIRST_DEFERRED，因此**未证明策略实际启用，结果inconclusive，不报微小收益**。

实际scheduler等待分配使用keyword full_sequence_must_fit，AsyncScheduler和FL子类都不覆盖schedule；base wrapper继承关系已核。模型/并行配置可从日志核实，但不能从源代码默认值推断运行时KV spec/coordinator/manager的准确类型、layer_names、policy或V2 flag。root另核reserveFullISL默认True/watermark0及FullSpec两个默认字段，仍不能据此认定_eligible通过。现在没有可准确点名的失败guard，禁止猜测放宽。

## 单独模块与守卫

`patches/framework/biv150_growth_descriptor_once.py` SHA **4a6eaefa0b40358307f48c586b9be7dc4a801f4b8eeeda752ff2db5275619b99**。导入本身不安装；显式install只包constructor和allocation做观察，原growth9245与所有5源SHA、原constructor身份/已安装growth wrappers必须通过。原runtime一字未改。

纯bytes `transform_source()`只接受已加growth hook的init SHA `d9e2caf40f8d126ec4344b6c98605847f9b4be438eb9961a2eb3bb0f40671ef9`，在其general register_model末尾再追加诊断import/install。只在新隔离source中复制模块并变换init；在内存复核输出init SHA **5c11fd1f97057d9a820cb048690a8135bce41fea8d1160127c238653f181e163**。拒未知/重复变换。

挂点为原base Scheduler.__init__返回之后，此时实际EngineCore创建的KV manager与所有scope字段已稳定。从已哈希验证的本地growth文件解析_eligible AST，原29项AND表达式逐项单次求值并捕准确异常；setup赋值异常另列，原helper的最终bool也一起输出。生成器表达式使用同一globals/locals合并namespace，避免`all(...parallel...)`因eval作用域而假报NameError。JSON包含PID、actual类名、group/layer数、V2/reserve/block/maxlen/policy/KV形状等描述符与源指纹，不读tensor内容、环境凭据或请求文本。

constructor false时，这条完整guard JSON已足够定位，按root最短策略不再捕allocation。只有constructor true时，才定位其weakref对应manager，在首个有running的waiting分配外层额外一条kwargs/status/请求长度和原调用后stats。它不依赖growth授权ContextVar，不额外调用_growth_demand、不改状态/结果。descriptor/weakref/stats/JSON输出失败不得阻止原call，原allocate恰好一次、其异常原样透传。

## root最短运行方式

先以现有源打包机制创建**新**隔离growth-diagnostic source，保留原growth/runtime与full-source manifest；复制单独诊断模块，再以`new_init = diagnostic.transform_source(old_init)`变换这个新source的init。以下仅是接入模板，不应用到原105930或在途源码：

```text
python3 /workspace/experiments/minicpm-s2/scripts/run_framework_screen.py \
  /workspace/experiments/minicpm-s2/framework/<NEW-UTC>-growth-descriptors \
  --source-dir /workspace/experiments/minicpm-s2/code/<NEW-DIAGNOSTIC-SOURCE> \
  --smoke-only --seed 721201 \
  --require-log-marker GROWTH_CONSTRUCTOR_DESCRIPTORS
```

仍必须等待唯一设备任务清理，使用原SERVER。此run只诊断，不入性能对照。constructor已能定位时无需32请求长负载；如全部true而仍须诊断request fallback，只补2并发极短请求使waiting在非空running下发生，避免再做数分钟长测。原started/command/source/log/exit/清理与新模块/init哈希完整留档。

作者已py_compile，并用一个必要CPU合同确认29guard全通过（包括all(generator)），删除policy可准确保留对应AttributeError；exactinit变换编译通过。framework owner独立审最终4a6e通过，确认纯观察异常兜底与原调用保持；没有新增suite。下一步应读取实际JSON，只针对证据确认的单一类型/字段问题决定是否修原候选，不先改scope。

## 112603真实诊断完成：唯一失败是V2 guard

`experiments/framework/20261021T112603Z-growth-descriptor-smoke/independent-diagnostic-review.json`独立核23源SHA、exit0、DB前后三hash不变及完整postflight。EngineCore156959真实29项guard中仅 `not scheduler.use_v2_model_runner` 为false；其余28项true、setup_errors为空。实际类是builtin AsyncScheduler，use_v2=True，其余KV/模型/FCFS/Reserve均exact。此smoke实际seed721001，没有长负载或性能意义。11:32:08.170110Z fullpost68MiB/0%/9031closed。

原因至此已定位；后继采用审过actual placeholder/payload/释放协议的独立v2修订，见 `analysis/2026-10-21-growth-admission-v2.md`，不再重复29条件诊断，不改环境关闭V2，不覆盖9245旧版。
