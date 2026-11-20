<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261025T074041Z-attention-affine-pages-model-verify

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #252 · Attention连续页段寻址

- **尝试**：保持原KV分配与数学，对现存连续物理页段用仿射寻址。组件四布局逐位通过、局部耗时下降约5.0–6.9%；原四语义及三个串行prefill页表绑定通过，仅P恒等/C3prefix0。完整官方两档各四轮1536成功，弃首轮4K5741.68/16K4050.10 tok/s，相对main526观察−0.30%/+0.12%；KV546432对547536，不确认净收益、不定基线、不追加105。
- **改动**：相关实现 [biv150_attention_affine_pages.py](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify-control/plugin-source/vllm_fl/patches/biv150_attention_affine_pages.py)；[prototype.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/prototype.py)；[worker.py](../../../experiments/framework/20261025T071453655585Z-attention-affine-pages-component/source/worker.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：具体测法未单列，见原命令；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：连续页寻址527/tree41449b98，仅worker安装入口+新helper
- **是否保留**：保留进入原官方吞吐；完整105与混合/P实际覆盖尚待，不声称已恢复旧mixed2资格。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261025T074041Z-attention-affine-pages-model-verify",
  "local_date": "2026-10-25",
  "utc_start": "2026-10-25T07:40:41.842514+00:00",
  "profile_id": "attention-affine-pages",
  "phase": "真实模型接续验证",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "0bf9d2efeaa10144dd7f0ff4597298df029f9328",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "affine_model_short_gate_pass",
  "artifacts": "experiments/framework/20261025T074041Z-attention-affine-pages-model-verify",
  "conclusion": "连续页寻址527/tree41449b98，仅worker安装入口+新helper；原加85/乘323/除12/4908输入长题95全对，实际新FP/AOT与34native通过。三个真实长prefill epoch的描述符和GPU活页逐字一致，M2048/2048/796，Q-hoist及实际candidate命中；本门P恒等、C3prefix0，未证明P重排场景或完整105。源/native未变、DB恢复/清理成功，保留进入原官方4K/16K吞吐；性能关闭回读诊断，不借组件百分比报E2E。"
}
```

</details>

## 原件与说明

- 原始目录：[20261025T074041Z-attention-affine-pages-model-verify](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify)
- 原命令：未单列，见原始目录
- 环境 / 源码 / 后态：[source-sha256.json](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify-control/source-sha256.json)
- 原始结果：[result.json](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify/result.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify/server.log)；[gpu.csv](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify/gpu.csv)；[exit-code](../../../experiments/framework/20261025T074041Z-attention-affine-pages-model-verify/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
