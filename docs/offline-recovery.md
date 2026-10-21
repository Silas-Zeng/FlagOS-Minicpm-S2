# 离线保存与 API / 团队接续

工作 ZIP 保存项目中的代码、补丁、原始实验、SQLite、分析、子智能体交接和本地 scratch。它不是聊天记录导出，也不包含模型权重或远端整机镜像。先读 `CURRENT_WORK.md` 顶端的最终状态和 `docs/agent-work-index.md`；用户已冻结新探索，不能按历史待办自动重开实验。

`HANDOFF_FILE_MANIFEST.json` 列出各文件的 SHA256、大小、mtime 和模式；外置 summary 给出 ZIP SHA256 与 CRC 检查结果。归档自身、`.git`、运行环境缓存和凭据类文件不重复装入 ZIP。`tmp/pdfs` 中既有源脚本一并保留。合法的项目内部符号链接以 ZIP symlink entry 和 manifest target 双重保存；Windows 解压工具可能把它们解成普通文本，恢复时须按 manifest 核对，不可把链接文本当 JSON 配置。

归档只执行有限的凭据模式检查，不能视为适合公开发布的证明。此包供本地恢复和团队受控交接；GitHub 提交应选择代码和必要记录，大型原始证据与 bundle 独立保管。既有参考仓库只读，发布只使用本实验新建专用仓库。

## 已保存的 Git 恢复材料

`recovery/git/` 被 Git 忽略，但进入工作 ZIP：

- `experiment-history.bundle`：保存记录仓库的 refs 与 HEAD。此前 main 为 `c07eea19d88ce3f7f57d49f7fcb624fb3e3a3489`、可达历史 9 个提交的快照已离线 clone 核验；最终更新由主负责人完成，恢复时以配套状态文件及最终校验记录为准。
- `plugin-base.bundle`：完整补丁重建所需的本地参考对象，原版 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，原 tree `649161e62191e81a4b367e0e19dc37e32e745099`。
- `plugin-base-shallow-boundary.txt`：参考库原本就是 shallow，仅包含这一边界提交及其源码，不能恢复不存在的更早历史。
- `flaggems-team.bundle`、`flaggems-team-shallow-boundary.txt`：团队共用 FlagGems 代码副本的可达对象、refs 与实际浅库边界。
- `plugin-team.bundle`、`plugin-team-shallow-boundary.txt`：团队共用 vLLM 插件代码副本的可达对象、refs 与实际浅库边界。
- `*-head.txt`、`*-refs.txt`、`*-status.txt`、`*-index-stage.z`、`*-staged.patch`、`*-unstaged.patch`：源码状态与文件模式。最终未提交文件字节以 ZIP 为准；不要在已叠加最终文件的目录再次应用 diff。
- `git-state-manifest.json`：以上状态的身份及 bundle 的 SHA256；`offline-*.json` 保存实际恢复命令和成功/失败原件。

`scripts/save_git_handoff_state.py` 现在覆盖记录库、原插件基点及两个团队代码副本，保存 HEAD、HEAD tree、refs、浅库状态、可达提交数、index 和 diff。每个 Git 子进程只为当前明确的仓库路径设置 `-c safe.directory=<该仓库绝对路径>`，不设置通配信任、不写全局 config，也不访问远端。脚本不会创建或刷新 bundle；最终打包前仍需由负责人更新相应 bundle，再运行状态保存，核对版本相符。

普通 clone `plugin-base.bundle` 会因缺少 shallow 边界而失败；此失败已记录。正确办法是在**全新目录**初始化 Git，先写入 shallow 文件，再 unbundle 并检出已知基点。已用这一方法离线恢复、通过 `git fsck`，并在恢复对象上应用完整4aba补丁得到精确候选 tree `5c14cfb8d3a452e97a67758873bf18039e1bf989`，逆向应用也精确回到原 tree。

## 恢复参考源码的示例

下面路径均为占位符；目标必须是全新目录，不能覆盖当前工作目录：

```bash
git init /new/plugin-reference
cp /restored/recovery/git/plugin-base-shallow-boundary.txt /new/plugin-reference/.git/shallow
git -C /new/plugin-reference bundle unbundle /restored/recovery/git/plugin-base.bundle
git -C /new/plugin-reference config core.autocrlf false
git -C /new/plugin-reference checkout --detach 13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0
git -C /new/plugin-reference fsck --no-reflogs
```

Windows 无创建 symlink 权限时，在 checkout 前设置 `core.symlinks false`，按 Git index 保留120000模式并使用链接占位文件；受测完整补丁重建工具已按这种模式校验。`analysis/source/sql-mixed-full/rebuild_full_patch.py` 的参考路径固定为项目内 `tmp/src/vllm-plugin-FL`，恢复后必须使该路径具有上述原始对象。无需联网拉取新的框架版本。

