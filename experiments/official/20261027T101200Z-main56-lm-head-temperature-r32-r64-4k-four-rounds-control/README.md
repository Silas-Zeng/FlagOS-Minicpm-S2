# R32＋R64 head温度epilogue：4K原官方四轮入口

仅CPU派生已审fe3e 16K入口，生产固定8d1a3de4、809文件/tree8060，未改源码、kernel、服务或评测参数。本档使用原官方`[[4096,1024,64,256]]`，四轮弃首；唯一A为052425 main56/native14f完整4K，实际首暖5749.08、暖均5902.77、KV548432。baseline_reference直接复用旧R64 4K reader原字节，引用的是原控制组，不把旧R64候选成绩作A。

必要变化仅case_driver的负载、owner的负载/标签/driver SHA、supervisor的prefill标签及qualification的基线说明；原command、服务参数和finally清理AST不变。每shape SELECTED/SAMPLED闭合、异常拒绝、原backbone/provider/Q32/native门复用；缺覆盖单独记录，不推断分支准确率。KV须解析唯一正值，是否与A相等另记；不匹配可继续观测，不能声称严格因果收益。第2轮与本A首暖比较，负则停、正则完成四轮，运行错误立即停。组件检查不重复，准确率不继承。

CPU检查见cpu-check.json及check-incremental.py；未SSH、未排队或启动GPU。root独审并确认当前准确率任务完全清理后，方可手动运行：

```bash
python3 official_supervisor.py /workspace/experiments/minicpm-s2/code/main56-head-temperature-r32-r64-8d1a3de4 main56-head-temperature-r32-r64-4k
```

源码目录名称不替代809文件身份验证。asset-pins.json绑定所有执行资产，assets.tar包含pins与对应文件；生产源包SHA保持8d1a3de438f460bdc021d8bcb4a7ac66c1915a569ec8539f1392c3ec9c44f309。
