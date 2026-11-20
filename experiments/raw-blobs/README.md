# 大原件存储

GitHub 单文件 API 拒绝本批较大的张量文件，普通 Git 连接也被重置。超过 8 MiB 的新增原件在本地及远端完整保留，在仓库中按 SHA256 分块存储，不改变原始字节。

原路径旁的 `文件名.storage.json` 保存原大小、SHA256 和各块路径。运行 `python scripts/restore_large_evidence.py <清单路径>` 可核验并还原。原始归档清单里的 SHA256 仍有效；分块不产生新的实验结果。