根仓库可从 `experiment-history.bundle` clone 到另一空目录，核实 HEAD 后再结合 ZIP 的工作文件及状态恢复未提交内容。`.git/config`、认证信息、工作树锁和设备进程不会恢复。即使交接记录写设备空闲，后续使用前仍须实时核对。

## 两个私有代码库的本地历史与远端快照

两个代码库由团队共用，不按平台拆分。实验记录库才按 BI-V150 与 C500 分平台归档。主负责人已核验以下 GitHub main；远端使用初始化 README 提交作为 parent，通过 API 发布完整源码快照，因此本地与远端 commit 不同，但 Git tree 完全相同。不能用 commit 不同推断源码不同，也不能用 tree 相同宣称提交历史相同。

| 代码库 | 本地提交 | 已发布的远端 main | 相同的 Git tree |
|---|---|---|---|
| FlagGems | `6ddb4c4cd12790cfc7b1203bdca2ed7a131f7dd6` | `d7e5cef98344cd068df2e425748f849c94681048` | `e8ba50863b7bfabc725cc6aaff97d3548d7daf0f` |
| FlagOS-S2-vllm-plugin-FL | `70d04f38382e900949ddeb34d2ac75aacdc93af4` | `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c` | `82e37f8f263eeb09563a4790359ec95a0de1ca17` |

本轮 bundle 保存本地 refs 可达的历史，不包含 GitHub 新初始化提交及 API 发布提交对象。恢复源码时检出表中的本地提交并核对 tree 即可；不能要求离线 bundle 检出其中未保存的远端 commit。远端 private 可见性、访问权限和认证也不会随 bundle 恢复。

### 实际保留的历史范围

- FlagGems 本地分支为 `codex/team-collaboration`，其 parent 为固定的 `v5.3.5` revision `4df52d9168ac55c1c1061cefb4638c570292d896`。全部 refs 可达 3,298 个提交，HEAD 可达 52 个；包含现有 tag 与本地 remote-tracking ref，但这不是完整上游历史。本地浅库边界为 `0db588057a4aac1a35b3cde44d1fc7f5159fc3d0`，原文件重复记录该值两次，已按原始字节保存。不要把存在其他版本 tag 当作本实验已升级源码的证据。
- 插件本地分支为 `main`，可达 2 个提交：原 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` 和本地团队提交。浅库边界为该原基点，不能恢复边界之前的上游历史。
- 两份 bundle 均使用本地 `git bundle create <新文件> --all HEAD` 生成，没有覆盖旧 `experiment-history.bundle` 或 `plugin-base.bundle`。对应 SHA256 见 `git-state-manifest.json` 与 `offline-team-code-bundles-check.json`。

### 最短离线恢复

两份团队代码 bundle 都需要先恢复配套 shallow 文件；不要直接普通 clone。下面以插件为例，所有路径均为占位符，目标必须全新：

```bash
git init /new/plugin-team
cp /restored/recovery/git/plugin-team-shallow-boundary.txt /new/plugin-team/.git/shallow
git -C /new/plugin-team bundle unbundle /restored/recovery/git/plugin-team.bundle
git -C /new/plugin-team config core.autocrlf false
git -C /new/plugin-team checkout --detach 70d04f38382e900949ddeb34d2ac75aacdc93af4
git -C /new/plugin-team rev-parse 'HEAD^{tree}'
git -C /new/plugin-team fsck --no-reflogs
```

恢复 FlagGems 时同样初始化全新目录，改用 `flaggems-team-shallow-boundary.txt`、`flaggems-team.bundle`，检出 `6ddb4c4cd12790cfc7b1203bdca2ed7a131f7dd6`，预期 tree 见上表。Windows 无 symlink 权限时仍需在 checkout 前配置 `core.symlinks false`，按 Git index 保留原链接模式。

`bundle unbundle` 会解包对象并打印 refs，不自动安装分支或 tag。若需要原 refs，按 `bundle list-heads` 或保存的 `*-refs.txt` 对每个非 HEAD 项执行 `git update-ref <ref> <sha>`；HEAD 则通过 `git symbolic-ref HEAD refs/heads/<原分支>` 恢复，或保持示例的 detached checkout。不要把 HEAD 当普通分支 ref 写入。

实际验证记录在 `offline-team-code-bundles-check.json`：两个全新本地目录先写入原浅库边界，再 unbundle，安装全部 refs、恢复 HEAD 指向，核对完整 refs、HEAD、tree、全部及 HEAD 可达提交数，执行 `bundle verify` 和 `fsck --no-reflogs`，全部通过。FlagGems 为含 HEAD 的 30 项 refs，插件为 2 项；本次验证未 checkout 工作文件，验证的是可完整读取的 Git 对象和历史边界，不是重新运行代码或设备实验。原两个代码副本的工作树和 refs 未改，旧 root/base bundle 的 SHA256 也保持不变。
