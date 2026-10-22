# 纯 decode CPU gather：最短真实服务接线

仅本地 CPU 准备。必须先由 root 验收纯方法 GPU 门，再决定是否运行本服务候选；收益未知，资格 guard 可能抵消节省。本包不启动设备、不改已发布代码，BI-V150 结果不能外推 C500。

基点固定为干净组合 runner `6f918ae6e2f32a1244bb5ac7411a5cffdd5071b1636e899e61ab6f0f20df2141`，原 metadata0e／async1bb／SQL+C2+C3不变，不叠C3views。runtime `biv150_decode_cpu_gather.py` 保持原 **1a9de781b2f9504c627991071c5ee4b52eda59ca8af283f28a15b9fab38ef7bd** 全字节。candidate只有两条路径变化：

- `vllm_fl/worker/model_runner.py`：调用原runtime的精确transform，再追加 `service_append.py`；candidate SHA **70db5a6bbc5bb4bc75784ca6bce5d48021ff39aa58386853bc2872e8f8d7f16c**。
- `vllm_fl/patches/biv150_decode_cpu_gather.py`：原1a9 helper，不追加服务代码、不改数学／GPU输入／事件／采样。

`service_append.py` 是runner原C3安装块末尾的缩进footer，不是第三个运行时module。只包真实 `execute_model`：原调用恰一次／原结果异常透传；返回后该runner自身的 `selected` 当次增量>0且请求数≥2，才打印同Engine PID的 `BIV150_DECODE_CPU_GATHER_FIRST_ACTUAL_EXECUTE_SELECTED`，随后撤包装；观察前后读取或打印失败也只撤观察、不覆盖原成功结果，原callee始终在观察except之外。dummy/startup旧计数和driver单请求smoke不构成短筛命中。资格和N=1优化本身不被观察条件限制。marker只证明至少一个真实多请求步骤命中，不是覆盖率、GPU完成ACK或性能结论。

## 资产与入口

- `prepare_decode_gather_service.py`：**44018c6c8881e23a138a2cdcf8f4672bfd2635aab7076e85b955959367ddd33b**。
- `launch_decode_gather_service.sh`：**f4a8a0586ee0c02050ce70513e4c05b89c7118465ace7532d56ad3977073a59f**。
- footer：`59864f48bb0b9d687d91b4c088fa04642a629ac3af0239e67c3daab8f5c5d304`。
- `check_actual_selection.py`：`c2c760dde26e3910aa2e7d2ac9b434795ca7872dbcf7232d38ca71f6a0f6673b`。

沿用C3服务模板，只有素材／标签／命中marker不同；原bc51、`--decode-screen --seed 721201`及全部serving/benchmark参数不变。原driver仍是唯一设备锁／PID／清理owner；launcher只准备新隔离source/control、源全SHA、DB-before并启动原driver，不另加锁或设备作业。root按单卡协议串行运行：

```text
bash launch_decode_gather_service.sh candidate /workspace/experiments/minicpm-s2/code/EXACT_CLEAN_6F_BASE
python check_actual_selection.py RUN_DIR
```

也保留`baseline`选项，但不自动启动A/B。root可复用紧接的干净6f对照，前提是完整source差分、DB前后、KV容量、环境、原参数和host负载满足既有匹配门；失配或没有真实marker不得归因收益，不追最好样本。DB-after、postflight、source后态与全原件封存仍用root现有流程，首marker检查器不代替这些门。

## 新增验证边界

唯一新 `check_service_install_cpu.py` 初稿通过后，跨审指出观察输出失败风险；最小fail-open修正后只给同一合同加两个必要分支再过一次，旧稿/receipt保`history/initial`。当前`cpu-check.json`（ae9b8fb6…）：helper全字节一致、精确逆6f、原execute一次／原结果／同异常对象和context、dummy和单请求smoke不报、首次真实多请求增量与同PID、撤包装／缓存旧bound方法不重复打印、emit失败保成功返回／前读取失败不污染原异常context、source map静态412→413仅两路径、原driver命令行同。未执行整copy，实际prepare会再次完整核输出和基点source map；未重跑1a9合同／原方法门／GPU，未导入Torch/Triton/vLLM。当前只待跨职责owner审新接线，不扩大验证矩阵。

prepare直接pin的是runner与三个既有helper，并完整记录/核copy前后source map；不冒称已仅凭四文件锁定全部412文件。root首次选定BASE时仍须完整map与已封存070452干净组合吻合，之后复用同一基点即可，无需另造测试。

跨职责只读终审已通过（framework owner）：最终footer `59864f48`／prepare `44018c6c`／runner `70db5a6b` 与当前receipt一致；观察失败只撤观察，原execute恰一次且处于观察except之外，原成功结果与异常保留。复用原1a9方法证据，未重跑合同／设备；接线可交root串行部署。仍须root核选定干净基点完整412 map，并在真实服务后核同PID多请求命中、DB／KV／原参数和完整后态；此审阅不构成性能或准确率结果。


### 113627 服务结论更新：不集成

方法正确性门已通过后，root在原6f独立服务对照实际测得candidate6881.3277TPS、baseline6936.7042TPS，同DB/KV，差异−0.7983%。本小候选不保留集成，runtime/门/失败结果作为历史证据；guard成本可能抵消CPU gather省工，但没有局部成本分解不能定因。后续不为该方法追加同类门或大测试。该结果覆盖本文较早“待服务验证”的时间点。
