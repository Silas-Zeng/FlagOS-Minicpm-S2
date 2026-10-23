# 发布准备与切换 API 交接

2026-10-23 UTC（本地已10月24日）：本子任务仅CPU本地准备，无GitHub/SSH/GPU写入。用户已再次明确删除不合理的旧只读要求，三私有协作库继续维护；root已更新AGENTS，并以新授权说明重试同一P分支push，审批通过、push成功。root随后已通过connector创建并attach [Draft PR #21](https://github.com/Silas-Zeng/FlagOS-S2-vllm-plugin-FL/pull/21)。旧审批问题已经解决，不要重试push或重复创建PR。

**实验PR2复用入口。** 已验回执 `archive/github/20261023-math4-event-update.json`：本地发布基点 `c01f660eb57e94bfa8d438bd0fc63694380d4a31`，远端parent `84678bde9dddd674d83eaecfb87369e3b40cc6b9`，tree `33c1449903832de3d3c3b7e0123881f53c679e75`；本地基点tree已核相同。固定私有库 `Silas-Zeng/FlagOS-Minicpm-S2` / ID1427279927、PR2、分支 `codex/framework-experiments-20261022`，main仍应为 `f75b549a44a0f3cf35da3923766a2cc6b69ae6ee`。

root先完成206条/203run、本批官方摘要、CURRENT及交接，并只暂存展开原件与明确文档路径，保存最终完整commit；不要 `git add -A` 纳入当前未跟踪tgz。然后在workspace根运行：

```powershell
$batch = 'archive/github/20261023-current-main-official-batch'
$target = '<root最后保存的40位commit>'
C:\ProgramData\anaconda3\python.exe "$batch/prepare_local.py" --target-local $target
```

该脚本只读Git、复用已审 `scripts/publish_experiment_pr.py`（SHA256 f8e88196…）的tree/增量凭据扫描，检查206/203与官方8原行/2摘要；拒绝本轮新增/修改压缩包、gitlink和本地镜像路径。产出 `publish-plan.json`、`commit.request.json`、`body.request.json`；未得到root最终target前没有执行扫描计划。新正文位置是 `$batch/body.md`，**不再使用旧tmp/stage-pr-updater-20261023/body.md**。

对象传输沿用上一轮 `tmp/upload_compute_retest_git_objects.py`（SHA256 `50abf43fb453d527fd955ceaf8189f50245ee520cbf34729473fe21cbb2c6d58`），已经本地复制为 `tmp/upload_current_main_official_git_objects.py`（SHA256 `b3666ef01b9ab9ca54d9f583b42c625642a13daff7b8f91c6fd61928159e2188`）。只替换两处路径：state目录改为 `tmp/current-main-official-api-upload`，plan改为本批 `publish-plan.json`；字节级确认其余未改，AST通过，**尚未执行**。保留2线程、间隔、state续传及tree核对，不重写上传器、不复用旧state。root在准备器成功及实时身份复核后运行 `C:\ProgramData\anaconda3\python.exe tmp/upload_current_main_official_git_objects.py`。它仅上传对象/树、不移动ref；执行与后续远端写由root负责，不影响已发布的代码PR21。

原上传完成后，root复查仓库ID/private、PR2开放/head=84678bde、base=main、main=f75b549a及上传state.tree=plan.verified_tree，再按既有流程：

1. `gh api --method POST repos/Silas-Zeng/FlagOS-Minicpm-S2/git/commits --input "$batch/commit.request.json"`，保存返回commit；请求唯一父已固定84678bde，**不会发布root本地commit历史**。
2. 再次核head/main未变；以结构化JSON `{"sha":"<返回commit>","force":false}` PATCH `repos/Silas-Zeng/FlagOS-Minicpm-S2/git/refs/heads/codex/framework-experiments-20261022`。断线先读ref/state确认，不重复猜写；远端变化即重新计划，不覆盖。
3. `gh api --method PATCH repos/Silas-Zeng/FlagOS-Minicpm-S2/pulls/2 --input "$batch/body.request.json"`。核head、唯一父、完整tree、正文、main未变、未合并；回执写 `archive/github/20261023-current-main-official-pr2-update.json`，记录最终local_target与206/203。不新建重复实验PR，不触碰队友PR3。

**计算顺序代码PR。** root已成功push `collaboration/FlagOS-S2-vllm-plugin-FL` 的 `codex/biv150-compute-order`：commit `4fca58bad0c7e3ed73e59ed2c7749bb2511b6813`，唯一父 `3283672b92fa30f93f652b242193999836a95f88`，tree `5c77e68caff6aa0c8b6c230adb78a2d4c293cca1`，仅runner/helper两文件；三项已本地重读一致。不要从workspace根仓库push，不重建或重复推送此受测commit。

**Draft PR21已经创建并attach**，head4fca58ba/main328不变，中文正文已补最终官方4K5116.68/16K3436.04绝对结果、gain=null及完整准确率103/105但P0限制。原正文位置仍为 `archive/ai/20261022-framework-kv/compute-order-pr/PR正文.md`；实验批次正文已加入PR21链接。root继续补实验PR2发布后验与最终CURRENT；PR20属于队友且测试未通过，不合并。代码main如变化即停止重核，不改受测tree或放宽来源。

已完成验证：上一批本地base tree与回执相同；P分支commit/tree/唯一父相同；发布器/上传器pin相同；新准备器AST/--help与UTF-8检查通过。待root完成：最终target与增量扫描、实验PR2发布后验及最终CURRENT。不要为发布重跑原105题、官方CSV验证、封存或逐原件hash。
