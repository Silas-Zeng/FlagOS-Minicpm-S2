# BF16 2D full-visible prefix：隔离实现与最短门

2026-10-21，hardware_innovation。root在原调参复核后明确只授权首选mask实现；不做w16或新扫描。本owner的全部操作保持本地CPU、未SSH/GPU；root随后执行了下面的121838设备门，候选仍未安装到服务/default。设计依据和42行/17配置防重记录见 `analysis/2026-10-21-prefill-unmeasured-candidates.md`。

## 最新状态：121838通过，保留prototype，暂不服务集成

root设备owner回执：`framework/20261021T121838Z-prefill-visible-prefix-gate` exit0，最终policy87c6/gate d3db/generated a6d身份一致。D29+P2019与Q2048两case的bitwise、整KV、RNG、padding、2D selected和3D C2 fallback检查均true。root于12:25:01确认fullpost `68/0closed`，旧门已关闭。**后继本地原件已到盘，本owner已CPU读取results/manifest并逐项核15个source SHA全匹配，汇总与owner回执一致。** 该本地核对保存在 `analysis/source/mlp-cta-grouping/evidence.json`，不新增任何设备执行。

| P2019，32calls一次ABBA，预record events | baseline ms/call | candidate ms/call | 下降 |
|---|---:|---:|---:|
| wall中位 | 12.594359734375 | 12.559617125 | 0.275858% |
| event中位 | 12.491010189 | 12.434306145 | 0.453959% |

这是**小的合成单层信号**；没有端到端、准确率或官方分数结论。保存可复现prototype与失败/边界记录，当前不服务集成、不扩大accuracy，不因mask tile比例高就放大收益。下文“尚未验证/可执行命令”描述实现时的设计与历史门操作，不授权立即再跑。

**当前设备状态（root回执12:26:07）**：唯一GPU改由 `official/20261021T122607Z-original-baseline`、runner166637持有，pristine13eb/source091033执行两档四轮原benchmark。installed attention已在空闲锁内恢复成上游bab2c0…，与a4 `.orig`逐byte一致。baseline期间绝对不能import retained/C3平台或其它会触发a0c runtime把site-packages写回54c的远端代码；本owner仅更新本地文档，下面旧门命令此时不可执行。

## 文件身份

| 产物 | SHA256 |
|---|---|
| `patches/framework/biv150_prefill_visible_prefix.py` | `87c6a31075939c551402d7007b491546a215584a58ec82caddc08fc7249998d6` |
| `analysis/source/prefill-visible-prefix/triton_unified_attention_visible_prefix.py` | `a6d3604aaf3896dce150b8ef56253a3d0fa12dd89095740bb1ec99ce975ddaa2` |
| `scripts/remote/validate_prefill_visible_prefix.py` | `d3dbf65a9a711360c92ca7c6a01a4ec23046926ee753cd37f836ad33a3bf1996` |
| `analysis/source/prefill-visible-prefix/check_source.py` | `9710528f41d93633020d2a1d3874586fbdf6434412cc40ebe97eaa8265df0654` |

exact输入是092944官方归档的actual attention **54c495dcea404582a1526a96ae7e472965cbd03c8fa0931c71ef72223bf04e1f**、helper **59d9d34bbda988436593cfd9bcb05015d17db8ee85c50f6697e45f987acbf0b1**。创建同时核backend1219c4…、C2e5f68…和原函数绑定。原件/公开上游/当前运行器均未修改。

## 精确改动

`transform_source`在full-file SHA与四个唯一anchor全部匹配后，仅在原kernel加一个默认False的constexpr、原for-loop前的整数cutoff、mask构造/选择两个位置。所有非kernel顶层AST保持相同。

原 `for j in range(loop_lo,loop_hi)` **仍只有一个**，没有两套dot/softmax loop，没有更改Q/K/V地址或原load mask。固定原2D **BM128/BLOCK_Q16/T64/w8/s1**。在选中路径，只有 `j >= full_visible_tiles` 时构造和应用原mask；原整数mask计算移到原score select前，QK乘scale、softcap、在线softmax、acc rescale/PV及epilogue表达式保持。采用每tile统一scalar条件，是最小实现选择；branch成本可能抵消收益，不承诺速度。

`create`将派生文件写到调用者指定的新路径、载入独立module、返回proxy；**它不安装任何class/moduleglobal**。门先装既有C2/C3，再显式临时换 `attention.kernel_unified_attention`，finally恢复原对象。proxy遇3D或不匹配即调用原C2对象，不改3D内核、w2/s1策略、reducer、metadata、请求顺序、采样或RNG。尚不宣称服务初始化/重装C3组合已验证；如门正面，服务接入仍须单独审阅。

## 边界证明与回退

设当前序列本轮query length为L，KV有效长度为S，context=S-L，qblock首位置为p=16·local，T=64。仅在 `local>=0, p>=0, p+16<=L, context>=0` 时给非零cutoff；否则cutoff=0，整个原mask保留。cutoff为 `min(loop_hi,max(loop_lo,floor((context+p+1)/64)))`。strict dense scope下loop_lo=0。

对于任一被跳过的tile j，`64(j+1)-1 <= context+p <= S-1`，所以该tile全部key不晚于最早query；同tile其余query只更晚，原causal mask恒true。该tile的KV load边界也全部在S以内，原tile/load mask仍不变。p+16<=L保证128条展平GQA行全部有效；kv_head为0/1、offs_m%8为0..7，16Q/2KV/128维使head/dim mask恒true。

