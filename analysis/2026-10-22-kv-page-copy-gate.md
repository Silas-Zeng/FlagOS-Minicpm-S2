# 42层KV页保存与恢复：最短成本门

2026-10-22，systems_innovation；BI-V150，旧d841首门导入前失败已保留；修复93eb的191545门四case byte/event全部通过，成本仅单warm样本。root为唯一GPU owner，本agent没有SSH/GPU或服务protocol改动。

## 历史191017导入前失败与最小修复93eb（191545已完成，见末节）

root回执191017于19:10:18Z exit1/cases[]，尚未初始化复制。原因是归档source/copy.py遮蔽stdlib copy，dataclasses导入copy时循环；不是页复制/事件/数学错误，没有成本或正确性结果。旧d841原件必须保留，本地另存精确字节 `analysis/source/kv-page-copy/validate_kv_page_copy.d841.py`。

按root授权，仅四个归档/hash/加载字面量 `copy.py` 改为 `biv150_kv_page_copy.py`，policy c95f不变；当前gate **93eb02c7dbdaac3ec982fbf5b0dd0f24e29ebf74e73a5b48c7dc820ae0dab56d**，launcher `launch_kv_page_copy_gate.sh` 只改对应pin，SHA **ba3336e186b9f62c32b6dd053e55a4b990c17912f3c15d88cbbc2bddebf38836**。hardware已定向终审恰四字面量和launcher新pin无阻断，冻结不继续改策略/测试窗口。下述d841全审及guard差异保留为前次历史；后继新run使用93eb，不能混淆两次身份。

CPU实际构造独立source子目录+新Python进程验证：旧名重现partially initialized失败，新名加载成功，stdlib copy来自Python库而非source，mapping符合原合同，torch/numpy/vllm均未载；`analysis/source/kv-page-copy/source-load-check.json`保存完整command/exit/stdout/stderr及SHA。首轮父进程按UTF8读Windows默认编码子stderr导致收集器异常，后显式子进程-Xutf8完成同路径必要检查，未改候选/设备，也未重跑映射suite。原一项mapping合同不重复。


依据 `experiments/source-audits/20261021T184108Z-kv-copy` 的13实际源，complete/missing0/mismatch0；本地逐项SHA/长度核实。actual Triton backend1219的BF16/auto/NHD factory返回 `(num_blocks,2,16,2,128)`、identity stride order；actual reshape helper a351允许普通逐层raw或packed `(offset,block_stride)`。本门**构造两种受支持布局**，不声称已经观察服务tensor的实际normal/packed布局或executor类型。此前“缺executor/reshape等源”为184108采集前历史，现对应源已齐；静态executor分支不等于运行类型取证。

42层×2KV×16tokens×2heads×128×BF16 = 688128B/逻辑页，即672KiB；1024页/16K输入每方向672MiB。normal每层16384B/页，packed每页42×16384B且层offset=i×16384；只同时连续的src/dst页合并，保持逻辑顺序，绝不sort。两种布局各1run/8run，共四case；末端guard及未选内部页独立检查。

代码与固定身份：

- `patches/framework/biv150_kv_page_copy.py`：**c95f59a55f5409e651085ff52d788193ea1d5901dcbc99d38fa504842b12f44c**，stdlib-only/default无安装；一对一范围与type校验、CPU pinned↔cuda0 raw uint8连续页，仅提交non_blocking copies；返回completion_ack=false，不冒充已完成。
- 191017历史 `scripts/remote/validate_kv_page_copy.py`：当时冻结 **d841a1abbfee94a68fddc1afec8bd236b91e2831102217577fa90bd03605f8a3**。硬件owner已全文审b86a，并由d841逆换唯一delta精确重建b86a，定向确认无阻断。最后delta仅将全池poison+重置两guard改为 `tensor.narrow(0,1,POOL-2).fill_(165)`，guard初始化后不再写；event/copy/timing均不变，poison仍窗外。交付hash改后尚未即时回执曾造成pin不一致，已同步root/hardware并冻结，不再静默改稿。
- `tests/test_biv150_kv_page_copy.py`：bcda0387e8ac70f7f86b304d739c18f1012dc1e80f9d077299acf25bb87cee72；唯一必要CPU合同1项0.002s，仅mapping/type/bounds/总字节，非设备正确性。
- `analysis/source/kv-page-copy/cpu-check.json`：compile/help、stdlib import、已pin实际AST factory抽取与shape检查，以及上述单合同；无GPU，最终毒化delta只compile，没有重复合同。

