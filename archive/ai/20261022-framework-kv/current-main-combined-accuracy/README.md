# 当前 main + P 完整准确率准备

只复用 `20261023T141159Z-current-main-compute-order-context16k` 受测源码，不构造 tar、不改模型或评测。仅 root 在短测通过后决定是否启动。

部署三个文件：`launch_combined_accuracy.py`、`candidate-git-blobs.json`、`candidate-manifest.json`。执行 `python3 launch_combined_accuracy.py`，不接外部源路径参数。

启动前核原短测 exit0/清理记录、同 Engine 的 P 与 normalization 选择，以及 live source、原 control、固定 446 Git blobs/mode/内容的一致性；随后保留完整源码及两文件增量身份，调用未改的 `run_accuracy_gate.py` 35d / `run_math500_level3.sh` 6e045。原 105 题、SERVER、DB 快照、锁和清理均由原 owner 负责。

本地只 compile，未启动服务或评测，精确 SHA 见 `cpu-preparation.json`。本轮若 P 为 0 命中仍须如实限定，不继承队友 main 的 102/105 或旧组合结果；这不是性能测试。

framework_innovation 已只读核对 c5ec1da7 / 340e2ce1 / 0b17b3a1 新增接线，无启动阻断；未执行 launcher、模型或设备。

root 已启动 `20261023T142019Z-current-main-compute-order`（owner22265）。本地3资产与原receipt已逐字节归档至 `archive/ai/20261022-framework-kv/current-main-combined-accuracy/`。短pair最终仅same_KV失配（521840/521936），gain=null；本轮仍独立验证完整105题，不继承表观吞吐。

收尾复用原reviewer ba22（105唯一题/错误/原参数及输出cap诊断）与原accuracy sealer 716e；薄适配 `seal_combined_accuracy.py` 仅补固定142019、完整446 live/control/Git身份及独立 `method-coverage.json`。P零命中不否定完整105题，但不足以验证新P路径；首marker也不证明全程/逐题覆盖。`import_combined_accuracy.py` 仅在原8e2d上改固定run和446计数，保原tgz/全部seal/唯一已审symlink材料化。

```sh
python3 seal_combined_accuracy.py 20261023T142019Z-current-main-compute-order --reviewer /workspace/experiments/minicpm-s2/scripts/review_accuracy_gate.py
```

本地导入命令：`python import_combined_accuracy.py 20261023T142019Z-current-main-compute-order <实际tgz字节数> <实际SHA256> <实际seal条目数>`。精确hash及逐字逆回证明见 `recovery-preparation.json`；仅生成/compile，未判卷、封存、导入或操作设备。首份未执行草稿的normalization JSON假定已按实际tuple源码纠正，不修改任何原件。

framework_innovation 已只读终审 sealer51e2177b / importer40f6f9a3，无新增收尾阻断：固定142019/446闭包、仅定义runpy、实际normalized tuple/P JSON及0P边界正确；旧完整105题与import/link/seal门未变。未执行本轮数据、reader或设备，代码冻结。
