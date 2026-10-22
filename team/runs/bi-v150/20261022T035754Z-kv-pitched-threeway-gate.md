<!-- 自动生成：python scripts/build_team_view.py；登记源 experiments/registry.csv -->

# 20261022T035754Z-kv-pitched-threeway-gate

平台：天数 BI-V150。本页只摘录既有登记；未记录字段不补猜。

## 登记 #114 · KV 二维 SAVE 复制

- **尝试**：保留KV字节和逻辑顺序的正等差复制；单层信号与真实42层诊断分开看。
- **改动**：相关实现 [biv150_kv_pitched_copy.py](../../../patches/framework/candidates/biv150_kv_pitched_copy.py)；[biv150_kv_pitched_bridge.cpp](../../../patches/framework/candidates/biv150_kv_pitched_bridge.cpp)；本轮准确变体以原件源码清单为准。
- **怎么测**：局部正确性或能力门；输入 / 输出 / 并发 / 请求数：未记录 / 未记录 / 未记录 / 未记录。
- **结果**：两case30checks+计后7+CPU-GPU RNG/独立CPU完整payloadSHA全部过
- **是否保留**：待确认；通过某项检查不自动等于优化保留。

<details><summary>完整原登记（含UTC、状态、过程与标识）</summary>

```json
{
  "run_id": "20261022T035754Z-kv-pitched-threeway-gate",
  "local_date": "2026-10-22",
  "utc_start": "2026-10-22T03:57:55.075804+00:00",
  "profile_id": "kv_SAVE_threeway_fixed64_cpu_stat",
  "phase": "isolated_gpu_threeway_API_byte_microtiming_gate",
  "device": "Iluvatar BI-V150",
  "vllm_commit": "",
  "flaggems_commit": "",
  "input_len": "",
  "output_len": "",
  "concurrency": "",
  "num_prompts": "",
  "profiler": "false",
  "status": "complete_two_case_threeway_byte_stream_pass_fixed64_cpu_observed",
  "artifacts": "experiments/framework/20261022T035754Z-kv-pitched-threeway-gate",
  "conclusion": "本agent唯一实际本地系统审计9d0bcd7b通过：86seal/7source/b2c6-9b16/818e-0a4d-c95f/compile0-so9e33ecbf15936B/ABI与mappedlibd39d/同非0stream94323367614720/maxpitch2147483647/DB实体/source-post/cleanup全核。两真实源页序一层构造R16928-P1058-17334272B与R16768-P1048-17170432B；A c95f37/26calls，B同桥C-linear37/26linear且pitched0/受控fallback9/4（非真实pitch不足），C同桥2D11(2+9)/6(2+4)且fallback0；两case30checks+计后7+CPU-GPU RNG/独立CPU完整payloadSHA全部过。首case固定64call A/B/C/C/B/A wall0.682748/0.655124/0.631449/0.631231/0.654983/0.689953ms，event0.679097/0.652385/0.628297/0.628323/0.652413/0.653521ms；每窗v1cpu.stat原值/差值/进程CPU时间保留，六窗nr_throttled与throttled_time增量均0，未倒推032653波动/不证无其它干扰。CPU6/56Torch线程/host20GiB均未更改；DB52319474物理dc2c7646-schema0dc7a465-logicalc05d7e31前后同，03:58:09.177091Z后态68-0双栈闭无GPU进程。仅一次单层三路局部成本信号，非42层服务/E2E/accuracy或稳定收益，不自动复跑；无候选/桥/测试重复。"
}
```

</details>

## 原件与说明

- 原始目录：[20261022T035754Z-kv-pitched-threeway-gate](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate)
- 原命令：[launch-command.json](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate-control/launch-command.json)
- 环境 / 源码 / 后态：[manifest.json](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate/manifest.json)；[source-sha256.json](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate-control/source-sha256.json)；[postflight.json](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate-control/postflight.json)
- 原始结果：[results.json](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate/results.json)
- 日志 / 采样：[worker.log](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate/worker.log)；[gpu.csv](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate/gpu.csv)；[exit-code](../../../experiments/framework/20261022T035754Z-kv-pitched-threeway-gate/exit-code)
- 相关说明：[2026-10-22-kv-pitched-threeway-035754-system](../../../analysis/2026-10-22-kv-pitched-threeway-035754-system.md)；[2026-10-22-kv-pitched-threeway-035754-hardware](../../../analysis/2026-10-22-kv-pitched-threeway-035754-hardware.md)
- 完整原登记：[registry.csv](../../../experiments/registry.csv)（登记序号见上；同一run可有多个阶段）