实际语义及验证窗：compute producer→ready→transfer save→end_save.synchronize，**D2H完成后**才读pinned或poison/reuse；compute等save后毒化内部页→poisoned→transfer restore→end_restore→compute读取全部42实际factory view并clone→consumer event同步。所有GPU/host/golden/view/consumer保持强引用至完成。CPU正数basic narrow读全部保存/恢复页、两端guard及未选页，consumer按int16逐bit核对；RNG输入构造之后不得改变。首个untimed正确性pass含跨流生产依赖，第二个warm pass才计时。

四个timing Event预record；producer设置、poison、consumerclone、oracle、分配均在方向计时窗外。报告D2H/H2D各自提交至完成的wall/event及往返，总字节/copy调用数；每几何仅一组warm成本样本。另报告显式host/GPUraw字节及GPUallocator peak；cgroup只是若干时刻观察，**不是host峰值**。consumer clone额外显存是本门测试开销，不代表服务offload预算。

准备命令（由root排在唯一GPU完全空闲后执行；本agent未执行）：

```bash
python3 /workspace/experiments/minicpm-s2/scripts/validate_kv_page_copy.py \
  --run-dir /workspace/experiments/minicpm-s2/framework/<UTC>-kv-page-copy-gate \
  --copy-path /workspace/experiments/minicpm-s2/scripts/biv150_kv_page_copy.py \
  --source-evidence /workspace/experiments/minicpm-s2/source-audits/20261021T184108Z-kv-copy
```

controller固定source/helper/modelSHA、common lock、68MiB/0%/端口空闲、唯一child/monitor、300s和定向cleanup/postflight；不修改installed框架源，不加载权重。13源采集时cgroup限额20GiB，PCIe观察16GT/s×16，仅链接状态，非DMA实测带宽。

本门若过，仅证明构造的受支持两种布局的传输/事件/byte正确性和一次成本，不证明Attention/graph/模型accuracy或长期抢占服务收益。真正服务还需实际runtime tensor描述、executor/worker stream所有权、save完成前禁止free、zero之后restore且Attention之前ack、host buffer/epoch/取消生命周期与跨进程协议，当前**未实现**。181041的13758token gap只是prefix exposure，不是已发生GPU重算或可节省时间；terminal0负证据已否决drain，不重复full-output reserve。


## 设备门失败或成功后的最小封存清单

只读检查冻结d841后整理，不修改脚本。保留整个唯一run与control目录；至少含原始manifest.json、results.json（即使partial/failed）、worker.log、exit-code、finished-at.txt、gpu.csv、monitor.log、preflight-ixsmi.txt、postflight-ixsmi.txt、control的controller argv/PID/log，以及全部source。93eb当前固定归档8份：gate.py、biv150_kv_page_copy.py、triton_attn.py、attn_utils.py、source-evidence-manifest.json、model-config.json、validate_block_table_candidate.py、monitor_gpu.sh。八项逐byte SHA及此前13actual-source manifest相连，失败也不删除/重写。

`pass_once`在checks失败时先raise再return，因此当前case的passes数组可能为空；实际失败五项checks在results.error和worker traceback内。不能把前面case过了当整个门通过。进程SIGKILL/timeout可能连results.json都没有，保留controller_error/worker PID/已有partial；不合成结果或声称数学失败，先按异常原件分类。

controller保存owner.preflight+raw ix-smi及query；外层owner照既有流程追加完整postflight：UTC、单卡68MiB/0%、无GPU进程、9031 IPv4/IPv6闭、controller/worker/monitor PID退出或Z状态及targeted清理异常。此检查应在worker释放GPU后；如不足，原件保留并标后态未证，不隐去失败。最后完整tgz与包SHA由root取回，本agent仅读本地。

