# selected-Q 最短真实 backend 数值门

只用于决定末层 selected-Q 是否值得进入模型门，尚未上卡。固定 main526/tree `8671e2ec`、当前 native `14f4457a` 和已审 selected-Q helper `7d40d8d4`；不改冻结527、官方参数或当前服务。来源清单与原包映射在 `base-source-manifest.json`，新增 CPU 几何检查在 `cpu-check.json`。

原 SERVER 对应的 EngineArgs 建配置后，按真实 worker 顺序注册 OOT/启用 FlagGems，再导入固定526 runner执行现有 C2/C3/GQA/normalization/Q/native安装链；核实际来源/绑定与每臂调用增量，记录Q合法fallback，不拿安装marker冒充执行。14f库已加载但此组件不执行native GEMM或加载模型权重。

四例是 S32/40/64、M2048，加 S5/M141；覆盖穿插请求的非恒等P、40波次、16K与短/无历史、不齐页。只给一两条长历史，每例单份cache小于48MiB；页独占但物理顺序打乱。原 mixed 全M输出取物理末行，对照新 q1/S；两臂同stream、同cache、各自全M writer，旧C3 plan仅在新metadata丢弃。每臂先poison三份partial，实际slots全部K/V逐字核对与有限guard检查；不保存整cache。

记录输出finite/maxabs/RMS/relativeL2，并对每例最长请求的最后Query，用CPU NumPy FP32独立算QK/softmax/PV作为参考。归约次序改变不要求bitexact，也不设随意阈值称模型准确率通过。`completed=true`只指四例、写量、guard、实际路径和结果保存完整；数值接受仍需读原差异。每臂一次执行，含冷编译的wall只作诊断，不计算性能收益。

复用 f72e owner 的设备锁、实时9031/设备空闲门、300秒子进程上限、6秒清理、DB before/after/恢复。新增仅固定526/native身份、显式来源传参及前后核对，见 `owner.diff`。只有主智能体可在设备空闲后启动：

```bash
python -B /workspace/experiments/minicpm-s2/assets/<本包目录>/run_component.py \
  --run-dir /workspace/experiments/minicpm-s2/diagnostics/<唯一UTC>-final-query-row-component \
  --plugin-source /workspace/experiments/minicpm-s2/code/main0bf9-base-20261024T1548 \
  --native-library <实际已核14f的biv150_native_w8a8.so绝对路径>
```

源码未知、写量/guard不符或出现非有限输出即停止并保留原失败；数值与参考偏差由主线决定是否继续。通过组件也仍需新的实际模型M/S图、KV依赖和必要准确率，不复用旧四语义/105作新归约资格。纯prefill/S1的扩大另行处理，本包只覆盖当前首轮mixed范围。

本v2仅在导入526 runner前初始化真实world1/TP1，并在独立worker的finally清理。原005351失败在未初始化TP组、无有效case；原件不变。3项新增CPU窄查，数值/cases/helper不变；旧8项复用，不把CPU检查当GPU通过。

v3仅修正`torch.tensor(numpy,pin_memory=True)`不支持的构造，改为实际已可用的pinned empty＋numpy copy。v2真实TP建立/清理成功，但首case在双臂执行前失败；原件保留，无数值结论。新3项CPU窄查，生产helper、case和数值比较不变。封包以本包asset-pins及package-receipt为准；保留的旧freeze/check脚本仅作来源，不使用其旧封包列表重封本版本。
