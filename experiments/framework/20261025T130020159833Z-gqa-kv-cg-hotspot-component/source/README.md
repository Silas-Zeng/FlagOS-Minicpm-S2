# GQA decode 的 K/V 流式读提示

唯一候选是在当前生产 `biv150_gqa_decode.py` 的四处 K/V load（完整页和尾页）增加 `cache_modifier=".cg"`。原 BF16、页表、split、顺序、mask、softmax、dot、reducer、Graph 与服务参数均保留。源码逆变换严格等于 main 0915 的生产原件；组件 owner 继续核冻结 0bf9/526，因为 0915 新增 77 项仅为 docs/tools。未改任何生产目录。

实际 16K 轨迹中的 N33/bucket40/S16 GQA 是主要图内热点。一个 CTA 内已经复用八个 query heads，跨 CTA 不共享其同一 KV 段，长 KV 为流式读取；这里仅检验不向 L1 分配 K/V 的提示是否有净收益。[Triton load 文档](https://triton-lang.org/main/python-api/generated/triton.language.load.html) 对 `.cg` 的说明明确面向 NVIDIA PTX，不能直接当成 BI-V150 实测事实，因此入口首先保存并检查实际 CoreX ASM 中新增的 `cg` LSA load；若被忽略、机器读指令相同或编译不支持就停止，不扩展其它 cache 选项。

旧 `20261022T130457Z-prefill-v-late-cache-v2-gate` 负结果是 **2D prefill V-late 的函数级 PREFER_SHARED** 对照（shared 从64KiB变48KiB），不是本 GQA 指令级 load 提示。旧 TILE32、identity-rescale、next-K 不混入。最新 PR49 是 CJJ1008 的 INT8 KV writer+dequant 草稿；PR46/47 是 prefill Q/KV tile，PR38 与33/36/37/44仍由队友负责，本组件不改它们。

复用已受测 v3 组件：默认仅 N33/bucket40/S16、33条16K随机 KV 和7条 padding，原 Builder/Impl/KV writer 自然选择路由；不是实际模型激活重放。ASM 变化后再运行原逐位 eager/changed-input poisoned Graph、非有限值/尾页/零长/输入不变边界，全部通过才做16-call ABBA。原空 padding 修复保留；源码没有执行旧负候选数学。通过也仅是组件信号，不是模型准确率或官方吞吐。B32/S4 入口保留但不自动运行，由主智能体按首项结果决定。

```bash
python entry.py --shape hotspot \
  --source-dir /workspace/experiments/minicpm-s2/code/20261024T161030Z-main0bf9-main-official \
  --native-library /已核native14f原生库.so
```

仅主智能体启动。设备锁、GPU/9031检查、native14f、420秒上限、DB保存恢复与只清理所属 PID 均逐字继承；owner 只更换 run 后缀。`kernel.diff`、`worker.diff`、`owner.diff` 给新增审阅，`cpu-check.json` 仅证明新增静态差分和 ASM 判读合同，未触GPU。实测输出进入 `framework/<UTC>-gqa-kv-cg-hotspot-component`。