本地验收对照：必须恰好normal42/packed42各contiguous/fragmented8四case，各untimed/timed两pass；每方向704643072B。normal contiguous每方向42次copy，fragmented8为336次；packed分别1/8次。save和restore返回completion_ack=false只表示runtime提交接口没有承诺完成，真正完成由门的Event证明。每pass的保存全字节、恢复全字节、两guard、未选poison、42 actual-view consumer均true，各case RNG true。actual-derived形状(1058,2,16,2,128)，normal stride0=8192 BF16元素/packed344064，packed layer41 storage_offset=335872 BF16元素，normal offset0。只timed pass有四方向wall/event+roundtrip，严格正数并重算roundtrip；不能将untimed缺失计时当失败或补计时。

四case若全部通过，仍只报告构造布局byte/event门和一组warm成本。任何失败先保全error/阶段和后态，不绕过guard、不添加自动fallback掩盖错误；后继修订使用新run ID/新hash再互审，原d841和失败原件保持。


## 191545修正版KV门完成：四case正确，成本仅单样本

`experiments/framework/20261021T191545Z-kv-page-copy-gate{,-control}` 已完整本地，包SHA **7b491c525759e3320ecac8cd385d31fd1f434784ade63eef16bb2ab02a554316**。独立仅读8源SHA与93eb/c95f/1219/a351固定身份一致，19:16:59.928412Z exit0；normal42/packed42各contiguous与fragmented8四case，各untimed/timed两pass，40项checks与4项RNG均true。保存/恢复全byte、两guard不重写、未选页poison、42 actual-factory view消费者全部通过；shape(1058,2,16,2,128)、normal stride0=8192/offset41=0、packed stride0=344064/offset41=335872符合源码，每方向704643072B，copy调用分别42/336/1/8。原191017导入失败及修复加载证据保留；不是隐藏失败后只挑通过。

| 构造布局/页映射 | save wall ms | restore wall ms | roundtrip wall ms | save event ms | restore event ms |
|---|---:|---:|---:|---:|---:|
| normal42/contiguous | 25.946121 | 196.106984 | 222.053105 | 24.756731 | 26.488735 |
| normal42/fragmented8 | 27.699296 | 207.570993 | 235.270289 | 25.073376 | 194.106018 |
| packed42/contiguous | 24.943508 | 95.012686 | 119.956194 | 24.734741 | 26.496109 |
| packed42/fragmented8 | 25.027936 | 95.688994 | 120.716930 | 24.747791 | 26.758972 |

方向wall是host提交至事件同步返回，timing Event已预初始化，producer设置/poison/consumerclone/分配与CPUoracle窗外；保存事件完成后才读pinned/毒化，恢复事件后consumer才读取。每geometry仅一组warm成本，normal连续restore wall196ms/event26ms，而normal8run event194ms，host提交/调度混杂尚未分离，copy gate没有CPU quota或并行host工作负载记录。**不称稳定DMA带宽、packed因果加速或服务收益，不将event直接作纯硬件传输时间。** 各case显式host1432682496B、raw GPU728039424B；GPUallocated peak1456078848B含测试consumerclone，cgroup仅时点/20GiB限额非host峰值。

owner19:18:05.738516Z后态单卡68MiB/0%、9031双栈闭/无GPU进程，owned退出或Z、8源无failures核实。全量tensor没有另存binary；本地独立检查冻结代码的完整oracle和原结果，不重新运行GPU。结果保存 `run/independent-gate-review.json` 和 `analysis/2026-10-22-kv-page-copy-result.json`；registry93数据行×16列/queue69均LF。

这一门仍没有权重/真实runner tensor布局/Attention数学/请求allocator/跨进程恢复protocol/模型accuracy。后继服务入口若继续，须先证明actual executor与持有KV view的worker生命周期、save完成前不free、zero后restore且Attention前ack、host pinned强引用/epoch/cancel及失败回退；这些只是后继约束，**本批没有实现或运行**。181041 gap13758依旧只是exposure，不能把约0.12–0.24秒copywall替换成假定GPU重算节省；不能开启现成connector模式冒充实现。
