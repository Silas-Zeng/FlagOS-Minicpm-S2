# 本批张量证据的无损存储

这五轮的40份 `.pt` 原始数据在本地 archive 完整保留；GitHub 发布树使用 `.pt.gz`；超过512KiB的gzip以不超过256KiB的无损块保存。恢复器先按索引逐块核SHA并拼回相同gzip，再解压。完整gzip另保留本地tmp，不丢弃。原 `archive-receipt.json` 中的文件名、大小和 SHA 仍指未压缩原件，未被改写。每轮索引另列 gzip SHA、原件 SHA 和已实测解压 SHA。

恢复某轮全部原文件：

```bash
python scripts/restore_large_evidence.py experiments/framework/<run>/tensor-storage.json
```

恢复器核压缩件和还原件 SHA，已有不同文件不会被覆盖。

本批原始 1,152,731,720 B → gzip 38,792,631 B；40份完整解压逐SHA通过。

- [20261027T125106851090Z-corex-native-gqa-s2-synchronous-component](framework/20261027T125106851090Z-corex-native-gqa-s2-synchronous-component/tensor-storage.json)
- [20261027T131805595037Z-corex-native-gqa-s4-synchronous-component](framework/20261027T131805595037Z-corex-native-gqa-s4-synchronous-component/tensor-storage.json)
- [20261027T132510103688Z-gqa-strided-fixture-diagnostic](framework/20261027T132510103688Z-gqa-strided-fixture-diagnostic/tensor-storage.json)
- [20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component](framework/20261027T133209942679Z-corex-native-gqa-s2-qstride2560-component/tensor-storage.json)
- [20261027T133545186656Z-corex-native-gqa-s4-synchronous-component](framework/20261027T133545186656Z-corex-native-gqa-s4-synchronous-component/tensor-storage.json)
