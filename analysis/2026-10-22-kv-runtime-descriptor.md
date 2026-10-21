# 天数BI-V150实际KV布局与执行器：一次性观察门

2026-10-22，framework_innovation。承接 [`下一框架优先项`](2026-10-22-next-framework-priority.md)，只准备默认关闭的CPU元信息观察器和隔离source；不实现save/restore，不改变调度、请求、RNG、数值或官方参数。本owner未SSH/GPU/模型导入/共享代码库push；root持唯一设备并决定最短smoke。全部实测边界仅BI-V150，不外推C500。

## 已审时序与选定挂点

actual Core27b238在`__init__`109–110调用`load_general_plugins()`，221才绑定`self.step_fn`。因此general plugin内包装Core构造函数可能错过当前首次构造；经root确认，采用`step`/`step_with_batch_queue`首次调用前一次记录，明确phase=`first_engine_step_after_constructor`，不借frame、GC扫描或回溯猜对象。

plugin WorkerFL a8de1780的`initialize_from_config`677–694先初始化KV transfer，再调用exact e155 runner `initialize_kv_cache`；成功返回后一次读取已建立布局。选此处避开runner profile_run直接初始化minimal KV的临时布局；原方法成功结果原样返回，原方法抛错不执行后置观察也不吞原异常。观察失败只记录ERROR/`observation_error`，不替换原结果。

新取actual `WorkerWrapperBase`7da44338的319直接保存`self.worker=worker_class(...)`，333–334的代理`__getattr__`会转发。因此Core只通过实际对象的`__dict__`直接链读取`model_executor→driver_worker→worker→model_runner`，不用`getattr`探测未知代理，不RPC、不推断跨进程同址，不调用任一对象业务方法。缺项明确unobserved；实际类名/module与当前pid/objectid才是证据，静态UniProc源码不是运行时证明。

## 新文件与精确身份

| 产物 | SHA256 |
|---|---|
| `patches/framework/biv150_kv_runtime_descriptor.py` | `0c892ad02fbfe663d3f7c8f668cdd000c0c1fc7860ff915db8bce5949cae0667` |
| `scripts/remote/prepare_kv_runtime_descriptor_source.py` | `936c9260724f97b02dc1e69da2f4f0da7cdfaf7fdcb0e8ab866c26d9c028c59e` |
| 新init，仅向exact e043追加general注册footer | `90fe0b381fd53ec5273c623d91b806a0fc21f5b84165beba0b015a1e07d53e74` |
| CPU检查脚本 `analysis/source/kv-runtime-descriptor/check_cpu_contract.py` | `445cc886d5506537051dc3caa006d544c9858ef985a4f11c7a7c912b56f5a73a` |
| CPU结果 `analysis/source/kv-runtime-descriptor/cpu-contract.json` | `f0771d57a090466499bd48996636c41d198f1f3fe3abfd78618a40c98f0d189f` |

runtime默认`install(enabled=False)`不导入框架。隔离init才显式True，必须有`BIV150_KV_DESCRIPTOR_DIR`指向唯一`ROOT/framework/<run>/kv-descriptors`。安装先核Iluvatar平台及exact source：Core27b238、executor abstract419002、UniProc4625c8、worker_base7da443、WorkerFL a8de1780、runner e155；方法原qualname/文件/无既存wrapper、init完整prefix+exact footer均须通过，否则REJECTED不安装。不会更改installed源码或原080656。

包装复用已审owner0ecf7dc7，仅接受原080656全新code直接子目录，核心8份身份/现有5个BIV模块精确集合，拒已叠候选与现存输出。通过AST仅读取runtime两个literal常量，**不执行runtime/framework import**，只改init+增加一个观察模块，runner继续e155。全量copy前后SHA、内部regular-file alias规则和失败留档沿原owner，写新`innovation-source.json`。CPU真实213→215文件通过；同一远端410基点预期412含manifest，以实际全量输入/输出验证为准。

## JSON字段与边界

`worker-kv-<pid>-<serial>.json`包含：实际worker/runner类，配置group/block size/KV heads/head size/dtype，42层直接`static_forward_context[layer].kv_cache`视图、runner平面kv_caches逐项shape/stride/dtype/device/storage offset/element size/logical bytes/storage bytes/alias group，以及cross_layers实际descriptor、实际None的observed_none或缺属性的unobserved_missing_attribute。**源码事实纠正：exact e155构造函数587已初始化该属性为None；此前仅检索uniform赋值而称正常路径可能缺属性不准确，撤回该说法。** 最终0c892三分只为未知/部分对象保守区分，不改已有布局行为。列表索引不推断layer顺序；layer映射只来自实际直接属性。alias根据同pid的device/storage基指针/storage bytes分组，指针仅作内部key，不输出为可跨进程比较的地址。另存已观察的shared层映射、kernel block sizes/num_blocks及cgroup限额/时点；时点不是内存峰值或可分配保证。

`core-objects-<pid>-<serial>.json`记录实际engine/executor/可直接访问wrapper、worker、runner、scheduler类，queue size/async属性及cgroup；没有同进程worker引用就明确unobserved，不为补字段发RPC。所有文件`O_EXCL`创建、不覆盖旧原件；输出失败另打印WRITE_ERROR。弱引用once集合不持有cache存储。