- **leading invalid rows / virtual CTA**：原resolver和早退保留；local或p为负时禁止skip。完整块从有效首query开始，没有head或token前导padding；不能把一般padded tile当完整块。零length/虚拟尾块在原早退位置退出。
- **partial query块**：P2019最后仅3query，cutoff0，全部原row/causal mask保留，未去掉padded行的-inf；没有把它四舍五入为16query。
- **partial key tile / seq bounds**：cutoff只覆盖完全可见tile，边界及不齐尾继续原mask。P2019/16K的context14365未64对齐，有些块需要两个masked tile，动态条件自然保留，不能写死一个。
- **prefix cache**：证明使用当前序列S-L和原物理block table，既不假设context对齐，也不假设物理页连续/独占。C3子metadata的cu已归零，L取2019，不使用原mixed total2048；S仍16384。共享旧cache页只读，原KV update顺序不动。
- **negative slots**：本候选完全不读写slot_mapping、也不改KVwriter。-1仍由actual f18224… writer在K/V load前早退；Attention仅消费metadata定义的真实query和KV。门给NaN尾K/V与-1 slots，检查整cache不被Attention改写；不声称本kernel新增slot验证。

runtime只接受同cuda device的BF16 Q/K/V/out、Q/out形状(n,16,128)、KV(nblocks,16,2,128)、原head布局、正且不重叠的行stride、int32连续cu/seq和正stride blocktable；out不得与Q/K/V共享storage。KV支持actual interleaved unbind的outer stride8192。metadata值来自已审计原builder/C3，**没有D2H或GPU值验证器**；不接受任意伪造cu/seq作为新安全接口。

以下均原路：3D、非目标BM/T/warp/stage/头形状、FP8/量化、TD、非因果/per-seq causal、滑窗/chunk、MM-prefix、alibi、QQbias、sinks、softcap。runtime guard与kernel constexpr断言共同约束。未知shape/layout默认回原对象；source guard失败只创建失败，原模块未被安装/修改。

**浮点风险边界**：去掉恒true的where是数学identity，且浮点call AST保持；这不保证Triton控制流布局/指令分解保持bitwise。必须先真实编译与int16 bits门，不把CPU语法或数学证明当GPU等价。任何compile/bitwise/资源失败原样归档，不扩新架构补救。

## 最短设备门（仅root设备空闲后）

`validate_prefill_visible_prefix.py` 控制器不import torch/vLLM；拿既有单设备lock，9031/ixsmi及>=30000MiB空闲前检，唯一child拥有CUDA，300秒timeout、owned process group清理、postflight、命令/源码/版本/GPU样本保存。两个source_sha256遍历均过滤regular file，import生成__pycache__不会再次破坏归档。

worker读取actualMiniCPM5-2B BF16配置，不加载权重，调用原builder/Impl/KVwriter/C2/C3：

1. **D29+P2019/KV16K**：真实C3计划、prefill子cu长度2。随机物理页；D0/P共享16个旧prefix blocks（key位置<=255），new token从D0=16383/P=14365起，不写共享旧区。预期proxy选1次2D，3D回原C2一次。
2. **Q2048/KV16K**：完整query tile与一个原virtual尾CTA，预期选1次2D、无3D fallback。

两case均有3个NaN Q/K/V padding与-1 slot，actual KV update先于Attention，baseline/candidate相同输入比完整out的int16 bits、有效finite、padding哨兵、整KV和CPU/CUDA RNG。共享prefix只是该合成层的真实物理页别名，不冒充完整runner的prefix-cache生命周期测试。

正确性先过，再仅保留第一case做计时：各2warm调用、**一次32calls ABBA**，四对常规timing Event全部先record/sync完成底层惰性创建，之后重复record/submit/finalsync在wall内；逐组event/wall均保存。切换global在计时窗外。无新profiler、空kernel门、其它shape或扫参。若事件能力/编译失败，error区分但不冒称数学失败；无一致正信号停止，正面再考虑最短服务pair与必要accuracy，不能继承103/105。

下面保留的是121838门可复现参数：两个新文件位于 `/workspace/experiments/minicpm-s2/scripts/`，使用已归档080656源。**本owner未运行；root已完成该门，当前原始官方baseline期间不可执行这些命令或import相关retained平台代码。** 不重复开启第二设备作业。

```bash
root=/workspace/experiments/minicpm-s2
source_dir="$root/code/sql-mixed-20261021T080656Z"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
env VLLM_PLUGINS=fl PYTHONPATH="$source_dir" \
  timeout --signal=TERM --kill-after=15s 380s \
  python3 "$root/scripts/validate_prefill_visible_prefix.py" \
  --run-dir "$root/framework/$stamp-prefill-visible-prefix-gate" \
  --runtime-path "$source_dir/vllm_fl/patches/biv150_decode_launch_runtime.py" \
  --mixed-path "$source_dir/vllm_fl/patches/biv150_mixed_decode.py" \
  --policy-path "$root/scripts/biv150_prefill_visible_prefix.py"
```

## 已做CPU验证与审阅

source checker一次实际exit0：input/backend pin、扰动拒绝、保存的generated bytes、非kernel AST不变、原signature只加False constexpr、浮点call AST、原单loop/earlyreturn、完整/partial/invalid和未对齐prefix不等式检查。stdout留在 `analysis/source/prefill-visible-prefix/cpu-check.log`。runtime/gate py_compile和--help过；最后仅descriptor guard窄化并更新gate pin，generated source不变，补py_compile，未扩CPU模拟suite。

framework owner已独立审kernel/runtime及完整两shape gate无阻断，并最终核定87c6的三个stride窄化只收窄scope、actual KV stride8192仍可选；d3db相对c1a仅更新policy pin，generated a6d不变。此CPU审阅后root已完成121838设备门，结果与证据阅读状态见顶部；仍无整模型accuracy/E2E性能结论。没有已执行失败需要隐藏；草稿的policy pin占位已补为最终hash，旧草稿SHA在handoff保留作为历史，不能上传旧版本。
