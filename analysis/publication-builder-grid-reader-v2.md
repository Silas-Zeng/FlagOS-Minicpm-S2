# 本批实验记录的本地发布构建

本地构建器：`scripts/build_grid_reader_publication_payload.py`。它固定源HEAD `b3c869cdb4034b03499a8d5d4720a67eec10084a`、已发布parent `ff080419089bcc7a9e5a32e5dd81099cf809e3b5` 和base tree `9837334c5929ff76223f8fd5d3755a21228a5eec`，纳入本批7条登记、对应短页/bundle/raw chunks、生成团队视图、相关stager及中文说明。每个Git blob以SHA1与Git blob framing交叉核验，传输payload按1MiB SHA256分块，并从base tree算出预期完整tree和source commit。脚本不更新分支、不push、不调用GitHub。

运行：

```powershell
& 'C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 'scripts/build_grid_reader_publication_payload.py' --out 'analysis/publication-pr105-i32-batch-20261029'
```

最终 `tree-plan.json` 和 `PR-body.md` 位于输出目录；输出前会拒绝意外tracked diff、登记计数不符、证据分块SHA错误或缺少终态run。