仅调用plain Tensor的shape、stride、dtype、device、storage_offset、element_size和untyped_storage的nbytes/data_ptr元信息；不索引tensor、不item/cpu/numpy/copy/clone、无同步、无event/query、无大buffer。current_stream明确unobserved，不额外调用设备/stream API。本门不证明KV值、producer完成或未来save/restore协议正确，不能作性能或accuracy门。

## 唯一必要CPU合同与互审

一项最小CPU脚本已exit0，末次仅对cross_layers缺属性/None区分与asset pin作必要重核，1.73s。它执行actual WorkerFL初始化方法AST的fake依赖，证明ensure→原initialize→观察次序、原return/异常透传、once和观察失败原路；fake plain metadata验证42层packed alias、缺属性明确unobserved；exact init append/拒二次transform、全目录213→215复制、base不变/现存output拒绝、compile及无torch/vLLM import均通过。故意缺KV配置的fake负例打印ERROR是该合同预期，不是实际设备失败。没有构建GPU模拟或重跑旧suite。此合同不能证明实际Tensor storage API、真实布局、安装/EngineCore是否命中；交hardware独立只读审后由真实smoke判断。

## root下一条最短命令（本owner未执行）

将runtime、preparer与已审owner helper放进`$ROOT/scripts`并核上表SHA。root沿原screen driver `bc51ac2d9daf90205bde362f8384b1ac34238e7be932e9a6df7fc618d7350be9`，原SERVER和seed721201：

```bash
python3 "$ROOT/scripts/prepare_kv_runtime_descriptor_source.py" \
  --base-source "$ROOT/code/sql-mixed-20261021T080656Z" \
  --output "$ROOT/code/kv-runtime-descriptor-<UTC>" --asset-dir "$ROOT/scripts"

export BIV150_KV_DESCRIPTOR_DIR="$ROOT/framework/<UTC>-kv-runtime-descriptor-smoke/kv-descriptors"
python3 "$ROOT/scripts/run_framework_screen.py" \
  "$ROOT/framework/<UTC>-kv-runtime-descriptor-smoke" \
  --source-dir "$ROOT/code/kv-runtime-descriptor-<UTC>" \
  --smoke-only --seed 721201 \
  --require-log-marker BIV150_KV_RUNTIME_DESCRIPTOR_INSTALLED
```

**INSTALLED仅作预检，不当完成。** 退出封存后需有`worker-kv` status=`observed_complete`且42层/42平面tensor完整、实际shape/stride/offset/alias可读，以及`core-objects` phase=`first_engine_step_after_constructor`/actual executor。schema错误、partial、REJECTED、ERROR或没有事件必须原样保留并判观察未完成；不把smoke1请求时间作吞吐。照旧核driver/source/live/DB/CPU/请求与GPU idle。若成功才由systems/root继续审安全KV事务；本批不实现协议、不加额外GPU成本门。

## 195012实际smoke：normal42与本地UniProc对象已独立验收

root唯一设备run `experiments/framework/20261021T195012Z-kv-runtime-descriptor-smoke{,-control}`，19:51:12.927Z exit0。本owner执行纯只读 [`review_actual_smoke.py`](source/kv-runtime-descriptor/review_actual_smoke.py) **8695c1791ab0ee0f4eb1096fea26779de4c6300a8cfeac33b80ea7fc010e18c5** exit0，结果 [`actual-smoke-review.json`](source/kv-runtime-descriptor/actual-smoke-review.json) **be3f889f2227777f7eb623116ba77bfaf298011e98bf4f8c4bf33ac62421ac16**。

412份归档source逐项SHA、preparer936c、observer0c89、init90fe、原runner e155、原bc51 driver/原SERVER/seed721201与live412均通过；完整包装只改init+加module。smoke实际一请求8输入/32输出，无错误response；不是吞吐/accuracy。六源安装guard通过，原post installed54c未变。

worker与core事件实际同pid213942，worker/runner对象id完全一致。actual链为`EngineCoreProc→UniProcExecutor→WorkerWrapperBase→WorkerFL→ModelRunnerFL`，scheduler实际`AsyncScheduler`、async=True、batch_queue_size=2。42层与runner平面42项均为BF16/cuda:0、shape `[32621,2,16,2,128]`、stride `[8192,4096,256,128,1]`、offset0；各独立storage534462464B，共22447423488B，**actual normal42，不能拿packed42成本当生产路径**。block_size16/32621blocks=521936tokens，cross_layers actual observed_none、shared映射空。当前stream仍未观察，本门没有copy/restore事务。

before/after SQLite实体/schema/logical均相同（516表19270行、1593d60c/a0a590/90e9a868），CPU6/物理32768MiB。cgroup v1限20GiB，worker时点usage4373532672B、core时点4636340224B，仅时点不是pinned余量或峰值保证。post19:51:39.482845Z 68MiB0%、9031双栈闭、无GPU进程、412live source无失败；controller213760 Z/PPid1不持设备。完整raw和event未改，支持后续**独立**KV事务适配继续CPU准备，不构成恢复或accuracy通过。

文档命令已据实际bc51 parser纠正为positional `run_dir`，旧`--run-id`不存在；root真实launcher本来就正确，未影响本次运行或任何冻结代码。
