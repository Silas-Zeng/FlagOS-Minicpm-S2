# 原 main526 mixed 的采样边界诊断

仅一次原双请求，temperature=0、max_tokens=1024、首内容同步及返回 token IDs 不变。原 main0bf9/tree8671、native14f 是来源；实际运行是 **527 文件诊断树7ebc45b2**，只增加插件注册接线和图外观察 helper，不能标为“原526源码未变”。没有混入默认 native-off、队友候选或新优化；原 model_runner、模型数学、官方服务 CLI、Graph、native、缓存语义和清理均复用。

复用已受测 current-hotspot 的 EngineCore→runner 安装。模型完成预热/capture 后，预分配16777472B（约16MiB）；前8个涉及长题的模型步，记录原raw logits、processor后真正greedy输入、selected hidden、实际采样ID/请求行/丢弃mask/选行indices/实际M与Graph描述符。原stream执行copy_；运行时没有D2H、tensor.item或显式同步。原请求收齐、owner关闭服务时，runner.shutdown先同步一次设备，再回收快照；同期额外内存和复制仍可能改变故障复现。

原mixed语义失败照常保留非零exit；`state.boundary_observation.valid`只表示回收到可分析的快照。CPU分类区分hidden非有限、raw logits非有限、processor后无效、argmax/行归属不符；finite且argmax一致选0仍可能是较早数值退化/KV污染，不能当模型正确。partial-prefill被丢弃行不当作输出错误。未复现不撤销094755/103226旧失败，也不通过限制特殊token修饰输出。未定位具体层、kernel或责任PR，不借PR44的M8错误归因。

CPU验证：实际新挂钩在假对象上通过8步/40次copy封顶、raw与原地processor隔离、原请求映射/ID、推理中零D2H/零同步、shutdown仅一次同步先于D2H及绑定恢复；CPU分类覆盖有限值、argmax错配、hidden/raw/processed非有限和合法-inf mask。真实CUDA与退出回调仍由本次运行原件证明；检查结果见cpu-check.json，增量差分见candidate.diff/owner.diff。

主线程统一上卡；本子智能体没有启动GPU。先按package.json核包，解包entry.tar.gz到新目录，再将其中source.tar解到唯一的新code目录，保留Unix mode/symlink。示例：

```bash
python3 verify_service.py \
  --source-dir /workspace/experiments/minicpm-s2/code/main526-mixed-logits-7ebc45b2 \
  --performance-control /workspace/experiments/minicpm-s2/official/20261024T161030Z-main0bf9-main-official-four-rounds-control
```

输出在`framework/<UTC>-main526-mixed-logits-boundary`：原HTTP/SSE/token、model-path、`logits-boundary/{installed.json,metadata.json,tensors.pt,analysis.json}`；control保存实际527树、原SO身份、环境、命令、DB及清理。只有原请求完成且快照完整才标观察有效。一次缺窗/未复现便收口，不自动重跑或扩大测试矩阵。此诊断不形成官方准确率、性能或合规基线。
