# 计算顺序与采样顺序分离

截至2026-10-23，120949→121541原短服务31项可比门全过，同KV521936及DB561/20721，吞吐变化+5.124857%，仅单pair正信号。130351事件质量诊断固定原Level3 index0..3、采样和judge，4/4正确；index0/1/2三题在输出token的0基索引94处实际进入outside路径，首完整`boxed`前缀尚未出现，生成总长分别1123/744/1651。index3位于row0，未覆盖outside，总长733；背景32/0。该诊断不计性能、105题准确率或稳定收益，候选可推进独立Draft PR，仍不自动集成。

本轮DB561表/20721行→565表/20919行如实保留。125330是原请求发送前的客户端长度校验失败，背景0发送、Math4 ready但未放行，不是优化负结果。旧KV失配、未覆盖和数值差异证据不删除；061500完整105题与104132原四题均不能代替本轮新路径覆盖。详[130351质量诊断](../../../../analysis/compute-order-math4-event-130351.json)、[125330客户端失败](../../../../analysis/compute-order-math4-event-125330.json)及[同容量短对照](../../../../analysis/compute-order-service-retest-pair.json)。

以下保留初始CPU候选的实现接续说明；其中“尚未部署”等为当时状态，不覆盖以上最新结果。

基点为已封存 KV422（213134，runner `cc442e54…`，完整 map `82514a24…`）。这里只准备新隔离源码，不部署、不启动设备。044216 的 CPU metadata 摘要有 759/3000 个前缀外 q1；首版只选已有连续前缀的 70 步/729 个 q1，25.3% 不是时间收益。

候选把本次计算用的请求行稳定分区为 q1 在前，原持久 InputBatch、req IDs、采样行序、N 行（含部分 prefill 后丢弃的行）、RNG 调用与请求历史不改。输入/位置直接按 P 构建，页表用私有 pinned 行 staging 上传到原 GPU 地址；seq/computed/prompt 使用私有计算序 CPU 视图，optimistic/discard 保原序。原 `hidden_states[logits_indices]` 用原请求序 ends 做 N 行 gather，不逆拷整批 hidden，不改算子。

只选 `Dprefix>0 && outside>0`、普通 BF16 text/TP1/async 单 FullAttention 组及已核 FULL_DECODE_ONLY 的无 padding mixed 路径。pure decode、capture/dummy、恢复标记、spec/MM/prompt logprob、未知 scope 原路。原 dispatcher 仍只调用一次；写后若违背 NONE/M/N 合同即抛错，不重试旧路。本次 plan 只通过 execute 局部变量传递，跨步只保留 staging/cold scope/计数。

冻结文件（完整 SHA 见 `files-prepare.json` / `static-check.json`）：

| 产物 | SHA256 前缀 |
|---|---|
| `biv150_compute_order.py` | `5ce6f7b6a815` |
| `prepare_compute_order.py` | `b1a804a0c6da` |
| `files/vllm_fl/worker/model_runner.py` | `ea64a59cff61` |
| `files/vllm_fl/patches/biv150_kv_worker.py` | `2086980e1ea1` |
| `files/vllm_fl/patches/biv150_kv_protocol.py` | `b2c576d92be3` |

423 输出只新增 helper，修改 runner 及 worker/protocol 的两个整 runner SHA 锁；后两者除此逐字节不变。init、协议事务、Q/GQA/C3 和旧 CPU helpers 不改。`runner.diff` 与 `files-prepare.json` 保存 14 个精确切口及逆回依据。

root 后续可在独立 assets 目录放本 helper、preparer、`base-source-sha256.json`，纯 CPU 构建新源：

```bash
python3 <assets>/prepare_compute_order.py \
  --base /workspace/experiments/minicpm-s2/code/q-gqa-kv-swap-20261022T213134Z \
  --output /workspace/experiments/minicpm-s2/code/compute-order-<新UTC>
```

完整 422 输入 map 和前后身份均严格核对；新目录已存在即拒绝。`--emit-only` 只生成四路径镜像，不是完整可部署源。当前 `files/` 即此镜像，完整预期 423 map 在其同级 `files-prepare.json`。

新增持久 GPU storage 为 0（源码检查，未实测 allocator 峰值）；原 GPU 页表/positions/seq 对象不换。N 个 int32 临时 logits 索引由 pinned H2D 替代原 N 个 int32 减法结果，沿原局部生命周期。新增 host staging 为完整页表、maxM 个 int64 positions、四份 maxN 个 int32；全部写在原 `synchronize_input_prep` event 域。代价还包括 P/逆映射、页表 CPU 读写与早 H2D 重叠损失、索引小 H2D、Q ff64 覆盖可能变化；均由实际短服务承担。

作者仅完成完整 map、compile、精确逆回及 AST 增量检查；真实异步 input-ID 原 AST 与实际 Plan 的最小 CPU 合同由另一 owner 一次通过，见 `../compute-order-review/cpu-contract-result.json`。这不证明真实 cold scope、GPU 数值、RNG 输出或吞吐。`FIRST_SELECTED` 只表示选中 P 的原 model forward 已返回，位于 logits gather/sampler 前，不是完整输出正确性。

下一步由 root 唯一排卡：原 bc51 context-screen/原 SERVER/seed/VERIFY0/Q ENV，复用已完成 054306 原422基线；同 DB/KV 等条件才报告单 pair 信号。不为凑 KV 重启。不命中或无净益即按证据停止；有保留价值再补必要实际 GPU 数值/原 Math500，尚未继承基线准确率，也未集成。
