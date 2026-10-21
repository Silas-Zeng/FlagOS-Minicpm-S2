# 原物理 APC 前缀复用与缺失后缀恢复：下一项条件性框架方向

范围：仅本实例天数 BI-V150（16SM、32GiB、CPU 配额6、主机20GiB）与 MiniCPM5-2B；不外推沐曦－曦云 C500。本文是 CPU 源码/原件研究，没有新实现、GPU 运行或吞吐收益结论。现行 capacity/FULL 配对不加入本文任何观察器或计数器。

## 结论与优先级

值得保留的一项机制是：在外部恢复前复用**同一 victim 仍存活、内容有来源证明的原物理 APC 前缀**，只把缺失后缀从 host 复制回 GPU。它可减少 H2D 字节和提交数，避免把仍有效的缓存页先逐出、再用 host 数据覆盖。当前证据只足以安排后继最短元信息观察，尚不足以开始混合所有权恢复实现。

本方向不增加 KV 池容量，不改变 FCFS、请求集合、token budget、block size、模型或服务参数。对 ref0 命中，它不能使 `free1030 < prefix1044` 的旧等待立即成功。它也不是已有“截短所保存前缀、重算后缀”方案：这里仍恢复原真实 R，只争取少搬已经在 GPU 的部分。

## 一手资料与实际源码挂点

