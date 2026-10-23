# PR15 实际提交的独立准确率入口

固定PR15 `638c4ac0f07ed98e4476a5971c849630d9cdd580`（tree `d6a9597c…`，parent main9a43eb1）。本地发布素材在`tmp/computed-h2d-pr/`，不是完整工作树；本次使用root取回的固定commit tarball，SHA `a61e717f…`。相对main仅runner cc7f→195cc806，三hunk与受测cc442→97f41方法一致，原metadata helper0e961不变。214819方法门和215331短pair直接复用，不能称当前提交整树已测或继承旧QGQA准确率；C500仍无验证。

唯一包装`launch_pr15_accuracy.py`（最终e884b4b2）配`main-tree.json`（411f2a68）：先从base完整tree替runner推导PR目标tree，再核tar全部432 Git blob与模式；唯一symlink按链接文字算Git blob且目标须留在本树。所有成员通过后仅解包到全新固定source，不添base-revision或改任何代码。control保完整源码、Git blob map、普通SHA map、main-tree与提交身份；原35d owner继续负责锁、实时idle、DB、105题和清理，不新造controller。

```sh
assets=/workspace/experiments/minicpm-s2/scripts/pr15-accuracy-20261023
python3 "$assets/launch_pr15_accuracy.py" --archive "$assets/pr15-638c4ac0.tar.gz"
```

固定source为`/workspace/experiments/minicpm-s2/code/pr15-computed-h2d-638c4ac0`；已存在则拒绝覆盖。原SERVER、6e045 EvalScope脚本/采样/105题/阈值完全不变。源码无Q/KV实验接线，不设置Qartifact ENV，既有finite/Qartifact两项移除明确记purpose；原SQL启动marker已从本tar helper第71行核实。后验须同Engine出现原`BIV150_CPU_METADATA_FIRST_SELECTED positions_seq_h2d=2`，它结合实际195cc源证明成功分支省copy；不把该执行marker放在首题前的required marker。仍需原完整判卷及清理，不能先称准确率通过。历史用时约20分钟只供排期，不是本提交新成绩。

作者仅一次`--check-only`核tar/432blob/base及目标tree通过，未解包或运行模型/设备；该检查绑定23b9版本。之后仅加control复制main-tree和purpose环境移除名称两项记录，最终e884仅语法检查，未重跑已核包；wrapper-check.json保留此区别。team_view_final_check已只读最终新增差分通过，无当前部署阻断，代码冻结。root负责唯一设备派发、原件验收与归档。

112356收尾的专用导入入口为`import_pr15_accuracy.py <固定112356 run名> <tgz字节数> <tgz SHA256> <seal条目数>`。保旧全包与seal门，仅允许control/plugin-source内已审的唯一120000链接：锁路径/链接文字/e0f Git blob，目标须同目录包内regular且Git blob及双方seal内容hash相符，Windows写成原目标字节。stdout的`materialized_symlinks`留原path/linkname/Gitblob/target，原tgz不变、sealed树不添说明，最后仍核完整文件集合与内容SHA。最终8e2d67dc使用AGENTS.md与experiments/registry.csv双标识定位唯一仓库根，支持从tmp或归档目录运行；只有语法检查，未执行导入，root独占操作。新增链接规则b6c及末版根定位均已获team静态窄审通过，代码冻结。
