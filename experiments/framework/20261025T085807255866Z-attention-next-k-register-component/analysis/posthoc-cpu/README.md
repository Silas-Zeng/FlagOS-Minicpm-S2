这是 GPU 运行结束后对已回收 IR 的独立 CPU 后核；原 results.json、exit1 和源码未改。跨行 load 定位修复后，8条真实路径仍在首PV前遇wait/barrier；未计时、未执行换页复验，不能称数值或性能失败。check.py 保留执行时原路径，依赖见同目录 result.json；完整运行源码与 IR 在本 run 目录。
