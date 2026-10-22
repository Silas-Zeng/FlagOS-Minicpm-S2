# CPU metadata、异步 token 更新与 KV 工具的组合审阅

本次双向实际三方文本合并均只出现 **一处 import 冲突**，没有方法体冲突。保留两条原作者 import 后，两种顺序得到同一份 runner；AST 编译和字节逆变换通过。此结论只说明文本可组合，**不代表组合已上卡、通过准确率或具有叠加收益**。

固定基点为本地 commit `70d04f38382e900949ddeb34d2ac75aacdc93af4`、tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`；与作者材料所引用远端 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c` 同 tree。基点 runner 的 blob 为 `5288f44709edb1334db697d2bac77715711899f8`，SHA256 为 `e155a16669e69b7eb7aff370dbcbcf225a4f593fa42b2399722e96999b53a1f1`。基点已有 prefill、top-p、SQL 和 C3，是一次完整代码快照，不能描述为这些方法分别已有合并 PR。

## 实际合并结果

用固定基点 runner 作 BASE，对两份作者 runner 执行 `git merge-file --stdout --diff3`；没有 checkout 或修改 Git 索引。

| 顺序（CURRENT → OTHER） | exit | 冲突块 | 冲突输出行 | 其余逻辑 |
| --- | ---: | ---: | --- | --- |
| metadata → async | 1 | 1 | 22–27 | 两处方法改动自动合并 |
| async → metadata | 1 | 1 | 22–27 | 两处方法改动自动合并 |

冲突原件及完整命令分别保存在 `combination-artifacts/metadata-then-async.merge.txt`、`async-then-metadata.merge.txt` 和 `merge-attempts.json`。exit 1 是文本冲突，不是设备或测试失败。冲突来源是两方都在 `import torch` 后插入 helper import。解决只需同时保留以下两行（本材料固定此顺序）：

```python
from vllm_fl.patches.biv150_cpu_metadata import try_cpu_metadata as _biv150_try_cpu_metadata
from vllm_fl.patches.biv150_async_token_update import fused_sampled_token_update as _biv150_fused_sampled_token_update
```

已保存完整解决文件：

`docs/pr-preparation/combination-artifacts/resolved/vllm_fl/worker/model_runner.py`

其 SHA256 为 `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`，Git blob 为 `907fa58d3a74dc13c23936e6effb54043073bbdf`。两方向解决结果逐字节相同。

## 可应用的最小材料

下面两份 unified diff 都只修改 `vllm_fl/worker/model_runner.py`，从对应单方法版本补入另一方法；已在内存逐行验证全部上下文并重建上述同一结果。它们没有实际应用到共享 checkout。

| 当前单方法 runner | 使用补丁（相对实验库根目录） | 补丁 SHA256 |
| --- | --- | --- |
| metadata `50493fb68b194ed935650a3a743d2f56696d7379b702f4d7717eecac0325a9de` | `docs/pr-preparation/combination-artifacts/metadata-then-async-resolved.patch` | `382356e3aedce033c69561e7da6a734fc968539cb1b5962fea70e3ff1c4b0a7d` |
| async `f0d0bada4222038b69ed139d804622e27acd6aa4e19a37ff089b0ca35f393f41` | `docs/pr-preparation/combination-artifacts/async-then-metadata-resolved.patch` | `b78334737d3b9e513c887ea69a3323390270872f5a8e4e09868f1bb4aa8081b8` |

在包含对应单方法的代码分支根目录，先核当前 runner SHA，再按需要使用其中一份；以下只是给维护者的指令，本审阅未执行：

```powershell
# 当前已经是 metadata 单方法版本时：
$experimentRoot = 'C:/Users/Administrator/Documents/ChatGPT/MiniCPM 模型推理吞吐性能优化'
(Get-FileHash -Algorithm SHA256 -LiteralPath 'vllm_fl/worker/model_runner.py').Hash
# 必须等于上表 metadata SHA，且文件没有冲突标记。
git apply --check "$experimentRoot/docs/pr-preparation/combination-artifacts/metadata-then-async-resolved.patch"
git apply "$experimentRoot/docs/pr-preparation/combination-artifacts/metadata-then-async-resolved.patch"
```