vLLM 官方设计描述了先 touch 本地命中块再分配新块，以及 free 时逆序放回、优先逐出较后的前缀块；这些机制支持“原始前缀可能仍在”的假设，不证明本实例实际命中数量。[官方 APC 设计](https://docs.vllm.ai/en/v0.24.0/design/prefix_caching/)

本地固定源码是判断实现的依据，不能把较新的官方文档当成当前框架版本：

| 文件与位置 | 实际行为 | SHA256 |
|---|---|---|
| `experiments/source-audits/20261021T184108Z-kv-copy/source/vllm/v1/core/kv_cache_manager.py:202` | `get_computed_blocks` 可找真实本地命中，受 enable/skip-read 守卫；最多 `request.num_tokens-1`，有 log_stats 统计副作用，不能未经审计当纯观察调用 | `2e91e77f84dfd9d4bed79f50392be72559207f54e845a3d3402baf88dc529320` |
| 同文件 `:290`、`:348`、`:428` | 分配语义明确包括 local `new_comp` + external `ext_comp`，先交给 coordinator 加本地命中与外部页，再分新 token 页 | 同上 |
| `experiments/source-audits/20261021T173831Z-engine-core/source/vllm/v1/core/kv_cache_coordinator.py:214` | 所有组先 touch 本地命中，再分配 external，避免先分外部页把尚未 touch 的命中逐出 | `9dd0a647f671b859e3743fbf5ec84cd892fd5754022eef58c5b8c989a4cda97b` |
| 同目录 `single_type_kv_cache_manager.py:156`、`:182`、`:234` | 容量计入 ref0 命中；本地块先加入真实 `req_to_blocks`，`num_cached_block` 设成本地长度，随后只分缺失 external 页 | `22e3677acf0e769461bdbf278df031d6e362c97aa1ba7b862c071b76d47d8914` |
| 同文件 `:318`、`:383` | FullAttention 默认每个完整非 null 块可缓存；free 移除请求记账后按逆逻辑顺序释放 | 同上 |
| `experiments/source-audits/20261021T170854Z-scheduler-kv-c3/source/vllm/v1/core/block_pool.py:542`、`:597`、`:614` | 新分配会逐出 cached hash；touch ref0 块先移出 free queue；释放保留有 hash 块并排入 free queue | `3fc5dfe0ab7ccc6206f6eb7886b2aad15384f92708e6b9f7e5ec7838b7379abe` |
| `patches/framework/candidates/biv150_kv_full_restore_protocol.py:275` | 当前外部恢复不传本地命中，直接分完整 R 个 external token；随后要求所有页私有/unhashed，排序整段，再进行 FULL | `1aff952a421bdd942d85cb80903c2bbadba69a16c3301ee327ee22fc2b1aacd8` |

原 waiting scheduler `df780` 在 `:672` 才走普通本地命中查找；当前 `_try_restore` 插入在该切口之前。所以 mixed local/external 不是已有 FULL 开关，必须设计新的显式事务，不能放松现有私有页守卫直接塞进旧路径。

## 214400 实际几何：只证明值得观察

原件 `experiments/framework/20261021T214400Z-kv-full-restore-context16k-long/server.log` SHA256 `6f3a0eec9f4599cc53be7c987e6038a7edde61738b50c7dda598c068fbfa2f91`。从原始 SAVE 与 RESTORE_FULL 命令数组独立计算：

- R16704、1044页、718405632B，目的66个正向连续段，FULL/VERIFY 各2772calls，原诊断已经全42层逐字节通过。
- source 与 destination **物理 ID 集合交集218页**；source 逻辑开头连续190个 ID 均出现在后来 destination 集合中，其字节量124.6875MiB，占完整快照18.1992337%。
- 上述交集不证明 cached hit，不证明 refcount/hash，不证明那些页期间没有被重分配。190不是已证 H，218也不是有效 KV 页数；这些数值只显示旧路径确实可能重新分配原来使用过的 ID。
- 不能由当前日志推出保存后是否曾被同页复用、重新计算或写入；因此也不能据此算节省毫秒。保存/恢复阶段没有足以隔离该改动的阶段计时。

原数组派生 JSON 在 `analysis/source/kv-surviving-prefix/geometry-evidence.json`；不是新实验或测试。

## 容量与收益条件

设 P=R/16，H 为经过真实性证明的连续本地命中页，E 为其中 ref0 的页。actual 单组 FullAttention 对恢复 R 前缀本身的容量下界是 `P-H+E`；完整请求准入、水位与后续新 token 可能要求更多页，这不是整体准入充分条件。

- 首版若只接纳 victim 自己仍在 free queue 的原页，则 E=H，仍需 P 个 free；touch 后 free 少 H，external 少 H，两者抵消。**不能绕过当前 F<P 容量早退。**
- 只有已另证的 ref>0 共享命中才可能降低所需 free。本文不把共享命中作为首版范围，也没有本实例此类证据。
- H 页可少搬 `H×688128` 字节；提交数取决于缺失后缀的实际物理段数，不能按 H/P 同比例缩放，也不能把调用数差当 DMA 时长。
- 对同一请求每轮只发生一次恢复的当前单 victim 策略，端到端收益上界受这一次恢复成本限制，尚不能称“大吞吐收益”。如果观察 H=0，或额外 Python/所有权成本超过 H2D 节省，应明确收敛，不扩扫描。

## 最短后继观察与显式实现边界

1. **先观察，不混当前配对。** 后继获授权时，在 SAVE 完成时记录 CPU 原页/原 hash 描述，在第一次真正准备分配前记录本地 prefix lookup 的页 ID/hash/refcount、与 snapshot 逻辑位置的对应。先审 exact lookup 的副作用，不能为观察而 touch、改变 LRU 或多记 prefix-hit stats。当前没有这个观察器。
2. 首个观察只回答真实 H 是否大于0、有多少连续页、分配前 free 与 E。物理 ID＋同 hash 仍可能经历 evict/recompute 后相同 hash，严格的“原 bytes 未变”需期间未重分配/写入的 provenance，或后续真实全42层 byte gate；不要把 hash 匹配等同数值逐位证明。
3. 若有正证据，候选只允许同 session/incarnation/attempt、真实原 token digest、无 pending frames/placeholder、无 spec/MM/LoRA、单组 FullAttention、完整页。原 allocator 以 `local=16H`、`external=R-16H` 建立完整逻辑 R；先 touch 原本地段，再分新后缀，不能自行改 free queue 或手写 allocator。
4. 保持本地段逻辑顺序，不排序、不 zero、不覆盖 hashed/shared 块；只可对尚未发布、ref1/unhashed 的新后缀排序。新事务须分开证明本地 held-reference 与 suffix 私有所有权、host 逻辑 offset、完整 R 绑定。旧 `_order_private_pages`、FULL all-pages proof 和 worker31cc/5d9a 不适用混合段，**不能复用旧 ACK 冒称全量恢复**。
5. 新 RPC 只复制 host 对应 offset 的缺失后缀，但真实 fence/event/失败 settle/强引用要保留；完成证明必须分别覆盖已验证本地段与真实恢复后缀。失败只回滚本次持有/新分配引用，不 evict 本地缓存、不向旧路径二次提交；取消与未 settle 状态继续 fail closed。
6. H=P 时不能调用现 `allocate_slots(new=0,external=0)`（actual `:342` 抛错）；该边界应先回原 native 路径或作为明确排除，不能伪造一个 external token。
7. 只有上述资格与唯一 CPU 所有权合同成立，才建议一次原参数真实恢复门：记录 actual H/E/free/页映射，VERIFY1 对完整 R 的42层 host bytes（含未写本地段）逐位核对，原 runner 六检查、真实后继 token 消费、取消/回滚边界。通过后再同观察器/DB/KV/CPU 的 VERIFY0 短配对，不能沿用旧 FULL 精度或性能结论。

## KVPR 资料复核：不作为当前实现方向

[KVPR 原论文](https://aclanthology.org/2025.findings-acl.997.pdf) 的 Eq6–10 用输入 activation 替代部分 KV 传输并重算投影，代价模型基于 MHA 的 K/V 宽度等于 hidden；论文也包含不同软硬件/调度条件。这里只借用传输与重算需共同建模的原则，既有论文收益不外推本实例。

对当前实际形状自行代入：BF16 hidden2048 为每层4096B/token，而两 KV 头×128 的 K+V 为每层1024B/token。存所有42层输入需172032B/token，是现 KV43008B/token的4倍。若把原 KV 的比例 f 改为输入 activation 传输，仅 H2D 字节就变成 `C[(1-f)+4f]=C(1+3f)`，还没有算额外投影、RoPE/归一化、位置依赖和输出写入。R16704 时42层 hidden 为2873622528B（2.67626953125GiB），超过当前单 slot1GiB；现协议没有保存这些历史 hidden，不能在抢占时凭空取得。

这不排除少量层 checkpoint＋跨层完整重算等另一种成本模型，也不排除 activation 已驻 GPU 的特殊情形；但它们不是论文 Eq6 的直接替换。16SM 上新增重算会竞争原服务 compute，本实例没有空闲算力或有效并发证明。因此当前不实现 KVPR，不引入量化、模型参数变化、论文框架合并或新的扫描来追求其公布收益。

## 当前状态

写锁解除后只新增本研究及几何 JSON/交接记录；所有受测 runtime、默认入口、共享代码库和当前配对资产不改。下一必要动作是完成 systems 的 capacity/FULL 共同观察器包装互审，设备仍由 root 单独串行；本方向仅进入待授权的元信息观察队列。
