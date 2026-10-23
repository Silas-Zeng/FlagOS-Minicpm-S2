<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T191047Z-q-gqa-admission-observe-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #162 · 有限增长准入观察

- **尝试**：当前Q+GQA上的稀疏CPU准入与失败状态诊断；不实现预留策略，不把页预算反事实当作吞吐收益。
- **改动**：相关实现 [biv150_admission_observer.py](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/biv150_admission_observer.py)；本轮准确变体以原件源码清单为准。
- **怎么测**：真实服务短负载；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：32成功0失败；诊断有临时O(N)状态复制开销，不报吞吐或预算反事实收益，有限窗口与晚尾代价由后继实际诊断判断
- **是否保留**：保留作准入状态诊断；尚未实现预留策略，不提供性能收益结论。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T191047Z-q-gqa-admission-observe-context16k-long",
  "local_date": "2026-10-23",
  "utc_start": "2026-10-22T19:10:48.544958+00:00",
  "profile_id": "finite_admission_observer",
  "phase": "sparse_cpu_admission_observer_context16k_long",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_cpu_diagnostic",
  "artifacts": "experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long",
  "conclusion": "当前已过准确率的Q+GQA414基点仅init+观察helper生成415源，runnercc442不变；原16K/1024out/32请求/c64、seed721201，32成功0失败。Engine344148真实ARMED，记录4次WAITING首次实际准入、2次首次attempt及1次RUNNING分配失败；首准入样本N29/free2702与N30/free1664，队列/当前scheduled和APC/owned相位分开。只复制CPU标量和列表长度，不读Future或GPU、不实现reserve；owned逻辑页不等于唯一可释放页，GPU完成前缀/EOS未知。529表19769行DB三SHA前后同、KV521936，root逐477seal验收复用、退出0及设备清理；诊断有临时O(N)状态复制开销，不报吞吐或预算反事实收益，有限窗口与晚尾代价由后继实际诊断判断。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T191047Z-q-gqa-admission-observe-context16k-long](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/launch-command.json)；[command.txt](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/command.txt)；[launch.sh](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/launch.sh)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261023-031458.json](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261023-031458.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T191047Z-q-gqa-admission-observe-context16k-long/exit-code)
- 相关说明：未记录
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
