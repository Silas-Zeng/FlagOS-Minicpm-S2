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
    'pr25-kv-current': ('PR25 与缓存修复后的 KV 保存恢复', '当前性能对照基线已更新到main0bf9/tree8671（526文件、SO14f）：161030按官方4K/16K各四轮，第2–4轮5758.72/4045.20 total tok/s，TTFT3626.85/124212.05ms，1536/0；KV547536、初始DBfb035。该版本本实例完整105仍待，不能称最终合格基线。532组合155917 VERIFY1与4题语义门通过；171101正式测量前因目录前缀被图门误拒，原exit1和后验强身份相同证据保留，不记吞吐。只修测量门的重试由运行负责人维护，完成后另登记。\n\n队友[PR31](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/31)实际受测e972997、SO271327a0，暖后单轮4K/16K为5766.41/4048.28，准确率102/105；标题Draft且未合并。[原manifest](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/manifest.json)与[acceptance](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/blob/d79b7b1a012943dce867d1adcc29a45e0d7b79bf/docs/evidence/ragged-gqa-segments-20261024/service-final/acceptance.json)保留其边界。双方源码、SO、轮数及DB/KV不完全同条件，不直接算收益；#33/#36仍是局部探针，#37服务准确率仍待，#38仅调研，不当作新基线。\n\n前序7596共同基点的两轮筛选继续保留：同KV546432与DB，4K+0.103%/+0.644%但无FULL覆盖，16K+4.728%/−0.493%；仅保留候选，不确认稳定收益，不把旧组合成绩赋给新main。', ['native-quant-cache', 'native-cache-identity']),
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
    'other': ('其它登记与控制记录', '没有足够字段继续归类的登记；不补猜实验结论。', []),
}
CODE = {
    'pr25-kv-current': ['analysis/pr25-kv-current-pair.json', 'experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds/result.json', 'experiments/framework/20261024T142819Z-pr25-cache-main-fullsize-two-rounds-control/archive-receipt.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/source-manifest.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long/model-path/semantic-validation.json', 'experiments/framework/20261024T145945Z-pr25-cache-kv-verify1-context16k-long-control/archive-receipt.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds/result.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/state.json', 'experiments/framework/20261024T151255Z-pr25-cache-kv-fullsize-two-rounds-control/archive-receipt.json', 'experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long-control/coverage.json', 'experiments/framework/20261024T155917Z-main0bf9-kv-verify1-context16k-long/model-path/semantic-validation.json', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds/benchmark_results/summary_20261025_001229.csv', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/state.json', 'experiments/framework/20261024T161030Z-main0bf9-main-official-four-rounds-control/archive-receipt.json', 'experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds/result.json', 'experiments/framework/20261024T171101Z-main0bf9-kv-official-four-rounds-control/postfailure-cache-audit/audit.json'],
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
}


def group(row):
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
    """只摘结果/失败原句，不把审计与库身份搬入主视图。"""
    if row['status'] == 'official_four_rounds_baseline_completed':
        return '官方两档各4轮、1536/0；第2–4轮4K5758.72/16K4045.20 tok/s，TTFT3626.85/124212.05ms；本实例该版本完整105仍待。'
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
    text = row['conclusion']
    state = row['status'].lower()
    if state == 'official_four_rounds_baseline_completed':
        return '保留作当前性能对照基线；完整105仍待，不称最终合格基线，不跨队友条件算收益。'
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
    phase = row['phase'].lower()
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
    value = row['status'].lower()
    if value == 'official_four_rounds_baseline_completed':
        return '四轮性能基线完成，完整105待验'
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
                                       ('q-fragment-hoist', 23)]})
    pr_labels = {'cpu-metadata': 'CPU metadata #1', 'async-token-update': '异步token更新 #2',
                 'pr24-main': 'INT8 gate/up 组合 #24', 'native-quant-cache': '激活量化缓存 #25', 'native-cache-identity': 'native编译缓存身份 #35',
                 'kv-contiguous-copy': '连续页KV工具 #3', 'kv-pitched-copy': '二维SAVE工具 #4',
                 'diagnostics': '诊断配置 #5', 'prefill': 'prefill #6', 'top-p': 'top-p #7',
                 'sql-reflection': 'SQL反射 #8', 'decode3d': '3D decode #9', 'mixed-attention': 'mixed Attention #10',
                 'skip-computed-h2d': 'computed H2D+计算顺序组合 #22', 'compute-order': 'computed H2D+计算顺序组合 #22',
                 'q-fragment-hoist': 'Q fragment #23'}
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


if __name__ == '__main__':
    main()
