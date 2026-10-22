# 当前代码版本

框架 GitHub main 为 `87ed53719126208eaa9ba1cab698b14a5693eb5d`：比赛指定 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0` 为起点，十项方法已依次合并，并通过 #11 更新中文 README。

此前d5e2e3a导入的是完整SQL+C3优化快照，已保存在codex/archive/sql-c3-imported-20261022，历史未删除。该快照对应的准确率与吞吐证据保留，不能视为新main的成绩。

合并顺序见[方法 PR](pr-collaboration-plan.md)。六项早期增量重建原 SQL+C3；CPU 两项的冲突使用既有受测组合 runner `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`；KV 两项为显式工具。代码合并提交 `0f2b925588114d47c478707afa41e58c769c2ec4` 的 425 个文件与预期组件组合完全一致；后续 #11 仅改 README。复用既有验证，未重复测试，不把历史 103/105 外推到新增 CPU 组合。

[团队实验入口](../team/README.md) · [合并回执](../archive/github/20261022-framework-merge.json) · [历史迁移](../archive/github/20261022-framework-rebuild.json)
