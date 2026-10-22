# 算子线路线图（2026-10-23 凌晨，机器让出期间整理）

设备 03:00 之后由另一 agent 使用，本轮不再上卡。下面是"机器一空就能照单执行"的清单，按先后顺序，全部带 go/no-go 闸门。

## 0. 已完成、已合并（基线，不再动）

- 专用 GQA decode attention kernel：main `9a43eb1`；官方仪表两轮 4K 3738.62→4906.39（+31.2%）、16K 2734.40→3371.88（+23.3%）；官方四轮 4809.36 / 3364.03；Level-3 0.9714。
- 最优段数下的 kernel 实测：b64/kv4096 seg2 **0.5242 ms / 512 GB/s**，b16/kv16384 seg8 **0.5264 ms / 510 GB/s**（553 GB/s 锚点的 92–93%）。

## 1. 已关闭（负结果，不要再试）

| 轴 | 结论 |
|---|---|
| 循环流水线 `tl.range(num_stages)` | 慢 21–35%，stages 越大越差 |
| `evict_first` | 415.2 vs 414.9 GB/s，无差别 |
| 单遍固定 Δ 的 V-skip | Δ=6/10/14 均无一页被跳，分支本身慢 3–6% |
| pages_per_step=2 / warps=2 / ROWS=16 | 均更差 |
| int8 GEMM（七种集成形态） | 全部失败：自定义 op 慢 47%、triton_op/纯 aten 追踪失败、热编译缓存静默沿用旧图 |
| int8 KV / FP8 KV | cache dtype 属 serve 超参（禁止）；自建 shadow 21+10.5 GB > 32 GiB |
| 预填充 attention launch 网格 | 团队 BM128/TILE64/8w/1s 已是网格最优；本机占比约 1% |
| sampler / norm / act / RoPE / KV-write | 已优化或合计 <3% |

## 2. 待执行：页选择稀疏 decode attention（唯一够量级的路线）

**闸门 A（先做，约 25 分钟，只跑一次 Level-3）**
- 目的：回答"MATH Level-3 对解码时缺失中段上下文有多敏感"。
- 做法：临时把 decode 的可见范围裁成"首 32 token + 最近 W token"（W=2048）。实现最省事的方式是构造压缩 block table 后复用现有 kernel（不需要改 kernel 算术），或直接在 kernel 里改 `lower/upper` 并为 sink 单独跑一段。
- 判定：≥0.965 → 继续闸门 B；<0.95 → 稀疏线整体放弃，转闸门 C。

**闸门 B（约 2 小时，kernel + wrapper）**
- 分数平面：`[max_seqs, kv_heads, max_pages]` fp32，按 `k_cache.data_ptr()` 分层缓存，约 7 MB。
- kernel：读上一步页分数 → 低于本段最佳页超过 Δ（log2）则整页跳过 K 与 V 且不计入分母；首 2 页与末 2 页强制保留；序列首步稠密。
- 预期：f=0.5 → attention 27.5→13.8 ms → TPOT 60.35→46.6（**+29%**）；f=0.35 → **+39%**。
- 验证顺序：kernel A/B（同 seed，报 max_abs_diff 与跳页率）→ 2 轮 4K 探针 → Level-3。

**闸门 C（多天项目，需拍板）**
- 原生 int8 GEMM（无 Python 分发，C++/vendor 侧）或 int8 KV 的 cache 手术；两者都要重过精度门，且都触碰框架核心路径。

## 3. 风险与已知坑

- 序列槽复用会带来"首步脏分数"：必须首步稠密并重写全部分数，否则每个新请求有一个坏 token。
- 页分数分布未知：随机数据的微测不能代表模型真实分布，只能靠闸门 A/B 的服务级精度回答。
- 任何改动都要先清 `/root/.cache/vllm/torch_compile_cache`，否则图内改动会出现"恰好零效果"的假阴性。
- 停服务务必按进程组（`kill -TERM -$PID`），否则会留孤儿进程占端口。
