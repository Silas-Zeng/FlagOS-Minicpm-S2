<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T042225Z-kv-pitched-save-context16k-long

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #115 · KV 二维 SAVE 复制

- **尝试**：保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。
- **改动**：相关实现 [biv150_kv_pitched_copy.py](../../../patches/framework/candidates/biv150_kv_pitched_copy.py)；[biv150_kv_pitched_bridge.cpp](../../../patches/framework/candidates/biv150_kv_pitched_bridge.cpp)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：16384 / 1024 / 64 / 32。
- **结果**：event完成且源free前42层旧c95f对照966calls/同nbytes全bytespass
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T042225Z-kv-pitched-save-context16k-long",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T04:22:28.102718+00:00",
  "profile_id": "kv_pitched_SAVE_on_original_FULL_verify1",
  "phase": "short_context16k_long_two_42layer_byte_proof_diagnostic",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "d60b02367a852826f653165953f31b6dc696658e",
  "flaggems_commit": "4df52d9168ac55c1c1061cefb4638c570292d896",
  "input_len": "16384",
  "output_len": "1024",
  "concurrency": "64",
  "num_prompts": "32",
  "profiler": "false",
  "status": "complete_actual_42layer_pitched_SAVE_source_verify_and_FULL_restore_pass",
  "artifacts": "experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long",
  "conclusion": "本agent唯一实际本地后验pass/d7213a76；复用2071 raw与FULL链只source416→420/SAVE旧连续调用断言替换，再独立重算实际正等差几何；cd3d-df6a/a662worker/818e-0a4d-so9e33/1aff-84be-init791c-e155runner/原bc51SERVER-longseed721201/VERIFY1，420源当前完整map与live/installed54c过。实际R16688/P1043/717717504B/23源连续run→5segments每层，42层SAVE210=168linear+42pitched/fallback0（旧c95f966），actualstream0合法/maxpitch2147483647，提交非ACK；event完成且源free前42层旧c95f对照966calls/同nbytes全bytespass。原SAVE→FULL→DROP serial123/0ZERO，目的66run/FULL2772与独立42层恢复回读2772全bytespass，PRIVATE/PUBLISH/host释放/runner六checks/原consumer16/fast462/原preempt0→1完整。32-0/524288in32768out/230.82578303012997s/2413.317926131704total/TTFT62799.64288184419ms仅双回读诊断，KV521840/CPU6/32GiB；DB52319474物理dc2c7646-schema0dc7a465-logicalc05d7e31前后同，04:29:03.163250Z post68-0双栈闭无GPU进程，测前及shutdown ERROR皆空/forcekill WARN保留。maps严格guard成功是源码+成功SAVE证据，字典未入ACK不冒充直接实录。新SAVE与原FULL两组42byte证明各自核，不作吞吐gain/新accuracy或默认资格，不自动大官方/重复长pair，无旧run或测试重跑。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T042225Z-kv-pitched-save-context16k-long](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long)
- 原命令：[load-commands.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/load-commands.json)；[launch-command.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/launch-command.json)；[command.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long-control/command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/manifest.json)；[postflight-full.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/postflight-full.json)；[purpose.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long-control/purpose.json)；[source-sha256.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long-control/source-sha256.json)
- 原始结果：[context-16k-long-infqps-concurrency64-minicpm-20261022-122735.json](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/context-16k-long/results/context-16k-long-infqps-concurrency64-minicpm-20261022-122735.json)
- 日志 / 采样：[server.log](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/server.log)；[gpu.csv](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/gpu.csv)；[exit-code](../../../experiments/framework/20261022T042225Z-kv-pitched-save-context16k-long/exit-code)
- 相关说明：[2026-10-22-kv-pitched-save-system-deployment](../../../analysis/2026-10-22-kv-pitched-save-system-deployment.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
