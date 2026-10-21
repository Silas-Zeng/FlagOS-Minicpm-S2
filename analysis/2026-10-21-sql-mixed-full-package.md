# SQL+C3 fallback candidate：从原13eb一步应用的完整补丁

独立交付文件为
[`vllm-plugin-FL-biv150-sql-mixed-decode-full.patch`](../patches/candidates/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch)，
SHA256 `4aba147aa0bd3ec8dd1c12b6ae94bf39537a4cbad449e68e2fcdbfbdc0f8def6`。
它将已存在的 retained performance + SQL/C2/C3 联合增量压成一份普通 Git diff；
只在原 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` 上应用一次。
原默认 `patches/vllm-plugin-FL-biv150-performance.patch` 和既有增量均未改。
本次没有新增性能实现，没有加入 bucket、growth、hidden-gather、overlap 或 prefix-mask。

在新建、可写的独立实验 checkout 中使用；已有参考仓库继续只读：

```bash
git -C /path/to/new-experiment-checkout checkout --detach 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
git -C /path/to/new-experiment-checkout apply --check /path/to/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch
git -C /path/to/new-experiment-checkout apply /path/to/vllm-plugin-FL-biv150-sql-mixed-decode-full.patch
```

这是 `git apply` 格式。使用完整补丁后不再叠 retained、SQL、decode-launch 或 mixed 增量。
安装和服务命令仍见 [`docs/candidate-usage.md`](../docs/candidate-usage.md)；
本地包装过程没有运行安装、框架 import、SSH 或设备操作。
当前原13eb官方基线独占设备期间，禁止远端导入此候选：retained runtime 会持久修改已安装 Attention。

重建只读输入为：

| 输入 | SHA256 / 固定身份 |
|---|---|
| 本地 `tmp/src/vllm-plugin-FL` Git commit object、HEAD | `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` |
| retained performance.patch | `6e8d9fa631b7e2f9aa0a848443e602c224c1bbd1f0787b417f78dd3b9f51e99b` |
| SQL+C3 joint delta | `4b3e2e52b01d04a0f0477ae4e9b8dc3fed3c1f721360af3bbe6b01014572bbba` |
| 完整源码归档 | `experiments/official/20261021T092944Z-sql-mixed-official/source/plugin` |
| 原080656核心身份 | `experiments/framework/20261021T080656Z-sql-mixed-screen/manifest.json` |

080656 短测原件只记录核心文件 SHA，没有完整 plugin tree。
092944 官方 manifest 的 source_dir 明确仍为
`/workspace/experiments/minicpm-s2/code/sql-mixed-20261021T080656Z`；
本次以该完整归档逐项比较，并另外验证原080656全部六个 plugin 核心 SHA。
全部212个归档内仓库文件 bytes/SHA一致，另核 `base-revision.txt` 为 retained d60 的原始归档元数据；
该文件不是13eb Git tree里的源码，不加入补丁。

内部 MoE JSON alias 在 Git 中继续为 `120000`，link target blob 与原13eb完全相同。
Windows scratch 使用 Git symlink placeholder，但完整 diff 与候选 tree 保留原模式。
归档 copytree 曾解引用该链接；对照其实际目标 JSON bytes，而不把解引用副本当作新文件类型提交。
完整补丁仅修改预期9个Python文件、增加988行，没有 JSON/config diff。

包装 CPU 验证已完成：新 scratch 从13eb依次应用两个原补丁；
另一个新 scratch 一步应用完整补丁，全部 Git index blobs/modes 和 tree identity 完全相同；
再逆向应用精确回到原13eb tree。变更的Python文件仅做 `compile`，不执行模块。
候选 tree 为 `5c14cfb8d3a452e97a67758873bf18039e1bf989`。
逐文件SHA/模式、symlink语义、原080656身份和精确命令均保存在
[`rebuild-manifest.json`](source/sql-mixed-full/rebuild-manifest.json)。
初次 scratch 为 `tmp/patch-check/sql-mixed-full-20261021T124036892175Z`。

可用纯本地脚本重新检查已交付补丁；它只在新tmp scratch中复建，不覆盖已有补丁或输入：

```bash
python analysis/source/sql-mixed-full/rebuild_full_patch.py --verify-existing
```

该包装复现的是原080656候选：其独立准确率090505为103/105，
092944官方两档绝对结果为4K 3683.65 total tok/s、16K 2729.07 total tok/s。
包装没有重跑或新增准确率/设备证据，原13eb matched总体提升仍待当前官方基线结束并验收，
不能据此声明总体增益或比赛分数。该完整补丁作为fallback交付，默认补丁仍未覆盖。

hardware owner 已独立执行一次 `--verify-existing`，exit0、3.69s，完整补丁 bytes 确定性一致，
全部逐项/全tree/逆向恢复/原symlink语义与9文件988新增均通过；新独立scratch为
`tmp/patch-check/sql-mixed-full-20261021T124556037704Z`。
独立结论另存 [`hardware handoff`](../docs/agent-work/hardware_innovation.md)，无包装交付阻断。
