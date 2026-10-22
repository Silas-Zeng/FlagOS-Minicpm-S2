# GitHub 原始基线与方法 PR 重建：定向审阅

**建议按root当前方案推进，不改已有四个PR head，不force。** main以当前已发布完整快照为父提交，追加“恢复13eb源码及中文首页”的提交；六个历史方法增量从该恢复提交向前建立PR链。CPU #1/#2改指这条链末端、代码已回到原SQL+C3的集成分支；KV #3/#4继续指main。没有必要先重写四个head或补造历史合并。

本审阅只核祖先/三方合并机制，复用已核源码和两owner盘点，不重审DB/设备、不执行远端或分支操作。以下身份来自本地Git对象与既有发布回执，不冒充本次GitHub实时回读。

## 固定身份及必须成立的祖先关系

- 原始框架：`13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`，tree `649161e62191e81a4b367e0e19dc37e32e745099`。
- 旧完整快照 F：远端 `d5e2e3a54b48dcb1b50f575d2420979591fb3e1c`，tree `82e37f8f263eeb09563a4790359ec95a0de1ca17`；本地同tree为 `70d04f38382e900949ddeb34d2ac75aacdc93af4`。旧CPU runner为e155。
- R：新恢复提交，**parent必须是当前F**（若远端已经前进，先读回真实head再重算，不能对过期head强推）。R的非首页文件/mode/blob应逐项等13eb，例外只允许明确列出的中文README及原首页存档；不能在基线默留任何新增优化模块或实验开关。
- S：六方法链末端，必须是 `F → R → 六个新方法增量 → S`；S相关代码须精确回到F，而不是只“功能接近”。README/迁移说明差异另列。

这个非force方案改变的是当前main的源码树，不抹除已发布历史。若“开始”还要求过去第一提交也变成原始13eb，那需要另建仓库/新历史，不能假称一次追加恢复已经改写过去；本轮不做此事。

## 为什么旧 KV head 可以保留

硬件owner已核PR #3/#4全部新增路径在13eb不存在，两工具互不import，也不依赖CPU/SQL/C3；完整KV事务的依赖不能套给这两个工具。三方合并中：base为F、ours为R、theirs为旧KV head K。K对F只新增独占文件，故保留ours的源码恢复，新增工具文件；不把被R撤回的SQL+C3再带回。

GitHub三点diff是共同祖先F到K，仍应仅#3的2文件/#4的3文件。**不能仅凭页面文件数就接受**：root在实际R产生后，用下面最短Git门确认mergebase、合并无冲突以及结果相对R仅那些新增文件即可，不需新设备测试或重复作者审计。中文PR正文补清新main基线和历史实测上下文，head可原样保留。

## CPU retarget 的前提与一个易混淆点

旧CPU head H基于F。只要S由上述R继续，F仍是S的祖先，且旧H在F处分叉，`merge-base(S,H)=F`；GitHub `S...H` 就仍只显示各自三文件。S的runner/相关代码与F相同，三方合并保留S的新首页/历史，应用CPU一处条件包装和独占模块，既有受测50493/f0d0文件可保留；组合6f918及062205/070004–070452证据不因改PR base而变成新基线准确率。

**若六方法链直接从13eb原commit另起，而不从R继续，上述条件不成立。** 此时可能mergebase退回13eb或无公共祖先，旧CPU diff会带完整历史包；不能直接retarget后就宣布三文件。最省事是让新链从R建立。只有实际祖先门失败且决定不调整新链时，才考虑新head/双parent桥接等额外操作，不预先增加这些工作。

把S分支仅指向旧F可作为历史review参照，但F已是R祖先，不能再靠“合入F”向R重新引入方法。真正每项PR必须是R之上的新提交。CPU方法逻辑不必算法上依赖SQL/C3；这里选S作base，是保持现有受测head与审阅范围、避免另做无必要的新适配。#1/#2最后相互合并仍保两条helper import；既有组合材料直接复用。

## 最短验证条件（root执行，本审阅未执行）

下面R、S、K、H都应替换为刚回读/构造的真实SHA，不是新造的ref。只用已有对象；`merge-tree --write-tree`会新增Git对象，但不改checkout/index/分支，可在专用审计clone执行。

```bash
# KV：K取#3或#4真实head。
git merge-base "$R" "$K"              # 必须为F
git diff --name-status "$R...$K"       # 仅该KV工具的2/3个新增文件
git merge-tree --write-tree "$R" "$K" # exit0，首行得到结果tree T
git diff --name-status "$R" "$T"      # 仍仅上述新增文件；其mode/blob等原manifest

# CPU：H取#1或#2真实head。
git merge-base "$S" "$H"              # 必须为F
git diff --name-status "$S...$H"       # 仅runner+本方法runtime+独占文档
git merge-tree --write-tree "$S" "$H" # exit0；检查结果runner及新增文件等原作者blob
```

再做一次最终树检查即可：R除明确首页白名单外等13eb；S的九代码文件及其它非首页原文件等已验F；六个PR各自相对直接base只有清单内方法增量。GitHub读回新main/head/base/changed-files，确认仍Draft/未合并、diff未夹带其它方法。两个KV新增路径的完整manifest、两个CPU的原blob/组合冲突解决均已审，不重复测试。

## 安全迁移顺序与证据口径

1. 先从真实远端head建立永久快照branch/tag，保留F、四个PR URLs/head/tree及既有发布回执；不删除旧快照/PR/实验材料。
2. 以F为parent建立R，完整复查原13eb树及首页白名单，正常nonforce更新main。若main已被别人推进，停止使用旧parent并重新核对，不覆盖他人提交。
3. 按framework六项真实增量建立Draft链：诊断/配置支持、prefill、top-p、SQL反射、3D decode launch、mixed分流。prefill/top-p共用runtime产生包装依赖，可堆叠；不要声称这些历史组合已逐项独立验收。默认关闭开关也应单列，不能埋进五方法或冒充已证性能优化。最终S回F代码。
4. 对KV跑最短三方门后保持base=main；对CPU跑祖先/三方门后retarget到S。下层PR未来合并或改base时，只再检查受影响PR的diff，不重审未变方法/设备证据。
5. 中文README明确“main当前原始待改造框架”“完整已测组合在历史快照/本地”“新增由方法Draft展示”；旧103/105及正式吞吐只链接原SQL+C3组合，单项/新基线不继承。完整KV协议、进展victim、失败Event仍只在实验库，不塞入重建PR。

硬件owner对FlagGems已核：相对4df52d9只有中文README及原首页存档，没有新增算子源码；不要制造不存在的方法PR或改FlagGems库内代码。引用其独占 `docs/pr-rebuild/kv-inventory.md`，六方法源码分界由framework盘点负责。本agent只落此短review和交接，不改远端、共享分支、作者材料、registry/queue，不启动GPU。
