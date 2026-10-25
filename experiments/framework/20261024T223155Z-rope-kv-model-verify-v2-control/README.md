# RoPE＋KV 第二版同服务门

首次 211606 四语义正确，但旧解析器没有沿实际 FX 子模块的实参/返回值追踪 Q/K/dep，同时源码目录多出 autotune 元数据，原运行保留失败。此入口绑定独立 528 tree `4e2f52ce47382fe4d1ef13317c3e171ab922cd27`，生产修正只把元数据移到 Torch 外部缓存；不放宽源码闭包检查。

新解析器沿真实顶层调用传播子模块形参、tuple 返回和 view，逐层要求 42 融合的 0/1/2 输出接到同层原 Attention，拒绝未调用定义、重复调用、错误依赖和旧 KV update。211606 原始 FX 的回放及七个负例见 `graph-replay-cpu.json`；这只是旧图静态分析，不能把旧状态改成功。

```bash
python3 verify_service.py \
  --source-dir /workspace/experiments/minicpm-s2/code/替换为已解压v2源码目录 \
  --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

原 SERVER、同服务四语义（长输入至少 4096）、34 native、FP/AOT、锁/实时空闲、6 秒所属进程清理和 DB 恢复原样复用。owner 只换新 tree 与 run 名；不重跑 49 组件或 32 请求 swap 验证。首次核当前真实新图，不要求旧图 SHA；未来同源 `--prior-control` 复用才要求相同 FP/FX/AOT。实际 v2 模型验证尚未运行。

增量检查：真实 FX 八项回放/负例、实装 cache API 三项定向 CPU、owner 仅 tree/run 名的逐字逆回均通过。community 编写的新解析器经 resume 独立审阅，生产缓存改动经 teammate 审阅；不扩展或重跑旧数学/生命周期套件。
