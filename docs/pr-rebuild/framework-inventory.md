# 从原框架恢复、按历史方法重建PR

推荐让旧main快照F的后继提交R恢复原框架代码，再从R顺序建立下表六个PR；**R的代码身份是原13eb，commit parent仍保留F，不能另起历史或force覆盖。** 代码基点为 `13eb9be69ecc5b5ca4f79c44e9ee40081eaa1bf0`（tree `649161e62191e81a4b367e0e19dc37e32e745099`）。中文首页、上游README副本和基点说明属于文档，可由root另保留。

旧快照70d04f3相对13eb只有9个代码文件变化，另有README替换/README.upstream新增。六包顺序应用后，**9个代码文件全部逐byte回到旧快照**；去掉新方法说明、使用原上游README时，重建tree精确为 `5c14cfb8d3a452e97a67758873bf18039e1bf989`。实际GitHub tree还包含root的新基线中文文档和各PR说明，不能误写成上述投影tree。

## 六个真实增量

| 顺序/材料目录 | 本PR实际内容 | 依赖与范围 |
| --- | --- | --- |
| `00-diagnostics` | 原CPU线程、sampler compile诊断、batch/prefix/block覆盖开关及默认16的日志分支；修改init/platform/vendor三文件 | 默认关闭的实验支持，不能算作SQL或Attention收益，不能借此修改比赛参数 |
| `01-prefill` | 原Attention源码变换与vendor调用接点；BM128/BQ16/TILE64/w8/s1 | 为拆包暂去共享runtime中的top-p函数/调用，原Attention算法函数与变换字符串逐byte不动 |
| `02-top-p` | 原直方图zoom实现与原top-p-only分派；补回共享runtime原函数/调用 | 包装上接01，算法不依赖prefill；此步后runtime精确回受测a0c |
| `03-sql` | 原ad84目标表反射模块与runner三行安装接点 | 算法可独立于prefill/top-p；推荐堆叠顺序还原历史SQL-only上下文，不带C2/C3 |
| `04-decode-3d` | 原e5代理和footer，仅严格3D范围w2/s1 | 硬依赖prefill产生的Attention54c/helper59d9；SQL只是推荐堆叠顺序，不是算法依赖 |
| `05-mixed` | 原a129 builder/forward包装和footer，天然单token前缀拆分 | 硬依赖原e5代理和固定Attention/backend/helpers；不是SQL的一部分，归约顺序变化的准确率属于组合 |

每个目录含 `files/<repo-relative-path>`、中文 `PR.md`、`manifest.json`。机器入口为 [framework-inventory.json](framework-inventory.json)：root按 `recommended_parent` 建堆叠，读取entries中的文件内容创建blob/tree/commit/branch/PR即可；base/head blob与SHA、代码投影tree均在JSON，不需猜文件或改算法。README不夹进任何性能方法。

九条代码路径是：`vllm_fl/__init__.py`、`vllm_fl/platform.py`、`vllm_fl/dispatch/backends/vendor/iluvatar/iluvatar.py`、`vllm_fl/worker/model_runner.py`，以及 `vllm_fl/patches/` 下的 `biv150_runtime.py`、`biv150_top_p_triton.py`、`biv150_sql_reflection.py`、`biv150_decode_launch_runtime.py`、`biv150_mixed_decode.py`。没有漏掉默认关闭的实验支持，也没有把它们藏到五个性能方法中。

## SQL与历史证据边界

SQL最小接点确实只有 `SQLPersistantModel.build_sql_model_by_db` 的替换实现和runner footer。现有独立增量 `patches/candidates/vllm-plugin-FL-biv150-sql-reflection.patch`（2825325e…）只改这两条路径；module SHA为ad84c9…，已安装FlagGems原SQL源要求6dc19c…。fresh base、SQLite目标表callable过滤、缺表返回None、默认FK闭包与非SQLite原路均保留。retained performance不改runner，所以该SQL小增量也能接原13eb，但**已有SQL-only服务测量是在retained上下文**，不能改写成原13eb全树的独立官方对照。

SQL单项证据为064632/072153短筛及071554对照，另有072702同SQLAlchemy2.0.48的6项CPU门；早期pair没有完整DB初态快照，不声称cache-matched。101/105是SQL+C2，103/105和两档完整官方结果是SQL+C3，不能分摊为SQL单项准确率或单项官方成绩。硬件owner独立核这些原件，本次不重跑。

旧d60 commit对象不在当前本地对象库，不能假装读到它；6e8 retained patch、原064632 launcher与历史归档保存其来源。重建直接用已验13eb对象及固定原字节，不依赖猜测d60元数据。SQL/C2/C3逐阶段runner分别精确为c81e6ae9…、7ddf885a…、e155a166…；最终与旧main一致。

## 后续PR与已开发范围

保留F→R→六链→S的历史时，旧CPU PR head H仍以F为祖先，merge-base(S,H)为F；只要S重建代码与F相同，两个CPU方法的三点diff仍仅自身文件，**不需改写受测head**。root在实际构造后核merge-base/diff/merge-tree即可。若另从原13eb起新历史，才会失去此保证；不要把该备选当当前方案，也不要只盲改PR base。

CPU metadata、async token两个Draft继续保留原受测blobs，组合062205仅方法正确性门，不是新准确率或稳定吞吐。KV连续页工具与二维工具两个Draft仅新增独占文件，可在恢复基点上按三方结果处理，无需借五个历史方法引入服务hook。

其余本地开发没有默认导入旧main：KV事务/FULL/私有页排序/capacity/progress/pitched SAVE服务候选；bucket、hidden gather、growth、overlap、visible-prefix、CTA等探索；C3/KV/内存/抢占观察模块；Event/native阻塞门（无CPU收益）。48份其他framework源的路径与SHA列在JSON，供后继接续，不自动转成待合入方法。早期重复适配器、失败与未实施研究仍按原记录保留。

本次只在本独占目录机械拆包、计算Git blob/tree并compile语法；不导入候选、不做模型/设备/套件/SSH或远端操作，也不切共享分支。所有最终9代码字节与旧快照相同，但新单方法子集/新的分阶段发布不是新的上卡或准确率结果。特别是prefill安装器原本会改写site-packages Attention和清pycache，Git恢复原代码不等于设备依赖也恢复；以后基线实验须另核实际安装源。