若当前是 async 单方法版本，将补丁文件名替换为 `async-then-metadata-resolved.patch`，先核其对应 SHA。**若已处于 Git merge 冲突状态，不对带标记文件应用补丁**；从已保存的 `resolved/vllm_fl/worker/model_runner.py` 复制覆盖冲突的这一文件，再由维护者审 diff、核上述组合 SHA、`git add -- vllm_fl/worker/model_runner.py` 完成解决。

两份补丁不是独立安装器：组合树还必须包含两原 PR 各自新增的 `biv150_cpu_metadata.py`、`biv150_async_token_update.py` 及各自方法文档。在实际合入两个原 PR 时这些独占新增文件应一并保留；只拷 runner 会缺少依赖模块。

## AST、守卫与证据范围

两项唯一改动方法分别为 `ModelRunnerFL._prepare_inputs` 和 `ModelRunnerFL._prepare_input_ids`，没有方法名交集。组合中前者逐字节等 metadata 作者版，后者逐字节等 async 作者版；所有其余函数 AST 与基点相同。移除 async 的一个 import 和该方法改动后，精确恢复 metadata runner；反向同样精确恢复 async runner；再撤另一改动精确回到基点 e155。这也保留了原 input-prep event 方法、C3 footer 及所有其它基点字节。

作者包中六份 Python 快照及组合 runner 仅做 `compile(bytes, ..., 'exec')`，没有执行或导入。两 helper 模块保持各自受测原件完整 SHA，因此配置、capture、映射唯一性、tensor/storage 与 metadata 依赖 SHA 守卫均未修改；原条件回退表达式也保留。metadata 的两个依赖 SHA 仍为 `de1ea4fc...`（input batch）和 `4e4cda20...`（utils）。没有改 init、stream 或采样算法，也没有声称静态检查足以证明组合运行时的事件/缓冲区正确性。

作者已有单方法短筛信号分别保留在各自 PR 材料：metadata 吞吐约 `+0.286723%`、TTFT 约 `+0.234431%`（变慢）；async 吞吐约 `+0.703657%`。不相加、不作为稳定官方成绩；组合没有设备/准确率结果，旧 SQL+C3 的 `103/105` 不继承。已有设备证据仅 BI-V150，不代表 C500。

## 两个 KV 工具及 PR 次序

四包共 11 个文件记录、10 个不同目标路径，唯一重叠是上述 runner。两个 KV 包的目标文件全部在固定基点不存在，与 CPU 两包及彼此均无路径交集：

- 连续页工具只增加 `vllm_fl/patches/biv150_kv_page_copy.py`（`c95f59a5...`）与独占中文文档。
- 二维 SAVE 工具只增加 `vllm_fl/patches/biv150_kv_pitched_copy.py`（`818e788b...`）、桥源码 `biv150_kv_pitched_bridge.cpp`（`0a4d44d8...`）与独占中文文档。

实际 AST import 列表证明两 KV 模块不 import 对方；作者 manifest 的 `required_prs` 均为空。四份包的完整文件 SHA、Git blob、尺寸、源字节及 KV 唯一作者引用报告的哈希均已核对，详见同目录 JSON；没有重跑设备验收。KV 两 PR 可任意次序，不要求 CPU PR 先合；两个 CPU PR 也没有语义前置依赖，但后合者需要解决上面的一处 import 冲突。KV 工具没有默认服务 hook，二维工具不交付 SO；提交信息不等于完成 ACK，生命周期与失败 settle 仍由调用方保证。

本审阅只写组合审计材料和本 agent 交接，四位作者材料逐 byte 保持；共享 checkout HEAD/status 前后相同，没有修改分支、索引或远端。没有运行 Torch/Triton、候选模块、测试套件、C++ 编译、CDLL、GPU、SSH 或 GitHub 操作。实际 Draft PR 的创建和链接由 root 维护，本材料不补造链接。完整状态及各项 SHA 在 `docs/pr-preparation/combination-review.json`；本轮审阅完成后停止文件写入。
