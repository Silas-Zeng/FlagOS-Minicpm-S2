#!/usr/bin/env python3
"""仅从既有登记生成中文团队视图；不修改/重验实验原件。"""
import csv
import fnmatch
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
TEAM = ROOT / 'team'
MARK = '<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->\n\n'
AVAILABLE = set()
GROUPS = {
    'gqa-grouped-simt': ('GQA grouped SIMT页内归约', '固定page16/N33/B40/S16/KV16K，把QK/PV改为FP32广播归约并保留P先BF16舍入与原reducer，尝试减少TCU填充/布局开销；增加SIMT算术及广播成本。8类数值、FP64抽样、Graph/输入RNG和实际w8无dot/MMA/无3D全局scratch机制通过。Event1.279744→44.634184ms（34.8774倍），wall1.286918→44.640352ms（34.6878倍），明显无净收益；SGPR/VGPR均无spill也不保证快。停止此路线、整模与扫参，预备模型入口不推进；旧0bf9/526组件不是新main34942的成绩。', []),
    'night-kernel-counters': ('夜间单核硬件计数尝试', '只对原baseline prefill/GQA单核尝试ixkn计数，复用旧worker，不是候选复测。Prefill wrapper -11，worker结果已写且有61440B报告，但离线导入报Unknown device name（空）；GQA因launch-skip=0不被工具接受而立即255，无结果或报告。两轮DB/source/native/所属进程组及设备清理通过，失败一次即跳过，不修工具或重跑。CLI未产生可用metric；原SQLite事件仅可有限匹配来源，计数含义未闭合，见页尾原值补充。本run全部timing禁作收益、官方成绩或新增组件资格。小原件已回收，夜间阶段空窗另补完整封存回执；旧小包index与原记录保持，未将工具失败改成完整可用profiler。', []),
    'prefill-stride': ('Prefill stride常量特化', '仅11项stride改constexpr并保留int64寻址，原normalized/Q-hoist浮点表达式、tile和页序不变。组件SGPR spill30→6/mul103→30，Event省0.5151%、wall慢0.5676%，数值/FP64/Graph及alternate17项通过。旧main0915的603/tree1127346e原官方4K/16K各四轮与实际激活全部通过，1536 SUCCESS；弃首轮5726.63/4052.78 tok/s、TTFT3637.47/124103.35ms，相对旧5758.72/4045.20观察−0.56%/+0.19%。KV547648对547536，非严格因果，只保留长输入小信号；不确认净收益、不合并、不授105资格或新比赛基线，不能混入新main34942/PR51。单序列组件页表行stride仅身份覆盖。', []),
    'prefill-log2': ('Prefill log2域换底', '在当前normalized＋Q-hoist中将score/max保持log2域，P与alpha直接exp2；不改tile/页序/地址。M2047/KV16K组件FP64抽样、writer、换值Graph与inputs/RNG通过；换底改变FP32舍入，不能称跨臂逐位。Event省0.2888%，wall慢0.9317%，第二次候选提交CPU4.58ms对其余约1.4ms，原轮保留。ASM换底乘法20→0，n_regs114→116/shared32K不变。仅保留微小GPU正信号，模型收益未确认；qmod仅runtime0，不授官方或105资格，后续GQA固定w4结果另列。', []),
    'gqa-four-page-t64': ('GQA四页T64计算块', '将page16按四页组成T64计算块，减少循环与地址开销。N33/B40/S16、KV16K三轮8类数值/Graph/FP64抽样通过，跨臂不要求逐位。原T64 Event慢126.9037%、固定w4仍慢64.7108%且mma仍[4,1]；最后真实N4布局实现[1,4]，Event1.278378→1.827178ms仍慢42.9294%，wall慢42.5630%。N4的SGPR99/spill68、VGPR88/shared32K，实际occupancy未证明。机制落地仍明显负，整个四页T64路线收口，不再扫参、不进4K或模型；原件保留，不授官方/105资格。', []),
    'native-silu-vec2': ('native SiLU相邻两列访存', '相邻两列用int2/float2读取并打包写回BF16，尝试降低尾处理地址/访存及CTA开销，原量化/GEMM/舍入顺序保持。BI-V150随机M2048/N12288/K2048，15个数值/Graph case及独立CPU参考通过；隔离尾处理Event慢6.9849%、完整gate慢2.4404%，均无净收益。只加载私有测试库，未接模型或替换生产native；停止此候选。实验PR52已创建为Draft并于15:01:05 UTC关闭，未合并；仅保存原组件实现与教训，不改生产路径。', ['native-silu-vec2']),
    'gqa-kv-stride': ('GQA stride常量折叠', '仅将5个K/V stride参数声明为constexpr，保留原cache策略、数学和reducer。N33/B40/S16、KV16K原8组数值/换值Graph边界和alternate-stride13项通过；总整数乘法27→13、页地址关联乘法12→0。Event省−0.0410%、wall省+0.0454%，无净收益，停止，不扩形状或进入模型。', []),
    'gqa-kv-cg': ('GQA KV读取缓存策略', '实际GQA内核4处K/V load改.cg，三个组件形状Event省2.6666%/1.3662%/1.2912%。旧官方首暖4944.66混有Q-hoist和compute-order失活，不能判.cg本体无收益；原main当期首暖5761.99，两轮部分对照保留。后继修正三处关联身份，实际确认Q-fragment install+selected和compute-order selected，4K冷/首暖5073.26/5362.19 tok/s、512成功。首暖相对历史5751.88及当期5761.99观察−6.7750%/−6.9386%，按规则主动停止，第三轮中断、16K/105不跑。KV547648对547536仍不同，非严格因果；本轮没有模型净收益，不合并/定基线，也不回改旧混杂结果。', []),
    'lm-head-paired-gemv': ('LM-head双行GEMV', '随机BF16 M2/N130560/K2048组件：原FlagGems linear固定配置对比唯一BN32/BK256/w8 paired-GEMV，FP64参考、换值/指针、guard/RNG通过。Event0.834885→2.045513ms，明显负，停止。未加载框架模型/native，也未取得模型或官方资格，不扩调参、不建优化PR。', []),
    'attention-head-major': ('Attention head-major分页读取', 'M2047/KV16K、page16三臂，当前GQA、原FlagGems head-major和新增page16 loader+N64均真实编译并通过独立FP64抽样及换值Graph。Event约8.366/29.733/82.944ms，候选明显负，停止。N64同时改变归约分块，非逐位保证，不拆成loader单项因果，不扩调参或创建优化PR。', []),
    'main-correctness': ('主线复核与native备用方案', 'PR48备用f2ca/tree5e07默认关闭native：原完整105为103/105，原mixed长题答85且计数正确；原官方4K/16K各四轮1536请求成功，弃首轮5271.89/3763.84 tok/s，Mean TTFT4281.63/137244.33ms。实际KV521936，FX0native，源码未变、DB恢复和清理通过。高于官方公告基线2028.01/915.15并满足TTFT要求；低于native-on性能参考5758.72/4045.20，但DB/KV不匹配，不能拆成单内核因果收益。保留备用，PR48仍Draft，不替换性能主线。\n\n官方105使用temperature1/top_p.95，旧main99/105仅说明该轮未达门槛，不能据此认定代码缺陷；temperature0专项重复token另行保留，尚未定位具体kernel/PR。旧1ad9不含PR25也复现，不能直接撤回24/25。用户要求主力继续吞吐探索；团队main0915/tree766b完整603文件的原105本轮100/105（95.2381%）通过，102 stop＋3 cap（94/99/101），0传输错误/空答案，actual34native、源码/native/DB恢复及清理通过。新结果与旧99/105并列保留；原mixed专项重复token仍未定位，不据此宣称mixed修复、稳定改善或全部合格基线。', ['native-safe-default']),
    'attention-next-k': ('Attention next-K寄存器预取', '在已测affine＋Q-hoist组件上，提前加载下一tile的K以尝试覆盖PV计算。首次逐位/guard/KV/RNG/Q检查通过，原ASM定位门失败、未计时；CPU后核定位到真实load，但其8条路径均在首PV前遇wait/barrier，预期重叠机制不成立，停止本实现。不是数值或已测性能失败。', []),
    'gqa-identity-rescale': ('GQA恒等rescale跳过', '仅当同组8头的finite最大值严格不变时省去rescale，其他分支与原reducer保留。N33/B40/S16及B32/S4分别完成8组数值/Graph检查，Graph ABBA耗时观察分别+2.308%/+1.058%；未见收益，不推进模型/官方。B32首次空padding验证器异常单列，独立v3修验证器后重测，未修改候选数学。均为随机输入组件，非实际激活重放。', []),
    'current-main-hotspot': ('当前main526热点分析', '16K自然mixed4/FULL8独立诊断，原runner/P/Q/native和服务参数保留。mixed后2步Attention约68.08%可见GPU；FULL只见整图，不能拆内部占比。用于选择优化方向，不报吞吐收益。', []),
    'attention-affine-pages': ('Attention连续页段寻址', '保持原KV分配与数学，对现存连续物理页段用仿射寻址。组件四布局逐位通过、局部耗时下降约5.0–6.9%；原四语义及三个串行prefill页表绑定通过，仅P恒等/C3prefix0。完整官方两档各四轮1536成功，弃首轮4K5741.68/16K4050.10 tok/s，相对main526观察−0.30%/+0.12%；KV546432对547536，不确认净收益、不定基线、不追加105。', []),
    'selected-query-row': ('末层Query精确选行', '仅末层Attention选择需要输出的Query，完整M行K/V仍保留；组件核P映射、metadata、全slot字节及独立参考差异，不是模型准确率或端到端收益。', []),
    'rope-kv-fusion': ('RoPE与KV写入融合', '保持526的RoPE旋转数学与Q/K输出，在同一核追加完整KV写入。生产v2外置autotune元数据，四语义及实际42融合/0旧KV/34native图通过；性能筛选6完整轮未见净正信号，按用户要求早停并封存，不更新基线或追加105。组件正信号、首轮记录/模型失败和全部原始测量分别保留。', []),
    'final-ffn-row-prune': ('末层FFN/o_proj选行与模型对照', '原FFN527及unbacked v3均遇mixed长题不完成；原main526同mixed也失败、精确同请求serial通过，不能归因选行，根因未确认。v3解决S1的AOT检查节点问题并通过三语义；不恢复模型资格、不进性能。原失败保留，不为通过候选强改框架。', []),
    'pr25-kv-current': ('PR25 与缓存修复后的 KV 保存恢复', '当前性能对照基线已更新到main0bf9/tree8671（526文件、SO14f）：161030按官方4K/16K各四轮，第2–4轮5758.72/4045.20 total tok/s，TTFT3626.85/124212.05ms，1536/0；KV547536、初始DBfb035。该版本本实例完整105为99/105（94.2857%），未达至少100正确的门槛，不具比赛基线准确率资格；完整结果见当前main基线正确性方法。532组合155917 VERIFY1与4题语义门通过；171101正式测量前因目录前缀被图门误拒，原exit1和后验强身份相同证据保留，不记吞吐。172742第二次启动因额外compiled graph日志文案门误拒，仍未发正式benchmark；原exit1与随后failed-log-replay分开保留，CPU回放不算本轮模型资格。174713按更新的筛选规则主动早停：4K第2–4轮5702.26（−0.98%）；16K第2–3轮3966.86对基线同轮4045.15（−1.94%），第4轮不完整，不计官方完整结果或新基线。18:38:01 UTC清理/source/native/DB恢复通过。候选期间另有远端证据归档、背景主机负载未完全匹配，负差仅为实测观察，不严格归因KV，不重复跑解释负差。183929独立42层搬运诊断给出0.31–0.34s毛预算，未计gather/scatter、索引与scratch，不代表staging净收益。535的184509 VERIFY1字节与4题语义门通过；185439两轮4K5403.92/5732.73、16K3824.19/4066.32，768/0、14条完整FULL链。KV546432对526的547536，gain_calculated=false，不确认稳定收益。原测量/清理成功，但外层比较state结构异常，原日志与另存posthoc均保留。192645真实staging primitive三对wall净省322.382/347.481/314.353ms，仅独立微测、不计模型收益。535官方193100已完成两档各四轮、1536/0，第2–4轮4K5703.70/16K4060.24 tok/s，TTFT3635.20/123213.90ms；28条完整FULL链、VERIFY0。20:29:16 UTC清理/source/native/DB恢复通过；KV546432对526547536，比较仅actual_kv失配、gain_calculated=false，差值null，只记组合绝对观察。完整105尚未通过，不设新基线；不含staging primitive。 538 staging的203135已通过真实服务VERIFY1、4/4语义及34native新图，32请求、每向729415680字节、42 kernels＋43 DMA与临时释放通过，KV547536；含回读、非性能或完整105。\n\n队友[PR31](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/31)实际受测e972997、SO271327a0，暖后单轮4K/16K为5766.41/4048.28，准确率102/105；标题Draft且未合并。[原manifest](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/manifest.json)与[acceptance](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/acceptance.json)保留其边界。双方源码、SO、轮数及DB/KV不完全同条件，不直接算收益；上述队友状态来自当时读取的固定证据，不代表其后续PR实时状态，不自动更新本实例基线。\n\n前序7596共同基点的两轮筛选继续保留：同KV546432与DB，4K+0.103%/+0.644%但无FULL覆盖，16K+4.728%/−0.493%；仅保留候选，不确认稳定收益，不把旧组合成绩赋给新main。\n\n538的204402两轮筛选：4K5544.36/5615.02、16K3845.32/4078.31，768成功；暖轮对526 R2观察−2.38%/＋0.82%。KV546528≠547536，gain_calculated=false，非因果/稳定收益。清理、source/native与DB恢复通过；保留进入完整测量，本批不提前写其结果或更新基线。\n\n最新收尾：538 staging原官方4K/16K各四轮、1536请求全成功；原后三轮均5724.16/4079.71 tok/s，相对526观察−0.60%/+0.85%。KV546528对547536，比较器actual_kv失配/gain_calculated=false，不称严格因果或稳定净收益。22:31:50 UTC源码/native未变、DB恢复、清理成功。保留长输入信号，暂不定新基线、不追加105。', ['native-quant-cache', 'native-cache-identity']),
    'native-cache-identity': ('native 编译缓存身份与重启', 'PR25叠加native编译缓存身份修复，保留默认缓存目录和官方serve参数。135749完成49项组件门但checker误拒<think>格式，原失败保留；141536复用组件证据、4个语义请求全对（含4908token），同AOT与34层native图重启成功。原首启图证据由重启前首次补存，不能伪称首轮已归档。两轮均非官方准确率或吞吐，不继承前序PR24完整准确率。', ['native-cache-identity']),
    'pr24-main': ('PR24 真实路径复验与 KV 诊断', '131603同源码隔离编译缓存后，实际新图有34个native调用（layer4..37），完整Math500 Level3为100/105通过；0请求错误/0空最终，83/99/101达到输出上限，101无可提取答案。该结果仅证明本轮路径与准确率，不报吞吐或精度提升。105037至124000六轮仍因旧AOT图失配撤回PR24模型资格；standalone9、CPU/trace观察与VERIFY1字节事实保留，旧Attention1.018秒不能作有效PR24预算，也不追溯恢复旧性能资格。默认缓存修复和PR25复验另记。', ['pr24-main']),
    'accepted-fill': ('省去无消费者的 accepted GPU fill', '固定非推测Full路径保留CPU fill，省略无消费者的accepted-count GPU fill。064838→065325两侧32成功0失败，吞吐表观−0.235046%，但KV521840→521936不同，31门仅same_KV失败、gain=null；当前不集成，保留小负及失配证据。冷ENABLED后同Engine原CPU_METADATA_FIRST_SELECTED只证明首次prepare，不证明全程/GPU数值或新准确率。', []),
    'compute-order': ('计算顺序与采样顺序分离', '计算行重排以适配Attention路径，采样保持原请求顺序。PR15+PR21兼容组合已由PR22合入；142019完整105题102正确（97.1429%）通过，173454原官方8轮全部成功，第2–4轮均值4K5118.99、16K3436.17 total tok/s。该组合的官方16K KV为521936；这是组合绝对结果，不作两个方法的单项因果拆分。旧423短测、三题质量、结构映射与独立参考证据保留，不能替代新组合结果。', ['compute-order']),
    'allocator-noop': ('KV 分配器无状态快返', '普通decode不新增页或完整块哈希时返回原空分配结果；保留新页、哈希、恢复与非RUNNING原路径，CPU片段和服务配对分别记录。', []),
    'kv-restore-pitched': ('KV 二维 FULL 恢复', '保留原页序、私有页资格和完成事件，合并H2D提交；独立单层字节门与真实42层事务分开记录，调用数下降不当作性能收益。', []),
    'skip-computed-h2d': ('省去无消费者的 computed H2D', 'CPU metadata成功时省略一次计数GPU副本提交，保留原回退和固定buffer/event；方法门与独立短服务单pair分别记录，不与KV组合收益相加。', ['skip-computed-h2d']),
    'finite-growth-admission': ('有限窗口增长准入', '真实服务消除本轮抢占，但共同DB对照仍有KV容量失配；默认关闭保留研究证据，不宣称确定收益。\n\n两轮原 bc51 smoke 仅作启动显存诊断：共同 observer 下，finite 的非 Torch 内存多 4 MiB，差异在 before_profile 已存在；KV 为 baseline 521936、finite 521840，与旧性能对照方向相反。四端 DB 均为 532 表、19839 行且三项 SHA 一致；文本及 32 个 token ID 相同，但未覆盖 mixed Q/GQA 命中，不算准确率或性能收益。停止追查启动差异，旧性能对照仍因 KV 容量失配而不能归因。', []),
    'admission-observer': ('有限增长准入观察', '当前Q+GQA上的稀疏CPU准入与失败状态诊断；不实现预留策略，不把页预算反事实当作吞吐收益。', []),
    'q-gqa-framework': ('Q-hoist + GQA 框架组合', '仅适配精确GQA包装的安装身份，保留两条算术路径与原服务参数；已获单pair正信号及独立101/105准确率通过，评测DB增长另列。', []),
    'async-bookkeeping': ('异步输出 CPU 批量记账', '将有效单 token 异步输出的逐行 CPU 数组更新合并，保留请求历史、事件与回退；服务对照的 KV 失配单列。', []),
    'bq16-chunk-alignment': ('BQ16 chunk 形状对齐', '复用现有 C2/C3 与原算子，比较七段恢复链的 chunk 形状；局部正信号保留，未实现调度器或接入服务。', []),
    'prefix-scan': ('公共前缀扫描', '在实际不支持cascade的后端中检查公共前缀统计成本；观察诊断与跳过扫描的真实服务结果分开记录。', []),
    'q-fragment-hoist': ('Q fragment 循环外保留', '把唯一BF16 prefill Attention的Q local_load移到唯一K循环外并保持fragment活跃。默认由提交代码启用，保留normal fallback与精确源码/ABI/IR检查；PR23已合入main。官方1536请求、两档各4轮验证中4K/16K为5313.59/3764.67 total tok/s，较PR15+PR21旧基线+3.80%/+9.56%；完整Math500 L3为100/105通过。实际选中且fallback0，shared65536→32768、循环内Q read0。DB种子相同但KV521840对521936，不包装为严格等KV单项因果。', ['q-fragment-hoist']),
    'gpu-hotspots': ('当前版本GPU热点', '复用原轨迹并按需补短native诊断；GPU路径占比只用于选择下一实验，不作吞吐成绩。', []),
    'decode-cpu-gather': ('纯decode CPU gather跳过', '严格纯decode省略无消费者的CPU输入整理；正确性门通过，当前服务候选负收益，不集成。', []),
    'c3-views': ('C3重复视图清理', '复用mixed Attention中的视图，减少重复slice/unbind；短输入信号与大输入、真实服务结果分别记录。', []),
    'hot-key': ('Attention热key复用', '复用绑定后的key/cache并保留原launch尾；未命中、实际命中及负结果都保留。', []),
    'input-prep': ('输入准备成本诊断', '当前组合的真实输入等待与预处理累计；诊断耗时不作为性能收益。', []),
    'cpu-combination': ('CPU metadata + async token 组合', '两种CPU准备方法的组合；方法正确性与短服务性能分别记录。', ['cpu-metadata', 'async-token-update']),
    'cpu-metadata': ('CPU metadata 复用', '复用已计算的CPU视图，写回原GPU缓冲区；回退和事件边界见原报告。', ['cpu-metadata']),
    'async-token': ('异步 token 更新', '整数gather/scatter更新；既有索引、stream和回退条件保留。', ['async-token-update']),
    'kv-pitched': ('KV 二维 SAVE 复制', '保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。', ['kv-pitched-copy']),
    'kv-contiguous': ('KV 连续页复制', '连续页合并提交工具；提交不是完成ACK，工具与服务协议分开看。', ['kv-contiguous-copy']),
    'kv-progress': ('抢占请求选择与进展', '抢占瞬间观察、请求选择及其对照；失配结果也保留。', []),
    'kv-memory': ('KV 启动内存观察', '启动内存组成和容量分项诊断，不作为性能成绩。', []),
    'kv-protocol': ('KV 保存 / 恢复协议', '单victim、容量下界、私有页序与FULL恢复；VERIFY诊断不等于性能。', []),
    'kv-observation': ('KV 生命周期观察', '分配失败、抢占与恢复的观察原件，不自动等于可回收机会。', []),
    'admission': ('准入与输出增长', '准入候选及其负结果、未激活和容量限制。', []),
    'mapped-attention': ('非前缀 decode 映射', '单层构造、服务实际命中与重复结果分开记录。', []),
    'mm-cta': ('矩阵乘 CTA 分组', '固定tile下的映射与守卫诊断；单层收益不外推服务。', []),
    'buffers': ('缓冲区 gather 与 token bucket', '输入几何、padding和缓冲区复用候选。', []),
    'event': ('Event / graph 能力与等待', '能力门、完成性及等待CPU的正负结果。', []),
    'sql': ('SQLite 反射及 SQL+C2/C3 组合', '目标反射与历史组合；#9/#10只用于组合来源导航，组合成绩不能拆分归于单项方法，也不表示#8必须依赖两者。', ['sql-reflection', 'decode3d', 'mixed-attention']),
    'official': ('完整官方吞吐对照', '原版与完整候选的原始官方结果；保留DB、KV和计分边界。', []),
    'attention': ('Attention 分流与 launch', 'prefill、3D decode、mixed分流、可见prefix及重叠等路径；相关PR不等于各实验已包含或独立验证全部方法。', ['prefill', 'decode3d', 'mixed-attention']),
    'early': ('早期集成、块表与 profile', '早期基点、块表提交、集成短筛和profile，不自动作为诊断开关或top-p单项性能。', ['diagnostics', 'top-p']),
    'native-k8-sme': ('NativeK8 SME K页布局探针', '独立布局搬运探针：CoreX compile-only产物身份匹配；16个模式/页/head案例的2048B K-stage图像与A逐字节一致，CPU reference、输入不变和guard均通过。仅证明该full-page stage布局行为，不测Attention数学、partial page、模型/服务正确性、吞吐或生产资格。', []),
    'other': ('其它登记与控制记录', '没有足够字段继续归类的登记；不补猜实验结论。', []),
}
CODE = {
    'gqa-grouped-simt': ['experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/source/candidate.py', 'experiments/framework/20261025T181007536717Z-gqa-grouped-simt-hotspot-component/results.json'],
    'night-kernel-counters': ['experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/source/entry.py', 'experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/profile-import.txt', 'experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/prefill-baseline.ixkn-rep', 'experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/worker.log'],
    'prefill-stride': ['experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/source/kernel.diff', 'experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/source/alternate_stride.py', 'experiments/framework/20261025T161135828367Z-prefill-stride-constexpr-component/results.json', 'experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds/benchmark_results/raw_runs_20261026_011033.csv', 'experiments/framework/20261025T170831Z-main0915-prefill-stride-four-rounds-control/prefill-activation.json'],
    'prefill-log2': ['experiments/framework/20261025T152608409713Z-prefill-log2-component/source/kernel.diff', 'experiments/framework/20261025T152608409713Z-prefill-log2-component/source/worker.py', 'experiments/framework/20261025T152608409713Z-prefill-log2-component/results.json'],
    'gqa-four-page-t64': ['experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/ir-candidate/ttgir.txt', 'experiments/framework/20261025T154256643502Z-gqa-four-page-t64-n4-hotspot-component/results.json', 'experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/source/kernel.diff', 'experiments/framework/20261025T152940014266Z-gqa-four-page-t64-w4-hotspot-component/ir-candidate/ttgir.txt', 'experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/kernel.diff', 'experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/worker.py', 'experiments/framework/20261025T151303364296Z-gqa-four-page-t64-hotspot-component/source/fp_reference.py'],
    'native-silu-vec2': ['experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/native_w8a8.cu.diff', 'experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/native_w8a8.cpp.diff', 'experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/worker.py', 'experiments/framework/20261025T143942955934Z-native-silu-vec2-component/source/asset-pins.json'],
    'gqa-kv-stride': ['experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/source/kernel.diff', 'experiments/framework/20261025T134407482450Z-gqa-kv-stride-main-hotspot-component/source/worker.py'],
    'gqa-kv-cg': ['experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/stack-activation.json', 'experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/plugin-source/vllm_fl/patches/biv150_q_fragment_service.py', 'experiments/framework/20261025T154544Z-main0915-gqa-kv-cg-closed-four-rounds-control/plugin-source/vllm_fl/patches/biv150_compute_order.py', 'experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds/server.log', 'experiments/framework/20261025T140749Z-team-main0915-current-official-four-rounds/server.log', 'experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/kernel.diff', 'experiments/framework/20261025T130020159833Z-gqa-kv-cg-hotspot-component/source/worker.py'],
    'lm-head-paired-gemv': ['experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/candidate.py', 'experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/installed-linear.py', 'experiments/framework/20261025T130418879497Z-lm-head-paired-gemv-component/source/worker.py'],
    'attention-head-major': ['experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/source/candidate.diff', 'experiments/framework/20261025T130735173560Z-head-major-paged-prefill-component/source/worker.py'],
    'main-correctness': ['experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-response.json', 'experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/mixed-requests/prefill-tokens.json', 'experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/diagnostic-summary.json', 'experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic/analysis/tokenizer-special-ids.json', 'experiments/framework/20261025T094755Z-main526-mixed-token-diagnostic-control/diagnostic_requests.py', 'experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/accuracy-review.json', 'experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/state.json', 'experiments/accuracy/20261025T095054Z-main0bf9-main-math500-control/archive-receipt.json', 'experiments/accuracy/20261025T095054Z-main0bf9-main-math500/math500-level3/20261025_175201/reports/minicpm/math_500.json', 'experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic-control/state.json', 'experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/mixed-requests/prefill-tokens.json', 'experiments/framework/20261025T103226Z-pr24-467-mixed-token-diagnostic/model-path/evidence.json', 'experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic-control/state.json', 'experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/mixed-requests/prefill-response.json', 'experiments/framework/20261025T104211Z-pr24-467-native-disabled-mixed-token-diagnostic/model-path/evidence.json', 'experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/accuracy-review.json', 'experiments/accuracy/20261025T110044Z-native-safe-default-math500-control/model-path/evidence.json', 'experiments/accuracy/20261025T110044Z-native-safe-default-math500/source/plugin/vllm_fl/patches/biv150_native_w8a8.py', 'experiments/framework/20261025T112705Z-native-safe-default-mixed/mixed-requests/prefill-response.json', 'experiments/framework/20261025T112705Z-native-safe-default-mixed-control/model-path/evidence.json'],
    'attention-next-k': ['experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/kernel.diff', 'experiments/framework/20261025T085807255866Z-attention-next-k-register-component/source/worker.py', 'experiments/framework/20261025T085807255866Z-attention-next-k-register-component/analysis/posthoc-cpu/result.json'],
    'gqa-identity-rescale': ['experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/kernel.diff', 'experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/worker.py', 'experiments/framework/20261025T090302472109Z-gqa-identity-rescale-v2-hotspot-component/source/padding-source.json', 'experiments/framework/20261025T091037578775Z-gqa-identity-rescale-v2-b32-component/source/worker.diff'],
    'current-main-hotspot': ['analysis/current-main-hotspot-20261025/072151-analysis-v2.json', 'analysis/current-main-hotspot-20261025/072151-attribution-check.json', 'analysis/current-main-hotspot-20261025/analyze.py'],
    'attention-affine-pages': ['experiments/framework/20261025T074041Z-attention-affine-pages-model-verify-control/plugin-source/vllm_fl/patches/biv150_attention_affine_pages.py', 'experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py', 'experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py'],
    'selected-query-row': ['archive/candidates/20261025-final-rows/final-query-row-model-candidate/candidate.diff', 'experiments/framework/20261025T005351Z-final-query-row-component/state.json', 'experiments/framework/20261025T013820Z-final-query-row-component-v2/state.json', 'experiments/framework/20261025T014029Z-final-query-row-component-v3/state.json'],
    'rope-kv-fusion': ['experiments/framework/20261024T203032Z-rope-kv-component/results.json', 'experiments/framework/20261024T203032Z-rope-kv-component/state.json', 'experiments/framework/20261024T203032Z-rope-kv-component/archive-receipt.json', 'experiments/framework/20261024T203809Z-rope-kv-component-config-v2/results.json', 'experiments/framework/20261024T203809Z-rope-kv-component-config-v2/state.json', 'experiments/framework/20261024T203809Z-rope-kv-component-config-v2/archive-receipt.json', 'experiments/framework/20261024T211606Z-rope-kv-model-verify-control/state.json', 'experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/source-diff.json', 'experiments/framework/20261024T211606Z-rope-kv-model-verify-control/failed-posthoc/0-computation_graph.py', 'experiments/framework/20261024T211606Z-rope-kv-model-verify-control/archive-receipt.json', 'experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/state.json', 'experiments/framework/20261024T223155Z-rope-kv-model-verify-v2-control/archive-receipt.json'],
    'final-ffn-row-prune': ['experiments/framework/20261024T204020Z-final-ffn-row-prune/results.json', 'experiments/framework/20261024T204020Z-final-ffn-row-prune/state.json', 'experiments/framework/20261024T204020Z-final-ffn-row-prune/archive-receipt.json', 'experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/results.json', 'experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/state.json', 'experiments/framework/20261024T211402Z-final-ffn-row-prune-logger-v2/archive-receipt.json', 'experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/state.json', 'experiments/framework/20261024T223346Z-final-ffn-row-model-verify-control/archive-receipt.json'],
    'pr25-kv-current': ['analysis/pr25-kv-current-pair.json', 'experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json', 'experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json', 'experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/model-path/semantic-validation.json', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/summary_20261025_001229.csv', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/state.json', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/archive-receipt.json', 'experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds/result.json', 'experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds-control/postfailure-cache-audit/audit.json', 'experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds/result.json', 'experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/state.json', 'experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/archive-receipt.json', 'experiments/framework/20261024T172742Z-main0bf9-kv-official-four-rounds-control/failed-log-replay/model-path/evidence.json', 'experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds/benchmark_results/raw_runs_20261025_014809.csv', 'experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/early-stop-decision.json', 'experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/state.json', 'experiments/framework/20261024T174713Z-main0bf9-kv-official-four-rounds-control/archive-receipt.json', 'experiments/framework/20261024T183929Z-kv-staging-budget/results.json', 'experiments/framework/20261024T183929Z-kv-staging-budget/state.json', 'experiments/framework/20261024T183929Z-kv-staging-budget/archive-receipt.json', 'experiments/framework/20261024T184509Z-main0bf9-kv-restore-pitched-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T184509Z-main0bf9-kv-restore-pitched-verify1-context16k-long/model-path/semantic-validation.json', 'experiments/framework/20261024T184509Z-main0bf9-kv-restore-pitched-verify1-context16k-long-control/archive-receipt.json', 'experiments/framework/20261024T185439Z-main0bf9-restore-pitched-kv-fullsize-screen/result.json', 'experiments/framework/20261024T185439Z-main0bf9-restore-pitched-kv-fullsize-screen-control/transactions.json', 'experiments/framework/20261024T185439Z-main0bf9-restore-pitched-kv-fullsize-screen-control/original-owner.log', 'experiments/framework/20261024T185439Z-main0bf9-restore-pitched-kv-fullsize-screen-control/posthoc/posthoc-comparison.json', 'experiments/framework/20261024T185439Z-main0bf9-restore-pitched-kv-fullsize-screen-control/archive-receipt.json', 'experiments/framework/20261024T192645Z-kv-staging-primitive/results.json', 'experiments/framework/20261024T192645Z-kv-staging-primitive/build/manifest.json', 'experiments/framework/20261024T192645Z-kv-staging-primitive/archive-receipt.json', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/benchmark_results/raw_runs_20261025_033156.csv', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds/benchmark_results/summary_20261025_033156.csv', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/state.json', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/comparison.json', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/transactions.json', 'experiments/framework/20261024T193100Z-main0bf9-restore-pitched-kv-official-four-rounds-control/archive-receipt.json', 'experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen-control/comparison.json', 'experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen-control/state.json', 'experiments/framework/20261024T204402Z-main0bf9-staging-kv-fullsize-screen-control/archive-receipt.json', 'experiments/framework/20261024T213346Z-main0bf9-staging-kv-official-four-rounds-control/state.json', 'experiments/framework/20261024T213346Z-main0bf9-staging-kv-official-four-rounds-control/archive-receipt.json'],
    'native-cache-identity': ['experiments/framework/20261024T135749Z-pr25-cache-first-restart/failure.txt', 'experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/gate-auto.json', 'experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/cached-dispatch.json', 'experiments/framework/20261024T135749Z-pr25-cache-first-restart-control/archive-receipt.json', 'experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/result.json', 'experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/prior-audit/audit.json', 'experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/requests.json', 'experiments/framework/20261024T141536Z-pr25-cache-restart-recheck/startup-2/graph-evidence.json', 'experiments/framework/20261024T141536Z-pr25-cache-restart-recheck-control/archive-receipt.json'],
    'pr24-main': ['CURRENT_WORK.md', 'experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/accuracy-review.json', 'experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph-typed-assignment-check.json', 'experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/active-graph/computation_graph.py', 'experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/environment-overrides.json', 'experiments/accuracy/20261024T131603Z-pr24-isolated-cache-math500-control/archive-receipt.json', 'experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/loaded-computation-graph.py', 'experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/early-stop-request.json', 'experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/state.json', 'experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds-control/archive-receipt.json', 'experiments/framework/20261024T124000Z-pr24-main-fullsize-two-rounds/result.json', 'experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/state.json', 'experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/observer-manifest.json', 'experiments/framework/20261024T122225Z-pr24-kv-swap-v1-verify1-context16k-long-control/archive-receipt.json', 'analysis/pr24-kv-diagnostic.json', 'analysis/pr24-resume-native-v2-114500.json', 'analysis/pr24-resume-native-failure.json', 'analysis/pr24-resume-db-comparison.json', 'experiments/framework/20261024T105037Z-pr24-main-context16k-control/summary.json', 'experiments/framework/20261024T105037Z-pr24-main-context16k-control/native-build-manifest.json', 'experiments/framework/20261024T105037Z-pr24-main-context16k-control/operator-check.json'],
    'accepted-fill': ['analysis/accepted-fill-service-pair.json'],
    'skip-computed-h2d': ['analysis/pr15-computed-h2d-accuracy.json', 'analysis/skip-computed-h2d-service-pair.json'],
    'compute-order': ['analysis/compute-order-current-main-official.json', 'analysis/compute-order-current-main-accuracy.json', 'analysis/compute-order-current-main-pair.json', 'archive/ai/20261022-framework-kv/compute-order-main-profile/README.md', 'analysis/compute-order-math4-event-130351.json', 'analysis/compute-order-math4-event-125330.json', 'analysis/compute-order-service-retest-pair.json', 'analysis/compute-order-math4-summary.json', 'analysis/compute-order-structure.json', 'analysis/compute-order-oracle-summary.json', 'analysis/compute-order-oracle-085500.json', 'analysis/compute-order-first-layer.json', 'experiments/framework/20261023T075210Z-compute-order-shadow-context16k-control/shadow-artifacts/8403/result.json', 'archive/ai/20261022-framework-kv/compute-order-shadow-gate/README.md', 'experiments/framework/20261023T070816Z-compute-order-answer-baseline/context-16k/answer-summary.json', 'analysis/compute-order-service-pair.json', 'analysis/compute-order-accuracy.json', 'docs/agent-work/framework_innovation.md', 'docs/agent-work/compute_order_review.md', 'experiments/framework/20261023T054306Z-compute-order-baseline-context16k-progress/completion.json'],
    'allocator-noop': ['archive/ai/20261022-framework-kv/next-kv-noop-allocate/README.md', 'analysis/allocator-noop-service-pair.json'],
    'kv-restore-pitched': ['archive/ai/20261022-framework-kv/q-gqa-kv-restore-pitch/README.md', 'analysis/kv-pitched-restore-method.json'],
    'finite-growth-admission': ['analysis/finite-growth-common-db-service-pair.json', 'analysis/finite-growth-warm-service-pair.json', 'analysis/finite-growth-service-pair.json', 'analysis/current-kv-memory-smokes.json'],
    'admission-observer': ['experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/biv150_admission_observer.py'],
    'q-gqa-framework': ['archive/ai/20261022-framework-kv/q-gqa-framework/METHOD.md', 'archive/ai/20261022-framework-kv/q-gqa-framework/biv150_q_fragment_service.py', 'analysis/q-gqa-service-pair.json', 'experiments/accuracy/20261022T184819Z-q-gqa-framework/accuracy-review.json'],
    'async-bookkeeping': ['archive/ai/20261022-framework-kv/async-bookkeeping/biv150_async_bookkeeping.py', 'archive/ai/20261022-framework-kv/async-bookkeeping/compare_service_pair.py', 'analysis/async-bookkeeping-service-pair.json'],
    'bq16-chunk-alignment': ['archive/ai/20261022-framework-kv/bq16-chunk-alignment/validate_bq16_chunk_chain.py', 'archive/ai/20261022-framework-kv/bq16-chunk-alignment/result-review.json'],
    'q-fragment-hoist': ['analysis/qfragment-pr15-pr21-final.json', 'analysis/qfragment-adaptation.json', 'archive/ai/20261022-current-gpu-hotspots/q-hoist-service/biv150_q_fragment_service.py', 'archive/ai/20261022-current-gpu-hotspots/q-hoist-service/compare_q_service_pair.py', 'analysis/q-fragment-service-pair.json'],
    'decode-cpu-gather': ['archive/ai/20261022-next-service-queue/next-decode-gather/biv150_decode_cpu_gather.py'],
    'c3-views': ['patches/framework/candidates/biv150_c3_view_reuse.py'],
    'hot-key': ['patches/framework/candidates/biv150_attention_key_recipe_v2.py'],
    'input-prep': ['scripts/remote/input-prep-timing-combined/prepare_input_prep_timing.py', 'scripts/remote/input-prep-timing-combined/biv150_input_prep_timing.py'],
    'cpu-combination': ['docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py', 'patches/framework/biv150_cpu_metadata.py', 'patches/framework/biv150_async_token_update.py'],
    'cpu-metadata': ['patches/framework/biv150_cpu_metadata.py'],
    'async-token': ['patches/framework/biv150_async_token_update.py'],
    'kv-contiguous': ['patches/framework/biv150_kv_page_copy.py'],
    'kv-pitched': ['patches/framework/candidates/biv150_kv_pitched_copy.py', 'patches/framework/candidates/biv150_kv_pitched_bridge.cpp'],
    'sql': ['patches/framework/biv150_sql_reflection.py'],
    'event': ['scripts/remote/validate_event_wait_gate.py', 'scripts/remote/validate_native_event_wait_gate.py'],
    'native-k8-sme': ['analysis/publication-k8-sme-20261029/experiment-note.md', 'tmp/native-k8-sme-probe-20261029/native_k8_sme_probe.cu', 'tmp/native-k8-sme-probe-20261029/assembly-review.json', 'tmp/native-k8-sme-probe-20261029/terminal-review.json'],
}


BATCH_RESULTS = {'affine_official_no_confirmed_gain': ('官方两档各4轮、1536成功；弃首轮5741.68/4050.10 tok/s，观察−0.30%/+0.12%。KV失配，不确认净收益。', '保留完整结果及局部正信号；未确认净收益，不定新基线、不追加105。', '官方完成，净收益未确认', '原官方4K/16K各四轮、弃首轮；输入4096/16384、输出1024、并发64、每轮256/128请求；官方脚本与服务参数不变。'), 'next_k_mechanism_no_go': ('首次逐位/guard/KV/RNG/Q通过；ASM定位门失败，未计时。CPU后核发现实际PV前wait/barrier，重叠机制NO-GO。', '停止本实现；保留原失败与独立CPU后核，不宣称数值失败或性能回退。', '机制不成立，未计时', '真实affine＋Q-hoist对照；首次组件检查后在ASM定位门退出。CPU后核分析已回收IR，未启动GPU或换页复验。'), 'gqa_padding_checker_failed': ('B32无padding，验证器空切片.all()触发ZeroDivisionError；完整数值检查和计时未形成，不判候选数值失败。', '保留验证器失败；独立v3只修空padding检查，后继结果另列。', '验证器异常，未计时', '实际生产GQA＋reducer的B32/S4组件；首组padding检查异常，未执行完整Graph ABBA。'), 'gqa_rescale_hotspot_negative': ('N33/B40/S16：8组数值/Graph检查通过，event1.280913→1.310480ms（耗时+2.308%）；随机组件负信号。', '保留负结果，不推进模型或官方测试；不将局部差异外推端到端。', '组件检查通过，未见收益', '固定16384随机输入，实际生产GQA＋reducer；8组边界及变输入Graph对fresh基线，关闭profiler的16-call Graph ABBA。'), 'gqa_rescale_b32_negative': ('v3仅修空padding检查；B32/S4的8组数值/Graph通过，event1.029569→1.040463ms（+1.058%），wall+0.949%。', '两档均未见收益，收口保留原件，不推进模型或官方测试。', '组件检查通过，未见收益', '固定16384随机输入，实际生产GQA＋reducer；v3验证器保留原数学及16-call Graph ABBA。run后缀仍v2，源码pins识别v3。')}


BATCH_RESULTS.update({'main_mixed_token_failed': ('原main mixed再次失败：长题ID8一次＋ID0重复1023次，词表为<think>＋<s>；计数正常。根因未定位，原exit1保留。', '保留基线故障证据；不恢复淘汰候选，不归因M8或全部main，完整105独立判分。', '主基线mixed语义失败，根因待定位', 'freshserver原双请求及首内容同步，仅加return_token_ids；长题4652输入/max_tokens1024，原JSON/SSE/token IDs全部保存。')})


BATCH_RESULTS.update({'main_accuracy_rejected': ('原官方完整105题99/105（94.2857%），valid/reject；105请求成功、0传输错误，4题达到输出上限，0空最终/提取。', '保留完整结果；当前main不具比赛基线准确率资格，已知mixed错误仍待定位，不归因某PR、不反复运行取最好成绩。', '完整105未达标，基线资格不通过', '固定main0bf9/tree8671、526文件/native14f；原105题脚本、服务与评分参数不变，原review_accuracy_gate.py核105唯一题/原预测评审及至少100正确门槛。')})

BATCH_RESULTS.update({'old467_mixed_token_failed': ('旧467/a42完整组合也失败：长题ID8、220后ID0重复1022次，length耗尽1024；计数正常，实际34native通过。', '保留旧版同场景失败；直接回退该版本不能被视为已解决，不单独归因某PR。诊断原标签main526保留，实际state为467。', '旧完整组合也复现mixed失败', '恢复131603完整源码/native及新隔离缓存策略，freshserver原双请求与token返回字段不变；原失败/响应/实际图保留，无性能测量。')})

BATCH_RESULTS.update({'old467_native_off_mixed_pass': ('旧467仅关闭native后双请求通过：实际图0 native、installed False；长题57tokens答85，计数299tokens正确。', '保留正确性隔离证据，重点收敛native路径及执行/内存差异；不归因具体kernel/PR，不作优化或提交资格，当前main99/105 reject不变。', '关闭native后本边界恢复，仅诊断', '旧467源码/SO不改，沿相同新隔离缓存、原双请求/采样，仅环境清洗后设既有native开关0；保存实际0 native图与installed False证据。')})

BATCH_RESULTS.update({'native_safe_default_accuracy_pass': ('f2ca/527默认关闭native：原完整105为103/105（98.0952%），105 success/stop，0传输错误/空输出/cap；actual FX0native。', '保留本恢复候选完整准确率通过；不继承给未合并main，不恢复旧失败，吞吐代价仍在原官方测量中。', '恢复候选完整105通过', '原105题/采样/服务与评分器不变；清native环境覆盖，实际提交默认关闭及FP/FX/AOT身份、完整源码后态和DB恢复闭合。'), 'native_safe_default_mixed_pass': ('同f2ca/527默认关闭路径：原mixed长题4652输入、15tokens答85，计数299tokens正确，actual FX0native。', '保留同源码边界通过并与本候选103/105配套；PR48仍Draft，不表示全部根因已定位或获得新性能基线。', '恢复候选原mixed通过', 'freshserver原双请求及token返回字段不变；无native覆盖、默认共享cache0，核实际FP/installed False/FX0native及源码/DB/清理。')})

BATCH_RESULTS.update({'native_safe_default_official_complete': ('原官方两档各四轮1536请求全部成功；弃首轮4K/16K为5271.89/3763.84 tok/s，Mean TTFT4281.63/137244.33ms。', '结合同源103/105与mixed通过，保留备用，不替换性能主线；PR48仍Draft。', '备用方案完整官方性能完成', '原0813脚本/官方服务参数与四轮弃首轮口径不变；actual KV521936/FX0native。相对native-on的DB/KV不同，不作单内核因果结论。')})

BATCH_RESULTS.update({'team_main0915_accuracy_pass': ('团队main0915本轮原105为100/105（95.2381%），105 success、102 stop＋3 cap（94/99/101），0传输错误/空答案。', '保留本轮达标与旧99/105；mixed重复token专项未定位，不宣称已修复或建立全部合格基线。', '团队main本轮105达标，专项异常仍保留', '0915/tree766b完整603文件，生产同原526/native14f且actual34层；原105题、temperature1/top_p.95/batch8与服务参数不变，原评分器逐字相同只读核验。')})

BATCH_RESULTS.update({'gqa_cg_hotspot_signal': ('N33/B40/S16：8组数值/Graph边界通过，Event1.277376→1.243314ms，省2.6666%；wall省2.7239%。', '保留16K组件正信号；旧官方对照关闭Q-hoist/compute-order，存在混杂，.cg本体整模收益待修正集成后验证。', '16K组件局部正信号', 'KV16K随机输入，实际GQA+reducer，8组数值/换值Graph边界（含原非有限行为保持）与16-call Graph ABBA；ASM有64处cg load。'), 'gqa_cg_b32_signal': ('B32/S4：8组数值/Graph边界通过，Event1.029731→1.015663ms，省1.3662%；wall省1.4070%。', '保留第二形状的局部正信号，不外推官方吞吐收益。', '第二形状组件正信号', '同一4行.cg候选，KV16K随机输入、实际GQA+reducer，8组边界及16-call Graph ABBA；ASM有64处cg load。'), 'lm_head_paired_gemv_negative': ('数值/变指针内容/guard/RNG通过；Event0.834885→2.045513ms、wall0.892245→2.076413ms，明显负。', '停止唯一配置，不扩调参或接模型；保存负结果，不建优化PR。', '组件正确性通过，性能负', '随机BF16 M2/N130560/K2048，对照原FlagGems linear固定配置；CPU FP64参考及ABBA完整词表输出计时，不含分配/参考。未加载框架/native。'), 'head_major_paged_prefill_negative': ('三臂编译及数值/Graph通过；Event当前8.366/原FlagGems29.733/新loader82.944ms，候选明显负。', '停止该方法，不再调参、不创建优化PR；完整三臂结果保留。', '三臂数值通过，候选明显负', 'M2047/KV16K、Q16/KV2/D128/page16，真实原库对照；独立FP64抽样、KV writer/guard、同址换值Graph，当前锚定的两组ABBA。'), 'mixed_logits_snapshot_failed': ('mixed长题仍ID8＋ID0×1023耗尽上限；快照未生成、分析FileNotFoundError，无法判断logits或根因。', '保留原exit1及cleanup_errors；后态/DB/source/native通过，不扩大或重跑此诊断。', '有界观察失败，根因未定位', 'main526+两处graph外有界观察改动（实际527/tree7ebc），native14f/原双请求；记录原响应、token与安装标记。未形成完整快照，不是原526无改动对照。')})

SHORT_ATTEMPTS = {'gqa_cg_hotspot_signal': ('检查GQA K/V读取绕过L1是否减少长上下文访存开销。', '实际生产GQA仅4处load增加.cg，reducer保持；N33/B40/S16。'), 'gqa_cg_b32_signal': ('用B32/S4检验同一缓存策略的第二实际形状。', '复用同一4处.cg候选与原reducer。'), 'lm_head_paired_gemv_negative': ('用双行GEMV减少M2 LM-head矩阵乘开销。', '唯一BN32/BK256/w8，随机权重组件；未加载框架/native，不补造二者身份。'), 'head_major_paged_prefill_negative': ('用head-major大query tile和分页loader增加长prefill局部复用。', '新增page16 loader并把N32改N64；原库臂未改，不能拆分loader/归约两变化的因果。'), 'mixed_logits_snapshot_failed': ('在原mixed边界采集有界logits观察，不改采样或扩大排查。', 'main526仅加入口与观察模块两处，实际527/tree7ebc；原失败与快照缺失分别保留。')}

BATCH_RESULTS.update({'gqa_cg_official_first_warm_negative': ('4K冷/首暖4722.73/4944.66 tok/s，首暖对同轮5751.88为−14.03%；512成功，第三轮主动中断、16K未测。', '保存全部已测及停止原件；旧候选Q-hoist/compute-order未启用而原main已启用，属优化组合不完整的混杂比较，不能判.cg本体无收益；修正集成后另作对照。', '官方首暖负，优化组合不完整', '原0813脚本RUNS4/SKIP_FIRST1与服务参数不变；团队main0915完整603仅4处.cg，13:37:32向所属owner SIGTERM。KV547648对547536；原server.log第68/398行证实Q-hoist/compute-order拒绝，13:37:37 finished、source/native/DB/清理通过。'), 'gqa_stride_no_net_gain': ('8组数值/Graph及alternate-stride13项通过；整数mul27→13，Event1.277992→1.278517ms，wall1.284104→1.283520ms，无净收益。', '保留机制和无收益结果，收口；不扩形状或进入模型，不创建优化PR。', '指令减少，未见净收益', '实际原GQA+reducer、N33/B40/S16与KV16K；只改5个stride为constexpr，不混.cg。原8组边界、额外13项换stride/图绑定与关闭profiler的Graph ABBA。')})
SHORT_ATTEMPTS.update({'gqa_cg_official_first_warm_negative': ('检查16K组件局部省时能否转为原官方服务收益。', '团队main0915完整603仅4处KV load加.cg；KV547648对547536，DB后分析作为独立原件，原failed/残留running字段不改。'), 'gqa_stride_no_net_gain': ('用constexpr stride减少分页地址计算的整数乘法。', '仅5个K/V stride声明为constexpr，原缓存策略、数学与reducer保留；alternate stride校验不同值的新JIT和原Graph仍绑定正确。')})
CODE['gqa-kv-cg'] += ['experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/early-stop-request.json', 'experiments/framework/20261025T132239Z-main0915-gqa-kv-cg-four-rounds-control/analysis/posthoc-db-comparison.json', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/raw_runs_20261025_001229.csv']

BATCH_RESULTS.update({
    'native_q32_direct_q_grouped_compile_cpu_go': ('独立CPU编译审阅GO，仅授权一次pure2048组件A/B；无GPU数值、性能、模型或生产资格。', '保留CPU编译与审阅证据；只允许指定组件实验，不继承151702资格。', 'CPU编译及独立审阅GO；无GPU结果', 'CPU编译＋独立FP DAG/资源审阅；SGPR99/VGPR107、shared64KiB、scalar spill 2、无VGPR/private spill。'),
    'native_q32_direct_q_v2_official4k_complete_negative': ('官方4K四轮完整、1024请求成功；弃首暖均6537.81，对基线6627.816667为−1.358014%；首暖+0.424135%，故跑满。', '保留完整负结果并停止direct-Q；KV548432对548336不匹配，不作严格因果，不跑16K/105、不改基线。', '官方4K完整，均值负', '原4K官方脚本、服务参数及四轮弃首轮口径；路径资格、恢复和清理均通过。'),
    'native_q32_direct_q_grouped_component_stopped_event_negative': ('18项硬门通过；Event A/B .519592/.550852ms，慢6.016321%，按Event门停止。wall省8.498318%，B重复值波动大。', '保留raw原值并停止组件；wall不称稳定收益/退化，raw numerical_component_passed=false保留，系性能early return未赋值，18项数值/状态门全过。无模型/官方资格。', '组件Event负，wall波动', 'pure2048完整ABBA与18项硬门；依原Event筛选门停止，保留原始性能状态及flag。')
})
SHORT_ATTEMPTS.update({
    'native_q32_direct_q_grouped_compile_cpu_go': ('复核direct-Q＋grouped四行max组合是否具备开展一次纯组件测试的编译资格。', '仅CPU编译和独立资源审阅；批准范围限一次pure2048组件A/B。'),
    'native_q32_direct_q_v2_official4k_complete_negative': ('按原官方4K四轮口径筛选direct-Q v2。', 'direct-Q v2官方构建；原benchmark与服务参数、1024请求及四轮规则不变。'),
    'native_q32_direct_q_grouped_component_stopped_event_negative': ('检查grouped pure2048与qualified direct-Q组件组合。', 'A/B完整ABBA，Event为原筛选门；不把wall单项改作通过依据。')
})
SHORT_ATTEMPTS.update({'gqa_cg_b64_4k_signal': ('核查官方4K退化是否也出现在对应短输入局部形状。', '同一4处.cg候选，补4K/B64/S2；仅改组件负载，不写模型生产gating，不改官方参数。')})

BATCH_RESULTS.update({'team_main_current_control_partial': ('原main4K冷/首暖5404.31/5761.99 tok/s、512成功；因已有完整基线主动停止，仅两轮，16K未测。', '保留当期部分对照，不覆盖旧完整基线；本轮两项原有优化启用，与旧.cg关闭状态不同，修正后才能判断.cg本体整模收益。', '原main两轮对照，主动停止', '原团队main0915完整603/tree766b、native14f与官方参数不变，无.cg或stride；RUNS4/SKIP_FIRST1原设置保留，用户提醒已有完整基线后向所属owner SIGTERM。原server.log第68/186/326行确认Q-hoist/compute-order启用；14:18:14 source/native/DB及清理通过。')})
SHORT_ATTEMPTS.update({'team_main_current_control_partial': ('补当期原main冷/首暖对照，帮助阅读.cg组件与整模结果差异。', '没有新增优化；原0915/603源码与native14f。run名four-rounds及原failed/SIGTERM/stage=running保持，实际只有两轮且已结束。')})

BATCH_RESULTS.update({'native_silu_vec2_negative': ('15case逐位/finite/guard与Graph通过；隔离Event0.216360→0.231472ms慢6.9849%，完整gate0.712861→0.730258ms慢2.4404%。', '停止模型推进；实验PR52已关闭、未合并，不改生产csrc，不授模型/官方资格。', '数值检查通过，性能负', '独立随机M2048/N12288/K2048、同编译器私有库；32-call Graph ABBA，原15case、独立CPU参考、变指针/同址换输入、inputs/RNG；生产native未加载/替换，DB207f未变。')})
SHORT_ATTEMPTS.update({'native_silu_vec2_negative': ('用相邻两列向量读取和packed BF16写回减少native SiLU尾处理成本。', '原量化/GEMM及舍入顺序保留；只有私有测试库，独立组件不补造框架commit/native_unchanged。源码基点引用0915，实测身份见原source与library SHA。')})

BATCH_RESULTS.update({'gqa_four_page_t64_negative': ('8类数值/Graph/FP64抽样门通过；Event1.276535→2.896506ms，慢126.9037%；SGPR spill0→138、shared8K→32K。', '明确负结果收口，不测4K/模型、不扫参；保留原件及资源代价，不授模型或官方资格。', '组件数值通过，T64明显更慢', 'N33/B40/S16、KV16K/page16，生产GQA与四页T64候选+原reducer；8类边界、变输入Graph及独立CPU FP64抽样，Graph ABBA。跨臂不要求逐位，引用原数值合同。')})
SHORT_ATTEMPTS.update({'gqa_four_page_t64_negative': ('把四个物理页组成T64计算块，减少GQA循环与地址计算。', '实际T16→T64改变归约分块，保留分页/causal/reducer语义；独立FP64抽样判数值，不能声称跨臂逐位。')})

BATCH_RESULTS.update({'prefill_log2_small_signal': ('FP64/writer/换值Graph/inputs/RNG通过；Event8.358478→8.334337ms省0.2888%，wall8.453647→8.532408ms慢0.9317%。', '保留微小GPU正信号；模型收益未确认，不授官方/105资格，后续GQA固定w4结果另列。', '微小GPU正信号，wall未改善', 'M2047/KV16K、16Q/2KV/D128/page16/8192页表，已暖私有Q-hoist完整2D producer，16-call Graph ABBA；共同writer/metadata不计差额，FP64抽样max_abs≤5e-4、relativeL2≤0.01。')})
SHORT_ATTEMPTS.update({'prefill_log2_small_signal': ('将指数换底并入score scale，减少softmax重复乘法。', '仅score/max转log2域并直接exp2，tile/页序/地址及BF16转换不变；FP32舍入变化，非跨臂逐位，qmod仅runtime0。')})

BATCH_RESULTS.update({'gqa_four_page_t64_w4_negative': ('8类数值/Graph/FP64门通过；Event1.278072→2.105123ms慢64.7108%，wall慢64.3265%；SGPR spill92/shared32K。', '明确负，不进入4K或模型；原IR供CPU布局分析，不授官方/105资格。', '固定w4仍负，预期布局未形成', 'N33/B40/S16、KV16K/page16，四页T64固定num_warps=4与原生产GQA+reducer；原8类边界、独立FP64及Graph ABBA，未改原数值合同。')})
SHORT_ATTEMPTS.update({'gqa_four_page_t64_w4_negative': ('以固定w4检验T64资源压力能否缓解。', '仅将T64候选num_warps固定4；实际mma仍[4,1]而非N方向[1,4]，不把warp数量等同成功布局变化。')})

BATCH_RESULTS.update({'gqa_four_page_t64_n4_negative': ('8类数值/Graph/FP64门通过，实际mma=[1,4]；Event1.278378→1.827178ms慢42.9294%，wall慢42.5630%。', '整个四页T64路线收口，不再扫参、不进入4K或模型，不授官方/105资格。', 'N4布局实现，但仍明显负', 'N33/B40/S16、KV16K/page16，固定真实N方向四warp布局与原GQA+reducer；8类原数值门及Graph ABBA，关闭profiler。')})
SHORT_ATTEMPTS.update({'gqa_four_page_t64_n4_negative': ('让T64沿N维分摊到四warp，检查前轮未实现的布局机制。', '实际mma改为[1,4]，页表/causal/reducer及原数值合同保持；SGPR spill仍68/shared32K，机制实现不等于净收益。')})

BATCH_RESULTS.update({'gqa_cg_closed_first_warm_negative': ('Q-fragment与compute-order均实际选中；4K冷/首暖5073.26/5362.19 tok/s，512成功，首暖对历史/当期观察−6.7750%/−6.9386%。', '按首暖负可停策略收尾，第三轮中断、16K/105不跑；KV不同不判严格因果，无模型净收益或新基线。', '优化组合恢复，官方首暖仍负', '原0813/RUNS4/SKIP_FIRST1及服务参数不变，0915完整603/treefbb3四处.cg＋三处关联身份修正；原日志确认两项优化启用，15:58:19向owner273504 SIGTERM，15:58:24清理完成。')})
SHORT_ATTEMPTS.update({'gqa_cg_closed_first_warm_negative': ('恢复原有优化组合后重新检查.cg局部省时能否转为模型收益。', '保留4处.cg并同步Q-fragment/compute-order中受审源码身份；实际选中日志闭合，KV547648对参考547536，非严格同条件因果对照。')})

BATCH_RESULTS.update({'prefill_stride_small_signal': ('旧数值/FP64/Graph与alternate17项通过，跨臂初始/换值逐位；Event8.371886→8.328763ms省0.5151%，wall慢0.5676%。', '保留小GPU候选，生产官方入口准备中；模型收益未确认，不授105资格。', 'SGPR spill减少，局部微小正信号', 'M2047/KV16K、原normalized+Q-hoist，完整2D producer单ABBA/每窗16次；固定FP64门、自臂换值Graph与合法5项stride切换回原布局17项检查。单序列未覆盖非零页表行偏移。')})
SHORT_ATTEMPTS.update({'prefill_stride_small_signal': ('把长期活跃的stride常量化，减少分页整数计算和参数资源开销。', '仅11项stride constexpr＋原int64寻址，不叠加log2/.cg；SGPR spill30→6、mul103→30，代价为布局编译变体。')})

BATCH_RESULTS.update({'ixkn_prefill_report_import_failed': ('wrapper exit -11；worker写完results并有61440B ixkn-rep，离线导入rc255/Unknown device name（空），CLI指标不可用；SQLite原事件只作有限来源核对。', '保留工具失败，停止本次计数，不修不重跑；全部timing禁止作收益、官方成绩或新增组件资格。', 'profiler异常，报告无法导入', '原baseline prefill单核，ixkn SpeedOfLight/ComputeWorkload/Memory、launch-skip2/count1/kernel replay；worker保持旧组件，原manifest和命令保存。'), 'ixkn_gqa_argument_rejected': ('ixkn立即exit255：launch-skip参数0无效；未生成results.json或报告，未进入采样。', '记录工具参数拒绝后跳过，不修不重跑；不判候选数值或性能失败。', 'profiler参数被拒，未采样', '原page16 GQA单核计数入口，launch-skip0/count1；工具在参数阶段退出，DB/source/native及所属进程组清理通过。')})
SHORT_ATTEMPTS.update({'ixkn_prefill_report_import_failed': ('尝试获取当前prefill单核计算/访存/发射硬件计数以支持后续设计。', '仅增加ixkn包装、profiles目录和所属进程组收尾；复用已测worker，不把受profile影响的计时当复测。'), 'ixkn_gqa_argument_rejected': ('尝试采集原GQA单核硬件计数，与prefill关键路径信息分开。', '只加ixkn包装；launch-skip=0被工具拒绝，未运行数值或性能比较。')})

BATCH_RESULTS.update({'prefill_stride_official_mixed_signal': ('原官方两档各4轮、1536成功，实际激活闭合；弃首轮5726.63/4052.78 tok/s，TTFT3637.47/124103.35ms。', '相对旧完整参考观察−0.56%/+0.19%，KV不同不判因果；保留小信号，不合并、不升基线、不继承105资格。', '官方完成，净收益未确认', '旧main0915/603/tree1127346e、native14f；原0813/RUNS4/SKIP_FIRST1，4K/16K各四轮，逐档弃首轮；日志/CSV及真实prefill、Q-fragment和compute-order激活保存。'), 'gqa_grouped_simt_negative': ('8类原数值/FP64/Graph及实际SIMT机制通过；Event1.279744→44.634184ms（34.8774倍），wall34.6878倍。', '保留明显负结果，停止整模与扫参，不推进已准备的模型入口；非数值错误，不授官方/105资格。', '机制落地，SIMT明显变慢', 'N33/B40/S16/KV16K/page16，baseline w1与candidate w8，原reducer不变；完整producer+reducer单ABBA，每窗16次Graph replay，关闭profiler。')})
SHORT_ATTEMPTS.update({'prefill_stride_official_mixed_signal': ('检查stride常量特化的局部资源改善能否转为原官方吞吐。', '仅旧main0915的normalized stride及Q-fragment/compute-order精确依赖闭合；实际603/tree1127346e，不混新main34942或PR51。'), 'gqa_grouped_simt_negative': ('尝试避免小page16矩阵的TCU填充与布局开销。', 'QK/PV改FP32广播归约，保留P先BF16与原分页/尾mask/reducer；KV逻辑字节不减，w8增加SIMT算术和广播成本。')})

BATCH_RESULTS.update({'official_baseline_complete': (
    '干净main34942/618原官方两档各四轮、1536成功；暖均4K5638.86/16K4100.08 tok/s，TTFT3368.34/122586.38ms。',
    '保留为本次新main/A性能对照。KV548432、DB207f；4K暖轮渐升，不将单轮差值当稳定收益；本机新源105未跑。',
    '新main官方基线完整完成',
    '原官方4K/16K、输出1024、并发64、请求256/128，各四轮弃首轮；34942f7/618/treee35bdbe6，原native14f及服务参数。实际PR51/Q-fragment/compute-order及Graph门通过，源码/native不变、DB恢复和清理通过。')})
SHORT_ATTEMPTS.update({'official_baseline_complete': (
    '为包含PR51修复的新main建立本站同条件原官方性能基线，用于本次A配对。',
    '无本方优化补丁；完整团队34942f7/618原源码。旧wrapper control只提供native/环境原件，不继承旧main或队友成绩。')})

GROUPS['prefill-stride'] = ('Prefill stride常量特化',
    '仅11项stride改constexpr并保留int64寻址，原normalized/Q-hoist浮点表达式、tile和页序不变；代价为布局编译变体。组件SGPR spill30→6/mul103→30、Event省0.5151%、wall慢0.5676%，原数值/FP64/Graph及alternate17项通过。旧0915官方−0.56%/+0.19%保留为历史，不能混入新base。最新34942/PR51完整618配对，基线和候选分别两档各四轮、各1536请求成功；基线4K/16K暖均5638.86/4100.076667，候选5656.77/4119.24 tok/s，观察+0.3176%/+0.4674%。实际KV548432对548336，4K暖轮升速，非严格孤立因果或统计稳定收益。同冻结618/treeaa43原105题103/105，105 stop且0 transport/截断/空答案，实际路径和清理通过。框架PR60已合并为6971ef48，作为后继基线；不继承父main准确率。单序列组件页表行stride仅身份覆盖。', ['prefill-stride'])
BATCH_RESULTS['prefill_stride_main34942_positive_pending_accuracy'] = (
    '原官方4K/16K各四轮、1536成功；暖均5656.77/4119.24 tok/s，对本组新main基线观察+0.3176%/+0.4674%。',
    '保留小幅正信号；本条为性能结束时状态，后继同源原105已103/105通过，见同方法准确率轮次及PR60。实际KV548336对548432及单组暖轮趋势限制保留。',
    '完整对照小幅正，后继准确率已通过',
    '34942f7/618/treeaa43ea2c，原官方4K/16K各四轮弃首轮、原native14f/DB207f/服务参数；actual norm/Q/compute-order/PR51/Graph与source/native/DB恢复清理门通过。')
SHORT_ATTEMPTS['prefill_stride_main34942_positive_pending_accuracy'] = (
    '确认stride常量化能否在保留PR51修复的新main上改善实际吞吐。',
    '仅normalized stride及Q-fragment/compute-order精确依赖身份闭合，共3个生产文件；PR51 runner绑定和其它615文件不变。')

BATCH_RESULTS['prefill_stride_main34942_accuracy_pass'] = (
    '原105题103/105（98.0952%），valid/pass；105 stop，0 transport/截断/空答案/空提取，模型实际路径及收尾通过。',
    '结合本组两档完整官方对照保留，PR60已合并为6971ef48；新基线5656.77/4119.24 tok/s、103/105，保留KV差异和单组小幅观察限制。',
    '准确率通过，PR60已合并',
    '与性能组同冻结618/treeaa43，原105/temperature1/top_p.95/batch8/max32768及服务参数未改，source/native未变，DB恢复和清理通过。')
SHORT_ATTEMPTS['prefill_stride_main34942_accuracy_pass'] = (
    '验证最新A组合是否满足官方准确率门槛，不继承父main或队友分数。',
    '不新增源码或改采样；复用已审冻结组合与原35d驱动/评分器，只跑这一轮，不反复抽样刷分。')

GROUPS['shape-gemm'] = ('BI-V150特定形状GEMM', '按真实轨迹选形状。M2048 down占映射BF16 MM约47.10%；大M静态化/减warp/加深K及M64 SplitK均负。宽N 256/256/32/w16/s2的42层真实down组件省24.12%，但实际模型M2030/2048选中后，4K首暖5451.11对PR60对应5533.03观察−1.48%；512 SUCCESS后主动早停，16K/105未跑，KV548432对548336，不能称严格因果、完整官方或正确性失败。PR61关闭未合并，保留原件。后继独立QKV M2048/2030,N2560,K2048，42层真实Q/K/V拼接组件12.705318→12.174299ms（省4.1795%），84数值/FP64抽样/Graph换值/side stream门通过；模型筛选另列，不叠down、不把组件比例当吞吐。另保留独立M1-8 down SplitK8组件，M2/M8整环省31.69%/34.98%，尚未接模型。原正确PR51及PR60基线不变。', [])
CODE['shape-gemm'] = ['analysis/2026-10-26-gemm-target-priority.json','analysis/2026-10-26-gemm-component-results.json','experiments/framework/20261026T035139678096Z-biv150-down-wide-working-set-component/source/candidate.py','experiments/framework/20261026T034152136640Z-biv150-down-small-working-set-component/source/candidate.py']
CODE['shape-gemm'] += [
    'experiments/bundles/20261028T174702433104Z-biv150-down-groupm4-provided-linear-component/manifest.json', 'experiments/bundles/20261028T174702433104Z-biv150-down-groupm4-provided-linear-component/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component/manifest.json', 'experiments/bundles/20261028T175144741472Z-biv150-down-groupm4-provided-linear-component/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T182129Z-biv150-down-groupm4-official-staging-failed/manifest.json', 'experiments/bundles/20261028T182129Z-biv150-down-groupm4-official-staging-failed/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds/manifest.json', 'experiments/bundles/20261028T182535Z-native-gqa-overlap-4k-four-rounds/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T182704343608Z-biv150-down-groupm4-official-selector-failed/manifest.json', 'experiments/bundles/20261028T182704343608Z-biv150-down-groupm4-official-selector-failed/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T173517Z-down-w8a16-weight-screen/manifest.json', 'experiments/bundles/20261028T173517Z-down-w8a16-weight-screen/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component/manifest.json', 'experiments/bundles/20261028T180055825919Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T180433423251Z-down-w8a16-weight-only-component/manifest.json', 'experiments/bundles/20261028T180433423251Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component/manifest.json', 'experiments/bundles/20261028T180844751927Z-down-w8a16-weight-only-component/raw.tar.gz.storage.json',    'experiments/bundles/20261028T184911473313Z-down-bm32bn32-tile-component/manifest.json', 'experiments/bundles/20261028T184911473313Z-down-bm32bn32-tile-component/raw.tar.gz.storage.json',
    'experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component/manifest.json', 'experiments/bundles/20261028T185611249396Z-down-bm32bn32-tile-handles-component/raw.tar.gz.storage.json',
    'experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/manifest.json',
    'experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/result.json',
    'experiments/official/20261028T183704Z-native-gqa-overlap-4k-four-rounds/raw_runs_20261029_023914.csv',
    'experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds/manifest.json',
    'experiments/bundles/20261028T183704Z-native-gqa-overlap-4k-four-rounds/raw.tar.gz.storage.json',
]
for status, verdict, decision in [
    ('shape_gemm_negative','性能负结果，停止该候选','数值通过但完整组件慢，不接模型；不能把资源减少或循环减少当净收益。'),
    ('shape_gemm_official_negative_screen','官方首暖负，提前收尾','首暖负按约定主动停止，保留已测轮次和运行条件；未测16K/105，不合并或定基线。'),
    ('shape_gemm_local_positive','单权重组件正，整模型未验证','保留局部信号，后继完整权重工作集结果另列，不把组件比例当整轮收益。'),
    ('shape_gemm_working_set_positive','42层权重正，整模型未验证','保留候选；优先推进热点M2048 wide，M1-8 SplitK另列；需要实际接入、整模型性能/105和新增代码独立复核。')]:
    BATCH_RESULTS[status]=('实测数据见本条结论及result.json。',decision,verdict,'真实down权重，原安装MM或当前PR51 small_o JIT对照；数值/FP64抽样/换值Graph后ABBA，完整输出和SplitK归约计入。')
    SHORT_ATTEMPTS[status]=('针对BI-V150 warp64/16SM与真实M/N/K降低净开销。','实际实现和精确固定tile见原source/candidate.py；未改官方参数或切换现成库，不承诺任意输入bitwise。')

# 新批次状态只用于中文导航；原结果和失败分类不改写。
for key,verdict,decision in [
 ('five_test_weight_lookup_error','测试权重读取失败','修读取器后另run，保留原件；不当框架数值错误。'),
 ('shape_gemm_integration_pass','新增接线/Graph通过','仅继承已测内核部分，模型吞吐与准确率另验。'),
 ('gqa_t32_component_negative','组件性能负，停止','不扩形状、不进模型；寄存器spill反证保留。'),
 ('prefill_lpt_reference_scope_mismatch','旧参考界不适用，未计时','原臂/候选逐位一致；旧FP64拒绝不改判，后继逐位组件单列。'),
 ('prefill_lpt_component_negative','组件性能负，停止该范围','长上下文不进模型；短causal单独完成有界验证。')]:
    BATCH_RESULTS[key]=('实际数值见本条登记和result(s).json。',decision,verdict,'复用真实生产ABI/原数值门，新增改动单独验证；不重复旧测试。')
    SHORT_ATTEMPTS[key]=('验证本条所述固定形状和新增实现。','改动及精确命令见该run源码和manifest/command原件。')
GROUPS['shape-gemm']=('BI-V150特定形状GEMM','组件收益与模型分开：down大M宽tile、QKV宽tile、小M SplitK8及O宽tile先后局部正但模型负，均停止且不定基线。O真实42层组件省20.33%，原官方4K第三轮5568.49对5677.28观察−1.9162%，三轮768 SUCCESS后早停，16K/105未跑。新增来源限制：大行wide组件直接以固定mm_kernel为对照，而当前PR51大行生产入口是opaque内部F.linear，实际kernel一致性尚待一次直接诊断，不能将组件比例视为相对真实生产路径的加速。小M SplitK8使用原PR51 small_o，区别记录。保留原PR51/PR60合格基线，不将不同方法或组合比例相加。',[])

# 2026-10-26四项执行：方法描述只导航，结论来自每轮原登记。
GROUPS['gqa-two-page-t32']=('GQA两页T32计算块','保持物理page16、原split和reducer；固定T32/w1/s1检验减少online-softmax迭代能否抵消寄存器/布局成本。旧T64失败不改写，本方法实际结果以每轮短记为准。',[])
GROUPS['prefill-lpt']=('Prefill序列内CTA调序','在当前stride与Q-hoist上反转每个序列内的query块枚举，尝试减少causal最后一波拖尾；不改变单query的K遍历/softmax/输出地址。',[])
BATCH_RESULTS['shape_gemm_model_negative_early_stop']=('实测值见本条结论与原CSV。','已低于可比基线，停止后续；不跑105、不提收益PR、不定新基线。','模型性能负，主动停止','原官方脚本/参数不变；已测暖轮与原基线同负载/轮次比较，KV差异明示。')
SHORT_ATTEMPTS['shape_gemm_model_negative_early_stop']=('检验真实模型中的完整净收益。','独立候选精确形状接入；组件收益不继承为模型收益。')

# 07:16批次：原件逐文件SHA已核；仅新增导航与短记，不改原结果。
GROUPS['prefill-lpt']=('Prefill序列内CTA调序','保留stride/Q-hoist及每query的K顺序，只反转序列内CTA枚举。完整Graph Q2048/KV2048省12.2180%，Q2048/KV4096省5.7144%，长Q2047/KV16384慢3.57%。纯causal原FP64门两臂均false、输出逐位相同，保留原失败诊断；middle原FP64硬门通过。独立原官方4K暖均5722.4833观察+1.1617%，16K首暖4111.36观察−0.19663%后停，六轮1280 SUCCESS。私有LPT Q-hoist实际selected通过；KV548432对548336，保留混合结果候选，不能称稳定整体收益或整体负。无105/合并，main6971不变。',[])
GROUPS['gqa-sme-span']=('GQA同storage二维span','保持原KV storage，二维连续backing-span与行单位地址尝试改善SME传输资格。8类数值/Graph等门通过、mask15→63，但mask不是实际SMEcopy启用证明；producer＋原reducer Graph慢0.3806%，停止，不扩形状或接模型。',[])
GROUPS['down-group256']=('down K256分组INT8探索','独立W8A8原型首个CPU INT64精确整数门失败，未计时；保留exit1，不推进依赖该门的gate融合，不放宽容差或改框架凑过。不是完整量化/模型方案，也不泛化其它INT8实现。',[])
GROUPS['prefill-fresh-kv']=('Prefill当前chunk直读K/V','保留writer与原浮点顺序，历史KV走paged、当前chunk读post-RoPE BF16 K/V。长场景逐位/FP64/Graph与实际来源证明通过，但Event慢30.1099%，停止；causal未测，不叠LPT或进入模型。',[])
GROUPS['qkv-rope-fusion']=('QKV GEMM与RoPE融合','layer0真实权重＋合成激活，融合QKV GEMM输出和RoPE，不含KV writer。M2030/2048的14项逐位/FP64/Graph/side stream通过，Graph慢12.4198%/12.8168%，停止。原组件基于installed mm，未绑定生产opaque/F.linear身份，不能当生产linear的直接对照。单层未复现42层交织；原RoPE heuristic重新编译，不宣称服务原机器码，亦无官方资格。',[])
for key, run, filename in [
 ('prefill-lpt','20261026T062007042651Z-prefill-lpt-graph-causal-component','results.json'),
 ('gqa-sme-span','20261026T061316901168Z-gqa-sme-span-hotspot-component','results.json'),
 ('down-group256','20261026T062610126686Z-biv150-down-group256-component','result.json'),
 ('prefill-fresh-kv','20261026T062915011626Z-prefill-fresh-kv-long-component','results.json'),
 ('qkv-rope-fusion','20261026T064944259294Z-biv150-qkv-rope-fusion-component','result.json')]:
    CODE[key]=['experiments/framework/'+run+'/'+filename,'experiments/framework/'+run+'/source']
for key, verdict, decision, attempt, change, test in [
 ('o_wide_model_negative_early_stop','官方第三轮负，主动早停','停止，不合并、不定新基线；保留全部三轮及SIGTERM原件。','检验O宽tile局部收益是否转为官方吞吐。','只接入O宽tile，保留其它主线优化。','原官方4K已测三轮、每轮256请求；按对应冷/暖轮比较，16K/105未跑。'),
 ('prefill_lpt_causal_bitwise_component','逐位通过，直接JIT的Event正/wall负','保留逐位依据；直接JIT不代替完整Graph或整模，FP64诊断false不改判。','核对causal CTA调序的原生产等价性及提交开销。','仅反转CTA枚举，单query数学和K顺序不变。','Q2048/KV2048，原writer、换值Graph及直接JIT ABBA；FP64原阈值保留为诊断。'),
 ('prefill_lpt_causal_graph_positive_component','完整Graph组件正，FP64诊断仍false','保留早期chunk候选；无官方/105新资格。','隔离Python JIT提交后核完整Graph实际收益。','与逐位组件同CTA调序，完整Attention Graph回放。','Q2048/KV2048完整Graph replay ABBA，跨臂逐位；原FP64门两臂false，阈值未变。'),
 ('prefill_lpt_middle_graph_positive_component','完整Graph组件正，FP64硬门通过','保留已测第二chunk范围；不推广long或任意形状。','验证4K第二chunk是否同样改善拖尾。','CTA调序不改变context与K遍历。','Q2048/KV4096、context2048，完整Graph ABBA及初始/换值逐位、原FP64硬门。'),
 ('gqa_sme_span_negative_component','组件门通过，性能微负','停止，不扩形状或进模型；mask不当实际传输证明。','核二维span是否降低原page16传输成本。','同storage二维视图与行单位地址，原reducer不变。','N33/B40/S16、KV16K，8类数值/Graph/FP64适用门与完整producer+reducer Graph ABBA。'),
 ('down_group256_integer_gate_failed','精确整数门失败，未计时','停止当前错误实现；不推进依赖融合、不放宽容差。','检验K256分组INT8 dot布局与ABI是否精确。','独立K256 W8A8核，layer20 down真实权重、合成激活。','CPU INT64精确参考前置门；失败即停，cases/timings为空。'),
 ('prefill_fresh_kv_long_negative_component','逐位/FP64通过，组件明显负','停止，不叠LPT或接模型；causal未测。','减少当前chunk从paged KV读取的地址成本。','按context_len逐lane选择历史cache或当前post-RoPE K/V，原writer保留。','Q2047/KV16384，原数值门、换值Graph与fresh来源反事实证明；已暖直接JIT完整2D输出ABBA。'),
 ('qkv_rope_fusion_negative_component','14项通过，Graph性能负','停止，不进官方；无生产adapter或新基线。','减少QKV到RoPE的launch和中间访存。','新GEMM输出融合RoPE，不含KV writer。','layer0真实权重＋合成激活，M2030/2048共14项；两臂完整Graph ABBA，原RoPE heuristic重新编译。')]:
    BATCH_RESULTS[key]=('实际数值见本轮原登记及result(s).json。',decision,verdict,test)
    SHORT_ATTEMPTS[key]=(attempt,change)

# 阶段末两项：LPT为混合结果，gate为数值通过的组件负结果。
GROUPS['gate-partial-fusion']=('gate partial融合','实际opaque/F.linear默认FlagGems身份及GROUP_M8、BM256/BN256/BK32/w16/s2门通过；M2030的8项逐位/FP64/Graph/side stream通过，但完整Graph链慢14.8772%，停止M2048、8层工作集与模型。两臂均两个launch，partial_up shared64→128KiB、reg97→169；资源与退化同时观察，未隔离因果。单层合成激活，无生产/官方资格，不改主线。',[])
CODE['gate-partial-fusion']=['experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/result.json','experiments/framework/20261026T075700478338Z-biv150-gate-partial-fusion-component/source']
CODE['prefill-lpt'] += ['experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds-control/lpt-posthoc-activation.json','experiments/framework/20261026T071618Z-main6971-lpt-early-four-rounds/benchmark_results/raw_runs_20261026_151843.csv']
BATCH_RESULTS['prefill_lpt_official_mixed_partial_stop']=('原CSV六轮详见登记。','保留混合结果候选；停止后续测试，无105/合并或新基线，不称整体负或稳定收益。','4K正/16K首暖微负，混合候选','原官方4K四轮、16K两轮，输入4096/16384、输出1024、并发64，1280 SUCCESS；按负载及冷暖对应比较，KV548432对548336。')
SHORT_ATTEMPTS['prefill_lpt_official_mixed_partial_stop']=('检验已测早期chunk调序的整模净影响。','新私有LPT kernel/Manager按几何选择，long原核保留；posthoc核实际私有Q-hoist选中。')
BATCH_RESULTS['gate_partial_fusion_negative_component']=('完整Graph1.305488646→1.499709368ms，慢14.8772%，8项数值等门通过。','停止M2048、工作集和模型；不合并、不定基线，保留负结果。','8项通过，完整Graph组件负','真实layer0 gate/up权重＋合成BF16激活M2030，实际opaque/F.linear身份/config；完整output/gate逐位、FP64、换值Graph/side stream与ABBA。')
SHORT_ATTEMPTS['gate_partial_fusion_negative_component']=('将SiLU尾合入up输出以降低完整gate链开销。','A为生产merged linear＋原SiLU；B为gate写BF16 scratch＋up保留BF16 round并融合SiLU，均两个launch。')

# 20261026热点诊断与布局组件：仅本轮新增记录。
GROUPS.update({'main6971-graph-profile': ('main6971 Graph真实热点诊断', '保持生产源码，复用PR62诊断工具；Graph采样可用，fresh native FX证明缺项保留。图内插桩时间只用于排序，不作正常耗时或官方成绩。', []), 'bf16-packed-down': ('BF16 down权重微块布局', '仅加载时BF16位重排，真实opaque/F.linear同配置；先核正确性，再用完整组件判断净效果。首run停在SME机制检查，不判性能负。', []), 'prefill-history-tail': ('Prefill历史区间与causal尾块分离', '保持数学和原tile顺序；完整历史循环省去mask，至多两块尾部保留原causal处理。首run私有Q-hoist适配失败；未计时。', [])})
CODE.update({'main6971-graph-profile': ['experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/actual/posthoc.json'], 'bf16-packed-down': ['experiments/framework/20261026T090924033923Z-biv150-packed-down-component/source'], 'prefill-history-tail': ['experiments/framework/20261026T090943131971Z-prefill-history-tail-long-component/source']})
BATCH_RESULTS.update({'profile_preflight_symlink_failed': ('诊断adapter把Git mode120000符号链接解引用，源码身份检查在CPU阶段拒绝；未启动collector/服务/GPU。修为校验linktarget字节后另run执行，原失败保留。', '保留入口失败；v2单独登记，不当模型错误或性能负。', 'CPU启动前校验失败', '冻结main6971/618文件身份检查；原Driver未进入workloads。'), 'profile_graph_valid_missing_fresh_fx': ('4K诊断256/256成功；Graph四samples、334bindings，API/数值/别名检查通过，实际prefill栈有效。无日志指向fresh FX，posthoc仍diagnostic_incomplete；正常退出、共享DB未变。不是官方吞吐/105。', '保留可用Graph诊断，native FX缺口明示；分析实际热点，不把插桩时间当正常占比。', '诊断完成，fresh FX证明缺项', 'main6971/native14f，PR62诊断工具本站适配；3短warm＋1同负载warm＋1完整4K profile，c64、256请求、输出1024；生产源码和服务基准参数保留。'), 'packed_b_sme_not_retained': ('真实F.linear选BM256/BN256/BK32/w16/s2；pack/unpack及首normal逐位一致。B dot useSme2→0，shared64→48KiB/reg97→98，在机制检查停止；未完成全部正确性、未计时。', '原机制假设未实现；不当数学错误或性能负。后继独立v2保留数值门，以一次计时判断净效果。', 'SME机制检查停止，未计时', '真实layer0 down权重、合成M2030 BF16激活，原opaque/F.linear同配置与唯一无损微块布局；首次输入后停止。'), 'history_tail_qhoist_adapter_failed': ('完整历史loop＋至多两个causal尾块已编译；私有Q-hoist因allocation/loop/load顺序守卫fallback。两臂优化选中检查拒绝，尚未进入跨臂/FP64/Graph或计时；清理通过。', '保留编译变换适配失败；只用实际IR定位最小修正，不放宽正确性门或修改生产数学。', '私有Q-hoist适配失败，未计时', 'main6971 stride+Q-hoist对照，Q2047/KV16384/ctx14337、BM128/T64/w8s1，原长输入组件。')})

# 20261026布局v2收尾
BATCH_RESULTS.update({'packed_layout_negative_component': ('v2仅将SME机制要求改诊断，candidate字节不变；8项数值/FP64/Graph/side检查通过。M2030完整GEMM Graph ABBA原F.linear0.564831406→packed0.970907092ms，慢71.89%，停止M2048/权重环/模型。DB/source/清理成功。', '停止该布局，不合并、不定基线；局部负结果保留。', '正确性通过，组件慢71.89%', '真实layer0权重、合成M2030激活；原F.linear同配置/完整Graph16call ABBA，无profiler。不含eager CPU分配或加载pack，不是官方成绩。'), 'history_tail_bitwise_failed': ('v2按真实IR复用已有Q fragment，selected1/fallback0、两臂LLVM循环Q读0。SGPR104→90/spill6→0；两臂FP64门通过，但跨臂逐位失败，max_abs0.0001220703125。违反本方法数值不变要求，未计时，停止当前候选。', '停止当前候选，不放宽逐位门、不继续修优化或进模型；不能称主线错误/准确率下降，保留首次失败。', '数值不变要求未通过，停止', 'Q2047/KV16384/ctx14337、相同原tile/顺序；只修私有Q复用，数值/FP64/Graph门未改。初始逐位门拒绝，后续Graph/性能未跑。')})
GROUPS['bf16-packed-down']=('BF16 down权重微块布局', '真实F.linear同配置的BF16位重排；首次停在SME假设，v2保留全部正确性后通过8项，但M2030完整Graph慢71.89%，停止。', [])
GROUPS['prefill-history-tail']=('Prefill历史区间与causal尾块分离', '首run私有Q-hoist适配失败；v2实际消除loop Q读取及SGPR spill，但跨臂逐位门失败，未计时，停止该候选。FP64通过不覆盖数值不变要求。', [])
CODE['bf16-packed-down'].extend(['experiments/framework/20261026T092809453391Z-biv150-packed-down-component/source', 'experiments/framework/20261026T092809453391Z-biv150-packed-down-component/result.json'])
CODE['prefill-history-tail'].extend(['experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/source', 'experiments/framework/20261026T093219176303Z-prefill-history-tail-reuse-fragment-long-component/results.json'])

# 20261026 GQA for+span实测收尾
GROUPS['gqa-for-span']=('GQA动态for与二维span', '根据main6971真实Graph热点，保持原page16/数学顺序/reducer，仅改变循环形式与合法跨度；N64/S2八类门通过，但完整组件慢75.05%，停止。', [])
CODE['gqa-for-span']=['experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/source/kernel.diff', 'experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/results.json', 'experiments/framework/20261026T095708239358Z-gqa-for-span-hotspot-component/ir-candidate']
BATCH_RESULTS['gqa_for_span_negative_component']=('原page16/FP顺序的动态for＋二维span，N64/S2用真实4K观测长度多重集、合成激活。8类原数值/FP64/Graph/写入门通过，完整producer＋原reducer Event0.541187257→0.947350353ms，慢75.0504%，wall慢74.0019%。停止，不进模型。source/DB/native及9031清理通过；mask14→62不是SME启用证明。', '停止本候选，不扩形状或模型，不合并；复用原负结果，不重跑。', '8类检查通过，组件慢75.05%', '实际N64/B64/S2及replay32长度多重集，合成Q/KV；page16、原FP64/特殊值/换值Graph/side门，完整producer＋原reducer16-call ABBA。')

# 20261026 连续读参考、GQA页号预取与N-only布局批量收尾
GROUPS['stream-read-reference']=('BI-V150连续流读取参考', '固定512MiB BF16连续流读＋128KiB checksum输出，三组Event中位约0.806800ms、逻辑读665.432GB/s；两次内容checksum、一次copy正确性及计时后checksum通过。仅连续流读参考，不是物理HBM或散页GQA硬上限，不是吞吐优化/官方成绩。DB/source/native与设备清理通过。同期补回main6971三个实际linear缓存文本，仍不伪装大M实际参数采集。', [])
CODE['stream-read-reference']=['experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/results.json', 'experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/source/worker.py', 'experiments/profiles/20261026T101034477784Z-biv150-stream-read-reference-hotspot-component/archive-receipt.json', 'experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/triton-cache']
BATCH_RESULTS['stream_read_reference_completed']=('固定512MiB BF16连续流读＋128KiB checksum输出，三组Event中位约0.806800ms、逻辑读665.432GB/s；两次内容checksum、一次copy正确性及计时后checksum通过。仅连续流读参考，不是物理HBM或散页GQA硬上限，不是吞吐优化/官方成绩。DB/source/native与设备清理通过。同期补回main6971三个实际linear缓存文本，仍不伪装大M实际参数采集。', '保留带宽参考及实际linear文本，用于预算；不替换比赛基线，不从连续读参考推GQA可实现收益。', '两次checksum、一次copy正确性和计时后checksum通过；无参数扫描。', '单配置512MiB BF16连续流读＋128KiB checksum，每组16次Graph replay共三组；copy只核正确性不计带宽，profiler关闭。')
GROUPS['gqa-page-lookahead']=('GQA下一页号预取', '原page16 while仅提前读取下一i32页号，N64/S2观测长度多重集、合成激活；原8类FP64/特殊值/Graph等门与跨臂逐位全部通过。完整producer＋原reducer Event0.542211056→0.542784363ms（慢0.105735%），wall快0.06134%，无可分辨正信号，停止不进模型。ASM下一页load后立即wait，未实现预期计算重叠；SGPR64→68、两臂spill0，源码/DB/native及清理通过。', [])
CODE['gqa-page-lookahead']=['experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/results.json', 'experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/worker.py', 'experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/archive-receipt.json', 'experiments/framework/20261026T102536253539Z-gqa-page-lookahead-hotspot-component/source/candidate.py']
BATCH_RESULTS['gqa_page_lookahead_no_positive_signal']=('原page16 while仅提前读取下一i32页号，N64/S2观测长度多重集、合成激活；原8类FP64/特殊值/Graph等门与跨臂逐位全部通过。完整producer＋原reducer Event0.542211056→0.542784363ms（慢0.105735%），wall快0.06134%，无可分辨正信号，停止不进模型。ASM下一页load后立即wait，未实现预期计算重叠；SGPR64→68、两臂spill0，源码/DB/native及清理通过。', '保留数值通过但无净收益的负结果，停止，不扫参、不进模型；不将微小Event/wall反向差异写成稳定因果退化。', '8类原门与跨臂逐位通过；完整组件无可分辨正信号。', '固定N64/S2/page16原while及4D KV，同4K观测长度多重集与合成Q/KV；原reducer、FP64/换值Graph/特殊值及完整Graph ABBA。')
GROUPS['bf16-nonly-down']=('BF16 down N方向分组布局', '真实生产opaque/F.linear的M64 down单层组件，仅改N方向BF16无损权重布局，保留实际BM64/BN128/BK64/w8/s2与SME；9类逐位/独立FP64/Graph及RNG门通过。完整GEMM Graph Event0.085926324→0.076858178ms，省10.5534%，仅保留组件正信号。原W与packed两份各24MiB；若42层重复保留将多1008MiB、等价24576 KV token，容量风险及42层交织未测。无模型/官方/105资格，未定新基线；DB/source与清理通过。', [])
CODE['bf16-nonly-down']=['experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/result.json', 'experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/worker.py', 'experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/archive-receipt.json', 'experiments/framework/20261026T102808704037Z-biv150-nonly-down-component/source/candidate.py']
BATCH_RESULTS['nonly_down_positive_component']=('真实生产opaque/F.linear的M64 down单层组件，仅改N方向BF16无损权重布局，保留实际BM64/BN128/BK64/w8/s2与SME；9类逐位/独立FP64/Graph及RNG门通过。完整GEMM Graph Event0.085926324→0.076858178ms，省10.5534%，仅保留组件正信号。原W与packed两份各24MiB；若42层重复保留将多1008MiB、等价24576 KV token，容量风险及42层交织未测。无模型/官方/105资格，未定新基线；DB/source与清理通过。', '保留单层组件候选；先解决或验证42层额外1008MiB/24576 KV token容量成本及真实交织，不能直接合并或宣称模型收益。', 'M64单层9类case、跨臂逐位/独立FP64/Graph/RNG通过，完整Event省10.5534%；未测42层或模型。', '真实layer0 down权重、合成M64激活；基线真实opaque/F.linear默认FlagGems，复用实际选中tile及SME；N-only pack/unpack/数值/尾M/Graph后唯一完整Graph ABBA。')

# 20261026 N-only接线与M32/M2048批量收尾
GROUPS['bf16-nonly-down']=('BF16 down N方向分组布局', '同一N128 BF16无损格式：M64单层省10.5534%，新M32单层省约3.63%；M2048为适应格式BN256→128后慢约61.60%，停止该大M候选。42真实权重GPU helper/opaque/Graph接线门通过，但不是完整模型安装链或官方成绩。原W/P双份1008MiB及KV容量代价未消除；不叠加各M收益。', [])
CODE['bf16-nonly-down'] += ['experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/result.json', 'experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/source/worker.py', 'experiments/framework/20261026T105246722313Z-biv150-nonly-down-integration/archive-receipt.json']
BATCH_RESULTS['nonly_down_integration_component_pass']=('42层真实down权重的GPU _after_loading helper/新opaque接线门通过：pack全位反解、原W保留、1056964608B nonpersistent buffer、42层完整输出逐位及独立FP64样本、两种同址换X Graph和M32原路回退通过。未调用完整Llama install-chain，无吞吐计时、官方或105资格；1008MiB常驻副本及KV容量代价仍需模型验证。', '保留新增helper/opaque/Graph接线证据；完整模型加载链和官方净性能不继承，原W/P双份容量成本未消除。', '42真实权重helper、pack全位反解/原W/FP64样本/完整跨臂逐位、42层两次换值Graph与M32回退通过。', '实际42层BF16 down权重独立调用GPU _after_loading helper及新opaque，保留原W与层buffer；不计时、不运行完整Llama安装链。')
CODE['bf16-nonly-down'] += ['experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/result.json', 'experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/source/worker.py', 'experiments/framework/20261026T105528588827Z-biv150-nonly-down-M32-component/archive-receipt.json']
BATCH_RESULTS['nonly_down_M32_positive_component']=('同一N128 BF16无损格式的新M32消费者，真实layer0 down权重＋实际32行独立输入，原opaque/F.linear配置实捕；8门逐位/FP64/换值Graph/side/输入不变及RNG通过。完整Graph ABBA Event0.100297115743→0.096656851470ms，省约3.63%；保留单次单层组件正信号，不授模型/官方资格，不消除原W/P双份1008MiB风险。', '保留M32组件正信号，和M64分别记录；单次ABBA不能写稳定模型收益，42层及实际Attention/KV交织尚未测。', '8门通过，实际M32独立backing；完整GEMM Graph一次ABBA省约3.63%。', '同一layer0真实权重、实际32行独立输入；运行时捕获原opaque配置，候选N128消费者按已声明边界接线，数值/Graph门后唯一完整ABBA。')
CODE['bf16-nonly-down'] += ['experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/result.json', 'experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/source/worker.py', 'experiments/framework/20261026T105751336178Z-biv150-nonly-down-M2048-component/archive-receipt.json']
BATCH_RESULTS['nonly_down_M2048_negative_component']=('同一N128格式的新M2048消费者，实际2048行独立输入；8门逐位/FP64/换值Graph/side/输入不变及RNG通过。基线真实BN256，候选为适应N128物理分块明确改BN128，完整Graph ABBA Event0.565791100264→0.914294451475ms，慢约61.60%，停止当前大M候选，不进模型。此差异包含BN256→128，不能归因为纯布局；负结果不否定独立M32/M64正信号。', '停止当前N128大M候选，保留负证据；不扩模型、不混入M32/M64收益。若研究保留原BN256的P256，应作为新独立方法验证。', '8门通过，但完整GEMM Graph一次ABBA慢约61.60%；性能负，不是正确性失败。', '实际M2048独立输入/原opaque配置实捕；原BN256→候选BN128是已声明必要差分，其余BM/BK/warps/stages沿原；原8门后一次ABBA，负即停。')

# 20261026 P256同tile负结果收尾
GROUPS['bf16-nonly-down']=('BF16 down N方向分组布局', 'N128：M64单层省10.5534%、M32省约3.63%，M2048降BN后慢61.60%；新N256布局保持原tile仍慢25.01%，停止全M路线。各轮数值门通过；42层helper/Graph不是完整模型或官方成绩，双份1008MiB及KV成本未消除，不叠加各M收益。', [])
CODE['bf16-nonly-down'] += ['experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/result.json', 'experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-original_linear.ttgir', 'experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/2048-n256_linear.ttgir', 'experiments/framework/20261026T111350707291Z-biv150-n256-down-M2048-component/archive-receipt.json']
BATCH_RESULTS['n256_down_M2048_negative_component']=('新P[N/256,K,256]无损布局的M2048单层组件；原opaque/F.linear实际BM256/BN256/BK32、w16/s2全部保持，config_difference为空。8门逐位/独立FP64/换值Graph/side及RNG通过。完整GEMM Graph一次ABBA Event0.563351333141→0.704238474369ms，慢约25.01%，停止后续M32/M64及单份全M生产。两臂B SME2均真；原A/B均两槽异步共享环，候选仅A异步、B同步，shared65536→49152、寄存器97→96、spill0；流水变化与回退同时观测，未隔离精确因果。性能负而非数值错误；不覆盖N128独立结果，无模型/官方资格。', '停止本P256布局与单份全M生产准备，不扫tile、不改编译器；保留8门通过及完整负性能证据，不否定N128 M32/M64的独立组件正信号。', '实际原tile完全相同；8门/RNG通过，完整Graph一次ABBA慢约25.01%；DB恢复、源码不变及所属进程清理通过。', '真实layer0 down权重、实际2048行独立输入；P[N/256,K,256]只改物理地址，原opaque/F.linear配置实捕后保持全部参数、dot/K顺序；原8门后唯一完整Graph ABBA，负即停。Event不含加载pack或eager CPU输出分配。')

# 20261026 N-only M64官方首暖负收尾
GROUPS['bf16-nonly-down']=('BF16 down N方向分组布局', 'N128单层M64省10.5534%、M32省约3.63%；M64-only官方4K首暖5440.33对5533.03观察−1.675393%后停，512 SUCCESS，无16K/105。pack42/FX42/M64已证，KV516320；compute-order固定源SHA拒绝回退使prefill栈未闭合，不能纯归因布局。N128大M慢61.60%、同tile N256慢25.01%，全M路线停止。', [])
CODE['bf16-nonly-down'] += ['experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds/benchmark_results/raw_runs_20261026_192922.csv', 'experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/performance-stop-decision.json', 'experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/posthoc-after-stop.json', 'experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/prefill-activation.json', 'experiments/official/20261026T112706Z-main6971-nonly-down-four-rounds-control/archive-receipt.json']
BATCH_RESULTS['nonly_down_official_first_warm_negative']=('M64-only N128布局候选原官方4K冷/首暖4758.57/5440.33 tok/s，两轮512 SUCCESS；首暖对5533.03观察下降1.675393%，按规则主动SIGTERM早停，owner exit1不是框架错误，11:39:06清理及DB/source/native恢复通过。新路径pack42层/1056964608B、真实FX42个opaque和首次M64编译选中已证；KV516320对548336，低于理论523760。prefill全栈未闭合：compute-order因model_runner固定源SHA不匹配明确scope拒绝回原路，虽normalization/Q-hoist实际选中仍prefill_valid=false，不能作只改变N-only的严格因果比较。停止本模型候选；无16K/105/完整四轮或新基线，不继承103/105。', '停止旧v1原样运行；该组compute-order回退，不能作N-only净收益判定。保留原结果；精确身份修复作为新源码独立官方对照，尚未证明收益。', '两轮4K共512 SUCCESS；pack42/FX42/M64选中已证，但compute-order源SHA门拒绝，全prefill栈未闭合；按首暖负主动早停，清理通过。', '原官方benchmark与服务参数，4K输入/1024输出/c64/256请求，原定每档四轮；保留候选默认启用及1008MiB常驻权重，不隐去KV成本。复用未变基线，完成冷/首暖后按对应5533.03筛选，低于即停，不运行16K或105。')

# 20261026 GQA scalar-page-base负结果
GROUPS['gqa-scalar-page-base']=('GQA标量KV页基址', '标量KV页基址＋二维span，保原while/page16/FP顺序；8类门及跨臂逐位通过，完整组件Event慢0.38635%，停止。SGPR spill75为lane保存，非HBM；实际SME传输仍0。for＋scalar组合机制尚未验证。', [])
CODE['gqa-scalar-page-base']=['experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/source/kernel.diff', 'experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/results.json', 'experiments/framework/20261026T114133003627Z-gqa-scalar-page-base-hotspot-component/archive-receipt.json', 'analysis/main6971-084521-nodes/gqa-scalar-page-base-114133.json']
BATCH_RESULTS['gqa_scalar_page_base_negative_component']=('原page16 while与FP顺序不变，将KV页基址提升为标量并保留二维span；实际N64/S2、4K观测长度多重集、合成激活，8类原门及跨臂逐位通过。完整producer＋原reducer Graph一次ABBA Event0.542196542→0.544291317ms，慢0.38635%，wall慢0.18463%，停止不接模型。SGPR64→104、SGPR spill字段0→75；ASM保存于VGPR lane，private_segment=0，不能当HBM spill或独立耗时因果。真实LLVM/ASM SME传输仍0，mask14→62和TTGIR标签不是实际启用证明。动态for＋scalar只属未验证机制候选，不继承旧for或本轮资格；无官方/105/新基线，source/DB/native及清理通过。', '停止当前scalar-page-base实现，不进模型或合并；保留正确性通过及小幅负结果，不把一次ABBA写稳定因果。for＋scalar尚未实现验证，不自动列为已获益组合。', '8类原门、独立FP64适用样本、换值Graph/side/写入/输入RNG与跨臂逐位通过；完整组件Event慢0.38635%，实际SME传输0。', '沿main6971实际N64/S2及4K replay32长度多重集，合成Q/KV；原page16 while、数学/reducer不变，仅标量化KV页基址＋二维span。原数值门后完整producer＋reducer一次16-call ABBA；不修改模型或官方参数。')

# 20261026 N-only身份修复官方混合收尾
GROUPS['bf16-nonly-down']=('BF16 down N方向分组布局', 'N128单层M64省10.55%、M32省3.63%；精确身份修复后的M64-only官方4K暖均5719.8133（观察+1.1145%），16K首暖4005.55（观察−2.7652%）后停。六轮1280 SUCCESS、旧prefill栈/新FX42闭合；KV516320、1008MiB常驻副本，保留混合结果，不合并/定基线/跑105。旧v1身份失配与大M两种负布局分别保留。', [])
CODE['bf16-nonly-down'] += ['experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds/benchmark_results/raw_runs_20261026_200712.csv', 'experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/performance-stop-decision.json', 'experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/posthoc-after-stop.json', 'experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/prefill-activation.json', 'experiments/official/20261026T120453Z-main6971-nonly-down-identity-fixed-four-rounds-control/archive-receipt.json', 'analysis/2026-10-26-local-to-e2e-budget.md']
BATCH_RESULTS['nonly_down_identity_official_mixed_no_baseline']=('N-only M64精确runner身份修复v2，原compute-order/normalization/Q-hoist及新42pack/FX42实际闭合，posthoc valid/prefill_valid=true。4K四轮4899.30/5700.44/5672.77/5786.23 tok/s，弃冷暖均5719.813333对5656.77观察+1.114476%；16K冷/首暖3642.71/4005.55，首暖对4119.46观察−2.765168%后主动停止，六轮1280 SUCCESS。KV516320对548336；4K日志KV最高62.6%、Running最高64，16K最高100%、Running最高31，基线前两轮最高33；双方日志未发现抢占/重算记录，无独立计数。本轮M64调用分布未采，旧16K小M窗口仅历史参考；1008MiB副本及容量/调度差异公开，不声称严格布局因果。保留4K正/16K负混合结果，停止本轮后续16K/105，不合并、不定新基线；source/native/DB/清理通过。', '保留组件及4K正信号和完整负载原件；本M64-only双权重组合16K首暖负，停止后继，不合并或定新基线。容量压力是已有日志支持的可能解释，未独立隔离因果；准确率未跑、不继承103/105。', '原官方六轮1280 SUCCESS；修复后旧prefill栈与42个新opaque实际绑定均有效，posthoc=true；按16K首暖负主动早停，SIGTERM/owner exit1原样保留，DB/source/native及清理通过。', '原官方benchmark/服务参数，4K/16K输入、1024输出、并发64、请求256/128；M64原已测kernel/helper/runner不变，只修compute-order精确runner身份。4K完成四轮，16K完成冷/首暖后按对应首暖比较停止；不重测未变基线，不继承105。')

# 20261026 GQA for scalar i64实际SME负结果
GROUPS['gqa-scalar-page-base']=('GQA标量KV页基址与动态for组合', 'scalar＋while原8门过但慢0.38635%，SME未生效；后继for＋scalar＋一维i64正确性及逐位通过，实际SME LLVM/ASM各8条，却完整组件慢10.73864%。两者停止，不接模型；机制成功不等于净收益。', [])
CODE['gqa-scalar-page-base'] += ['experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/source/kernel.diff', 'experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/results.json', 'experiments/framework/20261026T134937447894Z-gqa-for-scalar-i64-hotspot-component/archive-receipt.json', 'analysis/main6971-084521-nodes/gqa-for-scalar-i64-134937.json']
BATCH_RESULTS['gqa_for_scalar_i64_negative_component']=('动态for＋标量页基址＋一维int64后expand，保持原NHD/page16/FP顺序与producer＋reducer；8类门、有限跨臂逐位硬门及非有限原语义诊断通过。完整Graph Event0.541995287→0.600198209ms，慢10.73864%，wall慢10.42853%，停止不接模型。LLVM/ASM实际SME指令均0→8，完整页路径启用而tail原路；VGPR93→81、SGPR64→84、spill均0、shared8192→10240，不能仅凭资源或指令认定收益/精确慢因。无官方、105或新基线，DB/source/native和清理通过。', '停止本组合及模型扩展；保留真实SME已生成、数值通过与净性能负证据，不以指令成功或资源下降继续盲扫。', '8类原门及有限跨臂逐位硬门通过，非有限原门/bit诊断通过；原641478生产核与reducer绑定。完整组件慢10.73864%，实际SME LLVM8/ASM8。', '复用main6971实际N64/S2、4K观察长度多重集的合成Q/KV组件；只组合三个编译条件，FP/页序/reducer/参数不变。计时前完成原数值检查，再完整producer＋reducer Graph 16-call ABBA，非官方性能或模型准确率。')

# 20261026 GQA stages2实际流水负结果
GROUPS['gqa-scalar-page-base']=('GQA标量KV页基址与动态for组合', 'scalar＋while慢0.38635%且SME未生效；for＋scalar＋一维i64 stages1实际SME8却慢10.73864%；stages2实际async-copy4/SME16仍慢27.63241%。三项原8门/逐位通过，均停止不接模型，机制生成不等于净收益。', [])
CODE['gqa-scalar-page-base'] += ['experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/source/kernel.diff', 'experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/results.json', 'experiments/framework/20261026T141615226388Z-gqa-for-scalar-i64-s2-hotspot-component/archive-receipt.json', 'analysis/main6971-084521-nodes/gqa-for-scalar-i64-s2-141615.json']
BATCH_RESULTS['gqa_for_scalar_i64_s2_negative_component']=('在已测for＋标量页基址＋一维int64组合上仅candidate num_stages=2；原生产A保持1，reducer/数学/页序/布局不变。8类原门及跨臂逐位通过，完整producer＋reducer Graph Event0.541960925→0.691717803ms，慢27.63241%，wall慢27.18074%。实际软件流水生成TTGIR async-copy4、LLVM/ASM SME各16条，shared8192→18432，仍无净益；停止stages2，不扫stages3/不接模型。DB/source/native及设备清理通过，无官方/105或新基线。', '停止当前SME流水路线并保留数值通过、机制生成与净负结果；不以异步指令数或低寄存器替代收益。', '8类原门和跨臂bitwise通过；实际候选编译stages2、TTGIR async-copy4、LLVM/ASM SME16。未取得模型准确率资格。', '复用main6971实际N64/S2及4K观察长度的合成Q/KV组件；原8门后完整producer＋reducer 16-call Graph ABBA，baseline stages1、candidate stages2，单项非参数扫描。')

# 20261026 main594实际MM身份
GROUPS['shape-gemm']=('BI-V150特定形状GEMM', '历史main6971的宽tile/小M SplitK等保留原组件正、模型负及路径不完全可比的限制。PR59合并后，main594的compiled M9–127已改为MM-out；本站M64实取BM64/BN64/BK128、w16/s2、grid32，原窄N双波提案已被覆盖而停止。旧15ef/F.linear局部收益不迁移到新基线。此轮仅身份/资源读取，无候选计时或新吞吐，后续以新main真实路径继续研究。', [])
CODE['shape-gemm'] += ['experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/result.json', 'experiments/framework/20261026T150802838380Z-main594-m64-mm-provider-probe/archive-receipt.json', 'analysis/2026-10-26-team-main594-source-manifest.json', 'analysis/2026-10-26-team-main594-github-receipt.json']
BATCH_RESULTS['main594_mm_provider_identity']=('团队PR59已合入main594，实际compiled M64走small_linear_out→MM-out。本站单次原callback证实BM64/BN64/BK128、w16/s2、grid32、shared64KiB、spill0及实际B SME；有限性/FP64抽样/输入不变sanity通过，无计时/候选/模型资格。原BN128→64窄N提案已被新main覆盖，停止旧方案，不重复开发。DB未变及所属进程/9031/设备清理通过。', '停止旧窄N提案，按新main实际MM重新选题；原探针和源码身份保留。', '单次sanity通过，不是完整数值/模型/105门。', '新main原callback唯一调用，实际registrar/SDK/stride/LibEntry配置与IR资源；无计时，不改库或DB。')

# 20261026 main594 M64固定寻址
GROUPS['shape-gemm']=('BI-V150特定形状GEMM', 'PR59合并后按main594真实MM-out继续。M64原路径已BN64/grid32，旧窄N停止；新增固定寻址仅去通用地址除余，原tile/math/自然权重保持。8门及RNG通过，单组完整MM Graph省1.47792%，无权重副本；保留组件正信号，待同main594生产官方对照，不把旧main6971数据迁为新候选收益。', [])
CODE['shape-gemm'] += ['experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/source/candidate.py', 'experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/result.json', 'experiments/framework/20261026T153134266216Z-main594-m64-fixed-address-component/archive-receipt.json']
BATCH_RESULTS['main594_m64_fixed_address_positive']=('新main594实际MM-out，固定M64/N2048网格寻址，原tile/runtime K/dot/原W不变，无额外权重。8类数值/FP64/换值Graph/side门及RNG通过；唯一ABBA完整MM Event 59.546635→58.666585us，单组省1.47792%。实际rcp3→0，SME/async/shared/regs不变。仅单层组件信号，未有42层/模型/105/官方或新基线资格；保留进入同版本生产对照。DB/source/进程与9031清理通过。', '保留组件正信号；最小生产接线后同main594官方对照，尚不合并或更新基线。', '8类全输出逐位/有限性/输入不变及独立FP64、Graph、side/RNG通过；只覆盖M64和layer0。', '实际生产MM callback对候选、同原W和预分配out，唯一ABBA各16次完整Graph；profiler关闭、DB恢复，无pack或永久副本。')

# 20261026 M64生产候选差分入口
CODE['shape-gemm'] += ['analysis/m64-fixed-address-production-20261026/README.md']

# 20261027 main594中断恢复
CODE['shape-gemm'] += ['experiments/official/20261026T154111Z-main594-official-control-four-rounds/benchmark_results/raw_runs_20261026_234328.csv', 'experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/interruption-recovery.json', 'experiments/official/20261026T154111Z-main594-official-control-four-rounds-control/posthoc-provider-recovery/result.json']
BATCH_RESULTS['main594_control_interrupted_4k_complete']=('main594原控制4K四轮全部SUCCESS，1024请求，4909.31/5843.85/5767.56/5931.59 tok/s，弃首均值5847.6667。首轮16K中断，无完整16K行，末尾无框架错误证据，原因未确认。原PID全部退出，原件及中断DB已保存，恢复初始207f；source/native未变。旧provider reader未识别CacheCompiledArtifact，已只读原产物补证，真实out调用1/4/3/3；旧false和原state保留，不重测4K。只作为独立4K控制，尚非完整官方基线。', '保留已完成4K控制，独立新服务补16K；候选也分负载启动，不拼接为同一连续8轮。', '4K请求全成功与实际路径证据已回收；不等于105准确率通过。', '原官方4K先跑四轮；16K首轮中断，原日志/CSV未改；同初始DB与native、无profiler。')

# 20261027 main594完整16K控制
CODE['shape-gemm'] += ['experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/raw_runs_20261027_004556.csv', 'experiments/official/20261026T164443Z-main594-control-16k-four-rounds/benchmark_results/summary_20261027_004556.csv', 'experiments/official/20261026T164443Z-main594-control-16k-four-rounds-control/state.json']
BATCH_RESULTS['main594_control_16k_complete']=('main594/native14f/初始DB207f独立16K官方四轮全部SUCCESS，512请求；3742.06/4194.03/4191.88/4191.56 tok/s，弃首均值4192.49。原validator四行/一summary及token数通过，实际provider/prefill/native路径闭合；源码未变、DB/设备清理通过。与原已完成4K组成分服务性能控制，不能冒充同run连续八轮或105准确率资格。', '保留同源16K性能控制，候选按相同独立新服务协议比较。', '512个请求成功与实际执行路径通过；未授新105资格。', '原官方16K参数，四轮弃首均值；新服务无先跑4K，初始DB207f/native14f，与候选分档对称。')

BATCH_RESULTS['main594_m64_fixed_address_firstwarm_negative']=('M64固定寻址生产候选同main594/native14f/初始DB207f，4K冷轮5014.13、首暖5743.94 tok/s；对同档首暖5843.85观察低1.70966%，按约定提前停止，512请求全部SUCCESS，新旧实际路径通过。原组件省1.47792%未转为本次官方首暖收益；单组不证明稳定回退或纯kernel因果。未跑后两轮、16K或105，无新基线/合并资格。SIGTERM来自性能监督器，不是框架报错；source/native不变、DB与设备清理通过。', '停止当前M64生产路线；保留组件与官方负结果，不开优化PR或拼成完整四轮成绩。', '原件中已执行检查按范围保留；不继承模型准确率。', '精确命令、版本及原始结果见本轮manifest/state、source和日志。')
CODE['shape-gemm'] += ['experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds/archive-receipt.json', 'experiments/official/20261026T172509Z-main594-m64-fixed-address-4096-four-rounds-control/supervisor-final.json']

BATCH_RESULTS['main594_m32_provider_identified']=('未改main594的small_linear_out原callback仅调用一次：M32/N2048/K6144实际BM32/BN64/BK128、w8/s2、grid32、split1，hash021fc309；shared49152、regs25、spill0、async4、B useSme2。原权重与输入不变、有限性及FP64样本通过，DB/进程/9031清理通过。无计时、候选或模型/105资格，不证明当前16K的形状覆盖。', '保留真实配置，准备一个M32固定寻址组件；不能直接搬用M64配置或收益。', '原件中已执行检查按范围保留；不继承模型准确率。', '精确命令、版本及原始结果见本轮manifest/state、source和日志。')
CODE['shape-gemm'] += ['experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/result.json', 'experiments/framework/20261026T173900314676Z-main594-m32-mm-provider-probe/archive-receipt.json']

GROUPS['shape-gemm']=('BI-V150特定形状GEMM', 'main594分服务性能控制：4K暖均5847.6667、16K4192.49。M64固定寻址组件省1.47792%，但实际4K首暖5743.94对5843.85低1.70966%，512请求成功后按约定停止，无16K/105或合并。M32原路径配置已取得，仅作后继依据；组件收益与模型结果分别保留。', [])

BATCH_RESULTS['main594_m32_fixed_address_positive']=('M32固定寻址真实原MM-out同32/64/128、w8/s2和原W；原八项逐位/FP64/换值Graph/side及RNG通过。唯一ABBA完整MM Event 49.417669→48.984375us，单组省0.87680%；实际rcp3→0，SME6/async4/shared49152/regs25/spill0保持，无额外权重或workspace。仅layer0组件正信号，尚无模型/105/官方资格；DB207f恢复、source/进程与9031清理通过。', '保留M32组件证据；后续官方16K首暖低0.23295%，本次生产路线已停止。', '原件中已执行检查按范围保留；不继承模型准确率。', '精确命令、版本及原始结果见本轮manifest/state、source和日志。')
CODE['shape-gemm'] += ['experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/result.json', 'experiments/framework/20261026T174414509153Z-main594-m32-fixed-address-component/archive-receipt.json']

GROUPS['shape-gemm']=('BI-V150特定形状GEMM', 'main594分服务性能控制：4K暖均5847.6667、16K4192.49。M64固定寻址组件省1.47792%，但实际4K首暖5743.94对5843.85低1.70966%，512请求成功后按约定停止，无16K/105或合并。M32固定寻址八门通过，单组组件省0.87680%，保留准备独立生产对照；组件收益与模型结果分别保留。', [])

CODE['prefill-panel4']=[]

BATCH_RESULTS['prefill_panel4_long_positive']=('main594长prefill Q2047/KV16384/ctx14337，原BM128/Q16/T64/w8s1分四个K panel，split-major FP32 partial及8-head reducer。原writer、初始/换值独立FP64、全输出close、双核Graph换值、输入/RNG/guard通过；归约树改变，非逐位。直接暖JIT唯一ABBA完整双核Event 8.304069→8.119503ms，单组省2.222603%，wall省2.086496%。新增68124160B workspace及全部读写/归约计入；分配在计时外，不声称生产容量或L2命中已证。DB/source/native及设备清理通过。保留，先补新分界边界和单workspace生产接线；尚无模型/105/官方资格。', '保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。', '原件中已执行检查按范围保留；不继承模型准确率。', '精确命令、版本及原始结果见本轮manifest/state、source和日志。')
CODE['prefill-panel4'] += ['experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/results.json', 'experiments/framework/20261026T180225915687Z-prefill-panel4-long-component/archive-receipt.json']

GROUPS['prefill-panel4']=('长prefill四面板完整Attention', 'main594长prefill Q2047/KV16384/ctx14337，原BM128/Q16/T64/w8s1分四个K panel，split-major FP32 partial及8-head reducer。原writer、初始/换值独立FP64、全输出close、双核Graph换值、输入/RNG/guard通过；归约树改变，非逐位。直接暖JIT唯一ABBA完整双核Event 8.304069→8.119503ms，单组省2.222603%，wall省2.086496%。新增68124160B workspace及全部读写/归约计入；分配在计时外，不声称生产容量或L2命中已证。DB/source/native及设备清理通过。保留，先补新分界边界和单workspace生产接线；尚无模型/105/官方资格。', [])

BATCH_RESULTS['main594_m32_fixed_address_firstwarm_negative'] = ('M32-only固定寻址生产候选基于main594/native14f/初始DB207f，未叠M64。16K冷轮3581.18、首暖4184.26 tok/s，对可比首暖4194.03低0.23295%；两轮256请求全部SUCCESS，真实新核及原栈启用。按约定首暖筛选停止，未跑后两轮/4K/105；SIGTERM是性能监督器，不是框架数值错误。源码/native不变、DB与设备清理通过。组件0.8768%省时未转成这组官方净收益，小幅差异不声称稳定退化；不更新基线、不提合并优化PR。', '停止本次M32生产路线，保留全部两轮原件；不继续旧main验证或把局部收益算官方收益。', '按原件保留已测正确性范围，不继承模型准确率。', '精确命令、源码、原始CSV/日志和清理见本轮原件。')
CODE['shape-gemm'] += ['experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds-control/supervisor-final.json', 'experiments/official/20261026T180653Z-main594-m32-fixed-address-16384-four-rounds/archive-receipt.json']

BATCH_RESULTS['main241_q32_panel4_negative'] = ('PR47合并后以main241真实Q32/w16为A，Q2047/KV16384；B同tile/warp加入四个K panel及完整reducer。实际Policy/Manager/hash绑定、初始与换值独立FP64/fullclose、Graph及输入/RNG/guard通过；非逐位。暖JIT完整双核ABBA 6.559703588→7.375295639ms，耗时增加12.43337%，wall增加13.98933%；68124160B scratch读写及reducer计入。source/native/DB/9031清理通过。停止该组合，不扫参数或进生产。旧Q16组件2.2226%仅保留历史，不能覆盖新Q32或继承到组合。', '停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。', '按原件保留已测正确性范围，不继承模型准确率。', '精确命令、源码、原始CSV/日志和清理见本轮原件。')
CODE['prefill-panel4'] += ['experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/results.json', 'experiments/framework/20261026T183816740050Z-prefill-q32-panel4-long-component/archive-receipt.json']

GROUPS['shape-gemm'] = ('BI-V150特定形状GEMM', 'main594控制4K暖均5847.6667、16K4192.49；M64首暖低1.70966%，但旧4K控制与候选跨容器，不能归因于方法。M32首暖低0.23295%，与16K控制同在重启后；两者按约定停止且请求全成功。后续以main241研究，原main594 4K另作重启后两轮复查。', [])
# 环境后核只补充解释，不覆盖原始测量或当时停止记录。
_m64_key='main594_m64_fixed_address_firstwarm_negative'
_m64_result=BATCH_RESULTS[_m64_key]
BATCH_RESULTS[_m64_key]=(_m64_result[0]+'新增环境限制：旧4K控制15:41早于当前PID1约16:11:13 UTC起点，M64于17:25在其后；相同6核配额但cgroup计数重置，跨容器/进程环境，不能把−1.70966%单独归因于候选。原main594重启后4K冷暖两轮已排在main241 16K清理之后，尚无新结果。', '暂不恢复M64生产路线；先复查同源码4K环境漂移，原组件和两轮记录保留。', *_m64_result[2:])
CODE['shape-gemm'] += ['experiments/environment/20261026T185836Z-container-context/container-observation.json', 'experiments/environment/20261026T185836Z-container-context/comparison-context.json']


GROUPS['prefill-panel4'] = ('长prefill四面板完整Attention', '旧main594 Q16组件省2.2226%；新main241 Q32/w16已合并，真实同配置panel4组合反而慢12.43337%，数值门通过但停止生产接入；旧边界准备保留未执行。', [])

GROUPS['baseline-environment']=('基线接续与容器环境复查','当前main241/native14f原官方4K/16K各四轮暖均5850.05/4487.49 tok/s，同身份105题104/105通过。105未覆盖Q32/C3，原owner覆盖检查失败单独保留。main594重启后4K首暖下降2.01%仅为两轮诊断，不证明容器因果；不同源码、KV和实验目的不混算。',[])
CODE['baseline-environment']=[]
BATCH_RESULTS['postrestart_4k_two_rounds']=('原main594/native14f/初始DB207f重启后4K两轮诊断：冷5612.30对4909.31（+14.32%），首暖5726.40对5843.85（−2.0098%），512请求全部成功。旧三暖5767.56–5931.59，本轮首暖比旧最小低0.714%；源码/DB/native与时钟相同，KV容量548432→548384少48tokens，不能称完全同环境。观察到小幅暖轮下移，不能由一个首暖证明持续回退或容器启停因果；不替换完整四轮基线、不追加大测。旧M64跨容器负比较不能全归因于方法。', '保留原件；不补大测，不更新正式四轮基线。', '请求及实际路径检查通过，不等于模型准确率资格。', '源码、精确命令、原始CSV/日志及清理见本轮原件。')
CODE['baseline-environment'] += ['experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/archive-receipt.json', 'experiments/official/20261026T192108Z-main594-postrestart-4k-two-round-diagnostic/result.json']
BATCH_RESULTS['main241_control_16k_complete']=('新团队main241/native14f/初始DB207f原官方16K四轮3791.43/4489.43/4487.31/4485.73 tok/s，弃首暖均4487.49，512请求全部成功；对旧main594暖均4192.49观察+7.0364%；KV容量548288→548432多144tokens，非严格等KV单项因果。实际Q32与原优化栈通过，source/native/DB恢复及清理成功。本次仅16K正式四轮，未取得本站新main4K或105资格；不冒用队友native5cbb成绩。', '保留新main同口径16K控制；4K和105资格独立。', '请求及实际路径检查通过，不等于模型准确率资格。', '源码、精确命令、原始CSV/日志及清理见本轮原件。')
CODE['baseline-environment'] += ['experiments/official/20261026T184110Z-main241-control-16k-four-rounds/archive-receipt.json', 'experiments/official/20261026T184110Z-main241-control-16k-four-rounds/result.json']

GROUPS['kv-lossless']=('无损KV位编码与页内布局','真实42层位样本支持继续组件；逻辑少读约24.2%不等于HBM或吞吐收益。',[])
CODE['kv-lossless']=['experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/archive-receipt.json', 'experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/kv-bit-stats.json', 'experiments/profiles/20261027T011819661362Z-main241-real-kv-bits/result.json']
BATCH_RESULTS['real_kv_bits_sample_complete']=('main241/native14f独立诊断，原数学题256prompt tokens，42层各128token的真实post-RoPE K/V共5.25MiB；writer与cache全部逐位相等。CPU无损12bit+escape估算K/V逻辑少读24.20258%/24.21341%，全部行可压缩且复原逐位一致；按独立256B row的128B事务粒度反而多0.78125%，所以不能当HBM或吞吐收益。保留真实样本，下一项改为页内SoA/行级raw exponent fallback组件；尚无压缩生产实现、长16K代表性或模型准确率成绩。采满后按设计终止请求与自有服务，exit0、原源码不变、DB恢复及清理通过。', '保留样本；准备完整writer＋decode组件，不进入生产。', '真实writer/cache及CPU编码复原逐位相等；非模型准确率验收。', '原题及token IDs、源码/native、服务命令与清理见原件。')

BATCH_RESULTS['main241_control_4k_complete']=('main241/native14f/初始DB207f原官方4K四轮[5632.05, 5833.56, 6000.87, 5715.73] tok/s，弃首暖均5850.053333；1024请求全SUCCESS，实际Q32/原栈、源码/native不变、DB恢复及清理通过。旧main594暖均5847.666667，观察变化+0.0408%，基本持平，不宣称稳定提升；KV 548432→548288。本站main241两档吞吐控制现已补齐，完整105准确率仍未取得；不能将请求成功等同准确率通过。', '保留本站main241完整4K控制，未取得105模型准确率资格。', '1024请求和实际路径检查通过。', '原官方四轮弃首，精确命令、CSV、源码/环境及收尾见原件。')
CODE['baseline-environment'] += ['experiments/official/20261027T012646Z-main241-control-4k-four-rounds/comparison.json', 'experiments/official/20261027T012646Z-main241-control-4k-four-rounds/archive-receipt.json']

GROUPS['native-silu-lut']=('BF16 SiLU精确查表','完整gate慢10.37%，正确性通过，停止。',[])
CODE['native-silu-lut']=['experiments/framework/20261027T014725735145Z-native-silu-lut-component/result.json', 'experiments/framework/20261027T014725735145Z-native-silu-lut-component/archive-receipt.json']
BATCH_RESULTS['native_silu_lut_negative']=('真实layer20权重/M2048完整native gate：A实际14f SO、B同量化/GEMM及BF16舍入，仅以256KiB同设备精确表替SiLU expf和除法。65280有限BF16位型×12up逐位、12项真实gate/Graph/side及独立INT64、输入/表/RNG门全过。完整Graph ABBA 0.716412395239→0.790738135576ms，耗时+10.374714%；额外gather成本计入，非只测尾核。停止该实现，不扫M或生产，不声称错误或近似；DB恢复/清理通过。', '停止，不进入生产或官方测试。', '逐位/有限域/真实gate/INT64/Graph门通过。', '原始计时、实际SO与编译命令、环境和清理见原件。')

BATCH_RESULTS['kv_soa_compile_failure']=('无损KV页内SoA首包：整数提升32位后直接bitcast BF16被编译器拒绝，未获得GPU数值或计时结论。保留冻结包及失败日志；下一包只显式收为uint16再bitcast，不改框架/数学/容差。DB恢复和清理通过。', '首包编译失败，保留；单行类型修正另run验证。', '未运行数值门，不标记正确性通过或数值错误。', '原始结果、精确命令、环境、编译产物及收尾见原件。')
CODE['kv-lossless'] += ['experiments/framework/20261027T015104107809Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json']
BATCH_RESULTS['kv_soa_component_negative']=('无损KV页内SoA v2：真实KV短样本拓展组件，65536 BF16位型编码、8项数值/Graph/FP64等与writer三转换门通过，有限输入跨臂逐位一致。完整writer+producer+reducer Graph ABBA 0.543926090002→2.477649092674ms，耗时+355.512089%。停止当前实现，不扫参/进生产。CPU按128B预算省约23%并未转化为完整组件收益；实际HBM事务/占用率未测，不归因缓存。非模型准确率或官方成绩，DB恢复及清理通过。', '性能显著负，停止当前实现，不进入模型或官方测试。', '组件位型、数值、Graph、writer门通过；不等同模型资格。', '原始结果、精确命令、环境、编译产物及收尾见原件。')
CODE['kv-lossless'] += ['experiments/framework/20261027T015640083939Z-gqa-lossless12-soa-hotspot-component/archive-receipt.json']
GROUPS['kv-lossless']=('无损KV位编码与页内布局','SoA完整组件慢355.51%，正确性通过；停止实现，保留真实位样本。',[])

BATCH_RESULTS['main241_accuracy_pass_scope_limited']=('main241完整765源/native14f/DB207f，原Math500 Level3全105题、temperature1/top_p.95/max32768/batch8不变：104/105=99.047619%，valid/pass；105 stop，0请求错误/截断/空答案/空提取。34层native、实际provider、原Q-hoist/normalization通过，源码/native不变、DB恢复和清理通过。Q32已安装但本轮未selected、无fallback/解析错误，原owner复用性能组必选Q32门而completed=false，原失败保留；官方精度通过与Q32/C3覆盖不足分开，不报框架数值错误，也不声称本轮验证长prefill分支。两档吞吐控制已完成，后续以本站同身份结果作基线，不继承队友native5cbb。', '保留当前main241原官方精度结果；不为覆盖门强改框架或重测105。', '104/105达到原95%门槛，Q32/C3未被该负载覆盖。', '原预测、review/report、配置、实际native/provider及清理原件均保存。')
CODE['baseline-environment'] += ['experiments/accuracy/20261027T021016Z-main241-native14f-math500/coverage-summary.json', 'experiments/accuracy/20261027T021016Z-main241-native14f-math500-control/accuracy-review.json', 'experiments/accuracy/20261027T021016Z-main241-native14f-math500/archive-receipt.json']

GROUPS['kv-vtranspose']=('纯BF16页内V布局', '完整组件慢1.33%，停止当前实现。', [])
CODE['kv-vtranspose']=['experiments/framework/20261027T024300270939Z-gqa-bf16-vtranspose-hotspot-component/archive-receipt.json']
BATCH_RESULTS['kv_vtranspose_component_negative']=('纯BF16页内V转置：K保持NHD，V改dim×slot；原GQA只改两处V维度寻址，并实作对应writer，未压缩或增持久容量。位型、8项数值/Graph及writer换值/换slot/负slot门通过，有限输入跨臂逐位一致。完整writer+GQA+reducer Graph ABBA Event 0.544616460800→0.551862716675ms，慢1.330525%；wall慢1.184494%。静态bytepermute减少但寄存器增多，未测实际occupancy/HBM，不作因果归因。性能负，停止当前实现，不扫参、不接prefill/模型；组件正确不等于官方资格。源码/native不变、DB恢复和清理通过。', '停止当前实现，不进生产。', '组件逐位/Graph/writer门通过；未运行模型或官方资格。', '原始结果、编译产物、命令与环境已回收，实际occupancy/事务未测。')

GROUPS['q32-mixed-overlap']=('当前Q32与GQA混合双流', '完整GPU耗时负，不进入生产，不扫形状或流优先级。', [])
CODE['q32-mixed-overlap']=['experiments/framework/20261027T030312159264Z-q32-mixed-overlap-mixed-component/archive-receipt.json']
BATCH_RESULTS['q32_mixed_overlap_negative']=('main241真实D63/P1985/KV4096，Q32 grid63×2，GQA自然S4/grid63×2×4。A串行、B原93c双流，完整writer+两路Attention/reducer+fork/join/event/record_stream/collect均计入。32calls ABBA Event 2.071281075478→2.185644984245ms，慢5.521409%；wall 2.222790375→2.211624625ms，省0.502330%，不一致且B两块波动大，无净收益。九项正确性检查全过，selected68/fallback1/pending最终0/峰值9；源码/native不变，DB恢复和清理通过。停止本实现，不证明实际共驻，不进生产。', '完整GPU耗时负，不进入生产，不扫形状或流优先级。', '真实Q32/GQA绑定、换Q即时消费、整输出逐位及输入/KV/RNG门通过，pending最终0；不等于官方资格。', '完整原件、精确命令、环境与收尾证据已回收。')
GROUPS['sampler-preprocess-stats']=('采样转换与首遍统计融合', '保留原启动失败，只修入口源码路径后单独重试；无收益或数值结论。', [])
CODE['sampler-preprocess-stats']=['experiments/framework/20261027T030446321226Z-sampler-preprocess-stats-component/archive-receipt.json']
BATCH_RESULTS['sampler_preprocess_entry_import_failure']=('首包f3e99d0a在候选执行前失败：入口PYTHONPATH只包含assets，导入安装旧vllm_fl，缺biv150_runtime，ImportError。cases/timings均空，尚无数值或性能结论，也不是生产框架报错。保留原包和26原件；下一包仅绑定main241765源码路径及复用既有身份检查，数学和候选不改。原owner已恢复DB并清理自有进程。', '保留原启动失败，只修入口源码路径后单独重试；无收益或数值结论。', '候选尚未运行，不能标记数值通过或数值错误。', '完整原件、精确命令、环境与收尾证据已回收。')

BATCH_RESULTS['sampler_stats_equality_failed_raw_pending']=('采样融合v2仅修main241源码入口，真实head首组scaled/filtered/sampled IDs、global/per-request RNG、输入及独立CPU FP64转换均通过，但stats_bitwise=false，按预定门停止；timings为空，后续换值/Graph/性能未运行。不能称原main框架报错或已造成预测错误，也不接受为等价候选。03:19:32 UTC收尾，DB恢复、source/native不变。结果已通过SSH读到；随后网关仅提供publickey且拒绝原密钥，完整原件暂留实验机，未伪造归档回执。停止本实现，不改容差/数学或继续变体。', '停止当前实现，无性能或官方资格。', '首组统计逐位不符；输出IDs相同不能代替全等价门。', '仅已读回摘要在本地，完整原件仍在实验机；恢复SSH后回收，不重测。')
GROUPS['sampler-preprocess-stats']=('采样转换与首遍统计融合', 'v2首组统计逐位门失败，停止；无性能计时，完整原件待回收。', [])
CODE['sampler-preprocess-stats'] += ['experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component/ssh-readback-summary.json']

BATCH_RESULTS['sampler_stats_equality_failed']=('采样融合v2真实head首组scaled/filtered/IDs/RNG相同，但stats_bitwise=false，按预定门停止；无计时，后续换值/Graph/性能未运行。不能称原main预测错误，也不接受为等价候选。DB恢复、source/native不变；36份原始文件已完整回收并逐SHA核验，保留此前SSH读回摘要。停止当前实现。', '停止当前实现，无性能或官方资格。', '统计逐位门失败；不能用IDs相同替代。', '36份原件已完整回收，SHA通过；不重测。')
GROUPS['sampler-preprocess-stats']=('采样转换与首遍统计融合', 'v2统计逐位门失败，停止；无性能计时，原件已完整回收。', [])
CODE['sampler-preprocess-stats'] += ['experiments/framework/20261027T031858174112Z-sampler-preprocess-stats-component/archive-receipt.json']

CODE['main6971-graph-profile'] += ['experiments/profiles/20261026T084521Z-main6971-production-hotspot-4k/posthoc-20261027/summary.md']

GROUPS['gqa-s2-incta']=('S2同CTA归约', '首次编译失败；停止当前实现，无数值或性能结论。', [])
CODE['gqa-s2-incta']=['experiments/framework/20261027T043321686931Z-gqa-s2-incta-hotspot-component/archive-receipt.json']
BATCH_RESULTS['gqa_s2_incta_compile_failed']=('S2两段同CTA/w2并在核内归约，拟省全局partial读写和一次启动；保持原page16、KV布局与逐段数学。实际CoreX在首个candidate的TritonGPUAccelerateMatmul阶段编译失败；checks/timings均空，未取得数值或性能结论。停止当前实现，不改编译器、门或重封包，不进入生产。main241/native14f/source2596与新main56同GQA源码；DB已恢复、源码/native不变、9031空闲及GPU清理通过。全部39份原件已回收逐SHA核验。', '停止当前实现，不进生产。', '首candidate编译失败，数值和性能均未开始。', '完整源码、命令、环境、失败日志及清理证据已回收。')

CODE['lm-head-temperature']=['experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/archive-receipt.json', 'experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/result.json', 'experiments/framework/20261027T050730877973Z-lm-head-temperature-epilogue-component/source/candidate.py']
BATCH_RESULTS['lm_head_temperature_component_positive']=('R64真实LM-head权重130560×2048、合成hidden；保留原BF16舍入后融合FP32转换与温度除法，原stats/top-p/RNG不变。10组逐位/FP64/采样ID/RNG/换值Graph及输入不变检查通过。完整eager head+Sampler唯一ABBA含分配与提交，Event3.828030→3.165252ms（省17.3138%），wall4.165081→3.655269ms（省12.2401%），无CPU节流。寄存器31→37，shared40960B不变，两臂spill0，无候选新增持久权重副本。保留局部正信号，下一步最窄生产接入；尚非模型准确率或官方吞吐资格，不迁移为整模收益。main56/native14f，DB恢复、源码/native不变及清理通过。44份原件逐SHA核验。', '保留局部正信号，待实际服务验证；不是官方收益。', '10组逐位、独立FP64、IDs/RNG及换值Graph门通过。', 'R64真实head W/合成hidden，唯一完整eager ABBA，原采样链不变。')

BATCH_RESULTS['main56_control_4k_complete']=('main56/native14f原官方4K四轮暖均5902.77 tok/s，1024请求成功，KV548432；原栈及清理通过。仅4K控制，不继承16K或105。', '保留本站main56完整4K控制；无16K/105资格。', '1024请求和原实际路径检查通过。', '原官方四轮弃首，原命令、CSV、807源及收尾见原件。')
CODE['baseline-environment'] += ['experiments/official/20261027T052425Z-main56-control-4k-four-rounds/comparison.json', 'experiments/official/20261027T052425Z-main56-control-4k-four-rounds/archive-receipt.json']
GROUPS['baseline-environment']=('基线接续与容器环境复查', '本站main56/native14f原官方4K四轮暖均5902.77 tok/s，KV548432，仅保留新4K控制；无新16K或105资格。旧main241/native14f两档暖均5850.05/4487.49及104/105仍按旧源码单列，不迁移或拆成严格因果收益。', [])

BATCH_RESULTS['lm_head_temperature_4k_positive_observation']=('head温度epilogue原官方4K暖均5921.12对A5902.77 tok/s，本组+0.3109%；同KV/native/DB，1024请求及实际启用/清理通过。保留小信号，待16K/105。', '保留单组4K小收益，待16K和105；非稳定净收益结论。', '1024请求/实际head消费与原栈通过，不等于模型准确率。', '原官方4轮弃首；同main56/native14f/DB/KV，CSV对比见原件。')
CODE['lm-head-temperature'] += ['experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/comparison.json', 'experiments/official/20261027T055059Z-main56-lm-head-temperature-4k-four-rounds/archive-receipt.json']

BATCH_RESULTS['main56_control_16k_complete']=('main56/native14f原官方16K暖均4526.57 tok/s，512成功、KV548384、原栈/清理通过。', '保留本次16K控制；4K与105资格分开。', '原请求与路径/清理检查通过，不等于105。', '原官方四轮弃首；同版本候选须引用本run。')
BATCH_RESULTS['lm_head_temperature_r32_component_positive']=('R32完整head+Sampler Event省10.05%、wall省11.00%；实际BM32/BN64/BK64/w8/s1，10门过。', '保留局部正信号，待最窄生产验证；不与R64相加。', '逐位/FP64/RNG/换值Graph过；不是模型准确率。', '完整eager链ABBA含分配/提交，reg21/shared12288/spill0，无节流。')
CODE['baseline-environment'] += ['experiments/official/20261027T075834Z-main56-control-16k-four-rounds/comparison.json', 'experiments/official/20261027T075834Z-main56-control-16k-four-rounds/archive-receipt.json']
CODE['lm-head-temperature'] += ['experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/comparison.json', 'experiments/framework/20261027T083835962824Z-lm-head-temperature-r32-epilogue-component/archive-receipt.json']
GROUPS['baseline-environment']=('基线接续与容器环境复查', '本站main56/native14f两档原官方控制：4K暖均5902.77、KV548432；16K暖均4526.57、KV548384，分别1024/512成功，原栈与清理通过。两档独立服务，未继承105或候选收益；旧main241成绩按旧源单列。', [])

BATCH_RESULTS['lm_head_temperature_r64_16k_kv_mismatch_stopped']=('R64-only 16K首冷4029.77 tok/s、128成功；KV548288≠548384资格停止。head无覆盖/无异常，原栈及清理通过。', '停止旧R64-only无覆盖16K；非数值错误，不计算收益。', '首冷请求成功不等于105准确率，原SIGTERM状态保留。', '仅1个冷轮，非完整官方；R32+R64后继另行验证。')
CODE['lm-head-temperature'] += ['experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/comparison.json', 'experiments/official/20261027T084030Z-main56-lm-head-temperature-16k-four-rounds/archive-receipt.json']

GROUPS['gqa-fused-append']=('GQA尾段append融合', '只对私有尾slot省独立writer启动，不改BF16/页序/归约。实际编译VGPR增51超过预设预算后停止；数值和计时尚未运行，不称错误或实测慢，不扩展或放宽阈值。', [])
CODE['gqa-fused-append']=['experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/comparison.json', 'experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/archive-receipt.json', 'experiments/framework/20261027T090439643177Z-gqa-fused-append-hotspot-component/source/candidate.py']
BATCH_RESULTS['gqa_fused_append_resource_budget_stopped']=('尾段append融合编译成功；VGPR93→144超预设+16预算，SGPR spill0→50，shared8KiB不变。数值/计时均未运行，清理通过。', '停止冻结实现，不放宽预算或扫参；非数值错误/实测慢。', '仅编译身份与资源已取得，原8门和FP64未执行。', '唯一N64/S2；完整链ABBA尚未开始，69原件保留。')

BATCH_RESULTS['lm_head_temperature_r32_r64_16k_complete_kv_mismatch']=('新8d1a R32+R64原官方16K暖均4529.79对A4526.57 tok/s，观察+0.0710%；512成功、R32实际消费/清理通过。KV不同。', '保留完整16K微小正观察；KV不匹配，非严格因果或稳定收益。', '512请求和实际R32/原栈通过，不继承旧4K或105资格。', '原官方四轮弃首；809源8d1a，KV548432对A548384。')
CODE['lm-head-temperature'] += ['experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/comparison.json', 'experiments/official/20261027T090733Z-main56-lm-head-temperature-r32-r64-16k-four-rounds/archive-receipt.json']

BATCH_RESULTS['lm_head_temperature_r32_r64_accuracy_pass_scope_limited']=('新8d1a/809源原105：103/105=98.0952%，valid/pass，105 stop、0错误/截断/空答，owner与清理通过。', '保留当前源码的完整原官方准确率；head32/64与Q32未覆盖，分支资格另列。', '未从安装/覆盖推断分支准确率；原score与原分母不变。', '353份原件逐SHA，native14f/DB207f及实际原栈闭合。')
CODE['lm-head-temperature'] += ['experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/coverage-summary.json', 'experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500-control/accuracy-review.json', 'experiments/accuracy/20261027T094907Z-main56-head-temperature-r32-r64-native14f-math500/archive-receipt.json']

BATCH_RESULTS['lm_head_temperature_r32_r64_4k_complete_kv_mismatch']=('新8d1a官方4K暖均5971.44对A5902.77，观察+1.1634%；1024成功，R32/R64实际消费。KV不同。', '保留单组正观察；非严格因果或稳定收益，不定新基线。', '同源105为103/105且通过，但head32/64与Q32未覆盖。', '原四轮弃首；809源8d1a，KV548288对A548432；365原件逐SHA。')
CODE['lm-head-temperature'] += ['experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/comparison.json', 'experiments/official/20261027T101200Z-main56-lm-head-temperature-r32-r64-4k-four-rounds/archive-receipt.json']

BATCH_RESULTS['lm_head_temperature_r32_bn256_nonpositive']=('R32 BN256完整链Event慢2.6150%，wall快5.7801%；十门和资源门通过。', '停止BN256，不扫参、不进模型；不取第一B当收益。', '三方全scaled/filtered/IDs/RNG、独立FP64与Graph/side通过。', '真实W＋合成hidden，完整eager ABBA；shared12→36KiB、regs21→37/spill0，无节流，73原件。')
CODE['lm-head-temperature'] += ['experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/comparison.json', 'experiments/framework/20261027T103846792930Z-lm-head-temperature-r32-bn256-component/archive-receipt.json']

BATCH_RESULTS['lm_head_temperature_same_kv_4k_control_complete']=('新A暖均5923.116667；同KV候选B观察+0.8158%，1024成功。', '支持按小收益建立代码PR；不声称稳定幅度或新基线。', '组件逐位/IDs/RNG已过；同源105通过但head分支未覆盖。', '同main56/native14f/初始DB/参数，KV548288；两A暖均漂移+0.3447%，326原件逐SHA。')
CODE['lm-head-temperature'] += ['experiments/official/20261027T105243Z-main56-control-4k-four-rounds/comparison.json', 'experiments/official/20261027T105243Z-main56-control-4k-four-rounds/archive-receipt.json']
GROUPS['lm-head-temperature']=('LM-head温度epilogue融合', '原main56+受测8d1a五文件已通过中文PR84合并，main dac1b8fb。4K同KV时间相近对照暖均5923.116667→5971.44 tok/s，单组观察+0.8158%；事后首暖−1.3314%、两A漂移+0.3447%，不称稳定幅度或新官方基线。16K暖均4529.79对4526.57（观察+0.0710%），KV不同；同源105为103/105 valid/pass，但head32/64及Q32未覆盖，组件数学资格另列。BN256扩展Event负，停止且不含在PR84。旧R64-only结果不与新组合相加。', ['lm-head-temperature'])


BATCH_RESULTS['corex_native_gqa_page16_coverage_check_stopped']=('4组已执行数值均逐位；第四覆盖检查false停止，Graph/side未到。', '保存原failed_stop，CPU事后仅补输入覆盖解释；不接生产、不报性能。', '前三组独立FP64过；全门资格未取得。', '原main56/807/native14f单page16合成诊断；80原件逐SHA，exit1但清理通过。')
CODE['corex-native-gqa-page16']=['experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/comparison.json', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/result.json', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/result.json', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/posthoc-120655/recompute.py', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/related-cpu/113301/llvm-build.log', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/compile-proof/compile-check.json', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/source/backend-equivalence.json', 'experiments/framework/20261027T120655436062Z-corex-native-gqa-page16-numeric/archive-receipt.json']

BATCH_RESULTS['corex_native_gqa_page16_single_page_numeric_passed']=('v3七组全位型/FP64/Graph poison/side与coverage通过，无计时。', '保留单页数值资格；不授历史loop/性能或模型资格。', '旧120655失败保留，v3只修CPU诊断，CU8545不变。', 'main56/807/native14f；87原件逐SHA，exit0，DB/source/native清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/comparison.json', 'experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/result.json', 'experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/independent-review.md', 'experiments/framework/20261027T122022380438Z-corex-native-gqa-page16-numeric/archive-receipt.json']

BATCH_RESULTS['corex_native_gqa_s2_component_positive']=('完整S2/4K组件Event省21.5733%，wall省21.5815%；9门通过。', '保留正信号；按真实服务post-RoPE布局验证启用后再做官方对照。', 'Qstride2048，完整producer＋原reducer；不计writer，不授模型资格。', 'main56原GQA/native14f，同worker/DB；115原件，清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/comparison.json', 'experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/results.json', 'experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/independent-review.md', 'experiments/framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/archive-receipt.json']

BATCH_RESULTS['gqa_s4_fixture_guard_failed']=('S4/N32/KV16384、Qstride2560在第4案extra512守卫失败而停止，尚未计时；其余已记录数值/全partial逐位/Graph门通过。随后132510无GQA诊断复现同zero_错误写入，不能将此原失败归责新内核。保留119原件和原false；仅修输入构造后另run，原CU/bridge/容差不改。', '保留原失败及定位证据；后继仅修夹具。', '无性能或模型资格。', '同dispatch、原内核未改；DB/source/native/9031清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/comparison.json', 'experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/results.json', 'experiments/framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json']
BATCH_RESULTS['gqa_noncontiguous_zero_fixture_diagnosed']=('同FlagGems dispatch隔离8项输入构造，不调用GQA。zero_在B32/B64误改extra512分别12800/26112元素，与连续numel写入源码预测吻合；fill(1)/copy全位型通过。neg的guard保持，但零符号位与CPU不同（2114/4228项），不扩大为模型结论。52原件含实际provider源码、完整backing前后位型；保留诊断，只改后继测试夹具，不改生产框架或数值门。', '保留原失败及定位证据；后继仅修夹具。', '无性能或模型资格。', '同dispatch、原内核未改；DB/source/native/9031清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/comparison.json', 'experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/results.json', 'experiments/framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/archive-receipt.json']

BATCH_RESULTS['corex_native_gqa_s2_real_stride_positive']=('QKV切片布局（非服务post-RoPE布局）、行距2560的N64/S2/KV4096完整producer＋原reducer Graph ABBA：Event0.528684→0.413887ms（省21.7137%），wall省21.6587%。9组数值/FP64/完整partial逐位/Graph/尾槽NaN/空段/输入RNG及前后extra512守卫全部通过。v2仅修原zero_忽略非连续行距的测试构造，CU/bridge/容差/ABBA保持；旧失败与隔离诊断另存。writer仅准备一次，不计时；这是组件正信号，非官方吞吐或模型准确率。保留组件正信号；需按实际服务post-RoPE布局验证启用。', '保留局部正信号；实际服务布局与启用另验。', '完整producer＋原reducer，Qstride2560；不计writer，不授模型资格。', '127原件逐SHA保留；DB/source/native/9031清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/comparison.json', 'experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/results.json', 'experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/independent-review.md', 'experiments/framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/archive-receipt.json']
BATCH_RESULTS['corex_native_gqa_s4_real_stride_positive']=('QKV切片布局（非服务post-RoPE布局）、行距2560的N32/S4/KV16384完整producer＋原reducer Graph ABBA：Event1.029622→0.801413ms（省22.1644%），wall省22.1438%。9组数值/FP64/完整partial逐位/Graph/尾槽NaN/空段/输入RNG及前后extra512守卫全部通过。v2仅修原zero_忽略非连续行距的测试构造，CU/bridge/容差/ABBA保持；旧失败与隔离诊断另存。writer仅准备一次，不计时；这是组件正信号，非官方吞吐或模型准确率。保留组件正信号；需按实际服务post-RoPE布局验证启用。', '保留局部正信号；实际服务布局与启用另验。', '完整producer＋原reducer，Qstride2560；不计writer，不授模型资格。', '129原件逐SHA保留；DB/source/native/9031清理通过。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/comparison.json', 'experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/results.json', 'experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/independent-review.md', 'experiments/framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/archive-receipt.json']

BATCH_RESULTS['native_gqa_4k_not_exercised']=('原官方4K暖5970.98、1024成功；native只有安装，无实际覆盖。', '不判断native收益或失败，不改基线；保留ABI定位。', '原参数/四轮；fresh FX证实服务post-RoPE Q行距2048。', '379原件由原压缩包、manifest及恢复索引保存。')
BATCH_RESULTS['native_gqa_s4_contiguous_positive']=('S4连续Q2048九门通过，完整组件Event省22.1242%、wall省22.0967%。', '保留实际服务布局组件资格；非整模或105成绩。', 'N32/S4/KV16384，完整producer＋原reducer Graph ABBA；writer不计时。', '133原件完整归档，DB/source/native清理通过。')
BATCH_RESULTS['native_gqa_abi_v2_4k_positive_observation']=('原官方4K暖6481.2267对A5971.44，观察+8.5371%；1024成功，S2/S4实际覆盖。', '保留整模正信号；KV差48，待16K/105后定基线。', '原四轮弃首；c75db/814、SOf720、native14f及原参数不变。', '386原件；KV548336对548288，不称严格单因子因果或稳定幅度。')
CODE['corex-native-gqa-page16'] += ['experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/summary.json', 'experiments/official/20261027T140221Z-native-gqa-4k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/manifest.json', 'experiments/bundles/20261027T140221Z-native-gqa-4k-four-rounds/raw.tar.gz.storage.json']
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/summary.json', 'experiments/framework/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw-evidence.json', 'experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/manifest.json', 'experiments/bundles/20261027T143828583459Z-corex-native-gqa-s4-contiguous-component/raw.tar.gz.storage.json']
CODE['corex-native-gqa-page16'] += ['experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/summary.json', 'experiments/official/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/manifest.json', 'experiments/bundles/20261027T145950Z-native-gqa-abi-v2-4k-four-rounds/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', '服务post-RoPE Q实际连续2048。S4连续布局九门通过，组件Event省22.1242%；ABI v2原官方4K弃首暖均6481.2267对A5971.44，观察+8.5371%，1024成功且S2/S4实际覆盖。KV548336对548288差48，不称严格因果或稳定幅度；待16K/105后定基线。旧a596只有安装未覆盖，不是内核负收益；QKV切片2560组件及夹具失败保留。', [])

BATCH_RESULTS['native_gqa_abi_v2_16k_positive_observation']=('原官方16K暖4826.4467对A4529.7867，观察+6.5491%；512成功，S2/S4实际覆盖。', '保留整模正信号；KV少144，不称严格因果或稳定幅度。', '原四轮弃首；c75db/814与SOf720、native14f，原参数不变。', '388原件；KV548288对548432，DB/source/native及清理通过。')
BATCH_RESULTS['native_gqa_abi_v2_accuracy_pass']=('原官方105题102/105（97.142857%），valid/pass，95%门通过；transport/cap/empty均0。', '保留完整受测源码成绩；启动capture不授105请求分支独立资格。', '原105题及temperature1.0/top_p0.95/max_tokens32768/batch8不变。', '379原件；request_coverage_proven=false，清理与身份通过。')
BATCH_RESULTS['native_q32_transfer_compile_sidecar_only']=('CPU实编32SME/64MMA、64KiB；原checker=false，静态sidecar仅接受CoreX同步顺序。', '保留编译可行性；无GPU、数值或性能资格。', '复用原LLVM/ASM，不重编；原NVVM屏障匹配失败保留。', '20原件；M16坐标映射和完整Attention均未验证。')
GROUPS['native-q32-transfer']=('CoreX Q32四页搬运编译探针', '原checker搜索NVVM屏障而实际CoreX使用bi.sl.barrier，passed=false原样保留；sidecar仅接受同步与共享生命周期静态顺序。无GPU执行、坐标映射、数值或性能资格。', [])
CODE['native-q32-transfer']=['experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/summary.json', 'experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/raw-evidence.json', 'experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/compile-backend-barrier-review.json', 'experiments/cpu-probes/20261027T160904Z-native-q32-transfer-fragments/review-compile-160904.py']
CODE['corex-native-gqa-page16'] += ['experiments/official/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/summary.json', 'experiments/official/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/manifest.json', 'experiments/bundles/20261027T152326Z-native-gqa-abi-v2-16k-four-rounds/raw.tar.gz.storage.json']
CODE['corex-native-gqa-page16'] += ['experiments/accuracy/20261027T161121Z-native-gqa-abi-v2-native14f-math500/summary.json', 'experiments/accuracy/20261027T161121Z-native-gqa-abi-v2-native14f-math500/raw-evidence.json', 'experiments/bundles/20261027T161121Z-native-gqa-abi-v2-native14f-math500/manifest.json', 'experiments/bundles/20261027T161121Z-native-gqa-abi-v2-native14f-math500/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'ABI v2原官方4K/16K各四轮暖均6481.2267/4826.4467，对各A观察+8.5371%/+6.5491%，1024/512请求成功且S2/S4实际覆盖；KV分别差+48/−144，不称严格因果或稳定幅度。原105题102/105、95%门通过，但启动capture不能证明105请求分支覆盖。旧未覆盖安装包和夹具失败均保留。', [])

BATCH_RESULTS['native_gqa_v_overlap_component_signal']=('宏1九门通过；完整组件对原Triton Event省22.3849%、wall省22.3205%。', '保留组件信号；无同轮宏0增量对照，不当官方收益。', 'N64/S2/KV4096，V等待后移；完整producer＋原reducer，writer仅准备。', '121原件；DB/source/native与清理通过。')
BATCH_RESULTS['native_q32_m16_mapping_diagnostic_pass']=('两次launch固定映射，换值QK16384/PV32768值对CPU FP64 cast FP32逐位通过。', '保留M16映射依据；非完整Attention或性能资格。', '第二组沿首组坐标，不重新拟合；Q/KV回读和输入/RNG守卫通过。', '70原件；无softmax/Graph/模型准确率资格。')
GROUPS['native-q32-transfer']=('CoreX Q32四页搬运与M16映射诊断', '160904原checker失败与CoreX sidecar静态接受分列；164809两次launch固定映射对独立FP64逐位通过。尚无softmax、Graph、完整Attention、性能或模型准确率资格。', [])
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', '同步ABI v2已由[框架PR92](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/92)合并至main b3b87d2a；接续基线4K/16K暖6481.2267/4826.4467、102/105，保留KV差异与105请求分支覆盖限制。宏1组件对原Triton省22.3849%，尚无同轮宏0增量或官方资格。', [])
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/summary.json', 'experiments/framework/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/raw-evidence.json', 'experiments/bundles/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/manifest.json', 'experiments/bundles/20261027T163852438077Z-corex-native-gqa-s2-v-overlap-component/raw.tar.gz.storage.json']
CODE['native-q32-transfer'] += ['experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/summary.json', 'experiments/framework/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw-evidence.json', 'experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/manifest.json', 'experiments/bundles/20261027T164809092948Z-native-q32-m16-mapping-diagnostic/raw.tar.gz.storage.json']

BATCH_RESULTS['native_q32_attention_trace_compile_only']=('完整Q32/T64原生Attention纯CPU实编机制通过，64KiB、VGPR122、SGPRspill89。', '保留编译可行性；无GPU数值或性能资格。', 'trace启用；32SME/64MMA/7barrier，依赖仍须源特定审阅。', '19原件；静态计数不作动态性能估算。')
BATCH_RESULTS['native_q32_attention_notrace_compile_only']=('CPU no-trace实编通过，七诊断参数无访问/FP32trace store为0；VGPR105、SGPRspill49。', '保留编译变体；仍有spill，无数值或性能资格。', '原机制与no-trace静态检查通过，64KiB/SGPR104保持。', '23原件；不凭资源减少宣称收益。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261027T171059Z-native-q32-attention/summary.json', 'experiments/cpu-probes/20261027T171059Z-native-q32-attention/raw-evidence.json', 'experiments/bundles/20261027T171059Z-native-q32-attention/manifest.json', 'experiments/bundles/20261027T171059Z-native-q32-attention/raw.tar.gz.storage.json']
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/summary.json', 'experiments/cpu-probes/20261027T172936Z-native-q32-attention-notrace/raw-evidence.json', 'experiments/bundles/20261027T172936Z-native-q32-attention-notrace/manifest.json', 'experiments/bundles/20261027T172936Z-native-q32-attention-notrace/raw.tar.gz.storage.json']

BATCH_RESULTS['native_gqa_profile_diagnostic_incomplete_parsed']=('原posthoc不完整；节点解析通过，4个N64样本/1988插桩区间；S2共17.9005ms为主要区间。', '保留热点诊断；不是未插桩时延或官方吞吐。', 'boundary26.7253ms/full29.2221ms；关闭compile cache无fresh FX，原失败保留。', '3109原件完整xz75.29MB；N32仅17replay，未采M2048。')
BATCH_RESULTS['native_q32_attention_entry_failed']=('首入口在EngineArgs config缺已有GQA SO路径而失败；checks/timings为空。', '保留入口失败；未执行候选，不判算法错误或性能负。', '后继仅补SO路径，不改受测数学/容差或失败原件。', '56原件；未编新extension，尚无数值/性能资格。')
GROUPS['native-gqa-production-hotspot']=('同步原生GQA实际热点诊断', '原profile posthoc因关闭compile cache缺fresh FX而不完整；现成节点解析通过。4个N64样本的1988插桩区间中，S2/42层17.9005ms、MM6.1148ms、W8A8 1.8053ms、reduce0.4305ms；不能当未插桩时延或官方吞吐。N32未达采样门，未采M2048。', [])
CODE['native-gqa-production-hotspot'] = ['experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/summary.json', 'experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/raw-evidence.json', 'experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/hotspot-and-posthoc-review.json', 'experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/graph-summaries.csv', 'experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/kernel-rankings.csv', 'experiments/profiles/20261027T171100Z-c75db-production-hotspot-4k/native-logical-bandwidth.json', 'experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/manifest.json.storage.json', 'experiments/bundles/20261027T171100Z-c75db-production-hotspot-4k/raw.tar.xz.storage.json']
CODE['native-q32-transfer'] += ['experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/summary.json', 'experiments/framework/20261027T173739735745Z-native-q32-synchronous-long-component/raw-evidence.json', 'experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/manifest.json', 'experiments/bundles/20261027T173739735745Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json']

BATCH_RESULTS['native_q32_attention_component_negative']=('完整Q32长组件数值/位型/FP64/Graph/side/尾NaN通过；Event慢21.5584%、wall慢20.2416%。', '停止实现及大测；无模型资格，不发优化PR。', 'v2仅补入口已有GQA SO路径；实际Q32/T64，完整两臂ABBA。', '80原件；stopped_negative，非数值错误。')
GROUPS['native-q32-transfer']=('CoreX原生Q32 Attention：编译、映射与组件', '编译/固定映射资格分阶段保留。173739首入口漏SO路径，未执行候选；174338薄修入口后完整Q32/T64长组件全部数值门通过，但Event慢21.5584%、wall慢20.2416%，停止实现，不授模型或官方资格。', [])
CODE['native-q32-transfer'] += ['experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/summary.json', 'experiments/framework/20261027T174338066784Z-native-q32-synchronous-long-component/raw-evidence.json', 'experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/manifest.json', 'experiments/bundles/20261027T174338066784Z-native-q32-synchronous-long-component/raw.tar.gz.storage.json']

# 六轮已结束原生GQA/Q32探索；组件与官方分列。
GROUPS['native-gqa-mixed-s4']=('原生BF16 GQA：mixed S4覆盖扩展', '原c75db仅覆盖B64/S2与B32/S4，真实mixed prefix61原回落Triton。step125 B61完整mixed组件Event省8.8533%；仅helper/CPP扩原已选S4的32–63且排40、CU/chooser/S2不动。新生产Runtime B60完整eager省25.5143%、B63上界位型通过；均为真实CPU几何/合成QKV，非模型或官方幅度。182749新SO仅离线构建身份，后继官方由主线独立记录，不提前更新基线。', [])
CODE['native-gqa-mixed-s4']=[]
GROUPS['native-q32-transfer']=('CoreX原生Q32 Attention：编译、映射与组件', '固定映射、CPU编译与完整设备资格分列。旧shared-P完整Q32数值通过但Event慢21.56%；direct-P独立删除P共享发布及两barrier，CPU实编通过，完整设备数值全过但Event慢0.0984%近持平/wall省1.0096%，未见GPU吞吐收益。停止该方向追加优化/官方，不把性能负当数学错误。', [])
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'PR92已合并main b3b87d2；当前有效4K/16K暖6481.2267/4826.4467、102/105，保留KV差异与105分支覆盖限制。同轮macro0/1 N64/S2完整producer+原reducer Event省1.0521%、wall省1.1805%，新增位型/Graph全过，保留小正候选但未接生产/官方；旧macro1对Triton22.38%不是此增量。', [])
BATCH_RESULTS['q32_direct_p_compile_only']=('完整M16概率直接寄存器pack，删除P共享发布／读取与两个barrier。', '保留编译／身份依据；不授数值或性能。', '完整M16概率直接寄存器pack，删除P共享发布／读取与两个barrier。175958仅CPU实编及独审通过；32SME／64MMA／5barrier、64KiB、SGPR104／VGPR106／SGPRspill45。符号256坐标等价，尚无设备数值或性能资格；后继设备结果单列。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/summary.json', 'experiments/cpu-probes/20261027T175958Z-native-q32-direct-p/raw-evidence.json', 'experiments/bundles/20261027T175958Z-native-q32-direct-p/manifest.json', 'experiments/bundles/20261027T175958Z-native-q32-direct-p/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_macro01_strict_positive']=('同轮严格macro0／macro1完整producer＋原reducer，固定N64/S2/KV4096/Qstride2048。', '保留候选；等待独立模型／官方验证。', '同轮严格macro0／macro1完整producer＋原reducer，固定N64/S2/KV4096/Qstride2048。全部新增位型、换值Graph／恢复、输入RNG门通过；Event .4138905704→.4095360637ms省1.0521%，wall省1.1805%。保留小正候选，非官方稳定收益；不扩大S4或接生产，不把旧对Triton比例相减。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T180400292465Z-native-gqa-macro01-hotspot-component/summary.json', 'experiments/framework/20261027T180400292465Z-native-gqa-macro01-hotspot-component/raw-evidence.json', 'experiments/bundles/20261027T180400292465Z-native-gqa-macro01-hotspot-component/manifest.json', 'experiments/bundles/20261027T180400292465Z-native-gqa-macro01-hotspot-component/raw.tar.gz.storage.json']
BATCH_RESULTS['q32_direct_p_no_gpu_gain']=('direct-P完整Q32长组件全部硬数值／位型／FP64／Graph／side／尾NaN门通过。', '停止追加优化／官方；不是数学错误。', 'direct-P完整Q32长组件全部硬数值／位型／FP64／Graph／side／尾NaN门通过。Event6.56635642→6.57281923ms慢0.0984%近持平，wall省1.0096%；未见GPU吞吐收益，停止该方向追加优化／官方，不扩形状。旧shared-P慢21.56%原结果保留，不能称数学错误。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['native-q32-transfer'] += ['experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/summary.json', 'experiments/framework/20261027T180735168348Z-native-q32-direct-p-long-component/raw-evidence.json', 'experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/manifest.json', 'experiments/bundles/20261027T180735168348Z-native-q32-direct-p-long-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_mixed61_component_positive']=('回放真实step125的61decode＋1987prefill CPU几何，随机QKV；私有B61桥直接链接同f720 S4导出，CU不重编。', '保留候选；等待独立模型／官方验证。', '回放真实step125的61decode＋1987prefill CPU几何，随机QKV；私有B61桥直接链接同f720 S4导出，CU不重编。全2048输出逐位、原九门／Graph、parent／输入RNG／guard通过；完整mixed eager Event1.289934576→1.175732970ms省8.8533%，wall省5.6627%。保留生产扩覆盖候选，非模型／官方幅度；完整105份原件tar流无损xz。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['native-gqa-mixed-s4'] += ['experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/summary.json', 'experiments/framework/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw-evidence.json', 'experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/manifest.json', 'experiments/bundles/20261027T181731151743Z-corex-native-gqa-mixed61-component/raw.tar.xz.storage.json']
BATCH_RESULTS['native_gqa_mixed_s4_offline_build']=('f6b4候选仅Python／CPP两文件扩原已选S4的32≤B≤63并排40，原CU a8b1／S2／chooser／macro0不变。', '保留编译／身份依据；不授数值或性能。', 'f6b4候选仅Python／CPP两文件扩原已选S4的32≤B≤63并排40，原CU a8b1／S2／chooser／macro0不变。182749离线构建新SO b9bff11d及完整receipt通过；此步确重编同源CU，服务／后继组件不做运行时编译。仅身份／构建资格，没有数值或性能；后继Runtime组件单列。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['native-gqa-mixed-s4'] += ['experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/summary.json', 'experiments/cpu-probes/20261027T182749Z-native-gqa-mixed-s4-production-build/raw-evidence.json', 'experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/manifest.json', 'experiments/bundles/20261027T182749Z-native-gqa-mixed-s4-production-build/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_mixed60_runtime_positive']=('只加载新b9bff11d SO：A旧Runtime guard自然回Triton，B实际新生产_Runtime；真实step123 B60＋1988／step129 B63＋1985。', '保留候选；等待独立模型／官方验证。', '只加载新b9bff11d SO：A旧Runtime guard自然回Triton，B实际新生产_Runtime；真实step123 B60＋1988／step129 B63＋1985。B63唯一上界位型、B60初始／换值完整输出、parent／输入RNG／guard全过；完整B60 eager Event1.66750455→1.24205244ms省25.5143%，wall省14.0096%。原CU九门复用，不冒称新mixed Graph／模型准确率或官方收益；4K另由主线验证。', '完整原件与manifest无损保存；不复跑未变检查，不叠加不同形状或组合收益。')
CODE['native-gqa-mixed-s4'] += ['experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/summary.json', 'experiments/framework/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw-evidence.json', 'experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/manifest.json', 'experiments/bundles/20261027T183250970628Z-corex-native-gqa-mixed60-runtime-component/raw.tar.gz.storage.json']

BATCH_RESULTS['native_gqa_mixed_s4_official_partial_negative']=('原官方4K两轮512成功；首暖6168.07对6301.93观察−2.1241%，按预设主动停止。', '候选不合并；停止16K/105，不更新基线。', 'f6b4仅helper/CPP扩原S4范围，新SO b9bff11d，首冷新增eager覆盖门通过。', 'KV548432对548336不同，不严格归因；原partial/KeyboardInterrupt15及DB/源/两库清理保留，非数值或模型故障。')
GROUPS['native-gqa-mixed-s4']=('原生BF16 GQA：mixed S4覆盖扩展', '原c75db仅覆盖B64/S2与B32/S4，真实mixed prefix61原回落Triton。B61/B60完整mixed组件Event省8.8533%/25.5143%、B63位型通过；仅helper/CPP扩32–63且排40，CU/chooser/S2不动。原官方4K两轮首暖6168.07对A6301.93观察−2.1241%后主动停，KV548432对548336不同，不能严格归因。候选不合并，停止16K/105，不定新基线；正确性门通过与性能筛选负分列。', [])
CODE['native-gqa-mixed-s4'] += ['experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/summary.json', 'experiments/official/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/manifest.json', 'experiments/bundles/20261027T183747Z-native-gqa-mixed-s4-4k-four-rounds/raw.tar.gz.storage.json']


# 后续独立两轮：小收益保留，负组件停止；不更新官方基线。
BATCH_RESULTS['qkv_bn32_w8_negative']=('M64真实layer0 QKV权重／合成激活，原64/64/128 w16s1对64/32/128 w8s1，仅BN与warp两项变化，原FPbody／runtime K不变、无额外权重。八项位型／独立FP64／换值Graph／side与RNG通过；完整MM Graph Event .03167163394→.03444711491ms慢8.7633%，停止形状／模型／官方，非数值错误。SME／shared静态减少不代表收益。', '停止该负组件，不进模型／官方。', '关闭profiler的同轮完整Graph ABBA；原数学／输入RNG门通过。', '原件逐SHA验证并完整无损分块；不叠加S2/S4或其它方法比例。')
CODE['shape-gemm'] += ['experiments/framework/20261027T190017939358Z-qkv-bn32-component/summary.json', 'experiments/framework/20261027T190017939358Z-qkv-bn32-component/raw-evidence.json', 'experiments/bundles/20261027T190017939358Z-qkv-bn32-component/manifest.json', 'experiments/bundles/20261027T190017939358Z-qkv-bn32-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_s4_macro01_strict_positive']=('N32/S4/KV16384／连续Qstride2048，同轮原f720 macro0对私有同源macro1，完整producer＋原reducer Graph ABBA。原九门／全partial位型／FP64／换值Graph／input／RNG通过；Event .8022495508→.7950562537ms省.8966408%，wall省1.0151%。保留小正候选，不冒称官方／模型资格，不与S2收益相加；mixed扩覆盖官方负路线不叠加。', '保留小正候选；原官方／准确率尚未授予。', '关闭profiler的同轮完整Graph ABBA；原数学／输入RNG门通过。', '原件逐SHA验证并完整无损分块；不叠加S2/S4或其它方法比例。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261027T190534106960Z-native-gqa-s4-macro01-hotspot-component/summary.json', 'experiments/framework/20261027T190534106960Z-native-gqa-s4-macro01-hotspot-component/raw-evidence.json', 'experiments/bundles/20261027T190534106960Z-native-gqa-s4-macro01-hotspot-component/manifest.json', 'experiments/bundles/20261027T190534106960Z-native-gqa-s4-macro01-hotspot-component/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'PR92有效4K/16K暖6481.2267/4826.4467、102/105，KV与请求覆盖限制保留。同轮macro0/1完整producer+原reducer：N64/S2省1.0521%，N32/S4省0.89664%，数值/位型/Graph门全过；仅小正组件，不相加、不继承官方。候选生产/官方由主线独立验证，不包含mixed扩范围负路线。', [])

BATCH_RESULTS['native_gqa_overlap1_offline_build']=('原c75db的S2／S4默认启用V等待重叠，源码58a2fc96／treef1658b69；仅CU默认宏、离线builder与helper回执三项，不含mixed扩覆盖、runner／采样不变。191340 CPU离线构建SO c8a725da与源码／命令／receipt身份通过；无GPU数值或官方资格，不继承组件比例或准确率，主线后续原官方另记。', '保留离线构建身份；官方尚未授予。', 'S2/S4默认macro1，未叠加mixed负范围；数值源未变。', 'CPU-only；完整20原件及源码/SO/命令回执逐SHA保存。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261027T191340Z-native-gqa-overlap1-production-build/summary.json', 'experiments/cpu-probes/20261027T191340Z-native-gqa-overlap1-production-build/raw-evidence.json', 'experiments/bundles/20261027T191340Z-native-gqa-overlap1-production-build/manifest.json', 'experiments/bundles/20261027T191340Z-native-gqa-overlap1-production-build/raw.tar.gz.storage.json']


# 宏1官方4K与独立Q32双槽：资格按每轮范围保存。
BATCH_RESULTS['native_q32_double_slot_compile_only']=('Q32 KV双槽64KiB原FPbody不变；191803仅CPU实编及独审通过，真实CFG存在下一页copy→当前QK／softmax／PV窗口，尾页／末页／空段同步已核。64SME／64MMA／5barrier、SGPR93／VGPR105、双spill0；没有设备数值／吞吐或实际并行隐藏资格，后继完整组件另记。', '仅CPU构建／机制；设备资格另记。', '已有原命令／参数／原数学及对应正确性门保持；原始阶段结果分列。', '完整原件与manifest逐SHA核验，不为发布重复上卡。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/summary.json', 'experiments/cpu-probes/20261027T191803Z-native-q32-kv-double-slot/raw-evidence.json', 'experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/manifest.json', 'experiments/bundles/20261027T191803Z-native-q32-kv-double-slot/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_macro1_official_4k_positive']=('仅原c75db S2／S4默认macro1，不含mixed扩范围。原官方4K四轮5481.01／6441.35／6721.46／6720.64，弃首均6627.816667对A6481.226667观察+2.2617632%；同KV548336，1024成功，真实原生覆盖／源码／两库／DB恢复／清理通过。4K完整正观察保留；16K／105尚未完成，不继承准确率，不称稳定幅度或新基线。', '保留正观察；不继承模型／准确率或新基线。', '已有原命令／参数／原数学及对应正确性门保持；原始阶段结果分列。', '完整原件与manifest逐SHA核验，不为发布重复上卡。')
CODE['corex-native-gqa-page16'] += ['experiments/official/20261027T192157Z-native-gqa-overlap-4k-four-rounds/summary.json', 'experiments/official/20261027T192157Z-native-gqa-overlap-4k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T192157Z-native-gqa-overlap-4k-four-rounds/manifest.json', 'experiments/bundles/20261027T192157Z-native-gqa-overlap-4k-four-rounds/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q32_double_slot_component_positive']=('Q32双KV槽保持64KiB与原数学，只将下一页copy放当前QK／softmax／PV之间。初始／恢复／换值／side全输出位型、原独立FP64／尾NaN／输入／RNG及Graph门全部通过；完整Q32长组件Event6.571181774→6.406544447ms省2.5054447%，wall省3.34544%。保留局部正候选，非模型／官方或新准确率；不与direct-P及GQA宏1收益相加，不继承生产资格。', '保留正观察；不继承模型／准确率或新基线。', '已有原命令／参数／原数学及对应正确性门保持；原始阶段结果分列。', '完整原件与manifest逐SHA核验，不为发布重复上卡。')
CODE['native-q32-transfer'] += ['experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/summary.json', 'experiments/framework/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw-evidence.json', 'experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/manifest.json', 'experiments/bundles/20261027T194147574489Z-native-q32-kv-double-slot-long-component/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'PR92仍为有效基线，4K/16K暖6481.2267/4826.4467、102/105。仅原S2/S4默认macro1，不叠mixed负范围：同KV548336原官方4K四轮暖6627.8167对6481.2267观察+2.26176%，1024成功／实际覆盖／源／两库／DB清理通过；16K/105另由主线验证，尚无新基线或稳定幅度。此前S2/S4同轮组件省1.0521%/.89664%，比例不相加。', [])
GROUPS['native-q32-transfer']=('CoreX原生Q32 Attention：编译、映射与组件', '旧shared-P组件数值正确但慢21.56%；direct-P近持平停止。独立双KV槽保持64KiB与原FPbody，191803实编存在预取/当前计算窗口且双spill0（非实际重叠证明）；194147完整长组件全部位型/FP64/Graph/尾NaN等门过，Event省2.50544%、wall省3.34544%。保留局部正候选，未接模型/官方，不与其它组件幅度相加。', [])


BATCH_RESULTS['native_gqa_macro1_official_16k_positive']=('仅原S2/S4默认macro1。原官方16K四轮4269.60／4834.45／4832.36／4831.17，弃首均4832.66对A4826.446667观察+0.128735%；同KV548288、同起始DB207f，512成功，实际原生覆盖／源／两库／DB恢复／清理通过。保留单组小正观察，105另验；不称稳定幅度或新基线。', '保留单组小正观察；105另验。', '原官方参数、同KV/DB、macro1实际覆盖与清理通过。', '366原件逐SHA保存；不为上传重测。')
CODE['corex-native-gqa-page16'] += ['experiments/official/20261027T194324Z-native-gqa-overlap-16k-four-rounds/summary.json', 'experiments/official/20261027T194324Z-native-gqa-overlap-16k-four-rounds/raw-evidence.json', 'experiments/bundles/20261027T194324Z-native-gqa-overlap-16k-four-rounds/manifest.json', 'experiments/bundles/20261027T194324Z-native-gqa-overlap-16k-four-rounds/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'PR92仍为有效基线。仅原S2/S4默认macro1：原官方4K／16K均四轮，弃首均6627.8167／4832.66，对各自A观察+2.26176%／+0.128735%，同各自KV与DB，1024／512成功；105另验，尚不更新基线。mixed扩范围负候选已停，未混入。', [])


# 宏1完整准确率与Q32新ABI性能负结果，资格分开保存。
BATCH_RESULTS['native_q32_gpu_metadata_compile_only']=('Q32 GPU metadata ABI仅CPU实编：65536B shared、96SGPR/105VGPR、private/spill0；实际LLVM/ASM及独立CFG/数学指令审阅通过。仅入口读取原GPU metadata与边界，原双槽数学不变；未由编译结果授予数值或性能资格。', '仅CPU资格。', '原参数和受测源码独立绑定，局部与模型资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/summary.json', 'experiments/cpu-probes/20261028T091802Z-native-q32-metadata-abi/raw-evidence.json', 'experiments/bundles/20261028T091802Z-native-q32-metadata-abi/manifest.json', 'experiments/bundles/20261028T091802Z-native-q32-metadata-abi/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q32_gpu_metadata_event_negative']=('原实际Manager接线pure2048的14项位型/存储/metadata/换值Graph/side硬门通过；完整Event0.543209106→0.593731284ms慢9.30068695%，wall省8.92290468%。按冻结Event筛选停止，mixed1987未运行，不将wall收益替代GPU收益。原FP64诊断两臂均false且误差完全相同，不能写FP64全过；无生产/模型资格。', 'Event负候选停止；mixed未测。', '原参数和受测源码独立绑定，局部与模型资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/summary.json', 'experiments/framework/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw-evidence.json', 'experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/manifest.json', 'experiments/bundles/20261028T094028832761Z-native-q32-kv-double-slot-metadata-metadata-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_macro1_accuracy_103of105']=('同一macro1源码与实际SO的原105题完成103/105=98.095238%，原95%门通过，0请求错误/截断/空答案。题目/采样脚本逐字同原基线，源/两SO/DB/清理通过，GQA两shape启动capture有效；通用stack缺compute_order_selected的pending与旧105相同，不称全stack或逐题原生覆盖通过。4K/16K已有各自四轮结果，不为发布重测；新基线待代码PR。', '原准确率通过，待代码PR。', '原参数和受测源码独立绑定，局部与模型资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['corex-native-gqa-page16'] += ['experiments/accuracy/20261028T091957Z-native-gqa-overlap-native14f-math500/summary.json', 'experiments/accuracy/20261028T091957Z-native-gqa-overlap-native14f-math500/raw-evidence.json', 'experiments/bundles/20261028T091957Z-native-gqa-overlap-native14f-math500/manifest.json', 'experiments/bundles/20261028T091957Z-native-gqa-overlap-native14f-math500/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', 'PR92仍为已合并基线。原S2/S4默认macro1的4K/16K各四轮弃首均6627.8167/4832.66，同各自KV/DB，对A单组观察+2.26176%/+0.128735%；原105为103/105、零错误/截断/空，原95%门过。生产与实际SO一致，待代码PR；通用stack缺compute_order marker与旧105相同，不称逐题原生覆盖。mixed扩范围负候选未混入。', [])
GROUPS['native-q32-transfer']=('CoreX原生Q32 Attention：编译、映射与组件', '原长组件双KV槽Event省2.50544%只属Q2047/KV16384组件。新GPU metadata ABI实编通过，但actual Manager pure2048完整Event慢9.30069%，wall省8.92290%；14硬门过，FP64原诊断两臂均false且误差一致。按冻结Event负筛选停止，mixed1987未测，无生产资格，不外推长组件小收益。', [])

GROUPS['corex-native-gqa-page16']=('CoreX原生BF16 GQA：单页与完整分页', '当前有效基线为框架PR105（https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/105），merge 1cbac531ca9afaa0e9a68624d5d10cb1d0412055。原S2/S4默认macro1：4K/16K四轮弃首均6627.816667/4832.66，同各自KV/DB，对PR92单组观察+2.261763%/+0.128735%；原105为103/105、零错误/截断/空，95%门通过。GQA启动capture非逐题覆盖，通用stack缺compute_order marker与旧105相同，原pending保留。不含mixed扩范围负候选，幅度不相加或称统计稳定。', [])


# Q64完整组件负与原生GQA双槽机制门否决，分别保留资格。
BATCH_RESULTS['native_q64_cohort_compile_only']=('Q64把两个原Q32 cohort放同一2048-thread CTA共享KV加载；CPU实际编译64KiB shared、83SGPR/107VGPR、private/spill0。实际逐cohort数学依赖、Q寄存器生命周期与统一barrier独审通过，只允许后续组件门，编译本身不授数值或性能资格。', '仅CPU编译资格，结果见后继组件。', '原数学、原形状与受测源码范围保持；组件与官方资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/summary.json', 'experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/review.json', 'experiments/cpu-probes/20261028T100025Z-native-q64-cohort-compile/raw-evidence.json', 'experiments/bundles/20261028T100025Z-native-q64-cohort-compile/manifest.json', 'experiments/bundles/20261028T100025Z-native-q64-cohort-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_cohort_event_negative']=('原Q32／旧双槽Q32／Q64同轮ABCCBA长组件Event为6.561143398／6.401421785／6.880203247ms；Q64对原慢4.862870%、对双槽慢7.479299%，停止。长输入位型/原FP64/换值Graph/side/输入与Q33八门通过，非数值失败；旧双槽同轮省2.434356%仍仅局部观察。未进模型/官方，不外推吞吐或准确率。', 'Q64组件性能负，停止；数值门通过。', '原数学、原形状与受测源码范围保持；组件与官方资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/summary.json', 'experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/review.json', 'experiments/framework/20261028T101658850160Z-native-q64-cohort-long-component/raw-evidence.json', 'experiments/bundles/20261028T101658850160Z-native-q64-cohort-long-component/manifest.json', 'experiments/bundles/20261028T101658850160Z-native-q64-cohort-long-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_double_slot_early_drain_stop']=('PR105原生GQA下一页K/V双slot只做CPU编译。S2/S4均16KiB shared、59SGPR/82VGPR、private/spill0；实际next SME后有QK/softmax部分窗口，但PV前g2scnt0排空，未达冻结完整QK/PV窗口门。按预设停止，不进入GPU、不改barrier救候选；不是数学错误或实测性能负结果。', '机制门否决，停止；没有GPU成绩。', '原数学、原形状与受测源码范围保持；组件与官方资格分开。', '原件与manifest无损保存，未为发布重跑。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T102147Z-native-gqa-double-slot-compile/summary.json', 'experiments/cpu-probes/20261028T102147Z-native-gqa-double-slot-compile/review.json', 'experiments/cpu-probes/20261028T102147Z-native-gqa-double-slot-compile/raw-evidence.json', 'experiments/bundles/20261028T102147Z-native-gqa-double-slot-compile/manifest.json', 'experiments/bundles/20261028T102147Z-native-gqa-double-slot-compile/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0],GROUPS['corex-native-gqa-page16'][1]+' 后继16KiB双槽的实际CPU ASM在PV前排空next SME，未达冻结完整QK/PV窗口门，停止、不进入GPU；仍有QK/softmax部分重叠，不写成数值或性能失败。',GROUPS['corex-native-gqa-page16'][2])
GROUPS['native-q32-transfer']=('CoreX原生Prefill Attention：Q32／Q64', 'Q32双KV槽原长组件Event省2.50544%只属Q2047/KV16384局部证据；后继三臂同轮旧双槽仍省2.434356%。Q64共享KV的两个Q32 cohort虽通过原数值/Graph/side与Q33边界门，但完整Event6.880203ms，对原Q32慢4.862870%、对旧双槽慢7.479299%，停止，不进模型/官方。此前GPU metadata ABI的pure2048 Event慢9.30069%，mixed未测，原FP64诊断两臂false仍保留；不同组件与负载结果不互相替代。', [])


# 长上下文组件、真实metadata与启动前失败分开登记。
BATCH_RESULTS['native_q64_direct_and_compile']=('Q64仅删V掩码分支，完整页默认全1掩码；实际32个masked/raw vector select归零，PV少64AND及64anyop3，数学/同步链保留。CPU64KiB、83SGPR/107VGPR、0spill；仅编译资格，组件见104855。', '仅CPU编译资格；后继组件单列。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261028T103515Z-native-q64-vmask-direct-and-compile/component-source-review.json', 'experiments/cpu-probes/20261028T103515Z-native-q64-vmask-direct-and-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T103515Z-native-q64-vmask-direct-and-compile/review.json', 'experiments/cpu-probes/20261028T103515Z-native-q64-vmask-direct-and-compile/summary.json', 'experiments/bundles/20261028T103515Z-native-q64-vmask-direct-and-compile/manifest.json', 'experiments/bundles/20261028T103515Z-native-q64-vmask-direct-and-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q32_long_metadata_positive']=('Q32双KV槽接真实GPU metadata，在原Builder/Policy/Manager完整forward测Q2047/KV16384；Event6.559120178→6.387941837ms省2.609776%，wall省5.389362%；20硬门与两组原FP64通过。保留长组件正信号；不取消短2048负结果、不授生产或官方资格。', '保留组件正信号，不更新正式基线。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T104549355108Z-native-q32-kv-double-slot-long-metadata-metadata-component/raw-evidence.json', 'experiments/framework/20261028T104549355108Z-native-q32-kv-double-slot-long-metadata-metadata-component/review.json', 'experiments/framework/20261028T104549355108Z-native-q32-kv-double-slot-long-metadata-metadata-component/summary.json', 'experiments/bundles/20261028T104549355108Z-native-q32-kv-double-slot-long-metadata-metadata-component/manifest.json', 'experiments/bundles/20261028T104549355108Z-native-q32-kv-double-slot-long-metadata-metadata-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_direct_and_positive']=('Q64 direct AND复用原三臂ABCCBA长组件：原Q32／双槽Q32／Q64 Event6.560417652／6.402368069／6.247346401ms；Q64省4.772124%／2.421318%。原长门及Q33八门通过，保留标量ABI局部正信号，不授真实metadata或模型资格；旧f999负结果保留。', '保留组件正信号，不更新正式基线。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T104855700928Z-native-q64-vmask-direct-and-long-component/raw-evidence.json', 'experiments/framework/20261028T104855700928Z-native-q64-vmask-direct-and-long-component/review.json', 'experiments/framework/20261028T104855700928Z-native-q64-vmask-direct-and-long-component/summary.json', 'experiments/bundles/20261028T104855700928Z-native-q64-vmask-direct-and-long-component/manifest.json', 'experiments/bundles/20261028T104855700928Z-native-q64-vmask-direct-and-long-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_metadata_compile']=('Q64 direct AND增加真实GPU seq/cu入口与当前view偏移；实际424条FP依赖、barrier和next32SME顺序保持，无提前drain；64KiB、84SGPR/107VGPR、0spill。编译机制与增量源审通过，仅CPU资格，数值/性能见111346。', '仅CPU编译资格；后继组件单列。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/review.json', 'experiments/cpu-probes/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/root-source-review.json', 'experiments/cpu-probes/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/summary.json', 'experiments/bundles/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/manifest.json', 'experiments/bundles/20261028T105914Z-native-q64-vmask-direct-and-metadata-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_long_metadata_positive_drift']=('Q64真实长metadata完整forward的20门及两组原FP64通过。ABBA Event A1=6.568206310、A2=6.972782135，B=6.295509338／6.295493126ms；均值省7.015632%，但A2明显漂移，不称稳定7%。两B均快于较快A，保留正信号，无模型/官方资格。', '保留组件正信号，不更新正式基线。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T111346761013Z-native-q64-vmask-direct-and-long-metadata-metadata-component/raw-evidence.json', 'experiments/framework/20261028T111346761013Z-native-q64-vmask-direct-and-long-metadata-metadata-component/review.json', 'experiments/framework/20261028T111346761013Z-native-q64-vmask-direct-and-long-metadata-metadata-component/summary.json', 'experiments/bundles/20261028T111346761013Z-native-q64-vmask-direct-and-long-metadata-metadata-component/manifest.json', 'experiments/bundles/20261028T111346761013Z-native-q64-vmask-direct-and-long-metadata-metadata-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q32_context_prelaunch_manifest_mismatch']=('16K上下文诊断owner在服务/GPU启动前因source-manifest整文件SHA配对失败停止。保留13份原件；源文件条目未改、扩展manifest格式多git_sha导致绑定不匹配，后继仅修固定哈希。此轮无GPU、无官方成绩，不是模型或数值失败。', '启动前失败，无GPU成绩；后继修正绑定。', '原件范围内的组件/编译资格；不替代模型、生产路由与官方验证。', '复用已有原件SHA和终态审阅，不为发布重测；A2漂移及历史负结果保留。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/q32-context-coverage-16k-ef8f5d62/raw-evidence.json', 'experiments/cpu-probes/q32-context-coverage-16k-ef8f5d62/review.json', 'experiments/cpu-probes/q32-context-coverage-16k-ef8f5d62/summary.json', 'experiments/bundles/q32-context-coverage-16k-ef8f5d62/manifest.json', 'experiments/bundles/q32-context-coverage-16k-ef8f5d62/raw.tar.gz.storage.json']
GROUPS['native-q32-transfer']=('CoreX原生Prefill Attention：Q32／Q64', 'Q32双槽真实长metadata组件Event省2.609776%；Q64 direct AND标量组件对原Q32省4.772124%、对双槽省2.421318%。Q64真实长metadata两B均快于较快A，均值省7.015632%但A2漂移，不称稳定7%。三项只属长组件正信号，不代替生产、模型或完整官方资格；后续125913首暖结果另列，PR105基线不变。旧Q64 f999长组件慢4.862870%与短2048 metadata慢9.30069%的负结果仍保留，后者原FP64诊断两臂false且误差相同、mixed未测。', [])


# GQA两页路线负结果、覆盖导出失败与Q64 mixed局部信号。
BATCH_RESULTS['context_coverage_export_failed']=('PR105原单轮16K诊断128请求全部成功，但SIGUSR1后缺worker输出，owner判覆盖导出失败；RAM观察不可恢复，未确定signal回调的具体原因。源/两SO/DB恢复、清理通过，不重跑整轮，不称覆盖已证实或官方四轮成绩。', '覆盖导出失败，不重跑整轮。', '按已测负载与源码范围；模型/官方/生产资格不由组件或编译替代。', '原gzip完整保存，复用终态和member SHA校验，不为上传重测。')
CODE['native-q32-transfer'] += ['experiments/diagnostics/20261028T111552Z-pr105-context-coverage-16k-diagnostic/raw-evidence.json', 'experiments/diagnostics/20261028T111552Z-pr105-context-coverage-16k-diagnostic/review.json', 'experiments/diagnostics/20261028T111552Z-pr105-context-coverage-16k-diagnostic/summary.json', 'experiments/bundles/20261028T111552Z-pr105-context-coverage-16k-diagnostic/manifest.json', 'experiments/bundles/20261028T111552Z-pr105-context-coverage-16k-diagnostic/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_double_slot_component_negative']=('GQA下一页双槽以部分next-K重叠的新假设做唯一N64/S2完整producer+原reducer ABBA32；九门、partial位型/FP64/NaN/Graph/side通过。Event .409521461→.426378354ms慢4.116242%，性能负停止，不扩S4或官方；102147完整QK/PV窗口NO-GO历史仍保留。', '数值门通过、性能负，停止。', '按已测负载与源码范围；模型/官方/生产资格不由组件或编译替代。', '原gzip完整保存，复用终态和member SHA校验，不为上传重测。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/raw-evidence.json', 'experiments/framework/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/review.json', 'experiments/framework/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/source-review.json', 'experiments/framework/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/summary.json', 'experiments/bundles/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/manifest.json', 'experiments/bundles/20261028T114531355264Z-native-gqa-double-slot-hotspot-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t32_compile_only']=('GQA逻辑T32合并两独立物理页一次softmax；真实热循环16QK两独立链、16PV、每acc分量只缩放一次，8K+8V等待安全；16KiB/80SGPR/80VGPR/0spill。共同max和BF16 P属新数学顺序，编译只允许一次原FP64合同完整组件，不授数值/性能/生产资格。', 'CPU机制通过；完整组件结果另列。', '按已测负载与源码范围；模型/官方/生产资格不由组件或编译替代。', '原gzip完整保存，复用终态和member SHA校验，不为上传重测。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T115612Z-native-gqa-t32-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T115612Z-native-gqa-t32-compile/review.json', 'experiments/cpu-probes/20261028T115612Z-native-gqa-t32-compile/source-review.json', 'experiments/cpu-probes/20261028T115612Z-native-gqa-t32-compile/summary.json', 'experiments/bundles/20261028T115612Z-native-gqa-t32-compile/manifest.json', 'experiments/bundles/20261028T115612Z-native-gqa-t32-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t32_component_negative']=('GQA T32两页合并在唯一N64/S2完整producer+原reducer ABBA32测完；原九数值门/FP64/非有限/同臂Graph/输入RNG与尾/side通过，跨臂位型仅诊断。Event .409620851→.424990505ms慢3.752166%，wall慢3.601438%；性能负停止，不扩S4或官方，不撤销本组件已通过的数值事实。', '数值门通过、性能负，停止。', '按已测负载与源码范围；模型/官方/生产资格不由组件或编译替代。', '原gzip完整保存，复用终态和member SHA校验，不为上传重测。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261028T120451425507Z-native-gqa-t32-hotspot-component/raw-evidence.json', 'experiments/framework/20261028T120451425507Z-native-gqa-t32-hotspot-component/review.json', 'experiments/framework/20261028T120451425507Z-native-gqa-t32-hotspot-component/summary.json', 'experiments/bundles/20261028T120451425507Z-native-gqa-t32-hotspot-component/manifest.json', 'experiments/bundles/20261028T120451425507Z-native-gqa-t32-hotspot-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_mixed_event_positive_wall_negative']=('Q64在61 decode+1987 prefill、context7948=4×1987边界做完整mixed forward，20门/两组FP64/全输出位型通过。Event4.430978775→4.325495720ms省2.380581%，wall4.764854469→4.782359062ms慢0.367369%；保留GPU组件正信号并保留wall回退。两臂为旧c75/f720冻结组件，非PR105官方，不授生产/模型/全范围资格。', '保留Event正信号；wall回退，无整体资格。', '按已测负载与源码范围；模型/官方/生产资格不由组件或编译替代。', '原gzip完整保存，复用终态和member SHA校验，不为上传重测。')
CODE['native-q32-transfer'] += ['experiments/framework/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/raw-evidence.json', 'experiments/framework/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/review.json', 'experiments/framework/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/source-review.json', 'experiments/framework/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/summary.json', 'experiments/bundles/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/manifest.json', 'experiments/bundles/20261028T120924623364Z-native-q64-long-context-mixed-metadata-component/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0], GROUPS['corex-native-gqa-page16'][1]+' 后续只按部分next-K新假设做114531完整组件，九门通过但Event慢4.116242%，停止；未改写102147完整窗口NO-GO。逻辑T32实际减少归约与缩放，115612编译后120451原数值九门通过，但Event慢3.752166%，停止，不扩S4或官方。', GROUPS['corex-native-gqa-page16'][2])
GROUPS['native-q32-transfer']=(GROUPS['native-q32-transfer'][0], GROUPS['native-q32-transfer'][1]+' 120924固定旧c75/f720 mixed61+1987、context7948边界的20门和FP64通过，Event省2.380581%，wall慢0.367369%；保留GPU局部信号，非PR105官方。111552原16K单轮128请求成功但覆盖导出失败，RAM数据不可恢复，不重跑整轮。', GROUPS['native-q32-transfer'][2])


# T32原位复用8KiB：保留单组小信号，旧16KiB负结果不改。
BATCH_RESULTS['native_gqa_t32_reuse_compile_only']=('T32保持两页数学，QK读完后barrier再用同8KiB写V；实际16QK/16PV与页序保持，shared16→8KiB、64SGPR/80VGPR、0spill。每pair多一道barrier，V仅重叠softmax；编译允许一次完整S2组件，不推断occupancy或收益。', '仅CPU编译资格，完整组件另列。', 'S2固定形状，原数值合同与新共享生命周期分别验证；无S4/模型/官方资格。', '110原件完整保存；额外保留启动前拒绝包，未执行不计GPU run。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T121814Z-native-gqa-t32-reuse-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T121814Z-native-gqa-t32-reuse-compile/review.json', 'experiments/cpu-probes/20261028T121814Z-native-gqa-t32-reuse-compile/source-review.json', 'experiments/cpu-probes/20261028T121814Z-native-gqa-t32-reuse-compile/summary.json', 'experiments/bundles/20261028T121814Z-native-gqa-t32-reuse-compile/manifest.json', 'experiments/bundles/20261028T121814Z-native-gqa-t32-reuse-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t32_reuse_small_positive']=('固定N64/S2/KV4096完整producer+原reducer ABBA32：九数值门/FP64/非有限/尾/同臂Graph/side/输入RNG通过。Event .409684807→.408775479ms省0.221958%，wall省0.287814%；保留单组小正信号，不称稳定或官方收益、不更PR105基线。旧16KiB负保留；dtype误改旧包dadfc328启动前拒绝从未执行，实际bfff519b。', '保留单组组件小正信号，不称稳定收益、不更新基线。', 'S2固定形状，原数值合同与新共享生命周期分别验证；无S4/模型/官方资格。', '110原件完整保存；额外保留启动前拒绝包，未执行不计GPU run。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/raw-evidence.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/review.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/source-review.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/summary.json', 'experiments/bundles/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/manifest.json', 'experiments/bundles/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/raw.tar.gz.storage.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/rejected-dadfc328/cpu-check.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/rejected-dadfc328/entry.tar.gz', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/rejected-dadfc328/freeze.json', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/rejected-dadfc328/prepare.py', 'experiments/framework/20261028T123106447870Z-native-gqa-t32-reuse-hotspot-component/rejected-dadfc328/失败说明.md']
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0],GROUPS['corex-native-gqa-page16'][1]+' 121814/123106 T32原位复用8KiB通过新生命周期与原九数值门；Event省0.221958%、wall省0.287814%，仅单组组件小信号，未更PR105基线。旧16KiB负保留；dadfc328包dtype误改启动前拒绝从未执行，实际bfff519b。',GROUPS['corex-native-gqa-page16'][2])


# 生产离线成品、T64编译和Q64官方两轮筛停；不更新PR105基线。
BATCH_RESULTS['native_q64_production_cpu_build']=('Q64生产接线离线构建成功：821源tree232258a8，实际SO c157a26a；原e5aa CU/bridge/launcher复用。未启动服务/GPU，只获成品身份；官方筛选另列125913。', '保存CPU构建/编译身份，GPU或模型资格另列。', 'CPU成品/资源不等于GPU数值或模型吞吐；不推断occupancy。', '本批418原件完整保存，root回收逐件SHA复用；不为发布重复测试。')
CODE['native-q32-transfer'] += ['experiments/cpu-probes/20261028T124728Z-native-q64-long-context-production-build/raw-evidence.json', 'experiments/cpu-probes/20261028T124728Z-native-q64-long-context-production-build/review.json', 'experiments/cpu-probes/20261028T124728Z-native-q64-long-context-production-build/source-review.json', 'experiments/cpu-probes/20261028T124728Z-native-q64-long-context-production-build/summary.json', 'experiments/bundles/20261028T124728Z-native-q64-long-context-production-build/manifest.json', 'experiments/bundles/20261028T124728Z-native-q64-long-context-production-build/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t32_reuse_production_cpu_build']=('T32复用生产成品离线构建成功：814源treea2ad8270、单CU22e0b2c3、实际SO502e1570。无GPU/服务；123106约0.22%组件小正另列，尚无本生产模型成绩。', '保存CPU构建/编译身份，GPU或模型资格另列。', 'CPU成品/资源不等于GPU数值或模型吞吐；不推断occupancy。', '本批418原件完整保存，root回收逐件SHA复用；不为发布重复测试。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T125302Z-native-gqa-t32-reuse-production-build/raw-evidence.json', 'experiments/cpu-probes/20261028T125302Z-native-gqa-t32-reuse-production-build/review.json', 'experiments/cpu-probes/20261028T125302Z-native-gqa-t32-reuse-production-build/source-review.json', 'experiments/cpu-probes/20261028T125302Z-native-gqa-t32-reuse-production-build/summary.json', 'experiments/bundles/20261028T125302Z-native-gqa-t32-reuse-production-build/manifest.json', 'experiments/bundles/20261028T125302Z-native-gqa-t32-reuse-production-build/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t64_reuse_compile_only']=('T64四页复用仅CPU实际编译：S2、16KiB、88SGPR/88VGPR、0spill；LLVM16817445/ASM b529dbe2。全kernel计数含尾路径，不代替完整quad热循环判断；尚无GPU数值/性能/模型资格。', '保存CPU构建/编译身份，GPU或模型资格另列。', 'CPU成品/资源不等于GPU数值或模型吞吐；不推断occupancy。', '本批418原件完整保存，root回收逐件SHA复用；不为发布重复测试。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T132607Z-native-gqa-t64-reuse-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T132607Z-native-gqa-t64-reuse-compile/review.json', 'experiments/cpu-probes/20261028T132607Z-native-gqa-t64-reuse-compile/source-review.json', 'experiments/cpu-probes/20261028T132607Z-native-gqa-t64-reuse-compile/summary.json', 'experiments/bundles/20261028T132607Z-native-gqa-t64-reuse-compile/manifest.json', 'experiments/bundles/20261028T132607Z-native-gqa-t64-reuse-compile/raw.tar.gz.storage.json']
BATCH_RESULTS['native_q64_official16k_first_warm_negative']=('Q64生产16K原官方首冷4041.81、首暖4819.11 tok/s，两轮256请求成功。对PR105首暖4834.45观察-0.317306%，按预设停止；KV548432对548288不匹配，不称严格因果或稳定退化。实际Q64首launch/原栈通过，DB/源/三SO恢复与清理正常；无完整四轮或准确率，不合并、不改PR105基线。', '首暖未通过筛选，不合并；保留局部正与官方两轮负观察。', 'KV不同，不称严格因果或稳定退化；未跑满四轮、未跑准确率。', '本批418原件完整保存，root回收逐件SHA复用；不为发布重复测试。')
CODE['native-q32-transfer'] += ['experiments/official/20261028T125913Z-native-q64-long-context-16k-four-rounds/raw-evidence.json', 'experiments/official/20261028T125913Z-native-q64-long-context-16k-four-rounds/review.json', 'experiments/official/20261028T125913Z-native-q64-long-context-16k-four-rounds/source-review.json', 'experiments/official/20261028T125913Z-native-q64-long-context-16k-four-rounds/summary.json', 'experiments/bundles/20261028T125913Z-native-q64-long-context-16k-four-rounds/manifest.json', 'experiments/bundles/20261028T125913Z-native-q64-long-context-16k-four-rounds/raw.tar.gz.storage.json']
GROUPS['native-q32-transfer']=(GROUPS['native-q32-transfer'][0],GROUPS['native-q32-transfer'][1]+' 124728离线生产构建后，125913原16K仅完成4041.81/4819.11两轮、256成功；首暖对4834.45观察-0.317306%，预设停止。KV548432对548288不同，不称严格因果或稳定退化；实际Q64首launch有效、源/三SO/DB恢复清理通过。未跑满四轮/准确率、不合并，当前基线仍PR105。',GROUPS['native-q32-transfer'][2])
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0],GROUPS['corex-native-gqa-page16'][1]+' 125302 T32复用生产SO502e1570离线构建，未新增模型成绩；132607新native T64仅CPU16KiB/88SGPR/88VGPR/0spill，热循环和GPU门不由资源记录替代。与旧Triton T64负结果分开，未宣称收益。',GROUPS['corex-native-gqa-page16'][2])


# T32官方首暖筛停、T64组件负与premax仅CPU编译；保留PR105基线。
BATCH_RESULTS['native_gqa_t32_reuse_official4k_first_warm_negative']=('T32复用4K原官方首冷5491.63／首暖6412.53 tok/s，两轮512请求成功；对PR105首暖6441.35观察−0.447422%，按门停止。KV548432对548336不同，非严格因果/稳定退化；源/两SO/DB与清理通过。无完整四轮/16K/准确率，不合并、不改PR105。', '首暖未通过筛选，不合并；保留原组件小正。', 'KV不同，不称严格因果或稳定退化；未满四轮/16K/准确率。', '本批450原件完整保存；复用root回收SHA及已有终态检查，不为发布重测。')
CODE['corex-native-gqa-page16'] += ['experiments/official/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/raw-evidence.json', 'experiments/official/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/review.json', 'experiments/official/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/source-review.json', 'experiments/official/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/summary.json', 'experiments/bundles/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/manifest.json', 'experiments/bundles/20261028T132807Z-native-gqa-t32-reuse-4k-four-rounds/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_t64_reuse_component_negative']=('T64四页复用N64/S2/KV4096完整producer+原reducer ABBA32：九原case、六双臂FP64、三非有限、同臂Graph/尾/side/输入RNG通过。Event .409594774→.421100542ms慢2.809061%，wall慢2.675528%；数值通过但性能负，停止，不进模型或合并。', '数值通过、性能负，停止，不扩shape或进入模型。', '跨算法位型仅诊断，原数值门通过；组件负不冒充模型成绩。', '本批450原件完整保存；复用root回收SHA及已有终态检查，不为发布重测。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/raw-evidence.json', 'experiments/framework/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/review.json', 'experiments/framework/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/source-review.json', 'experiments/framework/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/summary.json', 'experiments/bundles/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/manifest.json', 'experiments/bundles/20261028T134552095824Z-native-gqa-t64-reuse-hotspot-component/raw.tar.gz.storage.json']
BATCH_RESULTS['native_gqa_premax_vote_compile_only']=('premax vote仅CPU实际编译：8KiB／64SGPR／76VGPR／0spill，LLVMf2b09bfe/ASM6ec14738。试图在max树前统一vote跳过max/rho，仍需实际CFG和原数值/Graph门；无GPU/性能/模型资格，不把后续准备态计为已跑。', '保留CPU机制候选，GPU数值/性能待验证。', 'CPU编译不等于GPU数值或模型吞吐资格。', '本批450原件完整保存；复用root回收SHA及已有终态检查，不为发布重测。')
CODE['corex-native-gqa-page16'] += ['experiments/cpu-probes/20261028T134934Z-native-gqa-premax-vote-compile/raw-evidence.json', 'experiments/cpu-probes/20261028T134934Z-native-gqa-premax-vote-compile/review.json', 'experiments/cpu-probes/20261028T134934Z-native-gqa-premax-vote-compile/source-review.json', 'experiments/cpu-probes/20261028T134934Z-native-gqa-premax-vote-compile/summary.json', 'experiments/bundles/20261028T134934Z-native-gqa-premax-vote-compile/manifest.json', 'experiments/bundles/20261028T134934Z-native-gqa-premax-vote-compile/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0],GROUPS['corex-native-gqa-page16'][1]+' 132807 T32复用生产4K仅完成5491.63/6412.53两轮、512成功，首暖对6441.35观察−0.447422%；KV548432对548336不同，按门停止、不作严格因果、不合并。134552 T64原九case和六双臂FP64通过，但完整ABBA Event慢2.809061%、wall慢2.675528%，停止。134934 premax vote仅CPU8KiB/64SGPR/76VGPR/0spill，无GPU/模型资格。正式基线保持PR105。',GROUPS['corex-native-gqa-page16'][2])

# 已回收后继组件；等待与后续原件批量发布。
BATCH_RESULTS['native_gqa_premax_vote_component_neutral_event_stop']=('premax vote N64/S2/KV4096完整producer+原reducer ABBA32：原九case及三个新增边界共12门、有限output/partial硬逐位、原FP64、非有限/Graph/尾/side/输入RNG通过。Event .409584254→.409590021ms近持平慢0.001408%，wall省0.084431%；按原Event门停止，不进生产/官方、不改PR105，原134934仅CPU编译事实保留。', '数值通过，按原Event门停止，不进生产或官方。', 'Event近似持平，wall小正不改原筛选门；无模型资格。', '完整producer+原reducer Graph ABBA32；复用既有根终态薄审与回收SHA，无发布重测。')
CODE['corex-native-gqa-page16'] += ['experiments/framework/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/raw-evidence.json', 'experiments/framework/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/review.json', 'experiments/framework/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/source-review.json', 'experiments/framework/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/summary.json', 'experiments/bundles/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/manifest.json', 'experiments/bundles/20261028T141255044639Z-native-gqa-premax-vote-hotspot-component/raw.tar.gz.storage.json']
GROUPS['corex-native-gqa-page16']=(GROUPS['corex-native-gqa-page16'][0],GROUPS['corex-native-gqa-page16'][1]+' 141255随后完成premax组件：12项原/新增case及硬逐位/FP64/Graph/边界通过，Event近持平慢0.001408%、wall省0.084431%；按原Event门停止，无生产/官方资格。',GROUPS['corex-native-gqa-page16'][2])

GROUPS['native-gqa-s8'] = ('native GQA S8生产接入', 'PR105 producer新增N30/S8；仅BF16且Q stride=2048命中，其余fallback。16K四轮正向观察、4K四轮暖均6594.42（对6627.82低0.5039%），两档KV均有差异；原105为101/105通过，但batch8中S8 selected/captured为not_exercised，不证明S8分支准确率覆盖。保持PR105基线，不作严格因果或更新基线。勘误：登记#480把wall数值误写成Event数值；原始results.json及本轮短记记录wall 1.032342→0.768814ms（快25.5272%），本视图按原件显示，不改registry或原始证据。', [])


def group(row):
    if row['profile_id']=='native-gqa-shared4k': return 'native-gqa-shared4k'
    if row['profile_id']=='native-gqa-linear-n64': return 'native-gqa-linear-n64'
    if row['profile_id']=='native-gqa-live-acc': return 'native-gqa-live-acc'
    if row['profile_id'] == 'native-gqa-s8':
        return 'native-gqa-s8'
    if row['profile_id']=='native-gqa-mixed-s4':return 'native-gqa-mixed-s4'
    if row['profile_id']=='native-gqa-production-hotspot':return 'native-gqa-production-hotspot'
    if row['profile_id'] in ('native-q32-transfer', 'directq-grouped-compile', 'directq-grouped-incremental-pure2048'):return 'native-q32-transfer'
    if row['profile_id'] in ('corex-native-gqa-page16','corex-native-gqa-loop'):return 'corex-native-gqa-page16'
    if row['profile_id']=='gqa-fused-append':return 'gqa-fused-append'
    if row['profile_id'] in ('kv-vtranspose', 'q32-mixed-overlap', 'sampler-preprocess-stats', 'gqa-s2-incta', 'lm-head-temperature'):
        return row['profile_id']
    if row['profile_id']=='native-silu-lut':return 'native-silu-lut'
    if row['profile_id']=='kv-lossless':return 'kv-lossless'
    if row['profile_id']=='baseline-environment':return 'baseline-environment'
    if row['profile_id']=='prefill-panel4':return 'prefill-panel4'

    if row['profile_id']=='gqa-for-scalar-i64-s2':
        return 'gqa-scalar-page-base'
    if row['profile_id']=='gqa-for-scalar-i64':
        return 'gqa-scalar-page-base'
    if row['profile_id']=='gqa-scalar-page-base':
        return 'gqa-scalar-page-base'
    if row['profile_id']=='bf16-nonly-down-official':
        return 'bf16-nonly-down'
    if row['profile_id']=='bf16-n256-down-M2048':
        return 'bf16-nonly-down'
    if row['profile_id'] in ('bf16-nonly-down-integration','bf16-nonly-down-M32','bf16-nonly-down-M2048'):
        return 'bf16-nonly-down'
    if row['profile_id'] in ('stream-read-reference','gqa-page-lookahead','bf16-nonly-down'):
        return row['profile_id']
    if row['profile_id'] == 'gqa-for-span':
        return 'gqa-for-span'
    if row['profile_id'] in ('main6971-graph-profile', 'bf16-packed-down', 'prefill-history-tail'):
        return row['profile_id']
    if row['profile_id'] in ('gqa-two-page-t32','prefill-lpt','gqa-sme-span','down-group256','prefill-fresh-kv','qkv-rope-fusion','gate-partial-fusion'):
        return row['profile_id']
    if row['profile_id'] == 'shape-gemm':
        return 'shape-gemm'
    if row['profile_id'] == 'prefill-i32-offset':
        return 'prefill-i32-offset'
    if row['profile_id'] == 'prefill-base2':
        return 'prefill-base2'
    if row['profile_id'] in ('rope-kv-fusion', 'final-ffn-row-prune', 'selected-query-row', 'attention-affine-pages', 'current-main-hotspot', 'attention-next-k', 'gqa-identity-rescale', 'main-correctness', 'gqa-kv-cg', 'gqa-kv-stride', 'lm-head-paired-gemv', 'attention-head-major', 'native-silu-vec2', 'gqa-four-page-t64', 'prefill-log2', 'prefill-stride', 'night-kernel-counters', 'gqa-grouped-simt'):
        return row['profile_id']
    s = (row['profile_id'] + ' ' + row['run_id']).lower()
    if row['profile_id'] == 'launcher_only':
        parent = BY_ID.get(row['run_id'].removesuffix('-control'))
        return group(parent[0]) if parent else 'other'
    for key, pattern in [
        ('pr25-kv-current', r'pr25[_-]kv[_-]current'),
        ('native-cache-identity', r'native[_-]cache[_-]identity'),
        ('pr24-main', r'pr24[_-]main'),
        ('accepted-fill', r'accepted[_-]fill'),
        ('compute-order', r'compute[_-]order'),
        ('allocator-noop', r'allocator[_-]noop'),
        ('kv-restore-pitched', r'kv[_-](?:pitched[_-]restore|restore[_-]pitch)'),
        ('skip-computed-h2d', r'skip[_-]computed[_-]h2d'),
        ('finite-growth-admission', r'finite[_-]growth'),
        ('admission-observer', r'finite[_-]admission|q[_-]gqa[_-]admission[_-]observ'),
        ('q-gqa-framework', r'q[_-]gqa[_-](?:framework|service)'),
        ('async-bookkeeping', r'async[_-](?:cpu[_-])?bookkeeping'),
        ('bq16-chunk-alignment', r'bq16[_-]chunk'),
        ('prefix-scan', r'no[_-]cascade[_-]prefix|prefix[_-]cost|prefix[_-]skip'),
        ('q-fragment-hoist', r'q[_-]?(?:fragment|hoist)'),
        ('attention', r'prefill[_-]w16'),
        ('gpu-hotspots', r'current[_-]mixed|q[_-]gqa[_-]puredecode'),
        ('decode-cpu-gather', r'decode[_-](cpu[_-])?gather'),
        ('c3-views', r'c3[_-]view|c3views'),
        ('hot-key', r'key[_-]recipe|hot[_-]key'),
        ('input-prep', r'input[_-]prep'),
        ('cpu-combination', r'cpu[_-]combination|cpu_metadata_async_token'),
        ('cpu-metadata', r'cpu[_-]metadata'), ('async-token', r'async[_-]token'),
        ('kv-pitched', r'kv[_-]pitched|kv_save_threeway'), ('kv-contiguous', r'kv[_-]page[_-]copy'),
        ('kv-progress', r'progress[_-]victim|preemption[_-]snapshot'), ('kv-memory', r'kv[_-](memory|startup)'),
        ('kv-observation', r'kv[_-]completion|q[_-]gqa[_-]resume[_-]native'), ('kv-protocol', r'kv[_-]'),
        ('admission', r'growth'), ('mapped-attention', r'mapped[_-]decode'),
        ('mm-cta', r'cta|mm[_-]'), ('buffers', r'hidden|bucket'),
        ('event', r'event'), ('official', r'official|original13eb'),
        ('sql', r'sql'), ('attention', r'attention|mixed|decode_launch|direct_decode|\bc[23]\b'),
        ('native-k8-sme', r'native[_-]k8[_-]sme'),
        ('early', r'\bb[0o]\b|\bc1\b|native[_-]decode|dirty_block_table|host[_-]gap'),
    ]:
        if re.search(pattern, s):
            return key
    return 'other'


def platform(row):
    value = row['device'].strip()
    return {'Iluvatar BI-V150': ('bi-v150', '天数 BI-V150'), 'CPU': ('cpu', 'CPU')}.get(
        value, ('unrecorded', value or '未记录'))


def link(target, current, label):
    rel = Path(os.path.relpath(target, current.parent)).as_posix()
    return '[' + label.replace(']', '') + '](' + quote(rel, safe='/.-_') + ')'


def available(path):
    value = str(path).rstrip('/')
    return value in AVAILABLE or any(item.startswith(value + '/') for item in AVAILABLE)


def cell(value):
    return str(value or '未记录').replace('|', '\\|').replace('\n', ' ')


def brief(value, limit=220):
    value = re.sub(r'\s+', ' ', value or '').strip()
    if not value:
        return '未记录'
    # 只摘录原句，不计算/改判结果；优先结果句，并带其适用边界。
    clauses = [x.strip() for x in re.split('[。；]', value) if x.strip()]
    metric = next((x for x in clauses if re.search(r'%|pct|倍|无CPU下降|未见.*收益', x)), None)
    chosen = [metric] if metric else [next((x for x in clauses if re.search('失败|通过|不支持|未激活|不报', x)), clauses[0])]
    boundary = next((x for x in clauses if x not in chosen and re.search('非稳定|非E2E|不外推|仅.*诊断|未.*accuracy|不继承|不报.*收益', x)), None)
    if boundary:
        chosen.append(boundary)
    value = '；'.join(chosen)
    value = re.sub(r'\b[0-9a-f]{32,64}\b', '〔标识见原件〕', value)
    value = value[:limit] + ('…' if len(value) > limit else '')
    return value if re.search('[\u4e00-\u9fff]', value) else '原记录：' + value


def result(row, limit=190):
    if row['run_id'] == '20261029T014250520820Z-native-gqa-s8-hotspot-component':
        return 'Event 1.029299→0.766297ms（快25.5515%），wall 1.032342→0.768814ms（快25.5272%）；以原始results.json及本轮短记为准，registry中wall数值为误抄。'
    if row['run_id'] == '20261029T041010Z-native-gqa-s8-official16k-ready':
        return '官方入口因旧ready-marker reader误识别VLLM环境变量警告而失败；0个benchmark请求、无吞吐计时，不是模型数值错误。'
    current_component_summary = {
        'main241_q32_panel4_negative': '停止panel4生产接入；旧Q16三项边界未启动且暂缓，新main241成为后续研究基础。',
        'main594_m32_fixed_address_firstwarm_negative': '停止本次M32生产路线，保留全部两轮原件；不继续旧main验证或把局部收益算官方收益。',
        'prefill_panel4_long_positive': '保留旧Q16组件证据；新main241 Q32组合已负，停止生产接入，原边界不再排队。',
        'main594_m32_fixed_address_positive': '保留M32组件证据；后续官方16K首暖低0.23295%，本次生产路线已停止。',
        'main594_m32_provider_identified': '保留真实配置，准备一个M32固定寻址组件；不能直接搬用M64配置或收益。',
        'main594_m64_fixed_address_firstwarm_negative': '停止当前M64生产路线；保留组件与官方负结果，不开优化PR或拼成完整四轮成绩。',
        'main594_control_16k_complete': 'main594独立16K四轮暖均4192.49，512成功，清理通过；作为同档控制。',
        'main594_control_interrupted_4k_complete': 'main594控制4K四轮暖均5847.6667，16K首轮中断；已恢复并补测，非完整新基线。',
        'main594_m64_fixed_address_positive': 'M64固定寻址单组组件省1.47792%，8门过/无额外权重；待官方净收益。',
        'main594_mm_provider_identity': '新main M64已BN64/grid32，旧窄N提案停止；单次身份/资源，无性能结论。',
        'gqa_for_scalar_i64_s2_negative_component': '8门/逐位通过；实际stages2、async-copy4/SME16，完整Graph慢27.63241%，停止不扫stage。',
        'gqa_for_scalar_i64_negative_component': '8门/逐位通过；实际SME LLVM8/ASM8，完整Graph慢10.73864%，停止。资源下降不是收益证明，无官方/105。',
        'nonly_down_identity_official_mixed_no_baseline': '4K四轮暖均5719.8133（对5656.77观察+1.1145%）；16K首暖4005.55（对4119.46观察−2.7652%）后停，六轮1280 SUCCESS。修复后旧prefill栈/FX42有效，KV516320；混合结果，无105/新基线。',
        'gqa_scalar_page_base_negative_component': '8类门及跨臂逐位通过；Event0.542196542→0.544291317ms，慢0.38635%，停止。SGPR spill75为lane保存非HBM；实际SME仍0，for＋scalar未验证。',
        'nonly_down_official_first_warm_negative': '4K冷/首暖4758.57/5440.33 tok/s，512 SUCCESS；首暖对5533.03观察−1.675393%后主动停。pack42/FX42/M64已证；compute-order源SHA拒绝，prefill未闭合，KV516320；无16K/105。',
        'n256_down_M2048_negative_component': '新N256布局保持原tile，8门/RNG通过；完整Graph Event0.563351333141→0.704238474369ms，慢25.01%，停止全M路线；B异步环变化未证精确因果，无官方资格。',
        'stream_read_reference_completed': '连续流读参考665.432GB/s，checksum/copy检查通过；不是HBM硬上限或模型吞吐收益。',
        'gqa_page_lookahead_no_positive_signal': '8类数值门与逐位通过；完整组件Event慢0.1057%、wall快0.0613%，无可分辨正信号，停止。',
        'nonly_down_positive_component': 'M64单层9类检查通过，完整GEMM Event省10.5534%；保留组件候选，42层显存成本与模型净收益未测。',
        'nonly_down_integration_component_pass': '42真实权重helper/opaque、pack逐位、FP64、换值Graph及M32回退通过；不是完整Llama加载链，无计时或官方资格。',
        'nonly_down_M32_positive_component': 'M32单层8门通过，同配置完整Graph Event省约3.63%；保留组件信号，非模型收益，双份权重成本未消除。',
        'nonly_down_M2048_negative_component': 'M2048单层8门通过；P128使BN256→128，完整Graph Event慢约61.60%，停止；不能归因纯pack，不否定M32/M64。',
    }
    if row['status'] in current_component_summary:
        return current_component_summary[row['status']]
    if row['profile_id'] in ('shape-gemm','gqa-two-page-t32','prefill-lpt','gqa-sme-span','down-group256','prefill-fresh-kv','qkv-rope-fusion','gate-partial-fusion'):
        return row['conclusion'][:limit]
    """只摘结果/失败原句，不把审计与库身份搬入主视图。"""
    if row['status'] in BATCH_RESULTS:
        return BATCH_RESULTS[row['status']][0][:limit]
    if row['status'] in ('model_compile_failed', 'model_semantic_failed', 'baseline_mixed_failed', 'baseline_mixed_pass', 'baseline_serial_pass', 'selected_query_model_failed', 'selected_query_model_pass'):
        return row['conclusion'][:limit]
    if row['status'] in ('query_component_tp_initialization_failed', 'rope_official_screen_early_stopped', 'query_component_pinning_construction_failed', 'query_component_completed_numerical_unassessed'):
        return row['conclusion'][:limit]
    if row['status'] in ('official_staging_completed_kv_mismatch', 'rope_v2_model_gate_pass', 'final_ffn_mixed_semantic_failed'):
        return row['conclusion'][:limit]
    if row['status'] == 'kv_restore_pitched_verify1_pass':
        return '535 VERIFY1：32成功、双向730103808字节一致、SAVE546/FULL714；4/4语义与34层native图通过。KV547632，非性能或完整准确率。'
    if row['status'] == 'fullsize_two_rounds_restore_posthoc':
        return '535两轮：4K5403.92/5732.73、16K3824.19/4066.32，768/0、14条FULL链。KV失配不算收益；原外层比较异常与posthoc分开保留。'
    if row['status'] == 'kv_staging_primitive_net_signal':
        return '42层primitive全字节门通过；含pack/scatter等事务总wall三对省322.382/347.481/314.353ms，仅独立微测，不是模型收益。'
    if row['status'] == 'official_restore_pitched_kv_mismatch':
        return '535官方两档各4轮、1536/0；第2–4轮4K5703.70/16K4060.24 tok/s，28条FULL链。KV失配、差值null；完整105未过，不设新基线。'
    if row['status'] == 'kv_staging_service_verify1_pass':
        return '538 VERIFY1：32成功、4/4语义与34native图、每向729415680字节通过，42 kernels＋43 DMA/向；KV547536，非性能/105。'
    if row['status'] == 'rope_component_recording_failed':
        return 'configs=None导致记录器TypeError，无有效case；原失败保留，不作数值或性能负结果。'
    if row['status'] == 'rope_component_positive_signal':
        return '42层字节/guard/变输入Graph通过；M2048/32/64 Graph总wall约5.070→4.791、0.899→0.864、0.982→0.896ms，仅局部组件。'
    if row['status'] == 'final_ffn_dispatch_recording_failed':
        return '实际mm_out logger未挂入记录链，守卫停止，无有效case；清理/DB恢复通过，不是数值或性能负结果。'
    if row['status'] == 'staging_screen_kv_mismatch':
        return '538两轮：4K5544.36/5615.02，16K3845.32/4078.31，768成功；KV失配，只观察暖轮−2.38%/＋0.82%。'
    if row['status'] == 'final_ffn_component_positive_signal':
        return '四shape逐bit/变输入Graph通过；M2048→S32/64 Graph总wall约2.386→0.170/2.397→0.183ms，仅组件，不含dense回填。'
    if row['status'] == 'rope_model_source_and_parser_failed':
        return '4/4语义正确，但图门跨submod误拒且新增.best_config；source_unchanged=false、completed=false，原失败保留。'
    if row['status'] == 'official_four_rounds_baseline_completed':
        return '官方两档各4轮、1536/0；第2–4轮4K5758.72/16K4045.20 tok/s，TTFT3626.85/124212.05ms；本实例该版本完整105仍待。'
    if row['status'] == 'official_candidate_early_stopped':
        return '主动早停：4K第2–4轮−0.98%；16K仅第2–3轮−1.94%，R4不完整。背景主机负载未完全匹配，不严格归因KV。'
    if row['status'] == 'kv_staging_gross_budget_only':
        return '独立42层双向字节门通过；碎片/连续参照毛预算0.31–0.34s，未计gather/scatter等成本，非净收益。'
    if row['status'] == 'startup_gate_log_phrase_rejected':
        return '正式测量前额外compiled graph文案门误拒；exit1，无吞吐。随后CPU日志回放不算本轮模型资格。'
    if row['status'] == 'startup_gate_path_prefix_rejected':
        return '正式测量前图门误拒目录前缀；exit1，无吞吐。后验FX/FP/AOT及相对handles相同，原失败保留。'
    if row['status'] == 'fullsize_two_rounds_baseline_completed':
        return '4K两轮5396.58/5730.67、16K两轮3565.12/3992.53 total tok/s；768请求全成功，KV546432。仅本组筛选基线，非官方四轮分数或优化收益。'
    if row['status'] == 'kv_verify1_model_path_pass':
        return '32/0；R16960、每方向729415680字节一致，SAVE504/FULL2688。另同服务4/4语义正确、实际34层native图；VERIFY1不计性能或完整准确率。'
    if row['status'] == 'fullsize_two_rounds_mixed_signal':
        return '候选768/0；4K5402.15/5767.57（+0.103%/+0.644%，无FULL不可归因），16K3733.69/3972.85（+4.728%/−0.493%）。未确认稳定收益，待官方四轮。'
    if row['profile_id'] == 'pr24-main' and row['status'].startswith('model_path_invalidated_stale_aot_'):
        return row['conclusion'].split('。', 1)[0] + '。'
    if row['status'] == 'checker_failed_after_first_semantic_response':
        return '49项组件通过；首启答案85被checker的think格式解析误拒，原失败保留，不记模型算术失败。'
    if row['status'] == 'default_cache_restart_semantics_pass':
        return '默认缓存重启4/4语义正确（含4908token），同AOT与34层native图；仅服务验证，非官方准确率或性能。'
    if row['status'] == 'accuracy_pass_native_graph_verified':
        return '隔离缓存后实际34层native；Math500 Level3 100/105（95.2381%）通过，0请求错误/0空最终。仅本轮准确率，不恢复旧失配轮次资格、不报性能。'
    if row['run_id'] == '20261023T125330Z-compute-order-math4-event':
        return '客户端长度校验在发送前失败；背景0发送、四题未放行，本轮未评价优化。'
    if row['run_id'] == '20261023T130351Z-compute-order-math4-event':
        return '原四题4/4正确，3题实际覆盖且在首完整答案框前；背景32/0。仅小样本诊断，不计性能或完整准确率。'
    note = re.sub(r'\s+', ' ', row['conclusion']).strip()
    if row['profile_id'] == 'launcher_only':
        return '启动或收集记录，实验结果见对应主run。'
    clauses = [x.strip() for x in re.split(r'[。；;]', note) if x.strip()]
    if row['status'] == 'oracle_favors_permuted_sample_only':
        return '；'.join(x for x in clauses if x.startswith(('独立CPU FP32', '本样本P')))
    if row['status'] == 'first_layer_attention_mismatch_localized':
        return clauses[0] + '；仅诊断，候选暂不集成'
    positive = next((x for x in clauses if re.search(r'(?i)(?:TPS|TTFT|吞吐|耗时|wall|event)\s*(?:[+−-]\d|省\d|提升|降低)|\d+(?:\.\d+)?(?:%|pct|倍)|throughput factor\s+\d', x)), None)
    negative = next((x for x in clauses if re.search(r'无CPU下降|未见.*收益|无正信号|不支持.*收益|未激活|未命中|失败|遮蔽.*循环', x)), None)
    correctness = next((x for x in clauses if re.search(r'字段.*过|checks.*(?:过|true)|全bytes|全字节|bitwise|RNG.*(?:同|过|true)|输出.*通过|正确性.*通过', x, re.I)), None)
    choice = positive or negative or correctness
    if not choice:
        measured = re.search(r'\d+(?:\.\d+)?s/\d+(?:\.\d+)?(?:total|TPS)/TTFT\d+(?:\.\d+)?ms', note, re.I)
        choice = measured[0] if measured else (clauses[0] if clauses else '')
    if not choice:
        return '结果未单列；见原始记录。'
    # 从语义结果开始，不展示前置的SHA、seal、源码数、审计话术。
    start = re.search(r'(?i)TPS[+−-]|TTFT[+−-]|吞吐|耗时|wall|event|无CPU下降|未见|无正信号|未激活|未命中|\d+\s*成功\s*[/,，]?\s*\d+\s*失败|\d+\s*失败|失败|遮蔽|五case|两case|四case|\d+checks|全bytes|全字节|bitwise|RNG|字段|输出', choice)
    text = choice[start.start():] if start else choice
    text = re.sub(r'(?i)\b[0-9a-f]{8,64}\b(?=[^\w.]|$)', lambda m: '' if re.search('[a-f]', m[0], re.I) else m[0], text)
    text = re.sub(r'(?i)\d+seal|\b(?:SHA|schema|logical)[^，,；。 ]*|审计[^：:]*[：:]|后验[^：:]*[：:]', '', text)
    text = text.strip(' ，,：:/')
    # 结果正文限长；适用限制单独保留，不能在截断时把限制一并丢掉。
    boundary_pattern = r'非稳定|非E2E|不外推|不作.*归因|不报.*收益|不继承|无新accuracy|未.*accuracy|(?:DB|KV).*不同|(?:DB|KV).*未.*(?:快照|匹配)|not snapshotted|no (?:stable|model|new accuracy)|no .*comparison|never ready'
    boundaries = [x for x in clauses if re.search(boundary_pattern, x, re.I)]
    summary = text[:limit] + ('…' if len(text) > limit else '') if text else clauses[0][:limit]
    missing = [x for x in boundaries if x not in summary and not (x.endswith(text) and len(text) <= limit)]
    if missing:
        # 首段结果与至多两条直接限制即可导航；其它细节仍在完整原登记。
        summary += '；' + '；'.join(missing[:2])
        if len(missing) > 2:
            summary += '；其余限制见完整原登记'
    return summary


def keep(row):
    if row['status'] in BATCH_RESULTS:
        return BATCH_RESULTS[row['status']][1]
    if row['status'] == 'affine_model_short_gate_pass':
        return '保留进入原官方吞吐；完整105与混合/P实际覆盖尚待，不声称已恢复旧mixed2资格。'
    if row['status'] == 'current_main_hotspot_completed':
        return '保留有效当前轨迹；优先验证prefill Attention候选，不把FULL图壳或几步比例外推成全负载预算。'
    if row['status'] == 'affine_component_positive_signal':
        return '保留候选；真实服务页段覆盖、P索引接入及模型准确率待验，组件收益不代替官方吞吐。'
    if row['status'] in ('model_compile_failed', 'model_semantic_failed', 'baseline_mixed_failed', 'baseline_mixed_pass', 'baseline_serial_pass', 'selected_query_model_failed', 'selected_query_model_pass'):
        return '保留原始结果；模型门失败不进入性能验证，对照结论与候选收益分开。'
    text = row['conclusion']
    state = row['status'].lower()
    if row['status'] in ('query_component_tp_initialization_failed', 'rope_official_screen_early_stopped', 'query_component_pinning_construction_failed', 'query_component_completed_numerical_unassessed'):
        return '原始证据和失败保留；是否进入模型/合并以本轮结论为准，不自动续测。'
    if row['status'] in ('official_staging_completed_kv_mismatch', 'rope_v2_model_gate_pass', 'final_ffn_mixed_semantic_failed'):
        return '保留本轮原件与边界；收尾不重复测试，后继仅按实际资格继续。'
    if state == 'kv_restore_pitched_verify1_pass':
        return '保留535字节与小样本语义资格；关闭回读后做性能，完整105另验。'
    if state == 'fullsize_two_rounds_restore_posthoc':
        return '保留候选进入完整535验证；不设新基线，不把事后汇总记为原owner无异常。'
    if state == 'kv_staging_primitive_net_signal':
        return '保留staging集成候选；服务同步、显存/KV影响和端到端收益仍待验证。'
    if state == 'official_restore_pitched_kv_mismatch':
        return '保留完整官方组合观察与原件；不算严格因果收益、不更新accepted baseline，完整105仍待。'
    if state == 'kv_staging_service_verify1_pass':
        return '保留538服务字节与语义资格，关闭回读后再筛性能；不更新基线。'
    if state == 'rope_component_recording_failed':
        return '保留失败；仅修记录器后另开v2，不追溯改判。'
    if state == 'rope_component_positive_signal':
        return '保留正信号供模型接线，模型准确率/端到端尚待。'
    if state == 'final_ffn_dispatch_recording_failed':
        return '保留首次失败；独立v2仅修日志，等待新run。'
    if state == 'staging_screen_kv_mismatch':
        return '保留16K筛选信号，后续完整测量；KV失配不报因果收益，不更新基线。'
    if state == 'final_ffn_component_positive_signal':
        return '保留局部正信号供模型接线，实际模型准确率/端到端收益待。'
    if state == 'rope_model_source_and_parser_failed':
        return '保留失败与posthoc原件；cache位置和parser修复后另验，不能追溯恢复资格。'
    if state == 'official_four_rounds_baseline_completed':
        return '保留作当前性能对照基线；完整105仍待，不称最终合格基线，不跨队友条件算收益。'
    if state == 'official_candidate_early_stopped':
        return '保留负差与主动早停原件，不计完整官方成绩或新基线；不为解释负差重跑。'
    if state == 'kv_staging_gross_budget_only':
        return '保留毛预算，尚未证明staging净收益；后续必须计入额外搬运、索引及显存成本。'
    if state == 'startup_gate_log_phrase_rejected':
        return '保留原失败及单列的事后CPU回放；修测量日志门另开run，不追溯补记模型资格或成绩。'
    if state == 'startup_gate_path_prefix_rejected':
        return '保留原失败与后验身份取证；修测量目录门后另开run，不补记成绩。'
    if state == 'fullsize_two_rounds_baseline_completed':
        return '保留两档全部原轮作本组筛选基线；不丢首轮、不以第二轮变快归因优化，不自动定为新官方基线。'
    if state == 'kv_verify1_model_path_pass':
        return '保留KV字节、真实模型路径和4题语义门；允许进入关闭VERIFY回读的性能对照，完整组合准确率另验。'
    if state == 'fullsize_two_rounds_mixed_signal':
        return '候选保留待确认；两轮未见明显退化，但16K正负并存。按用户要求跑满官方四轮并完成最终组合准确率后再下结论、确定新基线。'
    if row['profile_id'] == 'pr24-main' and state.startswith('model_path_invalidated_stale_aot_'):
        facts = {'standalone_pass': '9项组件检查与请求原件', 'cpu_observation': 'CPU抢占及失败/恢复原件', 'smoke_failed': '探针识别失败原件', 'native_trace': '旧图运行的trace及冷调优证据', 'kv_bytes_pass': 'KV全字节与消费者到达证据', 'screen_stopped': '异常中止、两轮4K原值及缓存失配原件'}
        fact = facts.get(state.removeprefix('model_path_invalidated_stale_aot_'), '原始诊断事实')
        return f'保留{fact}；撤回PR24模型路径资格，不作有效基线、完整模型正确性或净收益预算。'
    if state == 'checker_failed_after_first_semantic_response':
        return '保留49组件通过及checker失败原件；首启图为后续首次补存，不将本轮流程改判成功。'
    if state == 'default_cache_restart_semantics_pass':
        return '保留缓存修复和重启语义通过证据；组件未重测，源码新版本的官方性能与完整准确率另验。'
    if state == 'accuracy_pass_native_graph_verified':
        return '保留本实例实际native路径及完整准确率通过证据；3题输出上限、1题无可提取答案仍在105分母。旧六轮失配不恢复，默认缓存修复与性能另验。'
    if state == 'official_pass_q_selected_no_fallback':
        return '保留并已合并PR23；确认为最新BI-V150基准，KV失配边界随结果保留。'
    if state == 'accuracy_pass' and row['profile_id'] == 'q-fragment-hoist':
        return '保留准确率通过证据及2题输出上限边界；组合已合并。'
    if state == 'diagnostic_selected_cleanup_exit2_not_performance':
        return '保留适配失败/修复与选中证据；短诊断exit2，不作性能或准确率。'
    if state == 'confounded_kv_capacity_current_main':
        return '保留基线与候选；KV容量不同，不计归因收益，组合准确率另验。'
    if state == 'client_validation_failed_before_requests':
        return '保留客户端失败与修复证据；本轮未评价优化。'
    if state == 'limited_math4_quality_signal_three_outside_questions':
        return '保留小样本质量信号及候选，可准备独立Draft PR；暂不集成。'
    if state == 'comparable_single_pair' and row['profile_id'] == 'compute_order':
        if 'baseline' in row['phase']:
            return '保留作本轮可比对照基线。'
        return '保留单pair正信号；稳定收益与目标路径质量尚待确认，暂不集成。'
    if state in ('first_layer_attention_mismatch_localized', 'oracle_favors_permuted_sample_only'):
        return '保留诊断与候选；完整正确性尚未确认，暂不集成，不计性能。'
    if row['profile_id'] == 'launcher_only':
        return '保留作过程记录。'
    if row['profile_id'] == 'finite_admission_observer':
        return '保留作准入状态诊断；尚未实现预留策略，不提供性能收益结论。'
    if row['profile_id'] == 'q_gqa_framework' and 'baseline' in row['phase']:
        return '保留作GQA对照基线；组合单pair正信号与独立准确率另列。'
    if row['profile_id'] == 'q_gqa_framework' and row['phase'] == 'official_math500_level3':
        return '组合准确率通过；性能仍仅单pair，不据此声明稳定或完整官方成绩。'
    if row['profile_id'] == 'async_cpu_bookkeeping' and 'baseline' in row['phase']:
        return '保留作对照基线；KV失配，不据此判断候选收益。'
    if 'input_prep_timing' in row['profile_id']:
        return '保留诊断结论；当前不据此实施输入同步优化。'
    if re.search(r'baseline|reference|original13eb|^b0$', row['profile_id'], re.I):
        return '保留作对照基线；不据此判断候选收益。'
    if re.search(r'failed|reject|error|no_.*cpu_reduction', state) or re.search(r'放弃|不集成|未集成|不启用|不服务集成|无CPU下降|未见.*收益|无正信号', text):
        return '未集成；失败或无收益记录保留。'
    if 'positive_signal' in state or re.search(r'信号.{0,8}保留|保留.{0,8}候选|小收益.{0,8}保留', text):
        return '保留作候选，仍待确认；不等于默认启用。'
    return '待确认；通过某项检查不自动等于优化保留。'


def how(row):
    if row['status'] in BATCH_RESULTS:
        return BATCH_RESULTS[row['status']][3]
    phase = row['phase'].lower()
    if row['phase'] == 'kv_staging_primitive':
        return '独立42层真实页序；双向全字节/guard/event门及三组完整事务wall配对，含pack/scatter与索引，不含模型服务。'
    if row['profile_id'] == 'launcher_only':
        return '只记录启动、日志或封存，不单独测性能。'
    kind = next((label for pattern, label in [
        ('fullsize_two_rounds' if row['profile_id'] == 'pr25-kv-current' else r'(?!)', '官方负载规模、每档两轮筛选；非官方四轮成绩'),
        ('kv_verify1' if row['profile_id'] == 'pr25-kv-current' else r'(?!)', '真实服务KV全字节VERIFY1与独立4题语义/实际编译图检查'),
        ('cpu_oracle', '实际单行KV与独立CPU FP32/FP64参考'),
        ('first_layer_diagnostic', '自然混合负载同一步首层对照诊断'),
        ('official', '原官方吞吐对照'), ('accuracy', '准确率门'), ('profile', '性能分析诊断'),
        ('gate|correctness|byte', '局部正确性或能力门'), ('smoke|startup|descriptor', '启动或描述符诊断'),
        ('context|screen|decode|4k|16k', '真实服务短负载')]
        if re.search(pattern, phase)), '具体测法未单列，见原命令')
    shape = ' / '.join(row[key] or '未记录' for key in ('input_len', 'output_len', 'concurrency', 'num_prompts'))
    return kind + '；输入 / 输出 / 并发 / 请求数：' + shape + '。'


def code_links(key, page):
    paths = [ROOT / x for x in CODE.get(key, ['patches/framework']) if available(x)]
    return '；'.join(link(x, page, x.name) for x in paths) or '未单列，见原件源码清单'


def status(row):
    if row['status'] in BATCH_RESULTS:
        return BATCH_RESULTS[row['status']][2]
    if row['status'] == 'affine_model_short_gate_pass':
        return '原四语义及真实页表绑定通过'
    if row['status'] == 'current_main_hotspot_completed':
        return '当前路径诊断完成，非吞吐成绩'
    if row['status'] == 'affine_component_positive_signal':
        return '组件逐位通过，存在局部正信号'
    if row['status'] in ('model_compile_failed', 'model_semantic_failed', 'baseline_mixed_failed', 'baseline_mixed_pass', 'baseline_serial_pass', 'selected_query_model_failed', 'selected_query_model_pass'):
        return '真实模型诊断完成，结论与限制见本轮'
    value = row['status'].lower()
    if row['status'] in ('query_component_tp_initialization_failed', 'rope_official_screen_early_stopped', 'query_component_pinning_construction_failed', 'query_component_completed_numerical_unassessed'):
        return '阶段收尾，原始结果及限制已保存'
    if row['status'] in ('official_staging_completed_kv_mismatch', 'rope_v2_model_gate_pass', 'final_ffn_mixed_semantic_failed'):
        return '已完成，结论及限制见本轮'
    if value == 'kv_restore_pitched_verify1_pass':
        return '535字节与模型路径门通过'
    if value == 'fullsize_two_rounds_restore_posthoc':
        return '两轮筛选完成，比较事后补存'
    if value == 'kv_staging_primitive_net_signal':
        return 'staging微测正信号，未集成模型'
    if value == 'official_restore_pitched_kv_mismatch':
        return '535官方完成，KV失配/105待验'
    if value == 'kv_staging_service_verify1_pass':
        return '538服务字节与语义门通过'
    if value == 'rope_component_recording_failed':
        return '组件记录失败，无有效case'
    if value == 'rope_component_positive_signal':
        return '组件通过并有局部正信号'
    if value == 'final_ffn_dispatch_recording_failed':
        return '执行日志守卫失败，无有效case'
    if value == 'staging_screen_kv_mismatch':
        return '538筛选完成，KV条件失配'
    if value == 'final_ffn_component_positive_signal':
        return '末层组件通过，局部正信号'
    if value == 'rope_model_source_and_parser_failed':
        return '模型门失败：源码后态与图解析'
    if value == 'official_four_rounds_baseline_completed':
        return '四轮性能基线完成，完整105待验'
    if value == 'official_candidate_early_stopped':
        return '负差后主动早停，非完整成绩'
    if value == 'kv_staging_gross_budget_only':
        return '独立搬运毛预算，不计净收益'
    if value == 'startup_gate_log_phrase_rejected':
        return '日志文案门误拒，正式测量未启动'
    if value == 'startup_gate_path_prefix_rejected':
        return '目录门误拒，正式测量未启动'
    if value == 'fullsize_two_rounds_baseline_completed':
        return '两轮基线完成，不单报收益'
    if value == 'kv_verify1_model_path_pass':
        return 'KV字节与模型路径门通过'
    if value == 'fullsize_two_rounds_mixed_signal':
        return '两轮正负并存，待官方四轮'
    if value.startswith('model_path_invalidated_stale_aot_'):
        return '旧AOT图失配，模型资格撤回'
    if value == 'checker_failed_after_first_semantic_response':
        return '检查器格式误拒，原失败保留'
    if value == 'default_cache_restart_semantics_pass':
        return '默认缓存重启语义通过'
    if value == 'accuracy_pass_native_graph_verified':
        return '真实native路径与完整准确率通过'
    if value == 'client_validation_failed_before_requests':
        return '客户端发送前失败'
    if value == 'limited_math4_quality_signal_three_outside_questions':
        return '小样本质量信号（3/4题覆盖）'
    if value == 'diagnostic_selected_cleanup_exit2_not_performance':
        return '适配诊断，不计性能'
    if value == 'comparable_single_pair':
        return '可比单对照，候选待确认'
    if value in ('first_layer_attention_mismatch_localized', 'oracle_favors_permuted_sample_only'):
        return '诊断完成，候选待确认'
    for needle, text in [('confounded', '不可直接比较'), ('inconclusive', '结论未定'),
                         ('not_activated', '未激活'), ('no_activation', '未激活'),
                         ('failed', '失败/未通过'), ('reject', '失败/未通过'),
                         ('error', '失败/未通过'),
                         ('partial', '部分记录'), ('running', '进行中'), ('pending', '待处理'),
                         ('complete', '已完成'), ('pass', '通过'), ('candidate', '候选，见短记'),
                         ('integration_only', '仅集成记录'), ('launch', '启动/控制记录'),
                         ('profile', '诊断记录')]:
        if needle in value:
            return text
    return '已登记，见短记' if row['status'] else '未记录'


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not path.read_text(encoding='utf-8').startswith(MARK):
        raise RuntimeError('不覆盖人工文件：' + str(path))
    path.write_text(MARK + text.rstrip() + '\n', encoding='utf-8', newline='\n')
    GENERATED.append(path.relative_to(ROOT).as_posix())


def evidence(rows):
    folders = [ROOT / r['artifacts'] for r in rows if r['artifacts']]
    folders = list(
        dict.fromkeys(
            p
            for p in folders
            if available(p.relative_to(ROOT).as_posix())
        )
    )
    commands, manifests, raw, logs = [], [], [], []
    for folder in folders:
        control = folder.with_name(folder.name + '-control')
        for base in (folder, control):
            base_rel = base.relative_to(ROOT).as_posix()
            commands += [base / n for n in ('command.json', 'command.txt', 'benchmark-command.json', 'load-commands.json', 'launch-command.json', 'launch.sh') if base_rel + '/' + n in AVAILABLE]
            manifests += [base / n for n in ('manifest.json', 'purpose.json', 'source-sha256.json', 'postflight-full.json', 'postflight.json') if base_rel + '/' + n in AVAILABLE]
        folder_rel = folder.relative_to(ROOT).as_posix()
        for path in sorted(AVAILABLE):
            if not path.startswith(folder_rel + '/'):
                continue
            relative = path[len(folder_rel) + 1:]
            if relative in ('results.json', 'result.json') or any(
                fnmatch.fnmatch(relative, pattern)
                for pattern in ('*/results/*.json', '*/results/*.csv', '*.csv', '*/*.csv')
            ):
                if Path(path).name != 'gpu.csv' and '/source/' not in '/' + path:
                    raw.append(ROOT / path)
        logs += [folder / n for n in ('server.log', 'worker.log', 'gate.log', 'gpu.csv', 'exit-code') if folder_rel + '/' + n in AVAILABLE]
    return folders, {'原命令': commands, '环境 / 源码 / 后态': manifests, '原始结果': raw, '日志 / 采样': logs}


def main():
    global BY_ID, GENERATED, AVAILABLE
    GENERATED = []
    tracked = set(
        subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()
    )
    present = {
        path.relative_to(ROOT).as_posix()
        for path in ROOT.rglob('*')
        if path.is_file() and '.git' not in path.parts
    }
    AVAILABLE = tracked | present
    registry = ROOT / 'experiments/registry.csv'
    raw = registry.read_bytes()
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8'))))
    BY_ID = {}
    for index, row in enumerate(rows, 1):
        row['_index'] = index
        BY_ID.setdefault(row['run_id'], []).append(row)
    # 相关说明只建立既有链接，不重算其结论或审计证据。
    reports = {}
    for p in (ROOT / 'analysis').glob('*.md'):
        for rid in set(re.findall(r'20\d{6}T\d{6}Z-[A-Za-z0-9_-]+', p.read_text(encoding='utf-8', errors='replace'))):
            if rid in BY_ID:
                reports.setdefault(rid, []).append(p)
    prs = {}
    receipt = ROOT / 'docs/pr-preparation/publication-receipt.json'
    if receipt.is_file():
        prs = {p['method']: p['url'] for p in json.loads(receipt.read_text(encoding='utf-8'))['pull_requests']}
    # root已实际创建的新PR；仅导航，不改变原实验的归因/依赖/准确率。
    prs.update({method: 'https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/' + str(number)
                for method, number in [('diagnostics', 5), ('prefill', 6), ('top-p', 7),
                                       ('sql-reflection', 8), ('decode3d', 9), ('mixed-attention', 10),
                                       ('skip-computed-h2d', 22), ('compute-order', 22),
                                       ('pr24-main', 24), ('native-quant-cache', 25), ('native-cache-identity', 35),
                                       ('q-fragment-hoist', 23), ('native-safe-default', 48), ('native-silu-vec2', 52), ('prefill-stride', 60), ('lm-head-temperature', 84)]})
    pr_labels = {'lm-head-temperature': 'LM-head温度融合 #84', 'cpu-metadata': 'CPU metadata #1', 'async-token-update': '异步token更新 #2',
                 'pr24-main': 'INT8 gate/up 组合 #24', 'native-quant-cache': '激活量化缓存 #25', 'native-cache-identity': 'native编译缓存身份 #35',
                 'kv-contiguous-copy': '连续页KV工具 #3', 'kv-pitched-copy': '二维SAVE工具 #4',
                 'diagnostics': '诊断配置 #5', 'prefill': 'prefill #6', 'top-p': 'top-p #7',
                 'sql-reflection': 'SQL反射 #8', 'decode3d': '3D decode #9', 'mixed-attention': 'mixed Attention #10',
                 'skip-computed-h2d': 'computed H2D+计算顺序组合 #22', 'compute-order': 'computed H2D+计算顺序组合 #22',
                 'q-fragment-hoist': 'Q fragment #23', 'native-safe-default': '默认关闭风险native #48', 'native-silu-vec2': 'SiLU vec2负结果 #52（已关闭，未合并）'}
    run_pages, buckets = {}, {key: [] for key in GROUPS}
    for rid, records in BY_ID.items():
        slug, hardware = platform(records[0])
        page = TEAM / 'runs' / slug / (rid + '.md')
        run_pages[rid] = page
        body = '# ' + rid + '\n\n平台：' + hardware + '。本页只摘录既有登记；未记录字段不补猜。\n\n'
        for row in records:
            key = group(row)
            buckets[key].append(row)
            body += '## 登记 #' + str(row['_index']) + ' · ' + GROUPS[key][0] + '\n\n'
            if row['status'] in SHORT_ATTEMPTS:
                attempt, change = SHORT_ATTEMPTS[row['status']]
                body += '- **尝试**：' + attempt + '\n'
                body += '- **改动**：' + change + ' 版本、命令和源码见下方原件；' + link(TEAM / 'methods' / (key + '.md'), page, '方法记录') + '。\n'
            elif row['status'] == 'team_main0915_accuracy_pass':
                body += '- **尝试**：复核最新团队 main 的原官方完整105题准确率，与旧99/105分别保留。\n'
                body += '- **改动**：无新增优化；固定0915/tree766b完整603文件、原native14f及34层真实图。' + link(ROOT / (row['artifacts'] + '-control/state.json'), page, '实际版本与后态') + '；' + link(ROOT / (row['artifacts'] + '-control/accuracy-review.json'), page, '逐字原评分器回执') + '。\n'
            elif row['status'] in ('staging_screen_kv_mismatch', 'final_ffn_component_positive_signal', 'rope_model_source_and_parser_failed'):
                body += '- **尝试**：' + {'staging_screen_kv_mismatch': '538 staging关闭回读，官方完整规模两档各两轮筛选。', 'final_ffn_component_positive_signal': '真实权重和编译suffix，对比全M后选行与两gather后FFN。', 'rope_model_source_and_parser_failed': '528 RoPE融合首次真实服务，四语义及实际编译图/来源门。'}[row['status']] + '\n'
                body += '- **改动**：本轮来源与原件见下方证据，限制见方法记录。\n'
            elif row['status'] in ('kv_staging_service_verify1_pass', 'rope_component_recording_failed', 'rope_component_positive_signal', 'final_ffn_dispatch_recording_failed'):
                body += '- **尝试**：' + {'kv_staging_service_verify1_pass': '验证staging保存/恢复接入真实模型的字节、同步与释放。', 'rope_component_recording_failed': '42层RoPE＋KV原数学融合组件首次验证。', 'rope_component_positive_signal': '修记录器后完整验证42层RoPE＋KV融合，与原combo＋KV writer对照。', 'final_ffn_dispatch_recording_failed': '实际末层权重与原编译数学，比较全M后选行与先选行再FFN。'}[row['status']] + '\n'
                body += '- **改动**：本轮源码、版本与原始结果见下方证据；方法边界见' + link(TEAM / 'methods' / (key + '.md'), page, '方法记录') + '。\n'
            elif row['status'] == 'official_restore_pitched_kv_mismatch':
                body += '- **尝试**：验证535 KV保存＋H2D批量恢复组合在原官方两档各四轮的表现；不包含staging primitive。\n'
                body += '- **改动**：main0bf9＋535组合/tree98f4688a，SO14f；' + link(ROOT / (row['artifacts'] + '-control/source-manifest.json'), page, '源码身份') + '，前序实现与边界见' + link(TEAM / 'methods' / (key + '.md'), page, '方法记录') + '。\n'
            else:
                body += '- **尝试**：' + GROUPS[key][1] + '\n'
                body += '- **改动**：相关实现 ' + code_links(key, page) + '；本轮准确变体以原件源码清单为准。\n'
            body += '- **怎么测**：' + how(row) + '\n'
            body += '- **结果**：' + cell(result(row)) + '\n'
            body += '- **是否保留**：' + keep(row) + '\n\n'
            body += '<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>\n\n```json\n' + json.dumps({k: v for k, v in row.items() if not k.startswith('_')}, ensure_ascii=False, indent=2) + '\n```\n\n</details>\n\n'
        folders, links = evidence(records)
        body += '## 原件与说明\n\n'
        body += '- 原始目录：' + ('；'.join(link(p, page, p.name) for p in folders) or '未记录') + '\n'
        for label, paths in links.items():
            paths = list(dict.fromkeys(paths))[:8]
            body += '- ' + label + '：' + ('；'.join(link(p, page, p.name) for p in paths) or '未单列，见原始目录') + '\n'
        related = sorted(reports.get(rid, []), key=lambda p: (rid.split('T')[1][:6] not in p.name, 'framework-experiments' in p.name, len(p.name)))[:3]
        body += '- 相关说明：' + ('；'.join(link(p, page, p.stem) for p in related) or '未记录') + '\n'
        body += '- 完整原登记：' + link(registry, page, 'registry.csv') + '（登记序号见上；同一run可有多个阶段）\n'
        # Preserve hand-authored run notes; only generated pages carry the marker.
        if not page.exists() or page.read_text(encoding='utf-8').startswith(MARK):
            write(page, body)
    table = TEAM / 'experiments.md'
    text = '# 实验总表\n\n唯一登记源：' + link(registry, table, 'registry.csv') + '。共' + str(len(rows)) + '条登记、' + str(len(BY_ID)) + '个run；同一run的不同阶段保留。设备空白显示未记录，不自动归平台。\n\n'
    text += '| 平台 | 登记 | UTC开始 | 方法 | 状态 | 输入/输出/并发/请求 | 原登记摘录 | 每轮短记与原件 |\n|---|---:|---|---|---|---|---|---|\n'
    for row in sorted(rows, key=lambda r: (platform(r)[0], r['_index'])):
        key = group(row)
        text += '| ' + platform(row)[1] + ' | ' + str(row['_index']) + ' | ' + cell(row['utc_start']) + ' | ' + link(TEAM / 'methods' / (key + '.md'), table, GROUPS[key][0]) + ' | ' + cell(status(row)) + ' | ' + '/'.join(row[k] or '未记录' for k in ('input_len', 'output_len', 'concurrency', 'num_prompts')) + ' | ' + cell(result(row, 110)) + ' | ' + link(run_pages[row['run_id']], table, row['run_id']) + ' |\n'
    write(table, text)
    for key, (title, description, methods) in GROUPS.items():
        records = buckets[key]
        if not records:
            continue
        page = TEAM / 'methods' / (key + '.md')
        text = '# ' + title + '\n\n' + description + '\n\n'
        text += '相关代码：' + code_links(key, page) + '。\n\n'
        text += '相关方法PR：' + ('；'.join('[' + pr_labels.get(method, method) + '](' + prs[method] + ')' for method in methods if method in prs) or '未记录') + '。\n\n'
        text += '下列是既有登记摘要，不叠加单项收益、不把诊断当端到端或完整准确率。完整条件沿每轮原件查阅。\n\n'
        for slug in ('bi-v150', 'cpu', 'unrecorded'):
            subset = [r for r in records if platform(r)[0] == slug]
            if not subset:
                continue
            text += '## ' + platform(subset[0])[1] + '\n\n'
            for row in subset:
                text += '- ' + link(run_pages[row['run_id']], page, row['run_id']) + '（登记#' + str(row['_index']) + '）：' + cell(result(row, 150)) + ' **是否保留：** ' + keep(row) + '\n'
            text += '\n'
        if key == 'night-kernel-counters':
            text += '\n## 后续完整封存\n\n在A/B结束后的GPU空窗已补封两轮完整原件，完整包留远端。独立回执：[Prefill完整封存](../../experiments/profiles/20261025T170235660423Z-prefill-one-kernel-counters/full-seal-receipt.json)、[GQA完整封存](../../experiments/profiles/20261025T170652502004Z-gqa-one-kernel-counters/full-seal-receipt.json)。旧小包index、原日志与原登记未改；完整包SHA与全文件SHA在回执中，不能把补封解释为工具重跑或计数恢复。\n'
            text += '## 2026-10-26 本地只读补充\n\nPrefill报告虽无法由CLI导入，但SQLite保留1条kernel活动和57条EVENT，均以iterator/coorelationid=934关联；名称`kernel_biv150_prefill_normalized`、grid128×2×1、block512、VRF114/SRF104/shared32768与本run原current基线BM128/T64/w8、M2047/KV16384相符。[原值导出](../../analysis/20261025T170235-prefill-raw-events.json)保留全部事件、配置对照和报告SHA；原SQLite未修改。仅支持来源匹配，报告没有cubin/hash或动态参数，不能宣称二进制逐字绑定。\n\nDEVICE_INFO、METRIC与METRIC_DATA为空且wrapper exit -11；已有材料缺计数域、聚合、单位和metric公式，事件数值仍待解释。原shared-store conflicts130752336/transactions126742528、LLC两core hit合计24899406/req24998649、total_cycles803635136/active_cycles776790603均不转换为冲突率、整轮命中率、占用率或收益；time8363934也保留原值。没有修数据库、重跑或新方案，原工具失败与所有timing禁作成绩的结论不变。此补充不改既有登记原文。\n'
        write(page, text)
    for slug, label in [('bi-v150', '天数 BI-V150'), ('c500', '沐曦－曦云 C500'), ('cpu', 'CPU'), ('unrecorded', '未记录平台')]:
        page = TEAM / 'platforms' / (slug + '.md')
        subset = [r for r in rows if platform(r)[0] == slug]
        text = '# ' + label + '\n\n'
        text += ('现有登记' + str(len(subset)) + '条。打开' + link(table, page, '唯一实验总表') + '查看平台列和每轮原件。\n\n') if subset else '当前registry无该平台登记，不引用其它平台成绩。\n\n'
        text += '\n'.join('- ' + link(TEAM / 'methods' / (key + '.md'), page, GROUPS[key][0]) for key in GROUPS if any(group(r) == key for r in subset))
        write(page, text)
    archive = TEAM / 'archive-index.md'
    write(archive, '# 详细记录与 AI 交接归档入口\n\n这里只建立入口，不搬动原文件，固定脚本/manifest路径继续有效。\n\n' + '\n'.join('- ' + link(ROOT / path, archive, title) for path, title in [
        ('docs/agent-work-index.md', '子智能体交接索引'), ('docs/agent-work', '各智能体完整工作记录'),
        ('CURRENT_WORK.md', '当前工作与API交接'), ('analysis', '详细研究、过程稿与长报告'),
        ('analysis/source', '独立审计JSON、源码摘录与机器记录'), ('experiments/framework', '框架实验原件'),
        ('experiments/official', '官方吞吐原件'), ('experiments/accuracy', '准确率原件'),
        ('experiments/source-audits', '实际安装源码只读取证'), ('docs/pr-preparation', '早期PR材料与组合证据'),
        ('docs/pr-rebuild', '原始基线与方法PR重建材料'), ('docs/github-publications', '完整发布回执')
    ] if available(path)))
    home = TEAM / 'README.md'
    write(home, '# 团队实验导航\n\n先看' + link(table, home, '唯一实验总表') + '，再打开每轮短记和原始证据。登记源保持为registry，不另造成绩或补猜缺字段。\n\n## 按平台\n\n' + '\n'.join('- ' + link(TEAM / 'platforms' / (slug + '.md'), home, label) for slug, label in [('bi-v150', '天数 BI-V150'), ('c500', '沐曦－曦云 C500'), ('cpu', 'CPU'), ('unrecorded', '设备字段未记录')]) + '\n\n## 按方法\n\n' + '\n'.join('- ' + link(TEAM / 'methods' / (key + '.md'), home, GROUPS[key][0]) for key in GROUPS if buckets[key]) + '\n\n' + link(archive, home, 'AI交接、详细SHA及过程稿归档入口') + '\n\n更新：`python scripts/build_team_view.py`。仅重建本目录自动视图，不修改登记和证据。')
    assert registry.read_bytes() == raw
    write(TEAM / 'generated-index.md', '# 自动视图来源\n\n登记：`experiments/registry.csv`；SHA256 `' + hashlib.sha256(raw).hexdigest() + '`。\n\n共' + str(len(rows)) + '条登记、' + str(len(BY_ID)) + '个run。程序只读取目录/既有说明建立链接，不重验实验。\n')
    print(json.dumps({'registry_records': len(rows), 'unique_runs': len(BY_ID), 'generated_files': len(GENERATED), 'entry': 'team/README.md', 'registry_unchanged': True}, ensure_ascii=False))


# 2026-10-29 down GROUP_M4 与 W8A16 归档短记录
for _k,_a,_c,_r,_d in [
 ('shape_gemm_groupm4_entry_interface_failed', '验证GROUP_M4候选组件入口能否进入原生产provided-linear测试。', '只运行已有组件owner；入口接口失败，未开始数值/性能计时。', '入口初始化异常，未计时', '保留失败原件；不当数值错误或性能负结果。'),
 ('shape_gemm_groupm4_component_positive', '用真实42层权重与两种BF16图案验证down GROUP_M4组件。', '自研JIT内核将CTA分组映射GROUP_M8改为GROUP_M4；生产provided-linear callback、tile与数学主体保持受测版本。', '两pattern逐元素相等及FP64/Graph/side/RNG门通过；A/B分别约省0.960829%与0.892794%，仅组件信号。', '保留为待官方接线候选；不外推为模型或官方收益。'),
 ('shape_gemm_groupm4_official_staging_failed', '验证GROUP_M4官方4K候选能否通过冻结源暂存门。', '沿用原官方owner，只记stage源映射异常；未启动benchmark。', 'source_maps暂存失败，计算前退出。', '保留接口失败证据；不能归为性能或数值结果。'),
 ('shape_gemm_groupm4_official_selector_failed', '验证GROUP_M4官方selector首暖回执与编译身份门。', '沿用官方路径；selector接口异常，未进入benchmark计时。', '接口异常，未获得性能比较。', '保留失败证据；不当作候选性能失败。'),
 ('shape_gemm_w8a16_cpu_weight_screen', 'CPU筛查down W8A16 K128量化权重与有限合成输出误差。', '仅CPU评估对称分组量化误差，不运行CUDA、模型或官方准确率。', '42层真实down权重最大relative L2为0.007979；仅有限合成输出筛查，不能代表比赛准确率或吞吐。', '仅保留研究结果；未启用量化，不进入比赛候选。'),
 ('shape_gemm_w8a16_compile_interface_failed', '检查W8A16 down候选能否用当前生产compile/config接口编译。', '编译调用接口异常，未取得可比较内核。', '编译接口失败，无性能/数值结果。', '保留接口失败原件；不判量化候选快慢。'),
 ('shape_gemm_w8a16_timing_record_failed', '验证W8A16 down候选短测结果回执是否完整。', '复用受测候选，但计时结果记录接口异常。', '数值/Graph/side等五项门通过，只有ABBA计时回执缺失；不作性能判断。', '保留诊断原件；不把接口异常写作性能结论。'),
 ('shape_gemm_w8a16_component_negative', '比较真实M64 down生产MM-out与W8A16 K128组件的完整Graph。', '候选采用权重分组量化与BF16 dot；A/B完整输出和ABBA计时。', 'A 0.0588357ms、B 0.6471999ms；五项门通过，候选约11倍慢，达到停止条件。', '保留负结果；停止W8A16组件路线，不接模型。'),
 ('shape_gemm_groupm4_official_first_warm_negative_stop', '验证GROUP_M4生产接线的官方4K吞吐净影响。', 'G4为已测自研JIT CTA分组映射；源、两库及DB均恢复，selector/config有效。', '原官方设置RUNS=4/SKIP_FIRST=1；本次两轮观察，512 SUCCESS；KV计数不匹配。', '首暖负后按预设停止；不完整四轮/16K/105，不合并或更新基线；保留非因果限制。'),
 ('shape_gemm_bm32bn32_compile_handles_uninitialized', '核对小CTA配置能否取得完整编译资源句柄。', '只尝试固定BM32/BN32/BK128编译筛选，不进入计时。', 'warmup资源字段未初始化导致停止；无数值或性能结论。', '保留接口/回执失败证据；待资源句柄闭合后再评估是否计时。'),
 ('shape_gemm_bm32bn32_component_negative', '检验M64 down采用BM32/BN32/BK128是否减少完整组件时间。', '只改tile分块，原数学与生产callback保留；完整Graph计入结果。', '五项数值门通过，compile/RNG/清理门通过；完整Graph慢53.669168%。', '停止该固定点，不接官方或扩扫矩阵。'),
]:
    BATCH_RESULTS[_k]=('结果与限制见原始bundle及登记结论。',_d,_r,'本条所列source/result/manifest原件完整打包并按SHA256分块；组件/CPU筛查与官方成绩分开。')
    SHORT_ATTEMPTS[_k]=(_a,_c)

for _k,_a,_c,_r,_d in [
 ('shape_gemm_direct_launch_component_positive','比较原SDK GROUP_M8、GROUP_M4 normal-JIT与同一已编译核direct launch的42层down组件。','C仅省掉已选kernel的host wrapper路径；数学/kernel/真实权重不变，两种输入各一次ABCCBA。','C对B两种pattern wall均值分别快2.802766%/2.798879%，GPU Event近似持平；84个输出及FP64、输入/RNG通过，Graph仅三臂互比、side仅layer0；非整模收益。','保留为host提交组件信号；不外推整模或官方收益，原“Bhost>A”假说被否决。'),
 ('shape_gemm_direct_launch_official4k_small_positive_kv_mismatch','检验direct C/GROUP_M4候选在原官方4K设置下的端到端表现。','沿用原官方benchmark与服务参数，仅声明的生产down wrapper候选；首暖有正信号后完成四轮。','四轮/1024请求完成：总吞吐5244.67/6450.53/6723.84/6723.28；首暖对照+0.1425%，弃首均值+0.0714%。KV548432对548336不匹配。','仅保留小幅观察；不作严格因果/稳定收益，不更新基线、不合并；16K和准确率另判。'),
 ('shape_gemm_direct_launch_official16k_driver_pin_preparation_failed','准备同候选的原官方16K入口并验证driver身份门。','运行owner准备入口；case_driver SHA未与owner pin一致，值未改也未实际开始benchmark。','启动owner Python后立刻因driver/common SHA门退出；无服务/benchmark子进程、无GPU运行和吞吐数据。','保留入口准备失败原件；与后续冻结修正版本及16K实测分开记录。'),
 ('shape_gemm_direct_launch_official16k_first_warm_negative_stop','检验G4直调C在原官方16K负载上的整体表现。','原服务与评测参数不变；对PR105同档首暖筛选，负结果提前停止。','冷轮4361.39、首暖4825.32 tok/s；256请求成功，首暖观察−0.188853%，KV548384对548288不同。','停止C，不合并、不更新基线；不是完整四轮成绩，105条件包未运行。'),
 ('shape_gemm_direct_launch_samekernel_component_positive','比较原SDK GROUP_M8与其同一CompiledKernel的直接调用。','保留原GPU核及数学，只减少LibEntry处理；42层真实权重、两pattern各一次ABBA。','wall观察省7.755105%/6.109667%，Event近似；84数值门、D换值Graph对fresh eager A、side0/41及输入/RNG通过。','保留D进入生产对照；不称官方收益，A Graph快照已被eager覆盖，未保存全输出数组。'),
]:
    BATCH_RESULTS[_k]=('结果与限制见原始bundle及登记结论。',_d,_r,'原始文件按清单SHA核验并完整打包；性能组件、官方成绩与入口准备失败分开。')
    SHORT_ATTEMPTS[_k]=(_a,_c)



# 2026-10-29 Direct-G8 官方4K资格失败与完整负结果
for _k,_a,_c,_r,_d in [
 ('shape_gemm_direct_g8_official_prebenchmark_marker_failed','验证Direct-G8官方4K入口能否在服务启动后完成首请求前资格检查。','冷路径尚未触发真实GEMM，driver因预期direct marker缺失而停止；benchmark未开始。','服务启动后资格门退出，0轮benchmark；无数值或吞吐结论。','保留入口时序失败原件；不归类为kernel正确性或性能负结果。'),
 ('shape_gemm_direct_g8_first_round_bind_failed','验证Direct-G8官方4K冷轮后的实际kernel绑定身份。','首轮256请求沿SDK fallback完成；首条SUCCESS后未取得Direct-G8 receipt，supervisor停止后续轮次。','冷轮6005.43 tok/s，但候选未启用，不作为候选吞吐结论。','保留接口绑定失败证据；不归类为数值错误。'),
 ('shape_gemm_direct_g8_transport_base_qualification_failed','验证Direct-G8官方4K候选冻结source运输身份。','CPU暂存完成815文件后，qualification错误地把341运输基底与f165性能基线比较；GPU未启动。','pre-GPU资格失败，无服务、benchmark、数值或吞吐结论。','保留准备失败原件；运输基底与测量基线分开记录。'),
 ('shape_gemm_direct_g8_official4k_full_negative','检验Direct-G8实际绑定后的官方4K端到端影响。','原官方参数及服务流程完成四轮，首轮actualDirect receipt有效；DB/source/两SO及stack清理通过。','四轮5418.24/6519.84/6726.82/6441.8 tok/s；弃首均6562.82，对PR105基线6627.816667为−0.980665%。KV548432对548336不匹配。','保留官方完整负均值；不称严格因果收益，不进入16K/105、不合并或更新基线。'),
]:
    BATCH_RESULTS[_k]=('结果与限制见原始bundle及登记结论。',_d,_r,'原始成员、清单与压缩分块按SHA256核验；入口资格失败与完整官方负结果分开。')
    SHORT_ATTEMPTS[_k]=(_a,_c)


# 2026-10-29 BM32/BN32 与宽转置tile的CPU/组件后续
BATCH_RESULTS.update({
    'shape_gemm_bm32bn32_warp32_cpu_metadata_failed': ('Triton导入成功但distribution metadata查询失败；未形成有效编译结果。', '保留CPU环境失败原件，不判layout、数值或性能。', 'CPU环境查询失败', '仅CPU编译准备；importlib.metadata.version失败，GPU未启动。'),
    'shape_gemm_bm32bn32_warp32_layout_no_go': ('w16/w32编译成功，但warp32未增加有效坐标工作；layout筛选NO-GO。', '固定点停止；无GPU数值或性能结论。', 'CPU编译成功，layout NO-GO', '同源pair仅num_warps不同；layout/TTGIR审查发现新增warp不产生独立输出/MMA工作。'),
    'shape_gemm_transpose_wide_cpu_compile_pass': ('固定宽转置tile CPU编译及ASM筛查通过；未测数值或性能。', '保留为编译筛查结果，不据此授予GPU或生产资格。', 'CPU编译通过', 'M64 down，BM128/BN64/BK128，w32/s2；CPU-only，无设备运行。'),
    'shape_gemm_transpose_wide_metadata_gate_failed': ('组件计时前metadata断言失败；原A/B实际use_sme均为7，worker误要求15。', '保留入口门失败；无数值/性能结论，不标为kernel错误。', 'metadata契约失败，未计时', 'BI-V150组件准备阶段退出；实际两臂metadata均为7，未进入数值或ABBA计时。'),
    'shape_gemm_transpose_wide_component_negative': ('42层真实权重、两种图案、ABBA完成；数值/Graph/side通过。B Event 3.184987ms对A 2.324920ms慢36.9934%。', '停止此实现；不进官方/105、不合并或更新基线。', '组件正确性通过，性能明显负', 'M64 down固定宽转置tile，42层真实权重；两pattern完整ABBA，实际use_sme 7/7，恢复清理通过。'),
})
SHORT_ATTEMPTS.update({
    'shape_gemm_bm32bn32_warp32_cpu_metadata_failed': ('检查BM32/BN32配置的CPU编译器版本与可用性。', '仅metadata查询失败，无有效编译或GPU尝试。'),
    'shape_gemm_bm32bn32_warp32_layout_no_go': ('比较w16与w32配置是否产生独立且有用的warp工作分配。', '两臂同源、仅num_warps不同；实际编译后layout未显示新增有效工作，停止。'),
    'shape_gemm_transpose_wide_cpu_compile_pass': ('对固定宽转置tile做CPU-only编译与ASM检查。', '仅编译筛查，不把未初始化资源字段当作设备资源或性能证据。'),
    'shape_gemm_transpose_wide_metadata_gate_failed': ('准备真实42层M64 down权重组件的宽转置tile计时。', 'A/B实际use_sme=7，worker错误期待15，未开始数值或计时。'),
    'shape_gemm_transpose_wide_component_negative': ('验证宽转置tile能否改善M64 down的42层完整组件时间。', '固定BM128/BN64/BK128、w32/s2、CTA1；真实权重和生产数学不变，完整ABBA。'),
})

# 发布前更正：2026-10-29 warp32/宽转置新增5run事实表述
BATCH_RESULTS.update({
 'shape_gemm_bm32bn32_warp32_cpu_metadata_failed': ('实际BM64/BN64/BK128；w16编译成功并有6项产物，之后Triton distribution version查询因metadata缺失失败，w32未执行。', '保留环境查询失败；父归档目录名称bm32bn32不代表本次tile配置。', 'w16编译后metadata查询失败', 'BM64/BN64/BK128，CPU-only；只有w16已运行编译，w32未执行。'),
 'shape_gemm_bm32bn32_warp32_layout_no_go': ('实际BM64/BN64/BK128，w16/w32均CPU编译成功；warp32布局未增加有效坐标工作，筛选NO-GO。', '停止此配置；父归档目录名bm32bn32不代表tile，无GPU结果。', 'CPU编译完成，layout NO-GO', '同源w16/w32 pair，BM64/BN64/BK128；编译后审查布局工作映射。'),
 'shape_gemm_transpose_wide_cpu_compile_pass': ('BM128/BN64/BK128宽转置tile CPU编译与ASM检查通过；没有GPU或性能结果。', '仅保留编译筛查；不授予数值、组件或生产资格。', 'CPU编译通过', 'CPU-only编译检查，BM128/BN64/BK128。'),
 'shape_gemm_transpose_wide_metadata_gate_failed': ('首轮组件在数值与计时前因worker错误要求metadata.use_sme=15退出；A/B实际均为7。内核配置未被改成15。', '保留worker metadata期望值门错误；无数值或计时结论。', 'metadata期望值错误，未计时', '组件准备失败；原A/B的metadata.use_sme均为7，worker误要求15。'),
 'shape_gemm_transpose_wide_component_negative': ('42层真实权重、两组输入、ABBA完成；数值/Graph/side通过。B Event均值3.184987ms，对A 2.324920ms慢36.9934%。', '停止该实现；不进官方/105，不合并或更新基线。', '组件正确性通过，性能明显负', 'M64 down固定宽转置tile、42层真实权重；两组输入、ABBA完整，实际metadata.use_sme为7/7，恢复清理通过。'),
})
SHORT_ATTEMPTS.update({
 'shape_gemm_bm32bn32_warp32_cpu_metadata_failed': ('检查BM64/BN64/BK128下w16/w32候选的CPU编译可行性。', 'w16成功编译并保存6项产物；随后distribution version查询失败，因此w32未执行。父归档目录名不代表tile配置。'),
 'shape_gemm_bm32bn32_warp32_layout_no_go': ('比较BM64/BN64/BK128下w16和w32布局是否增加有效warp工作。', '两臂均编译；w32未增加有效坐标工作，layout筛选NO-GO。'),
 'shape_gemm_transpose_wide_cpu_compile_pass': ('对固定宽转置tile做CPU-only编译和ASM检查。', 'BM128/BN64/BK128；仅编译筛查，无设备性能结论。'),
 'shape_gemm_transpose_wide_metadata_gate_failed': ('准备42层M64 down宽转置组件测量。', 'worker错误要求metadata.use_sme=15，而原A/B均为7；不是kernel配置变更，未开始数值/计时。'),
 'shape_gemm_transpose_wide_component_negative': ('检验宽转置tile对M64 down完整42层组件耗时的影响。', '固定BM128/BN64/BK128、w32/s2、CTA1；真实权重与生产数学不变，两组输入做完整ABBA。'),
 'shape_gemm_native_gqa_grid_order_negative': ('比较native GQA原CTA顺序与单一grid-order置换的N64/S2组件耗时。', '真实production macro1与同run候选32-call ABBA；九类正确性/Graph/side/RNG门通过，event慢0.2253%，wall慢0.0941%，停止。'),
 'profile_diagnostic_reader_gate_failed_before_benchmark': ('分析PR105原官方16K单轮诊断的真实热点和native GQA覆盖。', 'benchmark前reader将真实overlap_v=true错判为false，0请求/0吞吐；保留资格失败，不归为模型错误。'),
})

BATCH_RESULTS.update({
 'shape_gemm_native_gqa_grid_order_negative': ('N64/S2 production GQA组件九类门通过；32-call ABBA event慢0.2253%、wall慢0.0941%。', '保留小幅负结果并停止该grid-order候选；不外推模型/官方成绩。', '组件通过，性能小幅负', 'BI-V150、同run production macro1对单一CTA/grid置换，32-call ABBA；非模型或官方性能测量。'),
 'profile_diagnostic_reader_gate_failed_before_benchmark': ('PR105 16K单轮诊断在预检阶段退出；生产GQA receipt因overlap_v期望值错误被拒。', '保留reader资格失败；0请求，不作为模型数值错误或性能结果。', '诊断预检失败，未启动benchmark', '原官方16K输入16384/输出1024/并发64/128请求入口；GQA shape/SO/stride/capture marker reader gate在benchmark前拒绝。'),
})

# 2026-10-29 PR105 16K diagnostic and prefill i32 CPU compile attempts.
GROUPS['prefill-i32-offset'] = (
    'Prefill i32 offset CPU 编译筛查',
    '当前受测组件为单层M2048/KV16384、BM128/BQ16/page16的私有i32相对地址候选。四次运行中前三次分别因GQA依赖缺失、scope断言和结果记录异常而未形成A/B数值/计时结论；第四次组件数值门通过（FP64为采样），但Event慢10.63%、wall慢10.21%，按负向停止。此前CPU机制资源差异没有转成吞吐收益。只保留实验记录，不接入生产、不授予完整模型、准确率或官方资格。', [])
CODE['prefill-i32-offset'] = []
BATCH_RESULTS.update({
 'profile_diagnostic_completed_posthoc_fresh_fx_missing': ('PR105 16K冷态诊断完成128/128；原件source/SO/DB/collector清理通过。posthoc返回diagnostic_incomplete，fresh FX图证缺项；仅覆盖诊断，不是官方分数。', '保留单次冷态profile和原始trace；不补伪造FX证据，不当作官方成绩或稳态收益。', '诊断完成，FX证据不完整', 'BI-V150 PR105树f1658、814源文件；16K输入/1024输出/128请求；driver/owner/collector为0，posthoc为1，native GQA生产回执覆盖。'),
 'prefill_i32_v2_compile_attrs_failed': ('i32-offset v2 CPU-only编译在set_arg_attr失败：ABI attrs把整数值解成list，Triton拒绝；未进入正常kernel编译。静态7项guard通过但锁定BM128/BQ16/page32，和目标BM256/BQ32/page16不符。', '保留编译接口失败，不称kernel数值/性能负；guard不适用于实际目标形状。', 'CPU编译因ABI attrs停止', '仅CPU、CUDA API未调用；真实编译trace显示set_arg_attr收到错误的list值。目标BM256/BQ32/page16，旧guard为BM128/BQ16/page32。'),
 'prefill_i32_v3_normal_identity_mismatch': ('i32-offset v3 CPU-only在A normal kernel身份门停止：未复现171100 selected normal hash，B候选未编译。静态guard仍是BM128/BQ16/page32，不适用于实际目标BM256/BQ32/page16。', '保留A身份门失败；不放宽normal identity，也不据此判断候选数学或性能。', 'A normal身份不匹配，停止编译', '仅CPU、CUDA API未调用；运行在B编译前退出。目标BM256/BQ32/page16，旧guard为BM128/BQ16/page32。'),
 'prefill_i32_v5_normal_identity_mismatch': ('i32-offset v5 CPU-only完成A normal编译，但身份仍未匹配171100 selected kernel；保留严格身份门拒绝。', '保留为CPU身份失败；无GPU、模型数值、吞吐或生产资格。', 'CPU编译完成，A身份失败', 'CPU-only；A normal identity不匹配，未授予生产或设备资格。'),
 'prefill_i32_v6_cpu_mechanism_diagnostic': ('i32-offset v6仅作CPU机制诊断：两臂normal/Q-fragment编译及proof通过，但A生产selected hash仍不匹配。资源观察A SGPR104/VGPR113/spill4，B SGPR85/VGPR112/spill0，shared 65536B。', '机制proof不是数值或性能结果；明确不授生产、GPU或官方资格，保留证据并停止。', 'CPU机制诊断完成，未获生产资格', 'normal identity未匹配；仅CPU编译/静态proof，无运行或吞吐数据。'),
})
SHORT_ATTEMPTS.update({
 'profile_diagnostic_completed_posthoc_fresh_fx_missing': ('对PR105 16K/128请求运行一次带采集器的冷态覆盖诊断。', '128/128完成；driver/owner/collector成功并完成清理；posthoc缺fresh FX图证，非官方性能测量。'),
 'prefill_i32_v2_compile_attrs_failed': ('用i32相对offset候选尝试重现171100的normal编译配置并检查编译门。', 'set_arg_attr因attrs值解码为list而停止；旧guard的BM128/BQ16/page32与目标BM256/BQ32/page16不符。'),
 'prefill_i32_v3_normal_identity_mismatch': ('修正attrs解码后重试同一CPU编译身份门。', 'A normal identity未重现171100 selected hash，B未编译；旧guard与目标BM256/BQ32/page16不符。'),
 'prefill_i32_v5_normal_identity_mismatch': ('验证v5按生产模块名修正后的A normal编译身份。', 'A仍未匹配171100 selected hash；严格拒绝，无GPU或性能结论。'),
 'prefill_i32_v6_cpu_mechanism_diagnostic': ('在不放宽生产身份门的前提下诊断i32 offset/Q-fragment编译机制。', '两臂编译与CPU proof通过，但A selected identity仍不匹配；不授GPU/生产资格。'),
})
GROUPS['prefill-i32-offset'] = (
    'Prefill i32 offset 组件筛查',
    'M2048/KV16384、BM128/BQ16/page16私有单层组件。前三次入口/harness失败均未形成数值/计时结论；第四次通过单shape正确性门（FP64采样），但Event慢10.63%、wall慢10.21%，已停止。CPU资源变化不代表吞吐收益；不接入生产或官方。', [])
BATCH_RESULTS.update({
 'prefill_i32_component_gqa_dependency_missing': ('入口没有传固定GQA依赖，EngineArgs初始化时报缺少native GQA库；未进入A/B、数值或计时。', '保留依赖接线失败，不称候选数值/性能失败。', '依赖入口失败，未测数值/性能', 'BI-V150私有组件入口；source tree f1658b69，原native与DB恢复。'),
 'prefill_i32_component_scope_assertion_failed': ('组件在scope断言停止；worker预设配置与当时selected compile scope不符，未进入A/B、数值或计时。', '保留scope/harness失败，不判候选正确性或性能。', 'scope断言失败，未测数值/性能', 'BI-V150私有单层组件；未形成A/B结果，source/native/GQA/DB恢复。'),
 'prefill_i32_component_result_recording_failed': ('组件完成A/B编译与Q-fragment proof后，结果记录代码访问未定义属性并退出；未形成数值/计时。', '保留记录器异常，不判候选数值或性能。', '结果记录器失败，未测数值/性能', 'BI-V150私有组件准备；A/B数值和计时未产生，环境恢复通过。'),
 'prefill_i32_component_negative': ('M2048/KV16384单层组件正确性门通过（FP64采样）；ABBA Event 8.347575→9.235266ms（+10.63%），wall 8.441216→9.303357ms（+10.21%）。', '保留正确性与负性能证据，停止i32候选，不接入生产或官方。', '单层数值通过、性能负向停止', 'BI-V150私有单shape attention组件；完整输出/Graph等门及ABBA通过，FP64仅采样；不代表完整模型或官方吞吐。'),
})
SHORT_ATTEMPTS.update({
 'prefill_i32_component_gqa_dependency_missing': ('尝试启动i32单层attention组件。', 'EngineArgs因未提供native GQA依赖而退出；没有A/B数值或性能结果。'),
 'prefill_i32_component_scope_assertion_failed': ('修复依赖接线后捕获组件scope并执行原固定scope断言。', '断言不符后停止；无A/B数值/性能结果，不据此判候选。'),
 'prefill_i32_component_result_recording_failed': ('以实际scope准备两臂并执行既定组件门。', '结果记录器异常；无数值/计时结果，保留原错误与恢复证据。'),
 'prefill_i32_component_negative': ('同ABI对比原kernel与i32相对offset kernel，单shape ABBA。', '正确性门通过（FP64采样），Event慢10.63%、wall慢10.21%；停止候选，不进生产。'),
})
GROUPS['shape-gemm'] = ('BI-V150特定形状GEMM', GROUPS['shape-gemm'][1] + ' 另有PR105 16K单次profile诊断完成128请求，posthoc缺fresh FX图证，非官方分数。', GROUPS['shape-gemm'][2])

# 2026-10-29 native GQA S8 accuracy + base2 CPU compile batch.
GROUPS['prefill-base2'] = ('Prefill base2 CPU编译筛查', '尝试将log2e并入score scale、将P/alpha改用exp2；本批两次入口/编译工具失败后，063736 CPU编译完成并显示乘法数减少，但exp条数未变、寄存器略增。仅机制/编译证据，没有GPU数值或性能结论；S8准确率与官方4K另列。', [])
BATCH_RESULTS.update({
 'native_gqa_s8_official_4k_four_rounds_complete': ('4K四轮6161.33/6506.76/6723.79/6552.71 tok/s；暖均6594.42，对PR105 6627.82低0.5039%，KV548384对548336不同。', '保留4K完整实测观察；KV不匹配，不作严格因果或基线更新。', '4K四轮完成，暖均小幅低于对照', 'BI-V150官方4K、四轮各256成功；S8自然eager_only；候选/参考KV差48。'),
 'native_gqa_s8_accuracy105_pass_s8_not_exercised': ('原105题101/105（96.1905%），达到至少100正确门；S8库安装有效但N30/S8 selected/captured均未出现。', '准确率门通过；batch8未覆盖S8 kernel执行，不能据此称S8分支正确性已验证。', '原105准确率通过，S8 not_exercised', 'BI-V150原105题、batch8；105成功review/stop，0传输错误/截断/空答案；S8 natural activation not_exercised。'),
 'prefill_base2_cpu_entry_missing_script': ('CPU入口引用的run_compile.py路径不存在；owner启动前失败，无编译产物或设备结果。', '保留入口路径错误；不归为候选数值/性能失败。', 'CPU入口失败，未编译', 'CPU-only；入口找不到run_compile.py，未触碰GPU。'),
 'prefill_base2_q_debug_source_reader_path_error': ('CPU编译器把源码字符串误交给Path.read_text作路径，触发文件名过长；B Q-hoisted未编译。', '保留source-reader工具错误；非kernel失败，无GPU或性能结论。', 'CPU编译中断，工具读源码路径错误', 'CPU-only；normal B有ASM产物，Q-hoisted B缺失；无数值/性能结果。'),
 'prefill_base2_cpu_compile_mechanism_complete': ('A/B CPU编译完成；SGPR spill 4→3、VGPR113→115、ASM乘法84→65而exp仍20。', '保留为换底机制证据；未上GPU，无数值/性能或生产资格。', 'CPU编译通过，未测性能', 'Q-hoisted A/B编译；仅静态指令/资源观察，不推出吞吐收益。'),
})
SHORT_ATTEMPTS.update({
 'native_gqa_s8_official_4k_four_rounds_complete': ('检验N30/S8生产接入在官方4K参数下的端到端影响。', '保留PR105 producer/N30 S8 producer；仅BF16 Q stride=2048命中，其余fallback。'),
 'native_gqa_s8_accuracy105_pass_s8_not_exercised': ('按原batch8及服务参数运行完整105题准确率评估。', 'S8库身份安装有效，但自然负载没有触发N30/S8 selected或capture；准确率不能充当S8分支覆盖。'),
 'prefill_base2_cpu_entry_missing_script': ('尝试运行base2候选CPU编译入口。', '入口引用的run_compile.py不存在，启动前退出；无编译、GPU或性能结果。'),
 'prefill_base2_q_debug_source_reader_path_error': ('修复入口后检查base2 normal与Q-hoisted两臂CPU编译。', '源码读取helper把源码内容当文件路径，导致路径过长；Q-hoisted B未编译，无数值/性能结论。'),
 'prefill_base2_cpu_compile_mechanism_complete': ('编译base2换底A/B并检查生成ASM与寄存器/溢出。', 'spill 4→3、VGPR113→115、mul84→65、exp维持20；CPU-only机制观察，不代表GPU性能。'),
})


BATCH_RESULTS.update({
 'prefill_base2_component_entry_keyerror': ('M2048/KV16K组件worker引用不存在kw_a[key_ptr]，实际ABI为key_cache_ptr/value_cache_ptr；selected_calls=0，无timings。','保留入口接线失败；不归为候选数值或性能失败。','组件入口KeyError，未计时','BI-V150固定合成M2048/KV16K；worker入口失败，零benchmark。'),
 'prefill_base2_component_negative': ('ABBA Event 6.5530→6.6058ms（慢0.8052%），wall 6.6458→6.6968ms（慢0.7673%）。','保留负结果并停止；无生产或官方资格。','局部组件负结果','BI-V150合成M2048/KV16K，暖JIT ABBA，两臂各2×16次。'),
 'native_gqa_s8_short_kv_component_positive': ('KV16K Event 1.02895→0.76604ms，KV4K 0.27377→0.21720ms；wall两档均同步下降。','保留N30/S8组件正向观察；不授官方、准确率或长度分流资格。','两档局部组件正向','BI-V150 N30/S8，KV16K与4K分开ABBA；非官方吞吐。'),
})
SHORT_ATTEMPTS.update({
 'prefill_base2_component_entry_keyerror': ('检查base2候选的M2048/KV16K组件入口接线。','worker读取不存在的key_ptr，实际ABI名为key_cache_ptr/value_cache_ptr；没有进入计时。'),
 'prefill_base2_component_negative': ('测试exp2换底在固定合成attention组件上的代价。','只改变log2(e)并入score scale及P/alpha换exp2；其余Q fragment与ABI固定。'),
 'native_gqa_s8_short_kv_component_positive': ('比较N30/S8 native producer在KV16K与KV4K下的组件时延。','固定producer和Q stride，两档分别ABBA；未增加长度分流。'),
})
GROUPS['prefill-base2'] = ('Prefill base2 CPU编译筛查', 'CPU机制证据之外，M2048/KV16K单层入口因ABI参数名KeyError未计时，exp2换底局部ABBA为负（Event慢0.8052%、wall慢0.7673%）。保留入口失败与负结果，不作生产或官方资格。', [])
GROUPS['native-gqa-s8'] = ('native GQA S8生产接入', 'PR105 producer新增N30/S8；仅BF16且Q stride=2048命中，其余fallback。16K官方四轮正向、4K官方观察略负且KV不匹配；本批KV16K/4K两档局部组件正向。原105为101/105通过，但batch8的S8为not_exercised；保持PR105基线，不作严格因果、长度分流或新基线。', [])


# 2026-10-30 storage/profile/Q32：本批登记的精确分类与保留决定。
_STORAGE_Q32_RUNS = {'20261029T220427329020Z-native-k8-storage-snapshot': ('storage-snapshot', '只保留局部证据，服务结论见同方法16K记录。'), '20261029T220702833593Z-mixed-a-16k-profile': ('mixed-warm-profile', '保留工具入口失败；不是模型错误。'), '20261029T222344850512Z-mixed-a-16k-profile': ('mixed-warm-profile', '保留热点证据；不作为官方吞吐或准确率。'), '20261029T224653126532Z-native-k8-storage-snapshot-b-16384-four-rounds': ('storage-snapshot', '保留小幅观察，不升级基线；完整准确率未测。'), '20261029T233910926379Z-q32-causal-interior-component': ('q32-causal-interior', '保留入口失败证据；此轮未执行候选内核。'), '20261029T234221231370Z-q32-causal-interior-component': ('q32-causal-interior', '停止候选，不进入计时或服务。候选未改动团队main。')}
GROUPS.update({'storage-snapshot': ('Storage 元数据单次调用复用', '在一次调用内复用 backing storage 元数据，仍执行 bounds/alias 检查。CPU helper中位耗时约省33.47%；官方16K四轮暖均4552.473333 tok/s，对既有A 4548.78观察+0.0812%。KV页相同，起始DB相同而末态调优DB不同；尚无稳定因果收益或新准确率资格。团队PR120旧4K ABA同样未证明稳定收益，本批补充16K，不重复声明新方法。', []), 'mixed-warm-profile': ('Mixed 暖态性能分析', '保留窗494.888s，GPU union489.748s（98.96%）；非Graph Q32 attention累计201.460s，约占窗口40.7%。实际Mixed调度样例Q2018/context12108/KV14126已回收，但不等同逐调用pointer ABI。profile/collector/analyzer成功；旧posthoc解析不完整，不是模型报错。这些时间是诊断结果，不是官方成绩或可直接省去的成本。', []), 'q32-causal-interior': ('Q32 历史块掩码精简', '尝试将完整历史tile与因果边界tile分为两个保持升序的循环，减少历史tile的load/causal mask。第一次入口仅有helper SHA抄写错误；修正入口后，首个组件样例A/B逐位不一致。finite、guard和输入只读通过，但未进入计时；停止候选。此结果不等于团队main已确认错误。', [])})
_storage_q32_old_group, _storage_q32_old_result, _storage_q32_old_keep = group, result, keep
def group(row):
    return _STORAGE_Q32_RUNS[row['run_id']][0] if row['run_id'] in _STORAGE_Q32_RUNS else _storage_q32_old_group(row)
def result(row, limit=190):
    return row['conclusion'][:limit] if row['run_id'] in _STORAGE_Q32_RUNS else _storage_q32_old_result(row, limit)
def keep(row):
    return _STORAGE_Q32_RUNS[row['run_id']][1] if row['run_id'] in _STORAGE_Q32_RUNS else _storage_q32_old_keep(row)


# 2026-10-30：Q32 head4 与 score-scale 的精确run覆盖。
_Q32_HEAD4_SCALE = {'20261030T002901364769Z-q32-head4-component': {'method': 'q32-gqa-head4', 'keep': '保留负结果并停止'}, '20261030T003609248517Z-q32-score-scale-compile-probe': {'method': 'q32-score-scale', 'keep': '暂缓，资源门未闭合'}}
GROUPS.update({'q32-gqa-head4': ('Q32 GQA head4 CTA拆分', '四例逐位通过，但完整producer+reducer组件中B慢28.7083%，停止，不进入服务。', []), 'q32-score-scale': ('Q32 score-scale循环外提', 'TTGIR循环乘法3→2；SGPR spill计数98→110，资源门未闭合。仅编译探针，无数值或性能结论。', [])})
_q32_old_group, _q32_old_keep = group, keep
def group(row):
    return _Q32_HEAD4_SCALE[row['run_id']]['method'] if row['run_id'] in _Q32_HEAD4_SCALE else _q32_old_group(row)
def keep(row):
    return _Q32_HEAD4_SCALE[row['run_id']]['keep'] if row['run_id'] in _Q32_HEAD4_SCALE else _q32_old_keep(row)

_q32_old_result = result
def result(row, limit=190):
    return row['conclusion'][:limit] if row['run_id'] in _Q32_HEAD4_SCALE else _q32_old_result(row, limit)


# 2026-10-30：Q32 K-scale/TILE128本批精确run映射。
_Q32_BATCH = {'20261030T005910507361Z-q32-key-scale-compile-probe': {'method': 'q32-key-scale', 'keep': '保留原件并按审阅边界表述'}, '20261030T011120000584Z-q32-key-scale-component': {'method': 'q32-key-scale', 'keep': '保留负向观察与数值门未闭合的证据边界；停止候选，不进官方或生产资格，不重测。'}, '20261030T010749147245Z-q32-tile128-compile-probe': {'method': 'q32-tile128', 'keep': '保留编译与资源记录，进入同几何数值/组件门；当前不宣称性能收益、官方成绩或生产资格。'}, '20261030T012148540966Z-q32-tile128-component': {'method': 'q32-tile128', 'keep': '数值门通过但组件性能为负，停止候选；保留编译资源成本与本轮原件，不进服务/官方，不更新基线。'}}
GROUPS.update({'q32-key-scale': ('Q32 K-scale每tile尺度融合', '每个KV tile读取K尺度后与score scale合并，再乘到整数QK分数；尝试减少循环内一组256×64 score乘法，代价是新增64元素逐token尺度运算并改变FP32结合顺序。TTGIR显示循环内score乘法3→2，ASM SGPR spill计数98→99。四组组件ABBA中B慢0.872%；全量AB数值门因GPU摘要与CPU回读矛盾未闭合，停止且不重测，不称数值通过或已确认错误。', []), 'q32-tile128': ('Q32 TILE128', '将Q32 encoded attention的KV tile从64扩为128，BM256/BQ32/w16/stage1保持；期望减少循环次数，实际VGPR 135→164、shared 57344→81920 B、ASM SGPR spill计数98→128。五case数值/guard/readonly/changed-Q通过，但组件B慢5.358%；停止，不进入服务/官方或更新基线。', [])})
_q32_group, _q32_keep, _q32_result = group, keep, result
def group(row):
    return _Q32_BATCH[row['run_id']]['method'] if row['run_id'] in _Q32_BATCH else _q32_group(row)
def keep(row):
    return _Q32_BATCH[row['run_id']]['keep'] if row['run_id'] in _Q32_BATCH else _q32_keep(row)
def result(row, limit=190):
    return row['conclusion'][:limit] if row['run_id'] in _Q32_BATCH else _q32_result(row, limit)


# 2026-10-30：Q32 K-only lookahead本批精确run映射。
_Q32_BATCH = {'20261030T015910809947Z-q32-k-lookahead-compile-probe': {'method': 'q32-k-lookahead', 'keep': '保留原件并按审阅边界表述'}, '20261030T021326156242Z-q32-k-lookahead-component': {'method': 'q32-k-lookahead', 'keep': '保留原件并按审阅边界表述'}}
GROUPS.update({'q32-k-lookahead': ('Q32 K-only lookahead', '在当前QK MMA之后、PV之前发起下一KV tile的K/K-scale加载，尝试覆盖全局访存延迟；增加预取状态和活跃值。ASM确认跨PV候选窗口且编译资源未增加。组件五case数值门通过，但四组ABBA中B慢6.303%，停止，不进入服务/官方测试或更新基线。', [])})
_q32_group, _q32_keep, _q32_result = group, keep, result
def group(row):
    return _Q32_BATCH[row['run_id']]['method'] if row['run_id'] in _Q32_BATCH else _q32_group(row)
def keep(row):
    return _Q32_BATCH[row['run_id']]['keep'] if row['run_id'] in _Q32_BATCH else _q32_keep(row)
def result(row, limit=190):
    return row['conclusion'][:limit] if row['run_id'] in _Q32_BATCH else _q32_result(row, limit)


# 2026-10-30：Q32连续页仿射寻址本批精确run映射。
_Q32_BATCH = {'20261030T024139836824Z-q32-affine-pages-compile-probe': {'method': 'q32-affine-pages', 'keep': '保留原件并按审阅边界表述'}, '20261030T024939570521Z-q32-affine-pages-component': {'method': 'q32-affine-pages', 'keep': '保留为条件候选；下一步先核真实连续页覆盖率和descriptor构建/传输成本，再决定是否服务接入。'}}
GROUPS.update({'q32-affine-pages': ('Q32 连续页仿射寻址', '在完整且连续的KV页区间内，以仿射页号替代页表读取；跨界与尾部保留原页表路径。编译审阅确认命中分支去除页表读取，但ASM SGPR spill计数98→110。理想连续页布局的5-case数值门通过、四组ABBA局部省1.4188%；descriptor构建/H2D与真实覆盖率未测，仅保留条件候选。', [])})
_q32_group, _q32_keep, _q32_result = group, keep, result
def group(row):
    return _Q32_BATCH[row['run_id']]['method'] if row['run_id'] in _Q32_BATCH else _q32_group(row)
def keep(row):
    return _Q32_BATCH[row['run_id']]['keep'] if row['run_id'] in _Q32_BATCH else _q32_keep(row)
def result(row, limit=190):
    return row['conclusion'][:limit] if row['run_id'] in _Q32_BATCH else _q32_result(row, limit)

if __name__ == '__main__':
    main()


# PR5 publication batch 2026-10-29: native S8/shared4k evidence.
BATCH_RESULTS['native_gqa_s8_source_build_identity_pass'] = ('CPU build-only完成；产物身份可供后续组件参考，不含GPU验证。', '保留为构建/身份记录，不视为性能或生产资格。', 'CPU build-only完成；产物身份可供后续组件参考，不含GPU验证。', '核查source files、build summary与SO SHA；原件manifest逐项SHA复核。')
SHORT_ATTEMPTS['native_gqa_s8_source_build_identity_pass'] = ('为N30/S8组件准备实际source build和SO身份。', '构建固定source树并生成build receipt；限定build_only，未发起GPU workload。')
BATCH_RESULTS['native_gqa_s8_short_kv_component_positive'] = ('两档组件Event均有明显下降；本结果不等同端到端官方吞吐。', '保留局部正信号；不授生产、官方或完整S8准确率资格。', '两档组件Event均有明显下降；本结果不等同端到端官方吞吐。', 'ABBA组件计时及完整输出、partial、FP64抽样、Graph、side/input/RNG检查。')
SHORT_ATTEMPTS['native_gqa_s8_short_kv_component_positive'] = ('测量N30/S8 native producer在KV16K与KV4K的组件路径。', '固定N30/S8实现，分别测试两档KV长度，没有新增长度分流。')
BATCH_RESULTS['native_gqa_live_acc_component_negative'] = ('Event慢0.0135%，wall差极小且方向不一致；候选按Event负信号停止。', '保留负观察，不扩展到官方或模型测试。', 'Event慢0.0135%，wall差极小且方向不一致；候选按Event负信号停止。', '固定KV16K，检查数值/FP64抽样/Graph及side-effect，再做暖组件ABBA。')
SHORT_ATTEMPTS['native_gqa_live_acc_component_negative'] = ('复核N32/S4 live-acc producer的热点组件代价。', '保持原macro1对照与live-acc候选数学和reducer。')
BATCH_RESULTS['native_gqa_s8_shared4k_entry_crlf_failed'] = ('入口工具失败，不代表候选源码编译/数值/性能失败。', '保留失败原件，后续LF修复后独立重试。', '入口工具失败，不代表候选源码编译/数值/性能失败。', '检查owner结果与原始shell日志；没有kernel launch、数值门或计时。')
SHORT_ATTEMPTS['native_gqa_s8_shared4k_entry_crlf_failed'] = ('尝试运行shared4k候选的CoreX compile-only入口。', '未形成编译结果；shell脚本换行符导致解析失败。')
BATCH_RESULTS['native_gqa_s8_shared4k_compile_only_pass'] = ('编译成功、spill为0；这只是compile-only机制证据。', '保留编译产物，等待独立组件数值与性能结果。', '编译成功、spill为0；这只是compile-only机制证据。', '读取compile summary、LLVM/ASM和实际资源字段；不推断CTA occupancy。')
SHORT_ATTEMPTS['native_gqa_s8_shared4k_compile_only_pass'] = ('验证S8 shared4k源码在实际CoreX工具链下可编译。', '候选把K/V共享stage压到4096B；无源码数值/运行改动。')
BATCH_RESULTS['native_gqa_linear_n64_no_linear_observed'] = ('本次采集未观察到可用目标调用；不是全局不存在该调用的证明。', '保留无观察诊断；不转为性能或实现结论。', '本次采集未观察到可用目标调用；不是全局不存在该调用的证明。', '保留final/owner日志、profile与DB状态；本轮未得到目标launch证据。')
SHORT_ATTEMPTS['native_gqa_linear_n64_no_linear_observed'] = ('用有界capture检查该profile窗口是否观察到目标N64 linear调用。', '没有改变kernel、模型或评测参数；采集driver异常退出。')
BATCH_RESULTS['native_gqa_s8_shared4k_component_positive'] = ('两档Event与wall均正向；这是局部组件信号。', '保留组件候选观察；不声称官方收益/模型资格，不修改生产代码。', '两档Event与wall均正向；这是局部组件信号。', '同bundle包含102155 CPU build记录；组件分别对KV16K/4K执行数值、FP64、Graph、输入/RNG检查和ABBA。')
SHORT_ATTEMPTS['native_gqa_s8_shared4k_component_positive'] = ('比较N30/S8原shared8KiB与shared4k K/V同址复用候选。', '只变共享缓冲区生命周期与V写入/读取地址；QK、softmax、PV数学与reducer保持。')
GROUPS['native-gqa-s8'] = ('native GQA S8与shared4k组件', 'PR105原S8官方观察与本批局部组件结果分开：已有官方16K暖均相对PR105观察+1.1275%、4K−0.5039%，两档KV条件均不匹配；原105为101/105，S8分支未被batch8触发。本批N30/S8 short-KV与shared4k组件局部正向，live-acc不同候选负向，shared4k另有入口失败和CPU compile-only；这些组件不授官方、模型或新生产资格。', [])
GROUPS['native-gqa-live-acc'] = ('native GQA live-acc组件', 'N32/S4 live-acc组件数值/FP64/Graph/副作用门通过，但Event慢0.0135%，wall微幅反向；保留负观察并停止，不扩展为模型或官方结论。', [])


# PR5 local draft 2026-10-29: shared4k S4, linear capture, and pre-GPU entry failures.
BATCH_RESULTS['native_gqa_shared4k_s4_component_micropositive'] = ('S4 Event省0.0538%、wall省0.1435%；属微弱组件正向，未确认稳定收益。', '保留组件观察；不作官方成绩、生产资格或基线更新。', '局部ABBA微正向', 'N32/S4/KV16K，每窗32次producer+原reducer；9个数值/状态用例通过。')
SHORT_ATTEMPTS['native_gqa_shared4k_s4_component_micropositive'] = ('验证N32/S4 shared4k复用shared stage的组件代价。', '只改变shared stage生命周期；PR105 macro1 S4与shared4k两臂使用同一原reducer。')
BATCH_RESULTS['native_gqa_linear_n64_actual_shape_no_go'] = ('135次linear调用已观察；窄N方向对实际shape为NO-GO，warm-only调用不代表请求热点。', '保留真实shape诊断；不重复上卡或推断模型性能。', '仅捕获，不测候选性能', '真实LibEntry.run observer及私有数据库精确shape记录；warm QKV request_calls=0。')
SHORT_ATTEMPTS['native_gqa_linear_n64_actual_shape_no_go'] = ('核实真实linear调用shape以及窄N方向的已有同shape证据。', '只安装observer采集调用信息，不修改kernel、模型或评测参数。')
BATCH_RESULTS['native_gqa_s8_official_entry_failed_pre_gpu'] = ('三次官方入口均在GPU启动前失败；无benchmark请求或GPU性能结果。', '保留入口失败证据；修复接线后另行启动，不作为模型数值错误。', 'CPU入口失败；未测GPU', '三次分别为旧overlay路径、旧DRIVER_SHA、qualification manifest字段结构不符。')
SHORT_ATTEMPTS['native_gqa_s8_official_entry_failed_pre_gpu'] = ('尝试启动shared4k S8官方候选入口。', '三次失败均发生在启动GPU前，分别修正wrapper路径、DRIVER_SHA及manifest读取。')
GROUPS['native-gqa-shared4k'] = ('GQA shared4k共享缓冲区复用', 'N32/S4/KV16K局部ABBA省时约0.05% Event、0.14% wall，只是微弱正向组件信号，未确认稳定收益。S8官方候选的三次入口失败均在GPU启动前，无benchmark请求和性能计时；不将其解读为候选数值错误或退化。', [])
GROUPS['native-gqa-linear-n64'] = ('真实linear shape与窄N方向诊断', '104512短请求捕获135次linear调用；实际shape与warm-only调用分开，精确shape私有数据库记录不支持窄N候选，故NO-GO。诊断不是候选性能测试，也不据此推断官方请求热点。', [])
GROUPS['native-gqa-s8'] = ('native GQA S8生产接入与shared4k筛选', 'PR105 producer新增N30/S8，仅BF16且Q stride=2048命中，其余fallback。16K官方暖均观察+1.1275%，4K暖均−0.5039%，KV条件不匹配；原105为101/105，但batch8未覆盖S8 kernel执行。另有三次shared4k官方入口失败，全部在GPU启动前，无benchmark请求和性能数据；不构成候选正确性或性能结论。保持PR105基线，不作严格因果或新基线。', [])


# PR5 publication batch shared4k official 2026-10-29
BATCH_RESULTS['native_gqa_s8_shared4k_official_16k_positive_observation'] = ('暖均4908.913333 tok/s，对PR105 4832.66为观察+1.577875%；KV容量差48 tokens。', '保留为完整官方16K正向观察；不作严格因果、新基线或准确率资格，4K另行筛选。', '暖均4908.913333 tok/s，对PR105 4832.66为观察+1.577875%；KV容量差48 tokens。', '沿用官方脚本/服务参数，16384输入、1024输出、并发64、每轮128请求；完成四轮，弃首轮比较PR105。')
SHORT_ATTEMPTS['native_gqa_s8_shared4k_official_16k_positive_observation'] = ('筛选N30/S8 shared4k候选的官方16K吞吐表现。', 'PR105 N30/S8 producer接入shared4k实现；仅BF16、Q stride=2048命中，其余回退保持。')
BATCH_RESULTS['native_gqa_s8_shared4k_official_4k_negative_stopped'] = ('第二轮6204.95 tok/s，对PR105 6441.35低3.670038%；512请求成功，KV差48 tokens。', '保留两轮负向筛选结果；不扩为四轮、不称框架错误，不建立基线或准确率资格。', '第二轮6204.95 tok/s，对PR105 6441.35低3.670038%；512请求成功，KV差48 tokens。', '官方4K输入4096、输出1024、并发64、512请求；记录两轮，在第二轮按负向筛选规则停止。')
SHORT_ATTEMPTS['native_gqa_s8_shared4k_official_4k_negative_stopped'] = ('按官方首暖筛选规则评估shared4k S8候选4K负载。', '运行同一shared4k S8接入；保持官方服务及评测参数，未改变候选实现。')
GROUPS['native-gqa-s8'] = ('native GQA S8与shared4k官方筛选', 'shared4k S8路径官方16K完成四轮，暖均相对PR105观察+1.577875%；KV条件差48 tokens，不能严格归因。官方4K第二轮低3.670038%，按首暖规则停止，仅两轮，不是四轮成绩。两档均实际触发S8 eager_only，但无准确率资格，不更新PR105基线。', [])




# PR5 publication batch native K8 component 2026-10-29
BATCH_RESULTS['native_k8_sme_component_pair_build_pass'] = ('隔离A/B SO构建成功；符号、动态依赖和20参数ABI核对通过。无GPU执行。', '保留为组件入口构建身份；不把compile结果写成数值或性能结论。', 'A/B final SO构建与静态身份核验', '分别检查linked SO IR/SASS、symbols、动态依赖、build receipt。')
SHORT_ATTEMPTS['native_k8_sme_component_pair_build_pass'] = ('为NativeK8 SME lookahead准备A/B隔离组件so。', '两臂使用独立launcher和producer符号；数学/原reducer不在此run测试。')
BATCH_RESULTS['native_k8_sme_component_candidate'] = ('4组数值/Graph边界通过；Event四项减少2.07–2.73%，4K Q stride2560 wall反向慢2.10%。', '保留为局部producer+原reducer组件候选信号；不作稳定模型/官方吞吐、准确率或新基线资格。', '组件ABBA候选信号', '4个形状/stride case，数值全数组逐位、混合边界、变Q Graph、输入不变与redzone；原始A/B顺序见summary。')
SHORT_ATTEMPTS['native_k8_sme_component_candidate'] = ('验证K-lookahead SME候选在producer+原reducer组件中的数值与局部耗时。', '仅比较已构建的隔离A/B producer，沿用同一原reducer及相同输入。')
CODE['native-k8-sme'] = CODE.get('native-k8-sme', []) + ['experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_A.cu', 'experiments/bundles/20261029T155955570211Z-native-k8-sme-pair-build/source/native_k8_sme_B.cu', 'experiments/bundles/20261029T161341635355Z-native-k8-sme-component/source/worker.py']
GROUPS['native-k8-sme'] = ('NativeK8 SME布局与lookahead组件探针', '完整页K-stage字节布局探针通过；lookahead两臂standalone compile/ASM顺序门通过。新增producer+原reducer组件4-case结果逐位数值/Graph/input门全通过，Event改善2.07–2.73%，但4K Q stride2560 wall反向慢2.10%。均为组件/编译证据，不代表attention完整正确性、官方吞吐、模型准确率或生产资格。', [])
