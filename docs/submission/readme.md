# MiniCPM5-2B 双平台复现说明

本项目在天数智芯 BI-V150 和沐曦曦云 C500 上分别运行 MiniCPM5-2B，均使用单卡、BF16 和 TP=1。两个平台共用模型、评测脚本和数据集。下文给出各自的服务启动命令。

优化实现和逐项 PR 见 [vllm-plugin-FL 框架仓库](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL) 和 [FlagGems 算子仓库](https://github.com/Silas-Zeng/FlagGems)。

## 1. 环境与目录

在对应平台的比赛镜像中运行，沿用镜像内的厂商版 PyTorch 和 Triton。C500 还使用镜像提供的 FlashAttention。

| 项目 | 天数 BI-V150 | 沐曦曦云 C500 |
| --- | --- | --- |
| GPU 显存 | 32 GiB | 64 GiB |
| 驱动与软件栈 | 驱动 4.5.0，CoreX 4.5.0，IX-ML 4.4.0 | 驱动 3.8.30，MACA 3.7.0.38 |
| Python | 3.12.11 | 3.12.11 |
| PyTorch | `2.10.0+corex.4.5.0` | `2.8.0+metax3.7.0.7` |
| Triton | 厂商版 3.6.0 | mcTriton `3.0.0+metax3.7.0.7` |
| vLLM | `0.24.0+empty` | `0.24.0+empty` |
| Transformers | 5.14.1 | 5.9.0 |
| EvalScope / datasets | 1.11.1 / 4.8.4 | 1.11.1 / 4.8.4 |

将提交包中的两个源码目录解压到 `/workspace`。模型及数据集使用比赛环境提供的副本。

| 内容 | 路径 |
| --- | --- |
| FlagGems 源码 | `/workspace/FlagGems` |
| vllm-plugin-FL 源码 | `/workspace/vllm-plugin-FL` |
| MiniCPM5-2B 模型权重、配置与 tokenizer | `/workspace/MiniCPM5-2B` |
| MATH-500 数据集（含 `test.jsonl` 和 `eval.yaml`） | `/workspace/evalscope-datasets/math_500` |

## 2. 安装

两张卡都先装 FlagGems，再装框架。以下命令直接从解压后的源码构建并安装 Python 包，保留比赛镜像里的依赖。

```bash
python3 -m pip install --no-build-isolation --no-deps /workspace/FlagGems
python3 -m pip install --no-build-isolation --no-deps /workspace/vllm-plugin-FL
```

需要边修改边验证时，可改用可编辑安装。

```bash
python3 -m pip install --no-build-isolation --no-deps -e /workspace/FlagGems
python3 -m pip install --no-build-isolation --no-deps -e /workspace/vllm-plugin-FL
```

安装后用同一 Python 环境检查框架和 DSA 算子模块的导入路径。

```bash
python3 -c "import flag_gems, vllm_fl; from flag_gems.fused.DSA import bin_topk; print(flag_gems.__file__, vllm_fl.__file__, bin_topk.__file__, sep='\n')"
```

## 3. 启动服务

在服务终端选择当前平台。两张卡均使用端口 9031、最大序列长度 131072、显存利用率 0.85。

### 天数 BI-V150

```bash
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --compilation-config '{"cudagraph_mode":"FULL_DECODE_ONLY"}' \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072
```

### 沐曦曦云 C500

C500 受测环境采用以下两项设置降低启动期间的主机内存峰值。主机内存充足时可省略这两行。

```bash
export MACA_HOST_MEMORY_POLICY=0
export TORCHINDUCTOR_COMPILE_THREADS=1
```

```bash
export VLLM_PLUGINS=fl
vllm serve /workspace/MiniCPM5-2B \
  --port 9031 \
  --served-model-name minicpm \
  --gpu-memory-utilization 0.85 \
  --max-model-len 131072
```

首次启动需等待编译和预热。在另一个终端执行健康检查，收到 HTTP 200 后再运行评测。评测期间保持服务运行，当前 GPU 仅用于本次测试。

```bash
curl --fail -sS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:9031/health
```

## 4. 性能评测

在单独的 Bash 终端中定义官方压测命令。每组参数依次为输入长度、输出长度、最大并发数和请求数。

```bash
cd /workspace
bench=(
  python3 /workspace/vllm-plugin-FL/benchmarks/benchmark_throughput_serve.py
  --model /workspace/MiniCPM5-2B
  --served-model-name minicpm
  --port 9031
  --test-cases '[[4096,1024,64,256],[16384,1024,64,128]]'
)
```

天数客户端直接执行下列命令。

```bash
"${bench[@]}"
```

沐曦客户端执行下列命令，将客户端 GPU 可见设备和插件列表置空，减少客户端占用的主机内存。设置仅作用于本次压测命令，服务端继续使用 C500 和 `fl` 插件。

```bash
env CUDA_VISIBLE_DEVICES="" MACA_VISIBLE_DEVICES="" VLLM_PLUGINS="" "${bench[@]}"
```

每个场景运行四轮，汇总后三轮的算术平均值。在 `/workspace/benchmark_results/raw_runs_*.csv` 核对各轮的 `Run Status`、成功请求数和 token 总数，在同目录的 `summary_*.csv` 查看 `Total tok/s` 和 `Mean TTFT (ms)`。只测 4K 时，将 `--test-cases` 改为 `'[[4096,1024,64,256]]'`。

| 场景 | 每轮成功请求数 | 输入 token 总数 | 输出 token 总数 |
| --- | ---: | ---: | ---: |
| 4K 输入 / 1K 输出 | 256 | 1,048,576 | 262,144 |
| 16K 输入 / 1K 输出 | 128 | 2,097,152 | 131,072 |

## 5. 准确率评测

性能评测结束后，保持服务运行，在评测终端执行同一条官方命令。每次生成新的结果目录。

```bash
eval_dir="/workspace/evalscope-results/level3/$(date -u +%Y%m%dT%H%M%SZ)"
evalscope eval \
  --model minicpm \
  --api-url http://127.0.0.1:9031/v1/chat/completions \
  --api-key EMPTY \
  --eval-type openai_api \
  --datasets math_500 \
  --dataset-args '{"math_500":{"dataset_id":"/workspace/evalscope-datasets/math_500","subset_list":["Level 3"]}}' \
  --eval-batch-size 8 \
  --timeout 3600 \
  --generation-config '{"temperature":1.0,"top_p":0.95,"max_tokens":32768}' \
  --work-dir "$eval_dir" \
  --ignore-errors
```

官方门槛为 95%，105 题至少答对 100 题。命令结束后，在 `$eval_dir` 下找到 `reports/minicpm/math_500.json`，核对 `execution_summary` 中的 `requested=105`、`succeeded=105`、`errored=0`，再读取准确率指标 `metrics` 中的 `score`。逐题生成和评分分别保存在同次运行的 `predictions/` 和 `reviews/`。

## 6. 已测结果

| 平台 | 4K 总吞吐（tok/s） | 16K 总吞吐（tok/s） | MATH-500 Level 3 |
| --- | ---: | ---: | ---: |
| 天数 BI-V150 | 7,135.08 | 5,254.02 | 101/105（96.19%） |
| 沐曦曦云 C500 | 12,276.94 | 10,757.13 | 103/105（98.10%） |

天数吞吐采用团队在另一台 BI-V150 上的整机实测，准确率来自最终框架的完整 105 题评测。沐曦吞吐取团队两次实测的均值，准确率来自该平台的完整评测。[天数官方准确率报告](https://github.com/Silas-Zeng/FlagOS-Minicpm-S2/blob/049d0a71ad5b4ba6b2939e7d55fced8f0878bdd8/experiments/accuracy/20261120T082740Z-final-main-accuracy/math_500.json)
