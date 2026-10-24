# 实验记录阶段增量 PR：准备完成，未发布

现有 `scripts/publish_private_tree.py` 是整树快照并直接更新 main，不能用于本阶段协作维护。这里的新发布器只处理私有 `Silas-Zeng/FlagOS-Minicpm-S2`（固定仓库 ID 1427279927），从最新远端 main 建新的 `codex/` 分支与 PR；没有 main 更新、force 或自动合并入口。旧发布器未改。

计算明确的 `--base-local 8af67cc --accepted-maintenance-local ed86941 --target-local <阶段末commit>` 路径增量；旧发布 state 用于证明本地基点 tree 身份。远端路径等于本地目标就跳过，等于旧本地基点才应用；队友同路径不同改动、删除冲突或文件/目录冲突都保留并停止。其它队友路径/文件模式/内部 symlink 字节完整保留。只上传新增 blob，可复用远端已有对象；合成完整 tree 精确验 SHA 后才创建 commit/ref/PR，过程中 main 前进则要求重计划。没有复制整个旧本地 tree 去覆盖远端。

已实际离线准备 `ed86941-local-delta.json`：515 新增、8 修改、0 删除，共 523 路径，475 个不同 blob／10,002,185 字节；基点与目标 tree 都由叶子重算匹配 Git，新增字节凭据模式检查通过。**这不是实时远端 main 计划**。一次默认权限的只读 gh 元数据请求被网络权限拒绝，未读到实时 head，也没有 GitHub 写操作。后续新增 run 应先由root提交，再把 target 改为最终 commit；不将 ed86941 写死。

唯一离线 `check_plan.py` 已通过：保留队友路径、相同目标跳过、同路径/删除/文件目录冲突停止、无空 PR、executable/symlink 模式、禁止 PATCH main/错误 ref/merge API。`cpu-check.json` 是回执，**没有运行真实 Git Data API 写入、断线恢复或 PR 创建**；实际部署前由 root 定向审脚本即可，不重跑实验。

准备命令（项目根目录；本轮只执行了第一种离线模式）：

```powershell
python -X utf8 tmp/stage-pr-publisher/publish_experiment_pr.py --local . --published-state tmp/publish-team-rebuild-final-20261022.json --base-local 8af67cc --accepted-maintenance-local ed86941 --target-local <最终commit> --branch codex/experiment-records-<阶段> --output tmp/stage-pr-publisher/<阶段>-delta.json --offline-delta

# 仅GET实时远端main，保存可审计划；有冲突不会发布。
python -X utf8 tmp/stage-pr-publisher/publish_experiment_pr.py --local . --published-state tmp/publish-team-rebuild-final-20261022.json --base-local 8af67cc --accepted-maintenance-local ed86941 --target-local <最终commit> --branch codex/experiment-records-<阶段> --output tmp/stage-pr-publisher/<阶段>-plan.json
```

只有 root 决定发布时，第二条另加 `--publish-pr --state tmp/stage-pr-publisher/<阶段>-publish-state.json`；默认中文标题/正文，也可传 `--title`／`--body-file`。写模式仍重新 GET main，禁止用离线 snapshot 发布。成功会输出 PR URL，root 在当前任务挂接该 PR 后审阅/安排合并，脚本自身不合并。若 main/来源变化，保留 state 并换新分支/计划，不覆盖旧分支。CLI 的 `--remote-snapshot` 仅供离线计划复核，不能与发布组合。

PR state 不是“已合并发布水位”；不要在 PR 创建后就替换原发布 state。下一阶段仍可从同一 8af67cc 计算，已经合并的相同字节会自动跳过。只有确认 PR 已合并且来源对应后才另行推进水位，当前没有自动推进功能。Git 忽略的 raw SQLite/scratch 不在本发布器范围，仍由独立完整离线归档保存。

维护 PR 中间基点适配已冻结：显式 `--accepted-maintenance-local ed86941`，验证它位于 base→target 祖先区间，仅固定六文档可把远端完整 Git 条目等于该版本时继续更新；这六路径既不接受任意队友内容，也不退回接受旧 8af 版本。实际采用的路径列于计划 `intermediate_accepted_paths`。唯一新增 `check_maintenance.py` 已通过，见 `maintenance-check.json`；原合同不重复运行。本轮离线 ed869 例子有 475 个变化 blob，但相对最近完整发布树只有 67 个新 blob（7217336 字节）；live 计划仍以实际远端 tree 的对象交集复用，不新增并发上传。
